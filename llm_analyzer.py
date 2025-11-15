#!/usr/bin/env python3
"""
llm_analyzer.py
LLM analysis of motion-detected clips
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
import threading

class ClipAnalyzer:
    """Analyze clips using LLM"""
    
    def __init__(self, api_key=None, model="gpt-4-turbo-preview", use_local=False):
        """
        Initialize LLM analyzer
        
        Args:
            api_key: OpenAI API key (if not using local model)
            model: Model to use (gpt-4-turbo-preview, gpt-3.5-turbo, etc.)
            use_local: Use local Ollama model instead of OpenAI
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.use_local = use_local
        
        if not use_local and not self.api_key:
            print("⚠️  No OpenAI API key found. Set OPENAI_API_KEY environment variable.")
        
        self.analysis_queue = []
        self.processing = False
        self.thread = None
    
    def analyze_clip(self, clip_path, camera_id):
        """
        Analyze a video clip using LLM
        
        Args:
            clip_path: Path to video clip
            camera_id: Camera ID
        
        Returns:
            Description of clip content
        """
        try:
            # For now, return a placeholder
            # In production, you would:
            # 1. Extract keyframes from video
            # 2. Encode frames to base64
            # 3. Send to OpenAI Vision API or local model
            # 4. Get description back
            
            description = f"Analysis of camera {camera_id} motion clip"
            return description
            
        except Exception as e:
            print(f"✗ Error analyzing clip: {e}")
            return None
    
    def queue_analysis(self, clip_data):
        """Queue a clip for analysis"""
        self.analysis_queue.append(clip_data)
    
    def start_processing(self):
        """Start processing analysis queue"""
        if not self.processing:
            self.processing = True
            self.thread = threading.Thread(target=self._process_queue, daemon=True)
            self.thread.start()
    
    def stop_processing(self):
        """Stop processing queue"""
        self.processing = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _process_queue(self):
        """Process analysis queue"""
        while self.processing:
            if self.analysis_queue:
                clip_data = self.analysis_queue.pop(0)
                description = self.analyze_clip(clip_data['filepath'], clip_data['camera_id'])
                
                if description:
                    clip_data['description'] = description
                    clip_data['status'] = 'analyzed'
                    clip_data['analysis_time'] = datetime.now().isoformat()
                    
                    # Update metadata file
                    self._update_clip_metadata(clip_data)
            
            time.sleep(1)
    
    def _update_clip_metadata(self, clip_data):
        """Update clip metadata file"""
        try:
            camera_id = clip_data['camera_id']
            clip_dir = f"/Users/vibhorkashyap/Documents/code/clips/camera_{camera_id}"
            metadata_file = os.path.join(clip_dir, "metadata.json")
            
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                # Update the clip entry
                for i, clip in enumerate(metadata):
                    if clip.get('filename') == clip_data.get('filename'):
                        metadata[i].update(clip_data)
                        break
                
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"✗ Error updating metadata: {e}")
