#!/bin/bash
# Quick setup script for Camera Events AI System

echo "🚀 Camera Events AI System - Setup"
echo "===================================="
echo ""

# Check Python
echo "✓ Checking Python version..."
python --version

# Check if OpenCV is installed
echo ""
echo "📦 Checking dependencies..."
python -c "import cv2" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  OpenCV not installed. Installing..."
    pip install opencv-python
else
    echo "✓ OpenCV installed"
fi

# Check if numpy is installed
python -c "import numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  NumPy not installed. Installing..."
    pip install numpy
else
    echo "✓ NumPy installed"
fi

# Check OpenAI API key
echo ""
echo "🔑 Checking API keys..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set"
    echo "   To enable LLM analysis, set:"
    echo "   export OPENAI_API_KEY='your-key-here'"
else
    echo "✓ OPENAI_API_KEY configured"
fi

# Create clips directory
echo ""
echo "📁 Creating directories..."
mkdir -p /Users/vibhorkashyap/Documents/code/clips
for i in {0..3}; do
    mkdir -p /Users/vibhorkashyap/Documents/code/clips/camera_$i
done
echo "✓ Directories created"

# Check FFmpeg
echo ""
echo "📹 Checking FFmpeg..."
ffmpeg -version | head -1

# Ready message
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Set OpenAI API key (if using LLM):"
echo "   export OPENAI_API_KEY='sk-...'"
echo ""
echo "2. Restart the server:"
echo "   cd /Users/vibhorkashyap/Documents/code"
echo "   . .venv/bin/activate"
echo "   python camera_server.py"
echo ""
echo "3. Open the chat interface:"
echo "   http://localhost:8080/chat"
echo ""
echo "4. Enable motion detection by uncommenting in camera_server.py:"
echo "   # MOTION_MANAGER.start_all()"
echo ""
