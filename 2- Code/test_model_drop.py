import json
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]

    flow_page.mouse.click(100, 100)
    time.sleep(0.5)

    # Click settings button
    settings_btn = flow_page.locator("button.settings-trigger-button").first
    settings_btn.click()
    time.sleep(1)

    # Click model trigger button
    model_btn = flow_page.locator('button[aria-label="Select model family"]').first
    model_btn.click()
    time.sleep(1)

    flow_page.screenshot(path="2- Code/model_dropdown_open.png")
    print("Saved model_dropdown_open.png")

    menu_items = flow_page.evaluate("""() => {
        return Array.from(document.querySelectorAll('.mat-mdc-menu-panel button, [role="menuitem"]')).map(b => ({
            text: (b.innerText || '').trim(),
            aria: b.getAttribute('aria-label') || '',
            cls: b.className || ''
        }));
    }""")
    print("Found menu items count:", len(menu_items))
    for m in menu_items:
        txt = m['text'].encode('ascii', 'backslashreplace').decode('ascii')
        print("  Item:", repr(txt))

    flow_page.mouse.click(100, 100)
