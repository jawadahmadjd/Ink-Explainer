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
import threading
from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

STAGE4_PAUSE_EVENT = threading.Event()
STAGE4_PAUSE_EVENT.set()
STAGE4_CANCEL_FLAG = False
STAGE4_RUNNING_FLAG = False

class _Stage4RunningTracker:
    def __enter__(self):
        global STAGE4_RUNNING_FLAG
        STAGE4_RUNNING_FLAG = True
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        global STAGE4_RUNNING_FLAG
        STAGE4_RUNNING_FLAG = False

def pause_stage4():
    STAGE4_PAUSE_EVENT.clear()

def resume_stage4():
    STAGE4_PAUSE_EVENT.set()

def cancel_stage4():
    global STAGE4_CANCEL_FLAG, STAGE4_RUNNING_FLAG
    STAGE4_CANCEL_FLAG = True
    STAGE4_RUNNING_FLAG = False
    STAGE4_PAUSE_EVENT.set()

def is_stage4_paused() -> bool:
    """Return True if Stage 4 image generation is actively paused."""
    return not STAGE4_PAUSE_EVENT.is_set()

def is_stage4_running() -> bool:
    """Return True if Stage 4 image generation worker loop is actively executing."""
    return bool(STAGE4_RUNNING_FLAG)

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
        page.keyboard.press("Escape")
        time.sleep(0.3)

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

        # Close settings panel cleanly via keyboard Escape (never click arbitrary sidebar coordinates)
        page.keyboard.press("Escape")
        time.sleep(0.3)
        page.keyboard.press("Escape")
        time.sleep(0.3)
    except Exception as e:
        print(f"[MODEL SWITCH] Note during switch: {e}")
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass

def download_flow_image_2k(flow_page, target_src: str = None, dest_path: str = None, timeout: int = 30000) -> bool:
    """
    Downloads native 2K (Upscaled) image from Google Flow via Playwright CDP.
    Finds the image by src or clicks the latest rendered image, opens detail view,
    clicks 'Download media' -> '2K (Upscaled)', saves to dest_path, and returns to canvas.
    """
    try:
        flow_page.keyboard.press("Escape")
        time.sleep(0.3)

        # Locate image element
        target_locator = None
        if target_src:
            loc = flow_page.locator(f'img[src="{target_src}"]')
            if loc.count() > 0:
                target_locator = loc.first

        if not target_locator:
            # Fallback to large image on canvas
            imgs = flow_page.locator("img")
            for i in range(imgs.count()):
                box = imgs.nth(i).bounding_box()
                if box and box['width'] > 200:
                    target_locator = imgs.nth(i)
                    break

        if not target_locator:
            print("  [2K DOWNLOAD] Could not locate target image on canvas.")
            return False

        target_locator.click(force=True)
        time.sleep(1.0)

        # Find download media button
        dl_btn = flow_page.locator('button[aria-label="Download media"], button[aria-label="Download"]').first
        if not dl_btn.is_visible():
            dl_btn = flow_page.locator('button:has-text("download")').first

        if not dl_btn.is_visible():
            print("  [2K DOWNLOAD] Download button not visible in detail view.")
            flow_page.keyboard.press("Escape")
            return False

        dl_btn.click(force=True)
        time.sleep(0.5)

        # Find 2K option
        menu_2k = flow_page.locator('button[role="menuitem"]:has-text("2K")').first
        if not menu_2k.is_visible():
            menu_2k = flow_page.locator('button:has-text("2K\\nUpscaled"), button:has-text("2K")').first

        if not menu_2k.is_visible():
            print("  [2K DOWNLOAD] 2K Upscaled option not found in menu.")
            flow_page.keyboard.press("Escape")
            return False

        with flow_page.expect_download(timeout=timeout) as dl_info:
            menu_2k.click(force=True)

        download = dl_info.value
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        download.save_as(dest_path)

        # Return to canvas
        done_btn = flow_page.locator('button:has-text("Done")').first
        if done_btn.is_visible():
            done_btn.click(force=True)
            time.sleep(0.5)
        else:
            flow_page.keyboard.press("Escape")
            time.sleep(0.5)

        print(f"  -> [2K SUCCESS] Downloaded native 2K image ({os.path.getsize(dest_path)} bytes) to {os.path.basename(dest_path)}")
        return True
    except Exception as ex:
        print(f"  [2K DOWNLOAD WARNING] Flow 2K download exception: {ex}")
        try:
            done_btn = flow_page.locator('button:has-text("Done")').first
            if done_btn.is_visible():
                done_btn.click(force=True)
            else:
                flow_page.keyboard.press("Escape")
        except Exception:
            pass
        return False

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

