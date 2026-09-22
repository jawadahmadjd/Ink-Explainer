"""
Frontend Verification with Playwright
Spawns Flask server on port 5055 and runs end-to-end browser UI tests and captures screenshots.
"""

import os
import sys
import time
import threading
from playwright.sync_api import sync_playwright

CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

import web_ui

PORT = 5057

def start_server():
    web_ui.app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)

def run_verification():
    # Start server in daemon thread
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(1.5)

    screenshots_dir = os.path.join(CODE_DIR, "tests", "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        print(f"Connecting to http://127.0.0.1:{PORT}...")
        page.goto(f"http://127.0.0.1:{PORT}", wait_until="domcontentloaded")
        page.wait_for_selector("#tabModeLink", state="visible", timeout=10000)

        # 1. Verify Mode A & Mode B tabs
        print("1. Testing Step 1 Dual Mode Tabs...")
        page.wait_for_selector("#tabModeLink", state="visible")
        page.wait_for_selector("#tabModePrompt", state="visible")
        
        # Click Mode B
        page.click("#tabModePrompt")
        page.wait_for_selector("#panelModePrompt", state="visible")
        page.fill("#manualTitle", "Why Did Ancient Civilizations Disappear?")
        page.fill("#manualPrompt", "Explore climate shifts, agricultural collapse, and early technology.")
        page.screenshot(path=os.path.join(screenshots_dir, "01_mode_b_manual_prompt.png"))
        print("   -> Mode B verified and screenshot saved.")

        # Switch back to Mode A
        page.click("#tabModeLink")
        page.wait_for_selector("#panelModeLink", state="visible")
        print("   -> Mode A toggle verified.")

        # 2. Select project 2 ("2- What Did Ancient Humans Do at Night")
        print("2. Selecting active project...")
        page.wait_for_function("document.querySelectorAll('#projectSelector option').length > 1", timeout=10000)
        page.select_option("#projectSelector", value="2- What Did Ancient Humans Do at Night")
        page.dispatch_event("#projectSelector", "change")
        page.wait_for_timeout(2000)

        # 3. Test Manual Prompts Modal in Stage 02
        print("3. Testing Manual Prompts Modal...")
        page.wait_for_selector("#btnManualPrompts", state="visible")
        page.click("#btnManualPrompts")
        page.wait_for_selector("#manualPromptsModalBackdrop", state="visible")
        page.wait_for_selector("#manualPromptsCardList > div", timeout=5000)
        page.screenshot(path=os.path.join(screenshots_dir, "02_manual_prompts_modal.png"))
        print("   -> Manual Prompts modal verified and screenshot saved.")

        # Switch to Bulk View in modal
        page.click("#tabPromptsBulkView")
        page.wait_for_selector("#panelPromptsBulkView", state="visible")
        page.screenshot(path=os.path.join(screenshots_dir, "03_manual_prompts_bulk_view.png"))
        page.click("#manualPromptsModalBackdrop button:has-text('Cancel')")
        page.wait_for_timeout(500)

        # 4. Test Manual SRT Modal in Stage 03
        print("4. Testing Manual SRT Timestamps Modal...")
        page.wait_for_selector("#btnOpenManualSrtModal", state="visible")
        page.click("#btnOpenManualSrtModal")
        page.wait_for_selector("#manualSrtModalBackdrop", state="visible")
        page.wait_for_selector("#manualSrtDetectedBanner", state="visible", timeout=5000)
        page.screenshot(path=os.path.join(screenshots_dir, "04_manual_srt_modal.png"))
        print("   -> Manual SRT Timestamps modal verified with detected project SRT.")
        page.click("#btnCancelManualSrt")
        page.wait_for_timeout(500)

        # 5. Test Manual VO modal with SRT attachment
        print("5. Testing Manual VO Modal with SRT attachment...")
        page.click("#btnOpenManualVoModal")
        page.wait_for_selector("#manualVoModalBackdrop", state="visible")
        page.wait_for_selector("#manualVoSrtPathInput", state="visible")
        page.screenshot(path=os.path.join(screenshots_dir, "05_manual_vo_modal_with_srt.png"))
        print("   -> Manual VO modal with SRT attachment field verified.")
        page.click("#btnCancelManualVo")

        browser.close()
        print("\nALL FRONTEND VERIFICATIONS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_verification()
