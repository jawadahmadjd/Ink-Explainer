import csv
import os

csv_path = os.path.join('3- Finals', 'storyboard_master.csv')
out_txt = os.path.join('3- Finals', 'all_prompts.txt')
out_raw = os.path.join('3- Finals', 'all_prompts_raw.txt')

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = list(reader)

# 1. Master production prompt book (Shot, Time, VO, Description, Prompt)
with open(out_txt, 'w', encoding='utf-8') as f:
    f.write("================================================================================\n")
    f.write("MASTER IMAGE PROMPTS COMPILATION (334 FULL-BLEED SHOTS)\n")
    f.write("Style: Minimalist Hand-Drawn 2D Comic Vector Line Art (Ink Explainer Style)\n")
    f.write("Target Engine: Google Nano Banana Pro / Imagen 3\n")
    f.write("Aspect Ratio: 16:9 Widescreen (Full Bleed Edge-to-Edge, No Borders, No Frames)\n")
    f.write("================================================================================\n\n")
    
    for row in rows:
        shot_num, timecode, vo, desc, prompt = row
        f.write(f"--- [SHOT {shot_num}] | {timecode} ---\n")
        f.write(f"VO: \"{vo}\"\n")
        f.write(f"Visual: {desc}\n")
        f.write(f"Prompt:\n{prompt}\n\n")

# 2. Raw prompts (pure prompt on each line for batch/bulk generation)
with open(out_raw, 'w', encoding='utf-8') as f:
    for row in rows:
        shot_num, timecode, vo, desc, prompt = row
        f.write(f"{prompt}\n")

print(f"Compiled {len(rows)} shots successfully.")
print(f"1. Formatted book: {out_txt} ({os.path.getsize(out_txt)} bytes)")
print(f"2. Raw line-by-line: {out_raw} ({os.path.getsize(out_raw)} bytes)")

