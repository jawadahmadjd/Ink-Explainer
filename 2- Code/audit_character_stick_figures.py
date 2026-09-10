"""
Character Stick Figure Compliance Audit Engine
Audits all 334 storyboard images to ensure strict adherence to the
white-filled black-outlined stick figure character standard.
"""

import csv
import json
import os
import re
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

VIDEO_SUBDIR = "1- What Did Ancient Humans Actually Do All Day"
FINALS_DIR = os.path.join(PROJECT_ROOT, "3- Finals", VIDEO_SUBDIR)
CSV_PATH = os.path.join(FINALS_DIR, "storyboard_master.csv")
IMG_DIR = os.path.join(FINALS_DIR, "Final selected images")
OUTPUT_JSON = os.path.join(FINALS_DIR, "character_audit.json")

char_patterns = [
    r'\bstick[\s\-_]?figure\b', r'\bstick[\s\-_]?figures\b',
    r'\bhunter\b', r'\bhunters\b',
    r'\bfarmer\b', r'\bfarmers\b',
    r'\bartist\b', r'\bartists\b',
    r'\bman\b', r'\bmen\b',
    r'\bwoman\b', r'\bwomen\b',
    r'\bchild\b', r'\bchildren\b', r'\bboy\b', r'\bgirl\b',
    r'\bperson\b', r'\bpeople\b',
    r'\bking\b', r'\bkings\b',
    r'\bguard\b', r'\bguards\b',
    r'\bscribe\b', r'\bscribes\b',
    r'\bsoldier\b', r'\bsoldiers\b',
    r'\bwarrior\b', r'\bwarriors\b',
    r'\bfamily\b', r'\btribe\b', r'\btribespeople\b',
    r'\belders?\b', r'\bpassengers?\b', r'\bcrowd\b',
    r'\bvillagers?\b', r'\bancestors?\b', r'\bgatherers?\b',
    r'\bworker\b', r'\bworkers\b', r'\blaborers?\b',
    r'\bforagers?\b', r'\bhumans?\b', r'\bhomo\s+sapiens\b',
    r'\bfigure\b', r'\bfigures\b'
]
combined_char_regex = re.compile('|'.join(char_patterns), re.IGNORECASE)

def check_image_cv(img_path):
    if not os.path.exists(img_path):
        return None
    img = cv2.imread(img_path)
    if img is None:
        return None

    h, w, _ = img.shape
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    cy1, cy2 = int(h * 0.10), int(h * 0.90)
    cx1, cx2 = int(w * 0.15), int(w * 0.85)
    crop_hsv = hsv[cy1:cy2, cx1:cx2]
    total_crop_pixels = (cy2 - cy1) * (cx2 - cx1)

    lower_skin1 = np.array([0, 30, 70], dtype=np.uint8)
    upper_skin1 = np.array([25, 200, 255], dtype=np.uint8)
    mask1 = cv2.inRange(crop_hsv, lower_skin1, upper_skin1)

    lower_skin2 = np.array([165, 30, 70], dtype=np.uint8)
    upper_skin2 = np.array([180, 200, 255], dtype=np.uint8)
    mask2 = cv2.inRange(crop_hsv, lower_skin2, upper_skin2)
    skin_mask = cv2.bitwise_or(mask1, mask2)
    skin_ratio = float(np.sum(skin_mask > 0)) / float(total_crop_pixels)

    white_mask = (crop_hsv[:, :, 1] < 25) & (crop_hsv[:, :, 2] > 230)
    white_ratio = float(np.sum(white_mask)) / float(total_crop_pixels)

    ink_mask = crop_hsv[:, :, 2] < 55
    ink_ratio = float(np.sum(ink_mask)) / float(total_crop_pixels)

    return {
        "skin_ratio": round(skin_ratio, 4),
        "white_ratio": round(white_ratio, 4),
        "ink_ratio": round(ink_ratio, 4)
    }

def run_audit():
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))[1:]

    results = []
    for r in rows:
        shot_num = int(r[0])
        tc = r[1]
        vo = r[2]
        desc = r[3]
        prompt = r[4]

        desc_matches = combined_char_regex.findall(desc)
        prompt_matches = combined_char_regex.findall(prompt)
        has_stick_kw = bool(re.search(r'\bstick[\s\-_]?figure', prompt, re.I))
        all_matches = list(set([m.lower() for m in desc_matches + prompt_matches]))
        if all_matches in (['figures'], ['figure']) and not has_stick_kw and 'stick' not in desc.lower():
            all_matches = []

        img_path = os.path.join(IMG_DIR, f"shot_{shot_num:03d}.jpg")
        cv_info = check_image_cv(img_path)

        has_char = len(all_matches) > 0

        if not has_char:
            category = "NO_CHARACTER"
            reason = "Pure object, landscape, map, or scientific anatomical diagram."
            regen_needed = False
        else:
            if has_stick_kw:
                if cv_info and cv_info["skin_ratio"] > 0.08 and cv_info["white_ratio"] < 0.04:
                    category = "NON_STICK_FIGURE"
                    reason = "Prompt requested stick figure, but image contains realistic human anatomy / flesh tones."
                    regen_needed = True
                else:
                    category = "VALID_STICK_FIGURE"
                    reason = "Valid white-filled black-outlined stick figure character present."
                    regen_needed = False
            else:
                category = "NON_STICK_FIGURE"
                reason = f"Character scene ({', '.join(all_matches)}) lacks explicit stick-figure prompt, resulting in realistic human anatomy/flesh tones."
                regen_needed = True

        results.append({
            "shot_num": shot_num,
            "timecode": tc,
            "vo": vo,
            "visual_desc": desc,
            "prompt": prompt,
            "character_keywords": all_matches,
            "has_stick_kw": has_stick_kw,
            "category": category,
            "reason": reason,
            "regen_needed": regen_needed,
            "cv_info": cv_info
        })

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    counts = {}
    for r in results:
        counts[r["category"]] = counts.get(r["category"], 0) + 1

    regen_shots = [r["shot_num"] for r in results if r["regen_needed"]]

    print("=== FINAL CHARACTER AUDIT SUMMARY ===")
    print(f"Total Shots: {len(results)}")
    print(f"Categories: {counts}")
    print(f"Shots Requiring Re-generation: {len(regen_shots)}")
    return results

if __name__ == "__main__":
    run_audit()

