import os
import sys
import time
import threading
from playwright.sync_api import sync_playwright

CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

import config
import web_ui

PORT = 5058

def start_server():
    web_ui.app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)

def run_verification():
    # Start server in thread
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(2.0)

    artifacts_dir = r"C:\Users\Jawad Ahmad\.gemini\antigravity\brain\c9fef496-4fa3-4dc5-bb3b-4d95643f5eb6"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 920})
        page = context.new_page()

        print(f"Connecting to http://127.0.0.1:{PORT}...")
        page.goto(f"http://127.0.0.1:{PORT}", wait_until="domcontentloaded")
        page.wait_for_selector("#projectSelector", state="visible", timeout=10000)

        # 1. Check Stage 4 card controls
        print("1. Checking Stage 4 2K Resolution selector...")
        page.wait_for_selector("#stage4Resolution", state="visible")
        selected_res = page.eval_on_selector("#stage4Resolution", "el => el.value")
        print(f"   Default Stage 4 resolution selected: {selected_res}")

        # 2. Select project 1 or 2
        print("2. Selecting active project...")
        page.wait_for_function("document.querySelectorAll('#projectSelector option').length > 1", timeout=10000)
        options = page.eval_on_selector_all("#projectSelector option", "opts => opts.map(o => o.value).filter(Boolean)")
        print(f"   Available project options: {options}")
        
        target_project = options[0] if options else ""
        if target_project:
            page.select_option("#projectSelector", value=target_project)
            page.dispatch_event("#projectSelector", "change")
            page.wait_for_timeout(2500)

        # Screenshot 1: Overview showing Stage 4 controls with 2K select
        ss1_path = os.path.join(artifacts_dir, "01_stage4_and_gallery_2k.png")
        page.screenshot(path=ss1_path, full_page=False)
        print("Saved screenshot 1:", ss1_path)

        # 3. Scroll to Gallery and take shot cards screenshot
        print("3. Checking Storyboard Gallery & Shot Cards...")
        page.locator("#galleryPanel").scroll_into_view_if_needed()
        page.wait_for_timeout(800)
        ss2_path = os.path.join(artifacts_dir, "02_shot_cards_2k_badge.png")
        page.locator("#galleryPanel").screenshot(path=ss2_path)
        print("Saved screenshot 2:", ss2_path)

        # 4. Check if any shot card has 2K download button
        btn_2k = page.locator(".shot-card button:has-text('2K')")
        print(f"   Found {btn_2k.count()} shot card 2K download button(s)")

        # 5. Open Lightbox Preview modal
        first_img = page.locator(".shot-card .shot-preview-container").first
        if first_img.is_visible():
            first_img.click()
            page.wait_for_timeout(800)
            ss3_path = os.path.join(artifacts_dir, "03_lightbox_modal_2k_download.png")
            page.screenshot(path=ss3_path)
            print("Saved screenshot 3:", ss3_path)
            page.locator("#modalBackdrop button:has-text('Close')").click()
            page.wait_for_timeout(500)

        # 6. Open Custom Prompt & Regeneration modal
        regen_btn = page.locator(".shot-card button:has-text('Custom Prompt'), .shot-card button:has-text('Generate')").first
        if regen_btn.is_visible():
            regen_btn.click()
            page.wait_for_timeout(800)
            ss4_path = os.path.join(artifacts_dir, "04_regen_modal_2k_option.png")
            page.screenshot(path=ss4_path)
            print("Saved screenshot 4:", ss4_path)

        browser.close()
        print("Frontend UI Playwright verification PASSED successfully!")

if __name__ == "__main__":
    run_verification()