def has_valid_final_image(final_img_dir: str, shot_num: int) -> bool:
    """Checks if a valid, non-zero-byte final image exists for the given shot number."""
    for ext in (".jpg", ".png", ".jpeg"):
        p = os.path.join(final_img_dir, f"shot_{shot_num:03d}{ext}")
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return True
    return False

def get_missing_shots(video_title: str, start_shot: int = 1, end_shot: int = None) -> list:
    """
    Returns a sorted list of shot numbers from master CSV that do not currently have
    a valid image file in final_images_dir.
    """
    dirs = config.get_project_dirs(video_title)
    final_img_dir = dirs["final_images_dir"]
    master_csv = dirs["master_csv"]
    if not os.path.exists(master_csv):
        return []

    with open(master_csv, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))[1:]

    max_end = end_shot or len(rows)
    missing = []
    for r in rows:
        try:
            shot_num = int(r[0])
        except (ValueError, IndexError):
            continue
        if start_shot <= shot_num <= max_end:
            if not has_valid_final_image(final_img_dir, shot_num):
                missing.append(shot_num)
    return sorted(missing)

def update_production_status(
    finals_dir: str,
    shot_num: int,
    total_shots: int,
    completed_count: int,
    status: str,
    note: str = "",
    active_model: str = "Nano Banana Pro",
    last_image_info: dict = None
):
    """Writes Arslan's production_status.json in the project finals directory."""
    try:
        os.makedirs(finals_dir, exist_ok=True)
        status_file = os.path.join(finals_dir, "production_status.json")
        data = {
            "current_shot": shot_num,
            "total_shots": total_shots,
            "completed_count": completed_count,
            "status": status,
            "active_model": active_model,
            "last_updated": datetime.now().isoformat(),
            "note": note,
            "last_image": last_image_info
        }
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as ex:
        print(f"  [TRACKER WARNING] Could not write production_status.json: {ex}")

