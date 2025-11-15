import socket
import subprocess
import sys
import platform
import ipaddress
import threading
import queue
import re
import time

#!/usr/bin/env python3
"""
find_cameras.py
- Finds the router IP (default gateway)
- Scans the local /24 network for devices
- Tries to detect IP cameras via RTSP/HTTP banners and common ports
Usage: python3 find_cameras.py
Note: running this may require privileges for some operations and will perform network probes.
"""


# quick vendor keywords and common camera-related banner strings
CAM_KEYWORDS = [
    "hikvision", "dahua", "axis", "reolink", "foscam", "goahead", "netwave",
    "webcam", "ipcamera", "camera", "rtsp", "video", "dvr", "nvr", "sercomm",
    "xmhd", "avtech", "samsung", "sony", "hikvision-webs", "gwell", "cp-vision",
    "cp-plus", "cpplus", "gvminirtsp", "onvif", "soap", "http/1", "200 ok",
    "401", "digest", "happytimesoft", "ireader", "h264", "pcm", "rtsp/1.0",
]

# Extended port list including alternate RTSP and HTTP ports
COMMON_PORTS = [554, 8554, 80, 8080, 8000, 8899, 443, 5543, 1554, 8200, 9999, 9998, 9997, 9996]

# basic OUI hints for some camera vendors (not exhaustive)
OUI_HINTS = {
    "00:1A:6E": "Axis Communications",
    "00:1E:C9": "Hikvision",
    "00:1B:2F": "Dahua",
    "00:18:DE": "Foscam",
    "00:23:AB": "Reolink",
    "00:12:FE": "CP Plus",
    "00:0C:29": "VMware",  # sometimes used in lab/VMs
    "28:18:fd": "Happytimesoft",  # Camera vendor prefix
}


def get_local_ip():
    # best-effort method to get local IP without external packages
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_default_gateway():
    # Try `netstat -nr | grep default` (macOS/BSD)
    try:
        out = subprocess.check_output(["netstat", "-nr"], stderr=subprocess.DEVNULL, text=True)
        for line in out.splitlines():
            if "default" in line:
                parts = line.split()
                if len(parts) > 1:
                    # typically: "default <IP> ..." 
                    m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                    if m:
                        return m.group(1)
    except Exception:
        pass
    # Try `ip route` (Linux)
    try:
        out = subprocess.check_output(["ip", "route"], stderr=subprocess.DEVNULL, text=True)
        m = re.search(r"default via (\d+\.\d+\.\d+\.\d+)", out)
        if m:
            return m.group(1)
    except Exception:
        pass
    try:
        out = subprocess.check_output(["route", "-n"], stderr=subprocess.DEVNULL, text=True)
        m = re.search(r"^0\.0\.0\.0\s+(\d+\.\d+\.\d+\.\d+)", out, flags=re.M)
        if m:
            return m.group(1)
    except Exception:
        pass
    if platform.system().lower().startswith("win"):
        try:
            out = subprocess.check_output(["route", "PRINT"], stderr=subprocess.DEVNULL, text=True)
            m = re.search(r"0\.0\.0\.0\s+0\.0\.0\.0\s+(\d+\.\d+\.\d+\.\d+)", out)
            if m:
                return m.group(1)
        except Exception:
            pass
    # fallback: assume gateway is .1 of local subnet
    lip = get_local_ip()
    parts = lip.split(".")
    if len(parts) == 4:
        parts[-1] = "1"
        return ".".join(parts)
    return None


def icmp_ping(ip, count=1, timeout=1000):
    # cross-platform ping to populate ARP cache; timeout in ms for windows, seconds for unix
    plat = platform.system().lower()
    if plat == "windows":
        cmd = ["ping", "-n", str(count), "-w", str(timeout), ip]
    else:
        # -c count, -W timeout (seconds)
        cmd = ["ping", "-c", str(count), "-W", str(max(1, int(timeout / 1000))), ip]
    try:
        subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def get_mac_from_arp(ip):
    # try common arp/ip neigh commands and regex for mac
    plat = platform.system().lower()
    patterns = [
        r"([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})",
    ]
    # try "arp -n IP"
    try:
        out = subprocess.check_output(["arp", "-n", ip], stderr=subprocess.DEVNULL, text=True)
        for p in patterns:
            m = re.search(p, out)
            if m:
                return m.group(0).lower()
    except Exception:
        pass
    # try "ip neigh show IP"
    try:
        out = subprocess.check_output(["ip", "neigh", "show", ip], stderr=subprocess.DEVNULL, text=True)
        for p in patterns:
            m = re.search(p, out)
            if m:
                return m.group(0).lower()
    except Exception:
        pass
    # Windows: "arp -a IP"
    try:
        out = subprocess.check_output(["arp", "-a"], stderr=subprocess.DEVNULL, text=True)
        # find line containing IP
        for line in out.splitlines():
            if ip in line:
                m = re.search(patterns[0], line)
                if m:
                    return m.group(0).lower()
    except Exception:
        pass
    return None


def banner_probe(ip, port, timeout=1.5, verbose=False):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, port))
        entry_found = True  # Connection successful = port is open
        
        # send appropriate probe depending on port
        if port in (80, 8080, 8000, 443):
            try:
                req = b"GET / HTTP/1.0\r\nHost: %b\r\n\r\n" % ip.encode()
                s.sendall(req)
            except Exception:
                pass
        elif port in (554, 8554, 5543, 1554):
            try:
                # simple RTSP OPTIONS probe
                req = b"OPTIONS rtsp://%b/ RTSP/1.0\r\nCSeq: 1\r\n\r\n" % ip.encode()
                s.sendall(req)
            except Exception:
                pass
        
        # try to read banner
        data = b""
        try:
            data = s.recv(2048)
        except socket.timeout:
            # Timeout on recv but port is open, return empty string (port open but no banner)
            pass
        except Exception:
            pass
        
        s.close()
        
        try:
            banner = data.decode(errors="ignore")
            if verbose and banner:
                print(f"    Port {port}: Got response ({len(banner)} bytes)")
            return banner if banner else ""  # Return empty string for open ports with no banner
        except Exception:
            return ""
    except socket.timeout:
        try:
            s.close()
        except Exception:
            pass
        return None  # Timeout = port closed/filtered
    except Exception as e:
        try:
            s.close()
        except Exception:
            pass
        if verbose:
            pass  # suppress verbose output for connection failures
        return None


