import time
from playwright.sync_api import sync_playwright

target_url = "https://flow.google.com/u/0/project/8a28cfa5-fddf-4528-b188-6deb5ce5e0e5"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    
    flow_page = None
    for page in ctx.pages:
        if "flow.google.com" in page.url:
            flow_page = page
            break
            
    if not flow_page:
        flow_page = ctx.new_page()
        flow_page.goto(target_url)
    elif flow_page.url != target_url:
        flow_page.goto(target_url)

    flow_page.wait_for_load_state("domcontentloaded")
    time.sleep(3)
    
    print("Page Title:", flow_page.title())
    print("Page URL:", flow_page.url)
    
    # Save a screenshot to inspect UI
    flow_page.screenshot(path="2- Code/flow_screenshot.png")
    print("Saved screenshot to 2- Code/flow_screenshot.png")
    
    # Dump key elements (inputs, textareas, contenteditable, buttons)
    elements = flow_page.evaluate('''() => {
        const results = [];
        const query = 'textarea, input, [contenteditable="true"], button, [role="button"]';
        document.querySelectorAll(query).forEach((el, idx) => {
            const rect = el.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {
                results.push({
                    tag: el.tagName.toLowerCase(),
                    type: el.getAttribute('type') || '',
                    role: el.getAttribute('role') || '',
                    ariaLabel: el.getAttribute('aria-label') || '',
                    placeholder: el.getAttribute('placeholder') || '',
                    text: (el.innerText || '').trim().substring(0, 50),
                    className: (el.className || '').toString().substring(0, 50),
                    id: el.id || '',
                    rect: {x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.w), h: Math.round(rect.h)}
                });
            }
        });
        return results;
    }''')
    
    print(f"Found {len(elements)} visible interactive elements:")
    for el in elements:
        print(f"  Tag: {el['tag']}, Type: {el['type']}, Role: {el['role']}, Aria: '{el['ariaLabel']}', Placeholder: '{el['placeholder']}', Text: '{el['text']}', Rect: {el['rect']}")

