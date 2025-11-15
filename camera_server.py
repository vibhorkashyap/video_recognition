#!/usr/bin/env python3
"""
camera_server.py
Flask server with HLS streaming support for camera grid display
"""

from flask import Flask, render_template, jsonify, send_file, request
import json
import os
import subprocess
import threading
import time
from datetime import datetime
import cv2

# Import video summarizer (OpenAI)
try:
    from video_summarizer import VideoSummarizer
    SUMMARIZER_AVAILABLE = True
except ImportError:
    SUMMARIZER_AVAILABLE = False
    print("Warning: VideoSummarizer not available")

# Import Ollama summarizer (local Gemma 3:4b)
try:
    from ollama_summarizer import OllamaSummarizer
    OLLAMA_SUMMARIZER_AVAILABLE = True
except ImportError:
    OLLAMA_SUMMARIZER_AVAILABLE = False
    print("Warning: OllamaSummarizer not available")

# Import frame capture service
try:
    from frame_capture_service import FrameCaptureService
    FRAME_CAPTURE_AVAILABLE = True
except ImportError:
    FRAME_CAPTURE_AVAILABLE = False
    print("Warning: FrameCaptureService not available")

# Import Ollama frame capture service
try:
    from ollama_frame_capture_service import OllamaFrameCaptureService
    OLLAMA_FRAME_CAPTURE_AVAILABLE = True
except ImportError:
    OLLAMA_FRAME_CAPTURE_AVAILABLE = False
    print("Warning: OllamaFrameCaptureService not available")

app = Flask(__name__)

# Configuration
CAMERAS_FILE = '/Users/vibhorkashyap/Documents/code/cameras.json'
HLS_DIR = '/Users/vibhorkashyap/Documents/code/hls_streams'
CLIPS_DIR = '/Users/vibhorkashyap/Documents/code/clips'
SUMMARIES_DIR = '/Users/vibhorkashyap/Documents/code/video_summaries'
OLLAMA_SUMMARIES_DIR = '/Users/vibhorkashyap/Documents/code/ollama_video_summaries'
FFMPEG_PROCESSES = {}
VIDEO_SUMMARIZER = None  # Will be initialized on startup (OpenAI)
OLLAMA_SUMMARIZER = None  # Will be initialized on startup (Gemma 3:4b)
FRAME_CAPTURE_SERVICE = None  # Will be initialized on startup (OpenAI)
OLLAMA_FRAME_CAPTURE_SERVICE = None  # Will be initialized on startup (Ollama)
MOTION_MANAGER = None
ANALYZER = None

# Create HLS directory if it doesn't exist
os.makedirs(HLS_DIR, exist_ok=True)

def load_cameras():
    """Load camera data from JSON file"""
    if os.path.exists(CAMERAS_FILE):
        with open(CAMERAS_FILE, 'r') as f:
            return json.load(f)
    return []


def start_hls_stream(camera_id, rtsp_url):
    """Start ffmpeg process to convert RTSP to HLS"""
    stream_dir = os.path.join(HLS_DIR, f'stream_{camera_id}')
    os.makedirs(stream_dir, exist_ok=True)
    
    playlist_path = os.path.join(stream_dir, 'playlist.m3u8')
    
    # Clean up old files before starting
    for f in os.listdir(stream_dir):
        try:
            os.remove(os.path.join(stream_dir, f))
        except:
            pass
    
    # FFmpeg command to convert RTSP to HLS with optimized real-time settings
    # Increased buffer to keep more segments available, ensuring longer LIVE status
    cmd = [
        'ffmpeg',
        '-rtsp_transport', 'tcp',
        '-i', rtsp_url,
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-b:v', '1200k',
        '-maxrate', '1500k',
        '-bufsize', '2000k',
        '-g', '20',  # GOP size = 20 frames for better segment boundaries
        '-c:a', 'aac',
        '-b:a', '128k',
        '-f', 'hls',
        '-hls_time', '3',  # Increased to 3 seconds per segment (more stable)
        '-hls_list_size', '15',  # Keep 15 segments (45 seconds total buffer)
        '-hls_init_time', '3',  # Initial segment time
        '-hls_flags', 'delete_segments+append_list+program_date_time+independent_segments',
        '-hls_segment_type', 'mpegts',
        '-start_number', '0',
        playlist_path
    ]
    
    try:
        logfile = open(os.path.join(stream_dir, 'ffmpeg.log'), 'w')
        process = subprocess.Popen(
            cmd,
            stdout=logfile,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid
        )
        FFMPEG_PROCESSES[camera_id] = process
        print(f"✓ Started HLS stream for camera {camera_id}")
        return True
    except Exception as e:
        print(f"✗ Failed to start HLS stream for camera {camera_id}: {e}")
        return False


