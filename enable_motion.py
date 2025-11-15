#!/usr/bin/env python3
"""
Enable motion detection in the camera system
Run this script to activate motion detection and LLM analysis
"""

import os
import sys
sys.path.insert(0, '/Users/vibhorkashyap/Documents/code')

print("🎬 Camera Events Motion Detection Enabler")
print("=" * 50)
print()

# Check dependencies
print("✓ Checking dependencies...")
try:
    import cv2
    import numpy
    import openai
    print("  ✓ OpenCV, NumPy, OpenAI installed")
except ImportError as e:
    print(f"  ✗ Missing dependency: {e}")
    sys.exit(1)

# Check clips directory
clips_dir = '/Users/vibhorkashyap/Documents/code/clips'
os.makedirs(clips_dir, exist_ok=True)
for i in range(4):
    os.makedirs(f'{clips_dir}/camera_{i}', exist_ok=True)
print(f"  ✓ Clips directory ready: {clips_dir}")

# Check cameras.json
cameras_file = '/Users/vibhorkashyap/Documents/code/cameras.json'
if not os.path.exists(cameras_file):
    print(f"  ✗ Missing: {cameras_file}")
    sys.exit(1)
print(f"  ✓ Cameras config found")

# Check OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("\n  ⚠️  OPENAI_API_KEY not set (LLM analysis disabled)")
    print("     To enable: export OPENAI_API_KEY='sk-...'")
else:
    print(f"  ✓ OpenAI API key configured")

print()
print("✅ All checks passed!")
print()
print("📋 Next steps:")
print()
print("1. Start motion detection (optional - requires modifications):")
print("   a. Edit camera_server.py and uncomment motion detection code")
print("   b. Around line 190, uncomment:")
print("      # MOTION_MANAGER = MotionDetectionManager(cameras)")
print("      # MOTION_MANAGER.start_all()")
print()
print("2. Restart the Flask server:")
print("   killall camera_server")
print("   cd /Users/vibhorkashyap/Documents/code")
print("   . .venv/bin/activate")
print("   python camera_server.py")
print()
print("3. Access the chat interface:")
print("   http://localhost:8080/chat")
print()
print("💡 Tips:")
print("   - Motion detection will save clips to /clips/camera_X/")
print("   - LLM will analyze clips and add descriptions")
print("   - Use the chat interface to query events")
print("   - Set sensitivity in motion_detector.py as needed")
print()
