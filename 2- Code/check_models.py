import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]

    btn = flow_page.locator("button.settings-trigger-button").first
    print("Found settings button:", btn.count())
    if btn.count() > 0:
        btn.click()
        time.sleep(1.5)
        flow_page.screenshot(path="2- Code/model_settings_menu.png")
        print("Saved screenshot to 2- Code/model_settings_menu.png")
        
        # Click outside to close
        flow_page.mouse.click(200, 200)

