import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]

    elements = flow_page.evaluate("""() => {
        const container = document.querySelector('.cdk-overlay-container');
        if (!container) return [];
        return Array.from(container.querySelectorAll('*')).map(el => {
            const rect = el.getBoundingClientRect();
            if (rect.width === 0 || rect.height === 0) return null;
            return {
                tag: el.tagName.toLowerCase(),
                id: el.id,
                cls: el.className,
                aria: el.getAttribute('aria-label') || '',
                role: el.getAttribute('role') || '',
                text: (el.innerText || '').trim().substring(0, 50),
                rect: {x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.w), h: Math.round(rect.h)}
            };
        }).filter(Boolean);
    }""")

    with open("2- Code/overlay_elements.json", "w", encoding="utf-8") as f:
        json.dump(elements, f, indent=2)

    print(f"Dumped {len(elements)} overlay elements to 2- Code/overlay_elements.json")
