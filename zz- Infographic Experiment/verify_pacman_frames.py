import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

EXPERIMENT_DIR = Path(__file__).resolve().parent
HTML_PLAYER_PATH = EXPERIMENT_DIR / "full_player.html"
OUT_DIR = EXPERIMENT_DIR / "audit_frames_scene3"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TIMESTAMPS = [
    (12.20, "01_post_stamp_12.20s"),
    (13.20, "02_monster_chomping_approach_13.20s"),
    (13.80, "03_instant_of_chomp_13.80s"),
    (14.50, "04_chewing_and_badge_14.50s")
]

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--allow-file-access-from-files"])
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.goto(HTML_PLAYER_PATH.as_uri(), wait_until="networkidle")
        await page.wait_for_timeout(400)

        for t, name in TIMESTAMPS:
            await page.evaluate(f"window.seekTo({t});")
            await page.wait_for_timeout(150)
            await page.screenshot(path=str(OUT_DIR / f"{name}.png"))
            print(f"Captured {name}.png at t={t}s")

        await browser.close()

asyncio.run(capture())
