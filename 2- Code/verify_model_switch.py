import time
from playwright.sync_api import sync_playwright

def switch_flow_model(page, target_model_name):
    print(f"Switching Google Flow model to: {target_model_name}...")
    try:
        page.mouse.click(100, 100)
        time.sleep(0.5)

        settings_btn = page.locator("button.settings-trigger-button").first
        settings_btn.click()
        time.sleep(0.8)

        model_btn = page.locator('button[aria-label="Select model family"]').first
        model_btn.click()
        time.sleep(0.8)

        target_option = page.locator(f'.mat-mdc-menu-panel button:has-text("{target_model_name}")').first
        target_option.click()
        time.sleep(0.8)

        # Ensure x2 is active
        x2_btn = page.locator('button:has-text("x2")').first
        if x2_btn.count() > 0:
            x2_btn.click()
            time.sleep(0.3)

        page.mouse.click(100, 100)
        time.sleep(0.8)
        
        btn_text = settings_btn.inner_text().encode('ascii', 'backslashreplace').decode('ascii')
        print(f"Active settings button: {repr(btn_text)}")
        return True
    except Exception as e:
        print(f"Failed to switch model: {e}")
        page.mouse.click(100, 100)
        return False

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]

    switch_flow_model(flow_page, "Nano Banana Pro")
    time.sleep(1)
    switch_flow_model(flow_page, "Nano Banana 2")
