import argparse
import csv
import os
import sys
import time
from playwright.sync_api import sync_playwright

def run_batch(start_shot=1, end_shot=334, max_wait=45):
    csv_path = os.path.join("3- Finals", "storyboard_master.csv")
    out_dir = os.path.join("3- Finals", "flow_generated_images")
    os.makedirs(out_dir, exist_ok=True)

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        all_rows = list(reader)

    # Filter rows by range
    target_rows = [r for r in all_rows if start_shot <= int(r[0]) <= end_shot]
    print(f"Targeting {len(target_rows)} shots (Shots {start_shot} to {end_shot})...")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx = browser.contexts[0]
        flow_pages = [pg for pg in ctx.pages if "flow.google.com" in pg.url]
        if not flow_pages:
            print("Error: No Google Flow tab found in connected Chrome browser.")
            return
        flow_page = flow_pages[0]

        for row in target_rows:
            shot_num = int(row[0])
            vo_text = row[2]
            prompt = row[4]

            # Check if this shot already has downloaded images
            existing_files = [f for f in os.listdir(out_dir) if f.startswith(f"shot_{shot_num:03d}_var_")]
            if len(existing_files) >= 4:
                print(f"[SKIP] Shot {shot_num:03d} already has {len(existing_files)} images.")
                continue

            print(f"\n==================================================")
            print(f"Generating Shot {shot_num:03d} / {len(all_rows)}")
            print(f"VO: \"{vo_text}\"")
            print(f"Prompt: {prompt[:90]}...")

            # Snapshot existing images
            existing_srcs = set(flow_page.evaluate("""() => {
                return Array.from(document.querySelectorAll('img'))
                    .filter(img => img.src && img.src.includes('flow-content.google'))
                    .map(img => img.src);
            }"""))

            # Fill prompt
            editor = flow_page.locator(".ProseMirror").first
            editor.click()
            time.sleep(0.2)
            editor.fill(prompt)
            time.sleep(0.8)

            # Click generate
            submit_btn = flow_page.locator('button[aria-label="Start generation"]').first
            submit_btn.click()
            print(f"Clicked Generate. Waiting for render...")

            # Wait for 4 new images
            start_t = time.time()
            new_srcs = []
            while time.time() - start_t < max_wait:
                time.sleep(2.5)
                current_srcs = flow_page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('img'))
                        .filter(img => img.src && img.src.includes('flow-content.google'))
                        .map(img => img.src);
                }""")
                new_srcs = [s for s in current_srcs if s not in existing_srcs]
                if len(new_srcs) >= 4:
                    time.sleep(2.0)
                    break

            print(f"Render complete! Downloading {len(new_srcs[:4])} variations...")
            for var_idx, src in enumerate(new_srcs[:4], 1):
                resp = flow_page.request.get(src)
                if resp.status == 200:
                    dest = os.path.join(out_dir, f"shot_{shot_num:03d}_var_{var_idx}.jpg")
                    with open(dest, "wb") as f_out:
                        f_out.write(resp.body())
                    print(f"  -> Saved {dest} ({len(resp.body()):,} bytes)")
                else:
                    print(f"  -> Failed download ({resp.status}): {src[:60]}")

            # Brief pause between shots to prevent browser memory bloat
            time.sleep(1.5)

    print("\nBatch generation complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1, help="Start shot number")
    parser.add_argument("--end", type=int, default=334, help="End shot number")
    args = parser.parse_args()
    run_batch(start_shot=args.start, end_shot=args.end)

