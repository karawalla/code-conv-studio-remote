#!/bin/bash

# Code Conversion Studio - Start Script
# Starts the service and runs it in the background

set -e

echo "🚀 Starting Code Conversion Studio..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Do not run this script as root. Run as ubuntu user."
    exit 1
fi

# Check if service file exists
if [ ! -f "/etc/systemd/system/code-conv-studio.service" ]; then
    echo "❌ Service file not found. Please ensure the service is properly installed."
    exit 1
fi

# Start the service
echo "🔧 Starting code-conv-studio service..."
sudo systemctl start code-conv-studio

# Enable auto-start on boot
echo "🔧 Enabling auto-start on boot..."
sudo systemctl enable code-conv-studio

# Wait a moment for service to start
sleep 3

# Check service status
echo "📊 Checking service status..."
if systemctl is-active --quiet code-conv-studio; then
    echo "✅ Code Conversion Studio is running!"
    echo ""
    echo "📍 Service Details:"
    echo "   • Status: $(systemctl is-active code-conv-studio)"
    echo "   • Auto-start: $(systemctl is-enabled code-conv-studio)"
    echo "   • Main PID: $(systemctl show code-conv-studio --property=MainPID --value)"
    echo ""
    echo "🌐 Application URL: http://localhost"
    echo "📊 Service Status: sudo systemctl status code-conv-studio"
    echo "📋 View Logs: sudo journalctl -u code-conv-studio -f"
    echo ""
    echo "🛑 To stop: ./stop.sh"
else
    echo "❌ Failed to start Code Conversion Studio"
    echo "📋 Check logs: sudo journalctl -u code-conv-studio -n 20"
    exit 1
fi