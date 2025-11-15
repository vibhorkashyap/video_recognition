# Quick Start Guide

## Prerequisites
- macOS with Python 3
- Virtual environment already set up
- Cameras connected to your 192.168.0.x network

## Step 1: Extract RTSP URLs

Run this command to automatically discover and extract RTSP URLs from all cameras:

```bash
cd /Users/vibhorkashyap/Documents/code
source .venv/bin/activate
python extract_rtsp_urls.py
```

**Output:**
```
Extracting RTSP URLs from cameras...

Scanning 192.168.0.100...
  Trying 192.168.0.100:80... ✗
  Trying 192.168.0.100:8000... ✓ Found at port 8000
  RTSP URL: rtsp://192.168.0.100:5543/live/channel0

...

✓ Found 4 cameras
Camera data saved to cameras.json
```

## Step 2: Start the Dashboard

```bash
python camera_server.py
```

**Output:**
```
 * Serving Flask app 'camera_server'
 * Debug mode: on
 * Running on http://0.0.0.0:8080
```

## Step 3: Open Dashboard

Open your browser to: **http://localhost:8080**

You should see a beautiful dashboard with all 4 cameras in a grid layout!

## Features You Can Use:

### 📺 Watch Streams
- Click "📺 Open Stream" button on any camera card
- Opens in your default media player (VLC)

### 📋 Copy URLs
- Click "📋 Copy URL" to copy RTSP URL to clipboard
- Use in VLC, ffmpeg, or any RTSP-compatible player

### 📊 View Statistics
- See number of online cameras
- View last update time
- Monitor connection status

### 🎯 View Camera Details
- IP Address
- Port number
- Stream name
- Full RTSP URL

## Common Tasks:

### Watch a camera in VLC
1. Open VLC Media Player
2. Go to "Media" → "Open Network Stream"
3. Paste RTSP URL from the dashboard
4. Click "Play"

### Watch a camera in terminal
```bash
ffplay rtsp://192.168.0.100:5543/live/channel0
```

### Record a camera stream
```bash
ffmpeg -i rtsp://192.168.0.100:5543/live/channel0 -c copy recording.mp4
```

### Change server port
Edit `camera_server.py` line 26:
```python
app.run(debug=True, host='0.0.0.0', port=8888)  # Change 8080 to your port
```

### Add more cameras
Edit `extract_rtsp_urls.py` line 12 and add camera IP:
```python
CAMERAS = [
    {"ip": "192.168.0.100", "username": "admin", "password": "shivasindia"},
    {"ip": "192.168.0.999", "username": "admin", "password": "shivasindia"},  # Add here
]
```

## Troubleshooting:

**Q: Port 8080 is already in use**
A: Change the port in `camera_server.py` to 8888, 9000, or another available port

**Q: Cameras not showing in dashboard**
A: Make sure you ran `python extract_rtsp_urls.py` and `cameras.json` exists

**Q: Can't see video feed in browser**
A: Browsers don't support RTSP natively. Use "Open Stream" button to watch in VLC instead

**Q: Can't connect to camera**
A: Verify:
- Camera is powered on and connected to network
- You're on the same network as cameras
- Default credentials are correct (admin/shivasindia)

## Next Steps:

1. Monitor your cameras from the dashboard
2. Export RTSP URLs for other applications
3. Set up motion detection or recording
4. Share camera URLs with team members

Enjoy your camera monitoring system! 🎉
