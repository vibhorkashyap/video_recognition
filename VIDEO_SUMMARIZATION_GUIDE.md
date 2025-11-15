# Video Summarization System - Setup & Usage Guide

## Overview

The video summarization system generates **temporal summaries** of camera streams at different time intervals:
- **1 minute** - Ultra-short term activity overview
- **5 minutes** - Short-term activity patterns
- **10 minutes** - Medium-term activity summary
- **30 minutes** - Extended activity overview
- **1 hour** - Long-term activity summary

Each summary uses LLM (GPT-4 Vision) to analyze sampled frames and describe:
1. Main activities/events
2. Number of people/objects
3. Motion patterns
4. Anomalies or notable changes
5. Overall scene description

---

## Setup Instructions

### 1. Install Required Dependencies

```bash
pip install opencv-python openai
```

### 2. Configure OpenAI API Key

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY='sk-your-api-key-here'
```

Or add to your shell profile (`~/.zshrc` for macOS):

```bash
echo "export OPENAI_API_KEY='sk-your-api-key-here'" >> ~/.zshrc
source ~/.zshrc
```

### 3. Verify Setup

```bash
python -c "import openai; from video_summarizer import VideoSummarizer; print('✓ Setup complete')"
```

---

## System Architecture

### Components

1. **VideoSummarizer** (`video_summarizer.py`)
   - Manages frame buffers for each temporal interval
   - Calls GPT-4 Vision to analyze frames
   - Stores summaries to disk
   - Generates text reports

2. **FrameCaptureService** (`frame_capture_service.py`)
   - Runs in background as daemon thread
   - Captures frames from HLS segments every 15 seconds
   - Feeds frames to VideoSummarizer
   - Automatically triggers summary generation

3. **Flask API Endpoints** (in `camera_server.py`)
   - `/api/video-summaries` - All summaries
   - `/api/video-summaries/<camera_id>` - Single camera summaries
   - `/api/video-summaries/<camera_id>/<interval>` - Specific interval
   - `/api/video-summaries/report` - Formatted text report
   - `/api/video-summaries/capture` - Manual frame capture

---

## API Usage Examples

### Get All Video Summaries

```bash
curl http://localhost:8080/api/video-summaries
```

Response includes summaries from all cameras for all intervals.

### Get Camera-Specific Summaries

```bash
curl http://localhost:8080/api/video-summaries/0
```

Get all summaries for camera 0.

### Get Latest 1-Minute Summary

```bash
curl http://localhost:8080/api/video-summaries/0/minute | jq '.summary'
```

Output:
```
"At the scene, there are 2 people visible wearing business attire. The main activities include walking across the camera view from left to right. The lighting is bright from overhead fixtures. No anomalies detected. The overall scene shows normal office movement patterns."
```

### Get Latest 5-Minute Summary

```bash
curl http://localhost:8080/api/video-summaries/0/5_minutes | jq '.summary'
```

### Get Latest 10-Minute Summary

```bash
curl http://localhost:8080/api/video-summaries/0/10_minutes
```

### Get Latest 30-Minute Summary

```bash
curl http://localhost:8080/api/video-summaries/0/30_minutes
```

### Get Latest Hour Summary

```bash
curl http://localhost:8080/api/video-summaries/0/hour
```

### Get Formatted Text Report

```bash
curl -H "Accept: text/plain" http://localhost:8080/api/video-summaries/report
```

Output:
```
================================================================================
VIDEO SUMMARIES REPORT
Generated: 2025-11-15 21:35:20
================================================================================

CAMERA 0
================================================================================
  [MINUTE]
  ────────────────────────────────────────────────────────────────────────────
  Timestamp: 2025-11-15T21:31:20.123456
  Frames: 4
  Summary: Two people in the room having a meeting at the conference table...

  [5_MINUTES]
  ────────────────────────────────────────────────────────────────────────────
  Timestamp: 2025-11-15T21:31:25.456789
  Frames: 12
  Summary: Extended meeting with ongoing discussion. No movement from original ...

  [10_MINUTES]
  ...
```

### Get Specific Camera Report

```bash
curl -H "Accept: text/plain" http://localhost:8080/api/video-summaries/report/2
```

### Manual Frame Capture (for testing)

```bash
curl -X POST http://localhost:8080/api/video-summaries/capture \
  -H "Content-Type: application/json" \
  -d '{"camera_id": 0}'
```

---

## File Structure

```
/Users/vibhorkashyap/Documents/code/
├── camera_server.py          # Flask server (API endpoints)
├── video_summarizer.py       # Video analysis & LLM integration
├── frame_capture_service.py  # Background frame capture daemon
├── video_summaries/          # Output directory for summaries
│   ├── camera_0/
│   │   ├── minute_20251115_213000.json
│   │   ├── 5_minutes_20251115_213500.json
│   │   ├── 10_minutes_20251115_214000.json
│   │   ├── 30_minutes_20251115_215000.json
│   │   └── hour_20251115_220000.json
│   ├── camera_1/
│   │   └── ...
│   └── ...
└── hls_streams/
    ├── stream_0/
    ├── stream_1/
    ├── stream_2/
    └── stream_3/
