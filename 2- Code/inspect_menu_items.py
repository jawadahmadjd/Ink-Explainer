import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]

    # Reset any open menu
    flow_page.mouse.click(100, 100)
    time.sleep(0.5)

    # Click settings button
    settings_btn = flow_page.locator("button.settings-trigger-button").first
    settings_btn.click()
    time.sleep(0.8)

    # Click model trigger
    model_trigger = flow_page.locator('button[aria-label="Select model family"]').first
    model_trigger.click()
    time.sleep(0.8)

    # Dump all menuitems
    menu_items = flow_page.locator('[role="menuitem"]').all()
    print(f"Found {len(menu_items)} menuitems:")
    for idx, item in enumerate(menu_items):
        txt = item.inner_text().strip().replace("\n", " ").encode("ascii", "backslashreplace").decode("ascii")
        print(f"  [{idx}] {repr(txt)}")

    flow_page.mouse.click(100, 100)
