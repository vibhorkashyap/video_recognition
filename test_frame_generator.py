#!/usr/bin/env python3
"""
Generate test summaries with frame snapshots for testing
This creates realistic test data with actual frame images
"""

import os
import json
import cv2
import numpy as np
from datetime import datetime, timedelta
import random

# Configuration
OLLAMA_SUMMARIES_DIR = '/Users/vibhorkashyap/Documents/code/ollama_video_summaries'
CLIPS_DIR = '/Users/vibhorkashyap/Documents/code/clips'

# Test data
TEST_SUMMARIES = [
    {
        "camera_id": 0,
        "interval": "5_minutes",
        "summary": "During this 5-minute period, a man in a blue shirt and dark pants walked across the street from left to right. He carried a black backpack and moved at a steady pace. The scene shows a residential area with parked cars and green vegetation in the background. No other significant activity observed.",
        "frames_analyzed": 45,
        "frames_sampled": 8,
    },
    {
        "camera_id": 0,
        "interval": "5_minutes",
        "summary": "A delivery truck (white color, license plate visible) pulled up to the curb and parked for approximately 2 minutes. A delivery person in a brown uniform exited the vehicle and entered a building. The person wore a cap and carried a package. Traffic was minimal during this period.",
        "frames_analyzed": 52,
        "frames_sampled": 9,
    },
    {
        "camera_id": 0,
        "interval": "5_minutes",
        "summary": "Two cyclists (one on a red bike, one on a black mountain bike) rode past the camera position heading northbound. Both riders wore helmets. The first cyclist wore a yellow jacket, the second wore black athletic gear. They maintained a distance of about 10 feet apart and moved at moderate speed.",
        "frames_analyzed": 58,
        "frames_sampled": 10,
    },
    {
        "camera_id": 1,
        "interval": "5_minutes",
        "summary": "A family group (two adults, one child) walked along the sidewalk. The child wore a red backpack and walked between the two adults. The adults wore casual clothing (gray hoodie and blue jeans). They stopped briefly to look at a street sign, then continued walking eastward.",
        "frames_analyzed": 48,
        "frames_sampled": 8,
    },
]

def create_test_frame(frame_number, total_frames):
    """Create a test frame with various content"""
    # Create a frame with different content based on frame number
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add gradient background
    for i in range(480):
        frame[i, :] = [30 + i//10, 30 + i//15, 50 + i//20]
    
    # Add some random rectangles to simulate scene content
    colors = [
        (100, 150, 200),  # Light blue
        (200, 150, 100),  # Brown/tan
        (100, 200, 100),  # Green
        (200, 100, 150),  # Pink
        (150, 200, 200),  # Cyan
    ]
    
    # Draw rectangles simulating objects
    num_objects = 3 + (frame_number % 3)
    for i in range(num_objects):
        x = (50 * frame_number + i * 100) % 550
        y = (30 * frame_number + i * 80) % 400
        cv2.rectangle(frame, (x, y), (x + 80, y + 60), colors[i % len(colors)], -1)
    
    # Add frame number text
    cv2.putText(frame, f'Frame {frame_number}', (20, 450), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Add timestamp text
    cv2.putText(frame, f'Test Data', (450, 450), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 200, 100), 1)
    
    return frame

def generate_test_summaries():
    """Generate test summaries with frame snapshots"""
    
    print("🔄 Generating test summaries with frame snapshots...")
    
    for summary_data in TEST_SUMMARIES:
        camera_id = summary_data["camera_id"]
        interval = summary_data["interval"]
        frames_analyzed = summary_data["frames_analyzed"]
        frames_sampled = summary_data["frames_sampled"]
        
        # Create directories
        camera_dir = os.path.join(OLLAMA_SUMMARIES_DIR, f'camera_{camera_id}')
        frames_dir = os.path.join(camera_dir, 'frames')
        os.makedirs(frames_dir, exist_ok=True)
        
        # Generate frame snapshots
        frame_snapshots = []
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create sampled frames (evenly distributed from total)
        frame_indices = []
        if frames_sampled <= frames_analyzed:
            step = max(1, frames_analyzed // frames_sampled)
            for i in range(0, frames_analyzed, step)[:frames_sampled]:
                frame_indices.append(i)
        
        print(f"  📹 Camera {camera_id} - {interval}")
        print(f"     Total frames: {frames_analyzed}, Sampled: {frames_sampled}")
        
        for idx, frame_num in enumerate(frame_indices):
            # Create test frame
            test_frame = create_test_frame(frame_num, frames_analyzed)
            
            # Save frame
            frame_filename = f"{interval}_{timestamp_str}_frame_{idx}_{frame_num}.jpg"
            frame_path = os.path.join(frames_dir, frame_filename)
            cv2.imwrite(frame_path, test_frame)
            
            # Add to frame snapshots list
            frame_snapshots.append({
                "filename": frame_filename,
                "path": f"/api/frame/{camera_id}/{interval}/{timestamp_str}/frame_{idx}_{frame_num}.jpg",
                "frame_number": frame_num,
                "index": idx
            })
            print(f"     ✓ Saved frame {idx} (original frame #{frame_num})")
        
        # Create summary record
        now = datetime.now()
        summary_record = {
            "timestamp": now.isoformat(),
            "camera_id": camera_id,
            "camera_name": f"Camera {camera_id}",
            "interval": interval,
            "frames_analyzed": frames_analyzed,
            "frames_sampled": frames_sampled,
            "frame_snapshots": frame_snapshots,
            "summary": summary_data["summary"],
            "start_time": (now - timedelta(minutes=5)).isoformat(),
            "end_time": now.isoformat(),
            "model": "gemma3:4b",
            "llm_backend": "ollama"
        }
        
        # Save summary JSON
        summary_filename = os.path.join(
            camera_dir,
            f"{interval}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(summary_filename, 'w') as f:
            json.dump(summary_record, f, indent=2)
        
        print(f"  ✓ Saved summary JSON: {os.path.basename(summary_filename)}")
        print()
    
    print("✅ Test data generation complete!")
    print(f"\n📍 Location: {OLLAMA_SUMMARIES_DIR}")
    print("\nYou can now:")
    print("1. Open the app at http://localhost:3000")
    print("2. Click 'Search' button to load test summaries")
    print("3. Click on any result to see:")
    print("   - Frame snapshots (with actual images)")
    print("   - Detailed frame count (e.g., 45 analyzed, 8 sampled)")
    print("   - Frame grid in both modal and chat bubbles")

if __name__ == "__main__":
    generate_test_summaries()