def stop_hls_stream(camera_id):
    """Stop ffmpeg process for a camera"""
    if camera_id in FFMPEG_PROCESSES:
        try:
            process = FFMPEG_PROCESSES[camera_id]
            os.killpg(os.getpgid(process.pid), 15)
            del FFMPEG_PROCESSES[camera_id]
            print(f"✓ Stopped HLS stream for camera {camera_id}")
        except Exception as e:
            print(f"✗ Failed to stop HLS stream: {e}")


def init_streams():
    """Initialize HLS streams for all cameras"""
    cameras = load_cameras()
    for idx, camera in enumerate(cameras):
        start_hls_stream(idx, camera['rtsp_url'])
        time.sleep(1)  # Small delay between starting streams


@app.route('/')
def index():
    """Serve the main camera grid page"""
    return render_template('index.html')


@app.route('/chat')
def chat_page():
    """Serve the chat interface page"""
    return render_template('chat.html')


@app.route('/api/cameras')
def get_cameras():
    """API endpoint to get all cameras with HLS stream URLs"""
    cameras = load_cameras()
    
    # Add HLS stream URLs
    for idx, camera in enumerate(cameras):
        camera['hls_url'] = f'/hls/stream_{idx}/playlist.m3u8'
    
    return jsonify(cameras)


@app.route('/api/cameras/<int:camera_id>')
def get_camera(camera_id):
    """API endpoint to get specific camera"""
    cameras = load_cameras()
    if camera_id < len(cameras):
        camera = cameras[camera_id]
        camera['hls_url'] = f'/hls/stream_{camera_id}/playlist.m3u8'
        return jsonify(camera)
    return jsonify({"error": "Camera not found"}), 404


@app.route('/hls/<path:filename>')
def serve_hls(filename):
    """Serve HLS playlist and segments with no-cache headers"""
    from flask import make_response
    
    # Extract stream ID
    parts = filename.split('/')
    if len(parts) >= 2:
        stream_id = parts[0]
        segment_file = parts[1] if len(parts) > 1 else ''
        
        stream_path = os.path.join(HLS_DIR, stream_id)
        
        if segment_file:
            file_path = os.path.join(stream_path, segment_file)
        else:
            file_path = os.path.join(stream_path, 'playlist.m3u8')
        
        if os.path.exists(file_path):
            # Set appropriate content type
            if file_path.endswith('.m3u8'):
                response = make_response(send_file(file_path, mimetype='application/vnd.apple.mpegurl'))
                # Don't cache playlists - they change frequently
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
            elif file_path.endswith('.ts'):
                response = make_response(send_file(file_path, mimetype='video/mp2t'))
                # Cache segments for short time since they don't change
                response.headers['Cache-Control'] = 'public, max-age=60'
                return response
    
    return jsonify({"error": "File not found"}), 404


