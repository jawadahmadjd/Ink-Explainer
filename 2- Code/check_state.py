from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    flow_page = [pg for pg in ctx.pages if "flow.google.com" in pg.url][0]

    btn = flow_page.locator("button.settings-trigger-button").first
    txt = btn.inner_text().encode("ascii", "backslashreplace").decode("ascii")
    print("Button text:", txt)
    flow_page.screenshot(path="2- Code/current_flow_state.png")
    print("Screenshot saved to 2- Code/current_flow_state.png")

