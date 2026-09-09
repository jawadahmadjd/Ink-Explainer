import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]
    
    tiles = flow_page.evaluate('''() => {
        const imgs = Array.from(document.querySelectorAll('img'));
        return imgs.map(img => ({
            src: img.src ? img.src.substring(0, 150) : '',
            alt: img.alt || '',
            className: img.className || '',
            width: img.naturalWidth || img.width,
            height: img.naturalHeight || img.height,
            parentClass: img.parentElement ? img.parentElement.className : ''
        }));
    }''')
    
    print("Found images:", len(tiles))
    for t in tiles:
        print(t)

