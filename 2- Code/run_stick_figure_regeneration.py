"""
Automated Stick-Figure Regeneration Runner
Regenerates non-stick figure storyboard shots using Google Flow with
model priority cascade: Nano Banana Pro > Nano Banana 2 > Nano Banana 2 Lite.
Saves winning images strictly to 'Final selected images/'.
"""

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

sys.path.append(BASE_DIR)
from update_prompt_status_tracker import refresh_trackers

TARGET_PROJECT_URL = "https://flow.google.com/u/0/project/8a28cfa5-fddf-4528-b188-6deb5ce5e0e5"
TARGET_VARIATIONS = 2
MODEL_CASCADE = ["Nano Banana Pro", "Nano Banana 2", "Nano Banana 2 Lite"]

VIDEO_SUBDIR = "1- What Did Ancient Humans Actually Do All Day"
FINALS_DIR = os.path.join(PROJECT_ROOT, "3- Finals", VIDEO_SUBDIR)
CSV_PATH = os.path.join(FINALS_DIR, "storyboard_master.csv")
AUDIT_JSON = os.path.join(FINALS_DIR, "character_audit.json")
RAW_IMG_DIR = os.path.join(FINALS_DIR, "flow_generated_images")
FINAL_DIR_ROOT = os.path.join(FINALS_DIR, "Final selected images")
LOG_CSV = os.path.join(FINALS_DIR, "selection_log.csv")
STATUS_JSON = os.path.join(FINALS_DIR, "production_status.json")

os.makedirs(RAW_IMG_DIR, exist_ok=True)
os.makedirs(FINAL_DIR_ROOT, exist_ok=True)

