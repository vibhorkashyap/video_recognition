#!/usr/bin/env python3
"""
motion_detector.py
Motion detection and clip recording for camera feeds
"""

import cv2
import threading
import time
import os
import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import numpy as np

class MotionDetector:
    def __init__(self, camera_id, rtsp_url, clip_dir="/Users/vibhorkashyap/Documents/code/clips"):
        """
        Initialize motion detector for a camera
        
        Args:
            camera_id: Unique camera identifier (0-3)
            rtsp_url: RTSP stream URL
            clip_dir: Directory to save clips
        """
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.clip_dir = clip_dir
        self.recording = False
        self.thread = None
        
        # Motion detection parameters
        self.motion_threshold = 500  # Pixel area threshold for motion
        self.sensitivity = 0.02  # % of frame that must change to trigger motion
        self.clip_duration = 15  # seconds
        self.pre_motion_buffer = 5  # seconds of buffer before motion
        self.post_motion_buffer = 5  # seconds of buffer after motion
        
        # Frame buffer for pre-motion recording
        self.frame_buffer = []
        self.buffer_fps = 5  # Frame rate for buffering
        self.buffer_max_frames = self.pre_motion_buffer * self.buffer_fps
        
        # Create clip directory
        self.camera_clip_dir = os.path.join(clip_dir, f"camera_{camera_id}")
        os.makedirs(self.camera_clip_dir, exist_ok=True)
        
        # Metadata file
        self.metadata_file = os.path.join(self.camera_clip_dir, "metadata.json")
        self.clips_metadata = self._load_metadata()
        
        # Motion state
        self.motion_active = False
        self.motion_start_time = None
        self.last_motion_time = None
        
    def _load_metadata(self):
        """Load existing metadata"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_metadata(self):
        """Save metadata to file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.clips_metadata, f, indent=2)
    
    def detect_motion(self, frame1, frame2):
        """
        Detect motion between two frames
        Returns True if motion detected, False otherwise
        """
        try:
            # Convert to grayscale
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Calculate frame difference
            frame_diff = cv2.absdiff(gray1, gray2)
            
            # Apply threshold
            _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Calculate total area of motion
            motion_area = sum(cv2.contourArea(c) for c in contours)
            
            # Calculate sensitivity threshold
            frame_area = frame1.shape[0] * frame1.shape[1]
            sensitivity_threshold = frame_area * self.sensitivity
            
            return motion_area > sensitivity_threshold
        except Exception as e:
            print(f"Error detecting motion: {e}")
            return False
    
    def run(self):
        """Main motion detection loop"""
        cap = cv2.VideoCapture(self.rtsp_url)
        
        if not cap.isOpened():
            print(f"✗ Failed to open RTSP stream for camera {self.camera_id}")
            return
        
        print(f"✓ Started motion detection for camera {self.camera_id}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        prev_frame = None
        frame_count = 0
        buffer_frames = []
        
        while self.recording:
            ret, frame = cap.read()
            
            if not ret:
                print(f"✗ Failed to read frame from camera {self.camera_id}")
                break
            
            # Resize for faster processing
            frame_resized = cv2.resize(frame, (frame_width // 2, frame_height // 2))
            
            # Add to buffer
            if len(buffer_frames) < self.buffer_max_frames:
                buffer_frames.append(frame)
            else:
                buffer_frames.pop(0)
                buffer_frames.append(frame)
            
            # Detect motion
            if prev_frame is not None:
                motion_detected = self.detect_motion(frame_resized, cv2.resize(prev_frame, (frame_width // 2, frame_height // 2)))
                
                if motion_detected:
                    self.last_motion_time = time.time()
                    
                    if not self.motion_active:
                        self.motion_active = True
                        self.motion_start_time = self.last_motion_time
                        print(f"🔴 Motion detected on camera {self.camera_id}")
            
            prev_frame = frame.copy()
            frame_count += 1
            
            # Check if motion window has ended
            if self.motion_active and self.last_motion_time:
                if time.time() - self.last_motion_time > self.post_motion_buffer:
                    # Save clip
                    self._save_clip(buffer_frames, fps, frame_width, frame_height)
                    self.motion_active = False
                    self.motion_start_time = None
        
        cap.release()
        print(f"✓ Stopped motion detection for camera {self.camera_id}")
    
    def _save_clip(self, frames, fps, width, height):
        """Save motion-detected clip to file"""
        try:
            timestamp = datetime.now()
            clip_filename = f"motion_{timestamp.strftime('%Y%m%d_%H%M%S')}.mp4"
            clip_path = os.path.join(self.camera_clip_dir, clip_filename)
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(clip_path, fourcc, fps, (width, height))
            
            # Write frames
            for frame in frames:
                out.write(frame)
            
            out.release()
            
            # Add metadata
            clip_data = {
                "clip_id": len(self.clips_metadata),
                "camera_id": self.camera_id,
                "filename": clip_filename,
                "filepath": clip_path,
                "timestamp": timestamp.isoformat(),
                "duration": len(frames) / fps,
                "motion_start": self.motion_start_time,
                "motion_end": self.last_motion_time,
                "status": "pending_analysis"
            }
            self.clips_metadata.append(clip_data)
            self._save_metadata()
            
            print(f"✓ Saved motion clip for camera {self.camera_id}: {clip_filename}")
            
        except Exception as e:
            print(f"✗ Error saving clip: {e}")
    
    def start(self):
        """Start motion detection thread"""
        if not self.recording:
            self.recording = True
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop motion detection thread"""
        self.recording = False
        if self.thread:
            self.thread.join(timeout=5)


class MotionDetectionManager:
    """Manages motion detection for all cameras"""
    
    def __init__(self, cameras_config):
        self.detectors = {}
        self.cameras_config = cameras_config
    
    def start_all(self):
        """Start motion detection for all cameras"""
        for idx, camera in enumerate(self.cameras_config):
            detector = MotionDetector(idx, camera['rtsp_url'])
            detector.start()
            self.detectors[idx] = detector
    
    def stop_all(self):
        """Stop all motion detectors"""
        for detector in self.detectors.values():
            detector.stop()
    
    def get_clips(self, camera_id, start_time=None, end_time=None):
        """Get clips for a camera within time range"""
        if camera_id not in self.detectors:
            return []
        
        detector = self.detectors[camera_id]
        clips = detector.clips_metadata
        
        if start_time or end_time:
            filtered_clips = []
            for clip in clips:
                clip_time = datetime.fromisoformat(clip['timestamp'])
                if start_time and clip_time < start_time:
                    continue
                if end_time and clip_time > end_time:
                    continue
                filtered_clips.append(clip)
            return filtered_clips
        
        return clips
