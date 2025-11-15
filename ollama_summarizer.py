#!/usr/bin/env python3
"""
ollama_summarizer.py
Video summarization using Ollama Gemma 3:4b model for frame analysis and caption generation
"""

import os
import cv2
import json
import base64
import threading
import time
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple
import requests


class OllamaSummarizer:
    """Handles video frame analysis and caption generation using Ollama Gemma 3:4b"""
    
    # Temporal hierarchy in seconds
    INTERVALS = {
        'minute': 60,
        '5_minutes': 300,
        '10_minutes': 600,
        '30_minutes': 1800,
        'hour': 3600
    }
    
    def __init__(self, hls_dir: str, output_dir: str = None, ollama_base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama summarizer
        
        Args:
            hls_dir: Directory containing HLS streams
            output_dir: Directory to save summaries (default: hls_dir/summaries)
            ollama_base_url: URL to Ollama API endpoint
        """
        self.hls_dir = hls_dir
        self.output_dir = output_dir or os.path.join(hls_dir, 'ollama_summaries')
        self.ollama_url = ollama_base_url
        self.model = "gemma3:4b"
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Verify Ollama is available
        self.ollama_available = self._check_ollama_health()
        
        if self.ollama_available:
            print(f"✓ Ollama available at {self.ollama_url}")
            print(f"✓ Using model: {self.model}")
        else:
            print(f"⚠️  Ollama not available at {self.ollama_url}")
        
        # Storage for frame captures
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
    
    def _check_ollama_health(self) -> bool:
        """Check if Ollama is running and healthy"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception as e:
            print(f"Ollama health check failed: {e}")
            return False
    
    def frame_to_base64(self, frame) -> str:
        """Convert OpenCV frame to base64 string"""
        _, buffer = cv2.imencode('.jpg', frame)
        return base64.b64encode(buffer).decode('utf-8')
    
    def capture_frame_from_segment(self, segment_path: str) -> Tuple[bool, any]:
        """Extract a frame from an HLS segment (.ts file)"""
        try:
            if not os.path.exists(segment_path):
                return False, None
            
            cap = cv2.VideoCapture(segment_path)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Resize for faster processing
                frame = cv2.resize(frame, (640, 360))
                return True, frame
            return False, None
        except Exception as e:
            print(f"Error capturing frame from {segment_path}: {e}")
            return False, None
    
    def generate_caption_from_image(self, frame, frame_number: int = 0) -> str:
        """
        Generate caption for a single frame using Ollama Gemma 3:4b
        
        Args:
            frame: OpenCV frame
            frame_number: Frame number for context
        
        Returns:
            Caption text
        """
        if not self.ollama_available:
            return "Ollama not available"
        
        try:
            # Encode frame to base64
            frame_b64 = self.frame_to_base64(frame)
            
            # Create prompt for frame analysis
            prompt = f"""Analyze this video frame (frame #{frame_number}) and provide a concise caption describing:
1. Main objects and people visible
2. Actions being performed
3. Any motion or activity
4. Scene context and location

Keep the caption to 1-2 sentences, factual and descriptive."""
            
            # Call Ollama API with vision capability
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "images": [frame_b64],
                    "stream": False,
                    "temperature": 0.3,
                    "top_p": 0.9,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Failed to generate caption").strip()
            else:
                return f"API Error: {response.status_code}"
        
        except Exception as e:
            return f"Caption generation error: {str(e)}"
    
    def generate_temporal_summary(self, frames: List, camera_id: int, interval: str) -> str:
        """
        Generate summary from multiple frames using Ollama
        
        Args:
            frames: List of frames to analyze
            camera_id: Camera ID
            interval: Time interval
        
        Returns:
            Summary text
        """
        if not self.ollama_available or not frames:
            return "Unable to generate summary"
        
        try:
            # Generate captions for sampled frames
            captions = []
            frame_sample_rate = max(1, len(frames) // 3)  # Sample up to 3 frames
            
            for idx, frame in enumerate(frames):
                if idx % frame_sample_rate == 0:
                    caption = self.generate_caption_from_image(frame, idx)
                    if caption:
                        captions.append(f"Frame {idx}: {caption}")
            
            # Generate overall summary from captions
            if not captions:
                return "No captions generated"
            
            captions_text = "\n".join(captions)
            
            summary_prompt = f"""Based on these video frame captions from a {interval.replace('_', ' ')} period:

{captions_text}

Generate a concise summary describing:
1. What was happening during this time period
2. Key activities or events
3. Notable observations
4. Any patterns or changes

Keep it brief (2-3 sentences) and factual."""
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": summary_prompt,
                    "stream": False,
                    "temperature": 0.3,
                    "top_p": 0.9,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Failed to generate summary").strip()
            else:
                return f"API Error: {response.status_code}"
        
        except Exception as e:
            return f"Summary generation error: {str(e)}"
    
    def add_frame(self, camera_id: int, frame, timestamp: datetime = None):
        """Add frame to buffer for analysis"""
        if timestamp is None:
            timestamp = datetime.now()
        
        with self.lock:
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
        """Generate summary for a specific camera and interval"""
        with self.lock:
            if not self.should_generate_summary(camera_id, interval):
                return None
            
            frames_data = self.frame_buffers[camera_id][interval]
            
            if not frames_data:
                return None
            
            # Extract frames
            sample_frames = []
            step = max(1, len(frames_data) // 3)
            for i in range(0, len(frames_data), step)[:3]:
                sample_frames.append(frames_data[i]['frame'])
            
            # Generate summary using Ollama
            summary_text = self.generate_temporal_summary(sample_frames, camera_id, interval)
            
            # Create summary record
            summary_record = {
                'timestamp': datetime.now().isoformat(),
                'camera_id': camera_id,
                'camera_name': camera_name or f'Camera {camera_id}',
                'interval': interval,
                'frames_analyzed': len(frames_data),
                'frames_sampled': len(sample_frames),
                'summary': summary_text,
                'start_time': frames_data[0]['timestamp'].isoformat() if frames_data else None,
                'end_time': frames_data[-1]['timestamp'].isoformat() if frames_data else None,
                'model': self.model,
                'llm_backend': 'ollama'
            }
            
            # Store summary
            self.summaries[camera_id][interval].append(summary_record)
            
            # Update last generation time
            self.last_summary_times[camera_id][interval] = time.time()
            
            # Clear frame buffer
            self.frame_buffers[camera_id][interval] = []
            
            # Save to file
            self.save_summary(camera_id, interval, summary_record)
            
            return summary_record
    
    def save_summary(self, camera_id: int, interval: str, summary: Dict):
        """Save summary to JSON file"""
        try:
            summary_dir = os.path.join(self.output_dir, f'camera_{camera_id}')
            os.makedirs(summary_dir, exist_ok=True)
            
            filename = os.path.join(
                summary_dir,
                f"{interval}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(filename, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"✓ Saved {interval} summary for camera {camera_id}")
        
        except Exception as e:
            print(f"Error saving summary: {e}")
    
    def get_all_summaries(self, camera_id: int = None) -> Dict:
        """Get all generated summaries"""
        with self.lock:
            if camera_id is not None:
                return self.summaries.get(camera_id, {})
            return dict(self.summaries)
    
    def get_latest_summary(self, camera_id: int, interval: str) -> Dict:
        """Get most recent summary for a camera and interval"""
        with self.lock:
            summaries = self.summaries[camera_id][interval]
            return summaries[-1] if summaries else None
    
    def export_summaries_report(self, camera_id: int = None) -> str:
        """Generate text report of all summaries"""
        lines = [
            "=" * 90,
            "OLLAMA VIDEO SUMMARIES REPORT (Gemma 3:4b)",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 90,
            ""
        ]
        
        with self.lock:
            summaries_data = self.summaries.get(camera_id) if camera_id else self.summaries
            
            if isinstance(summaries_data, dict) and 'minute' in summaries_data:
                # Single camera
                for interval in self.INTERVALS.keys():
                    lines.extend([
                        f"[{interval.upper()}]",
                        "─" * 90
                    ])
                    
                    interval_summaries = summaries_data[interval]
                    if interval_summaries:
                        for summary in interval_summaries[-5:]:
                            lines.extend([
                                f"Timestamp: {summary['timestamp']}",
                                f"Frames: {summary['frames_analyzed']} (sampled: {summary.get('frames_sampled', 0)})",
                                f"Model: {summary.get('model', 'N/A')} via {summary.get('llm_backend', 'N/A')}",
                                f"Summary: {summary['summary']}",
                                ""
                            ])
                    else:
                        lines.append("No summaries yet\n")
            else:
                # Multiple cameras
                for cam_id, cam_summaries in summaries_data.items():
                    lines.extend([
                        f"CAMERA {cam_id}",
                        "=" * 90
                    ])
                    
                    for interval in self.INTERVALS.keys():
                        lines.extend([
                            f"  [{interval.upper()}]",
                            "  " + "─" * 86
                        ])
                        
                        interval_summaries = cam_summaries[interval]
                        if interval_summaries:
                            for summary in interval_summaries[-3:]:
                                lines.extend([
                                    f"  Timestamp: {summary['timestamp']}",
                                    f"  Frames: {summary['frames_analyzed']} (sampled: {summary.get('frames_sampled', 0)})",
                                    f"  Summary: {summary['summary']}",
                                    ""
                                ])
                        else:
                            lines.append("  No summaries yet")
                    lines.append("")
        
        return "\n".join(lines)
