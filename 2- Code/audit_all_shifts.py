import csv
import re
import os

csv_path = r"d:\Tools of Jawad\25- Ink Explainers\3- Finals\1- What Did Ancient Humans Actually Do All Day\storyboard_master.csv"
with open(csv_path, 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f))[1:]

shifts = []
for i in range(len(rows)):
    s = int(rows[i][0])
    vo = rows[i][2]
    desc = rows[i][3].lower()
    prompt = rows[i][4].lower()
    
    ignore_words = {'with', 'from', 'into', 'that', 'this', 'over', 'clean', 'line', 'black', 'white', 'flat', 'muted', 'colors', 'figure', 'stick', 'drawing', 'illustration', 'vector', 'minimalist'}
    desc_words = [w for w in re.findall(r'[a-zA-Z]{4,}', desc) if w not in ignore_words]
    curr_matches = [w for w in desc_words if w in prompt]
    curr_score = len(curr_matches) / max(1, len(desc_words))
    
    next_score = 0
    next_matches = []
    if i + 1 < len(rows):
        next_desc = rows[i+1][3].lower()
        next_words = [w for w in re.findall(r'[a-zA-Z]{4,}', next_desc) if w not in ignore_words]
        next_matches = [w for w in next_words if w in prompt]
        next_score = len(next_matches) / max(1, len(next_words))
        
    prev_score = 0
    prev_matches = []
    if i > 0:
        prev_desc = rows[i-1][3].lower()
        prev_words = [w for w in re.findall(r'[a-zA-Z]{4,}', prev_desc) if w not in ignore_words]
        prev_matches = [w for w in prev_words if w in prompt]
        prev_score = len(prev_matches) / max(1, len(prev_words))
        
    shifts.append({
        'shot': s,
        'vo': vo,
        'desc': rows[i][3],
        'prompt': rows[i][4],
        'curr_score': curr_score,
        'next_score': next_score,
        'prev_score': prev_score,
        'curr_m': curr_matches,
        'next_m': next_matches,
        'prev_m': prev_matches
    })

print(f"Total shots analyzed: {len(shifts)}")

print("\n" + "=" * 80)
print("ALL OFFSET ANOMALIES ACROSS THE ENTIRE SCRIPT")
print("=" * 80)
anomalies = [x for x in shifts if (x['next_score'] > 0.4 and x['curr_score'] < 0.25) or (x['prev_score'] > 0.4 and x['curr_score'] < 0.25)]
print(f"Total obvious offset anomalies: {len(anomalies)}")

for a in anomalies:
    kind = "MATCHES NEXT (+1 shift)" if a['next_score'] > a['curr_score'] else "MATCHES PREV (-1 shift)"
    print(f"Shot {a['shot']:03d} [{kind}]: curr={a['curr_score']:.2f}, next={a['next_score']:.2f}, prev={a['prev_score']:.2f}")
    print(f"   VO: {a['vo']}")
    print(f"   DESC: {a['desc']}")
    # print prompt snippet
    print(f"   PROMPT: {a['prompt'][-90:]}")
    print("-" * 80)

