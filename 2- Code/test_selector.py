import os
import cv2
import numpy as np
from PIL import Image

def analyze_and_score_variation(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return -1, "Failed to load image"

    h, w, _ = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Edge & Linework Sharpness (Laplacian variance) - Ink line art quality
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    sharpness_score = min(100.0, laplacian_var / 15.0)

    # 2. Full-bleed border penalty (check if border has white framing)
    top_strip = gray[:int(h*0.02), :]
    bot_strip = gray[int(h*0.98):, :]
    left_strip = gray[:, :int(w*0.02)]
    right_strip = gray[:, int(w*0.98):]
    border_pixels = np.concatenate([top_strip.flatten(), bot_strip.flatten(), left_strip.flatten(), right_strip.flatten()])
    border_mean = np.mean(border_pixels)
    border_std = np.std(border_pixels)
    border_penalty = 0
    if border_mean > 240 and border_std < 10:
        border_penalty = 50.0

    # 3. Subject prominence (Center vs periphery contrast)
    center_y, center_x = int(h*0.2), int(w*0.2)
    center_crop = gray[center_y:int(h*0.8), center_x:int(w*0.8)]
    center_std = np.std(center_crop)
    center_score = min(100.0, center_std * 1.5)

    # 4. Value Dynamic Range (ink contrast between dark lines and muted fills)
    p5 = np.percentile(gray, 5)
    p95 = np.percentile(gray, 95)
    dynamic_range = p95 - p5
    contrast_score = min(100.0, (dynamic_range / 200.0) * 100.0)

    # 5. Information Entropy (detail richness)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist = hist / hist.sum()
    entropy = -np.sum([p * np.log2(p) for p in hist.flatten() if p > 0])
    entropy_score = min(100.0, (entropy / 7.5) * 100.0)

    # Composite Score (weighted)
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
    return total_score, details

# Test on shots 1, 2, 3
for shot in [1, 2, 3]:
    print(f"\n--- Shot {shot} Analysis ---")
    best_score = -1
    best_var = 1
    for var in range(1, 5):
        path = f"3- Finals/flow_generated_images/shot_{shot:03d}_var_{var}.jpg"
        score, details = analyze_and_score_variation(path)
        print(f"Var {var}: Total Score = {score} | {details}")
        if score > best_score:
            best_score = score
            best_var = var
    print(f"-> Selected Best for Shot {shot}: Variation {best_var} (Score: {best_score})")

