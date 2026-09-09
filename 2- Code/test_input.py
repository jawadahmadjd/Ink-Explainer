import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    
    flow_page = None
    for page in ctx.pages:
        if "flow.google.com" in page.url:
            flow_page = page
            break
            
    print("Found page:", flow_page.url)
    
    # Locate ProseMirror editor
    editor = flow_page.locator(".ProseMirror").first
    print("Editor count:", editor.count())
    
    editor.click()
    time.sleep(0.5)
    
    test_text = "Minimalist hand-drawn 2D vector illustration test"
    # In ProseMirror, fill or keyboard.type
    editor.fill(test_text)
    time.sleep(1)
    
    # Check if submit button is enabled
    submit_btn = flow_page.locator('button[aria-label="Start generation"]').first
    is_disabled = submit_btn.get_attribute("disabled") is not None or "disabled" in (submit_btn.get_attribute("class") or "")
    print("Submit button disabled?", is_disabled)
    print("Submit button outerHTML:", submit_btn.evaluate("el => el.outerHTML"))
    
    # Take screenshot
    flow_page.screenshot(path="2- Code/test_input_screenshot.png")
    print("Screenshot saved to 2- Code/test_input_screenshot.png")

