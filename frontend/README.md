# React Camera Analysis Chat Frontend

## Setup Instructions

### 1. Install Dependencies
```bash
cd /Users/vibhorkashyap/Documents/code/frontend
npm install
```

### 2. Start the Development Server
```bash
npm start
```

This will:
- Start the React development server on port 3000
- Proxy all API calls to the Flask backend on port 8080
- Open the app in your browser automatically

### 3. Ensure Flask Backend is Running
Make sure your Flask camera_server.py is running on port 8080:
```bash
cd /Users/vibhorkashyap/Documents/code
python3 camera_server.py
```

## Features

✅ **React-based Frontend**
- Component-based architecture for better maintainability
- State management for chat messages and filters
- Real-time updates

✅ **Visible Fetching Loader**
- Green animated spinner that clearly shows while fetching
- Displays "Fetching response from backend..." text
- Auto-hides when response arrives

✅ **Chat Interface**
- ChatGPT-style dark theme
- Message history with animations
- Filter sidebar with camera selection and time range

✅ **Time Management**
- Auto-initializes with IST timezone (Asia/Kolkata)
- FROM time = 1 hour before current time
- TO time = current time
- All times displayed in IST format

## File Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── index.js
│   ├── index.css
│   ├── App.js
│   ├── App.css
│   └── components/
│       ├── ChatWindow.js
│       ├── ChatWindow.css
│       ├── Message.js
│       ├── Message.css
│       ├── FetchingLoader.js
│       ├── FetchingLoader.css
│       ├── ChatInput.js
│       ├── ChatInput.css
│       ├── Sidebar.js
│       └── Sidebar.css
├── package.json
└── .gitignore
```

## Components

### App.js
Main component that manages:
- Message state
- Loading state
- Filter state
- API calls to Flask backend

### ChatWindow.js
Displays:
- Message list
- Fetching loader (when loading)
- Chat input area
- Auto-scroll to latest message

### FetchingLoader.js
Shows animated spinner with "Fetching response from backend..." text
- Only visible when `isLoading` is true
- Disappears when API response arrives

### Message.js
Renders individual messages:
- User messages (green bubble, right-aligned)
- Assistant messages (dark bubble, left-aligned)
- Summary responses with formatted cards

### ChatInput.js
Input area with:
- Textarea for message input
- Send button
- Enter key to send (Shift+Enter for new line)
- Disabled state when loading

### Sidebar.js
Left sidebar with:
- Filter controls (camera, time range)
- Search button
- Recent summaries list

## API Communication

The frontend communicates with Flask backend at:
- Backend: `http://localhost:8080`
- Frontend proxies to: `/chat` endpoint
- All requests use POST with JSON body:
  ```json
  {
    "query": "ask your question",
    "camera_id": null or camera_id,
    "start_time": "2025-11-16T10:31",
    "end_time": "2025-11-16T11:31"
  }
  ```

## Troubleshooting

### Loader not visible
- Clear browser cache (Cmd+Shift+R on Mac)
- Check React Developer Tools to see component state
- Ensure `isLoading` state is being set correctly

### API calls failing
- Verify Flask backend is running on port 8080
- Check CORS headers in Flask app
- Look at browser console for error messages

### Time filters not updating
- Clear browser cache
- Refresh the page to re-initialize time filters with IST timezone
- Check browser timezone settings

## Performance Notes

- React components use efficient rendering with proper dependency arrays
- Message list uses key props for optimal list rendering
- CSS animations use GPU acceleration (transform/opacity)
- Loader visibility is managed through component state, not CSS hacks

## Next Steps

1. Install dependencies: `npm install`
2. Start the app: `npm start`
3. Make sure Flask server is running
4. Open http://localhost:3000 in browser
5. Type "anything about bikes?" and hit enter to test
6. Watch the green fetching loader appear and disappear!
