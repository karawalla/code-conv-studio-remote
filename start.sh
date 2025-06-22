#!/bin/bash

# start.sh - Start Code Conversion Studio
# This script starts the Flask application with proper environment setup

echo "🚀 Starting Code Conversion Studio..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
check_port() {
    local port="$1"
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url="$1"
    local max_attempts=30
    local attempt=1

    echo "  Waiting for service to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo "  ✅ Service is ready!"
            return 0
        fi
        echo "  Attempt $attempt/$max_attempts - waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "  ⚠️  Service may not be fully ready yet"
    return 1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check if Python is available
if ! command_exists python && ! command_exists python3; then
    echo "  ❌ Python is not installed or not in PATH"
    echo "     Please install Python 3.7+ and try again"
    exit 1
fi

# Determine Python command
if command_exists python3; then
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_CMD="python"
fi

echo "  ✅ Python found: $PYTHON_CMD"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "  ❌ app.py not found in current directory"
    echo "     Please run this script from the service directory"
    exit 1
fi

echo "  ✅ Application files found"

# Check if port 5003 is available
echo "  Checking port 5003..."
if ! check_port 5003; then
    echo "  ⚠️  Port 5003 is already in use"
    echo "     Attempting to stop existing processes..."
    ./stop.sh
    sleep 3

    if ! check_port 5003; then
        echo "  ❌ Port 5003 is still in use after cleanup"
        echo "     Please manually stop the process using port 5003"
        exit 1
    fi
fi

echo "  ✅ Port 5003 is available"

# Create necessary directories
echo "📁 Setting up directories..."

if [ ! -d "output" ]; then
    mkdir -p output
    echo "  ✅ Created output directory"
else
    echo "  ✅ Output directory exists"
fi

if [ ! -d "input" ]; then
    mkdir -p input
    echo "  ✅ Created input directory"
else
    echo "  ✅ Input directory exists"
fi

# Check Python dependencies
echo "🔍 Checking Python dependencies..."

# Check if Flask is available
if ! $PYTHON_CMD -c "import flask" 2>/dev/null; then
    echo "  ⚠️  Flask not found, attempting to install..."
    $PYTHON_CMD -m pip install flask flask-cors
    if [ $? -ne 0 ]; then
        echo "  ❌ Failed to install Flask"
        echo "     Please install Flask manually: pip install flask flask-cors"
        exit 1
    fi
fi

echo "  ✅ Python dependencies ready"

# Start the application
echo "🎬 Starting Flask application..."

# Check if we should run in background or foreground
if [ "$1" = "--background" ] || [ "$1" = "-b" ]; then
    echo "  Starting in background mode..."
    nohup $PYTHON_CMD app.py > app.log 2>&1 &
    APP_PID=$!
    echo "  Application started with PID: $APP_PID"
    echo "  Logs are being written to: app.log"

    # Wait for service to be ready
    wait_for_service "http://localhost:5003"

    echo ""
    echo "🎯 Start Summary:"
    echo "  - Application PID: $APP_PID"
    echo "  - URL: http://localhost:5003"
    echo "  - Log file: app.log"
    echo "  - Stop with: ./stop.sh"
    echo ""
    echo "✅ Code Conversion Studio started successfully in background!"
    echo "   Open http://localhost:5003 in your browser"
else
    echo "  Starting in foreground mode..."
    echo "  Press Ctrl+C to stop the application"
    echo ""
    echo "🎯 Start Summary:"
    echo "  - URL: http://localhost:5003"
    echo "  - Mode: Foreground (interactive)"
    echo "  - Stop with: Ctrl+C or ./stop.sh"
    echo ""
    echo "✅ Starting Code Conversion Studio..."
    echo "   Open http://localhost:5003 in your browser"
    echo ""

    # Start in foreground
    exec $PYTHON_CMD app.py
fi