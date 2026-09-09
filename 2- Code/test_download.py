import os
from playwright.sync_api import sync_playwright

os.makedirs("3- Finals/flow_generated_images", exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]
    
    srcs = flow_page.evaluate("""() => {
        const imgs = Array.from(document.querySelectorAll('img'));
        return imgs
            .filter(img => img.src && img.src.includes('flow-content.google'))
            .map(img => img.src);
    }""")
    
    print(f"Found {len(srcs)} image sources.")
    for idx, src in enumerate(srcs, 1):
        resp = flow_page.request.get(src)
        if resp.status == 200:
            out_path = f"3- Finals/flow_generated_images/shot_001_var_{idx}.jpg"
            with open(out_path, "wb") as f:
                f.write(resp.body())
            print(f"Saved {out_path} ({len(resp.body())} bytes)")
        else:
            print(f"Failed to fetch {src}: status {resp.status}")

