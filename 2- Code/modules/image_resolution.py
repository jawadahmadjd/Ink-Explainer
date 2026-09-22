"""
Image Resolution & 2K Management Engine for Ink Explainer Autonomous Studio
Handles Google Flow native 2K upscaled downloads, high-fidelity Lanczos 2K processing,
single-shot 2K attachments, and complete project 2K zip packaging.
"""

import os
import sys
import io
import time
import zipfile
import shutil
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

TARGET_2K_WIDTH = getattr(config, "TARGET_2K_WIDTH", 2752)
TARGET_2K_HEIGHT = getattr(config, "TARGET_2K_HEIGHT", 1536)

def get_image_dimensions(image_path: str) -> tuple[int, int]:
    """Returns (width, height) for an image file without loading all pixels."""
    if not image_path or not os.path.exists(image_path):
        return 0, 0
    try:
        with Image.open(image_path) as im:
            return im.size
    except Exception:
        return 0, 0

def ensure_2k_image(source_path: str, dest_path: str = None, target_w: int = 2752, target_h: int = 1536) -> tuple[str, int, int]:
    """
    Ensures the image at source_path is at least 2K resolution (2752x1536 / 2560x1440).
    If already >= 2000px wide, leaves or copies as-is.
    If below 2000px, resamples using anti-aliased Lanczos with pure white (#FFFFFF)
    background preservation and subtle unsharp edge enhancement for crisp ink lines.
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source image not found: {source_path}")

    out_path = dest_path or source_path
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    with Image.open(source_path) as im:
        w, h = im.size
        # If already at or above 2K width, keep high quality
        if w >= 2500 and h >= 1400:
            if out_path != source_path:
                shutil.copyfile(source_path, out_path)
            return out_path, w, h

        # Calculate high-quality 2K dimensions (maintaining 16:9)
        ratio = w / max(1, h)
        target_ratio = target_w / target_h

        # Direct 16:9 resize or fit with pure white background
        if abs(ratio - target_ratio) < 0.05:
            resized = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
        else:
            # Fit inside canvas and pad with pure white #FFFFFF
            fit_scale = min(target_w / w, target_h / h)
            new_w = int(round(w * fit_scale))
            new_h = int(round(h * fit_scale))
            scaled = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
            resized = Image.new("RGB", (target_w, target_h), (255, 255, 255))
            paste_x = (target_w - new_w) // 2
            paste_y = (target_h - new_h) // 2
            resized.paste(scaled, (paste_x, paste_y))

        # Apply subtle edge preservation for ink linework
        try:
            enhanced = resized.filter(ImageFilter.UnsharpMask(radius=1.2, percent=105, threshold=3))
        except Exception:
            enhanced = resized

        # Save with maximum broadcast JPEG quality
        if enhanced.mode != "RGB":
            enhanced = enhanced.convert("RGB")
        enhanced.save(out_path, format="JPEG", quality=98, subsampling=0)
        return out_path, target_w, target_h

def pull_single_shot_2k_from_flow(video_title: str, shot_num: int, timeout: int = 30000) -> dict:
    """
    Connects to active Chrome Google Flow tab, clicks the generated image,
    triggers native '2K (Upscaled)' download, and replaces the shot image.
    """
    from playwright.sync_api import sync_playwright
    from modules.stage4_image_gen import download_flow_image_2k

    dirs = config.get_project_dirs(video_title)
    final_img_dir = dirs["final_images_dir"]
    raw_img_dir = dirs["raw_images_dir"]
    final_path = os.path.join(final_img_dir, f"shot_{shot_num:03d}.jpg")

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
                        break
                if browser: break
            except Exception:
                continue

        if not browser:
            raise ConnectionError("Google Flow tab not found in Chrome. Please ensure flow.google.com is open on port 9222.")

        flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]
        flow_page.bring_to_front()

        success = download_flow_image_2k(flow_page, dest_path=final_path, timeout=timeout)
        if not success or not os.path.exists(final_path):
            raise RuntimeError("Failed to trigger 2K download from Google Flow.")

        # Also copy to root junction if present
        root_final = os.path.join(config.ROOT_CANONICAL_IMAGES_DIR, f"shot_{shot_num:03d}.jpg")
        if os.path.exists(config.ROOT_CANONICAL_IMAGES_DIR):
            shutil.copyfile(final_path, root_final)

        w, h = get_image_dimensions(final_path)
        return {
            "success": True,
            "shot_num": shot_num,
            "path": final_path,
            "width": w,
            "height": h,
            "is_2k": (w >= 2000),
            "size_bytes": os.path.getsize(final_path)
        }

def build_project_2k_zip(video_title: str) -> tuple[io.BytesIO, str, int]:
    """
    Bundles all final selected images for the project in 2K resolution into a zip file.
    Returns (BytesIO_buffer, zip_filename, count).
    """
    dirs = config.get_project_dirs(video_title)
    final_img_dir = dirs["final_images_dir"]

    if not os.path.exists(final_img_dir):
        raise FileNotFoundError(f"Final images directory not found for '{video_title}'")

    img_files = sorted([
        f for f in os.listdir(final_img_dir)
        if f.lower().startswith("shot_") and f.lower().endswith((".jpg", ".png", ".jpeg"))
    ])

    if not img_files:
        raise FileNotFoundError(f"No generated shot images found in '{final_img_dir}'")

    zip_buffer = io.BytesIO()
    clean_name = config.sanitize_title(dirs["title"]).replace(" ", "_")
    zip_filename = f"{clean_name}_2K_Images.zip"

    # Temporary cache dir for processed 2K images
    cache_2k_dir = os.path.join(dirs["finals_dir"], "Final selected images 2K")
    os.makedirs(cache_2k_dir, exist_ok=True)

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in img_files:
            src_full = os.path.join(final_img_dir, fname)
            cached_2k = os.path.join(cache_2k_dir, fname)

            # Check if source is already >= 2K
            w, h = get_image_dimensions(src_full)
            if w >= 2500 and h >= 1400:
                zf.write(src_full, arcname=f"2K_Images/{fname}")
            else:
                # Ensure 2K upscaled
                ensure_2k_image(src_full, cached_2k)
                zf.write(cached_2k, arcname=f"2K_Images/{fname}")

    zip_buffer.seek(0)
    return zip_buffer, zip_filename, len(img_files)

