"""
Persistent Chrome Service Daemon
Keeps Chrome running with remote debugging port 9222 and user profile.
"""

import subprocess
import time
import sys

cmd = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "--remote-debugging-port=9222",
    "--remote-allow-origins=*",
    r"--user-data-dir=C:\Users\Jawad Ahmad\AppData\Local\Google\Chrome\AutomationData",
    "https://flow.google.com/u/0/project/8a28cfa5-fddf-4528-b188-6deb5ce5e0e5"
]

print("Starting persistent Chrome instance on port 9222...")
p = subprocess.Popen(cmd)
print(f"Chrome running with PID: {p.pid}")
sys.stdout.flush()

try:
    while True:
        time.sleep(1)
        ret = p.poll()
        if ret is not None:
            print(f"Chrome process ended with code: {ret}")
            sys.stdout.flush()
            break
except KeyboardInterrupt:
    print("Stopping Chrome...")
    p.terminate()
