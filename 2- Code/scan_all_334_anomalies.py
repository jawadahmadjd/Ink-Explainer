import csv
import re

csv_path = r"d:\Tools of Jawad\25- Ink Explainers\3- Finals\1- What Did Ancient Humans Actually Do All Day\storyboard_master.csv"
with open(csv_path, 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f))[1:]

ignore = {
    'with', 'from', 'into', 'that', 'this', 'over', 'clean', 'line', 'black',
    'white', 'flat', 'muted', 'colors', 'figure', 'stick', 'drawing',
    'illustration', 'vector', 'minimalist', 'showing', 'background', 'under',
    'across', 'through', 'around', 'their', 'there', 'where', 'which', 'about'
}

def get_keywords(text):
    return [w for w in re.findall(r'[a-zA-Z]{4,}', text.lower()) if w not in ignore]

all_anomalies = []
for i, r in enumerate(rows):
    s = int(r[0])
    vo = r[2]
    desc = r[3]
    prompt = r[4]
    
    dkw = get_keywords(desc)
    prompt_lower = prompt.lower()
    matches = [w for w in dkw if w in prompt_lower]
    score = len(matches) / max(1, len(dkw))
    
    # Check next row
    next_score = 0
    if i + 1 < len(rows):
        ndkw = get_keywords(rows[i+1][3])
        nmatches = [w for w in ndkw if w in prompt_lower]
        next_score = len(nmatches) / max(1, len(ndkw))
        
    # Check prev row
    prev_score = 0
    if i > 0:
        pdkw = get_keywords(rows[i-1][3])
        pmatches = [w for w in pdkw if w in prompt_lower]
        prev_score = len(pmatches) / max(1, len(pdkw))
        
    if score < 0.35:
        all_anomalies.append({
            'shot': s,
            'vo': vo,
            'desc': desc,
            'prompt': prompt,
            'score': score,
            'prev_score': prev_score,
            'next_score': next_score
        })

print(f"Total shots with low description match (score < 0.35): {len(all_anomalies)}")
for a in all_anomalies:
    rel = "EXACT MATCH TO PREV (-1)" if a['prev_score'] >= 0.5 else ("EXACT MATCH TO NEXT (+1)" if a['next_score'] >= 0.5 else "LOW MATCH / THEMATIC")
    print(f"Shot {a['shot']:03d} | Rel: {rel:25s} | Score: {a['score']:.2f} (prev={a['prev_score']:.2f}, next={a['next_score']:.2f})")
    print(f"   VO  : {a['vo'][:50]}")
    print(f"   DESC: {a['desc'][:55]}")

