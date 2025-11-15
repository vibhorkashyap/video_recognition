# 📦 Complete File Inventory

## Project Structure
```
/Users/vibhorkashyap/Documents/code/
│
├── 🐍 Python Scripts
│   ├── find_cameras.py              (320 lines) - Network scanner
│   ├── extract_rtsp_urls.py         (50 lines)  - RTSP extractor
│   ├── camera_server.py             (30 lines)  - Flask API server
│   └── get_rtsp_url.py              (80 lines)  - Single camera URL getter
│
├── 📄 Configuration Files
│   ├── cameras.json                 - Auto-generated camera data
│   └── .venv/                       - Virtual environment
│
├── 🌐 Web Files
│   └── templates/
│       └── index.html               (300 lines) - Dashboard UI
│
├── 📚 Documentation
│   ├── README.md                    - Complete documentation
│   ├── QUICK_START.md               - Quick reference
│   ├── SUMMARY.md                   - System summary
│   └── FILES.md                     - This file
│
└── 🚀 Startup Scripts
    └── startup.sh                   - One-command startup
```

## Detailed File Descriptions

### Python Scripts

#### **find_cameras.py** (320 lines)
**Purpose:** Discover IP cameras on the network

**Key Features:**
- Network scanning with nmap or port probing
- Banner detection for camera identification
- Multi-threaded scanning (20 threads)
- MAC address OUI matching
- Verbose logging support
- Fallback scanning if nmap unavailable

**Configuration:**
- Common ports: 554, 8554, 80, 8080, 8000, 8899, 443, 5543, 1554, 8200, 9999+
- Camera keywords: 100+ detection strings
- Known vendor OUIs: 8 prefixes

**Usage:**
```bash
# Full subnet scan
python find_cameras.py

# Specific IPs
python find_cameras.py 192.168.0.100 192.168.0.102
```

---

#### **extract_rtsp_urls.py** (50 lines)
**Purpose:** Extract RTSP stream URLs from ONVIF cameras

**Process:**
1. Connects to each camera via ONVIF
2. Tries ports: 80, 8000, 8080, 8899, 554
3. Gets media profiles from camera
4. Extracts RTSP URI for each profile
5. Saves to cameras.json

**Default Cameras:**
- 192.168.0.100, 192.168.0.101, 192.168.0.102, 192.168.0.118

**Credentials:**
- Username: admin
- Password: shivasindia

**Usage:**
```bash
python extract_rtsp_urls.py
```

**Output:**
```
✓ Found 4 cameras
Camera data saved to cameras.json
```

---

#### **camera_server.py** (30 lines)
**Purpose:** Flask REST API server for dashboard

**Endpoints:**
- `GET /` → Renders dashboard (index.html)
- `GET /api/cameras` → Returns all cameras (JSON)
- `GET /api/cameras/<id>` → Returns specific camera (JSON)

**Configuration:**
- Host: 0.0.0.0 (all interfaces)
- Port: 8080
- Debug mode: Enabled
- Auto-reload: Enabled

**Usage:**
```bash
python camera_server.py
# Server starts at http://0.0.0.0:8080
```

**API Response Example:**
```json
[
  {
    "ip": "192.168.0.100",
    "port": 8000,
    "rtsp_url": "rtsp://192.168.0.100:5543/live/channel0",
    "profile_name": "PROFILE_1"
  }
]
```

---

#### **get_rtsp_url.py** (80 lines)
**Purpose:** Get RTSP URL for a single camera (original script)

**Features:**
- Automatic ONVIF port detection
- Tries multiple common ports
- Graceful error handling
- Direct camera access

**Usage:**
```bash
# Edit IP address in script
python get_rtsp_url.py
```

---

### Configuration Files

#### **cameras.json** (Generated)
**Purpose:** Camera configuration cache

**Format:**
```json
[
  {
    "ip": "192.168.0.100",
    "port": 8000,
    "rtsp_url": "rtsp://192.168.0.100:5543/live/channel0",
    "profile_name": "PROFILE_1"
  }
]
```

**Generation:**
- Created by extract_rtsp_urls.py
- Updated when cameras are rescanned
- Used by camera_server.py

**4 Cameras Total:**
- 192.168.0.100 (Happytimesoft)
- 192.168.0.101 (Happytimesoft)
- 192.168.0.102 (Happytimesoft)
- 192.168.0.118 (Happytimesoft)

---

### Web Files

#### **templates/index.html** (300 lines)
**Purpose:** Beautiful dashboard for camera monitoring

**Features:**

**Layout:**
- Responsive grid (2x2 on desktop, 1 column on mobile)
- 4 camera cards visible
- Full-screen capable

**Each Camera Card Shows:**
- Camera name (Camera 1-4)
- Status indicator (green pulsing dot)
- IP address
- ONVIF port
- Profile name
- Full RTSP URL
- Two action buttons

**Statistics Dashboard:**
- Number of cameras online
- Active streams count
- Last update timestamp

**Interactive Elements:**
- "📺 Open Stream" button (opens RTSP in VLC)
- "📋 Copy URL" button (copies to clipboard)
- Direct links to RTSP URLs
- Hover animations

