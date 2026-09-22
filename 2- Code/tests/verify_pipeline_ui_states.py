import os
import sys
import time
import requests
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\Jawad Ahmad\.gemini\antigravity\brain\c9fef496-4fa3-4dc5-bb3b-4d95643f5eb6"
BASE_URL = "http://127.0.0.1:5000"

def set_server_state(payload):
    try:
        r = requests.post(f"{BASE_URL}/api/test/set-state", json=payload, timeout=3)
        return r.json()
    except Exception as e:
        print(f"Error setting server state: {e}")
        return {}

def run_verification():
    print(f"Starting Playwright UI verification against {BASE_URL}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 960})
        page = context.new_page()

        # 1. Reset state to IDLE first
        set_server_state({
            "state": "IDLE",
            "step1": "WAITING",
            "step2": "WAITING",
            "step3": "WAITING",
            "step4": "WAITING",
            "step6": "WAITING",
            "is_paused": False,
            "task_description": "Clean canvas ready."
        })

        # Load initial page
        page.goto(BASE_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(1000)

        # Select an existing project so all stages populate
        page.select_option("#projectSelector", index=1)
        page.wait_for_timeout(1000)

        # 2. Test IDLE State
        print("Testing IDLE state...")
        assert page.is_visible("#btnStartPipeline"), "Start Pipeline button should be visible"
        assert not page.is_disabled("#btnStartPipeline"), "Start Pipeline should be enabled when idle"
        assert page.is_disabled("#btnPausePipeline"), "Pause should be disabled when idle"
        assert page.is_disabled("#btnResumePipeline"), "Resume should be disabled when idle"

        # 3. Simulate RUNNING State (Stage 2)
        print("Testing RUNNING state (Stage 2)...")
        set_server_state({
            "state": "RUNNING_SCRIPT",
            "step1": "COMPLETED",
            "step2": "RUNNING",
            "task_description": "Compiling Script & Storyboard Prompts (Stage 02)..."
        })
        page.evaluate("() => fetchStatus()")
        page.wait_for_timeout(600)

        page.wait_for_selector(".step-card.active", timeout=5000)
        page.wait_for_selector("#liveExecutionPill.running", timeout=5000)
        
        # Capture Running state screenshot
        running_shot = os.path.join(ARTIFACT_DIR, "01_pipeline_running_state.png")
        page.screenshot(path=running_shot)
        print(f"Captured: {running_shot}")

        # 4. Simulate PAUSED State (Paused after Stage 2)
        print("Testing PAUSED state (Paused at Stage 2)...")
        set_server_state({
            "state": "PAUSED_AFTER_STAGE_2",
            "step2": "COMPLETED",
            "is_paused": True,
            "task_description": "Stage 2 Complete. Paused for review. Click 'Continue' to advance to Stage 3."
        })
        page.evaluate("() => fetchStatus()")
        page.wait_for_timeout(600)

        page.wait_for_selector(".step-card.paused", timeout=5000)
        page.wait_for_selector("#pausedBanner", state="visible", timeout=5000)
        page.wait_for_selector("#btnResumePipeline.is-resume-ready", timeout=5000)

        # Capture Paused state screenshot
        paused_shot = os.path.join(ARTIFACT_DIR, "02_pipeline_paused_state.png")
        page.screenshot(path=paused_shot)
        print(f"Captured: {paused_shot}")

        # 5. Test Button Loading State & Toast Trigger
        print("Testing Button Loading state & Toast...")
        page.evaluate("""() => {
          showToast('Stage 2 compiled successfully! Ready for voiceover generation.', 'success', 6000);
          setButtonLoading('btnRunStage2', true, 'Compiling Prompts...');
        }""")
        page.wait_for_timeout(500)

        loading_shot = os.path.join(ARTIFACT_DIR, "03_button_loading_and_toast.png")
        page.screenshot(path=loading_shot)
        print(f"Captured: {loading_shot}")

        # 6. Test Backend Failure & Diagnostic Banner
        print("Testing Backend Failure State & Diagnostic Banner...")
        set_server_state({
            "state": "ERROR",
            "is_paused": False,
            "task_description": "Failed to connect to Google Flow CDP on port 9222. Connection refused."
        })
        page.evaluate("() => fetchStatus()")
        page.wait_for_timeout(600)

        page.wait_for_selector("#backendFailureBanner", state="visible", timeout=5000)
        page.evaluate("""() => {
          showToast('Pipeline Error: Failed to connect to Google Flow CDP on port 9222. Connection refused.', 'error', 6000);
        }""")
        page.wait_for_timeout(500)

        failure_shot = os.path.join(ARTIFACT_DIR, "04_backend_failure_state.png")
        page.screenshot(path=failure_shot)
        print(f"Captured: {failure_shot}")

        # Reset state back to IDLE
        set_server_state({
            "state": "IDLE",
            "step1": "COMPLETED",
            "step2": "COMPLETED",
            "step3": "COMPLETED",
            "step4": "COMPLETED",
            "step6": "COMPLETED",
            "is_paused": False,
            "task_description": "Clean canvas ready."
        })
        page.wait_for_timeout(1000)

        browser.close()
        print("All UI states verified successfully!")

if __name__ == "__main__":
    run_verification()
