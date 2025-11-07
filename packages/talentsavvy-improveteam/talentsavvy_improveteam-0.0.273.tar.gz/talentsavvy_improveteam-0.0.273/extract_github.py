import requests
import json
import datetime
import re
import sys
import os
import argparse
import time

base_dir = os.path.dirname(os.path.abspath(__file__))
common_dir = os.path.join(base_dir, "common")
if not os.path.isdir(common_dir):
    # Common not found - go up one level to find it (for installed package structure)
    base_dir = os.path.dirname(base_dir)
    common_dir = os.path.join(base_dir, "common")

if os.path.isdir(common_dir) and base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from common.utils import Utils
from common.code_commit_event import CodeCommitEvent
import logging

# Configure logging to print messages on stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)


class GitHubExtractor:
    """Extracts pull request and cherry-pick events from GitHub."""

    def run_extraction(self, cursor, config, start_date, last_modified, export_path=None):
        # Set up configuration
        self.github_owner = config.get('Organization')

        # Parse repositories - handle both JSON array and comma-separated string
        repos_config = config.get('Repos', '')
        if repos_config:
            try:
                # Try to parse as JSON array first
                self.repositories = json.loads(repos_config)
            except (json.JSONDecodeError, TypeError):
                # Fall back to comma-separated string
                self.repositories = repos_config.split(',')
        else:
            self.repositories = []

        self.personal_access_token = config.get('Personal Access Token')

        # Validate configuration
        if not self.github_owner or not self.repositories:
            logging.error("Missing required configuration: Organzation / Repos")
            return

        # Set up headers - User-Agent is required by GitHub API
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'TalentSavvy-PA'
        }

        # Only add Authorization header if PAT is provided
        if self.personal_access_token and self.personal_access_token.strip():
            self.headers['Authorization'] = f'Bearer {self.personal_access_token}'
            logging.info("Using Personal Access Token for GitHub API authentication")
        else:
            logging.info("No Personal Access Token provided - using unauthenticated requests (public repositories only)")

        # Determine start date
        if start_date:
            # Validate date format
            try:
                datetime.datetime.strptime(start_date, '%Y-%m-%d')
                last_modified_date = f"{start_date} 00:00:00.000"
            except ValueError:
                logging.error("Invalid date format. Please use YYYY-MM-DD format.")
                return
        else:
            last_modified_date = last_modified

        # CSV mode - create CSV files lazily
        if not cursor:
            csv_file = None
            max_timestamp = None

            def save_output_fn(events):
                nonlocal csv_file, max_timestamp

                if not events:
                    return 0, 0, 0

                # Create CSV file lazily on first write
                if csv_file is None:
                    csv_file = Utils.create_csv_file("github_events", export_path, logging)

                # Save to CSV using common utility (expects dict events)
                result = Utils.save_events_to_csv(events, csv_file, logging)
                # result: (total, inserted, duplicates, max_ts)
                if len(result) == 4 and result[3]:
                    if max_timestamp is None or result[3] > max_timestamp:
                        max_timestamp = result[3]
                total_events = result[0] if len(result) > 0 else len(events)
                inserted_events = result[1] if len(result) > 1 else 0
                duplicates = result[2] if len(result) > 2 else 0
                return total_events, inserted_events, duplicates

            # Process repositories for CSV mode
            for repo_name in self.repositories:
                repo_name = repo_name.strip()
                logging.info(f"Fetching data from https://api.github.com/repos/{self.github_owner}/{repo_name}")

                try:
                    # Process pull requests
                    pr_data_count, pr_inserted, pr_duplicates = self.process_pull_requests_for_csv(repo_name, last_modified_date, save_output_fn)

                    # Process cherry picks
                    cp_data_count, cp_inserted, cp_duplicates = self.process_cherry_picks_for_csv(repo_name, save_output_fn)

                except Exception as e:
                    logging.error(f"Error processing repository {self.github_owner}/{repo_name}: {str(e)}")
                    continue

            # Save checkpoint in CSV mode
            if max_timestamp:
                if Utils.save_checkpoint(prefix="github", last_dt=max_timestamp, export_path=export_path):
                    logging.info(f"Checkpoint saved successfully: {max_timestamp}")
                else:
                    logging.warning("Failed to save checkpoint")

            logging.info("CSV extraction completed")

        else:
            # Database mode

            def save_output_fn(events):
                if not events:
                    return 0, 0, 0

                # Filter by last_modified_date (events are dicts)
                filtered_events = []
                try:
                    last_modified_datetime = datetime.datetime.strptime(last_modified_date, "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    last_modified_datetime = None
                for event in events:
                    event_dt = event.get('timestamp_utc')
                    if isinstance(event_dt, str):
                        try:
                            event_dt = datetime.datetime.strptime(event_dt, "%Y-%m-%d %H:%M:%S.%f")
                        except ValueError:
                            event_dt = None
                    if not last_modified_datetime or (event_dt and event_dt >= last_modified_datetime):
                        filtered_events.append(event)

                if not filtered_events:
                    return 0, 0, 0

                total, inserted, duplicates = CodeCommitEvent.save_events_to_database(filtered_events, cursor, cursor.connection)
                return total, inserted, duplicates

            # Initialize counters and data collection
            total_api_records_fetched = 0
            total_sql_inserted_count = 0
            total_sql_duplicate_count = 0

            # Process repositories for database mode
            logging.info(f"Starting data extraction from {last_modified_date}")
            for repo_name in self.repositories:
                repo_name = repo_name.strip()

                logging.info(f"Fetching data from https://api.github.com/repos/{self.github_owner}/{repo_name}")

                try:
                    # Process pull requests and get actual counts
                    pr_data_count, pr_inserted, pr_duplicates = self.process_pull_requests(cursor, repo_name, last_modified_date, [0])
                    total_api_records_fetched += pr_data_count
                    total_sql_inserted_count += pr_inserted
                    total_sql_duplicate_count += pr_duplicates

                    # Process cherry picks and get actual counts
                    cp_data_count, cp_inserted, cp_duplicates = self.process_cherry_picks(cursor, self.github_owner, repo_name)
                    total_api_records_fetched += cp_data_count
                    total_sql_inserted_count += cp_inserted
                    total_sql_duplicate_count += cp_duplicates

                except Exception as e:
                    logging.error(f"Error processing repository {self.github_owner}/{repo_name}: {str(e)}")
                    continue

            # Print summary statistics
            if total_api_records_fetched > 0:
                logging.info(f"Fetched {total_api_records_fetched} records from API")

            logging.info(f"Inserted {total_sql_inserted_count} records in database, skipped {total_sql_duplicate_count} duplicate records.")

    def process_pull_requests_for_csv(self, repo_name, last_modified_date, save_output_fn):
        """Process pull requests for CSV mode."""
        page = 1
        max_retries = 3
        retry_delay = 1
        total_inserted = 0
        total_duplicates = 0
        total_data_count = 0

        while True:
            pull_requests_url = f"https://api.github.com/repos/{self.github_owner}/{repo_name}/pulls?state=all&per_page=100&page={page}&sort=created&direction=desc"

            for attempt in range(max_retries):
                try:
                    response = requests.get(pull_requests_url, headers=self.headers, timeout=30)

                    if response.status_code == 200:
                        pull_requests = response.json()
                        if isinstance(pull_requests, list):
                            if not pull_requests:
                                return total_data_count, total_inserted, total_duplicates

                            # Check if we've gone past our date range
                            first_pr_date = pull_requests[0].get('created_at')
                            if first_pr_date:
                                first_pr_datetime = datetime.datetime.strptime(first_pr_date, "%Y-%m-%dT%H:%M:%SZ")
                                start_date_datetime = datetime.datetime.strptime(last_modified_date.split(' ')[0], "%Y-%m-%d")
                                if first_pr_datetime.date() < start_date_datetime.date():
                                    logging.info(f"Reached PRs older than {last_modified_date.split(' ')[0]}, stopping processing")
                                    return total_data_count, total_inserted, total_duplicates

                            # Process this page of pull requests
                            pr_data = []
                            for pr in pull_requests:
                                data = extract_pull_request_data(pr, repo_name)
                                pr_data.extend(data)

                            # Save this page's data
                            data_count, inserted, duplicates = save_output_fn(pr_data)
                            total_data_count += data_count
                            total_inserted += inserted
                            total_duplicates += duplicates

                            if page % 10 == 0:
                                logging.info(f"Processed {page} pages of pull requests ({total_inserted} inserted, {total_duplicates} duplicates)")

                            page += 1
                            break
                        else:
                            logging.warning(f"Unexpected response format for pull requests in {self.github_owner}/{repo_name}: {pull_requests}")
                            return total_data_count, total_inserted, total_duplicates

                    elif response.status_code == 403:
                        if 'X-RateLimit-Reset' in response.headers:
                            reset_time = int(response.headers['X-RateLimit-Reset'])
                            wait_time = reset_time - int(time.time()) + 10
                            logging.warning(f"Rate limit exceeded. Waiting {wait_time} seconds...")
                            time.sleep(wait_time)
                            continue
                        else:
                            logging.warning(f"Rate limit exceeded for {self.github_owner}/{repo_name}")
                            return total_data_count, total_inserted, total_duplicates

                    else:
                        logging.error(f"Failed to fetch pull requests for {self.github_owner}/{repo_name}: {response.status_code} - {response.text}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay * (2 ** attempt))
                            continue
                        else:
                            return total_data_count, total_inserted, total_duplicates

                except requests.exceptions.RequestException as e:
                    logging.error(f"Request failed for page {page} (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (2 ** attempt))
                        continue
                    else:
                        return total_data_count, total_inserted, total_duplicates

        return total_data_count, total_inserted, total_duplicates

    def process_cherry_picks_for_csv(self, repo_name, save_output_fn):
        """Process cherry picks for CSV mode."""
        release_branches = self.get_release_branches(self.github_owner, repo_name)
        cherry_pick_data = []

        # Process each release branch
        for release_branch in release_branches:
            commits = self.get_commits(self.github_owner, repo_name, release_branch)

            for commit in commits:
                commit_sha = commit['sha']
                commit_message = commit['commit']['message']
                commit_timestamp = commit['commit']['committer']['date']
                author_name = commit['commit'].get('committer', {}).get('name', '')

                # Extract pull request number and work item ID from commit message
                pull_request_number, work_item_id = process_commit_message(commit_message)

                if work_item_id or pull_request_number:
                    # Convert commit timestamp to UTC datetime
                    timestamp_dt = datetime.datetime.strptime(commit_timestamp, '%Y-%m-%dT%H:%M:%SZ')
                    extended_attrs = {'pull_request_number': pull_request_number} if pull_request_number else None
                    event = CodeCommitEvent.create_event(
                        timestamp_utc=timestamp_dt,
                        repo_name=repo_name,
                        event_type='Pull Request Cherry-picked',
                        source_branch='',
                        target_branch=release_branch,
                        revision=commit_sha,
                        author=author_name,
                        comment=commit_message,
                        extended_attributes=extended_attrs
                    )
                    cherry_pick_data.append(event)

        # Save cherry-pick data
        return save_output_fn(cherry_pick_data)

    def get_config_from_database(self, cursor):
        """Fetch GitHub configuration from data_source_config table."""
        cursor.execute("""
            SELECT config_item, config_value
            FROM data_source_config
            WHERE data_source = 'source_code_revision_control'
            AND config_item IN ('Organization', 'Repos', 'Personal Access Token')
        """)

        config = {}
        for row in cursor.fetchall():
            config[row[0]] = row[1]

        return config

    def get_last_modified_date(self, cursor):
        last_modified_dt = CodeCommitEvent.get_last_event(cursor)
        if last_modified_dt:
            # Ensure naive UTC
            if last_modified_dt.tzinfo is not None:
                last_modified_dt = last_modified_dt.replace(tzinfo=None)
            return last_modified_dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        return "2020-01-01 00:00:00.000"  # Default to a far-past date

    def insert_into_pull_request(self, cursor, data, last_modified_date):
        """Deprecated: use CodeCommitEvent.save_events_to_database via save_output_fn instead."""
        # Convert legacy tuple data to dict events if needed and delegate to save_output_fn callers.
        filtered_events = []
        try:
            last_modified_datetime = datetime.datetime.strptime(last_modified_date, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            last_modified_datetime = None
        for row in data:
            # Expecting dict events already; if tuple, skip here (legacy path)
            if isinstance(row, dict):
                event_dt = row.get('timestamp_utc')
                if isinstance(event_dt, str):
                    try:
                        event_dt = datetime.datetime.strptime(event_dt, "%Y-%m-%d %H:%M:%S.%f")
                    except ValueError:
                        event_dt = None
                if not last_modified_datetime or (event_dt and event_dt >= last_modified_datetime):
                    filtered_events.append(row)
        if not filtered_events:
            return 0, 0, 0
        return CodeCommitEvent.save_events_to_database(filtered_events, cursor, cursor.connection)

    def process_pull_requests(self, cursor, repo_name, last_modified_date, exit_code_ref):
        page = 1
        max_retries = 3
        retry_delay = 1  # seconds
        total_inserted = 0
        total_duplicates = 0
        total_data_count = 0

        while True:
            # Use regular API with sorting for better performance
            pull_requests_url = f"https://api.github.com/repos/{self.github_owner}/{repo_name}/pulls?state=all&per_page=100&page={page}&sort=created&direction=desc"

            # Retry logic for failed requests
            for attempt in range(max_retries):
                try:
                    response = requests.get(pull_requests_url, headers=self.headers, timeout=30)

                    if response.status_code == 200:
                        pull_requests = response.json()
                        # Check if pull_requests is a list (successful response) or dict (error response)
                        if isinstance(pull_requests, list):
                            if not pull_requests:  # If no more PRs, break out of the loop
                                return total_data_count, total_inserted, total_duplicates

                            # Check if we've gone past our date range (since we're sorted by created desc)
                            first_pr_date = pull_requests[0].get('created_at')
                            if first_pr_date:
                                first_pr_datetime = datetime.datetime.strptime(first_pr_date, "%Y-%m-%dT%H:%M:%SZ")
                                start_date_datetime = datetime.datetime.strptime(last_modified_date.split(' ')[0], "%Y-%m-%d")
                                if first_pr_datetime.date() < start_date_datetime.date():
                                    # We've gone past our date range, stop processing
                                    logging.info(f"Reached PRs older than {last_modified_date.split(' ')[0]}, stopping processing")
                                    return total_data_count, total_inserted, total_duplicates

                            # Process this page of pull requests
                            pr_data = []
                            for pr in pull_requests:
                                data = extract_pull_request_data(pr, repo_name)
                                pr_data.extend(data)

                            # Insert this page's data immediately using common saver
                            data_count, inserted, duplicates = CodeCommitEvent.save_events_to_database(pr_data, cursor, cursor.connection)
                            total_data_count += data_count
                            total_inserted += inserted
                            total_duplicates += duplicates

                            # Log progress every 10 pages
                            if page % 10 == 0:
                                logging.info(f"Processed {page} pages of pull requests ({total_inserted} inserted, {total_duplicates} duplicates)")

                            page += 1
                            break
                        else:
                            logging.warning(f"Unexpected response format for pull requests in {self.github_owner}/{repo_name}: {pull_requests}")
                            return total_data_count, total_inserted, total_duplicates

                    elif response.status_code == 403:
                        # Rate limit exceeded
                        if 'X-RateLimit-Reset' in response.headers:
                            reset_time = int(response.headers['X-RateLimit-Reset'])
                            wait_time = reset_time - int(time.time()) + 10  # Add 10 seconds buffer
                            logging.warning(f"Rate limit exceeded. Waiting {wait_time} seconds...")
                            time.sleep(wait_time)
                            continue
                        else:
                            logging.warning(f"Rate limit exceeded for {self.github_owner}/{repo_name}")
                            return total_data_count, total_inserted, total_duplicates

                    else:
                        logging.error(f"Failed to fetch pull requests for {self.github_owner}/{repo_name}: {response.status_code} - {response.text}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                            continue
                        else:
                            # API error - log error and set exit code but preserve partial data
                            logging.error(f"Max retries exceeded for page {page}. Preserving partial data but marking as failed.")
                            exit_code_ref[0] = 1  # Set exit code to 1 for API error
                            return total_data_count, total_inserted, total_duplicates

                except requests.exceptions.RequestException as e:
                    logging.error(f"Request failed for page {page} (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                        continue
                    else:
                        logging.error(f"Max retries exceeded for page {page}. Preserving partial data but marking as failed.")
                        exit_code_ref[0] = 1  # Set exit code to 1 for API error
                        return total_data_count, total_inserted, total_duplicates

        return total_data_count, total_inserted, total_duplicates

    def process_cherry_picks(self, cursor, organization, repo):
        release_branches = self.get_release_branches(organization, repo)
        cherry_pick_data = []

        # Process each release branch
        for release_branch in release_branches:
            # Get the commits for this release branch
            commits = self.get_commits(organization, repo, release_branch)

            for commit in commits:
                commit_sha = commit['sha']
                commit_message = commit['commit']['message']
                commit_timestamp = commit['commit']['committer']['date']
                author_name = commit['commit'].get('committer', {}).get('name', '')

                # Extract pull request number and work item ID from commit message
                pull_request_number, work_item_id = process_commit_message(commit_message)

                if work_item_id or pull_request_number:
                    # Convert commit timestamp to UTC datetime
                    timestamp_dt = datetime.datetime.strptime(commit_timestamp, '%Y-%m-%dT%H:%M:%SZ')
                    extended_attrs = {'pull_request_number': pull_request_number} if pull_request_number else None
                    event = CodeCommitEvent.create_event(
                        timestamp_utc=timestamp_dt,
                        repo_name=repo,
                        event_type='Pull Request Cherry-picked',
                        source_branch='',
                        target_branch=release_branch,
                        revision=commit_sha,
                        author=author_name,
                        comment=commit_message,
                        extended_attributes=extended_attrs
                    )
                    cherry_pick_data.append(event)

        # Batch insert all cherry-pick data and return counts using common saver
        if not cherry_pick_data:
            return 0, 0, 0
        return CodeCommitEvent.save_events_to_database(cherry_pick_data, cursor, cursor.connection)

    def get_release_branches(self, organization, repo):
        """Get the list of release branches in the repository."""
        url = f'https://api.github.com/repos/{organization}/{repo}/branches'

        for attempt in range(3):  # Max 3 retries
            try:
                response = requests.get(url, headers=self.headers, timeout=30)

                if response.status_code == 200:
                    branches = response.json()
                    # Check if branches is a list (successful response) or dict (error response)
                    if isinstance(branches, list):
                        release_branches = [branch['name'] for branch in branches if branch['name'].startswith('release/')]
                        return release_branches
                    else:
                        logging.warning(f"Unexpected response format for branches in {organization}/{repo}: {branches}")
                        return []
                elif response.status_code == 403:
                    # Rate limit exceeded
                    if 'X-RateLimit-Reset' in response.headers:
                        reset_time = int(response.headers['X-RateLimit-Reset'])
                        wait_time = reset_time - int(time.time()) + 10
                        logging.warning(f"Rate limit exceeded. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logging.warning(f"Rate limit exceeded for {organization}/{repo}")
                        return []
                else:
                    logging.warning(f"Failed to fetch branches for {organization}/{repo}: {response.status_code} - {response.text}")
                    if attempt < 2:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        return []

            except requests.exceptions.RequestException as e:
                logging.warning(f"Request failed for branches (attempt {attempt + 1}): {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return []

        return []

    def get_commits(self, organization, repo, branch):
        """Get the commits from the branch."""
        url = f'https://api.github.com/repos/{organization}/{repo}/commits?sha={branch}'
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            commits = response.json()
            # Check if commits is a list (successful response) or dict (error response)
            if isinstance(commits, list):
                return commits
            else:
                logging.warning(f"Unexpected response format for commits in {organization}/{repo}/{branch}: {commits}")
                return []
        else:
            logging.warning(f"Failed to fetch commits for {organization}/{repo}/{branch}: {response.status_code} - {response.text}")
            return []

    def insert_cherry_picks_batch(self, cursor, cherry_pick_data):
        """Insert cherry-pick records into the database using batch insertion."""
        if not cherry_pick_data:
            return 0, 0, 0

        from psycopg2.extras import execute_values

        # Use execute_values for batch insertion
        columns = [
            'pull_request_number', 'repo', 'event', 'target_branch', 'revision', 'timestamp_utc', 'comment'
        ]

        # Get count before insertion
        cursor.execute("SELECT COUNT(*) FROM code_commit_event")
        count_before = cursor.fetchone()[0]

        execute_values(
            cursor,
            f"INSERT INTO code_commit_event ({', '.join(columns)}) VALUES %s ON CONFLICT DO NOTHING",
            cherry_pick_data,
            template=None,
            page_size=1000
        )

        # Get count after insertion to determine actual inserted records
        cursor.execute("SELECT COUNT(*) FROM code_commit_event")
        count_after = cursor.fetchone()[0]

        # Calculate actual inserted and skipped records
        inserted_count = count_after - count_before
        duplicate_count = len(cherry_pick_data) - inserted_count

        return len(cherry_pick_data), inserted_count, duplicate_count


# Step 1: GitHub API Authentication - Configuration will be loaded from database
github_owner = None
repositories = None
personal_access_token = None
headers = None








# Step 6: Extract and format pull request data for each stage (created, merged, closed)
def extract_pull_request_data(pr, repo_name):
    pull_request_number = pr['number']
    title = pr.get('title', '')
    actor = pr.get('user', {}).get('login', '')
    base_branch = pr.get('base', {}).get('ref', '')
    head_branch = pr.get('head', {}).get('ref', '')
    head_sha = pr.get('head', {}).get('sha', '')

    # Do not set work_item_id in extractor

    created_at_dt = Utils.convert_to_utc(pr.get('created_at'))
    merged_at_dt = Utils.convert_to_utc(pr.get('merged_at')) if pr.get('merged_at') else None
    closed_at_dt = Utils.convert_to_utc(pr.get('closed_at')) if pr.get('closed_at') else None

    extended_attrs = {
        'pull_request_number': pull_request_number,
        'pull_request_title': title
    }

    data = []
    if created_at_dt:
        data.append(CodeCommitEvent.create_event(
            timestamp_utc=created_at_dt,
            repo_name=repo_name,
            event_type='Pull Request Created',
            source_branch=head_branch,
            target_branch=base_branch,
            revision=head_sha,
            author=actor,
            comment=title,
            extended_attributes=extended_attrs
        ))

    if merged_at_dt:
        data.append(CodeCommitEvent.create_event(
            timestamp_utc=merged_at_dt,
            repo_name=repo_name,
            event_type='Pull Request Merged',
            source_branch=head_branch,
            target_branch=base_branch,
            revision=head_sha,
            author=actor,
            comment=title,
            extended_attributes=extended_attrs
        ))

    if closed_at_dt:
        data.append(CodeCommitEvent.create_event(
            timestamp_utc=closed_at_dt,
            repo_name=repo_name,
            event_type='Pull Request Closed',
            source_branch=head_branch,
            target_branch=base_branch,
            revision=head_sha,
            author=actor,
            comment=title,
            extended_attributes=extended_attrs
        ))

    return data





def process_commit_message(commit_message):
    """Extract pull request number and work item ID from commit message."""
    pull_request_number = None
    work_item_id = None
    # Match the pattern 'Merge pull request #<pull_request_number> from <head_branch_prefix>/<work_item_id>'
    match = re.search(r'Merge pull request #(\d+) from .*/(\d+)', commit_message)
    if match:
        pull_request_number = match.group(1)
        work_item_id = match.group(2)
    return pull_request_number, work_item_id





def main():
    # Main Execution
    parser = argparse.ArgumentParser(description="Add new events in the code_commit_event table.")

    # Add command-line arguments
    parser.add_argument('-p', '--product', type=str, help='Product name (if provided, saves to database; otherwise saves to CSV)')
    parser.add_argument('-s', '--start-date', type=str, help='Start date in YYYY-MM-DD format')
    args = parser.parse_args()
    product = args.product
    start_date = args.start_date

    extractor = GitHubExtractor()

    if product is None:
        # CSV Mode: Load configuration from config.json
        config = json.load(open(os.path.join(common_dir, "config.json")))
        
        # Get configuration from config dictionary
        config = {
            'Organization': config.get('GITHUB_ORGANIZATION'),
            'Repos': config.get('GITHUB_REPOS'),
            'Personal Access Token': config.get('GITHUB_API_TOKEN')
        }

        # Use checkpoint file for last modified date
        last_modified = Utils.load_checkpoint("github")

        extractor.run_extraction(None, config, start_date, last_modified)

    else:
        # Database Mode: Connect to the database
        from database import DatabaseConnection
        db = DatabaseConnection()
        with db.product_scope(product) as conn:
            with conn.cursor() as cursor:
                config = extractor.get_config_from_database(cursor)
                last_modified = extractor.get_last_modified_date(cursor)
                extractor.run_extraction(cursor, config, start_date, last_modified)

    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
