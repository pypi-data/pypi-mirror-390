#!/bin/bash

# Go to the directory where this script resides
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Loop through each system in DATA_SOURCE_SYSTEMS and execute corresponding extract script
IFS=',' read -ra SYSTEMS <<< "$DATA_SOURCE_SYSTEMS"
for system in "${SYSTEMS[@]}"; do
    # Trim whitespace from system name
    system=$(echo "$system" | xargs)
    
    # Execute the corresponding extract script
    extract_${system} >> "$SCRIPT_DIR/extract_${system}.log" 2>&1
done

sftp_upload >> "$SCRIPT_DIR/sftp_upload.log" 2>&1
