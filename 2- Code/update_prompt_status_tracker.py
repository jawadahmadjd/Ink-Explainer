import csv
import json
import os
import shutil

FINAL_DIR = "Final selected images"
CSV_PATH = os.path.join("3- Finals", "storyboard_master.csv")
ALL_PROMPTS_TXT = os.path.join("3- Finals", "all_prompts.txt")
STATUS_MD = "PROMPT_STATUS.md"
STATUS_MD_FINALS = os.path.join("3- Finals", "PROMPT_STATUS.md")
LOG_CSV = os.path.join("3- Finals", "selection_log.csv")

def refresh_trackers():
    os.makedirs(FINAL_DIR, exist_ok=True)
    os.makedirs(os.path.join("3- Finals", "Final selected images"), exist_ok=True)
    
    # Mirror any existing images between the two folders
    for f in os.listdir(FINAL_DIR):
        if f.endswith(".jpg"):
            shutil.copy2(os.path.join(FINAL_DIR, f), os.path.join("3- Finals", "Final selected images", f))
    for f in os.listdir(os.path.join("3- Finals", "Final selected images")):
        if f.endswith(".jpg"):
            shutil.copy2(os.path.join("3- Finals", "Final selected images", f), os.path.join(FINAL_DIR, f))

    # Existing completed shots
    completed_shots = set()
    for f in os.listdir(FINAL_DIR):
        if f.startswith("shot_") and f.endswith(".jpg"):
            try:
                num = int(f.split("_")[1].split(".")[0])
                completed_shots.add(num)
            except:
                pass

    # Read log csv if exists for scores
    scores_by_shot = {}
    if os.path.exists(LOG_CSV):
        with open(LOG_CSV, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if row and len(row) >= 4:
                    try:
                        scores_by_shot[int(row[0])] = (row[2], row[3]) # (var, score)
                    except:
                        pass

    # Read all storyboard rows
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    total_shots = len(rows)
    completed_count = len(completed_shots)
    remaining_count = total_shots - completed_count
    pct = (completed_count / total_shots) * 100.0

    # 1. Generate updated all_prompts.txt with clear status tags
    with open(ALL_PROMPTS_TXT, "w", encoding="utf-8") as f:
        f.write("================================================================================\n")
        f.write("MASTER IMAGE PROMPTS & LIVE STATUS TRACKER (334 SHOTS)\n")
        f.write(f"Total Shots: {total_shots} | Completed: {completed_count} | Remaining: {remaining_count} ({pct:.1f}% Done)\n")
        f.write("Target Model: Google Flow (Nano Banana Pro 16:9 Full Bleed)\n")
        f.write("================================================================================\n\n")

        for row in rows:
            shot_num = int(row[0])
            timecode = row[1]
            vo_text = row[2]
            desc = row[3]
            prompt = row[4]

            is_done = shot_num in completed_shots
            status_tag = "[STATUS: COMPLETED]" if is_done else "[STATUS: PENDING]"

            f.write(f"{status_tag} --- [SHOT {shot_num:03d}] | {timecode} ---\n")
            f.write(f"VO: \"{vo_text}\"\n")
            if is_done:
                score_info = scores_by_shot.get(shot_num, ("Auto", "Selected"))
                f.write(f"Selected Image: Final selected images/shot_{shot_num:03d}.jpg (Var {score_info[0]} | Score: {score_info[1]})\n")
            f.write(f"Visual: {desc}\n")
            f.write(f"Prompt:\n{prompt}\n\n")

    # 2. Generate PROMPT_STATUS.md visual dashboard
    filled_blocks = int(pct // 5)
    empty_blocks = 20 - filled_blocks
    progress_bar = "█" * filled_blocks + "░" * empty_blocks

    md_content = f"""# Storyboard Generation Live Status Tracker

**Overall Progress**: `{progress_bar}` **{pct:.1f}%** ({completed_count} / {total_shots} Shots Completed | {remaining_count} Remaining)

- **Storage Location**: [`Final selected images/`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/Final%20selected%20images)
- **Status File**: [`3- Finals/production_status.json`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/3-%20Finals/production_status.json)
- **Detailed Prompts**: [`3- Finals/all_prompts.txt`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/3-%20Finals/all_prompts.txt)

---

## Recent Shots Status (First 30 Overview)

| Shot # | Timecode | Status | Selected Image | VO Script |
| :--- | :--- | :--- | :--- | :--- |
"""
    for row in rows[:35]:
        shot_num = int(row[0])
        timecode = row[1]
        vo_text = row[2]
        is_done = shot_num in completed_shots
        badge = "🟢 **COMPLETED**" if is_done else "⚪ *PENDING*"
        img_link = f"[`shot_{shot_num:03d}.jpg`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/Final%20selected%20images/shot_{shot_num:03d}.jpg)" if is_done else "-"
        md_content += f"| {shot_num:03d} | `{timecode}` | {badge} | {img_link} | {vo_text} |\n"

    if total_shots > 35:
        md_content += f"\n*(Showing first 35 of {total_shots} shots. See [`all_prompts.txt`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/3-%20Finals/all_prompts.txt) for the full line-by-line status of all 334 prompts).* \n"

    with open(STATUS_MD, "w", encoding="utf-8") as f:
        f.write(md_content)
    with open(STATUS_MD_FINALS, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Refreshed trackers: {completed_count}/{total_shots} completed ({pct:.1f}%).")

if __name__ == "__main__":
    refresh_trackers()

