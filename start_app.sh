#!/bin/bash

# ============================================================================
# 🚀 COMPLETE APP STARTUP SCRIPT
# Start Backend (Flask) + Frontend (React) + Generate Test Data
# ============================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8080
FRONTEND_PORT=3000
OLLAMA_PORT=11434
BASE_DIR="/Users/vibhorkashyap/Documents/code"
VENV_PATH="$BASE_DIR/.venv"
FRONTEND_DIR="$BASE_DIR/frontend"

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}         🎬 CAMERA ANALYSIS CHAT APP - STARTUP SCRIPT${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================================================
# 1. CHECK DEPENDENCIES
# ============================================================================
echo -e "${YELLOW}[1/6] Checking dependencies...${NC}"

# Check if Ollama is running
if ! curl -s http://localhost:$OLLAMA_PORT/api/tags > /dev/null 2>&1; then
    echo -e "${RED}❌ Ollama is not running on port $OLLAMA_PORT${NC}"
    echo -e "${YELLOW}   Please start Ollama:${NC} ollama serve"
    exit 1
fi
echo -e "${GREEN}✓ Ollama running (port $OLLAMA_PORT)${NC}"

# Check if venv exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found at $VENV_PATH${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python venv found${NC}"

# Check if Node modules exist
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Node modules not found, installing...${NC}"
    cd "$FRONTEND_DIR"
    npm install > /dev/null 2>&1
    cd "$BASE_DIR"
    echo -e "${GREEN}✓ Node modules installed${NC}"
else
    echo -e "${GREEN}✓ Node modules found${NC}"
fi

echo ""

# ============================================================================
# 2. KILL EXISTING PROCESSES
# ============================================================================
echo -e "${YELLOW}[2/6] Cleaning up existing processes...${NC}"

# Kill any existing Flask/camera_server processes
pkill -f "camera_server.py" 2>/dev/null || true
echo -e "${GREEN}✓ Stopped old backend${NC}"

# Kill any existing npm/React processes
pkill -f "npm start" 2>/dev/null || true
pkill -f "node" 2>/dev/null || true
echo -e "${GREEN}✓ Stopped old frontend${NC}"

sleep 1

echo ""

# ============================================================================
# 3. START BACKEND (FLASK)
# ============================================================================
echo -e "${YELLOW}[3/6] Starting Flask Backend (port $BACKEND_PORT)...${NC}"

cd "$BASE_DIR"
source "$VENV_PATH/bin/activate"

# Start backend in background
nohup python camera_server.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo -e "${YELLOW}   Waiting for backend to initialize...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/api/cameras > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend failed to start${NC}"
        echo -e "${YELLOW}   Check logs: tail -f /tmp/backend.log${NC}"
        exit 1
    fi
    echo -n "."
    sleep 1
done

echo ""

# ============================================================================
# 4. GENERATE TEST DATA
# ============================================================================
echo -e "${YELLOW}[4/6] Generating test summaries with frame snapshots...${NC}"

python << 'PYTHON_SCRIPT'
import json
import os
import cv2
import numpy as np
from datetime import datetime, timedelta

# Create test data directory
OLLAMA_SUMMARIES_DIR = "/Users/vibhorkashyap/Documents/code/ollama_video_summaries"

for camera_id in range(1):  # Camera 0
    camera_dir = os.path.join(OLLAMA_SUMMARIES_DIR, f'camera_{camera_id}')
    frames_dir = os.path.join(camera_dir, 'frames')
    os.makedirs(frames_dir, exist_ok=True)
    
    # Create 3 test summaries
    for summary_idx in range(3):
        # Generate test frame snapshots
        frame_snapshots = []
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for frame_num in range(8):  # 8 sampled frames
            # Create a random test image (simulating actual frame)
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            # Add some variation so frames are different
            cv2.putText(frame, f'Frame {frame_num}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f'Camera {camera_id}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            
            interval = "5_minutes"
            frame_filename = f"{interval}_{timestamp_str}_frame_{frame_num}_{frame_num}.jpg"
            frame_path = os.path.join(frames_dir, frame_filename)
            
            cv2.imwrite(frame_path, frame)
            
            frame_snapshots.append({
                "filename": frame_filename,
                "path": f"/api/frame/{camera_id}/{interval}/{timestamp_str}/frame_{frame_num}_{frame_num}.jpg",
                "frame_number": frame_num,
                "index": frame_num
            })
        
        # Create test summary
        summary = {
            "timestamp": (datetime.now() - timedelta(minutes=summary_idx*10)).isoformat(),
            "camera_id": camera_id,
            "camera_name": f"Camera {camera_id}",
            "interval": "5_minutes",
            "frames_analyzed": 45 + (summary_idx * 10),  # Different frame counts
            "frames_sampled": 8,
            "frame_snapshots": frame_snapshots,
            "summary": f"Sample summary {summary_idx + 1}: This is a test summary showing {'a person walking across the street' if summary_idx == 0 else 'a car parked on the side' if summary_idx == 1 else 'multiple people in the scene'}. The activity level is moderate with clear visibility.",
            "start_time": (datetime.now() - timedelta(minutes=5)).isoformat(),
            "end_time": datetime.now().isoformat(),
            "model": "gemma3:4b",
            "llm_backend": "ollama"
        }
        
        # Save summary JSON
        summary_filename = f"5_minutes_{timestamp_str}_{summary_idx}.json"
        summary_path = os.path.join(camera_dir, summary_filename)
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✓ Created test summary {summary_idx + 1}: {summary_filename}")
        print(f"  - Frames analyzed: {summary['frames_analyzed']}, Sampled: {summary['frames_sampled']}")
        print(f"  - Frame snapshots: {len(frame_snapshots)} images saved")

print("\n✓ Test data generated successfully!")
PYTHON_SCRIPT

echo -e "${GREEN}✓ Test data created${NC}"
echo ""

# ============================================================================
# 5. START FRONTEND (REACT)
# ============================================================================
echo -e "${YELLOW}[5/6] Starting React Frontend (port $FRONTEND_PORT)...${NC}"

cd "$FRONTEND_DIR"

# Start frontend in background
nohup npm start > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait for frontend to be ready
echo -e "${YELLOW}   Waiting for frontend to compile...${NC}"
for i in {1..60}; do
    if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is ready${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${YELLOW}⚠️  Frontend still compiling (this is normal)${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

echo ""

# ============================================================================
# 6. DISPLAY STARTUP SUMMARY
# ============================================================================
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}                    ✓ APP STARTED SUCCESSFULLY!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📍 Access the app:${NC}"
echo -e "${GREEN}   🌐 http://localhost:$FRONTEND_PORT${NC}"
echo ""
echo -e "${YELLOW}📊 Services:${NC}"
echo -e "${GREEN}   Backend:  http://localhost:$BACKEND_PORT${NC}"
echo -e "${GREEN}   Ollama:   http://localhost:$OLLAMA_PORT${NC}"
echo ""
echo -e "${YELLOW}📝 Test Data:${NC}"
echo -e "${GREEN}   ✓ 3 Sample summaries created${NC}"
echo -e "${GREEN}   ✓ 45+ frames analyzed per summary${NC}"
echo -e "${GREEN}   ✓ 8 frame snapshots per summary${NC}"
echo ""
echo -e "${YELLOW}🧪 What to test:${NC}"
echo -e "   1. Open http://localhost:$FRONTEND_PORT${NC}"
echo -e "   2. Click 'Search' in sidebar (uses default 1-hour time filter)${NC}"
echo -e "   3. You should see 3 summaries with:${NC}"
echo -e "      • 📌 Frames analyzed: 45-65 (not 1!)${NC}"
echo -e "      • Sampled: 8${NC}"
echo -e "      • 🖼️ Frame snapshots grid${NC}"
echo -e "      • Summary text${NC}"
echo -e "   4. Click on any summary to see modal with all details${NC}"
echo ""
echo -e "${YELLOW}📋 Logs:${NC}"
echo -e "${GREEN}   Backend:  tail -f /tmp/backend.log${NC}"
echo -e "${GREEN}   Frontend: tail -f /tmp/frontend.log${NC}"
echo ""
echo -e "${YELLOW}🛑 To stop the app:${NC}"
echo -e "${GREEN}   pkill -f 'camera_server.py'${NC}"
echo -e "${GREEN}   pkill -f 'npm start'${NC}"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Keep script running to show PIDs
echo -e "${YELLOW}Backend PID: $BACKEND_PID${NC}"
echo -e "${YELLOW}Frontend PID: $FRONTEND_PID${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Wait indefinitely
wait
