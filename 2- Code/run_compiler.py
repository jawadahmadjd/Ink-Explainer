import csv
from data_part1 import act1_data, act2_data
from data_part2 import act3_data, act4_data
from data_part3 import act5_data, act6_data, act7_data

all_shots = act1_data + act2_data + act3_data + act4_data + act5_data + act6_data + act7_data

print(f"Total shots loaded: {len(all_shots)}")

# Rule: 1000 characters = 60 seconds (1 sec = 16.6667 chars)
cumulative_chars = 0
storyboard = []

for i, (text, visual, subject) in enumerate(all_shots):
    prompt = f"Minimalist hand-drawn black ink line art, clean doodle stick-figure illustration, expressive face, flat muted colors, cream off-white background (#FAF8F5), {subject}, clean 2D vector style, editorial cartoon, no text, 16:9 aspect ratio"
    
    char_count = len(text)
    start_sec = cumulative_chars * 60.0 / 1000.0
    end_sec = (cumulative_chars + char_count) * 60.0 / 1000.0
    cumulative_chars += char_count
    
    start_m, start_s = int(start_sec // 60), start_sec % 60
    end_m, end_s = int(end_sec // 60), end_sec % 60
    time_str = f"{start_m:02d}:{start_s:04.1f} - {end_m:02d}:{end_s:04.1f}"
    
    storyboard.append({
        "shot_id": i + 1,
        "time": time_str,
        "text": text,
        "visual": visual,
        "prompt": prompt
    })

total_duration_sec = cumulative_chars * 60.0 / 1000.0
print(f"Total characters: {cumulative_chars}")
print(f"Total duration: {int(total_duration_sec // 60):02d}:{total_duration_sec % 60:04.1f} ({total_duration_sec:.1f} seconds)")

# 1. Clean Voiceover Script for AI Voiceover
with open("clean_ai_voiceover_script.txt", "w", encoding="utf-8") as f:
    full_script = " ".join([s["text"] for s in storyboard])
    f.write(full_script)

# 2. Complete CSV File
with open("storyboard_master.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Shot #", "Time", "Spoken VO script", "Visual description", "Exact Prompt for google nano banana pro"])
    for s in storyboard:
        writer.writerow([s["shot_id"], s["time"], s["text"], s["visual"], s["prompt"]])

# 3. Complete Markdown File
with open("storyboard_master.md", "w", encoding="utf-8") as f:
    f.write("# Master Production Storyboard (350 Shots)\n\n")
    f.write("| Shot | Time | Spoken VO script | Visual description | Exact Prompt for google nano banana pro |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- |\n")
    for s in storyboard:
        # Escape pipes in text
        t_clean = s["text"].replace("|", "/")
        v_clean = s["visual"].replace("|", "/")
        p_clean = s["prompt"].replace("|", "/")
        f.write(f"| {s['shot_id']} | {s['time']} | {t_clean} | {v_clean} | `{p_clean}` |\n")

print("Files generated successfully: clean_ai_voiceover_script.txt, storyboard_master.csv, storyboard_master.md")

