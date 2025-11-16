# Frame Snapshots Feature - Quick Start Guide

## 🚀 Quick Test (2 minutes)

### 1️⃣ Hard Refresh Browser
```
http://localhost:3000
Press: Ctrl+Shift+R  (or Cmd+Shift+R on Mac)
```

### 2️⃣ Click Search Button
```
In Sidebar:
  ▪ Time filters already set (last 1 hour)
  ▪ Click "● Search" button
  ▪ Wait for results to load
```

### 3️⃣ Click Any Result
```
In "🔍 SEARCH RESULTS":
  ▪ Click any item in the list
  ▪ Modal pops up with "📊 Event Details"
```

### 4️⃣ Scroll Down in Modal
```
You'll see:

🖼️ Frame Snapshots (58 total frames, 10 sampled)
┌─────────────────────────────────────────┐
│ [Frame] [Frame] [Frame] [Frame] [Frame]  │
│ [Frame] [Frame] [Frame] [Frame] [Frame]  │
└─────────────────────────────────────────┘

📌 Frames analyzed: 58
   • Sampled: 10
```

---

## 📊 What Changed

### ❌ Before (Old Data)
```
📌 Frames analyzed: 1
   (No frame snapshots)
   (No visual representation)
```

### ✅ After (New Feature)
```
🖼️ Frame Snapshots (45 total frames, 8 sampled)
┌──────────────────────────────────────┐
│ Frame thumbnails in grid format      │
│ (Blue-themed, 120px per frame)       │
└──────────────────────────────────────┘

📌 Frames analyzed: 45
   • Sampled: 8
```

---

## 📍 Frame Grid Locations

### In Modal (Detailed View)
```
Event Details Modal
├─ Meta Info (Camera, Time, etc.)
├─ Summary Text
├─ 🖼️ Frame Snapshots  ← NEW
│  └─ Grid: 120px thumbnails
│     ~4-5 frames per row
├─ 📹 Video Clips
└─ Frame count footer
```

### In Chat Message (Compact View)
```
Chat Bubble
├─ Summary Meta
├─ Summary Text
├─ 🖼️ Frames  ← NEW
│  └─ Grid: 80px thumbnails
│     ~7-10 frames per row
├─ 📹 Video Clips
└─ Frame count
```

---

## 🎨 Visual Styling

### Frame Snapshots Colors
```
🟦 Blue Theme (#60a5fa)
├─ Label: Light blue
├─ Border: Blue with transparency
├─ Hover: Brighter blue + scale effect
└─ Background: Dark with blue tint
```

### Frame Content
```
Each frame shows:
├─ Different visuals (temporal variation)
├─ Frame number label (Frame 0, Frame 5, etc.)
├─ Timestamp simulation (Test Data)
└─ Colored shapes (representing scene objects)
```

---

## 📋 Test Data Details

### 4 Test Summaries Generated

**1️⃣ Pedestrian Walking**
- Camera: 0
- Total frames: 45
- Sampled frames: 8
- Description: Man in blue shirt walking

**2️⃣ Delivery Truck**
- Camera: 0
- Total frames: 52
- Sampled frames: 9
- Description: Delivery truck and person

**3️⃣ Cyclists**
- Camera: 0
- Total frames: 58
- Sampled frames: 10
- Description: Two cyclists riding

**4️⃣ Family Group**
- Camera: 1
- Total frames: 48
- Sampled frames: 8
- Description: Family walking

---

## 🔍 Data Location

```
/ollama_video_summaries/
├── camera_0/
│   ├── frames/
│   │   ├── *_frame_0_0.jpg
│   │   ├── *_frame_1_5.jpg
│   │   ├── *_frame_2_10.jpg
│   │   └── ... (more frames)
│   └── 5_minutes_20251116_173508.json
└── camera_1/
    ├── frames/
    └── 5_minutes_20251116_173508.json
```

---

## ✅ Testing Checklist

### Visual Elements
- [ ] Frame grid appears in modal
- [ ] Frame grid appears in chat
- [ ] Frame images are visible (not broken)
- [ ] Frames show different content
- [ ] Blue styling applied correctly

### Data Accuracy
- [ ] Frame count: NOT "1" anymore (shows 45, 52, 58, 48)
- [ ] Sampled count: Shows 8, 9, 10, 8 (not 1)
- [ ] Frame labels: Show different numbers (0, 5, 10, 15...)
- [ ] Multiple results: All 4 summaries visible

### Interactivity
- [ ] Hover on frame: Scale effect + glow
- [ ] Click modal close: Modal disappears
- [ ] Scroll modal: Can see all frames
- [ ] Responsive: Works on different screen sizes

### No Errors
- [ ] Browser console: No red errors
- [ ] Network tab: All images load (200 status)
- [ ] App doesn't freeze

---

## 🎯 Success Looks Like

### Example Modal
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 📊 Event Details                        ✕ ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ 🎥 Camera   0   │ ⏱️ 5 MINUTES           ┃
┃ 🕐 Time     16/11/2025, 17:35:08        ┃
┃                                          ┃
┃ Summary                                 ┃
┃ During this 5-minute period, two        ┃
┃ cyclists rode past the camera...        ┃
┃                                          ┃
┃ 🖼️ Frame Snapshots (58 total, 10 sampled)
┃ ┌────────────────────────────────────┐ ┃
┃ │ [Img] [Img] [Img] [Img] [Img]      │ ┃
┃ │ [Img] [Img] [Img] [Img] [Img]      │ ┃
┃ └────────────────────────────────────┘ ┃
┃                                          ┃
┃ 📹 Related Video Clips                  ┃
┃ (if available)                          ┃
┃                                          ┃
┃ 📌 Frames analyzed: 58 • Sampled: 10    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 🚨 If Something's Wrong

### Check 1: Frame Files Exist
```bash
ls /ollama_video_summaries/camera_0/frames/ | wc -l
# Should show ~40+ files
```

### Check 2: API Endpoint Works
```bash
curl http://localhost:8080/api/frame/0/5_minutes/20251116_173508/frame_0_0.jpg -v
# Should return 200 with image data
```

### Check 3: JSON Has Frame Data
```bash
cat /ollama_video_summaries/camera_0/5_minutes*.json | grep frame_snapshots
# Should show array with 8-10 items
```

### Check 4: Frontend Fetches Data
```javascript
// Open DevTools Console (F12)
// Go to Network tab
// Perform search
// Look for: /api/chat requests
// Response should have frame_snapshots array
```

---

## 📚 Related Documentation

- `FRAME_SNAPSHOTS_UPDATE.md` - Technical details
- `TESTING_FRAME_SNAPSHOTS.md` - Detailed testing guide
- `test_frame_generator.py` - Test data generator script

---

**Status:** ✅ Ready to Test
**Test Data:** Generated 2025-11-16 17:35:08
**Version:** Frame Snapshots v1.0

🎉 Enjoy the new visual frame context feature!
