# Frame Snapshots - Testing Instructions

## ✅ Test Data Generated Successfully

Your app now has test summaries with complete frame snapshots. Here's what to do:

## 🎯 How to Test

### Step 1: Refresh the Browser
```
1. Go to http://localhost:3000
2. Press Ctrl+Shift+R (hard refresh) to clear cache
```

### Step 2: Click Search Button
```
1. In the Sidebar, click the "● Search" button
2. This will load all summaries from the last 1 hour
3. You should see 4 test summaries appear in the list
```

### Step 3: Click on a Result
```
1. Click on any result in the "🔍 SEARCH RESULTS" list
2. A modal will open showing "📊 Event Details"
```

## 🖼️ What You'll See

### In the Modal (Event Details)

You'll see a section like this:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖼️ Frame Snapshots (58 total frames, 10 sampled)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Frame 0]  [Frame 5]  [Frame 10] [Frame 15] [Frame 20]
[Frame 25] [Frame 30] [Frame 35] [Frame 40] [Frame 45]

(Blue-themed grid with 10 thumbnails, 120px each)
```

### Frame Count Display

```
📌 Frames analyzed: 58
   • Sampled: 10
```

**NOT** "Frames analyzed: 1" anymore!

### In the Chat Message

When you ask a question and get results, each summary card will show:

```
📊 Found X Video Summaries

📌 Summary 1:
   🎥 Camera 0 | ⏱️ 5 MINUTES | 🕐 17:35:08
   
   Summary text: "During this 5-minute period, a man in a blue 
   shirt and dark pants walked across..."
   
   🖼️ Frames (58 total):
   [Frame] [Frame] [Frame] [Frame] [Frame] [Frame] [Frame]
   [Frame] [Frame] [Frame]
   
   (Compact blue-themed grid)
   
   📌 Frames analyzed: 58
```

## 📊 Test Data Summary

We generated 4 test summaries with the following data:

| Camera | Interval | Total Frames | Sampled Frames | Description |
|--------|----------|-------------|----------------|-------------|
| 0 | 5-min | 45 | 8 | Man in blue shirt walking |
| 0 | 5-min | 52 | 9 | Delivery truck and person |
| 0 | 5-min | 58 | 10 | Two cyclists riding |
| 1 | 5-min | 48 | 8 | Family group walking |

## 🔍 Verify the Data

### Check Frame Images
```bash
ls -la /Users/vibhorkashyap/Documents/code/ollama_video_summaries/camera_0/frames/
```

You should see ~40 JPG files (8-10 per summary × 4 summaries + old test files)

### Check Summary JSON
```bash
cat /Users/vibhorkashyap/Documents/code/ollama_video_summaries/camera_0/5_minutes_20251116_173508.json
```

Should include:
- `"frames_analyzed": 58`
- `"frames_sampled": 10`
- `"frame_snapshots": [...]` with 10 items

## 🎯 Key Features to Verify

✅ **Frame Count**
- Shows actual total (45, 52, 58, 48)
- Shows actual sampled (8, 9, 10, 8)
- NOT showing "1" anymore

✅ **Frame Snapshots**
- Grid displays in modal (blue theme)
- Grid displays in chat messages (compact blue theme)
- Each frame is a clickable thumbnail
- Hover effects work (scale and glow)

✅ **Frame Labels**
- Shows "Frame 0", "Frame 5", etc. (original frame numbers)
- Different frames for temporal coverage

✅ **Responsive Layout**
- Modal: 4-5 frames per row
- Chat: 7-10 frames per row
- Adapts to screen size

## 📱 Browser Console

If you see any errors:
1. Open DevTools: F12
2. Go to Console tab
3. Look for errors
4. They should be minimal if everything works

## ✅ Success Criteria

You've successfully tested the feature when you see:

- [ ] Frame count shows "45 analyzed" not "1"
- [ ] Frame grid appears in modal
- [ ] Frame grid appears in chat bubbles
- [ ] Frame images are actual images (not broken links)
- [ ] Frames show different content (temporal variation)
- [ ] No console errors
- [ ] Both modal and chat show frames

## 🔧 Troubleshooting

### No frames showing?
- Check: `curl http://localhost:8080/api/frame/0/5_minutes/20251116_173508/frame_0_0.jpg`
- If 404: Frame endpoint not working
- If blank image: Frame saving failed

### Showing old data?
- Hard refresh browser (Ctrl+Shift+R)
- Clear browser cache

### Still seeing "1 frame analyzed"?
- Likely showing old summary from before changes
- Use the newly generated test data
- Make sure you clicked Search button

## 📝 Next Steps (Production)

Once testing is complete:

1. **Connect real cameras** (RTSP feeds)
2. **Frame capture** will automatically start
3. **Real summaries** will be generated with frames
4. **Older data** can be cleared or migrated

The test data can stay or be deleted - it won't interfere with real data.

---

**Test data location:** `/Users/vibhorkashyap/Documents/code/ollama_video_summaries/`

**Generated:** 2025-11-16 17:35:08

Happy testing! 🎉
