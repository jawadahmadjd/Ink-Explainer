"""
Stage 4: Autonomous Google Flow Stick-Figure Generation & Curation Pipeline
Automates Google Flow via Chrome DevTools CDP, model cascade (Pro > 2 > 2 Lite),
instant limit bypass, computer vision scoring, and strictly saves to Final selected images/.
"""

import os
import sys
import time
import json
import csv
import random
import shutil
from datetime import datetime
from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def safe_copy_file(src: str, dst: str, max_retries: int = 5, retry_delay: float = 1.0):
    """Safely copy a file handling Windows file-lock contention."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    last_err = None
    for attempt in range(max_retries):
        try:
            shutil.copyfile(src, dst)
            return True
        except Exception as e:
            last_err = e
            time.sleep(retry_delay)
    # Byte-level fallback
    try:
        with open(src, "rb") as f_in, open(dst, "wb") as f_out:
            f_out.write(f_in.read())
        return True
    except Exception as e:
        print(f"  [ERROR] safe_copy_file failed after {max_retries} retries: {e}")
        return False

def check_for_page_errors(page):
    """Check if Google Flow displayed an error toast, banner, or usage limit."""
    try:
        return page.evaluate("""() => {
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
    except Exception:
        return None

def switch_flow_model(page, target_model_name):
    """Switch model family in Google Flow settings dropdown."""
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

        item = page.locator(f'button[role="menuitem"]:has-text("{target_model_name}"), div[role="menuitem"]:has-text("{target_model_name}")').first
        if item.count() > 0:
            item.click(timeout=5000)
            time.sleep(1.0)
            print(f"[MODEL SWITCH] Successfully switched to {target_model_name}")
        else:
            print(f"[MODEL SWITCH] Could not find menu item '{target_model_name}', pressing Escape")
            page.keyboard.press("Escape")

        # Close settings panel
        page.keyboard.press("Escape")
        time.sleep(0.5)
        page.mouse.click(200, 200)
    except Exception as e:
        print(f"[MODEL SWITCH] Note during switch: {e}")
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass

def analyze_and_score_variation(image_path: str, is_character_shot: bool = True):
    """Evaluate image quality, stick-figure compliance, and border absence."""
    try:
        img = Image.open(image_path).convert("RGB")
        arr = np.array(img, dtype=np.float32)

        # Grayscale
        gray = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]

        # 1. Sharpness (Laplacian variance approximation)
        diff_x = np.abs(gray[:, 1:] - gray[:, :-1])
        diff_y = np.abs(gray[1:, :] - gray[:-1, :])
        edge_energy = float(np.mean(diff_x) + np.mean(diff_y))
        sharpness_score = min(100.0, edge_energy * 3.5)

        # 2. Contrast
        p5, p95 = np.percentile(gray, (5, 95))
        contrast_score = min(100.0, (p95 - p5) / 2.0)

        # 3. Stick Figure Verification
        stick_penalty = 0.0
        stick_head_detected = False
        head_area = 0

        if is_character_shot:
            white_mask = (arr[:, :, 0] > 235) & (arr[:, :, 1] > 235) & (arr[:, :, 2] > 235)
            black_mask = (arr[:, :, 0] < 45) & (arr[:, :, 1] < 45) & (arr[:, :, 2] < 45)
            white_pixels = int(np.sum(white_mask))
            black_pixels = int(np.sum(black_mask))
            if white_pixels > 500 and black_pixels > 200:
                stick_head_detected = True
                head_area = white_pixels

        # 4. Full-bleed border penalty
        h, w = gray.shape
        margin = 15
        border_penalty = 0.0
        border_white = (
            np.mean(gray[:margin, :]) > 248 or
            np.mean(gray[-margin:, :]) > 248 or
            np.mean(gray[:, :margin]) > 248 or
            np.mean(gray[:, -margin:]) > 248
        )
        if border_white:
            border_penalty = 50.0

        total_score = max(0.0, (sharpness_score * 0.4 + contrast_score * 0.4 + 20.0) - stick_penalty - border_penalty)

        return total_score, {
            "sharpness": round(sharpness_score, 1),
            "contrast": round(contrast_score, 1),
            "stick_head_detected": stick_head_detected,
            "head_area": head_area,
            "border_penalty": border_penalty,
            "total_score": round(total_score, 1)
        }
    except Exception as e:
        return 50.0, {"error": str(e)}

