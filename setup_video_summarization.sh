#!/bin/bash
# setup_video_summarization.sh
# Quick setup script for video summarization system

echo "🎥 Video Summarization System Setup"
echo "===================================="
echo ""

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set!"
    echo ""
    echo "To enable LLM-based video analysis, set your API key:"
    echo ""
    echo "  export OPENAI_API_KEY='sk-your-api-key-here'"
    echo ""
    echo "Get your API key at: https://platform.openai.com/api-keys"
    echo ""
    echo "System will work without key, but summaries will show placeholder text."
    echo ""
else
    echo "✓ OpenAI API key found: ${OPENAI_API_KEY:0:20}..."
fi

echo ""
echo "📦 Checking dependencies..."
echo ""

# Check Python packages
python -c "import cv2; print('✓ OpenCV installed')" 2>/dev/null || echo "⚠️  OpenCV not found. Run: pip install opencv-python"
python -c "import openai; print('✓ OpenAI package installed')" 2>/dev/null || echo "⚠️  OpenAI not found. Run: pip install openai"
python -c "from video_summarizer import VideoSummarizer; print('✓ VideoSummarizer available')" 2>/dev/null || echo "⚠️  VideoSummarizer file issue"
python -c "from frame_capture_service import FrameCaptureService; print('✓ FrameCaptureService available')" 2>/dev/null || echo "⚠️  FrameCaptureService file issue"

echo ""
echo "✨ Setup complete!"
echo ""
echo "API Endpoints:"
echo "  GET  /api/video-summaries                    - All summaries"
echo "  GET  /api/video-summaries/0                  - Camera 0 summaries"
echo "  GET  /api/video-summaries/0/minute           - Latest 1-minute summary"
echo "  GET  /api/video-summaries/0/5_minutes        - Latest 5-minute summary"
echo "  GET  /api/video-summaries/0/10_minutes       - Latest 10-minute summary"
echo "  GET  /api/video-summaries/0/30_minutes       - Latest 30-minute summary"
echo "  GET  /api/video-summaries/0/hour             - Latest 1-hour summary"
echo "  GET  /api/video-summaries/report             - Formatted text report"
echo "  POST /api/video-summaries/capture            - Manual frame capture"
echo ""
echo "Test with:"
echo "  curl http://localhost:8080/api/video-summaries/0 | jq '.summaries'"
echo ""
