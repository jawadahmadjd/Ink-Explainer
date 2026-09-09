import re, json

with open('transcript.en-orig.vtt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

time_pattern = re.compile(r'(\d{2}:)?(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(\d{2}:)?(\d{2}):(\d{2})\.(\d{3})')
cues = []
for line in lines:
    line = line.strip()
    if '-->' in line:
        parts = line.split('-->')
        cues.append({'time': parts[0].strip(), 'text': []})
    elif cues and line and not line.startswith('WEBVTT') and not line.startswith('NOTE'):
        clean = re.sub(r'<[^>]+>', '', line).strip()
        if clean:
            cues[-1]['text'].append(clean)

full_lines = []
for c in cues:
    txt = ' '.join(c['text']).strip()
    if txt and (not full_lines or full_lines[-1] != txt):
        full_lines.append(txt)

raw_text = ' '.join(full_lines)
# Remove repeated adjacent words often introduced by auto-captions
words = raw_text.split()
dedup = []
for w in words:
    if not dedup or dedup[-1].lower() != w.lower():
        dedup.append(w)

clean_script = ' '.join(dedup)
with open('clean_transcript.txt', 'w', encoding='utf-8') as f:
    f.write(clean_script)

print('Word count:', len(clean_script.split()))
print('Sample text:', clean_script[:400])
