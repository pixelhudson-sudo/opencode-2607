import subprocess
import re
import os

def find_airport():
    paths = [
        "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport",
        "/usr/sbin/airport",
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("airport binary not found")

def scan_wifi(airport):
    result = subprocess.run([airport, "-s"], capture_output=True, text=True)
    return result.stdout

def parse_scan(output):
    lines = output.strip().split("\n")
    if len(lines) < 2:
        return []
    networks = []
    for line in lines[1:]:
        parts = re.split(r"\s{2,}", line)
        if len(parts) >= 4:
            ssid = parts[0]
            bssid = parts[1].strip()
            rssi = parts[2].strip()
            channel = parts[3].strip()
            networks.append({"ssid": ssid, "bssid": bssid, "rssi": rssi, "channel": channel})
    return networks

if __name__ == "__main__":
    ap = find_airport()
    raw = scan_wifi(ap)
    nets = parse_scan(raw)
    for n in sorted(nets, key=lambda x: int(x["rssi"]), reverse=True):
        print(f"{n['ssid']:30s} {n['bssid']:20s} RSSI: {n['rssi']:>4s}  CH: {n['channel']}")
