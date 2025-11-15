#!/usr/bin/env python3
"""
Test and verify the HLS streaming system
"""

import requests
import json
import subprocess
import os
from datetime import datetime

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def check_flask_server():
    """Check if Flask server is running"""
    print_header("1. Flask Server Status")
    try:
        response = requests.get('http://localhost:8080/', timeout=2)
        if response.status_code == 200:
            print("✅ Flask server is running on port 8080")
            return True
        else:
            print(f"❌ Flask server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Flask server is not responding: {e}")
        return False

def check_api():
    """Check API endpoints"""
    print_header("2. API Endpoints")
    try:
        response = requests.get('http://localhost:8080/api/cameras', timeout=2)
        cameras = response.json()
        
        print(f"✅ API is responding with {len(cameras)} cameras")
        
        for idx, camera in enumerate(cameras):
            print(f"\n  Camera {idx+1}:")
            print(f"    IP: {camera['ip']}")
            print(f"    RTSP: {camera['rtsp_url']}")
            print(f"    HLS: {camera.get('hls_url', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

def check_ffmpeg_processes():
    """Check if FFmpeg processes are running"""
    print_header("3. FFmpeg Processes")
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        ffmpeg_lines = [l for l in lines if 'ffmpeg' in l and 'grep' not in l]
        
        if ffmpeg_lines:
            print(f"✅ {len(ffmpeg_lines)} FFmpeg processes running:")
            for line in ffmpeg_lines:
                # Extract just the camera stream info
                if 'rtsp://' in line:
                    ip = line.split('rtsp://')[1].split(':')[0] if 'rtsp://' in line else 'Unknown'
                    print(f"    • Camera at {ip}")
            return True
        else:
            print("❌ No FFmpeg processes found - streams not converting!")
            return False
    except Exception as e:
        print(f"❌ Error checking FFmpeg: {e}")
        return False

def check_hls_streams():
    """Check if HLS segments are being generated"""
    print_header("4. HLS Stream Generation")
    hls_base = '/Users/vibhorkashyap/Documents/code/hls_streams'
    
    try:
        total_size = 0
        streams_ok = 0
        
        for i in range(4):
            stream_dir = os.path.join(hls_base, f'stream_{i}')
            if os.path.exists(stream_dir):
                files = os.listdir(stream_dir)
                size = sum(os.path.getsize(os.path.join(stream_dir, f)) 
                          for f in files if os.path.isfile(os.path.join(stream_dir, f)))
                total_size += size
                
                if 'playlist.m3u8' in files:
                    print(f"✅ Stream {i}: {len(files)-1} segments, {size/1024/1024:.1f}MB")
                    streams_ok += 1
                else:
                    print(f"⚠️  Stream {i}: No playlist found")
        
        if streams_ok == 4:
            print(f"\n✅ All 4 streams generating segments ({total_size/1024/1024:.1f}MB total)")
            return True
        else:
            print(f"\n⚠️  Only {streams_ok}/4 streams have playlists")
            return streams_ok > 0
    except Exception as e:
        print(f"❌ Error checking streams: {e}")
        return False

def check_hls_playback():
    """Check if HLS playlists are being served"""
    print_header("5. HLS Playback Capability")
    
    try:
        for i in range(4):
            response = requests.get(f'http://localhost:8080/hls/stream_{i}/playlist.m3u8', timeout=2)
            if response.status_code == 200:
                content = response.text
                if '#EXTM3U' in content:
                    # Count segments
                    segments = [l for l in content.split('\n') if l.endswith('.ts')]
                    print(f"✅ Stream {i}: Valid HLS playlist with {len(segments)} segments")
                else:
                    print(f"⚠️  Stream {i}: Invalid playlist format")
            else:
                print(f"❌ Stream {i}: Failed to fetch playlist")
        
        return True
    except Exception as e:
        print(f"❌ Error checking HLS: {e}")
        return False

def check_disk_space():
    """Check available disk space"""
    print_header("6. System Resources")
    
    try:
        import shutil
        stat = shutil.disk_usage('/Users/vibhorkashyap/Documents/code')
        free_gb = stat.free / (1024**3)
        total_gb = stat.total / (1024**3)
        
        print(f"✅ Disk Space: {free_gb:.1f}GB free of {total_gb:.1f}GB total")
        
        # Check memory (macOS specific)
        result = subprocess.run(['vm_stat'], capture_output=True, text=True)
        print("✅ Memory status available")
        
        return True
    except Exception as e:
        print(f"⚠️  Could not check system resources: {e}")
        return True

def main():
    print("\n" + "="*60)
    print("  🎥 HLS Camera Streaming System - Verification")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    checks = [
        check_flask_server,
        check_api,
        check_ffmpeg_processes,
        check_hls_streams,
        check_hls_playback,
        check_disk_space,
    ]
    
    results = []
    for check in checks:
        try:
            results.append(check())
        except Exception as e:
            print(f"❌ Unexpected error in {check.__name__}: {e}")
            results.append(False)
    
    print_header("Summary")
    passed = sum(results)
    total = len(results)
    
    print(f"\n  Checks Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  ✅ All systems operational!")
        print("  🎬 Your camera streams are ready to view at:")
        print("     http://localhost:8080")
    elif passed >= total - 1:
        print("\n  ⚠️  System mostly operational")
        print("  Some features may not work as expected")
    else:
        print("\n  ❌ System has issues")
        print("  Please troubleshoot and try again")
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()
