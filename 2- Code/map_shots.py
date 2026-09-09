import json, re

with open('cuts_data.json') as f:
    data = json.load(f)

cuts = [0.0] + data['cuts'] + [672.3]
durations = data['durations']

with open('transcript.en-orig.vtt', encoding='utf-8') as f:
    vtt = f.read()

lines = vtt.splitlines()
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
        clean = re.sub(r'<[^>]+>', '', line).strip()
        if clean:
            cues.append((cur_start, cur_end, clean))

# Map cues to shots
shot_details = []
for i in range(len(durations)):
    s_start = cuts[i]
    s_end = cuts[i+1]
    dur = durations[i]
    # find words spoken during this shot
    words = []
    for c_start, c_end, txt in cues:
        if max(s_start, c_start) < min(s_end, c_end):
            words.append(txt)
    spoken = " ".join(words)
    shot_details.append({
        'shot_id': i + 1,
        'start': s_start,
        'end': s_end,
        'duration': round(dur, 2),
        'spoken': spoken[:100]
    })

print(f"Total mapped shots: {len(shot_details)}")
print("Sample first 10 shots:")
for s in shot_details[:10]:
    print(f"Shot {s['shot_id']:03d} [{s['start']:.2f}s - {s['end']:.2f}s, dur {s['duration']}s]: {s['spoken']}")
