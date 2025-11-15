# ⌨️ Minimal Dashboard - Complete Reference

## Quick Start (30 Seconds)

1. **Start Server**
   ```bash
   cd /Users/vibhorkashyap/Documents/code
   source .venv/bin/activate
   python camera_server.py
   ```

2. **Open Browser**
   ```
   http://localhost:8080
   ```

3. **Watch Videos**
   - Videos auto-load and start playing
   - Use standard video controls
   - Click ⓘ for camera details

Done! 🎉

## Dashboard Overview

### What You See
```
┌─────────────────────────────────────┐
│  Video 1 (ⓘ)  │  Video 2 (ⓘ)      │
├─────────────────────────────────────┤
│  Video 3 (ⓘ)  │  Video 4 (ⓘ)      │
└─────────────────────────────────────┘
```

### What Each Element Does
- **Videos**: Live HLS streams from cameras
- **ⓘ Button**: Click to see camera details
- **Video Controls**: Standard player controls

## Using the Dashboard

### View Live Streams
✅ **Automatic**: Videos start playing when page loads
✅ **Wait**: First segment takes 5-10 seconds
✅ **Control**: Use player buttons to play/pause/adjust volume

### Access Camera Info
1. **Click ⓘ button** on any video
2. **See modal popup** with:
   - Camera IP address
   - ONVIF port
   - Stream profile
   - RTSP URL
   - HLS URL
3. **Actions available**:
   - 📋 Copy RTSP URL
   - 📺 Open in VLC
4. **Close modal**: Click X or click outside

### Video Player Controls

| Control | Action | Shortcut |
|---------|--------|----------|
| Play/Pause | Click play button | Space |
| Volume | Click volume icon | Up/Down arrows |
| Seek | Drag progress bar | Left/Right arrows |
| Fullscreen | Click fullscreen button | F |
| Settings | Click settings icon | S |

### Keyboard Shortcuts

#### Global
| Key | Action |
|-----|--------|
| F5 / Cmd+R | Refresh page |
| Cmd+Shift+Del | Clear cache |
| F12 / Cmd+Option+J | Open console |

#### Video Player (when focused)
| Key | Action |
|-----|--------|
| Space | Play/Pause |
| F | Fullscreen |
| M | Mute/Unmute |
| → | Seek +10s |
| ← | Seek -10s |
| ↑ | Volume +10% |
| ↓ | Volume -10% |
| . | Step frame forward |
| , | Step frame backward |
| 0-9 | Jump to position |
| > | Speed up |
| < | Speed down |
| P | Picture-in-Picture |
| C | Toggle captions |
| ? | Help (if available) |

## Common Tasks

### Watch Fullscreen
1. Click the video
2. Click fullscreen button (bottom-right)
3. Press F to exit

### Copy RTSP URL
1. Click ⓘ button on video
2. Click "📋 Copy RTSP URL"
3. Paste in VLC or other app

### Open in VLC
1. Click ⓘ button on video
2. Click "📺 Open in VLC"
3. VLC opens automatically

### Monitor Multiple Cameras
1. 2×2 grid shows all 4 cameras at once
2. Perfect for multi-monitor setups
3. Each video can be fullscreen independently

### Check Network Performance
1. Open browser DevTools (F12)
2. Go to Network tab
3. Watch HLS segments download
4. Segments are ~1-2MB each
5. One segment every 5 seconds

## Settings & Customization

### Video Quality (Edit camera_server.py)
```python
# Line in start_hls_stream() function:

# Lower quality (faster, less bandwidth)
'-b:v', '400k',
'-preset', 'ultrafast',

# Standard (current)
'-b:v', '800k',
'-preset', 'veryfast',

# Higher quality (slower, more bandwidth)
'-b:v', '1500k',
'-preset', 'medium',
```

### Refresh Server After Changes
```bash
pkill -f camera_server
python camera_server.py
```

### Grid Layout (Edit templates/index.html)
```css
/* Change from 2×2 to 3×2 */
.camera-grid {
    grid-template-columns: 1fr 1fr 1fr;  /* 3 columns */
    grid-template-rows: 1fr 1fr;         /* 2 rows */
    gap: 8px;  /* Increase gap to 8px */
}
```

## Troubleshooting

### Problem: Videos Not Playing

**Symptoms**:
- Black video, no content
- Player shows "buffering" forever
- No error messages

**Solutions**:
1. **Wait longer** - First video takes 10+ seconds
2. **Refresh page** - Press F5
3. **Restart server**:
   ```bash
   pkill -f camera_server
   python camera_server.py
   ```
4. **Check camera** - May be offline or unreachable

### Problem: Video Stuttering/Freezing

**Symptoms**:
- Video plays then freezes
- Audio/video out of sync
- Happens repeatedly

**Solutions**:
1. **Pause and resume** - Click play/pause
2. **Lower video quality** - Edit camera_server.py (reduce bitrate)
3. **Check network** - Run speed test
4. **Check camera** - Verify it's online
5. **Restart FFmpeg** - Stop and start server

### Problem: ⓘ Button Not Working

**Symptoms**:
- Click button, nothing happens
- Modal doesn't appear
- Console shows errors (F12)

**Solutions**:
1. **Refresh page** - F5
2. **Clear cache** - Cmd+Shift+Delete
3. **Try different browser** - Chrome, Firefox, Safari
4. **Check console** - F12 → Console tab for errors

### Problem: Can't Copy RTSP URL

**Symptoms**:
- Click copy button, nothing happens
- Browser shows permission error

