#!/bin/bash

# Remote Setup Script for Node.js and Dependencies
# This script sets up Node.js, npm, and other dependencies on the Ubuntu EC2 instance

# Configuration
EC2_HOST="18.117.154.176"
EC2_USER="ubuntu"
EC2_DNS="ec2-18-117-154-176.us-east-2.compute.amazonaws.com"
SSH_KEY="aqclaude.pem"
REMOTE_DIR="/home/ubuntu/code-conv-studio"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${2}${1}${NC}"
}

# Function to run SSH commands
run_ssh() {
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" "$1"
}

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    print_status "Error: SSH key file '$SSH_KEY' not found!" "$RED"
    exit 1
fi

# Set correct permissions for SSH key
chmod 400 "$SSH_KEY"

print_status "Starting remote setup on Ubuntu EC2 instance..." "$BLUE"

# Update system packages
print_status "Updating system packages..." "$YELLOW"
run_ssh "sudo apt-get update -y"

# Install curl and other essential tools
print_status "Installing essential tools..." "$YELLOW"
run_ssh "sudo apt-get install -y curl wget git build-essential"

# Install Node.js using NodeSource repository (latest LTS version)
print_status "Installing Node.js (latest LTS)..." "$YELLOW"
run_ssh "curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -"
run_ssh "sudo apt-get install -y nodejs"

# Verify Node.js and npm installation
print_status "Verifying Node.js and npm installation..." "$YELLOW"
NODE_VERSION=$(run_ssh "node --version" 2>&1)
NPM_VERSION=$(run_ssh "npm --version" 2>&1)

print_status "Node.js version: $NODE_VERSION" "$GREEN"
print_status "npm version: $NPM_VERSION" "$GREEN"

# Install global npm packages that might be useful
print_status "Installing useful global npm packages..." "$YELLOW"
run_ssh "sudo npm install -g pm2 nodemon typescript ts-node"

# Install Python and pip (often needed for some npm packages)
print_status "Installing Python and pip..." "$YELLOW"
run_ssh "sudo apt-get install -y python3 python3-pip python3-dev"

# Install other common dependencies
print_status "Installing additional dependencies..." "$YELLOW"
run_ssh "sudo apt-get install -y redis-server postgresql-client mysql-client"

# Create project directory if it doesn't exist
print_status "Setting up project directory..." "$YELLOW"
run_ssh "mkdir -p $REMOTE_DIR"

# Check if package.json exists and install dependencies
print_status "Checking for project dependencies..." "$YELLOW"
if run_ssh "[ -f $REMOTE_DIR/package.json ]"; then
    print_status "Found package.json, installing project dependencies..." "$YELLOW"
    run_ssh "cd $REMOTE_DIR && npm install"
else
    print_status "No package.json found in project directory" "$YELLOW"
fi

# Set up environment for PM2 (process manager)
print_status "Setting up PM2 for process management..." "$YELLOW"
run_ssh "pm2 startup systemd -u $EC2_USER --hp /home/$EC2_USER"

# Display system information
print_status "\nSystem setup completed!" "$GREEN"
print_status "=======================" "$GREEN"
run_ssh "echo 'Node.js version:' && node --version"
run_ssh "echo 'npm version:' && npm --version"
run_ssh "echo 'Python version:' && python3 --version"
run_ssh "echo 'Git version:' && git --version"

print_status "\nGlobal npm packages installed:" "$GREEN"
run_ssh "npm list -g --depth=0"

print_status "\nYou can now deploy and run your application!" "$GREEN"
print_status "SSH into the server: ssh -i \"$SSH_KEY\" $EC2_USER@$EC2_DNS" "$BLUE"