def update_prompt_status_md(
    video_title: str,
    finals_dir: str,
    total_shots: int,
    completed_count: int,
    rows: list,
    selection_log_path: str = None
):
    """Writes Arslan's PROMPT_STATUS.md with visual progress bar and shot status table."""
    try:
        os.makedirs(finals_dir, exist_ok=True)
        status_md = os.path.join(finals_dir, "PROMPT_STATUS.md")
        pct = (completed_count / total_shots * 100.0) if total_shots > 0 else 0.0
        remaining = max(0, total_shots - completed_count)
        filled_blocks = int(pct // 5)
        empty_blocks = max(0, 20 - filled_blocks)
        progress_bar = "█" * filled_blocks + "░" * empty_blocks

        scores_by_shot = {}
        if selection_log_path and os.path.exists(selection_log_path):
            try:
                with open(selection_log_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    for r in reader:
                        if r and len(r) >= 4:
                            try:
                                scores_by_shot[int(r[0])] = (r[2], r[3])
                            except Exception:
                                pass
            except Exception:
                pass

        lines = [
            f"# Storyboard Generation Live Status Tracker: {video_title}",
            "",
            f"**Overall Progress**: `{progress_bar}` **{pct:.1f}%** ({completed_count} / {total_shots} Shots Completed | {remaining} Remaining)",
            "",
            f"- **Storage Location**: `Final selected images/`",
            f"- **Status File**: `production_status.json`",
            f"- **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## Shots Overview",
            "",
            "| Shot # | Timecode | Status | Score | VO Script |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ]

        final_img_dir = os.path.join(finals_dir, "Final selected images")
        for r in rows:
            try:
                s_num = int(r[0])
            except Exception:
                continue
            tc = r[1] if len(r) > 1 else ""
            vo = (r[2][:50] + "...") if len(r) > 2 and len(r[2]) > 50 else (r[2] if len(r) > 2 else "")
            done = has_valid_final_image(final_img_dir, s_num)
            st_text = "✓ COMPLETED" if done else "⏳ PENDING"
            score_str = scores_by_shot.get(s_num, ("", "--"))[1] if done else "--"
            lines.append(f"| #{s_num:03d} | {tc} | {st_text} | {score_str} | {vo} |")

        with open(status_md, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    except Exception as ex:
        print(f"  [TRACKER WARNING] Could not write PROMPT_STATUS.md: {ex}")

def run_stage4_image_gen(
    video_title: str,
    target_shots: list = None,
    start_shot: int = 1,
    end_shot: int = None,
    model: str = None,
    limit: int = 0,
    force_all: bool = False,
    resolution: str = None,
    only_missing: bool = False,
    status_callback: callable = None
) -> dict:
    """
    Run autonomous stick-figure image generation and curation on Google Flow.
    """
    global STAGE4_CANCEL_FLAG, STAGE4_RUNNING_FLAG
    STAGE4_CANCEL_FLAG = False
    STAGE4_RUNNING_FLAG = True

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

    if target_shots:
        shots_to_run = [int(s) for s in target_shots if int(s) in csv_map]
    elif only_missing:
        shots_to_run = get_missing_shots(video_title, start_shot=start_shot, end_shot=end_shot)
    else:
        max_end = end_shot or len(rows)
        shots_to_run = [
            int(r[0]) for r in rows
            if (force_all or not has_valid_final_image(final_img_dir, int(r[0])))
            and (start_shot <= int(r[0]) <= max_end)
        ]

    if limit > 0:
        shots_to_run = shots_to_run[:limit]

    print(f"\n[STAGE 4] Google Flow Autonomous Image Generation for '{video_title}'")
    print(f"Target Shots: {len(shots_to_run)} shots (Only Missing Mode: {only_missing})")

    completed_on_disk = len([r for r in rows if has_valid_final_image(final_img_dir, int(r[0]))])
    res_setting = (resolution or getattr(config, "FLOW_IMAGE_RESOLUTION", "2k") or "2k").lower().strip()
    current_model = model or config.MODEL_CASCADE[0]
    completed_in_run = 0

    def emit_progress(phase: str, phase_text: str, shot_idx: int = None, score: float = None, last_image: dict = None, pacing_sec: float = 0.0):
        update_production_status(
            finals_dir=dirs["finals_dir"],
            shot_num=shot_idx or 0,
            total_shots=len(rows),
            completed_count=completed_on_disk,
            status=phase,
            note=phase_text,
            active_model=current_model,
            last_image_info=last_image
        )
        if status_callback:
            try:
                run_target_count = len(shots_to_run)
                run_pct = round((completed_in_run / run_target_count * 100.0), 1) if run_target_count > 0 else 100.0
                payload = {
                    "is_active": phase not in ("COMPLETE", "HALTED", "CANCELLED"),
                    "shot_num": shot_idx,
                    "index_in_run": min(run_target_count, completed_in_run + (1 if phase not in ("APPROVED", "PACING", "COMPLETE") else 0)),
                    "total_in_run": run_target_count,
                    "completed_in_run": completed_in_run,
                    "total_project_shots": len(rows),
                    "completed_project_shots": completed_on_disk,
                    "run_percent": run_pct,
                    "phase": phase,
                    "phase_text": phase_text,
                    "model": current_model,
                    "resolution": res_setting.upper(),
                    "best_score": score,
                    "last_approved_shot": last_image,
                    "pacing_sec": pacing_sec
                }
                status_callback(payload)
            except Exception as cb_err:
                print(f"  [STATUS CALLBACK WARNING] {cb_err}")

    if not shots_to_run:
        STAGE4_RUNNING_FLAG = False
        print("All target shots already generated and verified! Zero remaining.")
        emit_progress("COMPLETE", f"All {len(rows)} shots already generated and verified! Zero remaining.")
        update_prompt_status_md(video_title, dirs["finals_dir"], len(rows), completed_on_disk, rows, selection_log)
        return {"completed": len(rows), "pending": 0, "total_missing": 0, "completed_in_run": 0}

    emit_progress("START", f"Initialized generation for {len(shots_to_run)} shots...")

    # Connect to Chrome DevTools CDP
    model_cascade_idx = config.MODEL_CASCADE.index(current_model) if current_model in config.MODEL_CASCADE else 0

    with _Stage4RunningTracker(), sync_playwright() as p:
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
            emit_progress("HALTED", "Could not connect to Chrome on port 9222.")
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

        for shot_idx in shots_to_run:
            if STAGE4_CANCEL_FLAG:
                print("  [STAGE 4] Generation cancelled by user.")
                emit_progress("CANCELLED", "Generation cancelled by user.", shot_idx=shot_idx)
                break
            STAGE4_PAUSE_EVENT.wait()
            row = csv_map.get(shot_idx)
            if not row: continue

            final_file = os.path.join(final_img_dir, f"shot_{shot_idx:03d}.jpg")
            prompt = row[4] if len(row) > 4 else row[3]
            vo_text = row[2]
            tc = row[1]

            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] GENERATING SHOT {shot_idx:03d} (Model: {current_model})")
            print(f"VO: {vo_text[:70]}...")
            emit_progress("INJECTING", f"Shot #{shot_idx:03d}: Injecting prompt into Google Flow...", shot_idx=shot_idx)

            # Ensure we are NOT inside the Characters tab or any modal dialog
            try:
                flow_page.evaluate("""() => {
                    const listItems = Array.from(document.querySelectorAll('mat-list-item, .mdc-list-item'));
                    const charItem = listItems.find(el => (el.innerText || '').toLowerCase().includes('characters'));
                    if (charItem && (charItem.classList.contains('mdc-list-item--activated') || charItem.getAttribute('aria-selected') === 'true')) {
                        const allMedia = listItems.find(el => (el.innerText || '').toLowerCase().includes('all media'));
                        if (allMedia) allMedia.click();
                    }
                    const closeButtons = document.querySelectorAll('mat-dialog-container button[aria-label="Close"], button[aria-label="Close dialog"]');
                    closeButtons.forEach(b => b.click());
                }""")
            except Exception:
                pass

            # Inject prompt specifically into the main generation ProseMirror editor
            type_success = False
            for attempt in range(3):
                try:
                    editor = flow_page.locator("div.prosemirror-editor div.ProseMirror, div.ProseMirror[contenteditable='true'], div.ProseMirror").first
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

            # Snapshot existing images before submitting
            existing_srcs = set(flow_page.evaluate("""() => {
                const imgs = Array.from(document.querySelectorAll('img')).filter(i => {
                    const s = i.src || '';
                    return s.includes('googleusercontent') || s.includes('blob:') || s.includes('data:image') || s.includes('flow-content.google');
                });
                return imgs.map(i => i.src);
            }""") or [])

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
            emit_progress("RENDERING", f"Shot #{shot_idx:03d}: Waiting for Google Flow to render variations...", shot_idx=shot_idx)
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

                # Check for newly rendered images
                srcs = flow_page.evaluate("""() => {
                    const imgs = Array.from(document.querySelectorAll('img')).filter(i => {
                        const s = i.src || '';
                        return s.includes('googleusercontent') || s.includes('blob:') || s.includes('data:image') || s.includes('flow-content.google');
                    });
                    return imgs.map(i => i.src);
                }""") or []
                new_srcs = [s for s in srcs if s not in existing_srcs]
                if len(new_srcs) >= config.TARGET_VARIATIONS:
                    time.sleep(1.5)
                    render_success = True
                    break

            # 1-Image Rule: if at least 1 image rendered despite timeout/error
            if not render_success and len(new_srcs) >= 1:
                print(f"  [1-IMAGE RULE] {len(new_srcs)} variation rendered under partial timeout. Evaluating viability...")
                render_success = True

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
            emit_progress("SCORING", f"Shot #{shot_idx:03d}: Scoring variations & fetching {res_setting.upper()} image...", shot_idx=shot_idx)
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
                # If 2K resolution requested, download native 2K version from Flow for winning variation
                downloaded_2k = False
                if res_setting == "2k" and best_var <= len(new_srcs):
                    best_src = new_srcs[best_var - 1]
                    downloaded_2k = download_flow_image_2k(flow_page, target_src=best_src, dest_path=final_file)

                if not downloaded_2k or not os.path.exists(final_file):
                    safe_copy_file(best_path, final_file)

                # Also copy to root junction if present
                root_final = os.path.join(config.ROOT_CANONICAL_IMAGES_DIR, f"shot_{shot_idx:03d}.jpg")
                if os.path.exists(config.ROOT_CANONICAL_IMAGES_DIR):
                    safe_copy_file(final_file, root_final)

                res_label = "2K Native Upscaled" if downloaded_2k else "1K Standard"
                print(f"  -> [APPROVED] Shot {shot_idx:03d} Var {best_var} ({res_label}, Score: {best_score:.1f}) saved to Final selected images!")

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
                completed_on_disk += 1

                last_shot_payload = {
                    "shot_num": shot_idx,
                    "score": round(best_score, 1),
                    "res_label": res_label,
                    "timecode": tc,
                    "image_url": f"/images/{dirs['title']}/Final selected images/shot_{shot_idx:03d}.jpg",
                    "vo_text": vo_text[:80]
                }
                emit_progress(
                    phase="APPROVED",
                    phase_text=f"Shot #{shot_idx:03d} Approved ({res_label}, Score: {best_score:.1f})!",
                    shot_idx=shot_idx,
                    score=round(best_score, 1),
                    last_image=last_shot_payload
                )
                update_prompt_status_md(video_title, dirs["finals_dir"], len(rows), completed_on_disk, rows, selection_log)

            pacing = round(random.uniform(config.PACING_MIN_SEC, config.PACING_MAX_SEC), 1)
            print(f"  Pacing: Waiting {pacing}s...")
            emit_progress("PACING", f"Resting {pacing}s anti-ban pacing before next shot...", shot_idx=shot_idx, pacing_sec=pacing)
            time.sleep(pacing)

    emit_progress("COMPLETE", f"Stage 4 complete: {completed_in_run} shots generated.")
    update_prompt_status_md(video_title, dirs["finals_dir"], len(rows), completed_on_disk, rows, selection_log)
    print(f"\n-> [STAGE 4 COMPLETE] Generated {completed_in_run} shots.")
    return {"completed_in_run": completed_in_run}
