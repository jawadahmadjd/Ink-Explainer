import time
from playwright.sync_api import sync_playwright

target_url = "https://flow.google.com/u/0/project/8a28cfa5-fddf-4528-b188-6deb5ce5e0e5"
prompt_26 = "Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art, stick-figure character with skeptical frowning face and arms crossed stubbornly, flat muted colors, modern apartment living room background with sofa, window, and houseplant, stick figure sitting on sofa with arms crossed looking unconvinced with question marks floating overhead, full bleed edge-to-edge composition, no borders, no frames, widescreen 16:9 aspect ratio"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]
    
    if flow_page.url != target_url:
        flow_page.goto(target_url, wait_until="domcontentloaded")
        time.sleep(2)
        
    editor = flow_page.locator(".ProseMirror").first
    editor.click()
    time.sleep(0.3)
    editor.fill(prompt_26)
    time.sleep(0.8)
    
    submit_btn = flow_page.locator('button[aria-label="Start generation"]').first
    submit_btn.click()
    print("Clicked Start generation for Shot 26...")
    
    for i in range(1, 9):
        time.sleep(3)
        print(f"Elapsed {i*3}s...")
        flow_page.screenshot(path=f"2- Code/shot_26_progress_{i*3}s.png")
        txt = flow_page.evaluate('() => document.body ? document.body.innerText : ""')
        if "limit" in txt.lower() or "try again later" in txt.lower():
            print(f"FAILED: Rate limit hit at {i*3}s!")
            break
            
    print("Test finished!")

