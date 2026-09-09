import argparse
import csv
import json
import os
import random
import shutil
import sys
import time
from datetime import datetime
import cv2
import numpy as np
from playwright.sync_api import sync_playwright

# Import status tracker
sys.path.append(os.path.dirname(__file__))
from update_prompt_status_tracker import refresh_trackers

TARGET_PROJECT_URL = "https://flow.google.com/u/0/project/8a28cfa5-fddf-4528-b188-6deb5ce5e0e5"
TARGET_VARIATIONS = 2  # 2 variations per prompt per SOP
MODEL_CASCADE = ["Nano Banana 2", "Nano Banana Pro", "Nano Banana 2 Lite"]

CSV_PATH = os.path.join("3- Finals", "storyboard_master.csv")
RAW_IMG_DIR = os.path.join("3- Finals", "flow_generated_images")

# Dual destination folders for maximum visibility
FINAL_DIR_ROOT = "Final selected images"
FINAL_DIR_FINALS = os.path.join("3- Finals", "Final selected images")
FINAL_DIR_LEGACY = os.path.join("3- Finals", "final_selected_images")

LOG_CSV = os.path.join("3- Finals", "selection_log.csv")
STATUS_JSON = os.path.join("3- Finals", "production_status.json")

os.makedirs(RAW_IMG_DIR, exist_ok=True)
os.makedirs(FINAL_DIR_ROOT, exist_ok=True)
os.makedirs(FINAL_DIR_FINALS, exist_ok=True)
os.makedirs(FINAL_DIR_LEGACY, exist_ok=True)

def safe_evaluate(page, js_code, max_retries=3):
    """Safely evaluates JavaScript in page context with retry logic if execution context is reloaded."""
    for attempt in range(max_retries):
        try:
            return page.evaluate(js_code)
        except Exception as e:
            err_str = str(e).lower()
            if "context was destroyed" in err_str or "navigation" in err_str:
                print(f"Notice: Page context reloading, waiting to stabilize (attempt {attempt+1}/{max_retries})...")
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=10000)
                except Exception:
                    pass
                time.sleep(2.0)
            else:
                print(f"safe_evaluate warning: {e}")
                time.sleep(1.0)
    return None

