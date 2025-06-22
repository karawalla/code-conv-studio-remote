#!/bin/bash

# AWS Deployment Script for Code Conversion Studio
# This script uploads the project to an Ubuntu EC2 instance

# Configuration
EC2_HOST="18.117.154.176"
EC2_USER="ubuntu"
EC2_DNS="ec2-18-117-154-176.us-east-2.compute.amazonaws.com"
SSH_KEY="aqclaude.pem"
REMOTE_DIR="/home/ubuntu/code-conv-studio"
PROJECT_NAME="code-conv-studio"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${2}${1}${NC}"
}

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    print_status "Error: SSH key file '$SSH_KEY' not found!" "$RED"
    exit 1
fi

# Set correct permissions for SSH key
chmod 400 "$SSH_KEY"

# Create remote directory if it doesn't exist
print_status "Creating remote directory..." "$YELLOW"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" "mkdir -p $REMOTE_DIR"

if [ $? -ne 0 ]; then
    print_status "Error: Failed to create remote directory!" "$RED"
    exit 1
fi

# Create a temporary archive of the project (excluding certain files)
print_status "Creating project archive..." "$YELLOW"
tar -czf /tmp/${PROJECT_NAME}.tar.gz \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='*.log' \
    --exclude='*.pem' \
    --exclude='creds.md' \
    --exclude='.env*' \
    --exclude='dist' \
    --exclude='build' \
    --exclude='.DS_Store' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    .

if [ $? -ne 0 ]; then
    print_status "Error: Failed to create project archive!" "$RED"
    exit 1
fi

# Upload the archive to EC2
print_status "Uploading project to EC2 instance..." "$YELLOW"
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no /tmp/${PROJECT_NAME}.tar.gz "$EC2_USER@$EC2_DNS:$REMOTE_DIR/"

if [ $? -ne 0 ]; then
    print_status "Error: Failed to upload project archive!" "$RED"
    rm -f /tmp/${PROJECT_NAME}.tar.gz
    exit 1
fi

# Extract the archive on the remote server
print_status "Extracting project on remote server..." "$YELLOW"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" "cd $REMOTE_DIR && tar -xzf ${PROJECT_NAME}.tar.gz && rm -f ${PROJECT_NAME}.tar.gz"

if [ $? -ne 0 ]; then
    print_status "Error: Failed to extract project on remote server!" "$RED"
    rm -f /tmp/${PROJECT_NAME}.tar.gz
    exit 1
fi

# Clean up local temporary file
rm -f /tmp/${PROJECT_NAME}.tar.gz

# Optional: Install dependencies on remote server
print_status "Installing dependencies on remote server..." "$YELLOW"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" "cd $REMOTE_DIR && [ -f package.json ] && npm install || echo 'No package.json found, skipping npm install'"

print_status "Deployment completed successfully!" "$GREEN"
print_status "You can access the server using:" "$GREEN"
echo "ssh -i \"$SSH_KEY\" $EC2_USER@$EC2_DNS"
echo ""
print_status "Project deployed to: $REMOTE_DIR" "$GREEN"