def looks_like_camera(banner, mac):
    if not banner and not mac:
        return False, []
    hints = []
    if banner:
        b = banner.lower()
        for k in CAM_KEYWORDS:
            if k in b:
                hints.append("banner:" + k)
    if mac:
        oui = mac.upper()[0:8]
        for prefix, vendor in OUI_HINTS.items():
            if oui.startswith(prefix):
                hints.append("oui:" + vendor)
    return (len(hints) > 0), hints


def nmap_scan(network):
    """
    Run nmap -sn (ping scan) over a network to find live hosts.
    Returns a list of active IP addresses.
    """
    try:
        print(f"Running nmap -sn {network}...")
        out = subprocess.check_output(["nmap", "-sn", network], stderr=subprocess.DEVNULL, text=True)
        ips = re.findall(r"(\d+\.\d+\.\d+\.\d+)", out)
        # nmap reports both network and hosts, filter unique
        return sorted(set(ips))
    except FileNotFoundError:
        print("nmap not found. Falling back to local scanning.")
        return None
    except Exception as e:
        print(f"nmap error: {e}")
        return None


def scan_worker(q, results, verbose=False):
    while True:
        try:
            ip = q.get_nowait()
        except queue.Empty:
            return
        
        if verbose:
            print(f"Probing {ip}...")
        
        entry = {"ip": ip, "open_ports": [], "banners": {}, "mac": None, "hints": [], "is_alive": False}
        
        # First, check if IP is alive via ICMP ping
        icmp_ping(ip, count=1, timeout=500)
        
        # try common ports
        for p in COMMON_PORTS:
            b = banner_probe(ip, p, timeout=1.2, verbose=verbose)
            if b is None:
                continue
            entry["open_ports"].append(p)
            entry["is_alive"] = True
            if b:
                entry["banners"][str(p)] = b.strip()[:800]
        
        # get MAC (ping first to populate ARP)
        mac = get_mac_from_arp(ip)
        if mac:
            entry["mac"] = mac
            entry["is_alive"] = True
        
        is_cam, hints = looks_like_camera(" ".join(entry["banners"].values()), mac)
        entry["hints"] = hints
        
        # Report devices that:
        # 1. Have camera hints
        # 2. Have open RTSP/video ports (554, 8554, 5543, etc.)
        # 3. Are alive and have open ports
        # 4. Have camera vendor MAC OUI
        has_camera_hints = is_cam
        has_video_ports = any(p in entry["open_ports"] for p in [554, 8554, 5543, 1554, 8200])
        has_mac_hint = any("oui:" in h for h in hints)
        should_report = has_camera_hints or has_video_ports or has_mac_hint or (entry["is_alive"] and len(entry["open_ports"]) > 0)
        
        if should_report:
            if verbose:
                print(f"  -> Found device: ports={entry['open_ports']}, hints={hints}, mac={entry['mac']}")
            results.append(entry)
        
        q.task_done()


def main():
    print("Detecting local IP and default gateway...")
    local_ip = get_local_ip()
    gw = get_default_gateway()
    print("Local IP:", local_ip)
    print("Default gateway:", gw)
    
    # Check for command-line arguments for specific IPs
    if len(sys.argv) > 1:
        ips_to_scan = sys.argv[1:]
        print(f"Scanning specific IPs: {ips_to_scan}")
    else:
        # Determine network
        net_addr = ipaddress.ip_network(local_ip + "/24", strict=False)
        network_str = str(net_addr.with_prefixlen)
        print("Network:", network_str)
        
        # Try nmap first
        nmap_ips = nmap_scan(network_str)
        
        if nmap_ips:
            # Use nmap results
            print(f"Found {len(nmap_ips)} active hosts via nmap")
            ips_to_scan = nmap_ips
        else:
            # Fallback to manual scanning
            print("Using fallback host enumeration...")
            ips_to_scan = [str(host) for host in net_addr.hosts()]
    
    q = queue.Queue()
    for ip in ips_to_scan:
        if ip == local_ip or ip == gw:
            continue
        q.put(ip)
    
    threads = []
    results = []
    n_threads = min(20, max(1, q.qsize()))
    verbose = len(sys.argv) > 1  # Enable verbose if scanning specific IPs
    
    for _ in range(n_threads):
        t = threading.Thread(target=scan_worker, args=(q, results, verbose), daemon=True)
        t.start()
        threads.append(t)
    
    try:
        while any(t.is_alive() for t in threads):
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Interrupted.")
    
    # Print found cameras
    if not results:
        print("No camera-like devices found.")
        return
    print("\nDevices found:")
    for r in results:
        print("-" * 40)
        print("IP:", r["ip"])
        if r["mac"]:
            print("MAC:", r["mac"])
        if r["open_ports"]:
            print("Open ports:", ", ".join(map(str, r["open_ports"])))
        if r["hints"]:
            print("Hints:", ", ".join(r["hints"]))
        for p, b in r["banners"].items():
            snippet = b.replace("\r", " ").replace("\n", " ")[:300]
            print(f"Banner({p}): {snippet}")
    print("-" * 40)


if __name__ == "__main__":
    main()