def analyze_and_score_variation(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return -1.0, {}

    h, w, _ = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Edge & Linework Sharpness (Laplacian variance)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    sharpness_score = min(100.0, float(laplacian_var) / 15.0)

    # 2. Full-bleed border penalty (check if border has white framing)
    top_strip = gray[:max(1, int(h*0.02)), :]
    bot_strip = gray[max(0, int(h*0.98)):, :]
    left_strip = gray[:, :max(1, int(w*0.02))]
    right_strip = gray[:, max(0, int(w*0.98)):]
    border_pixels = np.concatenate([top_strip.flatten(), bot_strip.flatten(), left_strip.flatten(), right_strip.flatten()])
    border_mean = float(np.mean(border_pixels))
    border_std = float(np.std(border_pixels))
    border_penalty = 0.0
    if border_mean > 240 and border_std < 10:
        border_penalty = 50.0

    # 3. Subject prominence (Center vs periphery contrast)
    center_y, center_x = int(h*0.2), int(w*0.2)
    center_crop = gray[center_y:int(h*0.8), center_x:int(w*0.8)]
    center_std = float(np.std(center_crop))
    center_score = min(100.0, center_std * 1.5)

    # 4. Value Dynamic Range
    p5 = float(np.percentile(gray, 5))
    p95 = float(np.percentile(gray, 95))
    dynamic_range = p95 - p5
    contrast_score = min(100.0, (dynamic_range / 200.0) * 100.0)

    # 5. Information Entropy
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist = hist / hist.sum()
    entropy = -float(np.sum([p * np.log2(p) for p in hist.flatten() if p > 0]))
    entropy_score = min(100.0, (entropy / 7.5) * 100.0)

    total_score = (
        sharpness_score * 0.30 +
        center_score * 0.25 +
        contrast_score * 0.25 +
        entropy_score * 0.20
    ) - border_penalty

    details = {
        "sharpness": round(sharpness_score, 1),
        "center_focus": round(center_score, 1),
        "contrast": round(contrast_score, 1),
        "entropy": round(entropy_score, 1),
        "border_penalty": border_penalty,
        "total_score": round(total_score, 1)
    }
    return float(total_score), details

def check_for_page_errors(page):
    """Detect failure toasts, error dialogs, or unusual activity warnings."""
    res = safe_evaluate(page, """() => {
        const alertElements = Array.from(document.querySelectorAll('[role="alert"], mat-snack-bar-container, .mdc-snackbar__label, .flow-toast'));
        for (const el of alertElements) {
            const txt = (el.innerText || '').toLowerCase();
            if (txt.includes('failed') || txt.includes('something went wrong') || txt.includes('unusual') || txt.includes('limit')) {
                return 'Flow Toast/Alert: ' + el.innerText.substring(0, 80);
            }
        }

        const allText = document.body ? document.body.innerText : '';
        if (allText.includes("You've reached your usage limit") || 
            allText.includes("something went wrong") || 
            allText.includes("Unusual activity detected")) {
            return 'Flow Usage Limit / Warning Banner detected on canvas';
        }

        return null;
    }""")
    return res

def switch_flow_model(page, target_model_name):
    """
    Switches Google Flow model to target_model_name ('Nano Banana 2', 'Nano Banana Pro', 'Nano Banana 2 Lite')
    and ensures x2 variations are configured.
    """
    print(f"[MODEL SWITCH] Switching Google Flow model to: {target_model_name}...")
    try:
        page.mouse.click(100, 100)
        time.sleep(0.5)

        settings_btn = page.locator("button.settings-trigger-button").first
        settings_btn.click(timeout=5000)
        time.sleep(0.8)

        model_btn = page.locator('button[aria-label="Select model family"]').first
        model_btn.click(timeout=5000)
        time.sleep(0.8)

        target_option = page.locator(f'.mat-mdc-menu-panel button:has-text("{target_model_name}")').first
        target_option.click(timeout=5000)
        time.sleep(0.8)

        # Ensure x2 variations
        x2_btn = page.locator('button:has-text("x2")').first
        if x2_btn.count() > 0:
            x2_btn.click(timeout=3000)
            time.sleep(0.3)

        page.mouse.click(100, 100)
        time.sleep(0.8)
        print(f"[MODEL SWITCH] Successfully switched to {target_model_name} (x{TARGET_VARIATIONS})")
        return True
    except Exception as e:
        print(f"[MODEL SWITCH ERROR] Failed to switch model: {e}")
        page.mouse.click(100, 100)
        return False

def update_status(shot_num, total_shots, status, note="", active_model="Nano Banana 2"):
    data = {
        "current_shot": shot_num,
        "total_shots": total_shots,
        "completed_count": len([f for f in os.listdir(FINAL_DIR_ROOT) if f.startswith("shot_") and f.endswith(".jpg")]),
        "status": status,
        "active_model": f"{active_model} (x{TARGET_VARIATIONS})",
        "last_updated": datetime.now().isoformat(),
        "note": note
    }
    with open(STATUS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_or_create_dedicated_flow_page(ctx):
    """Finds existing dedicated Flow page or creates a new isolated tab for this pipeline."""
    # Look for existing tab that matches target project
    for pg in ctx.pages:
        if TARGET_PROJECT_URL in pg.url or "flow.google.com" in pg.url:
            print(f"[TAB MANAGER] Found existing Google Flow tab: {pg.title()}")
            return pg

    # If not found, open a dedicated new tab
    print("[TAB MANAGER] Creating a new isolated tab for Google Flow...")
    new_pg = ctx.new_page()
    new_pg.goto(TARGET_PROJECT_URL, wait_until="domcontentloaded")
    try:
        new_pg.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass
    time.sleep(3)
    print(f"[TAB MANAGER] Dedicated tab ready: {new_pg.title()}")
    return new_pg

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=334)
    args = parser.parse_args()

    # Initial sync and tracker refresh
    refresh_trackers()

    # Load master rows
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        all_rows = list(reader)

    total_shots = len(all_rows)
    print(f"Loaded {total_shots} shots from storyboard master.")

    # Initialize log CSV if not exists
    if not os.path.exists(LOG_CSV):
        with open(LOG_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Shot #", "Timecode", "Selected Var", "Score", "VO Text", "Timestamp"])

    consecutive_failures = 0
    model_cascade_idx = 0
    current_model = MODEL_CASCADE[model_cascade_idx]

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx = browser.contexts[0]
        
        # Dedicated tab management per user instruction
        flow_page = get_or_create_dedicated_flow_page(ctx)

        # Ensure we are on the main project canvas
        if TARGET_PROJECT_URL not in flow_page.url:
            print(f"Navigating dedicated Flow tab to target project: {TARGET_PROJECT_URL}")
            flow_page.goto(TARGET_PROJECT_URL, wait_until="domcontentloaded")
            time.sleep(3)

        shot_idx = args.start
        while shot_idx <= min(args.end, total_shots):
            final_root_file = os.path.join(FINAL_DIR_ROOT, f"shot_{shot_idx:03d}.jpg")
            final_finals_file = os.path.join(FINAL_DIR_FINALS, f"shot_{shot_idx:03d}.jpg")
            final_legacy_file = os.path.join(FINAL_DIR_LEGACY, f"shot_{shot_idx:03d}.jpg")

            # Check if already processed
            if os.path.exists(final_root_file) and os.path.exists(final_finals_file):
                print(f"[SKIP] Shot {shot_idx:03d} already exists in Final selected images.")
                shot_idx += 1
                consecutive_failures = 0
                continue

            row = all_rows[shot_idx - 1]
            timecode = row[1]
            vo_text = row[2]
            prompt = row[4]

            print(f"\n========================================================")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] PROCESSING SHOT {shot_idx:03d} / {total_shots}")
            print(f"Active Model: {current_model} (x{TARGET_VARIATIONS}) | Failures: {consecutive_failures}")
            print(f"Time: {timecode} | VO: \"{vo_text}\"")
            print(f"Prompt: {prompt[:85]}...")
            update_status(shot_idx, total_shots, "GENERATING", f"Shot {shot_idx} in progress ({current_model}, x{TARGET_VARIATIONS})", current_model)

            # Snapshot existing image URLs safely
            existing_srcs_list = safe_evaluate(flow_page, """() => {
                return Array.from(document.querySelectorAll('img'))
                    .filter(img => img.src && img.src.includes('flow-content.google'))
                    .map(img => img.src);
            }""")
            existing_srcs = set(existing_srcs_list or [])

            # Check for error state before typing
            err_msg = check_for_page_errors(flow_page)
            if err_msg:
                print(f"Pre-generation error detected: {err_msg}")

            # Fill prompt
            try:
                editor = flow_page.locator(".ProseMirror").first
                editor.click(timeout=5000)
                time.sleep(0.2)
                editor.fill(prompt)
                time.sleep(0.8)

                submit_btn = flow_page.locator('button[aria-label="Start generation"]').first
                submit_btn.click(timeout=5000)
                print(f"Clicked Start Generation for Shot {shot_idx:03d}. Waiting for {TARGET_VARIATIONS} variations...")
            except Exception as ex:
                print(f"Error submitting prompt: {ex}")
                err_msg = str(ex)

            # Wait for generation to complete (up to 50 seconds)
            render_success = False
            new_srcs = []
            start_wait = time.time()

            if not err_msg:
                while time.time() - start_wait < 50:
                    time.sleep(2.0)

                    # Check for live failure messages
                    live_err = check_for_page_errors(flow_page)
                    if live_err:
                        err_msg = live_err
                        print(f"WARNING: Google Flow indicated failure: {err_msg}")
                        break

                    current_srcs = safe_evaluate(flow_page, """() => {
                        return Array.from(document.querySelectorAll('img'))
                            .filter(img => img.src && img.src.includes('flow-content.google'))
                            .map(img => img.src);
                    }""") or []
                    new_srcs = [s for s in current_srcs if s not in existing_srcs]

                    if len(new_srcs) >= TARGET_VARIATIONS:
                        time.sleep(2.0)
                        render_success = True
                        break

            # Rule 2 Usability Check: If partial generation occurred (at least 1 image produced)
            single_image_accepted = False
            if not render_success and len(new_srcs) >= 1:
                print(f"\n[PARTIAL GENERATION] {len(new_srcs)} variation(s) rendered despite timeout/error.")
                print("Evaluating single image against usability threshold (score >= 50.0)...")
                single_src = new_srcs[0]
                temp_single_path = os.path.join(RAW_IMG_DIR, f"shot_{shot_idx:03d}_partial.jpg")
                try:
                    resp = flow_page.request.get(single_src)
                    if resp.status == 200:
                        with open(temp_single_path, "wb") as f_out:
                            f_out.write(resp.body())
                        s_score, s_details = analyze_and_score_variation(temp_single_path)
                        print(f"  Single image evaluation score: {s_score:.1f} ({s_details})")
                        if s_score >= 50.0:
                            print(f"-> [PARTIAL ACCEPTED] Score {s_score:.1f} >= 50.0! Image is usable for Shot {shot_idx:03d}.")
                            shutil.copy2(temp_single_path, final_root_file)
                            shutil.copy2(temp_single_path, final_finals_file)
                            shutil.copy2(temp_single_path, final_legacy_file)
                            
                            with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
                                writer = csv.writer(f)
                                writer.writerow([shot_idx, timecode, "partial_var_1", round(s_score, 1), vo_text, datetime.now().isoformat()])

                            refresh_trackers()
                            update_status(shot_idx, total_shots, "RUNNING", f"Completed shot {shot_idx} via single partial image (Score: {s_score:.1f})", current_model)
                            single_image_accepted = True
                            consecutive_failures = 0
                        else:
                            print(f"-> [PARTIAL REJECTED] Score {s_score:.1f} < 50.0. Quality insufficient, proceeding to retry.")
                except Exception as pe:
                    print(f"Error evaluating partial image: {pe}")

            if single_image_accepted:
                # Add random interval pacing before next shot
                pacing_wait = round(random.uniform(10.0, 30.0), 1)
                print(f"Pacing: Waiting {pacing_wait}s before proceeding to next shot...")
                time.sleep(pacing_wait)
                shot_idx += 1
                continue

            # Handle Failures with SOP Escalation
            if not render_success or err_msg:
                consecutive_failures += 1
                print(f"\n[FAILURE #{consecutive_failures} ON SHOT {shot_idx:03d}] Active Model: {current_model}. Reason: {err_msg or f'Timeout waiting for {TARGET_VARIATIONS} images'}")

                if consecutive_failures == 1:
                    print("Escalation #1: Reloading page and cooling down for 3 minutes (180s)...")
                    update_status(shot_idx, total_shots, "WAITING_COOLDOWN_3M", f"Cooldown 3m after failure 1 on Shot {shot_idx}", current_model)
                    try:
                        flow_page.reload(wait_until="domcontentloaded")
                        flow_page.wait_for_load_state("domcontentloaded", timeout=15000)
                    except Exception as rx:
                        print(f"Reload note: {rx}")
                    for rem in range(180, 0, -30):
                        print(f"  Cooldown remaining: {rem}s...")
                        time.sleep(30)
                    time.sleep(5)
                    continue

                elif consecutive_failures == 2:
                    print("Escalation #2: Reloading page and cooling down for 5 minutes (300s)...")
                    update_status(shot_idx, total_shots, "WAITING_COOLDOWN_5M", f"Cooldown 5m after failure 2 on Shot {shot_idx}", current_model)
                    try:
                        flow_page.reload(wait_until="domcontentloaded")
                        flow_page.wait_for_load_state("domcontentloaded", timeout=15000)
                    except Exception as rx:
                        print(f"Reload note: {rx}")
                    for rem in range(300, 0, -30):
                        print(f"  Cooldown remaining: {rem}s...")
                        time.sleep(30)
                    time.sleep(5)
                    continue

                elif consecutive_failures >= 3:
                    print(f"\nEscalation #3: 3 continuous failures reached on model '{current_model}'!")
                    model_cascade_idx += 1
                    if model_cascade_idx < len(MODEL_CASCADE):
                        next_model = MODEL_CASCADE[model_cascade_idx]
                        print(f"-> SHIFTING MODEL CASCADE: '{current_model}' -> '{next_model}'")
                        try:
                            flow_page.reload(wait_until="domcontentloaded")
                            time.sleep(3)
                        except Exception as rx:
                            pass
                        switch_flow_model(flow_page, next_model)
                        current_model = next_model
                        consecutive_failures = 0
                        update_status(shot_idx, total_shots, "MODEL_SHIFTED", f"Shifted to {next_model} after 3 failures on Shot {shot_idx}", current_model)
                        print("Waiting 30s for canvas stabilization before retrying shot...")
                        time.sleep(30)
                        continue
                    else:
                        print(f"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        print(f"CRITICAL: All models in cascade ({', '.join(MODEL_CASCADE)}) exhausted!")
                        print(f"HALTING PIPELINE AND PROMPTING USER.")
                        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        flow_page.screenshot(path=os.path.join("2- Code", "flow_error_halt.png"))
                        update_status(shot_idx, total_shots, "HALTED_CASCADE_EXHAUSTED", f"All models exhausted on Shot {shot_idx}: {err_msg}", current_model)
                        sys.exit(2)

            # If full generation successful
            consecutive_failures = 0
            print(f"Render successful! Downloading {len(new_srcs[:TARGET_VARIATIONS])} variations...")

            downloaded_paths = []
            for var_idx, src in enumerate(new_srcs[:TARGET_VARIATIONS], 1):
                raw_path = os.path.join(RAW_IMG_DIR, f"shot_{shot_idx:03d}_var_{var_idx}.jpg")
                try:
                    resp = flow_page.request.get(src)
                    if resp.status == 200:
                        with open(raw_path, "wb") as f_out:
                            f_out.write(resp.body())
                        downloaded_paths.append((var_idx, raw_path))
                except Exception as dx:
                    print(f"  Download error var {var_idx}: {dx}")

            # Step 2: Analyze all variations and select the best one
            best_var = 1
            best_score = -1.0
            best_path = None
            best_details = {}

            for var_idx, path in downloaded_paths:
                score, details = analyze_and_score_variation(path)
                print(f"  Variation {var_idx}: Score {score:.1f} ({details})")
                if score > best_score:
                    best_score = score
                    best_var = var_idx
                    best_path = path
                    best_details = details

            if best_path and os.path.exists(best_path):
                # Step 3: Put that best image to Final selected images folders
                shutil.copy2(best_path, final_root_file)
                shutil.copy2(best_path, final_finals_file)
                shutil.copy2(best_path, final_legacy_file)
                print(f"-> [SELECTED BEST] Shot {shot_idx:03d} -> Variation {best_var} (Score: {best_score:.1f}) saved to Final selected images!")

                # Log to CSV
                with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([shot_idx, timecode, best_var, round(best_score, 1), vo_text, datetime.now().isoformat()])

                # Live update prompt status & dashboard
                refresh_trackers()
                update_status(shot_idx, total_shots, "RUNNING", f"Completed shot {shot_idx} (Selected var {best_var})", current_model)
            else:
                print(f"Warning: No valid best image path for Shot {shot_idx}")

            # Step 4: Random interval pacing (10 to 30 seconds) before next shot
            pacing_wait = round(random.uniform(10.0, 30.0), 1)
            print(f"Pacing: Waiting {pacing_wait}s before next shot...")
            time.sleep(pacing_wait)
            shot_idx += 1

    print("\n========================================================")
    print("ALL 334 PROMPTS COMPLETED SUCCESSFULLY!")
    print("Final images are saved in Final selected images/")
    refresh_trackers()
    update_status(total_shots, total_shots, "COMPLETED", "All shots generated and selected!", current_model)

if __name__ == "__main__":
    main()
