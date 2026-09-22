import os
import re
import math
import time
import shutil
import asyncio
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

EXP_DIR = Path(__file__).resolve().parent
EXPORT_HTML = EXP_DIR / "export_player.html"
FRAMES_DIR = EXP_DIR / "temp_export_frames"
AUDIO_PATH = EXP_DIR / "what-happens-if-you-take-five-.wav"
OUTPUT_MP4 = EXP_DIR / "The_5_Dollar_Daily_Habit.mp4"

FPS = 30
TOTAL_DURATION = 26.855 # Exact duration from director storyboard
TOTAL_FRAMES = int(math.ceil(TOTAL_DURATION * FPS))
NUM_WORKERS = 4

def generate_export_html():
    """Generates a clean, 1920x1080 borderless canvas page for pristine frame capture."""
    with open(EXP_DIR / "character_library.js", "r", encoding="utf-8") as f:
        c_lib = f.read()
        c_lib = re.sub(r"export\s+const\s+", "const ", c_lib)
        c_lib = re.sub(r"export\s+function\s+", "function ", c_lib)

    c1 = f"""// --- MASTER CHARACTER SKELETAL RIG ---
{c_lib}
function renderCharacter(options = {{}}) {{
  return renderMasterCharacter(options);
}}
"""

    with open(EXP_DIR / "agent2_scene.js", "r", encoding="utf-8") as f:
        c2 = f.read().replace("export function renderSceneEnvironment", "function renderSceneEnvironment")

    with open(EXP_DIR / "orchestrator_engine.js", "r", encoding="utf-8") as f:
        c_orch = f.read()
        c_orch = re.sub(r"import\s+.*?;\n?", "", c_orch)
        c_orch = c_orch.replace("export const SPATIAL_ZONES", "const SPATIAL_ZONES")
        c_orch = c_orch.replace("export function getQuadraticBezierPointAndTangent", "function getQuadraticBezierPointAndTangent")
        c_orch = c_orch.replace("export const CHUNKED_SUBTITLES", "const CHUNKED_SUBTITLES")
        c_orch = c_orch.replace("export function renderChunkedCaptions", "function renderChunkedCaptions")

    with open(EXP_DIR / "agent5_continuity.js", "r", encoding="utf-8") as f:
        c5 = f.read()
        for exp in ["export function easeInOutCubic", "export function easeOutBack", "export function clamp", "export function lerp", "export function getContinuityState"]:
            c5 = c5.replace(exp, exp.replace("export ", ""))

    with open(EXP_DIR / "scene2_scene5_assets.js", "r", encoding="utf-8") as f:
        c_scenes = f.read()
        c_scenes = re.sub(r"import\s+.*?;\n?", "", c_scenes)
        for exp in ["export function formatCurrency", "export function renderScene2", "export function renderScene3", "export function renderScene4", "export function renderScene5"]:
            c_scenes = c_scenes.replace(exp, exp.replace("export ", ""))

    with open(EXP_DIR / "scene1_animator.js", "r", encoding="utf-8") as f:
        c_anim1 = f.read()
        c_anim1 = re.sub(r"import\s+.*?;\n?", "", c_anim1)
        c_anim1 = c_anim1.replace("export function computeScene1Frame", "function computeScene1Frame")

    with open(EXP_DIR / "master_timeline_engine.js", "r", encoding="utf-8") as f:
        c_master = f.read()
        c_master = re.sub(r"import\s+.*?;\n?", "", c_master)
        c_master = c_master.replace("export function computeMasterFrame", "function computeMasterFrame")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Infographics Video Exporter</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{
      width: 1920px;
      height: 1080px;
      overflow: hidden;
      background: #020617;
    }}
    #stage {{
      width: 1920px;
      height: 1080px;
      display: block;
    }}
  </style>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800;900&family=Poppins:wght@600;700;800&family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
</head>
<body>
  <div id="stage"></div>
  <script>
    {c1}
    {c2}
    {c_orch}
    {c5}
    {c_scenes}
    {c_anim1}
    {c_master}

    const stageElem = document.getElementById('stage');
    window.renderFrameAtTime = function(t) {{
      stageElem.innerHTML = computeMasterFrame(t);
    }};
  </script>
</body>
</html>"""

    with open(EXPORT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print("Generated export_player.html")

async def worker_render_chunk(browser, worker_id, start_idx, end_idx):
    """Renders a range of frames in its own dedicated Playwright page."""
    page = await browser.new_page(viewport={"width": 1920, "height": 1080})
    await page.goto(EXPORT_HTML.as_uri(), wait_until="networkidle")
    await page.wait_for_timeout(800) # Wait for web fonts

    count = end_idx - start_idx
    print(f"[Worker {worker_id}] Starting frames {start_idx} to {end_idx - 1} ({count} frames)...")

    for idx in range(start_idx, end_idx):
        t = idx / float(FPS)
        await page.evaluate(f"window.renderFrameAtTime({t:.4f});")
        frame_file = FRAMES_DIR / f"frame_{idx:05d}.jpg"
        await page.screenshot(path=str(frame_file), type="jpeg", quality=96)

        if (idx - start_idx + 1) % 50 == 0 or idx == end_idx - 1:
            progress = ((idx - start_idx + 1) / count) * 100
            print(f"[Worker {worker_id}] Progress: {idx - start_idx + 1}/{count} ({progress:.1f}%)")

    await page.close()
    print(f"[Worker {worker_id}] Finished!")

async def capture_all_frames():
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    generate_export_html()

    print(f"\n--- Starting Parallel Frame Capture: {TOTAL_FRAMES} frames @ {FPS} fps ({TOTAL_DURATION}s) ---")
    chunk_size = math.ceil(TOTAL_FRAMES / NUM_WORKERS)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--allow-file-access-from-files", "--disable-web-security"]
        )

        tasks = []
        for i in range(NUM_WORKERS):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, TOTAL_FRAMES)
            if start < end:
                tasks.append(worker_render_chunk(browser, i, start, end))

        t0 = time.time()
        await asyncio.gather(*tasks)
        total_time = time.time() - t0
        print(f"\nFrame capture complete! Rendered {TOTAL_FRAMES} frames in {total_time:.2f}s ({TOTAL_FRAMES / total_time:.1f} fps).")

        await browser.close()

def encode_mp4():
    """Muxes frames and original voiceover audio into high-fidelity H.264 MP4."""
    print("\n--- Encoding MP4 with FFmpeg ---")
    input_pattern = str(FRAMES_DIR / "frame_%05d.jpg")
    
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", input_pattern,
        "-i", str(AUDIO_PATH),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(OUTPUT_MP4)
    ]

    print(f"Running command: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)

    if res.returncode != 0:
        print("FFmpeg Error:\n", res.stderr)
        raise RuntimeError("FFmpeg encoding failed!")

    file_size_mb = OUTPUT_MP4.stat().st_size / (1024 * 1024)
    print(f"\nSUCCESS! Exported MP4:")
    print(f"File: {OUTPUT_MP4}")
    print(f"Size: {file_size_mb:.2f} MB")
    print(f"Duration: {TOTAL_DURATION}s @ {FPS} fps, 1920x1080 Full HD")

def cleanup():
    print("Cleaning up temporary frame cache...")
    shutil.rmtree(FRAMES_DIR, ignore_errors=True)
    if EXPORT_HTML.exists():
        EXPORT_HTML.unlink()
    print("Cleanup complete.")

if __name__ == "__main__":
    asyncio.run(capture_all_frames())
    encode_mp4()
    cleanup()