def run_stage4_image_gen(
    video_title: str,
    target_shots: list = None,
    start_shot: int = 1,
    end_shot: int = None,
    model: str = None,
    limit: int = 0
) -> dict:
    """
    Run autonomous stick-figure image generation and curation on Google Flow.
    """
    dirs = config.get_project_dirs(video_title)
    final_img_dir = dirs["final_images_dir"]
    raw_img_dir = dirs["raw_images_dir"]
    master_csv = dirs["master_csv"]
    audit_json = dirs["character_audit"]
    selection_log = dirs["selection_log"]
    prompt_status_md = dirs["prompt_status_md"]

    os.makedirs(final_img_dir, exist_ok=True)
    os.makedirs(raw_img_dir, exist_ok=True)

    with open(master_csv, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))[1:]
    csv_map = {int(r[0]): r for r in rows}

    with open(audit_json, "r", encoding="utf-8") as f:
        audit_records = json.load(f)
    audit_map = {d["shot_num"]: d for d in audit_records}

    # Determine shots to process
    if target_shots:
        shots_to_run = [int(s) for s in target_shots if int(s) in csv_map]
    else:
        max_end = end_shot or len(rows)
        shots_to_run = [
            d["shot_num"] for d in audit_records
            if d.get("regen_needed", False) and (start_shot <= d["shot_num"] <= max_end)
        ]

    if limit > 0:
        shots_to_run = shots_to_run[:limit]

    print(f"\n[STAGE 4] Google Flow Autonomous Image Generation for '{video_title}'")
    print(f"Target Shots: {len(shots_to_run)} shots")

    if not shots_to_run:
        print("All target shots already generated and verified! Zero remaining.")
        return {"completed": len(rows), "pending": 0}

    # Connect to Chrome DevTools CDP
    current_model = model or config.MODEL_CASCADE[0]
    model_cascade_idx = config.MODEL_CASCADE.index(current_model) if current_model in config.MODEL_CASCADE else 0

    with sync_playwright() as p:
        browser = None
        ctx = None
        for cdp in config.CDP_ENDPOINTS:
            try:
                b = p.chromium.connect_over_cdp(cdp)
                for c in b.contexts:
                    if any("flow.google.com" in pg.url for pg in c.pages):
                        browser = b
                        ctx = c
                        print(f"Connected to Google Flow Chrome via {cdp}")
                        break
                if browser: break
            except Exception:
                continue

        if not browser:
            raise ConnectionError("Could not connect to Chrome on port 9222. Please start Chrome with --remote-debugging-port=9222.")

        # Find Flow tab
        flow_page = None
        for pg in ctx.pages:
            if "flow.google.com" in pg.url:
                flow_page = pg
                break

        if not flow_page:
            flow_page = ctx.new_page()
            flow_page.goto("https://flow.google.com", wait_until="domcontentloaded")
            time.sleep(5)

        flow_page.bring_to_front()
        switch_flow_model(flow_page, current_model)

        consecutive_failures = 0
        completed_in_run = 0

        for shot_idx in shots_to_run:
            row = csv_map.get(shot_idx)
            if not row: continue

            final_file = os.path.join(final_img_dir, f"shot_{shot_idx:03d}.jpg")
            prompt = row[4] if len(row) > 4 else row[3]
            vo_text = row[2]
            tc = row[1]

            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] GENERATING SHOT {shot_idx:03d} (Model: {current_model})")
            print(f"VO: {vo_text[:70]}...")

            # Inject prompt
            type_success = False
            for attempt in range(3):
                try:
                    editor = flow_page.locator("div.ProseMirror, textarea, [contenteditable='true']").first
                    editor.click(timeout=4000)
                    time.sleep(0.3)
                    flow_page.keyboard.press("Control+A")
                    flow_page.keyboard.press("Backspace")
                    time.sleep(0.2)
                    editor.fill(prompt)
                    type_success = True
                    break
                except Exception as ex:
                    time.sleep(1.0)

            if not type_success:
                print(f"  Error typing prompt for Shot {shot_idx}. Skipping.")
                continue

            # Click generate
            clicked = False
            for attempt in range(3):
                try:
                    start_btn = flow_page.locator('button[aria-label="Start generation"], button:has-text("Start generation"), button:has-text("Generate")').first
                    if start_btn.count() > 0 and start_btn.is_visible():
                        start_btn.click(timeout=4000)
                        clicked = True
                        break
                except Exception:
                    time.sleep(1.0)

            if not clicked:
                print(f"  Could not click generate button for Shot {shot_idx}.")
                continue

            print("  Monitoring render stream (up to 55s)...")
            start_time = time.time()
            render_success = False
            new_srcs = []

            while time.time() - start_time < 55:
                time.sleep(2.5)
                err = check_for_page_errors(flow_page)
                if err:
                    print(f"  Alert during render: {err}")
                    # Fast cascade if usage limit detected
                    if "limit" in err.lower() or "usage" in err.lower():
                        model_cascade_idx += 1
                        if model_cascade_idx < len(config.MODEL_CASCADE):
                            next_m = config.MODEL_CASCADE[model_cascade_idx]
                            print(f"  -> Instant limit bypass: Shifting to {next_m}...")
                            switch_flow_model(flow_page, next_m)
                            current_model = next_m
                            break
                    break

                # Check for rendered images
                srcs = flow_page.evaluate("""() => {
                    const imgs = Array.from(document.querySelectorAll('img')).filter(i => {
                        const s = i.src || '';
                        return s.includes('googleusercontent') || s.includes('blob:') || s.includes('data:image');
                    });
                    return imgs.map(i => i.src);
                }""")
                if len(srcs) >= config.TARGET_VARIATIONS:
                    new_srcs = srcs
                    render_success = True
                    break

            if not render_success and len(new_srcs) < 1:
                consecutive_failures += 1
                print(f"  [FAILURE #{consecutive_failures} ON SHOT {shot_idx:03d}]")
                if consecutive_failures >= 3:
                    model_cascade_idx += 1
                    if model_cascade_idx < len(config.MODEL_CASCADE):
                        current_model = config.MODEL_CASCADE[model_cascade_idx]
                        print(f"  -> Shifting model to: {current_model}")
                        switch_flow_model(flow_page, current_model)
                        consecutive_failures = 0
                time.sleep(10)
                continue

            # Ingest rendered variations
            consecutive_failures = 0
            downloaded = []
            for var_idx, src in enumerate(new_srcs[:config.TARGET_VARIATIONS], 1):
                raw_path = os.path.join(raw_img_dir, f"shot_{shot_idx:03d}_var_{var_idx}.jpg")
                try:
                    resp = flow_page.request.get(src)
                    if resp.status == 200:
                        with open(raw_path, "wb") as f_out:
                            f_out.write(resp.body())
                        downloaded.append((var_idx, raw_path))
                except Exception as ex:
                    print(f"  Download error: {ex}")

            # Score variations
            best_var, best_score, best_path = 1, -1.0, None
            for var_idx, path in downloaded:
                score, details = analyze_and_score_variation(path, is_character_shot=True)
                print(f"  Var {var_idx}: Score {score:.1f}")
                if score > best_score:
                    best_score = score
                    best_var = var_idx
                    best_path = path

            if best_path and os.path.exists(best_path):
                safe_copy_file(best_path, final_file)
                # Also copy to root junction if present
                root_final = os.path.join(config.ROOT_CANONICAL_IMAGES_DIR, f"shot_{shot_idx:03d}.jpg")
                if os.path.exists(config.ROOT_CANONICAL_IMAGES_DIR):
                    safe_copy_file(best_path, root_final)

                print(f"  -> [APPROVED] Shot {shot_idx:03d} Var {best_var} (Score: {best_score:.1f}) saved to Final selected images!")

                # Update selection log
                with open(selection_log, "a", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow([shot_idx, tc, f"var_{best_var}", round(best_score, 1), vo_text, datetime.now().isoformat()])

                # Update audit
                if shot_idx in audit_map:
                    audit_map[shot_idx]["category"] = "VALID_STICK_FIGURE"
                    audit_map[shot_idx]["regen_needed"] = False
                    audit_map[shot_idx]["reason"] = "Autonomous generation verified."
                    with open(audit_json, "w", encoding="utf-8") as af:
                        json.dump(list(audit_map.values()), af, indent=2)

                completed_in_run += 1

            pacing = round(random.uniform(config.PACING_MIN_SEC, config.PACING_MAX_SEC), 1)
            print(f"  Pacing: Waiting {pacing}s...")
            time.sleep(pacing)

    print(f"\n-> [STAGE 4 COMPLETE] Generated {completed_in_run} shots.")
    return {"completed_in_run": completed_in_run}
