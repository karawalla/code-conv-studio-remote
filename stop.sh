#!/bin/bash

# Code Conversion Studio - Stop Script
# Stops the service and all related processes

set -e

echo "🛑 Stopping Code Conversion Studio..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Do not run this script as root. Run as ubuntu user."
    exit 1
fi

# Function to check if service exists
service_exists() {
    systemctl list-unit-files | grep -q "^code-conv-studio.service"
}

# Function to check if service is running
service_running() {
    systemctl is-active --quiet code-conv-studio 2>/dev/null
}

# Stop the systemd service if it exists and is running
if service_exists; then
    if service_running; then
        echo "🔧 Stopping code-conv-studio service..."
        sudo systemctl stop code-conv-studio
        
        # Wait for service to stop
        echo "⏳ Waiting for service to stop..."
        sleep 3
        
        if service_running; then
            echo "⚠️  Service is taking longer to stop, waiting a bit more..."
            sleep 5
        fi
        
        if service_running; then
            echo "❌ Service failed to stop gracefully, forcing stop..."
            sudo systemctl kill code-conv-studio
            sleep 2
        fi
        
        echo "✅ Service stopped successfully"
    else
        echo "ℹ️  Service is not running"
    fi
else
    echo "ℹ️  Systemd service not found, checking for manual processes..."
fi

# Kill any remaining processes
echo "🔍 Checking for remaining processes..."

# Find Python processes running app.py
PIDS=$(pgrep -f "python.*app.py" 2>/dev/null || true)
if [ -n "$PIDS" ]; then
    echo "🔧 Stopping Python app processes..."
    for pid in $PIDS; do
        echo "   Stopping PID: $pid"
        kill -TERM "$pid" 2>/dev/null || true
    done
    
    # Wait a bit for graceful shutdown
    sleep 3
    
    # Force kill if still running
    PIDS=$(pgrep -f "python.*app.py" 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        echo "🔧 Force stopping remaining processes..."
        for pid in $PIDS; do
            echo "   Force stopping PID: $pid"
            kill -KILL "$pid" 2>/dev/null || true
        done
    fi
fi

# Kill any remaining Claude processes
CLAUDE_PIDS=$(pgrep -f "claude" 2>/dev/null || true)
if [ -n "$CLAUDE_PIDS" ]; then
    echo "🔧 Stopping Claude processes..."
    for pid in $CLAUDE_PIDS; do
        echo "   Stopping Claude PID: $pid"
        kill -TERM "$pid" 2>/dev/null || true
    done
    sleep 2
fi

# Check if port 80 is still in use
if lsof -Pi :80 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 80 is still in use by another process"
    echo "   Use 'sudo lsof -Pi :80 -sTCP:LISTEN' to identify the process"
else
    echo "✅ Port 80 is now available"
fi

# Final status check
echo "📊 Final status check..."
if service_exists && service_running; then
    echo "❌ Service is still running"
    exit 1
elif [ -n "$(pgrep -f 'python.*app.py' 2>/dev/null || true)" ]; then
    echo "❌ Some Python processes are still running"
    exit 1
else
    echo "✅ Code Conversion Studio stopped successfully"
    echo ""
    echo "📍 Status:"
    if service_exists; then
        echo "   • Service Status: $(systemctl is-active code-conv-studio 2>/dev/null || echo 'inactive')"
        echo "   • Auto-start: $(systemctl is-enabled code-conv-studio 2>/dev/null || echo 'disabled')"
    fi
    echo "   • Port 80: Available"
    echo "   • Python Processes: None"
    echo ""
    echo "🚀 To start again: ./start.sh"
fi