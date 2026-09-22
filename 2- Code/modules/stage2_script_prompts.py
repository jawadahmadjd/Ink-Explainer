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

def format_stick_figure_prompt(visual_description: str, is_character: bool, niche: str = None) -> str:
    """Format prompt strictly with full bleed and stick figure standards, respecting niche visual tokens."""
    color_palette = "Flat muted earthy color palette with subtle paper texture."
    if niche:
        try:
            from learning.learning_engine import load_codex
            codex = load_codex()
            n_data = codex.get("niches", {}).get(niche, {})
            color_palette = n_data.get("visual_style", {}).get("color_palette", color_palette)
        except Exception:
            pass

    clean_desc = visual_description.strip()
    if is_character:
        base_prefix = (
            "Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art. "
            "Hand-drawn doodle comic style, Casually Explained and MinutePhysics aesthetic. "
            "All human characters MUST be drawn strictly as simple, minimalist stick figures: "
            "thin black line bodies, plain empty white circle heads, minimal dot eyes, simple neutral line mouths. "
            f"Full bleed edge-to-edge illustration, grounded background environment completely filling 16:9 widescreen frame without borders. {color_palette}"
        )
        return f"{base_prefix} Scene depicts: {clean_desc}"
    else:
        # Non-character objects/landscapes
        non_char_prefix = (
            "Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art. "
            "Hand-drawn doodle comic style, Casually Explained and MinutePhysics aesthetic. "
            f"Full bleed edge-to-edge illustration, grounded background environment, completely filling the 16:9 widescreen frame without borders, "
            f"matted margins, or white card edges. {color_palette}"
        )
        return f"{non_char_prefix} Detailed illustration of: {clean_desc}"

from learning.learning_engine import (
    find_matching_reference_video,
    generate_script_and_shots,
    split_script_into_fast_paced_shots,
    split_script_into_elastic_steps,
    generate_smart_scene_description,
    classify_script_niche
)

def run_stage2_script_prompts(
    video_title: str,
    custom_script_path: str = None,
    user_prompt: str = None,
    force_regenerate: bool = False,
    niche: str = None,
    use_offline_fallback: bool = False
) -> dict:
    """
    Generate or sync script, master storyboard CSV, all prompts, and character audit.
    By default, script repurposing/creation and prompt generation are handled entirely by Antigravity.
    Provides use_offline_fallback=True as a local regex/heuristic fallback.
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

    # Detect or recover niche for project
    info_json_path = os.path.join(postmortem_dir, "video_info.json")
    vinfo = {}
    if os.path.exists(info_json_path):
        try:
            with open(info_json_path, "r", encoding="utf-8") as f:
                vinfo = json.load(f)
                if not niche:
                    niche = vinfo.get("niche")
        except Exception:
            pass
    if not niche:
        niche = classify_script_niche(video_title, user_prompt or "").get("niche", "history")

    cuts_path = os.path.join(postmortem_dir, "cuts_data.json")
    cuts_list = []
    if os.path.exists(cuts_path):
        try:
            with open(cuts_path, "r", encoding="utf-8") as f:
                cdata = json.load(f)
                cuts_list = cdata if isinstance(cdata, list) else cdata.get("cuts", [])
        except Exception:
            pass

    # 1. If existing master CSV exists in Finals, preserve and load it unless forced
    existing_rows = []
    if os.path.exists(master_csv_path) and not force_regenerate:
        print(f"Loading existing storyboard master: {master_csv_path}")
        with open(master_csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            existing_rows = list(reader)

    # If no existing master CSV, construct using Antigravity AI Engine (or offline fallback)
    if not existing_rows or force_regenerate:
        transcript_path = custom_script_path or os.path.join(postmortem_dir, "clean_transcript.txt")
        raw_text = ""
        if os.path.exists(transcript_path):
            with open(transcript_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

        match = find_matching_reference_video(video_title, niche=niche)
        if match:
            print(f"[REFERENCE MATCH FOUND] '{match['title']}' in niche '{match.get('niche', niche)}' (Score: {match['score']})")

        if not use_offline_fallback:
            # Primary path: Handled entirely by Antigravity
            from modules.antigravity_bridge import dispatch_task, wait_for_task_completion
            task_type = "SCRIPT_REPURPOSING_AND_STORYBOARD" if raw_text else "SCRIPT_CREATION_AND_STORYBOARD"
            print(f"\n[STAGE 2] Dispatching to Antigravity AI Engine ({task_type}) for '{video_title}' (Niche: {niche})...")
            dispatch_task(
                task_type=task_type,
                project_title=video_title,
                user_prompt=user_prompt or "",
                matched_blueprint=match,
                reference_transcript=raw_text,
                niche=niche,
                video_info=vinfo,
                cuts_data=cuts_list
            )
            print(f"Awaiting Antigravity script synthesis and storyboard generation...")
            completed = wait_for_task_completion(timeout_sec=3600, poll_interval=1.0)
            if not completed or not os.path.exists(master_csv_path):
                raise TimeoutError(f"Antigravity task timed out or '{master_csv_path}' was not generated.")

            with open(master_csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                existing_rows = list(reader)
        else:
            # Fallback path: Offline heuristic generation
            print("   [STAGE 2 FALLBACK] Running offline rule-based script & prompt generator...")
            rows = []
            if raw_text:
                from modules.script_spinner import get_spun_script_for_title
                spun_script = get_spun_script_for_title(video_title, raw_transcript=raw_text)
                final_script_text = spun_script if spun_script else raw_text
                shot_texts = split_script_into_elastic_steps(final_script_text, target_min_chars=16, target_max_chars=65)
                total_shots_count = len(shot_texts)

                total_dur = 60.0
                if cuts_list:
                    try:
                        total_dur = cuts_list[-1].get("end_sec", 60.0) if isinstance(cuts_list[-1], dict) else cuts_list[-1]
                    except Exception:
                        pass

                shot_dur = total_dur / float(max(1, total_shots_count))
                for i, cut_vo in enumerate(shot_texts, 1):
                    s_time = (i - 1) * shot_dur
                    e_time = i * shot_dur
                    s_min, s_sec = int(s_time // 60), s_time % 60
                    e_min, e_sec = int(e_time // 60), e_time % 60
                    tc_str = f"{s_min:02d}:{s_sec:04.1f} - {e_min:02d}:{e_sec:04.1f}"

                    prev_vo = shot_texts[i-2] if i > 1 else ""
                    next_vo = shot_texts[i] if i < len(shot_texts) else ""
                    desc = generate_smart_scene_description(cut_vo, prev_vo=prev_vo, next_vo=next_vo, niche=niche)
                    is_char = is_likely_character_shot(cut_vo, desc)
                    prompt = format_stick_figure_prompt(desc, is_char, niche=niche)
                    rows.append([i, tc_str, cut_vo, desc, prompt])
            else:
                raise ValueError("Offline fallback requires an existing reference transcript. Please use Antigravity mode.")

            existing_rows = rows
            with open(master_csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Shot #", "Time", "Spoken VO script", "Visual description", "Exact Prompt for google nano banana pro"])
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
