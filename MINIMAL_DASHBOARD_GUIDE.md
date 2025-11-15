# 📺 Minimal Camera Dashboard - User Guide

## Overview

The dashboard now displays a clean, minimal interface with just the essentials:
- **2×2 grid** of live video streams
- **Full-screen video focus** - no distracting elements
- **Small info button** (ⓘ) on each video to access camera details

## Layout

```
┌─────────────────────────────────────┐
│  Video 1          │  Video 2        │
│     [ⓘ]          │      [ⓘ]        │
├─────────────────────────────────────┤
│  Video 3          │  Video 4        │
│     [ⓘ]          │      [ⓘ]        │
└─────────────────────────────────────┘
```

## How to Use

### View Live Streams
1. Open browser: **http://localhost:8080**
2. Streams auto-load and start playing (may take 5-10 seconds for first segment)
3. Use video player controls:
   - **Play/Pause**: Click play button or space bar
   - **Volume**: Click volume icon
   - **Fullscreen**: Click fullscreen button (bottom right)
   - **Progress Bar**: Drag to seek (if supported by HLS)

### Access Camera Details
1. **Click the info button (ⓘ)** on any video
2. A modal window appears showing:
   - Camera IP address
   - ONVIF port
   - Stream profile name
   - RTSP URL
   - HLS URL
3. **Action buttons** in the modal:
   - **📋 Copy RTSP URL**: Copy to clipboard for external apps
   - **📺 Open in VLC**: Opens RTSP stream in VLC (if installed)
4. **Close modal**: Click X button or click outside the modal

## Features

### Minimal UI
- ✅ No header or title (full focus on video)
- ✅ No statistics panel
- ✅ No camera info permanently visible
- ✅ Black background (cinema mode)
- ✅ Thin borders between videos (4px gap)

### Responsive Design
- Works on desktop (2×2 grid)
- Works on tablet (2×1 or 1×2 depending on orientation)
- Works on mobile (stacked vertically)

### Video Controls
- Built-in HTML5 player controls
- HLS streaming support
- Auto-retry on errors
- Low-latency mode enabled

### Information Access
- Hover over camera cards to see subtle effects
- Click info button for detailed information
- Copy RTSP URL with one click
- Open in VLC with one click

## Keyboard Shortcuts

While a video is focused (click it first):
- **Space** - Play/Pause
- **F** - Fullscreen
- **M** - Mute/Unmute
- **→/←** - Seek forward/backward (10 seconds)
- **↑/↓** - Adjust volume
- **P** - Picture-in-Picture (if supported)

## Tips & Tricks

### Fullscreen Viewing
1. Click the video you want to view
2. Click fullscreen button (bottom-right corner)
3. Press F on keyboard to exit fullscreen

### Multi-Monitor Setup
- Each video can be opened in fullscreen on different monitors
- Perfect for multi-screen surveillance setups

### Aspect Ratio
- Videos automatically scale to fit the grid
- Maintains aspect ratio from camera source
- Uses "object-fit: cover" for full utilization of space

### Performance
- Videos stream at 800 kbps each
- Total network usage: ~3.2 Mbps for 4 cameras
- Each stream has ~5-10 second delay (HLS inherent)
- Minimum 30MB disk space required (auto-cleaning)

## Troubleshooting

### Videos Not Playing
- **Wait 10 seconds**: FFmpeg needs time to generate segments
- **Refresh page**: F5 or Cmd+R
- **Check server**: `lsof -i :8080`
- **Check FFmpeg**: `ps aux | grep ffmpeg`

### Video Freezes
- **Pause and resume**: Click play/pause
- **Refresh stream**: Close and reopen browser
- **Check network**: Verify WiFi connection
- **Check camera**: May be offline or unreachable

### Info Button Not Working
- Browser console shows errors (F12 → Console)
- Try refreshing the page
- Clear browser cache (Cmd+Shift+Delete)

### Can't Copy RTSP URL
- Use alternative method: Click info button, manually select and copy
- Try copying again after a few seconds
- Check browser permissions for clipboard access

## Browser Compatibility

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome | ✅ Full | Best performance |
| Firefox | ✅ Full | Good support |
| Safari | ✅ Full | Native HLS support |
| Edge | ✅ Full | Based on Chromium |
| Mobile browsers | ✅ Full | Responsive layout |

## Customization

The dashboard can be customized by editing `templates/index.html`:

### Change Grid Layout
```css
/* 3×2 grid instead of 2×2 */
.camera-grid {
    grid-template-columns: 1fr 1fr 1fr;
    grid-template-rows: 1fr 1fr;
}
```

### Change Gap Between Videos
```css
/* Larger gap (8px instead of 4px) */
.camera-grid {
    gap: 8px;
}
```

### Change Info Button Color
```css
/* Different color for button */
.info-btn {
    border: 2px solid #ff9500;  /* Orange instead of purple */
    color: #ff9500;
}
```

### Change Background Color
```css
/* Lighter background */
body {
    background: #1a1a1a;  /* Dark gray instead of black */
}
```

## API Reference

The dashboard uses these endpoints:

### GET /api/cameras
Returns JSON array of all cameras:
```json
[
  {
    "ip": "192.168.0.100",
    "port": 8000,
    "rtsp_url": "rtsp://192.168.0.100:5543/live/channel0",
    "profile_name": "PROFILE_1",
    "hls_url": "/hls/stream_0/playlist.m3u8"
  },
  ...
]
```

### GET /hls/stream_N/playlist.m3u8
Returns HLS playlist for camera N (0-3)

## Support

For technical support, see:
- `HLS_STREAMING_SETUP.md` - Technical documentation
- `SYSTEM_READY.md` - System overview
- `QUICK_START_HLS.md` - Quick reference

---

**Dashboard Version**: 2.0 - Minimal UI
**Last Updated**: 2025-11-15
