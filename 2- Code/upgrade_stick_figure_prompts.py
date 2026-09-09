"""
Upgrade Storyboard Master Prompts with Strict Stick-Figure Directives
Standardizes all character prompts to produce white-filled black-outlined
stick figures (MinutePhysics / Casually Explained style) with zero flesh tones.
"""

import csv
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

CSV_PATH = os.path.join(PROJECT_ROOT, "3- Finals", "storyboard_master.csv")
ALL_PROMPTS_TXT = os.path.join(PROJECT_ROOT, "3- Finals", "all_prompts.txt")
AUDIT_JSON = os.path.join(PROJECT_ROOT, "3- Finals", "character_audit.json")

STICK_PREFIX = (
    "Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art. "
    "All human characters are minimalist white-filled black-outlined stick figures with a round white circle head, "
    "pure solid white head fill, clean bold black comic outlines, simple black stick limbs, zero realistic human anatomy, "
    "zero flesh skin tones, zero muscle shading, MinutePhysics animated explainer cartoon style. "
)

def clean_and_stickify_prompt(prompt, desc):
    # Strip existing standard opening
    p = prompt.strip()
    p = re.sub(
        r'^minimalist\s+hand-drawn\s+2d\s+vector\s+illustration,\s*clean\s+bold\s+black\s+ink\s+comic\s+line\s+art[,\.]?\s*',
        '',
        p,
        flags=re.IGNORECASE
    )

    # Replacements for character nouns and realistic attributes
    subs = [
        (r'\bprehistoric\s+stick-figure\s+hunter\s+with\s+wild\s+hair\s+wearing\s+a\s+simple\s+brown\s+fur\s+pelt\b',
         'prehistoric stick figure with round solid white head and simple black stick limbs wearing a flat brown fur pelt shape'),
        (r'\bprehistoric\s+hunter\s+with\s+wild\s+hair\s+wearing\s+a\s+simple\s+brown\s+fur\s+pelt\b',
         'prehistoric stick figure with round solid white head and simple black stick limbs wearing a flat brown fur pelt shape'),
        (r'\bprehistoric\s+stick-figure\s+hunter\b', 'prehistoric stick figure'),
        (r'\bprehistoric\s+hunter\b', 'prehistoric stick figure'),
        (r'\bancient\s+hunter\b', 'ancient stick figure'),
        (r'\bhunters\b', 'stick figures'),
        (r'\bhunter\b', 'stick figure'),
        (r'\bneolithic\s+farmer\b', 'neolithic stick figure'),
        (r'\bfarmers\b', 'stick figures'),
        (r'\bfarmer\b', 'stick figure'),
        (r'\bartists\b', 'stick figures'),
        (r'\bartist\b', 'stick figure'),
        (r'\bgatherers\b', 'stick figures'),
        (r'\bgatherer\b', 'stick figure'),
        (r'\bscribes\b', 'stick-figure scribes'),
        (r'\bscribe\b', 'stick figure scribe'),
        (r'\bkings\b', 'stick-figure kings'),
        (r'\bking\b', 'stick-figure king with simple crown'),
        (r'\bguards\b', 'stick-figure guards with spears'),
        (r'\bguard\b', 'stick figure guard with spear'),
        (r'\bwarriors\b', 'stick figures'),
        (r'\bwarrior\b', 'stick figure'),
        (r'\bsoldiers\b', 'stick figures'),
        (r'\bsoldier\b', 'stick figure'),
        (r'\bvillagers\b', 'stick figures'),
        (r'\belders\b', 'stick-figure elders'),
        (r'\bpassengers\b', 'stick-figure passengers'),
        (r'\bancestors\b', 'stick figures'),
        (r'\bfamily\b', 'stick-figure family'),
        (r'\bchildren\b', 'stick-figure children'),
        (r'\bchild\b', 'stick-figure child'),
        (r'\bmodern\s+worker\b', 'modern stick figure'),
        (r'\bworker\b', 'stick figure'),
        (r'\bperson\b', 'stick figure'),
        (r'\bpeople\b', 'stick figures'),
        (r'\ba\s+man\b', 'a stick figure'),
        (r'\bmen\b', 'stick figures'),
        (r'\bwoman\b', 'stick figure'),
        (r'\bwomen\b', 'stick figures'),
        (r'\bwith\s+wild\s+hair\b', ''),
        (r'\bmuscular\s+arms\b', 'stick arms'),
        (r'\bmuscular\s+legs\b', 'stick legs'),
        (r'\bmuscular\b', ''),
        (r'\bhuman\s+figures\b', 'stick figures'),
        (r'\bhuman\s+figure\b', 'stick figure')
    ]

    for pat, rep in subs:
        p = re.sub(pat, rep, p, flags=re.IGNORECASE)

    # Clean double spaces
    p = re.sub(r'\s+', ' ', p).strip()

    # Prepend strict directive
    full_prompt = f"{STICK_PREFIX}{p}"
    return full_prompt

def main():
    with open(AUDIT_JSON, "r", encoding="utf-8") as f:
        audit_records = json.load(f)

    audit_map = {d["shot_num"]: d for d in audit_records}

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))

    header = reader[0]
    data_rows = reader[1:]

    updated_rows = []
    upgraded_count = 0

    for row in data_rows:
        shot_num = int(row[0])
        tc = row[1]
        vo = row[2]
        desc = row[3]
        prompt = row[4]

        audit_entry = audit_map.get(shot_num, {})
        category = audit_entry.get("category", "NO_CHARACTER")
        regen_needed = audit_entry.get("regen_needed", False)

        if regen_needed or category in ("NON_STICK_FIGURE", "VALID_STICK_FIGURE"):
            new_prompt = clean_and_stickify_prompt(prompt, desc)
            updated_rows.append([shot_num, tc, vo, desc, new_prompt])
            upgraded_count += 1
        else:
            # Preserved as-is (pure object, landscape, diagram, map)
            updated_rows.append([shot_num, tc, vo, desc, prompt])

    # Save upgraded storyboard_master.csv
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(updated_rows)

    print(f"Successfully upgraded {upgraded_count} character prompts in {CSV_PATH}!")

    # Update all_prompts.txt
    with open(ALL_PROMPTS_TXT, "w", encoding="utf-8") as f:
        for row in updated_rows:
            shot_num = row[0]
            tc = row[1]
            vo = row[2]
            desc = row[3]
            prompt = row[4]
            f.write(f"=== SHOT {shot_num:03d} | {tc} ===\n")
            f.write(f"VO: {vo}\n")
            f.write(f"Visual: {desc}\n")
            f.write(f"Prompt: {prompt}\n")
            f.write(f"[STATUS: QUEUED_FOR_REGEN]\n\n" if audit_map.get(shot_num, {}).get("regen_needed") else f"[STATUS: COMPLETED]\n\n")

    print(f"Updated {ALL_PROMPTS_TXT} with synchronized prompts!")

if __name__ == "__main__":
    main()
