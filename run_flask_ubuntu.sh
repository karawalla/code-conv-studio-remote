#!/bin/bash
# This script runs Flask as ubuntu user on port 80 using authbind

# Install authbind if not present
if ! command -v authbind &> /dev/null; then
    echo "Installing authbind..."
    sudo apt-get update && sudo apt-get install -y authbind
fi

# Configure authbind for port 80
sudo touch /etc/authbind/byport/80
sudo chown ubuntu:ubuntu /etc/authbind/byport/80
sudo chmod 755 /etc/authbind/byport/80

# Stop existing Flask processes
sudo pkill -f "python.*app.py" || true
sleep 2

# Run Flask as ubuntu user with authbind
cd /home/ubuntu/code-conv-studio
echo "Starting Flask as ubuntu user on port 80..."
authbind --deep python3 app.py > flask_ubuntu.log 2>&1 &
echo "Flask started with PID: $!"

sleep 3
echo "Checking if Flask is running:"
ps aux | grep "python3 app.py" | grep -v grep
netstat -tlnp 2>/dev/null | grep :80
