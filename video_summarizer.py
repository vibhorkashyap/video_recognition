#!/usr/bin/env python3
"""
video_summarizer.py
Temporal video summarization system with LLM-based frame analysis
Generates summaries at: 1min, 5min, 10min, 30min, 1hr intervals
"""

import os
import cv2
import json
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import base64
from io import BytesIO
import requests

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not installed. Install with: pip install openai")


class VideoSummarizer:
    """Handles temporal video summarization with LLM analysis"""
    
    # Temporal hierarchy in seconds
    INTERVALS = {
        'minute': 60,
        '5_minutes': 300,
        '10_minutes': 600,
        '30_minutes': 1800,
        'hour': 3600
    }
    
    def __init__(self, hls_dir: str, output_dir: str = None):
        """
        Initialize video summarizer
        
        Args:
            hls_dir: Directory containing HLS streams
            output_dir: Directory to save summaries (default: hls_dir/summaries)
        """
        self.hls_dir = hls_dir
        self.output_dir = output_dir or os.path.join(hls_dir, 'summaries')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup OpenAI client if available
        self.client = None
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        
        # Storage for frame captures at each interval
        self.frame_buffers: Dict[int, Dict[str, List]] = defaultdict(lambda: {
            'minute': [],
            '5_minutes': [],
            '10_minutes': [],
            '30_minutes': [],
            'hour': []
        })
        
        # Storage for generated summaries
        self.summaries: Dict[int, Dict[str, List]] = defaultdict(lambda: {
            'minute': [],
            '5_minutes': [],
            '10_minutes': [],
            '30_minutes': [],
            'hour': []
        })
        
        # Last summary generation times
        self.last_summary_times: Dict[int, Dict[str, float]] = defaultdict(lambda: {
            'minute': 0,
            '5_minutes': 0,
            '10_minutes': 0,
            '30_minutes': 0,
            'hour': 0
        })
        
        self.lock = threading.Lock()
    
    def frame_to_base64(self, frame) -> str:
        """Convert OpenCV frame to base64 string for API submission"""
        _, buffer = cv2.imencode('.jpg', frame)
        return base64.b64encode(buffer).decode('utf-8')
    
    def capture_frame_from_segment(self, segment_path: str) -> Tuple[bool, any]:
        """
        Extract a frame from an HLS segment (.ts file)
        Returns (success, frame)
        """
        try:
            cap = cv2.VideoCapture(segment_path)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Resize for faster processing and API limits
                frame = cv2.resize(frame, (640, 360))
                return True, frame
            return False, None
        except Exception as e:
            print(f"Error capturing frame from {segment_path}: {e}")
            return False, None
    
    def analyze_frames_with_llm(self, frames: List, camera_id: int, interval: str) -> str:
        """
        Use LLM to analyze captured frames and generate summary
        
        Args:
            frames: List of frames to analyze
            camera_id: ID of the camera
            interval: Time interval ('minute', '5_minutes', etc)
        
        Returns:
            Summary text from LLM
        """
        if not self.client or not frames:
            return f"No LLM analysis available (missing API key or frames)"
        
        try:
            # Prepare frame descriptions for LLM
            frame_descriptions = []
            for idx, frame in enumerate(frames):
                frame_b64 = self.frame_to_base64(frame)
                frame_descriptions.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{frame_b64}"
                    }
                })
            
            # Add text prompt
            prompt = f"""Analyze these frames from camera {camera_id} captured over a {interval.replace('_', ' ')} period.
            
Provide a concise summary including:
1. Main activities/events observed
2. Number of people/objects detected
3. Motion patterns and areas of interest
4. Any anomalies or notable changes
5. Overall scene description

Keep it concise and factual."""
            
            # Call GPT-4V (gpt-4-turbo with vision)
            response = self.client.messages.create(
                model="gpt-4-turbo",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            *frame_descriptions
                        ]
                    }
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            return f"LLM Analysis Error: {str(e)}"
    
    def add_frame(self, camera_id: int, frame, timestamp: datetime = None):
        """
        Add a frame to the buffer for analysis
        
        Args:
            camera_id: ID of the camera
            frame: OpenCV frame
            timestamp: Frame timestamp (default: now)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        with self.lock:
            # Add to all interval buffers
            for interval in self.INTERVALS.keys():
                self.frame_buffers[camera_id][interval].append({
                    'frame': frame,
                    'timestamp': timestamp
                })
    
    def should_generate_summary(self, camera_id: int, interval: str) -> bool:
        """Check if it's time to generate summary for this interval"""
        current_time = time.time()
        last_time = self.last_summary_times[camera_id][interval]
        interval_seconds = self.INTERVALS[interval]
        
        return (current_time - last_time) >= interval_seconds
    
    def generate_summary(self, camera_id: int, interval: str, camera_name: str = None) -> Dict:
        """
        Generate summary for a specific camera and interval
        
        Args:
            camera_id: ID of the camera
            interval: Time interval key
            camera_name: Name of the camera
        
        Returns:
            Dictionary with summary information
        """
        with self.lock:
            if not self.should_generate_summary(camera_id, interval):
                return None
            
            # Get frames for this interval
            frames_data = self.frame_buffers[camera_id][interval]
            
            if not frames_data:
                return None
            
            # Extract just frames for LLM analysis (use up to 3 frames per interval)
            sample_frames = []
            step = max(1, len(frames_data) // 3)
            for i in range(0, len(frames_data), step)[:3]:
                sample_frames.append(frames_data[i]['frame'])
            
            # Generate LLM summary
            llm_summary = self.analyze_frames_with_llm(sample_frames, camera_id, interval)
            
            # Create summary record
            summary_record = {
                'timestamp': datetime.now().isoformat(),
                'camera_id': camera_id,
                'camera_name': camera_name or f'Camera {camera_id}',
                'interval': interval,
                'frames_analyzed': len(frames_data),
                'summary': llm_summary,
                'start_time': frames_data[0]['timestamp'].isoformat() if frames_data else None,
                'end_time': frames_data[-1]['timestamp'].isoformat() if frames_data else None,
            }
            
            # Store summary
            self.summaries[camera_id][interval].append(summary_record)
            
            # Update last generation time
            self.last_summary_times[camera_id][interval] = time.time()
            
            # Clear frame buffer for this interval
            self.frame_buffers[camera_id][interval] = []
            
            # Save to file
            self.save_summary(camera_id, interval, summary_record)
            
            return summary_record
    
    def save_summary(self, camera_id: int, interval: str, summary: Dict):
        """Save summary to file"""
        try:
            summary_dir = os.path.join(self.output_dir, f'camera_{camera_id}')
            os.makedirs(summary_dir, exist_ok=True)
            
            filename = os.path.join(
                summary_dir,
                f"{interval}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(filename, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"✓ Saved {interval} summary for camera {camera_id}: {filename}")
        
        except Exception as e:
            print(f"Error saving summary: {e}")
    
    def get_all_summaries(self, camera_id: int = None) -> Dict:
        """Get all generated summaries"""
        with self.lock:
            if camera_id is not None:
                return self.summaries.get(camera_id, {})
            return dict(self.summaries)
    
    def get_latest_summary(self, camera_id: int, interval: str) -> Dict:
        """Get the most recent summary for a camera and interval"""
        with self.lock:
            summaries = self.summaries[camera_id][interval]
            return summaries[-1] if summaries else None
    
    def export_summaries_report(self, camera_id: int = None) -> str:
        """Generate a text report of all summaries"""
        lines = [
            "=" * 80,
            "VIDEO SUMMARIES REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80,
            ""
        ]
        
        with self.lock:
            summaries_data = self.summaries.get(camera_id) if camera_id else self.summaries
            
            if isinstance(summaries_data, dict) and 'minute' in summaries_data:
                # Single camera
                for interval in self.INTERVALS.keys():
                    lines.extend([
                        f"[{interval.upper()}]",
                        "─" * 80
                    ])
                    
                    interval_summaries = summaries_data[interval]
                    if interval_summaries:
                        for summary in interval_summaries[-5:]:  # Show last 5
                            lines.extend([
                                f"Timestamp: {summary['timestamp']}",
                                f"Frames: {summary['frames_analyzed']}",
                                f"Summary: {summary['summary']}",
                                ""
                            ])
                    else:
                        lines.append("No summaries yet")
                    lines.append("")
            else:
                # Multiple cameras
                for cam_id, cam_summaries in summaries_data.items():
                    lines.extend([
                        f"CAMERA {cam_id}",
                        "=" * 80
                    ])
                    
                    for interval in self.INTERVALS.keys():
                        lines.extend([
                            f"  [{interval.upper()}]",
                            "  " + "─" * 76
                        ])
                        
                        interval_summaries = cam_summaries[interval]
                        if interval_summaries:
                            for summary in interval_summaries[-3:]:
                                lines.extend([
                                    f"  Timestamp: {summary['timestamp']}",
                                    f"  Frames: {summary['frames_analyzed']}",
                                    f"  Summary: {summary['summary']}",
                                    ""
                                ])
                        else:
                            lines.append("  No summaries yet")
                    lines.append("")
        
        return "\n".join(lines)
