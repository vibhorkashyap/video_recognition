# Camera Events AI System - Implementation Guide

## Overview
Your camera system now includes an intelligent motion detection and AI analysis system with a chat interface for querying events.

## Architecture

### 1. **Motion Detection System** (`motion_detector.py`)
- Detects motion in camera feeds using frame differencing
- Records clips when motion is detected
- Configurable sensitivity and buffer times
- Pre/post motion capture for context

**Key Features:**
- Pre-motion buffer: 5 seconds (captures activity before motion trigger)
- Post-motion buffer: 5 seconds (captures activity after motion stops)
- Sensitivity: 2% of frame (configurable)
- Stores clips with metadata in `/clips/camera_X/` directories

### 2. **LLM Analysis System** (`llm_analyzer.py`)
- Sends motion-detected clips to LLM for analysis
- Generates text descriptions of events
- Supports OpenAI API and local Ollama models
- Queues clips for batch processing

**Features:**
- Processes clips asynchronously
- Updates metadata with descriptions
- Supports multiple LLM backends

### 3. **Backend Integration** (`camera_server.py`)
**New Endpoints:**
- `GET /api/clips/<camera_id>` - Get clips for a camera with optional time filtering
- `POST /api/chat` - Query events using natural language
- `GET /chat` - Chat interface page

### 4. **Chat Interface** (`templates/chat.html`)
Modern chat-based interface for querying events:
- Filter by camera, date, and time range
- Natural language queries
- Timeline view of events
- Real-time conversation history

## Usage

### Start Motion Detection
```python
# In your application
from motion_detector import MotionDetectionManager
from camera_server import load_cameras

cameras = load_cameras()
motion_manager = MotionDetectionManager(cameras)
motion_manager.start_all()
```

### Enable in Server
Uncomment these lines in `camera_server.py` `startup()` function:
```python
from motion_detector import MotionDetectionManager
MOTION_MANAGER = MotionDetectionManager(cameras)
MOTION_MANAGER.start_all()  # Uncomment this line
```

### Access Chat Interface
Open browser: `http://localhost:8080/chat`

**Features:**
1. **Filter Section:**
   - Select camera (1-4)
   - Set date/time range
   - Click "Search Events"

2. **Timeline:**
   - Shows recent motion events
   - Click event to add to query

3. **Chat Area:**
   - Ask questions about events
   - Examples:
     - "Show me person detection from today"
     - "What happened on camera 1 at 3 PM?"
     - "List all events with motion"

## Configuration

### Motion Detection Parameters
Edit in `motion_detector.py`:

```python
self.motion_threshold = 500  # Pixel area for motion
self.sensitivity = 0.02  # % of frame that must change
self.clip_duration = 15  # Clip length in seconds
self.pre_motion_buffer = 5  # Seconds before motion
self.post_motion_buffer = 5  # Seconds after motion
self.buffer_fps = 5  # Frame rate for buffering
```

### LLM Configuration
For OpenAI:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

For local Ollama:
```python
analyzer = ClipAnalyzer(use_local=True, model="llama2")
```

## Data Structure

### Clips Metadata (`clips/camera_X/metadata.json`)
```json
{
  "clip_id": 0,
  "camera_id": 0,
  "filename": "motion_20251115_175200.mp4",
  "filepath": "/Users/vibhorkashyap/Documents/code/clips/camera_0/motion_20251115_175200.mp4",
  "timestamp": "2025-11-15T17:52:00.123456",
  "duration": 15.5,
  "motion_start": 1700076720.5,
  "motion_end": 1700076735.2,
  "status": "pending_analysis | analyzed",
  "description": "Person walking through frame",
  "analysis_time": "2025-11-15T17:52:30.456789"
}
```

## API Reference

### Get Clips
```bash
GET /api/clips/0?start_time=2025-11-15T00:00:00&end_time=2025-11-15T23:59:59
```

Response:
```json
[
  {
    "clip_id": 0,
    "camera_id": 0,
    "timestamp": "2025-11-15T17:52:00",
    "description": "Motion detected",
    "duration": 15.5
  }
]
```

### Chat Query
```bash
POST /api/chat
Content-Type: application/json

{
  "query": "Show me recent motion",
  "camera_id": 0,
  "start_time": "2025-11-15T17:00:00",
  "end_time": "2025-11-15T18:00:00"
}
```

Response:
```json
{
  "query": "Show me recent motion",
  "camera_id": 0,
  "summary": "Found 3 events matching 'recent motion' on camera 0",
  "relevant_clips": [
    {
      "timestamp": "2025-11-15T17:52:00",
      "description": "Person walking"
    }
  ]
}
```

## Next Steps

### To Enable:
1. Install OpenCV: `pip install opencv-python`
2. Uncomment motion detection in `camera_server.py`
3. Set OpenAI API key: `export OPENAI_API_KEY="..."`
4. Restart server: `killall camera_server && python camera_server.py`

### Future Enhancements:
- [ ] Real-time video preview in chat
- [ ] WebSocket support for live updates
- [ ] Object detection (person, car, animal)
- [ ] Clip playback in browser
- [ ] Alert notifications
- [ ] Scheduled cleanup of old clips
- [ ] Export clips/reports
- [ ] Multi-language support for descriptions

## Troubleshooting

**No clips being saved:**
- Check if motion detection is enabled
- Verify clip directory exists: `/clips/camera_X/`
- Check motion sensitivity settings

**Chat not returning results:**
- Verify clips exist for the selected camera
- Check timestamp format in filters
- Ensure time range is correct

**LLM analysis not working:**
- Verify OpenAI API key is set
- Check network connectivity
- Verify API quota not exceeded

## Storage

Clips are stored in:
```
/Users/vibhorkashyap/Documents/code/clips/
├── camera_0/
│   ├── metadata.json
│   ├── motion_20251115_175200.mp4
│   └── motion_20251115_180500.mp4
├── camera_1/
│   └── ...
```

Recommend setting up cleanup:
```bash
# Remove clips older than 7 days
find /Users/vibhorkashyap/Documents/code/clips -name "*.mp4" -mtime +7 -delete
```

## Performance Tips

1. **Reduce sensitivity** if you get too many false positives
2. **Increase buffer size** for longer clips (uses more disk space)
3. **Use lower FPS** for faster motion detection
4. **Process clips asynchronously** to avoid blocking video capture
5. **Compress clips** using lower bitrate in FFmpeg

---

Enjoy your new AI-powered camera events system! 🎥🤖
