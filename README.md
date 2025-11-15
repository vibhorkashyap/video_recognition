# 🎥 Camera Monitoring System

A complete camera discovery and monitoring system built with Python, Flask, and modern web technologies.

## Features

✅ **Automatic Camera Discovery** - Find all cameras on your network using network scanning
✅ **RTSP Stream Extraction** - Automatically extract RTSP URLs from ONVIF cameras
✅ **Web Dashboard** - Beautiful, responsive grid interface to view all camera streams
✅ **Stream Management** - Copy stream URLs, open individual streams, view camera details
✅ **Real-time Monitoring** - Live statistics and camera status updates

## Components

### 1. **find_cameras.py** - Network Camera Scanner
Automatically discovers IP cameras on your network using multiple methods:
- Network scanning with `nmap` or fallback to port probing
- Banner detection to identify camera services
- MAC address OUI matching to identify camera vendors
- Multi-threaded scanning for speed

**Usage:**
```bash
# Scan entire subnet
python find_cameras.py

# Scan specific IPs
python find_cameras.py 192.168.0.100 192.168.0.102 192.168.0.118
```

### 2. **extract_rtsp_urls.py** - RTSP URL Extractor
Connects to discovered cameras via ONVIF and extracts their RTSP stream URLs.

**Usage:**
```bash
/Users/vibhorkashyap/Documents/code/.venv/bin/python extract_rtsp_urls.py
```

Output: `cameras.json` containing all discovered cameras and their RTSP URLs

### 3. **camera_server.py** - Flask Backend Server
REST API server that serves the web dashboard and provides camera data.

**API Endpoints:**
- `GET /` - Main dashboard page
- `GET /api/cameras` - List all cameras with their RTSP URLs
- `GET /api/cameras/<id>` - Get specific camera details

**Usage:**
```bash
/Users/vibhorkashyap/Documents/code/.venv/bin/python camera_server.py
```

Server runs on `http://localhost:8080`

### 4. **templates/index.html** - Web Dashboard
Beautiful, responsive web interface for monitoring cameras:
- 2x2 responsive grid layout
- Live camera feeds
- Camera status indicators
- Quick links to open streams in VLC
- Copy RTSP URL button for easy sharing
- Real-time statistics

## Installation

### Prerequisites
- Python 3.7+
- Virtual environment activated

### Setup
```bash
# Activate virtual environment
cd /Users/vibhorkashyap/Documents/code
source .venv/bin/activate

# Install dependencies
pip install onvif-zeep flask

# Extract camera URLs
python extract_rtsp_urls.py

# Start the web server
python camera_server.py
```

Then open `http://localhost:8080` in your browser.

## Camera Configuration

The system uses default credentials:
- **Username:** admin
- **Password:** shivasindia

Edit `extract_rtsp_urls.py` to change credentials or add/remove camera IPs.

## Discovered Cameras

The system successfully found and configured these cameras:

| Camera ID | IP Address    | RTSP Port | Stream URL                        |
|-----------|----------------|-----------|-----------------------------------|
| Camera 1  | 192.168.0.100  | 5543      | rtsp://192.168.0.100:5543/live/channel0  |
| Camera 2  | 192.168.0.101  | 5543      | rtsp://192.168.0.101:5543/live/channel0  |
| Camera 3  | 192.168.0.102  | 5543      | rtsp://192.168.0.102:5543/live/channel0  |
| Camera 4  | 192.168.0.118  | 5543      | rtsp://192.168.0.118:5543/live/channel0  |

## Viewing Streams

### Option 1: Web Dashboard
Open `http://localhost:8080` and click "📺 Open Stream" for any camera

### Option 2: VLC Media Player
Go to "Media" → "Open Network Stream" and paste the RTSP URL

### Option 3: Command Line (ffplay)
```bash
ffplay rtsp://192.168.0.100:5543/live/channel0
```

### Option 4: Command Line (ffmpeg)
```bash
ffmpeg -i rtsp://192.168.0.100:5543/live/channel0 -f sdl "Camera Stream"
```

## File Structure
```
/Users/vibhorkashyap/Documents/code/
├── find_cameras.py              # Network scanner
├── extract_rtsp_urls.py         # RTSP URL extractor
├── camera_server.py             # Flask API server
├── cameras.json                 # Camera configuration (auto-generated)
├── templates/
│   └── index.html              # Web dashboard
└── .venv/                       # Virtual environment
```

## Technology Stack

- **Backend:** Python 3, Flask
- **Camera Protocol:** ONVIF, RTSP
- **Network Tools:** nmap, socket, subprocess
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Streaming:** RTSP via browser video elements

## Troubleshooting

### Cameras not detected?
1. Make sure cameras are on the same network
2. Verify network connectivity: `ping 192.168.0.100`
3. Check camera ONVIF port: `nc -zv 192.168.0.100 8000`

### Streams not playing in browser?
Browsers don't natively support RTSP. Use:
- VLC Media Player
- ffplay command
- RTSP to HLS converter (separate tool)

### Port already in use?
Edit `camera_server.py` and change port number:
```python
app.run(debug=True, host='0.0.0.0', port=8888)  # Change 8080 to another port
```

## Future Enhancements

- [ ] HLS/HTTP streaming support for browser playback
- [ ] Persistent camera database
- [ ] Video recording to disk
- [ ] Motion detection alerts
- [ ] Multi-user authentication
- [ ] Mobile app support
- [ ] Cloud backup integration

## License

MIT License

## Support

For issues or questions, refer to the RTSP streaming documentation or camera manufacturer documentation.
