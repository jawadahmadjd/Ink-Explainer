import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    ctx = browser.contexts[0]
    flow_page = [pg for pg in ctx.pages if 'flow.google.com' in pg.url][0]
    
    print('Reloading page...')
    flow_page.reload(wait_until='domcontentloaded')
    time.sleep(4)
    flow_page.screenshot(path='2- Code/after_reload.png')
    
    txt = flow_page.evaluate('() => document.body ? document.body.innerText : ""')
    has_limit = 'usage limit' in txt.lower() or 'try again later' in txt.lower()
    print('Has usage limit text after reload?', has_limit)
    if has_limit:
        print('Found usage limit text in body!')
    else:
        print('Canvas is clean after reload!')

