import os
import csv

base_fn = r"d:\Tools of Jawad\25- Ink Explainers\3- Finals\1- What Did Ancient Humans Actually Do All Day"
csv_p = os.path.join(base_fn, "storyboard_master.csv")

with open(csv_p, "r", encoding="utf-8") as f:
    rows = list(csv.reader(f))[1:]

print("Checking Description vs Prompt alignment across all 334 shots...")

for i in range(len(rows)):
    shot_num = int(rows[i][0])
    desc = rows[i][3].lower()
    prompt = rows[i][4].lower()
    
    # Check if prompt matches current desc or next desc
    next_desc = rows[i+1][3].lower() if i + 1 < len(rows) else ""
    prev_desc = rows[i-1][3].lower() if i > 0 else ""
    
    # Check key words in desc
    desc_words = [w for w in desc.replace('.', '').replace(',', '').split() if len(w) > 4]
    matches_curr = sum(1 for w in desc_words if w in prompt)
    
    next_words = [w for w in next_desc.replace('.', '').replace(',', '').split() if len(w) > 4]
    matches_next = sum(1 for w in next_words if w in prompt) if next_words else 0
    
    prev_words = [w for w in prev_desc.replace('.', '').replace(',', '').split() if len(w) > 4]
    matches_prev = sum(1 for w in prev_words if w in prompt) if prev_words else 0

    if 40 <= shot_num <= 75:
        print(f"Shot {shot_num:03d} | MatchCurr: {matches_curr} | MatchNext: {matches_next} | MatchPrev: {matches_prev}")
        print(f"   VO: {rows[i][2][:35]}")
        print(f"   DESC: {rows[i][3][:45]}")
        print(f"   PROMPT snippet: {rows[i][4][200:260]}...")

