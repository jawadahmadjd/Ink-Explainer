import os
import time
from playwright.sync_api import sync_playwright

prompts = {
    2: "Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art, stick-figure character with round white head and anxious expressive face, flat muted colors, modern bedroom background with beige wall, wooden nightstand, and bed with crumpled blankets, stick figure sitting up in bed staring closely at a glowing smartphone screen displaying a crowded calendar grid, full bleed edge-to-edge composition, no borders, no frames, widescreen 16:9 aspect ratio",
    3: "Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art, flat muted colors, dark bedroom at night with dark navy blue walls and wooden bedside table, close-up of a bright smartphone screen face-up on a white pillow casting cold blue light across the dark sheets, full bleed edge-to-edge composition, no borders, no frames, widescreen 16:9 aspect ratio"
}

out_dir = "3- Finals/flow_generated_images"
os.makedirs(out_dir, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]
    
    for shot_idx in [2, 3]:
        prompt = prompts[shot_idx]
        print(f"\n==============================")
        print(f"Starting Generation for Shot {shot_idx}...")
        print(f"Prompt: {prompt[:80]}...")
        
        # Count existing flow images before starting
        existing_srcs = set(flow_page.evaluate("""() => {
            return Array.from(document.querySelectorAll('img'))
                .filter(img => img.src && img.src.includes('flow-content.google'))
                .map(img => img.src);
        }"""))
        print(f"Existing images before shot {shot_idx}: {len(existing_srcs)}")
        
        # Focus ProseMirror editor and fill prompt
        editor = flow_page.locator(".ProseMirror").first
        editor.click()
        time.sleep(0.3)
        editor.fill(prompt)
        time.sleep(1)
        
        # Click Generate button
        submit_btn = flow_page.locator('button[aria-label="Start generation"]').first
        submit_btn.click()
        print(f"Clicked generate for Shot {shot_idx}. Waiting for completion...")
        
        # Wait until 4 new images appear and finish loading (check every 3s, max 45s)
        new_srcs = []
        start_time = time.time()
        while time.time() - start_time < 45:
            time.sleep(3)
            current_srcs = flow_page.evaluate("""() => {
                return Array.from(document.querySelectorAll('img'))
                    .filter(img => img.src && img.src.includes('flow-content.google'))
                    .map(img => img.src);
            }""")
            new_srcs = [s for s in current_srcs if s not in existing_srcs]
            print(f"Elapsed {int(time.time() - start_time)}s: found {len(new_srcs)} new images...")
            if len(new_srcs) >= 4:
                # Extra small buffer to ensure 100% final render resolution
                time.sleep(3)
                break
                
        print(f"Shot {shot_idx} finished! Found {len(new_srcs)} new image variations.")
        
        # Download the new images
        for var_idx, src in enumerate(new_srcs[:4], 1):
            resp = flow_page.request.get(src)
            if resp.status == 200:
                out_path = f"{out_dir}/shot_{shot_idx:03d}_var_{var_idx}.jpg"
                with open(out_path, "wb") as f:
                    f.write(resp.body())
                print(f"  -> Saved {out_path} ({len(resp.body())} bytes)")
                
        # Take progress screenshot
        flow_page.screenshot(path=f"2- Code/flow_shot_{shot_idx}_complete.png")

print("\nAll shots 2 and 3 generated and downloaded successfully!")

