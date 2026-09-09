import re, json, numpy as np

with open('transcript.en-orig.vtt', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()
time_re = re.compile(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})')

def to_sec(s):
    p = s.split(':')
    return int(p[0])*3600 + int(p[1])*60 + float(p[2])

cues = []
cur_start, cur_end = None, None
for line in lines:
    m = time_re.search(line)
    if m:
        cur_start = to_sec(m.group(1))
        cur_end = to_sec(m.group(2))
    elif '<c>' in line and cur_start is not None:
        cleaned = re.sub(r'<[^>]+>', '', line).strip()
        if cleaned:
            cues.append((cur_start, cur_end, cleaned))

pauses = []
for i in range(len(cues)-1):
    gap = cues[i+1][0] - cues[i][1]
    if gap > 0.05:
        pauses.append((gap, cues[i][2], cues[i+1][2]))

pause_durs = [p[0] for p in pauses]
print(f'Total detected speech pauses: {len(pauses)}')
print(f'Mean pause duration: {np.mean(pause_durs):.2f}s')
print(f'Median pause duration: {np.median(pause_durs):.2f}s')
print(f'Max pause duration: {np.max(pause_durs):.2f}s')
print('Top 8 longest dramatic pauses:')
for p in sorted(pauses, key=lambda x: x[0], reverse=True)[:8]:
    print(f'  {p[0]:.2f}s pause between: "{p[1]}" -> "{p[2]}"')
