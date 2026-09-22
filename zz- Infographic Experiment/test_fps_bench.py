import time
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def benchmark():
    exp_dir = Path(r"d:\Tools of Jawad\25- Ink Explainers\zz- Infographic Experiment")
    player_path = exp_dir / "full_player.html"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.goto(player_path.as_uri())
        await page.wait_for_timeout(500)

        # Benchmark 20 frames
        t0 = time.time()
        for i in range(20):
            t = i * (1.0 / 30.0)
            await page.evaluate(f"window.seekTo({t});")
            # screenshot
            _ = await page.locator("#viewport-container").screenshot(type="jpeg", quality=90)
        dur = time.time() - t0
        print(f"20 frames took {dur:.2f}s ({dur/20:.3f}s per frame, ~{20/dur:.1f} fps)")
        await browser.close()

asyncio.run(benchmark())
