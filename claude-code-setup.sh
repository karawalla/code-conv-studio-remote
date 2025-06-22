#!/bin/bash

# Claude Code Setup Script for Ubuntu EC2
# This script installs Claude Code CLI and sets up authentication

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
CYAN='\033[0;36m'
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

print_status "Setting up Claude Code on Ubuntu EC2 instance..." "$BLUE"

# Step 1: Install Claude Code via npm
print_status "\nStep 1: Installing Claude Code CLI..." "$YELLOW"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" "sudo npm install -g @anthropic-ai/claude-code"

# Step 2: Verify installation
print_status "\nStep 2: Verifying Claude Code installation..." "$YELLOW"
CLAUDE_VERSION=$(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" "claude --version" 2>&1)
if [[ $? -eq 0 ]]; then
    print_status "Claude Code installed successfully!" "$GREEN"
    print_status "Version: $CLAUDE_VERSION" "$GREEN"
else
    print_status "Error: Claude Code installation failed!" "$RED"
    exit 1
fi

# Step 3: Set up authentication
print_status "\nStep 3: Setting up authentication..." "$YELLOW"
print_status "You'll need your Anthropic API key to authenticate Claude Code." "$CYAN"
print_status "Get your API key from: https://console.anthropic.com/account/keys" "$CYAN"
echo ""
read -p "Enter your Anthropic API key: " API_KEY

if [ -z "$API_KEY" ]; then
    print_status "Error: API key cannot be empty!" "$RED"
    exit 1
fi

# Set up the API key on the remote system
print_status "\nConfiguring API key on remote system..." "$YELLOW"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" "export ANTHROPIC_API_KEY='$API_KEY' && echo 'export ANTHROPIC_API_KEY=\"$API_KEY\"' >> ~/.bashrc"

# Create a Claude Code configuration directory
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" "mkdir -p ~/.config/claude-code"

# Step 4: Test authentication
print_status "\nStep 4: Testing Claude Code authentication..." "$YELLOW"
TEST_RESULT=$(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" "source ~/.bashrc && claude --version" 2>&1)
if [[ $? -eq 0 ]]; then
    print_status "Authentication successful!" "$GREEN"
else
    print_status "Warning: Could not verify authentication. You may need to run 'source ~/.bashrc' on the remote system." "$YELLOW"
fi

# Step 5: Create helper script on remote
print_status "\nStep 5: Creating helper script on remote system..." "$YELLOW"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" 'cat > ~/claude-code-test.sh << "EOF"
#!/bin/bash
# Quick test script for Claude Code

echo "Testing Claude Code CLI..."
source ~/.bashrc

if command -v claude &> /dev/null; then
    echo "Claude Code is installed!"
    claude --version
    echo ""
    echo "Try running: claude --help"
    echo "Or start a chat with: claude chat"
else
    echo "Error: Claude Code not found. Try running: source ~/.bashrc"
fi
EOF
chmod +x ~/claude-code-test.sh'

print_status "\nSetup completed!" "$GREEN"
print_status "===========================================" "$GREEN"
print_status "Claude Code has been installed on your EC2 instance!" "$GREEN"
print_status "" "$NC"
print_status "To use Claude Code on the remote system:" "$CYAN"
print_status "1. SSH into the server: ssh -i \"$SSH_KEY\" $EC2_USER@$EC2_DNS" "$CYAN"
print_status "2. Run: source ~/.bashrc" "$CYAN"
print_status "3. Test with: claude --help" "$CYAN"
print_status "" "$NC"
print_status "Quick test: ~/claude-code-test.sh" "$CYAN"
print_status "===========================================" "$GREEN"