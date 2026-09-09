import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]

    # Reload canvas to clear any error state
    flow_page.reload(wait_until="domcontentloaded")
    time.sleep(3)

    # Click settings trigger
    settings_btn = flow_page.locator("button.settings-trigger-button").first
    if settings_btn.count() > 0:
        settings_btn.click()
        time.sleep(1)
        
        # Click the model dropdown button inside the settings menu
        dropdown_btn = flow_page.locator(".cdk-overlay-container button:has-text('Nano Banana')").first
        if dropdown_btn.count() > 0:
            dropdown_btn.click()
            time.sleep(1)
            flow_page.screenshot(path="2- Code/available_models.png")
            
            # Extract options
            options = flow_page.evaluate('''() => {
                const els = Array.from(document.querySelectorAll('.cdk-overlay-container [role=\"option\"], .cdk-overlay-container [role=\"menuitem\"], .cdk-overlay-container button'));
                return els.map(e => e.innerText.trim()).filter(t => t.length > 0);
            }''')
            print("Available models / options:")
            for opt in set(options):
                print(" -", repr(opt))
        else:
            print("Model dropdown button not found in overlay.")
    else:
        print("Settings trigger button not found.")
        
    flow_page.mouse.click(100, 100)

