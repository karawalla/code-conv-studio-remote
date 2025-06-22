#!/bin/bash

# Deploy Code Conversion Studio App
# This script deploys the entire application including the Spring Boot example

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

print_status "Deploying Code Conversion Studio to EC2..." "$BLUE"

# Step 1: Create remote directory
print_status "Creating remote directory structure..." "$YELLOW"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" "mkdir -p $REMOTE_DIR"

# Step 2: Create a Flask app.py file
print_status "Creating Flask application file..." "$YELLOW"
cat > /tmp/app.py << 'EOF'
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import os
import json
import shutil
from datetime import datetime
import subprocess
import threading
import queue

app = Flask(__name__)
CORS(app)

# Configuration
INPUT_DIR = os.path.join(os.path.dirname(__file__), 'input')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
WORKING_DIR = os.path.join(os.path.dirname(__file__), 'working')

# Ensure directories exist
for dir_path in [INPUT_DIR, OUTPUT_DIR, WORKING_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Global processing queue
processing_queue = queue.Queue()
processing_status = {"status": "idle", "message": "Ready"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(processing_status)

@app.route('/api/check-input', methods=['POST'])
def check_input():
    try:
        input_path = request.json.get('path', INPUT_DIR)
        if not os.path.exists(input_path):
            return jsonify({"status": "error", "message": "Input directory not found"}), 404
        
        files = []
        for root, dirs, filenames in os.walk(input_path):
            for filename in filenames:
                if not filename.startswith('.'):
                    rel_path = os.path.relpath(os.path.join(root, filename), input_path)
                    files.append(rel_path)
        
        return jsonify({
            "status": "success",
            "path": input_path,
            "files": files,
            "count": len(files)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/cleanup-output', methods=['POST'])
def cleanup_output():
    try:
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        return jsonify({"status": "success", "message": "Output directory cleaned"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/list-folders', methods=['GET'])
def list_folders():
    try:
        path = request.args.get('path', '/')
        if not os.path.exists(path):
            path = '/'
        
        folders = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                folders.append({
                    "name": item,
                    "path": item_path
                })
        
        return jsonify({
            "status": "success",
            "current_path": path,
            "folders": sorted(folders, key=lambda x: x['name'].lower())
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/list-files', methods=['GET'])
def list_files():
    try:
        directory = request.args.get('directory', 'output')
        path = request.args.get('path', '')
        
        if directory == 'input':
            base_dir = INPUT_DIR
        else:
            base_dir = OUTPUT_DIR
        
        full_path = os.path.join(base_dir, path) if path else base_dir
        
        if not os.path.exists(full_path):
            return jsonify({"status": "success", "items": []})
        
        items = []
        for item in os.listdir(full_path):
            if not item.startswith('.'):
                item_path = os.path.join(full_path, item)
                rel_path = os.path.relpath(item_path, base_dir)
                
                if os.path.isdir(item_path):
                    items.append({
                        "name": item,
                        "type": "folder",
                        "path": rel_path
                    })
                else:
                    items.append({
                        "name": item,
                        "type": "file",
                        "path": rel_path,
                        "size": os.path.getsize(item_path)
                    })
        
        return jsonify({
            "status": "success",
            "items": sorted(items, key=lambda x: (x['type'] != 'folder', x['name'].lower()))
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/read-file', methods=['GET'])
def read_file():
    try:
        directory = request.args.get('directory', 'output')
        path = request.args.get('path', '')
        
        if directory == 'input':
            base_dir = INPUT_DIR
        else:
            base_dir = OUTPUT_DIR
        
        full_path = os.path.join(base_dir, path)
        
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            return jsonify({"status": "error", "message": "File not found"}), 404
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            "status": "success",
            "content": content,
            "filename": os.path.basename(path)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process():
    try:
        data = request.json
        query = data.get('query', '')
        selected_folder = data.get('selectedFolder', INPUT_DIR)
        
        # Update status
        processing_status["status"] = "processing"
        processing_status["message"] = f"Processing with query: {query}"
        
        # Here you would implement the actual processing logic
        # For now, we'll create a sample output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(OUTPUT_DIR, f"ship_output_{timestamp}.json")
        
        sample_output = {
            "query": query,
            "input_folder": selected_folder,
            "timestamp": timestamp,
            "status": "completed",
            "message": "Processing completed successfully"
        }
        
        with open(output_file, 'w') as f:
            json.dump(sample_output, f, indent=2)
        
        # Update status
        processing_status["status"] = "completed"
        processing_status["message"] = "Processing completed successfully"
        
        return jsonify({
            "status": "success",
            "output_file": f"ship_output_{timestamp}.json"
        })
    except Exception as e:
        processing_status["status"] = "error"
        processing_status["message"] = str(e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)
EOF

# Step 3: Copy all files to remote server
print_status "Creating deployment archive..." "$YELLOW"
tar -czf /tmp/${PROJECT_NAME}-deploy.tar.gz \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.pem' \
    --exclude='creds.md' \
    --exclude='.env*' \
    --exclude='target' \
    --exclude='*.log' \
    --exclude='.DS_Store' \
    .

# Step 4: Upload to server
print_status "Uploading application files..." "$YELLOW"
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no /tmp/app.py "$EC2_USER@$EC2_DNS:$REMOTE_DIR/"
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no /tmp/${PROJECT_NAME}-deploy.tar.gz "$EC2_USER@$EC2_DNS:$REMOTE_DIR/"

# Step 5: Extract and setup on remote
print_status "Setting up application on remote server..." "$YELLOW"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" << 'REMOTE_COMMANDS'
cd /home/ubuntu/code-conv-studio
tar -xzf code-conv-studio-deploy.tar.gz
rm -f code-conv-studio-deploy.tar.gz

# Install Python dependencies
pip3 install flask flask-cors

# Create necessary directories
mkdir -p input output working static/css static/js templates

# Set permissions
chmod +x *.sh 2>/dev/null || true
REMOTE_COMMANDS

# Step 6: Create start script on remote
print_status "Creating start script on remote..." "$YELLOW"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" 'cat > /home/ubuntu/code-conv-studio/start-app.sh << "EOF"
#!/bin/bash

# Start Code Conversion Studio
cd /home/ubuntu/code-conv-studio

# Colors
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
NC="\033[0m"

echo -e "${GREEN}Starting Code Conversion Studio...${NC}"

# Check if already running
if pgrep -f "python3 app.py" > /dev/null; then
    echo -e "${YELLOW}Application is already running!${NC}"
    echo "Use ./stop-app.sh to stop it first"
    exit 1
fi

# Start in background
nohup python3 app.py > app.log 2>&1 &
APP_PID=$!

echo "Application started with PID: $APP_PID"
echo $APP_PID > app.pid

# Wait a moment for startup
sleep 3

# Check if running
if ps -p $APP_PID > /dev/null; then
    echo -e "${GREEN}✓ Application started successfully!${NC}"
    echo "URL: http://18.117.154.176:5003"
    echo "Logs: tail -f app.log"
else
    echo -e "${RED}✗ Failed to start application${NC}"
    echo "Check app.log for errors"
    exit 1
fi
EOF
chmod +x /home/ubuntu/code-conv-studio/start-app.sh'

# Step 7: Create stop script on remote
print_status "Creating stop script on remote..." "$YELLOW"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" 'cat > /home/ubuntu/code-conv-studio/stop-app.sh << "EOF"
#!/bin/bash

# Stop Code Conversion Studio
cd /home/ubuntu/code-conv-studio

# Colors
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
NC="\033[0m"

echo -e "${YELLOW}Stopping Code Conversion Studio...${NC}"

# Check if PID file exists
if [ -f app.pid ]; then
    APP_PID=$(cat app.pid)
    if ps -p $APP_PID > /dev/null 2>&1; then
        kill $APP_PID
        echo -e "${GREEN}✓ Application stopped (PID: $APP_PID)${NC}"
        rm -f app.pid
    else
        echo -e "${YELLOW}Process not found, cleaning up PID file${NC}"
        rm -f app.pid
    fi
else
    # Try to find process
    APP_PID=$(pgrep -f "python3 app.py")
    if [ ! -z "$APP_PID" ]; then
        kill $APP_PID
        echo -e "${GREEN}✓ Application stopped (PID: $APP_PID)${NC}"
    else
        echo -e "${YELLOW}Application is not running${NC}"
    fi
fi
EOF
chmod +x /home/ubuntu/code-conv-studio/stop-app.sh'

# Step 8: Create status script on remote
print_status "Creating status script on remote..." "$YELLOW"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_DNS" 'cat > /home/ubuntu/code-conv-studio/status-app.sh << "EOF"
#!/bin/bash

# Check status of Code Conversion Studio
cd /home/ubuntu/code-conv-studio

# Colors
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
NC="\033[0m"

echo -e "${BLUE}Code Conversion Studio Status${NC}"
echo "================================"

# Check if running
APP_PID=$(pgrep -f "python3 app.py")
if [ ! -z "$APP_PID" ]; then
    echo -e "Status: ${GREEN}Running${NC}"
    echo "PID: $APP_PID"
    echo "URL: http://18.117.154.176:5003"
    
    # Show memory usage
    ps -p $APP_PID -o pid,vsz,rss,comm
else
    echo -e "Status: ${RED}Not Running${NC}"
fi

echo ""
echo "Directories:"
echo "- Input: /home/ubuntu/code-conv-studio/input"
echo "- Output: /home/ubuntu/code-conv-studio/output"
echo "- Logs: /home/ubuntu/code-conv-studio/app.log"

if [ -f app.log ]; then
    echo ""
    echo "Recent logs:"
    tail -n 5 app.log
fi
EOF
chmod +x /home/ubuntu/code-conv-studio/status-app.sh'

# Clean up local temp files
rm -f /tmp/app.py /tmp/${PROJECT_NAME}-deploy.tar.gz

print_status "\nDeployment completed successfully!" "$GREEN"
print_status "===========================================" "$GREEN"
print_status "Application deployed to: $REMOTE_DIR" "$GREEN"
print_status "" "$NC"
print_status "To manage the application:" "$BLUE"
print_status "1. SSH into server: ssh -i \"$SSH_KEY\" $EC2_USER@$EC2_DNS" "$CYAN"
print_status "2. Navigate to: cd $REMOTE_DIR" "$CYAN"
print_status "3. Start app: ./start-app.sh" "$CYAN"
print_status "4. Stop app: ./stop-app.sh" "$CYAN"
print_status "5. Check status: ./status-app.sh" "$CYAN"
print_status "" "$NC"
print_status "Access the app at: http://$EC2_HOST:5003" "$GREEN"
print_status "===========================================" "$GREEN"