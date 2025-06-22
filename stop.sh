#!/bin/bash

# stop.sh - Stop all Code Conversion Studio processes
# This script safely terminates all running processes related to the application

echo "🛑 Stopping Code Conversion Studio..."

# Function to kill processes by pattern
kill_processes() {
    local pattern="$1"
    local description="$2"
    
    echo "  Checking for $description processes..."
    
    # Find processes matching the pattern
    pids=$(pgrep -f "$pattern" 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo "  Found $description processes: $pids"
        echo "  Terminating $description processes..."
        
        # Try graceful termination first
        pkill -TERM -f "$pattern" 2>/dev/null
        sleep 2
        
        # Check if processes are still running
        remaining_pids=$(pgrep -f "$pattern" 2>/dev/null)
        if [ -n "$remaining_pids" ]; then
            echo "  Force killing remaining $description processes..."
            pkill -KILL -f "$pattern" 2>/dev/null
            sleep 1
        fi
        
        # Verify termination
        final_pids=$(pgrep -f "$pattern" 2>/dev/null)
        if [ -z "$final_pids" ]; then
            echo "  ✅ $description processes stopped successfully"
        else
            echo "  ⚠️  Some $description processes may still be running: $final_pids"
        fi
    else
        echo "  ✅ No $description processes found"
    fi
}

# Stop Flask application
kill_processes "app\.py" "Flask application"

# Stop Claude processes
kill_processes "claude" "Claude"

# Stop any conversion processes
kill_processes "process.*convert" "conversion"

# Stop any Python processes in the service directory
echo "  Checking for Python processes in service directory..."
service_python_pids=$(ps aux | grep python | grep "$(pwd)" | grep -v grep | awk '{print $2}' 2>/dev/null)
if [ -n "$service_python_pids" ]; then
    echo "  Found service Python processes: $service_python_pids"
    echo "  Terminating service Python processes..."
    echo "$service_python_pids" | xargs kill -TERM 2>/dev/null
    sleep 2
    
    # Force kill if still running
    remaining_service_pids=$(ps aux | grep python | grep "$(pwd)" | grep -v grep | awk '{print $2}' 2>/dev/null)
    if [ -n "$remaining_service_pids" ]; then
        echo "  Force killing remaining service Python processes..."
        echo "$remaining_service_pids" | xargs kill -KILL 2>/dev/null
    fi
    echo "  ✅ Service Python processes stopped"
else
    echo "  ✅ No service Python processes found"
fi

# Check for any remaining processes on port 5003
echo "  Checking for processes on port 5003..."
port_pids=$(lsof -ti:5003 2>/dev/null)
if [ -n "$port_pids" ]; then
    echo "  Found processes on port 5003: $port_pids"
    echo "  Terminating processes on port 5003..."
    echo "$port_pids" | xargs kill -TERM 2>/dev/null
    sleep 2
    
    # Force kill if still running
    remaining_port_pids=$(lsof -ti:5003 2>/dev/null)
    if [ -n "$remaining_port_pids" ]; then
        echo "  Force killing remaining processes on port 5003..."
        echo "$remaining_port_pids" | xargs kill -KILL 2>/dev/null
    fi
    echo "  ✅ Port 5003 processes stopped"
else
    echo "  ✅ No processes found on port 5003"
fi

echo ""
echo "🎯 Stop Summary:"
echo "  - Flask application processes: stopped"
echo "  - Claude processes: stopped"
echo "  - Conversion processes: stopped"
echo "  - Port 5003: cleared"
echo ""
echo "✅ Code Conversion Studio stopped successfully!"
echo "   You can now start fresh with ./start.sh"
