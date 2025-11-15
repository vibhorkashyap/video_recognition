# 🎥 Camera Monitoring System - Quick Start

## ⚡ 30-Second Setup

### Step 1: Start the Server
```bash
cd /Users/vibhorkashyap/Documents/code
source .venv/bin/activate
python camera_server.py
```

### Step 2: Open Browser
```
http://localhost:8080
```

### Done! 🎉
Your camera feeds are now streaming in the browser in real-time.

---

## 📺 What You'll See

A responsive 2×2 camera grid showing:
- Live video stream from each camera
- Camera IP address
- Stream profile information
- Buttons to copy RTSP URL or open in VLC

## 🎬 Video Playback

- **Automatic**: Videos start playing once page loads
- **Manual**: Click play button on video card
- **Controls**: Use standard video player controls (play, pause, volume, fullscreen)

## 🔧 Common Tasks

### Stop the Server
```bash
pkill -f camera_server
```

### View Server Logs
```bash
tail -f server.log
```

### Check Stream Status
```bash
# See FFmpeg processes
ps aux | grep ffmpeg | grep -v grep

# Check HLS segments
ls -lah hls_streams/stream_0/
```

### Access from Another Device
```
http://192.168.0.155:8080
```
(Replace 192.168.0.155 with your Mac's IP if different)

---

## 💡 Pro Tips

1. **Low Latency**: Each video segment is only 5 seconds, so ~5-10 second stream delay is normal
2. **Quality**: If video is choppy, it means lower network bandwidth - this is auto-adjusted by the system
3. **Resolution**: Current setup streams 800kbps - adjust in `camera_server.py` if needed
4. **Fullscreen**: Click fullscreen button on video player for immersive view
5. **Multi-device**: Open dashboard on multiple devices to monitor same cameras

---

## 📊 System Requirements

- ✅ Python 3.13.7
- ✅ FFmpeg (auto-started by Flask)
- ✅ Modern web browser (Chrome, Firefox, Safari, Edge)
- ✅ ~100MB disk space for HLS segments
- ✅ ~15-20% CPU per camera (due to H.264 encoding)

---

## 🎯 What's Actually Running

When you start the server:
1. **Flask Web Server** (port 8080) - serves dashboard and HLS playlists
2. **4 FFmpeg Processes** - convert RTSP streams to HLS in real-time
3. **Auto-cleanup** - old video segments deleted after 30 seconds

Total memory usage: ~800MB-1GB
CPU usage: ~15-20% per camera (varies with bitrate)

---

## 🆘 Not Working?

### Videos show but no video playback
- Wait 10 seconds for FFmpeg to generate segments
- Check browser console (F12) for errors
- Try refreshing the page

### Videos don't show at all
- Check Flask is running: `lsof -i :8080`
- Verify cameras are online: Check `cameras.json`
- Restart: `pkill -f camera_server && python camera_server.py`

### Server won't start
- Check Python: `python --version` (should be 3.13.x)
- Check venv: `source .venv/bin/activate`
- Check dependencies: `pip list | grep -E "Flask|requests"`

---

## 📖 Full Documentation

See `HLS_STREAMING_SETUP.md` for complete technical details, API reference, and troubleshooting.

---

**Ready to view your cameras? Open [http://localhost:8080](http://localhost:8080) now!**
