#!/usr/bin/env python3
"""
BitBucket Repos Data Extraction Script

This script extracts code events from BitBucket repositories and supports two modes of operation:

Usage:
    python extract_bitbucket_repos.py [-p <product_name>] [-s <start_date>]

Arguments:
    -p, --product: Product name (if provided, saves to database; otherwise saves to CSV)
    -s, --start-date: Start date for extraction in YYYY-MM-DD format (optional)

Modes (automatically determined):
    Database mode (when -p is provided):
        - Imports from the database module
        - Connects to the database
        - Reads the config from the data_source_config table
        - Gets the last extraction timestamp from the code_commit_event table
        - Saves the extracted data to the database table

    CSV mode (when -p is NOT provided):
        - Reads the config from environment variables:
          * BITBUCKET_WORKSPACE_ID: BitBucket workspace ID
          * BITBUCKET_API_URL: BitBucket API URL
          * BITBUCKET_API_TOKEN: BitBucket API token
          * BITBUCKET_REPOS: Comma-separated list of repository names
          * EXPORT_PATH: Export Path (Optional)
        - Gets the last extraction timestamp from the checkpoint (JSON) file
        - Saves the extracted data to CSV file, updating the checkpoint (JSON) file

Events extracted:
    - Pull Request Created
    - Pull Request Merged
    - Pull Request Closed
    - Pull Request Cherry-picked
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional
from urllib.parse import quote

base_dir = os.path.dirname(os.path.abspath(__file__))
common_dir = os.path.join(base_dir, "common")
if not os.path.isdir(common_dir):
    # go up one level to find "common" (for installed package structure)
    base_dir = os.path.dirname(base_dir)
    common_dir = os.path.join(base_dir, "common")

if os.path.isdir(common_dir) and base_dir not in sys.path:
    sys.path.insert(0, base_dir)

import requests

from common.code_commit_event import CodeCommitEvent
from common.utils import Utils

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('extract_bitbucket_repos')

# Set logger for CodeCommitEvent
CodeCommitEvent.LOGGER = logger


class BitbucketReposExtractor:
    """Extracts code events from BitBucket repositories."""

    def __init__(self):
        # Statistics
        self.stats = {
            'pr_created': 0,
            'pr_merged': 0,
            'pr_closed': 0,
            'pr_cherry_picked': 0,
            'total_inserted': 0,
            'total_duplicates': 0
        }

    def get_config_from_database(self, cursor) -> Dict:
        """Get BitBucket configuration from data_source_config table."""
        query = """
        SELECT config_item, config_value
        FROM data_source_config
        WHERE data_source = 'source_code_revision_control'
        AND config_item IN ('Workspace', 'Repos', 'Personal Access Token')
        """
        cursor.execute(query)
        results = cursor.fetchall()

        config = {}
        for config_item, config_value in results:
            if config_item == 'Repos':
                try:
                    repos = json.loads(config_value) if config_value else []
                    config['repos'] = repos if repos else []
                except (json.JSONDecodeError, TypeError):
                    # Fall back to comma-separated string
                    config['repos'] = config_value.split(',') if config_value else []
            elif config_item == 'Workspace':
                config['workspace'] = config_value
            elif config_item == 'Personal Access Token':
                config['api_token'] = config_value

        return config

    def get_last_modified_date(self, cursor) -> Optional[datetime]:
        """Get the last modified date from the database."""
        query = "SELECT MAX(timestamp_utc) FROM code_commit_event"
        cursor.execute(query)
        result = cursor.fetchone()
        if result[0]:
            # Convert to naive datetime if timezone-aware
            dt = result[0]
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            return dt
        else:
            return datetime(2020, 1, 1)

    def fetch_pull_requests(self, workspace: str, repo_name: str, headers: Dict) -> List[Dict]:
        """Fetch pull requests from BitBucket (handle pagination)."""
        all_pull_requests = []

        # States to fetch - both open and merged/declined PRs
        states = ['OPEN', 'MERGED', 'DECLINED']

        for state in states:
            page = 1
            rate_limit_retries = 0
            max_rate_limit_retries = 5

            while True:
                # BitBucket API endpoint for pull requests (URL encode the repo name)
                pull_requests_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{quote(repo_name)}/pullrequests"
                params = {
                    'page': page,
                    'pagelen': 50,
                    'state': state
                }

                # Retry logic for failed requests
                max_retries = 3
                retry_delay = 1  # seconds
                
                success = False
                for attempt in range(max_retries):
                    try:
                        response = requests.get(pull_requests_url, headers=headers, params=params, timeout=10)

                        if response.status_code == 200:
                            rate_limit_retries = 0  # Reset rate limit counter on successful response
                            data = response.json()
                            # Check if data is a dict with expected structure
                            if isinstance(data, dict) and 'values' in data:
                                pull_requests = data.get('values', [])
                                if not pull_requests:
                                    break
                                all_pull_requests.extend(pull_requests)

                                # Check if there are more pages
                                if 'next' not in data:
                                    break
                                page += 1
                                success = True
                                break
                            else:
                                logger.warning(f"Unexpected response format for pull requests in {repo_name}: {data}")
                                break
                        elif response.status_code == 429:
                            # Rate limit exceeded
                            rate_limit_retries += 1
                            if rate_limit_retries > max_rate_limit_retries:
                                logger.error(f"Max rate limit retries exceeded for {repo_name}. Skipping remaining pages.")
                                break
                            
                            if 'Retry-After' in response.headers:
                                wait_time = int(response.headers['Retry-After'])
                                logger.warning(f"Rate limit exceeded. Waiting {wait_time} seconds... (attempt {rate_limit_retries}/{max_rate_limit_retries})")
                                time.sleep(wait_time)
                                continue
                            else:
                                logger.warning(f"Rate limit exceeded. Waiting 60 seconds... (attempt {rate_limit_retries}/{max_rate_limit_retries})")
                                time.sleep(60)
                                continue
                        else:
                            logger.warning(f"Failed to fetch pull requests for {repo_name}: {response.status_code} - {response.text}")
                            if attempt < max_retries - 1:
                                time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                                continue
                            else:
                                break
                                
                    except requests.exceptions.RequestException as e:
                        logger.warning(f"Request failed for pull requests in {repo_name} (attempt {attempt + 1}): {e}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                            continue
                        else:
                            break
                    except Exception as ex:
                        logger.error(f"Error fetching pull requests for {repo_name}: {ex}")
                        break
                
                if not success:
                    break

        return all_pull_requests

    def extract_pull_request_events(self, pr: Dict, repo_name: str) -> List[Dict]:
        """Extract and format pull request events for each stage (created, merged, closed)."""
        events = []

        pull_request_number = pr['id']
        title = pr['title']
        actor = pr['author']['display_name']
        base_branch = pr['destination']['branch']['name']
        head_branch = pr['source']['branch']['name']
        head_sha = pr['source']['commit']['hash']

        # Do not set work_item_id in extractor

        # Parse timestamps
        created_at = Utils.convert_to_utc(pr['created_on'])
        merged_at = Utils.convert_to_utc(pr.get('merged_on'))
        closed_at = Utils.convert_to_utc(pr.get('closed_on'))

        # Create Pull Request Created event
        if created_at:
            event = CodeCommitEvent.create_event(
                timestamp_utc=created_at,
                repo_name=repo_name,
                event_type='Pull Request Created',
                source_branch=head_branch,
                target_branch=base_branch,
                revision=head_sha,
                author=actor,
                comment=title,
                extended_attributes={'pull_request_number': pull_request_number}
            )
            events.append(event)

        # Create Pull Request Merged event
        if merged_at:
            event = CodeCommitEvent.create_event(
                timestamp_utc=merged_at,
                repo_name=repo_name,
                event_type='Pull Request Merged',
                source_branch=head_branch,
                target_branch=base_branch,
                revision=head_sha,
                author=actor,
                comment=title,
                extended_attributes={'pull_request_number': pull_request_number}
            )
            events.append(event)

        # Create Pull Request Closed event
        if closed_at:
            event = CodeCommitEvent.create_event(
                timestamp_utc=closed_at,
                repo_name=repo_name,
                event_type='Pull Request Closed',
                source_branch=head_branch,
                target_branch=base_branch,
                revision=head_sha,
                author=actor,
                comment=title,
                extended_attributes={'pull_request_number': pull_request_number}
            )
            events.append(event)

        return events


    def get_release_branches(self, workspace: str, repo: str, headers: Dict) -> List[str]:
        """Get the list of release branches in the repository."""
        url = f'https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/refs/branches'
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'values' in data:
                branches = data.get('values', [])
                release_branches = [branch['name'] for branch in branches if branch['name'].startswith('release/')]
                return release_branches
            else:
                logger.warning(f"Unexpected response format for branches in {workspace}/{repo}: {data}")
                return []
        else:
            logger.warning(f"Failed to fetch branches for {workspace}/{repo}: {response.status_code} - {response.text}")
            return []

    def get_commits(self, workspace: str, repo: str, branch: str, headers: Dict) -> List[Dict]:
        """Get the commits from the branch."""
        url = f'https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/commits'
        params = {'include': branch}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'values' in data:
                commits = data.get('values', [])
                return commits
            else:
                logger.warning(f"Unexpected response format for commits in {workspace}/{repo}/{branch}: {data}")
                return []
        else:
            logger.warning(f"Failed to fetch commits for {workspace}/{repo}/{branch}: {response.status_code} - {response.text}")
            return []

    def process_commit_message(self, commit_message: str) -> tuple:
        """Extract pull request number and work item ID from commit message."""
        pull_request_number = None
        work_item_id = None
        # Match the pattern 'Merge pull request #<pull_request_number> from <head_branch_prefix>/<work_item_id>'
        match = re.search(r'Merge pull request #(\d+) from .*/(\d+)', commit_message)
        if match:
            pull_request_number = match.group(1)
            work_item_id = match.group(2)
        return pull_request_number, work_item_id

    def extract_cherry_pick_events(self, workspace: str, repo: str, headers: Dict) -> List[Dict]:
        """Extract cherry-pick events from release branches."""
        events = []

        release_branches = self.get_release_branches(workspace, repo, headers)

        # Process each release branch
        for release_branch in release_branches:
            # Get the commits for this release branch
            commits = self.get_commits(workspace, repo, release_branch, headers)

            for commit in commits:
                commit_sha = commit['hash']
                commit_message = commit['message']
                commit_timestamp = commit['date']

                # Extract pull request number and work item ID from commit message
                pull_request_number, work_item_id = self.process_commit_message(commit_message)

                if work_item_id or pull_request_number:
                    # Convert commit timestamp to UTC datetime
                    timestamp_utc = Utils.convert_to_utc(commit_timestamp)

                    if timestamp_utc:
                        event = CodeCommitEvent.create_event(
                            timestamp_utc=timestamp_utc,
                            repo_name=repo,
                            event_type='Pull Request Cherry-picked',
                            target_branch=release_branch,
                            revision=commit_sha,
                            comment=commit_message,
                            extended_attributes={'pull_request_number': pull_request_number}
                        )
                        events.append(event)

        return events

    def run_extraction(self, cursor, config: Dict, start_date: Optional[str], last_modified: Optional[datetime], export_path: str = None):
        """
        Run extraction: fetch and save data.

        Args:
            cursor: Database cursor (None for CSV mode)
            config: Configuration dictionary
            start_date: Start date from command line (optional)
            last_modified: Last modified datetime from database or checkpoint
            export_path: Export path for CSV mode
        """
        # Track maximum timestamp for checkpoint saving
        max_timestamp = None

        # Validate required configuration
        if not config.get('workspace') or not config.get('api_token'):
            logger.error("Missing required configuration: Workspace or Personal Access Token")
            sys.exit(1)

        if not config.get('repos'):
            logger.error("No repositories configured")
            sys.exit(1)

        workspace = config.get('workspace')
        api_token = config.get('api_token')
        repos = config.get('repos', [])

        # Set up headers
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }

        # Determine start date
        if start_date:
            try:
                extraction_start_date = datetime.strptime(start_date, '%Y-%m-%d')
                # Convert to naive UTC datetime
                if extraction_start_date.tzinfo is not None:
                    extraction_start_date = extraction_start_date.astimezone(timezone.utc).replace(tzinfo=None)
            except ValueError:
                logger.error("Invalid date format. Please use YYYY-MM-DD format.")
                sys.exit(1)
        else:
            if last_modified:
                # Convert to naive datetime if timezone-aware
                if last_modified.tzinfo is not None:
                    last_modified = last_modified.replace(tzinfo=None)
                extraction_start_date = last_modified
            else:
                extraction_start_date = datetime(2020, 1, 1)

        # Set up save function
        if cursor:
            # Database mode

            def save_output_fn(events):
                if events:
                    total, inserted, duplicates = CodeCommitEvent.save_events_to_database(events, cursor, cursor.connection)
                    self.stats['total_inserted'] += inserted
                    self.stats['total_duplicates'] += duplicates
                    return total, inserted, duplicates
                return 0, 0, 0
        else:
            # CSV mode - create CSV file at the start
            csv_file = Utils.create_csv_file("bitbucket_repos_events", export_path, logger)

            def save_output_fn(events):
                if events:
                    result = Utils.save_events_to_csv(events, csv_file, logger)
                    # Track maximum timestamp for checkpoint
                    if len(result) == 4 and result[3]:  # result[3] is max_ts
                        nonlocal max_timestamp
                        if not max_timestamp or result[3] > max_timestamp:
                            max_timestamp = result[3]

                    inserted = result[0] if len(result) > 0 else len(events)
                    duplicates = result[1] if len(result) > 1 else 0
                    self.stats['total_inserted'] += inserted
                    self.stats['total_duplicates'] += duplicates
                    return len(events), inserted, duplicates
                return 0, 0, 0

        # Log the fetch information

        logger.info(f"Starting extraction from {extraction_start_date}")
        logger.info(f"Fetching data from https://api.bitbucket.org/2.0/repositories/{workspace}")

        # Process each repository
        for repo_name in repos:
            repo_name = repo_name.strip()  # Remove any whitespace
            logger.info(f"Processing repository: {repo_name}")

            try:
                # Fetch pull requests
                pull_requests = self.fetch_pull_requests(workspace, repo_name, headers)
                logger.info(f"Found {len(pull_requests)} pull requests for repository {repo_name}")

                # Extract pull request events
                pr_events = []
                for pr in pull_requests:
                    events = self.extract_pull_request_events(pr, repo_name)
                    # Filter events by extraction_start_date
                    filtered_events = [
                        e for e in events
                        if e['timestamp_utc'] and e['timestamp_utc'] > extraction_start_date
                    ]
                    pr_events.extend(filtered_events)

                # Save pull request events
                if pr_events:
                    total, inserted, duplicates = save_output_fn(pr_events)
                    self.stats['pr_created'] += sum(1 for e in pr_events if e['event'] == 'Pull Request Created')
                    self.stats['pr_merged'] += sum(1 for e in pr_events if e['event'] == 'Pull Request Merged')
                    self.stats['pr_closed'] += sum(1 for e in pr_events if e['event'] == 'Pull Request Closed')

                # Process cherry picks
                cp_events = self.extract_cherry_pick_events(workspace, repo_name, headers)
                # Filter events by extraction_start_date
                filtered_cp_events = [
                    e for e in cp_events
                    if e['timestamp_utc'] and e['timestamp_utc'] > extraction_start_date
                ]

                # Save cherry pick events
                if filtered_cp_events:
                    total, inserted, duplicates = save_output_fn(filtered_cp_events)
                    self.stats['pr_cherry_picked'] += len(filtered_cp_events)

            except Exception as e:
                logger.error(f"Error processing repository {repo_name}: {e}")
                continue

        # Save checkpoint in CSV mode
        if not cursor and max_timestamp:
            if Utils.save_checkpoint(prefix="bitbucket_repos", last_dt=max_timestamp, export_path=export_path):
                logger.info(f"Checkpoint saved successfully: {max_timestamp}")
            else:
                logger.warning("Failed to save checkpoint")

        # Print summary statistics
        self._print_summary()

    def _print_summary(self):
        """Print extraction summary statistics."""
        logger.info(f"Pull Request Created:      {self.stats['pr_created']:>6}")
        logger.info(f"Pull Request Merged:       {self.stats['pr_merged']:>6}")
        logger.info(f"Pull Request Closed:       {self.stats['pr_closed']:>6}")
        logger.info(f"Pull Request Cherry-picked: {self.stats['pr_cherry_picked']:>6}")

        total_events = sum([
            self.stats['pr_created'],
            self.stats['pr_merged'],
            self.stats['pr_closed'],
            self.stats['pr_cherry_picked']
        ])
        logger.info(f"Total Events:              {total_events:>6}")
        logger.info(f"Inserted to DB:            {self.stats['total_inserted']:>6}")
        logger.info(f"Duplicates Skipped:       {self.stats['total_duplicates']:>6}")


def main():
    parser = argparse.ArgumentParser(description="Extract BitBucket Repos data")
    parser.add_argument('-p', '--product', help='Product name (if provided, saves to database; otherwise saves to CSV)')
    parser.add_argument('-s', '--start-date', help='Start date (YYYY-MM-DD)')
    args = parser.parse_args()

    extractor = BitbucketReposExtractor()

    if args.product is None:
        # CSV Mode: Load configuration from config.json
        config = json.load(open(os.path.join(common_dir, "config.json")))
        
        # Get configuration from config dictionary
        repos_str = config.get("BITBUCKET_REPOS", '')
        repos_list = [repo.strip() for repo in repos_str.split(",") if repo.strip()]

        config = {
            'workspace': config.get('BITBUCKET_WORKSPACE_ID'),
            'api_token': config.get('BITBUCKET_API_TOKEN'),
            'repos': repos_list
        }

        # Use checkpoint file for last modified date
        last_modified = Utils.load_checkpoint("bitbucket_repos")

        extractor.run_extraction(None, config, args.start_date, last_modified)

    else:
        # Database Mode: Connect to the database
        from database import DatabaseConnection
        db = DatabaseConnection()

        with db.product_scope(args.product) as conn:
            with conn.cursor() as cursor:
                config = extractor.get_config_from_database(cursor)
                last_modified = extractor.get_last_modified_date(cursor)
                extractor.run_extraction(cursor, config, args.start_date, last_modified)

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