**Solutions**:
1. **Check permissions** - Browser may block clipboard
2. **Manual copy** - See URL in modal, select and copy manually
3. **Different approach** - Use "Open in VLC" instead

### Problem: Audio Issues

**Symptoms**:
- Video plays but no sound
- Audio only from one camera
- Intermittent audio

**Solutions**:
1. **Check volume** - Unmute player (M key)
2. **Check camera** - Not all cameras have audio
3. **Check browser audio** - System audio settings
4. **Restart browser** - Close and reopen

### Problem: Server Won't Start

**Symptoms**:
- Python command gives error
- Port 8080 in use
- Connection refused

**Solutions**:
```bash
# Check what's using port 8080
lsof -i :8080

# Kill existing process
kill -9 [PID]

# Or use different port (edit camera_server.py)
app.run(port=8081)

# Then access at:
http://localhost:8081
```

### Problem: High CPU Usage

**Symptoms**:
- Mac fans running loud
- System slow
- Excessive heat

**Solutions**:
1. **Reduce video quality**:
   - Edit camera_server.py
   - Change `'-preset', 'veryfast'` to `'ultrafast'`
   - Change `'-b:v', '800k'` to `'400k'`

2. **Reduce number of cameras**:
   - Edit start_hls_stream() to skip some cameras

3. **Stop unnecessary processes**:
   ```bash
   pkill -f camera_server
   pkill -f ffmpeg
   ```

## System Requirements

### Hardware
- **CPU**: Minimum 2 cores (4+ recommended)
- **RAM**: Minimum 4GB (8GB+ recommended)
- **Network**: 1 Mbps per camera
- **Storage**: 50MB free minimum

### Software
- **Python**: 3.13.x
- **FFmpeg**: Latest (Homebrew)
- **Browser**: Any modern browser
- **OS**: macOS 10.13+

### Network
- **Router**: 2.4GHz or 5GHz WiFi
- **Bandwidth**: 4 Mbps for 4 cameras
- **Latency**: <100ms recommended

## Performance Tips

### Improve Speed
1. **Use wired network** - Faster than WiFi
2. **Close other apps** - Free up RAM
3. **Use Chrome** - Fastest HLS.js support
4. **Restart browser** - Clear memory leaks

### Improve Video Quality
1. **Increase bitrate** - Edit camera_server.py
2. **Use faster preset** - Change `veryfast` to `medium`
3. **Check camera resolution** - Higher = better quality
4. **Verify network speed** - Need 4+ Mbps for 4 cameras

### Reduce CPU Usage
1. **Lower bitrate** - Use `400k` instead of `800k`
2. **Use faster preset** - Use `ultrafast` instead of `veryfast`
3. **Monitor fewer cameras** - Comment out some cameras
4. **Close browser tabs** - Each tab uses CPU

## Advanced Usage

### Access from Another Device
```
Local Network (same WiFi):
http://192.168.0.155:8080

Replace 192.168.0.155 with your Mac's IP:
ifconfig | grep "inet "
```

### Enable HTTPS (Secure)
See HLS_STREAMING_SETUP.md for SSL configuration

### Add Authentication
See HLS_STREAMING_SETUP.md for basic auth setup

### Record Streams
Edit camera_server.py to add recording functionality

### Set Up Cron Auto-Start
```bash
crontab -e

# Add this line:
@reboot cd /Users/vibhorkashyap/Documents/code && source .venv/bin/activate && python camera_server.py > /tmp/camera_server.log 2>&1 &
```

## Browser Compatibility

| Browser | HLS | Controls | Fullscreen | Copy |
|---------|-----|----------|-----------|------|
| Chrome | ✅ | ✅ | ✅ | ✅ |
| Firefox | ✅ | ✅ | ✅ | ✅ |
| Safari | ✅ | ✅ | ✅ | ✅ |
| Edge | ✅ | ✅ | ✅ | ✅ |
| Mobile Safari | ✅ | ✅ | ✅ | ⚠️ |
| Chrome Mobile | ✅ | ✅ | ✅ | ✅ |

## Useful Commands

```bash
# Start server
cd /Users/vibhorkashyap/Documents/code && source .venv/bin/activate && python camera_server.py

# Start in background
cd /Users/vibhorkashyap/Documents/code && source .venv/bin/activate && python camera_server.py > server.log 2>&1 &

# Stop server
pkill -f camera_server

# Stop everything
pkill -f "camera_server\|ffmpeg"

# Check if running
ps aux | grep -E "camera_server|ffmpeg" | grep -v grep

# View logs
tail -f /Users/vibhorkashyap/Documents/code/server.log

# Test connection
curl http://localhost:8080/api/cameras

# Monitor FFmpeg
watch -n 1 'ps aux | grep ffmpeg | grep -v grep'

# Check disk usage
du -sh /Users/vibhorkashyap/Documents/code/hls_streams/
```

## Documentation

- **MINIMAL_DASHBOARD_GUIDE.md** - User guide
- **DASHBOARD_COMPARISON.md** - Before & after
- **HLS_STREAMING_SETUP.md** - Technical setup
- **SYSTEM_READY.md** - System overview
- **QUICK_START_HLS.md** - Quick start

## Support

### Where to Find Help
1. Check documentation files above
2. Review browser console (F12)
3. Check server logs: `tail -f server.log`
4. Run system verification: `python verify_hls_system.py`

### Report Issues
Include:
- Browser type and version
- Operating system
- Error message (if any)
- Steps to reproduce
- Screenshots if helpful

---

**Dashboard Version**: 2.0 - Minimal UI
**Last Updated**: 2025-11-15
**Status**: ✅ Production Ready
