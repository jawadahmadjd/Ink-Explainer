import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]

    # Click the PRO badge
    pro_btn = flow_page.locator("div[role='button']:has-text('PRO')").first
    if pro_btn.count() > 0:
        pro_btn.click()
        time.sleep(1.5)
        flow_page.screenshot(path="2- Code/account_details.png")
        print("Clicked PRO button, saved screenshot.")
        
        # Read popup text
        txt = flow_page.evaluate('''() => {
            const el = document.querySelector('.cdk-overlay-container, mat-dialog-container, [role=\"dialog\"]');
            return el ? el.innerText : 'No dialog found';
        }''')
        print("Dialog text:\n", txt)
        
        flow_page.mouse.click(100, 100)
    else:
        print("PRO button not found.")

