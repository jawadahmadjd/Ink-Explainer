import time
from playwright.sync_api import sync_playwright

prompt_1 = "Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art, flat muted colors, cozy bedroom background with warm beige walls, wooden floor, and wooden bed headboard in the soft background, extreme close-up of a red twin-bell mechanical alarm clock on a wooden nightstand with vibration motion lines, hands pointing to 6:30, full bleed edge-to-edge composition, no borders, no frames, widescreen 16:9 aspect ratio"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]
    
    editor = flow_page.locator(".ProseMirror").first
    editor.click()
    time.sleep(0.3)
    editor.fill(prompt_1)
    time.sleep(1)
    
    # Click generate button
    submit_btn = flow_page.locator('button[aria-label="Start generation"]').first
    submit_btn.click()
    print("Clicked Start Generation!")
    
    # Wait and observe
    for i in range(1, 8):
        time.sleep(3)
        print(f"Elapsed: {i*3}s...")
        flow_page.screenshot(path=f"2- Code/gen_progress_{i*3}s.png")
        
    print("Finished initial wait cycle.")

