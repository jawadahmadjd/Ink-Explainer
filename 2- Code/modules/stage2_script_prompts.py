"""
Stage 2: Script Preparation & Stick-Figure Storyboard Prompt Compilation
Aligns spoken script to shot cuts, applies strict MinutePhysics stick-figure rules,
and compiles storyboard_master.csv, all_prompts.txt, and character_audit.json.
"""

import os
import sys
import json
import csv
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

CHARACTER_KEYWORDS = [
    "human", "person", "man", "woman", "hunter", "gatherer", "child", "people",
    "farmer", "ancestor", "forager", "tribesman", "warrior", "priest", "worker",
    "figure", "someone", "they", "we", "you", "crowd", "family", "men", "women"
]

def is_likely_character_shot(vo_text: str, visual_desc: str) -> bool:
    """Heuristic check whether shot features human characters."""
    combined = (vo_text + " " + visual_desc).lower()
    return any(re.search(r"\b" + re.escape(kw) + r"\b", combined) for kw in CHARACTER_KEYWORDS)

def format_stick_figure_prompt(visual_description: str, is_character: bool) -> str:
    """Format prompt strictly with full bleed and stick figure standards."""
    base_prefix = config.MANDATORY_STICK_FIGURE_STYLE
    clean_desc = visual_description.strip()
    if is_character:
        return f"{base_prefix} Scene depicts: {clean_desc}"
    else:
        # Non-character objects/landscapes
        non_char_prefix = (
            "Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art. "
            "Hand-drawn doodle comic style, Casually Explained and MinutePhysics aesthetic. "
            "Full bleed edge-to-edge illustration, grounded background environment, completely filling the 16:9 widescreen frame without borders, "
            "matted margins, or white card edges. Flat muted earthy color palette with subtle paper texture."
        )
        return f"{non_char_prefix} Detailed illustration of: {clean_desc}"

