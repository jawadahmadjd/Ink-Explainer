import os
import sys
import time
import subprocess
import urllib.request
import json

def is_chrome_cdp_running(port: int = 9222) -> bool:
    """Check if Chrome CDP is active on port 9222."""
    endpoints = [
        f"http://127.0.0.1:{port}/json/version",
        f"http://localhost:{port}/json/version",
        f"http://[::1]:{port}/json/version"
    ]
    for url in endpoints:
        try:
            req = urllib.request.urlopen(url, timeout=1.5)
            if req.status == 200:
                return True
        except Exception:
            continue
    return False

def find_chrome_executable() -> str:
    """Locate Chrome binary on Windows PC."""
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
        "chrome.exe"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return "chrome.exe"

def launch_chrome_flow_cdp():
    """Launch Chrome with CDP remote debugging port 9222 pointing to flow.google.com."""
    if is_chrome_cdp_running(9222):
        print("[CHROME LAUNCHER] Chrome CDP is already active on port 9222. Bringing window to front...")
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
                for c in b.contexts:
                    for pg in c.pages:
                        if "flow.google.com" in pg.url or "labs.google" in pg.url:
                            pg.bring_to_front()
                            return True, "Chrome Flow brought to front!"
            return True, "Chrome CDP is already active on port 9222."
        except Exception:
            return True, "Chrome CDP is already active on port 9222."

    try:
        chrome_bin = find_chrome_executable()
        user_data_dir = os.path.join(os.path.expandvars("%LOCALAPPDATA%"), "InkExplainerStudio", "ChromeProfile")
        os.makedirs(user_data_dir, exist_ok=True)

        print("[CHROME LAUNCHER] Spawning interactive Chrome GUI window (port 9222)...")
        if sys.platform == "win32":
            cmd_str = f'start "" "{chrome_bin}" --remote-debugging-port=9222 "--user-data-dir={user_data_dir}" --new-window --window-size=1400,900 --window-position=100,100 --no-first-run --no-default-browser-check "https://flow.google.com"'
            subprocess.Popen(cmd_str, shell=True)
        else:
            cmd = [
                chrome_bin,
                "--remote-debugging-port=9222",
                f"--user-data-dir={user_data_dir}",
                "--new-window",
                "--window-size=1400,900",
                "--window-position=100,100",
                "--no-first-run",
                "--no-default-browser-check",
                "https://flow.google.com"
            ]
            subprocess.Popen(cmd)

        time.sleep(2.0)
        if is_chrome_cdp_running(9222):
            return True, "Launched interactive Chrome window on port 9222!"
        return True, "Chrome launched! Please check taskbar/screen for Chrome window."
    except Exception as ex:
        print(f"[CHROME LAUNCHER ERROR] {ex}")
        return False, f"Failed to launch Chrome: {ex}"

if __name__ == "__main__":
    ok, msg = launch_chrome_flow_cdp()
    print("Result:", ok, msg)
