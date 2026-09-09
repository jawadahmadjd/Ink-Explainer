import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    
    flow_page = None
    for page in ctx.pages:
        if "flow.google.com" in page.url:
            flow_page = page
            break
            
    info = flow_page.evaluate('''() => {
        // Find elements near the bottom prompt area
        const container = document.querySelector('div[class*="prompt"], div[class*="input"], footer') || document.body;
        
        // Find any element containing "What do you want to create"
        let promptInput = null;
        const all = document.querySelectorAll('*');
        for (const el of all) {
            if ((el.placeholder && el.placeholder.includes('create')) || 
                (el.innerText && el.innerText.includes('What do you want to create')) ||
                (el.getAttribute('aria-label') && el.getAttribute('aria-label').includes('create'))) {
                promptInput = el;
            }
        }
        
        // Find submit button
        const buttons = Array.from(document.querySelectorAll('button'));
        const buttonDetails = buttons.map(b => ({
            text: b.innerText,
            ariaLabel: b.getAttribute('aria-label'),
            className: b.className,
            html: b.outerHTML.substring(0, 150)
        }));
        
        return {
            inputTag: promptInput ? promptInput.tagName : null,
            inputClass: promptInput ? promptInput.className : null,
            inputHtml: promptInput ? promptInput.outerHTML.substring(0, 300) : null,
            buttons: buttonDetails
        };
    }''')
    
    with open("2- Code/prompt_box_info.json", "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
    print("Dumped prompt box info!")

