
from onvif import ONVIFCamera

# Replace with your camera's details
CAMERA_IP = '192.168.0.101'
USERNAME = 'admin'  # Change if needed
PASSWORD = 'shivasindia'  # Change if needed

COMMON_PORTS = [80, 8000, 8080, 8899, 554]
success = False

for PORT in COMMON_PORTS:
	try:
		print(f"Trying ONVIF port {PORT}...")
		camera = ONVIFCamera(CAMERA_IP, PORT, USERNAME, PASSWORD)
		media_service = camera.create_media_service()
		profiles = media_service.GetProfiles()
		profile = profiles[0]
		stream_uri = media_service.GetStreamUri({
			'StreamSetup': {
				'Stream': 'RTP-Unicast',
				'Transport': {'Protocol': 'RTSP'}
			},
			'ProfileToken': profile.token
		})
		print(f"Success! ONVIF port: {PORT}")
		print('RTSP Stream URL:', stream_uri.Uri)
		success = True
		break
	except Exception as e:
		print(f"Port {PORT} failed: {e}")

if not success:
	print("Could not connect to the camera on any common ONVIF port.")
