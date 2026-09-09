import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]

    # Reset
    flow_page.mouse.click(100, 100)
    time.sleep(1)

    # Click settings button
    settings_btn = flow_page.locator("button.settings-trigger-button").first
    settings_btn.click()
    time.sleep(1.5)

    flow_page.screenshot(path="2- Code/menu_state.png")
    print("Saved menu_state.png")

    btns = flow_page.evaluate("""() => {
        return Array.from(document.querySelectorAll('button')).map(b => ({
            text: (b.innerText || '').trim().substring(0, 40),
            aria: b.getAttribute('aria-label') || '',
            cls: b.className || '',
            tag: b.tagName
        })).filter(b => b.text || b.aria);
    }""")
    
    for idx, b in enumerate(btns):
        print(f"[{idx}] Text: {repr(b['text'])} | Aria: {repr(b['aria'])} | Class: {b['cls'][:30]}")

    flow_page.mouse.click(100, 100)
