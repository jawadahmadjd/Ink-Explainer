import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]

    # Open settings
    flow_page.locator("button.settings-trigger-button").first.click()
    time.sleep(1)
    
    # Click model dropdown
    flow_page.locator(".cdk-overlay-container button:has-text('Nano Banana')").first.click()
    time.sleep(1)
    
    # Click 'Nano Banana 2'
    nb2_option = flow_page.locator(".cdk-overlay-container button:has-text('Nano Banana 2')").first
    if nb2_option.count() > 0:
        nb2_option.click()
        time.sleep(1)
        flow_page.screenshot(path="2- Code/nb2_selected.png")
        txt = flow_page.evaluate('''() => {
            const el = document.querySelector('.cdk-overlay-container');
            return el ? el.innerText : '';
        }''')
        print("Nano Banana 2 info:\n", txt)
        
    flow_page.mouse.click(100, 100)

