import time
from playwright.sync_api import sync_playwright

def switch_model_test(model_name):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx = browser.contexts[0]
        flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]

        print(f"Attempting switch to {model_name}...")
        settings_btn = flow_page.locator("button.settings-trigger-button").first
        settings_btn.click()
        time.sleep(1)

        # Open model dropdown inside menu
        dropdown_btn = flow_page.locator(".cdk-overlay-container button:has-text('Nano Banana')").first
        dropdown_btn.click()
        time.sleep(1)

        # Select target model
        target_opt = flow_page.locator(f".cdk-overlay-container button:has-text('{model_name}')").first
        if target_opt.count() > 0:
            target_opt.click()
            time.sleep(1)
            print(f"Successfully clicked option for {model_name}!")
        else:
            print(f"Option for {model_name} not found!")

        # Close overlay
        flow_page.mouse.click(100, 100)
        time.sleep(1)
        
        btn_text = flow_page.locator("button.settings-trigger-button").first.inner_text().encode("ascii", "backslashreplace").decode("ascii")
        print("Updated settings button text:\n", btn_text)

if __name__ == "__main__":
    # Test switching to Nano Banana 2 Lite or Nano Banana 2
    switch_model_test("Nano Banana 2")

