#!/bin/bash

# Comprehensive Setup Script for Fresh Ubuntu EC2 Instance
# This script handles full system updates and Node.js installation

# Configuration
EC2_HOST="18.117.154.176"
EC2_USER="ubuntu"
EC2_DNS="ec2-18-117-154-176.us-east-2.compute.amazonaws.com"
SSH_KEY="aqclaude.pem"

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

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    print_status "Error: SSH key file '$SSH_KEY' not found!" "$RED"
    exit 1
fi

# Set correct permissions for SSH key
chmod 400 "$SSH_KEY"

print_status "Starting comprehensive setup on fresh Ubuntu EC2 instance..." "$BLUE"
print_status "This will take several minutes as we update the system and install Node.js" "$YELLOW"

# Create setup script content
SETUP_SCRIPT='#!/bin/bash

# Update and upgrade system
echo "======================================"
echo "Step 1: Updating package lists..."
echo "======================================"
sudo apt-get update -y

echo "======================================"
echo "Step 2: Upgrading system packages..."
echo "======================================"
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

echo "======================================"
echo "Step 3: Installing essential packages..."
echo "======================================"
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    ca-certificates \
    gnupg \
    lsb-release \
    software-properties-common

echo "======================================"
echo "Step 4: Installing Node.js via NodeSource..."
echo "======================================"
# Install Node.js 20.x LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs

echo "======================================"
echo "Step 5: Verifying installations..."
echo "======================================"
echo "Node.js version:"
node --version
echo ""
echo "npm version:"
npm --version
echo ""

echo "======================================"
echo "Step 6: Installing global npm packages..."
echo "======================================"
sudo npm install -g pm2 nodemon

echo "======================================"
echo "Step 7: Installing additional development tools..."
echo "======================================"
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    make \
    g++

echo "======================================"
echo "Setup completed successfully!"
echo "======================================"
echo "System information:"
echo "- Node.js: $(node --version)"
echo "- npm: $(npm --version)"
echo "- Python: $(python3 --version)"
echo "- Git: $(git --version)"
echo "======================================"
'

# Copy setup script to remote server and execute it
print_status "Copying setup script to remote server..." "$YELLOW"
echo "$SETUP_SCRIPT" | ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" "cat > /tmp/setup.sh && chmod +x /tmp/setup.sh"

print_status "Executing setup script (this will take several minutes)..." "$YELLOW"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -t "$EC2_USER@$EC2_DNS" "sudo /tmp/setup.sh"

# Clean up
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" "rm -f /tmp/setup.sh"

print_status "\nSetup completed! Your Ubuntu system now has:" "$GREEN"
print_status "- Latest system updates" "$GREEN"
print_status "- Node.js 20.x LTS" "$GREEN"
print_status "- npm package manager" "$GREEN"
print_status "- Essential development tools" "$GREEN"
print_status "\nYou can now deploy your application using ./deploy.sh" "$BLUE"