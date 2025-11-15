#!/usr/bin/env python3
"""
extract_rtsp_urls.py
Discovers RTSP stream URLs from ONVIF cameras on the network
"""

from onvif import ONVIFCamera
import json
import sys

# Camera credentials and known IPs
CAMERAS = [
    {"ip": "192.168.0.100", "username": "admin", "password": "shivasindia"},
    {"ip": "192.168.0.101", "username": "admin", "password": "shivasindia"},
    {"ip": "192.168.0.102", "username": "admin", "password": "shivasindia"},
    {"ip": "192.168.0.118", "username": "admin", "password": "shivasindia"},
]

COMMON_PORTS = [80, 8000, 8080, 8899, 554]


def get_rtsp_url(ip, username, password, ports=COMMON_PORTS):
    """Try to connect to camera on different ports and get RTSP URL"""
    for port in ports:
        try:
            print(f"  Trying {ip}:{port}...", end=" ", flush=True)
            camera = ONVIFCamera(ip, port, username, password)
            media_service = camera.create_media_service()
            profiles = media_service.GetProfiles()
            
            if not profiles:
                print("No profiles found")
                continue
            
            profile = profiles[0]
            stream_uri = media_service.GetStreamUri({
                'StreamSetup': {
                    'Stream': 'RTP-Unicast',
                    'Transport': {'Protocol': 'RTSP'}
                },
                'ProfileToken': profile.token
            })
            
            rtsp_url = stream_uri.Uri
            print(f"✓ Found at port {port}")
            return {
                "ip": ip,
                "port": port,
                "rtsp_url": rtsp_url,
                "profile_name": profile.Name if hasattr(profile, 'Name') else "Main"
            }
        except Exception as e:
            print(f"✗")
            continue
    
    return None


def main():
    print("Extracting RTSP URLs from cameras...\n")
    
    camera_data = []
    
    for cam in CAMERAS:
        print(f"Scanning {cam['ip']}...")
        result = get_rtsp_url(cam['ip'], cam['username'], cam['password'])
        
        if result:
            camera_data.append(result)
            print(f"  RTSP URL: {result['rtsp_url']}\n")
        else:
            print(f"  Failed to get RTSP URL\n")
    
    if camera_data:
        # Save to JSON file
        with open('/Users/vibhorkashyap/Documents/code/cameras.json', 'w') as f:
            json.dump(camera_data, f, indent=2)
        
        print(f"\n✓ Found {len(camera_data)} cameras")
        print("Camera data saved to cameras.json")
        return camera_data
    else:
        print("\n✗ No cameras found")
        return []


if __name__ == "__main__":
    main()
