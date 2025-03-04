#!/bin/bash

# Create backup directory with timestamp
BACKUP_DIR=~/2dto3d_backup_$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
echo "Created backup directory: $BACKUP_DIR"

# Function to backup and remove
backup_and_remove() {
    if [ -e "$1" ]; then
        echo "Backing up: $1"
        cp -r "$1" "$BACKUP_DIR/"
        echo "Removing: $1"
        rm -rf "$1"
    fi
}

# Temporary/Cache files
echo -e "\nProcessing temporary files..."
backup_and_remove ".nano.swp"
backup_and_remove ".sudo.swp"
backup_and_remove "__pycache__"
backup_and_remove "temp"
backup_and_remove "test.blend"
backup_and_remove "test.blend1"
backup_and_remove "test_image.png"
backup_and_remove "test_sdk.py"

# Unused/Old directories
echo -e "\nProcessing unused directories..."
backup_and_remove "components"
backup_and_remove "config"
backup_and_remove "output"  # but not outputs/
backup_and_remove "services"
backup_and_remove "templates"
backup_and_remove "test"
backup_and_remove "utils"

# Unused files
echo -e "\nProcessing unused files..."
backup_and_remove "analysis.json"
backup_and_remove "server.ts"

echo -e "\nBackup complete. Files are stored in: $BACKUP_DIR"
echo "Please verify the backup before permanent deletion."
echo -e "\nFiles that were backed up:"
ls -la $BACKUP_DIR

echo -e "\nTo restore any files, use:"
echo "cp -r $BACKUP_DIR/<file_or_directory> /home/mml_admin/2dto3d/" 