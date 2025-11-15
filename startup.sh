#!/bin/bash
# startup.sh - Start the complete camera monitoring system

set -e

SCRIPT_DIR="/Users/vibhorkashyap/Documents/code"
VENV="$SCRIPT_DIR/.venv/bin/python"

echo "🎥 Camera Monitoring System Startup"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -f "$VENV" ]; then
    echo "❌ Virtual environment not found at $VENV"
    exit 1
fi

# Extract RTSP URLs
echo "📡 Extracting RTSP URLs from cameras..."
"$VENV" "$SCRIPT_DIR/extract_rtsp_urls.py"
echo ""

# Start the server
echo "🚀 Starting Flask server on http://localhost:8080"
echo "   Press Ctrl+C to stop"
echo ""
"$VENV" "$SCRIPT_DIR/camera_server.py"
