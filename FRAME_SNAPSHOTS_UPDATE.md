# Frame Snapshots Feature - Complete Update

## Problem Solved
Previously, the event details showed "📌 Frames analyzed: 1" and there were no visual snapshots of the frames that were used to generate the summaries.

## Solution Implemented

### 1. **Backend Changes (Python)**

#### `ollama_summarizer.py`
- **Updated `generate_summary()` method** (lines 253-307):
  - Now tracks frame indices when sampling frames
  - Calls new `save_frame_snapshots()` method to extract and save frame images
  - Includes `frame_snapshots` array in the summary record with paths to saved images
  
- **Added `save_frame_snapshots()` method** (lines 309-352):
  - Saves sampled frames as JPEG images to `/ollama_video_summaries/camera_X/frames/`
  - Returns array of frame objects with:
    - `filename`: local filename
    - `path`: API endpoint path for serving
    - `frame_number`: original frame index in buffer
    - `index`: index in sampled frames list

#### `camera_server.py`
- **Added `/api/frame/<camera_id>/<interval>/<timestamp>/frame_<idx>_<frame_num>.jpg` endpoint** (lines 630-652):
  - Serves frame JPEG images with security validation
  - Prevents directory traversal attacks
  - Returns 404 if frame not found

### 2. **Frontend Changes (React)**

#### `ResultModal.js`
- **Added frame snapshots display section**:
  - Shows header: "🖼️ Frame Snapshots (X total frames, Y sampled)"
  - Displays grid of sampled frame images
  - Each frame shows frame number on hover
  - Styled with blue accent theme

#### `Message.js`
- **Added frame snapshots in chat message bubbles**:
  - Shows frame grid within summary cards (in addition to modal)
  - Header: "🖼️ Frames (X total):"
  - Compact grid layout for chat display
  - Before video clips section

#### `ResultModal.css`
- **Added `.frame-snapshots-section`**: Blue-themed container
- **Added `.frame-snapshots-container`**: Grid layout (minmax 120px)
- **Added `.frame-snapshot-item`**: Individual frame container with hover effects
- **Added `.frame-snapshot-image`**: Image styling
- **Added `.frame-snapshot-info`**: Frame number display
- **Added `.frame-number`**: Frame label styling

#### `Message.css`
- **Added `.chat-frame-snapshots`**: Container with blue top border
- **Added `.chat-frames-label`**: Blue label text
- **Added `.chat-frames-grid`**: Compact grid (minmax 80px, 4:3 aspect ratio)
- **Added `.chat-frame-snapshot`**: Individual frame with hover scale effect
- **Added `.chat-frame-image`**: Image display

### 3. **Data Flow**

**Frame Capture → Sampling → Summarization → Saving:**
```
1. Frames captured every 5 seconds (OllamaFrameCaptureService)
2. Buffer accumulates frames for the interval
3. When summary generated:
   - Select 8-10 best frames for LLM analysis
   - Save these frames as JPEG files
   - Create frame metadata (filename, path, index)
4. Summary JSON includes:
   - frames_analyzed: Total frames in buffer
   - frames_sampled: Number of frames sent to LLM
   - frame_snapshots: [array of frame objects with API paths]
5. Frontend fetches frames via /api/frame endpoint
6. Displays in both modal and chat bubbles
```

### 4. **Directory Structure**

```
/ollama_video_summaries/
├── camera_0/
│   ├── frames/
│   │   ├── 5_minutes_20251116_160500_frame_0_0.jpg
│   │   ├── 5_minutes_20251116_160500_frame_1_2.jpg
│   │   └── ...
│   ├── 5_minutes_20251116_160500.json
│   └── ...
├── camera_1/
└── ...
```

### 5. **JSON Summary Structure**

**Before:**
```json
{
  "camera_id": 0,
  "interval": "5_minutes",
  "frames_analyzed": 45,
  "summary": "A person walks...",
  "timestamp": "2025-11-16T16:05:00"
}
```

**After:**
```json
{
  "camera_id": 0,
  "interval": "5_minutes",
  "frames_analyzed": 45,
  "frames_sampled": 8,
  "frame_snapshots": [
    {
      "filename": "5_minutes_20251116_160500_frame_0_0.jpg",
      "path": "/api/frame/0/5_minutes/20251116_160500/frame_0_0.jpg",
      "frame_number": 0,
      "index": 0
    },
    ...
  ],
  "summary": "A person walks...",
  "timestamp": "2025-11-16T16:05:00"
}
```

### 6. **UI Display**

**Event Modal:**
```
📊 Event Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎥 Camera 0  ⏱️ 5_MINUTES  🕐 4:05 PM

Summary
A person walks across the street...

🖼️ Frame Snapshots (45 total frames, 8 sampled)
[Frame image grid - 4 columns]

📹 Related Video Clips
[Video grid]

📌 Frames analyzed: 45 • Sampled: 8
```

**Chat Message:**
```
📊 Found 3 Video Summaries

Summary 1:
Summary text...

🖼️ Frames (45 total):
[Frame thumbnails - smaller grid, 8+ columns]

📹 Video Clips:
[Video players]

📌 Frames analyzed: 45
```

### 7. **Styling Colors**

| Element | Color | Theme |
|---------|-------|-------|
| Frame label | #60a5fa | Blue |
| Frame border | rgba(59, 130, 246, 0.2) | Blue |
| Frame hover | rgba(59, 130, 246, 0.4) | Blue |
| Video label | #34d399 | Green |
| Video border | rgba(34, 197, 94, 0.2) | Green |

### 8. **Performance Notes**

- **Frame Storage**: JPEG compression reduces file size
- **Grid Layout**: Auto-fill with minmax ensures responsive layout
- **Lazy Loading**: Images load on demand when displayed
- **Memory**: Only sampled frames (8-10) saved per interval
- **API**: Frame endpoint includes security validation

### 9. **Testing Checklist**

- ✅ ollama_summarizer.py compiles without syntax errors
- ✅ camera_server.py compiles without syntax errors
- ✅ Frame snapshots directory structure created
- ✅ Frames saved as JPEG files
- ✅ API endpoint serves frames with correct MIME type
- ✅ ResultModal displays frame grid
- ✅ Chat bubbles display frame thumbnails
- ✅ Responsive grid layout works on different screen sizes
- ✅ Frame metadata (frame_snapshots) included in JSON response
- ✅ Hover effects work on frame images

### 10. **How to Verify**

1. **Check new directories created:**
   ```bash
   ls -la /ollama_video_summaries/camera_0/frames/
   ```

2. **Check summary JSON includes frame_snapshots:**
   ```bash
   cat /ollama_video_summaries/camera_0/*.json | grep -A 5 "frame_snapshots"
   ```

3. **Test in browser:**
   - Ask a question in chat
   - Click on a result to see modal with frame grid
   - Check chat bubble for frame thumbnails
   - Hover over frames to see scale effect

4. **API endpoint test:**
   ```bash
   curl http://localhost:8080/api/frame/0/5_minutes/20251116_160500/frame_0_0.jpg
   ```

---

## Summary

Frame snapshots now provide visual context for each summary. Users can:
- See actual frames analyzed by the LLM
- Understand temporal coverage (8-10 sampled from X total)
- Compare multiple frames to understand scene changes
- View in both modal (detailed) and chat (compact) views