**Styling:**
- Dark theme (#0a0e27 background)
- Purple gradient (#667eea to #764ba2)
- Smooth transitions
- Mobile responsive
- Professional UI

**JavaScript:**
- Fetches camera data from API
- Renders grid dynamically
- Updates statistics every 10s
- Reloads data every 30s
- Error handling
- Clipboard integration

---

### Documentation Files

#### **README.md**
Complete project documentation including:
- Feature overview
- Component descriptions
- Installation guide
- Camera configuration
- Usage instructions
- Viewing options (browser, VLC, CLI)
- File structure
- Technology stack
- Troubleshooting
- Future enhancements

#### **QUICK_START.md**
Quick reference guide:
- 3-step startup process
- Feature overview
- Common tasks
- Command examples
- Troubleshooting FAQ
- Quick customization tips

#### **SUMMARY.md**
High-level project summary:
- System architecture
- Files created/modified
- Discovered cameras
- Dashboard features
- Usage options
- API endpoints
- Performance metrics
- Security notes
- Limitations
- Enhancement ideas

---

### Startup Scripts

#### **startup.sh**
**Purpose:** One-command startup script

**Actions:**
1. Verify virtual environment
2. Run extract_rtsp_urls.py
3. Start camera_server.py
4. Display server URL

**Usage:**
```bash
bash startup.sh
# Opens server at http://localhost:8080
```

---

## File Sizes

```
find_cameras.py              ~12 KB
extract_rtsp_urls.py         ~2 KB
camera_server.py             ~1 KB
get_rtsp_url.py              ~3 KB
templates/index.html         ~15 KB
cameras.json                 ~300 B
README.md                    ~8 KB
QUICK_START.md               ~4 KB
SUMMARY.md                   ~10 KB
FILES.md                     ~8 KB
startup.sh                   ~500 B

Total Code                   ~64 KB
```

## Dependencies

**Python Packages:**
- onvif-zeep (0.9.0+) - ONVIF camera protocol
- flask (2.0+) - Web server
- zeep (4.0+) - SOAP/WSDL client
- requests (2.25+) - HTTP library

**System Tools:**
- nmap (optional) - Network scanning
- python3 - Runtime
- bash - Shell scripts

**Tested On:**
- macOS 13+
- Python 3.9+
- Flask 2.0+

## Total Project Stats

```
Total Lines of Code:     ~700+
Python Scripts:          4
Web Files:               1
Configuration Files:    1
Documentation:          4
Startup Scripts:        1
Total Files:            11
Cameras Configured:     4
API Endpoints:          3
Dashboard Features:     10+
```

## How Files Work Together

```
User starts system
        ↓
startup.sh runs
        ↓
extract_rtsp_urls.py executes
        ↓
Connects to 4 cameras via ONVIF
        ↓
Extracts RTSP URLs from each
        ↓
Saves to cameras.json
        ↓
camera_server.py starts
        ↓
Flask serves index.html
        ↓
index.html loads and displays
        ↓
JavaScript fetches /api/cameras
        ↓
camera_server.py returns cameras.json content
        ↓
Dashboard renders 4-camera grid
        ↓
User clicks "Open Stream"
        ↓
RTSP URL from cameras.json opens in VLC
        ↓
Live camera feed appears!
```

## Key Implementation Details

### Network Discovery (find_cameras.py)
- Uses socket.socket() for port scanning
- Threading.Queue for multi-threaded scanning
- subprocess.Popen() for nmap/ping/arp commands
- Regex pattern matching for IP/MAC extraction

### RTSP Extraction (extract_rtsp_urls.py)
- ONVIFCamera client connection
- GetProfiles() ONVIF method
- GetStreamUri() for RTSP URL retrieval
- Port-cycling for ONVIF discovery

### Web Backend (camera_server.py)
- Flask.Flask() application
- @app.route decorators for endpoints
- JSON response formatting
- Static file serving

### Dashboard Frontend (index.html)
- Fetch API for async requests
- CSS Grid for responsive layout
- Event listeners for interactions
- LocalStorage for client-side data (can be added)

## Customization Points

**Add More Cameras:**
Edit `extract_rtsp_urls.py` line 12:
```python
CAMERAS = [
    {"ip": "192.168.0.100", "username": "admin", "password": "shivasindia"},
    {"ip": "NEW.IP.HERE", "username": "admin", "password": "password"},
]
```

**Change Server Port:**
Edit `camera_server.py` line 26:
```python
app.run(debug=True, host='0.0.0.0', port=9000)
```

**Update Camera Credentials:**
Edit `extract_rtsp_urls.py` CAMERAS list

**Modify Dashboard Layout:**
Edit `templates/index.html` CSS Grid styles

**Add More Camera Keywords:**
Edit `find_cameras.py` CAM_KEYWORDS list

---

## Next Files to Create (Optional)

- `docker/Dockerfile` - Containerization
- `config.yaml` - Configuration file
- `requirements.txt` - Python dependencies
- `tests/` - Unit tests
- `static/` - CSS/JS assets
- `migrate_db.py` - Database setup
- `gunicorn_config.py` - Production server

---

This completes the project! All files are in place and working together to provide a complete camera monitoring system. 🎉