@app.before_request
def startup():
    """Initialize streams on first request"""
    if not hasattr(app, 'streams_initialized'):
        app.streams_initialized = True
        threading.Thread(target=init_streams, daemon=True).start()
        
        # Initialize Ollama Summarizer (Gemma 3:4b) with frame capture
        try:
            global OLLAMA_SUMMARIZER, OLLAMA_FRAME_CAPTURE_SERVICE
            if OLLAMA_SUMMARIZER_AVAILABLE:
                OLLAMA_SUMMARIZER = OllamaSummarizer(HLS_DIR, OLLAMA_SUMMARIES_DIR)
                print("✓ Ollama Summarizer (Gemma 3:4b) initialized")
                
                # Start Ollama frame capture service for continuous analysis
                if OLLAMA_FRAME_CAPTURE_AVAILABLE:
                    OLLAMA_FRAME_CAPTURE_SERVICE = OllamaFrameCaptureService(
                        HLS_DIR, 
                        OLLAMA_SUMMARIZER, 
                        capture_interval=15  # Capture every 15 seconds
                    )
                    OLLAMA_FRAME_CAPTURE_SERVICE.start()
                    print("✓ Ollama Frame Capture Service started")
        except Exception as e:
            print(f"⚠️  Ollama Summarizer initialization failed: {e}")
        
        # Initialize video summarizer (OpenAI - optional)
        try:
            global VIDEO_SUMMARIZER, FRAME_CAPTURE_SERVICE
            if SUMMARIZER_AVAILABLE:
                VIDEO_SUMMARIZER = VideoSummarizer(HLS_DIR, SUMMARIES_DIR)
                print("✓ Video Summarizer (OpenAI) initialized")
                
                # Start frame capture service for continuous analysis
                if FRAME_CAPTURE_AVAILABLE:
                    FRAME_CAPTURE_SERVICE = FrameCaptureService(
                        HLS_DIR, 
                        VIDEO_SUMMARIZER, 
                        capture_interval=15  # Capture every 15 seconds
                    )
                    FRAME_CAPTURE_SERVICE.start()
                    print("✓ Frame Capture Service started")
        except Exception as e:
            print(f"⚠️  Video Summarizer initialization failed: {e}")
        
        # Initialize motion detection (optional - requires opencv)
        try:
            from motion_detector import MotionDetectionManager
            global MOTION_MANAGER
            cameras = load_cameras()
            MOTION_MANAGER = MotionDetectionManager(cameras)
            # Uncomment to enable motion detection:
            # MOTION_MANAGER.start_all()
        except ImportError:
            print("⚠️  OpenCV not available. Motion detection disabled.")


@app.route('/api/clips/<int:camera_id>')
def get_clips(camera_id):
    """Get motion-detected clips for a camera"""
    clip_dir = os.path.join(CLIPS_DIR, f'camera_{camera_id}')
    metadata_file = os.path.join(clip_dir, 'metadata.json')
    
    if not os.path.exists(metadata_file):
        return jsonify([])
    
    try:
        with open(metadata_file, 'r') as f:
            clips = json.load(f)
        
        # Filter by time range if provided
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        if start_time or end_time:
            filtered_clips = []
            for clip in clips:
                clip_time = datetime.fromisoformat(clip['timestamp'])
                if start_time and clip_time < datetime.fromisoformat(start_time):
                    continue
                if end_time and clip_time > datetime.fromisoformat(end_time):
                    continue
                filtered_clips.append(clip)
            return jsonify(filtered_clips)
        
        return jsonify(clips)
    except Exception as e:
        print(f"Error loading clips: {e}")
        return jsonify([])


