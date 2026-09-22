"""
Ink Explainer Studio - Standalone Desktop Launcher
Wraps Flask Web UI in a native pywebview desktop window.
Falls back to default web browser if pywebview is unavailable.
"""

import os
import sys
import time
import threading
import urllib.request

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

import web_ui

def is_server_running(port: int = 5000) -> bool:
    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{port}/api/status", timeout=1.0)
        return req.status == 200
    except Exception:
        return False

def start_flask_background(port: int = 5000):
    if not is_server_running(port):
        print(f"[DESKTOP APP] Starting detached background Flask server on port {port}...")
        python_exe = sys.executable
        pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")
        if not os.path.exists(pythonw_exe):
            pythonw_exe = "pythonw"

        web_ui_script = os.path.join(CODE_DIR, "web_ui.py")
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        try:
            import subprocess
            subprocess.Popen(
                [pythonw_exe, web_ui_script],
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                close_fds=True,
                cwd=os.path.dirname(CODE_DIR)
            )
        except Exception as ex:
            print(f"[DESKTOP APP] Fallback to in-process thread: {ex}")
            t = threading.Thread(
                target=lambda: web_ui.app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False),
                daemon=True
            )
            t.start()

        for _ in range(30):
            if is_server_running(port):
                break
            time.sleep(0.3)

def main():
    port = int(os.getenv("PORT", 5000))
    start_flask_background(port)
    url = f"http://localhost:{port}"
    print(f"[DESKTOP APP] Opening Ink Explainer Studio at {url}...")
    try:
        import webview
        webview.create_window(
            "Ink Explainer Studio - Autonomous Pipeline",
            url,
            width=1400,
            height=900,
            resizable=True,
            text_select=True
        )
        webview.start()
    except ImportError:
        print("[DESKTOP APP] pywebview not installed. Opening in default web browser...")
        import webbrowser
        webbrowser.open(url)
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            print("\n[DESKTOP APP] Exiting...")

if __name__ == "__main__":
    main()
