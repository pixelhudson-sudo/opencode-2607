import subprocess
import re

def get_saved_ssids():
    """List all saved WiFi network names from system keychain."""
    cmd = ["security", "list-keychains"]
    # Use the default keychain path
    result = subprocess.run(
        ["security", "find-internet-password", "-l", "AirPort"],
        capture_output=True, text=True
    )
    # Actually, better approach: enumerate via airport pref plist
    result = subprocess.run(
        ["defaults", "read", "/Library/Preferences/SystemConfiguration/com.apple.airport.preferences", "RememberedNetworks"],
        capture_output=True, text=True
    )
    ssids = re.findall(r'SSIDString\s*=\s*"(.+?)"', result.stdout)
    return sorted(set(ssids))

def get_password_for_ssid(ssid):
    """Extract WiFi password from keychain for a given SSID."""
    cmd = ["security", "find-generic-password", "-wa", ssid]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return None

if __name__ == "__main__":
    ssids = get_saved_ssids()
    for ssid in ssids:
        pwd = get_password_for_ssid(ssid)
        if pwd:
            print(f"{ssid:30s} → {pwd}")
        else:
            print(f"{ssid:30s} → (keychain denied or not found)")