```

---

## Summary JSON Format

```json
{
  "timestamp": "2025-11-15T21:31:20.123456",
  "camera_id": 0,
  "camera_name": "Camera 1",
  "interval": "minute",
  "frames_analyzed": 4,
  "summary": "Two people visible in the room. One person is seated at desk, another standing nearby. Minimal motion detected. Lighting is bright. No anomalies observed. Overall normal office activity.",
  "start_time": "2025-11-15T21:30:00.000000",
  "end_time": "2025-11-15T21:31:00.000000"
}
```

---

## Temporal Hierarchy Explanation

### 1-Minute Summaries
- **When**: Every 60 seconds
- **Frames**: ~4 frames sampled from the minute
- **Use**: Real-time activity detection, instant alerts
- **Example**: "2 people walking across scene"

### 5-Minute Summaries
- **When**: Every 300 seconds
- **Frames**: ~12 frames (every 25 seconds)
- **Use**: Short-term pattern recognition
- **Example**: "Continuous foot traffic in hallway, 5-8 people per minute"

### 10-Minute Summaries
- **When**: Every 600 seconds
- **Frames**: ~24 frames
- **Use**: Activity trend analysis
- **Example**: "Scene shows gradual increase in activity, meeting in progress at table"

### 30-Minute Summaries
- **When**: Every 1800 seconds
- **Frames**: ~60 frames
- **Use**: Extended activity overview
- **Example**: "Office section remains moderately busy with consistent foot traffic and two active meetings"

### 1-Hour Summaries
- **When**: Every 3600 seconds
- **Frames**: ~120 frames
- **Use**: Long-term trend analysis, daily activity patterns
- **Example**: "Morning shift shows steady office activity with peak during 2-3 PM, normal pattern observed"

---

## Customization

### Change Frame Capture Interval

Edit `camera_server.py` in the `startup()` function:

```python
FRAME_CAPTURE_SERVICE = FrameCaptureService(
    HLS_DIR, 
    VIDEO_SUMMARIZER, 
    capture_interval=10  # Change from 15 to 10 seconds
)
```

### Change Summary Intervals

Edit `video_summarizer.py`:

```python
INTERVALS = {
    'minute': 60,
    '5_minutes': 300,
    '10_minutes': 600,
    '30_minutes': 1800,
    'hour': 3600,
    # Add custom:
    '3_minutes': 180,
}
```

### Adjust LLM Analysis

Edit the `analyze_frames_with_llm()` method in `video_summarizer.py`:

```python
response = self.client.messages.create(
    model="gpt-4-turbo",
    max_tokens=250,  # Shorter summaries
    temperature=0.5,  # More conservative
    messages=[...]
)
```

---

## Monitoring & Debugging

### Check Server Logs

```bash
tail -f /Users/vibhorkashyap/Documents/code/server.log
```

### Verify Frame Capture is Running

```bash
curl http://localhost:8080/api/video-summaries/0 | jq '.summaries.minute | length'
```

This should show an increasing number as summaries are generated.

### Check Summary Files on Disk

```bash
ls -lh /Users/vibhorkashyap/Documents/code/video_summaries/camera_0/
```

### Test Without API Key (Placeholder Mode)

If you don't have an OpenAI API key, summaries will still be generated with:
```
"summary": "No LLM analysis available (missing API key or frames)"
```

This is useful for testing the system architecture before integrating LLM.

---

## Troubleshooting

### "Video summarizer not initialized"

Solution: Ensure dependencies are installed and server is fully started:

```bash
pip install opencv-python openai
python -c "from video_summarizer import VideoSummarizer; print('OK')"
```

### OpenCV errors reading .ts files

This is expected - some segments might not be fully written yet. The system automatically handles this and continues.

### API key not recognized

Ensure you exported the key:

```bash
echo $OPENAI_API_KEY  # Should print your key
```

If empty, re-run:

```bash
export OPENAI_API_KEY='sk-your-key'
```

### Summaries not generating

1. Check that frame capture service is running (look in server.log)
2. Verify at least 60 seconds have passed for minute summaries
3. Check OpenAI API rate limits
4. Ensure API key has sufficient quota

---

## Performance Notes

- **Frame Capture**: ~50-100ms per frame (depends on segment size)
- **LLM Analysis**: ~3-5 seconds per summary (network + processing)
- **Storage**: ~500KB-1MB per camera per day (summaries only, not video)
- **Memory**: ~100-200MB (frames kept in buffer during interval)

---

## Next Steps

1. Set up OpenAI API key
2. Restart the server
3. Wait 1 minute for first summary
4. Query `/api/video-summaries/0/minute`
5. View formatted report: `/api/video-summaries/report`

Enjoy automated video understanding! 🎥📊