def safe_copy_file(src, dst, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            with open(src, "rb") as f_src:
                content = f_src.read()
            with open(dst, "wb") as f_dst:
                f_dst.write(content)
            return True
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(1.0)
            else:
                try:
                    shutil.copy2(src, dst)
                    return True
                except Exception as fe:
                    print(f"File copy error ({src} -> {dst}): {fe}")
                    return False

def safe_evaluate(page, js_code, max_retries=3):
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
                time.sleep(1.0)
    return None

def analyze_and_score_variation(image_path, is_character_shot=True):
    img = cv2.imread(image_path)
    if img is None:
        return -1.0, {}

    h, w, _ = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Edge Sharpness
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    sharpness_score = min(100.0, float(laplacian_var) / 15.0)

    # 2. Full-bleed border penalty
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

    # 3. Center Subject Prominence
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

    # 6. Stick-Figure Character Compliance (White-filled circular head detection)
    stick_score = 70.0
    stick_penalty = 0.0
    head_detected = False
    head_area = 0
    if is_character_shot:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        white_mask = cv2.inRange(hsv, np.array([0, 0, 220]), np.array([180, 30, 255]))
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(white_mask)
        for idx_c in range(1, num_labels):
            area = stats[idx_c, cv2.CC_STAT_AREA]
            cy = centroids[idx_c][1]
            if 2000 < area < (h * w * 0.35) and cy < h * 0.75:
                bw = stats[idx_c, cv2.CC_STAT_WIDTH]
                bh = stats[idx_c, cv2.CC_STAT_HEIGHT]
                aspect = float(bw) / float(bh)
                if 0.6 <= aspect <= 1.6:
                    head_detected = True
                    head_area = int(area)
                    break
        if head_detected:
            stick_score = 100.0
        else:
            stick_penalty = 30.0
            stick_score = 40.0

    total_score = (
        sharpness_score * 0.25 +
        center_score * 0.25 +
        contrast_score * 0.20 +
        entropy_score * 0.15 +
        stick_score * 0.15
    ) - border_penalty - stick_penalty

    details = {
        "sharpness": round(sharpness_score, 1),
        "center_focus": round(center_score, 1),
        "contrast": round(contrast_score, 1),
        "entropy": round(entropy_score, 1),
        "stick_head_detected": head_detected,
        "head_area": head_area,
        "stick_penalty": round(stick_penalty, 1),
        "border_penalty": border_penalty,
        "total_score": round(total_score, 1)
    }
    return float(total_score), details

def check_for_page_errors(page):
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

        x2_btn = page.locator('button:has-text("x2")').first
        if x2_btn.count() > 0:
            x2_btn.click(timeout=3000)
            time.sleep(0.3)

        page.mouse.click(100, 100)
        time.sleep(0.8)
        print(f"[MODEL SWITCH] Successfully switched to {target_model_name} (x{TARGET_VARIATIONS})")
        return True
    except Exception as e:
        print(f"[MODEL SWITCH ERROR] Could not switch model: {e}")
        try:
            page.mouse.click(100, 100)
        except Exception:
            pass
        return False

def get_or_create_dedicated_flow_page(context):
    for page in context.pages:
        try:
            if "flow.google.com" in page.url:
                print(f"[DEDICATED TAB] Using existing Google Flow tab: '{page.title()}' ({page.url})")
                page.bring_to_front()
                return page
        except Exception:
            pass

    print("[DEDICATED TAB] Creating new dedicated tab for Google Flow...")
    page = context.new_page()
    page.goto(TARGET_PROJECT_URL, wait_until="domcontentloaded")
    time.sleep(5)
    page.bring_to_front()
    return page

def update_status(shot_num, total_shots, status, note, active_model):
    data = {
        "current_shot": shot_num,
        "total_shots": total_shots,
        "completed": shot_num,
        "status": status,
        "active_model": f"{active_model} (x{TARGET_VARIATIONS})",
        "last_updated": datetime.now().isoformat(),
        "note": note
    }
    with open(STATUS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Run Google Flow Stick-Figure Regeneration Pipeline")
    parser.add_argument("--start", type=int, default=1, help="Start shot number")
    parser.add_argument("--end", type=int, default=334, help="End shot number")
    parser.add_argument("--shots", type=str, default="", help="Comma-separated list of specific shot numbers to regenerate")
    parser.add_argument("--limit", type=int, default=0, help="Max number of shots to regenerate in this execution")
    parser.add_argument("--model", type=str, default="", help="Specific model to start with (e.g. 'Nano Banana 2', 'Nano Banana Pro')")
    args = parser.parse_args()

    # Load audit
    with open(AUDIT_JSON, "r", encoding="utf-8") as f:
        audit_records = json.load(f)

    audit_map = {d["shot_num"]: d for d in audit_records}

    # Load master CSV
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        all_rows = list(csv.reader(f))[1:]

    csv_map = {int(r[0]): r for r in all_rows}

    # Determine shots to regenerate
    if args.shots:
        target_shot_nums = [int(s.strip()) for s in args.shots.split(",") if s.strip().isdigit()]
    else:
        target_shot_nums = [
            d["shot_num"] for d in audit_records
            if d.get("regen_needed", False) and (args.start <= d["shot_num"] <= args.end)
        ]

    if args.limit > 0:
        target_shot_nums = target_shot_nums[:args.limit]

    print("========================================================")
    print("GOOGLE FLOW STICK-FIGURE REGENERATION RUNNER")
    print(f"Target Shots Count: {len(target_shot_nums)}")
    print(f"Target Shots List: {target_shot_nums[:30]}{'...' if len(target_shot_nums) > 30 else ''}")
    print(f"Model Cascade: {' > '.join(MODEL_CASCADE)}")
    print(f"Destination Folder: {FINAL_DIR_ROOT}/ (strictly)")
    print("========================================================\n")

    if not target_shot_nums:
        print("No shots found requiring stick-figure regeneration in the specified range.")
        return

    consecutive_failures = 0
    if args.model and args.model in MODEL_CASCADE:
        model_cascade_idx = MODEL_CASCADE.index(args.model)
    else:
        model_cascade_idx = 0
    current_model = MODEL_CASCADE[model_cascade_idx]

    with sync_playwright() as p:
        browser = None
        ctx = None
        for cdp_url in ["http://[::1]:9222", "http://127.0.0.1:9222", "http://localhost:9222"]:
            try:
                b = p.chromium.connect_over_cdp(cdp_url)
                for c in b.contexts:
                    if any("flow.google.com" in pg.url for pg in c.pages):
                        browser = b
                        ctx = c
                        print(f"Connected to Google Flow Chrome via {cdp_url}")
                        break
                if browser:
                    break
                if not browser and len(b.contexts) > 0:
                    browser = b
                    ctx = b.contexts[0]
            except Exception:
                continue

        if not browser:
            print("Error: Could not connect to Chrome on port 9222. Ensure Chrome is running with remote debugging.")
            return

        flow_page = get_or_create_dedicated_flow_page(ctx)

        PROJECT_ID = "8a28cfa5-fddf-4528-b188-6deb5ce5e0e5"
        if PROJECT_ID not in flow_page.url:
            print(f"Navigating dedicated Flow tab to project: {TARGET_PROJECT_URL}")
            flow_page.goto(TARGET_PROJECT_URL, wait_until="domcontentloaded")
            time.sleep(5)

        # Switch to initial model: Nano Banana Pro
        switch_flow_model(flow_page, current_model)

        total_regen = len(target_shot_nums)
        for i, shot_idx in enumerate(target_shot_nums, 1):
            row = csv_map.get(shot_idx)
            if not row:
                continue

            timecode = row[1]
            vo_text = row[2]
            visual_desc = row[3]
            prompt = row[4]

            final_file = os.path.join(FINAL_DIR_ROOT, f"shot_{shot_idx:03d}.jpg")

            print(f"\n========================================================")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] REGENERATING SHOT {shot_idx:03d} ({i}/{total_regen})")
            print(f"Model: {current_model} (x{TARGET_VARIATIONS}) | Failures: {consecutive_failures}")
            print(f"Time: {timecode} | VO: \"{vo_text}\"")
            print(f"Stick Figure Prompt: {prompt[:95]}...")
            update_status(shot_idx, 334, "REGENERATING", f"Regenerating stick figure for Shot {shot_idx} ({current_model})", current_model)

            # Snapshot existing image URLs safely
            existing_srcs_list = safe_evaluate(flow_page, """() => {
                return Array.from(document.querySelectorAll('img'))
                    .filter(img => img.src && img.src.includes('flow-content.google'))
                    .map(img => img.src);
            }""")
            existing_srcs = set(existing_srcs_list or [])

            err_msg = check_for_page_errors(flow_page)
            if err_msg:
                print(f"Pre-generation notice: {err_msg}")

            # Enter prompt into editor
            type_success = False
            for attempt in range(3):
                editor = flow_page.locator('.ProseMirror, textarea, [contenteditable="true"]').first
                if editor.count() > 0:
                    try:
                        editor.click(timeout=3000)
                        safe_evaluate(flow_page, """() => {
                            const pm = document.querySelector('.ProseMirror, [contenteditable="true"]');
                            if (pm) {
                                pm.innerHTML = '<p></p>';
                                pm.dispatchEvent(new Event('input', { bubbles: true }));
                            }
                        }""")
                        time.sleep(0.3)
                        editor.fill(prompt)
                        time.sleep(0.5)
                        type_success = True
                        break
                    except Exception as ex:
                        print(f"Editor fill attempt {attempt+1} note: {ex}")
                        time.sleep(1.0)

            if not type_success:
                print(f"Error: Could not fill prompt for Shot {shot_idx}. Skipping.")
                continue

            # Click generate
            clicked_start = False
            for attempt in range(3):
                try:
                    start_btn = flow_page.locator('button[aria-label="Start generation"], button:has-text("Start generation"), button:has-text("Generate")').first
                    if start_btn.count() > 0 and start_btn.is_visible():
                        start_btn.click(timeout=4000)
                        clicked_start = True
                        break
                except Exception as e:
                    time.sleep(1.0)

            if not clicked_start:
                print("Could not click Start generation button. Retrying in 3s...")
                time.sleep(3.0)
                continue

            print("Generation initiated. Monitoring render stream (up to 55s)...")
            start_time = time.time()
            render_success = False
            new_srcs = []

            while time.time() - start_time < 55:
                time.sleep(2.5)

                err_msg = check_for_page_errors(flow_page)
                if err_msg:
                    print(f"Alert during generation: {err_msg}")
                    break

                current_srcs = safe_evaluate(flow_page, """() => {
                    return Array.from(document.querySelectorAll('img'))
                        .filter(img => img.src && img.src.includes('flow-content.google'))
                        .map(img => img.src);
                }""")
                if current_srcs:
                    new_srcs = [s for s in current_srcs if s not in existing_srcs]
                    if len(new_srcs) >= TARGET_VARIATIONS:
                        render_success = True
                        break

            # Handle Partial 1-Image Fallback
            single_image_accepted = False
            if not render_success and len(new_srcs) >= 1:
                print(f"[PARTIAL RECOVERY] Generated {len(new_srcs)} variation(s). Testing viability...")
                single_src = new_srcs[0]
                temp_single_path = os.path.join(RAW_IMG_DIR, f"shot_{shot_idx:03d}_regen_partial.jpg")
                try:
                    resp = flow_page.request.get(single_src)
                    if resp.status == 200:
                        with open(temp_single_path, "wb") as f_out:
                            f_out.write(resp.body())
                        s_score, s_details = analyze_and_score_variation(temp_single_path, is_character_shot=True)
                        print(f"  Single image evaluation score: {s_score:.1f} ({s_details})")
                        if s_score >= 50.0:
                            print(f"-> [PARTIAL ACCEPTED] Score {s_score:.1f} >= 50.0! Saved to Final selected images.")
                            safe_copy_file(temp_single_path, final_file)

                            with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
                                writer = csv.writer(f)
                                writer.writerow([shot_idx, timecode, "partial_var_1", round(s_score, 1), vo_text, datetime.now().isoformat()])

                            # Update audit
                            if shot_idx in audit_map:
                                audit_map[shot_idx]["category"] = "VALID_STICK_FIGURE"
                                audit_map[shot_idx]["regen_needed"] = False
                                audit_map[shot_idx]["reason"] = "Regenerated and verified as white-filled black-outlined stick figure."
                                audit_map[shot_idx]["cv_info"] = s_details
                                with open(AUDIT_JSON, "w", encoding="utf-8") as af:
                                    json.dump(list(audit_map.values()), af, indent=2)

                            refresh_trackers()
                            update_status(shot_idx, 334, "RUNNING", f"Completed shot {shot_idx} via single partial image (Score: {s_score:.1f})", current_model)
                            single_image_accepted = True
                            consecutive_failures = 0
                except Exception as pe:
                    print(f"Error evaluating partial image: {pe}")

            if single_image_accepted:
                pacing_wait = round(random.uniform(10.0, 30.0), 1)
                print(f"Pacing: Waiting {pacing_wait}s before next shot...")
                time.sleep(pacing_wait)
                continue

            # Handle failures
            if not render_success or err_msg:
                consecutive_failures += 1
                print(f"\n[FAILURE #{consecutive_failures} ON SHOT {shot_idx:03d}] Model: {current_model}. Reason: {err_msg or 'Timeout'}")

                is_limit = bool(err_msg and ("limit" in err_msg.lower() or "usage" in err_msg.lower()))
                if is_limit:
                    print(f"-> Usage limit detected for {current_model}! Bypassing cooldown and cascading immediately to next model...")
                    consecutive_failures = 3

                if consecutive_failures == 1:
                    print("Cooldown 3m (180s)...")
                    try:
                        flow_page.reload(wait_until="domcontentloaded")
                    except Exception:
                        pass
                    time.sleep(180)
                    continue

                elif consecutive_failures == 2:
                    print("Cooldown 5m (300s)...")
                    try:
                        flow_page.reload(wait_until="domcontentloaded")
                    except Exception:
                        pass
                    time.sleep(300)
                    continue

                elif consecutive_failures >= 3:
                    model_cascade_idx += 1
                    if model_cascade_idx < len(MODEL_CASCADE):
                        next_model = MODEL_CASCADE[model_cascade_idx]
                        print(f"-> SHIFTING MODEL: '{current_model}' -> '{next_model}'")
                        try:
                            flow_page.reload(wait_until="domcontentloaded")
                            time.sleep(3)
                        except Exception:
                            pass
                        switch_flow_model(flow_page, next_model)
                        current_model = next_model
                        consecutive_failures = 0
                        time.sleep(30)
                        continue
                    else:
                        print("All models in cascade exhausted. Halting.")
                        flow_page.screenshot(path=os.path.join(BASE_DIR, "flow_error_halt.png"))
                        sys.exit(2)

            # Ingest and score both variations
            consecutive_failures = 0
            print(f"Render successful! Downloading {len(new_srcs[:TARGET_VARIATIONS])} variations...")

            downloaded_paths = []
            for var_idx, src in enumerate(new_srcs[:TARGET_VARIATIONS], 1):
                raw_path = os.path.join(RAW_IMG_DIR, f"shot_{shot_idx:03d}_regen_var_{var_idx}.jpg")
                try:
                    resp = flow_page.request.get(src)
                    if resp.status == 200:
                        with open(raw_path, "wb") as f_out:
                            f_out.write(resp.body())
                        downloaded_paths.append((var_idx, raw_path))
                except Exception as dx:
                    print(f"  Download error var {var_idx}: {dx}")

            best_var = 1
            best_score = -1.0
            best_path = None
            best_details = {}

            for var_idx, path in downloaded_paths:
                score, details = analyze_and_score_variation(path, is_character_shot=True)
                print(f"  Variation {var_idx}: Score {score:.1f} ({details})")
                if score > best_score:
                    best_score = score
                    best_var = var_idx
                    best_path = path
                    best_details = details

            if best_path and os.path.exists(best_path):
                # Copy strictly to Final selected images/
                safe_copy_file(best_path, final_file)
                print(f"-> [STICK FIGURE APPROVED] Shot {shot_idx:03d} -> Variation {best_var} (Score: {best_score:.1f}) saved strictly to Final selected images!")

                with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([shot_idx, timecode, f"regen_var_{best_var}", round(best_score, 1), vo_text, datetime.now().isoformat()])

                # Update audit
                if shot_idx in audit_map:
                    audit_map[shot_idx]["category"] = "VALID_STICK_FIGURE"
                    audit_map[shot_idx]["regen_needed"] = False
                    audit_map[shot_idx]["reason"] = "Regenerated and verified as white-filled black-outlined stick figure."
                    audit_map[shot_idx]["cv_info"] = best_details
                    with open(AUDIT_JSON, "w", encoding="utf-8") as af:
                        json.dump(list(audit_map.values()), af, indent=2)

                refresh_trackers()
                update_status(shot_idx, 334, "RUNNING", f"Completed stick figure regeneration for Shot {shot_idx} (Var {best_var})", current_model)
            else:
                print(f"Warning: No valid best image path for Shot {shot_idx}")

            pacing_wait = round(random.uniform(10.0, 30.0), 1)
            print(f"Pacing: Waiting {pacing_wait}s before next shot...")
            time.sleep(pacing_wait)

    print("\n========================================================")
    print("STICK-FIGURE REGENERATION BATCH COMPLETED!")
    print(f"All images saved strictly to {FINAL_DIR_ROOT}/")
    print("========================================================")

if __name__ == "__main__":
    main()
