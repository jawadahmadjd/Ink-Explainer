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

REGEN_QUEUE_JSON = os.path.join(PROJECT_ROOT, "3- Finals", "regeneration_queue.json")
RAW_IMG_DIR = os.path.join(PROJECT_ROOT, "3- Finals", "flow_generated_images")
FINAL_DIR_ROOT = os.path.join(PROJECT_ROOT, "Final selected images")
SELECTION_LOG = os.path.join(PROJECT_ROOT, "3- Finals", "selection_log.csv")

TARGET_PROJECT_URL = "https://flow.google.com/u/0/project/8a28cfa5-fddf-4528-b188-6deb5ce5e0e5"

def safe_evaluate(page, js_code, max_retries=3):
    for attempt in range(max_retries):
        try:
            return page.evaluate(js_code)
        except Exception as e:
            time.sleep(1.5)
    return None

def analyze_and_score_variation(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return -1.0, {}

    h, w, _ = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    sharpness_score = min(100.0, float(laplacian_var) / 15.0)

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

    center_y, center_x = int(h*0.2), int(w*0.2)
    center_crop = gray[center_y:int(h*0.8), center_x:int(w*0.8)]
    center_std = float(np.std(center_crop))
    center_score = min(100.0, center_std * 1.5)

    p5 = float(np.percentile(gray, 5))
    p95 = float(np.percentile(gray, 95))
    dynamic_range = p95 - p5
    contrast_score = min(100.0, (dynamic_range / 200.0) * 100.0)

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

def process_queue():
    if not os.path.exists(REGEN_QUEUE_JSON):
        print("No regeneration queue found.")
        return

    with open(REGEN_QUEUE_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    pending = [item for item in data.get("queue", []) if item.get("status") == "PENDING"]
    if not pending:
        print("No pending items in regeneration queue.")
        return

    print(f"Found {len(pending)} pending regeneration requests:")
    for p in pending:
        print(f"  - Shot #{p['shot_num']}: {p.get('critique', '')} [{', '.join(p.get('adjustments', []))}]")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        flow_page = None
        for ctx in browser.contexts:
            for page in ctx.pages:
                if "flow.google.com" in page.url:
                    flow_page = page
                    break
            if flow_page:
                break

        if not flow_page:
            print("Error: Could not find Google Flow tab in Chrome!")
            return

        flow_page.bring_to_front()
        print(f"Connected to Flow tab: {flow_page.title()}")

        for item in pending:
            shot_num = item["shot_num"]
            refined_prompt = item.get("refined_prompt") or item.get("original_prompt")
            print(f"\n--- Regenerating Shot #{shot_num} ---")
            print(f"Prompt: {refined_prompt[:90]}...")

            # Enter prompt into Flow input box
            res = safe_evaluate(flow_page, f"""() => {{
                const textarea = document.querySelector('textarea[aria-label*="prompt" i], textarea, [contenteditable="true"]');
                if (!textarea) return {{ success: false, error: 'textarea not found' }};
                textarea.focus();
                if (textarea.tagName.toLowerCase() === 'textarea') {{
                    textarea.value = {json.dumps(refined_prompt)};
                    textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    textarea.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }} else {{
                    textarea.innerText = {json.dumps(refined_prompt)};
                    textarea.dispatchEvent(new InputEvent('input', {{ bubbles: true }}));
                }}
                return {{ success: true }};
            }}""")

            if not res or not res.get("success"):
                print("Failed to set prompt in textarea.")
                continue

            time.sleep(1.0)

            # Click generate
            btn_clicked = safe_evaluate(flow_page, """() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                for (const b of buttons) {
                    const text = (b.innerText || '').toLowerCase();
                    const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                    if (text.includes('generate') || aria.includes('generate') || text.includes('start') || aria.includes('create')) {
                        b.click();
                        return true;
                    }
                }
                return false;
            }""")

            print(f"Generation triggered: {btn_clicked}. Waiting for new variations...")
            time.sleep(18.0)

            # Mark complete in queue
            item["status"] = "COMPLETED"
            item["completed_at"] = datetime.now().isoformat()
            with open(REGEN_QUEUE_JSON, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"Shot #{shot_num} marked as COMPLETED in queue.")

if __name__ == "__main__":
    process_queue()
