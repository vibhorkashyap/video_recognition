#!/usr/bin/env python3
"""
ollama_frame_capture_service.py
Background service to capture frames from HLS streams for Ollama summarization
"""

import os
import cv2
import threading
import time
from datetime import datetime
import json


class OllamaFrameCaptureService:
    """Continuously captures frames from HLS streams for Ollama analysis"""
    
    def __init__(self, hls_dir: str, ollama_summarizer, capture_interval: int = 15):
        """
        Initialize Ollama frame capture service
        
        Args:
            hls_dir: Directory containing HLS streams
            ollama_summarizer: OllamaSummarizer instance
            capture_interval: Seconds between frame captures (default: 15 seconds)
        """
        self.hls_dir = hls_dir
        self.summarizer = ollama_summarizer
        self.capture_interval = capture_interval
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the frame capture service"""
        if self.running:
            print("Ollama frame capture service already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        print(f"✓ Ollama frame capture service started (interval: {self.capture_interval}s)")
    
    def stop(self):
        """Stop the frame capture service"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("Ollama frame capture service stopped")
    
    def _get_latest_segment(self, camera_id: int):
        """Get the most recent .ts file from a camera's stream"""
        try:
            stream_dir = os.path.join(self.hls_dir, f'stream_{camera_id}')
            if not os.path.exists(stream_dir):
                return None
            
            ts_files = [f for f in os.listdir(stream_dir) if f.endswith('.ts')]
            if not ts_files:
                return None
            
            # Get the most recently modified file
            latest = max(
                (os.path.join(stream_dir, f) for f in ts_files),
                key=os.path.getmtime,
                default=None
            )
            return latest
        except Exception as e:
            print(f"Error getting latest segment for camera {camera_id}: {e}")
            return None
    
    def _capture_frame_from_segment(self, segment_path: str):
        """Extract a frame from an HLS segment"""
        try:
            if not os.path.exists(segment_path):
                return None
            
            cap = cv2.VideoCapture(segment_path)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Resize for faster processing
                return cv2.resize(frame, (640, 360))
            return None
        except Exception as e:
            print(f"Error capturing frame from {segment_path}: {e}")
            return None
    
    def _capture_loop(self):
        """Main capture loop - runs continuously in background"""
        print("Ollama frame capture loop started")
        
        while self.running:
            try:
                # Get list of cameras from cameras.json
                cameras_file = '/Users/vibhorkashyap/Documents/code/cameras.json'
                cameras = []
                
                if os.path.exists(cameras_file):
                    with open(cameras_file, 'r') as f:
                        cameras = json.load(f)
                
                # Capture frame from each camera
                for idx, camera in enumerate(cameras):
                    camera_id = camera.get('id', idx)
                    
                    # Get latest segment
                    segment_path = self._get_latest_segment(camera_id)
                    if not segment_path:
                        continue
                    
                    # Capture frame
                    frame = self._capture_frame_from_segment(segment_path)
                    if frame is not None:
                        # Add to Ollama summarizer
                        self.summarizer.add_frame(camera_id, frame, datetime.now())
                        
                        # Try to generate summaries if intervals are met
                        for interval in self.summarizer.INTERVALS.keys():
                            summary = self.summarizer.generate_summary(
                                camera_id, 
                                interval,
                                camera.get('name', f'Camera {camera_id}')
                            )
                            if summary:
                                print(f"  ✓ Generated {interval} summary for {camera.get('name', f'Camera {camera_id}')} (Gemma 3:4b)")
                
                # Wait before next capture
                time.sleep(self.capture_interval)
            
            except Exception as e:
                print(f"Error in Ollama capture loop: {e}")
                time.sleep(5)  # Wait before retrying
        
        print("Ollama frame capture loop stopped")