def search_ollama_summaries(query, camera_id=None, start_time=None, end_time=None):
    """Search Ollama-generated temporal summaries"""
    relevant_summaries = []
    query_lower = query.lower()
    query_words = [w for w in query_lower.split() if len(w) > 2]  # Filter out short words
    
    # Determine which cameras to search
    cameras_to_search = [camera_id] if camera_id is not None else range(4)
    
    # Parse time filters
    start_dt = None
    end_dt = None
    if start_time:
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        except:
            pass
    if end_time:
        try:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        except:
            pass
    
    for cam_id in cameras_to_search:
        camera_dir = os.path.join(OLLAMA_SUMMARIES_DIR, f'camera_{cam_id}')
        
        if not os.path.exists(camera_dir):
            continue
        
        # Search through all summary files (minute, 5_minutes, 10_minutes, 30_minutes, hour)
        for summary_file in os.listdir(camera_dir):
            if not summary_file.endswith('.json'):
                continue
            
            try:
                file_path = os.path.join(camera_dir, summary_file)
                with open(file_path, 'r') as f:
                    summary_data = json.load(f)
                
                # Parse timestamp and interval
                try:
                    summary_timestamp = datetime.fromisoformat(summary_data.get('timestamp', ''))
                except:
                    continue
                
                interval = summary_data.get('interval', '')
                summary_text = summary_data.get('summary', '').lower()
                
                # Skip error messages (timeout errors, etc)
                if 'error' in summary_text or 'timeout' in summary_text or 'connection' in summary_text.lower():
                    continue
                
                # Filter by time range if provided
                if start_dt and summary_timestamp < start_dt:
                    continue
                
                if end_dt and summary_timestamp > end_dt:
                    continue
                
                # Perform semantic search - match query words in summary
                match_score = 0
                matched_words = []
                for word in query_words:
                    if word in summary_text:
                        match_score += 1
                        matched_words.append(word)
                
                # Include summary even if no keywords matched (for time-based searches)
                # But prioritize keyword matches
                relevant_summaries.append({
                    **summary_data,
                    "match_score": match_score,
                    "matched_words": matched_words,
                    "file_name": summary_file,
                    "relative_timestamp": summary_timestamp.isoformat()
                })
            
            except Exception as e:
                print(f"Error reading summary file {summary_file}: {e}")
                continue
    
    # Sort by match score (descending) and timestamp (newest first)
    relevant_summaries.sort(key=lambda x: (-x['match_score'], -datetime.fromisoformat(x['relative_timestamp']).timestamp()))
    
    return relevant_summaries


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat interface for querying clips and Ollama summaries"""
    data = request.json
    query = data.get('query', '')
    camera_id = data.get('camera_id', None)
    start_time = data.get('start_time', None)
    end_time = data.get('end_time', None)
    search_type = data.get('search_type', 'all')  # 'all', 'summaries', 'clips'
    
    try:
        ollama_summaries = []
        clips_results = []
        
        # Search Ollama summaries
        if search_type in ['all', 'summaries']:
            ollama_summaries = search_ollama_summaries(query, camera_id, start_time, end_time)
        
        # Search motion-detected clips
        if search_type in ['all', 'clips']:
            if camera_id is not None:
                clip_dir = os.path.join(CLIPS_DIR, f'camera_{camera_id}')
                metadata_file = os.path.join(clip_dir, 'metadata.json')
                
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r') as f:
                        clips = json.load(f)
                    
                    # Filter by time range
                    if start_time or end_time:
                        filtered_clips = []
                        for clip in clips:
                            clip_time = datetime.fromisoformat(clip['timestamp'])
                            if start_time and clip_time < datetime.fromisoformat(start_time):
                                continue
                            if end_time and clip_time > datetime.fromisoformat(end_time):
                                continue
                            filtered_clips.append(clip)
                        clips = filtered_clips
                    
                    # Simple semantic search on descriptions
                    query_lower = query.lower()
                    for clip in clips:
                        description = clip.get('description', '').lower()
                        if any(word in description for word in query_lower.split()):
                            clips_results.append(clip)
            else:
                # Search all cameras' clips
                for cam_id in range(4):
                    clip_dir = os.path.join(CLIPS_DIR, f'camera_{cam_id}')
                    metadata_file = os.path.join(clip_dir, 'metadata.json')
                    
                    if os.path.exists(metadata_file):
                        with open(metadata_file, 'r') as f:
                            clips = json.load(f)
                            for clip in clips:
                                clip['camera_id'] = cam_id
                                clips_results.append(clip)
        
        # Generate comprehensive response
        response = {
            "query": query,
            "camera_id": camera_id,
            "timestamp": datetime.now().isoformat(),
            "ollama_summaries": ollama_summaries[:10],  # Return top 10 summaries
            "ollama_summaries_count": len(ollama_summaries),
            "motion_clips": clips_results[:5],  # Return top 5 clips
            "motion_clips_count": len(clips_results),
            "summary": f"Found {len(ollama_summaries)} video summaries and {len(clips_results)} motion events matching '{query}'"
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({
            "error": str(e),
            "query": query,
            "timestamp": datetime.now().isoformat()
        }), 500


def get_stream_metadata(camera_id):
    """Extract metadata from HLS stream"""
    stream_dir = os.path.join(HLS_DIR, f'stream_{camera_id}')
    playlist_path = os.path.join(stream_dir, 'playlist.m3u8')
    
    metadata = {
        'camera_id': camera_id,
        'stream_path': stream_dir,
        'total_segments': 0,
        'total_size_mb': 0,
        'playlist_size_kb': 0,
        'segments_info': [],
        'status': 'offline'
    }
    
    try:
        # Get directory size
        total_size = 0
        segment_files = []
        
        if os.path.exists(stream_dir):
            for filename in os.listdir(stream_dir):
                filepath = os.path.join(stream_dir, filename)
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    total_size += size
                    
                    if filename.endswith('.ts'):
                        segment_files.append({
                            'name': filename,
                            'size_kb': round(size / 1024, 2),
                            'mtime': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                        })
                    elif filename == 'playlist.m3u8':
                        metadata['playlist_size_kb'] = round(size / 1024, 2)
        
        metadata['total_segments'] = len(segment_files)
        metadata['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        metadata['segments_info'] = sorted(segment_files, key=lambda x: x['name'], reverse=True)[:15]
        
        # Read playlist to extract timing info
        if os.path.exists(playlist_path):
            with open(playlist_path, 'r') as f:
                playlist_content = f.read()
                metadata['status'] = 'online'
                
                # Extract program date time
                lines = playlist_content.split('\n')
                for i, line in enumerate(lines):
                    if 'EXT-X-PROGRAM-DATE-TIME' in line:
                        time_str = line.split(':')[1]
                        metadata['last_timestamp'] = time_str
                    elif 'EXT-X-MEDIA-SEQUENCE' in line:
                        seq = line.split(':')[1]
                        metadata['media_sequence'] = int(seq)
                    elif 'EXT-X-TARGETDURATION' in line:
                        dur = line.split(':')[1]
                        metadata['target_duration'] = int(dur)
    
    except Exception as e:
        metadata['error'] = str(e)
    
    return metadata


@app.route('/api/stream-summary')
def get_stream_summary():
    """Generate text summary of all active streams with metadata"""
    try:
        cameras = load_cameras()
        timestamp = datetime.now()
        
        summary_lines = [
            "=" * 80,
            f"CAMERA STREAMS SUMMARY REPORT",
            f"Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')}",
            "=" * 80,
            ""
        ]
        
        total_size = 0
        total_segments = 0
        
        for idx, camera in enumerate(cameras):
            camera_id = camera.get('id', idx)
            metadata = get_stream_metadata(camera_id)
            
            total_size += metadata['total_size_mb']
            total_segments += metadata['total_segments']
            
            summary_lines.extend([
                f"CAMERA {camera_id}: {camera.get('name', f'Camera {idx+1}')}",
                f"{'─' * 80}",
                f"Status:              {metadata['status'].upper()}",
                f"RTSP Source:         {camera.get('rtsp_url', 'N/A')}",
                f"Stream Directory:    {metadata['stream_path']}",
                "",
                f"SEGMENT STATISTICS:",
                f"  Total Segments:    {metadata['total_segments']} (.ts files)",
                f"  Total Stream Size: {metadata['total_size_mb']} MB",
                f"  Playlist Size:     {metadata['playlist_size_kb']} KB",
                f"  Media Sequence:    {metadata.get('media_sequence', 'N/A')}",
                f"  Target Duration:   {metadata.get('target_duration', 'N/A')} seconds",
                f"  Last Timestamp:    {metadata.get('last_timestamp', 'N/A')}",
                "",
                f"LATEST SEGMENTS (showing up to 15 most recent):",
                f"{'  Segment Name':<30} {'Size (KB)':<15} {'Modified':<25}"
            ])
            
            for seg in metadata['segments_info']:
                summary_lines.append(
                    f"  {seg['name']:<30} {seg['size_kb']:<15} {seg['mtime']:<25}"
                )
            
            summary_lines.extend([
                "",
                f"ERROR: {metadata['error']}" if metadata.get('error') else "",
                "",
                ""
            ])
        
        # Summary footer
        summary_lines.extend([
            "=" * 80,
            f"TOTAL SUMMARY",
            f"{'─' * 80}",
            f"Total Active Cameras:  {len(cameras)}",
            f"Total Segments Saved:  {total_segments}",
            f"Total Storage Used:    {total_size} MB ({round(total_size/1024, 2)} GB)",
            f"Report Generated:      {timestamp.isoformat()}",
            "=" * 80,
        ])
        
        summary_text = "\n".join(summary_lines)
        
        # Return as both JSON and plain text based on Accept header
        if request.headers.get('Accept') == 'text/plain':
            return summary_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        else:
            return jsonify({
                'summary': summary_text,
                'timestamp': timestamp.isoformat(),
                'cameras_count': len(cameras),
                'total_segments': total_segments,
                'total_size_mb': total_size,
                'metadata_by_camera': [get_stream_metadata(c.get('id', idx)) for idx, c in enumerate(cameras)]
            })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/stream-summary/<int:camera_id>')
def get_camera_stream_summary(camera_id):
    """Generate summary for a specific camera stream"""
    try:
        cameras = load_cameras()
        camera = next((c for idx, c in enumerate(cameras) if c.get('id', idx) == camera_id), None)
        
        if not camera:
            return jsonify({'error': f'Camera {camera_id} not found'}), 404
        
        metadata = get_stream_metadata(camera_id)
        timestamp = datetime.now()
        
        summary_lines = [
            "=" * 80,
            f"CAMERA {camera_id} STREAM SUMMARY",
            f"Name: {camera.get('name', f'Camera {camera_id}')}",
            f"Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80,
            "",
            f"Status:              {metadata['status'].upper()}",
            f"RTSP Source:         {camera.get('rtsp_url', 'N/A')}",
            f"Stream Directory:    {metadata['stream_path']}",
            f"IP Address:          {camera.get('ip', 'N/A')}",
            f"Port:                {camera.get('port', 'N/A')}",
            "",
            f"STREAM STATISTICS:",
            f"  Total Segments:    {metadata['total_segments']} (.ts files)",
            f"  Total Stream Size: {metadata['total_size_mb']} MB",
            f"  Playlist Size:     {metadata['playlist_size_kb']} KB",
            f"  Media Sequence:    {metadata.get('media_sequence', 'N/A')}",
            f"  Target Duration:   {metadata.get('target_duration', 'N/A')} seconds",
            f"  Last Timestamp:    {metadata.get('last_timestamp', 'N/A')}",
            "",
            f"SEGMENT DETAILS:",
            f"{'  Segment Name':<30} {'Size (KB)':<15} {'Modified':<25}"
        ]
        
        for seg in metadata['segments_info']:
            summary_lines.append(
                f"  {seg['name']:<30} {seg['size_kb']:<15} {seg['mtime']:<25}"
            )
        
        summary_lines.extend([
            "",
            "=" * 80,
        ])
        
        if metadata.get('error'):
            summary_lines.append(f"ERROR: {metadata['error']}")
        
        summary_text = "\n".join(summary_lines)
        
        if request.headers.get('Accept') == 'text/plain':
            return summary_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        else:
            return jsonify({
                'summary': summary_text,
                'camera_id': camera_id,
                'camera_info': camera,
                'metadata': metadata,
                'timestamp': timestamp.isoformat()
            })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'camera_id': camera_id,
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/video-summaries')
def get_video_summaries():
    """Get all video summaries with temporal hierarchy"""
    if not VIDEO_SUMMARIZER:
        return jsonify({'error': 'Video summarizer not initialized'}), 503
    
    try:
        summaries = VIDEO_SUMMARIZER.get_all_summaries()
        return jsonify({
            'summaries': summaries,
            'timestamp': datetime.now().isoformat(),
            'intervals': list(VIDEO_SUMMARIZER.INTERVALS.keys())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video-summaries/<int:camera_id>')
def get_camera_video_summaries(camera_id):
    """Get video summaries for a specific camera"""
    if not VIDEO_SUMMARIZER:
        return jsonify({'error': 'Video summarizer not initialized'}), 503
    
    try:
        summaries = VIDEO_SUMMARIZER.get_all_summaries(camera_id)
        
        if not summaries:
            return jsonify({
                'camera_id': camera_id,
                'message': 'No summaries generated yet',
                'intervals': list(VIDEO_SUMMARIZER.INTERVALS.keys())
            }), 204
        
        return jsonify({
            'camera_id': camera_id,
            'summaries': summaries,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video-summaries/<int:camera_id>/<interval>')
def get_camera_interval_summary(camera_id, interval):
    """Get summary for a specific camera and time interval"""
    if not VIDEO_SUMMARIZER:
        return jsonify({'error': 'Video summarizer not initialized'}), 503
    
    if interval not in VIDEO_SUMMARIZER.INTERVALS:
        return jsonify({
            'error': f'Invalid interval. Valid intervals: {list(VIDEO_SUMMARIZER.INTERVALS.keys())}'
        }), 400
    
    try:
        latest = VIDEO_SUMMARIZER.get_latest_summary(camera_id, interval)
        
        if not latest:
            return jsonify({
                'camera_id': camera_id,
                'interval': interval,
                'message': f'No {interval} summary available yet'
            }), 204
        
        return jsonify(latest)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video-summaries/report', defaults={'camera_id': None})
@app.route('/api/video-summaries/report/<int:camera_id>')
def get_summaries_report(camera_id):
    """Get formatted text report of all video summaries"""
    if not VIDEO_SUMMARIZER:
        return jsonify({'error': 'Video summarizer not initialized'}), 503
    
    try:
        report = VIDEO_SUMMARIZER.export_summaries_report(camera_id)
        
        if request.headers.get('Accept') == 'text/plain':
            return report, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        else:
            return jsonify({
                'report': report,
                'camera_id': camera_id,
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video-summaries/capture', methods=['POST'])
def capture_frame_for_summary():
    """
    Manually capture a frame from HLS stream for summarization
    
    POST data: {
        "camera_id": 0,
        "timestamp": "2025-11-15T21:23:15"
    }
    """
    if not VIDEO_SUMMARIZER:
        return jsonify({'error': 'Video summarizer not initialized'}), 503
    
    try:
        data = request.get_json() or {}
        camera_id = data.get('camera_id', 0)
        
        # Get latest segment for this camera
        stream_dir = os.path.join(HLS_DIR, f'stream_{camera_id}')
        if not os.path.exists(stream_dir):
            return jsonify({'error': f'Stream directory not found for camera {camera_id}'}), 404
        
        # Find latest .ts file
        ts_files = [f for f in os.listdir(stream_dir) if f.endswith('.ts')]
        if not ts_files:
            return jsonify({'error': f'No segments found for camera {camera_id}'}), 404
        
        latest_segment = os.path.join(stream_dir, sorted(ts_files)[-1])
        
        # Capture frame
        cap = cv2.VideoCapture(latest_segment)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return jsonify({'error': 'Failed to capture frame'}), 500
        
        # Add to summarizer
        VIDEO_SUMMARIZER.add_frame(camera_id, frame)
        
        return jsonify({
            'camera_id': camera_id,
            'segment': os.path.basename(latest_segment),
            'status': 'Frame captured and queued for analysis'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/api/ollama/summaries')
def get_ollama_summaries():
    """Get all Ollama video summaries (Gemma 3:4b)"""
    if not OLLAMA_SUMMARIZER:
        return jsonify({'error': 'Ollama summarizer not initialized'}), 503
    
    try:
        summaries = OLLAMA_SUMMARIZER.get_all_summaries()
        return jsonify({
            'summaries': summaries,
            'timestamp': datetime.now().isoformat(),
            'model': 'gemma3:4b',
            'backend': 'ollama',
            'intervals': list(OLLAMA_SUMMARIZER.INTERVALS.keys())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ollama/summaries/<int:camera_id>')
def get_ollama_camera_summaries(camera_id):
    """Get Ollama summaries for a specific camera"""
    if not OLLAMA_SUMMARIZER:
        return jsonify({'error': 'Ollama summarizer not initialized'}), 503
    
    try:
        summaries = OLLAMA_SUMMARIZER.get_all_summaries(camera_id)
        
        if not summaries:
            return jsonify({
                'camera_id': camera_id,
                'message': 'No summaries generated yet',
                'model': 'gemma3:4b'
            }), 204
        
        return jsonify({
            'camera_id': camera_id,
            'summaries': summaries,
            'timestamp': datetime.now().isoformat(),
            'model': 'gemma3:4b'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ollama/summaries/<int:camera_id>/<interval>')
def get_ollama_interval_summary(camera_id, interval):
    """Get latest Ollama summary for a specific camera and interval"""
    if not OLLAMA_SUMMARIZER:
        return jsonify({'error': 'Ollama summarizer not initialized'}), 503
    
    if interval not in OLLAMA_SUMMARIZER.INTERVALS:
        return jsonify({
            'error': f'Invalid interval. Valid intervals: {list(OLLAMA_SUMMARIZER.INTERVALS.keys())}'
        }), 400
    
    try:
        latest = OLLAMA_SUMMARIZER.get_latest_summary(camera_id, interval)
        
        if not latest:
            return jsonify({
                'camera_id': camera_id,
                'interval': interval,
                'message': f'No {interval} summary available yet',
                'model': 'gemma3:4b'
            }), 204
        
        return jsonify(latest)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ollama/report', defaults={'camera_id': None})
@app.route('/api/ollama/report/<int:camera_id>')
def get_ollama_report(camera_id):
    """Get formatted report of Ollama video summaries"""
    if not OLLAMA_SUMMARIZER:
        return jsonify({'error': 'Ollama summarizer not initialized'}), 503
    
    try:
        report = OLLAMA_SUMMARIZER.export_summaries_report(camera_id)
        
        if request.headers.get('Accept') == 'text/plain':
            return report, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        else:
            return jsonify({
                'report': report,
                'camera_id': camera_id,
                'model': 'gemma3:4b',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ollama/status')
def get_ollama_status():
    """Get Ollama integration status"""
    try:
        status = {
            'available': OLLAMA_SUMMARIZER is not None,
            'model': 'gemma3:4b',
            'backend': 'ollama',
            'timestamp': datetime.now().isoformat()
        }
        
        if OLLAMA_SUMMARIZER:
            status.update({
                'ollama_url': OLLAMA_SUMMARIZER.ollama_url,
                'ollama_health': OLLAMA_SUMMARIZER.ollama_available,
                'summaries_count': len([s for camera in OLLAMA_SUMMARIZER.get_all_summaries().values() for interval in camera.values() for s in interval])
            })
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def cleanup_streams():
    """Cleanup streams (called on shutdown only)"""
    for camera_id in list(FFMPEG_PROCESSES.keys()):
        stop_hls_stream(camera_id)
    
    # Stop Ollama frame capture service
    if OLLAMA_FRAME_CAPTURE_SERVICE:
        OLLAMA_FRAME_CAPTURE_SERVICE.stop()
    
    # Stop OpenAI frame capture service
    if FRAME_CAPTURE_SERVICE:
        FRAME_CAPTURE_SERVICE.stop()
    
    # Stop motion detection if active
    if MOTION_MANAGER:
        MOTION_MANAGER.stop_all()


if __name__ == '__main__':
    try:
        app.run(debug=False, host='0.0.0.0', port=8080, use_reloader=False)
    except KeyboardInterrupt:
        print("\nShutting down...")
        cleanup_streams()
        exit(0)