def run_stage2_script_prompts(video_title: str, custom_script_path: str = None) -> dict:
    """
    Generate or sync script, master storyboard CSV, all prompts, and character audit.
    """
    dirs = config.get_project_dirs(video_title)
    finals_dir = dirs["finals_dir"]
    postmortem_dir = dirs["postmortem_dir"]
    os.makedirs(finals_dir, exist_ok=True)
    os.makedirs(dirs["final_images_dir"], exist_ok=True)
    os.makedirs(dirs["voiceovers_dir"], exist_ok=True)
    os.makedirs(dirs["raw_images_dir"], exist_ok=True)

    master_csv_path = dirs["master_csv"]
    script_txt_path = dirs["script_txt"]
    all_prompts_path = dirs["all_prompts_txt"]
    audit_json_path = dirs["character_audit"]
    prompt_status_md = dirs["prompt_status_md"]

    # 1. If existing master CSV exists in Finals, preserve and load it
    existing_rows = []
    if os.path.exists(master_csv_path):
        print(f"Loading existing storyboard master: {master_csv_path}")
        with open(master_csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            existing_rows = list(reader)

    # If no existing master CSV, construct from postmortem cuts & transcript
    if not existing_rows:
        cuts_path = os.path.join(postmortem_dir, "cuts_data.json")
        transcript_path = custom_script_path or os.path.join(postmortem_dir, "clean_transcript.txt")

        if not os.path.exists(cuts_path) or not os.path.exists(transcript_path):
            raise FileNotFoundError(f"Missing postmortem files: {cuts_path} or {transcript_path}. Run Stage 1 first.")

        with open(cuts_path, "r", encoding="utf-8") as f:
            cuts = json.load(f)
        with open(transcript_path, "r", encoding="utf-8") as f:
            full_text = f.read()

        words = full_text.split()
        words_per_cut = max(1, len(words) // len(cuts))

        rows = []
        for i, cut in enumerate(cuts, 1):
            start_w = (i - 1) * words_per_cut
            end_w = i * words_per_cut if i < len(cuts) else len(words)
            cut_vo = " ".join(words[start_w:end_w])
            
            # Format timecode
            s_min, s_sec = int(cut["start_sec"] // 60), cut["start_sec"] % 60
            e_min, e_sec = int(cut["end_sec"] // 60), cut["end_sec"] % 60
            tc_str = f"{s_min:02d}:{s_sec:04.1f} - {e_min:02d}:{e_sec:04.1f}"

            desc = f"Concept visual for narration: {cut_vo[:80]}"
            is_char = is_likely_character_shot(cut_vo, desc)
            prompt = format_stick_figure_prompt(desc, is_char)
            rows.append([i, tc_str, cut_vo, desc, prompt])

        existing_rows = rows
        with open(master_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Shot", "Timecode", "Voiceover", "Description", "Stick Figure Prompt"])
            writer.writerows(rows)

    total_shots = len(existing_rows)

    # 2. Write clean_ai_voiceover_script.txt
    full_script_text = " ".join(r[2].strip() for r in existing_rows if len(r) > 2 and r[2].strip())
    with open(script_txt_path, "w", encoding="utf-8") as f:
        f.write(full_script_text.strip() + "\n")

    # 3. Compile all_prompts.txt
    prompt_lines = []
    for r in existing_rows:
        shot_num = int(r[0])
        tc = r[1]
        vo = r[2]
        desc = r[3]
        prompt = r[4] if len(r) > 4 else desc
        img_path = os.path.join(dirs["final_images_dir"], f"shot_{shot_num:03d}.jpg")
        status = "[STATUS: COMPLETED]" if os.path.exists(img_path) else "[STATUS: PENDING]"
        prompt_lines.append(f"SHOT {shot_num:03d} | {tc} | {status}")
        prompt_lines.append(f"VO: {vo}")
        prompt_lines.append(f"DESCRIPTION: {desc}")
        prompt_lines.append(f"PROMPT: {prompt}\n")

    with open(all_prompts_path, "w", encoding="utf-8") as f:
        f.write("\n".join(prompt_lines))

    # 4. Initialize / Sync character_audit.json
    audit_data = []
    if os.path.exists(audit_json_path):
        with open(audit_json_path, "r", encoding="utf-8") as f:
            try:
                audit_data = json.load(f)
            except Exception:
                audit_data = []

    audit_map = {d["shot_num"]: d for d in audit_data}
    new_audit = []
    for r in existing_rows:
        shot_num = int(r[0])
        tc = r[1]
        vo = r[2]
        desc = r[3]
        prompt = r[4] if len(r) > 4 else desc
        img_path = os.path.join(dirs["final_images_dir"], f"shot_{shot_num:03d}.jpg")
        img_exists = os.path.exists(img_path)

        if shot_num in audit_map:
            rec = audit_map[shot_num]
            # Ensure prompt and vo are up to date
            rec["timecode"] = tc
            rec["voiceover"] = vo
            rec["stick_prompt"] = prompt
            new_audit.append(rec)
        else:
            is_char = is_likely_character_shot(vo, desc)
            category = "VALID_STICK_FIGURE" if (img_exists and is_char) else ("NO_CHARACTER" if not is_char else "PENDING_REGEN")
            new_audit.append({
                "shot_num": shot_num,
                "timecode": tc,
                "voiceover": vo,
                "description": desc,
                "category": category,
                "regen_needed": not img_exists,
                "reason": "Initialized by Stage 2 compiler.",
                "stick_prompt": prompt,
                "cv_info": {}
            })

    with open(audit_json_path, "w", encoding="utf-8") as f:
        json.dump(new_audit, f, indent=2)

    # 5. Build PROMPT_STATUS.md
    completed_count = sum(1 for r in existing_rows if os.path.exists(os.path.join(dirs["final_images_dir"], f"shot_{int(r[0]):03d}.jpg")))
    pct = (completed_count / total_shots * 100.0) if total_shots > 0 else 0.0
    status_md = f"""# Storyboard Production Status: {video_title}

- **Total Shots**: {total_shots}
- **Completed Images**: {completed_count} / {total_shots} ({pct:.1f}%)
- **Pending Images**: {total_shots - completed_count}
- **Master CSV**: [`storyboard_master.csv`](storyboard_master.csv)
- **All Prompts Book**: [`all_prompts.txt`](all_prompts.txt)
- **Character Audit**: [`character_audit.json`](character_audit.json)
"""
    with open(prompt_status_md, "w", encoding="utf-8") as f:
        f.write(status_md)

    print(f"\n-> [STAGE 2 COMPLETE] {total_shots} shots prepared in: {finals_dir}")
    return {
        "total_shots": total_shots,
        "completed_count": completed_count,
        "master_csv": master_csv_path,
        "script_txt": script_txt_path,
        "all_prompts": all_prompts_path,
        "audit_json": audit_json_path,
        "char_count": len(full_script_text),
        "word_count": len(full_script_text.split())
    }
