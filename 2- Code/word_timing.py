import re, numpy as np

with open('transcript.en-orig.vtt', encoding='utf-8') as f:
    text = f.read()

# Pattern for word timestamps: <hh:mm:ss.mmm><c> word</c>
word_pat = re.compile(r'<(\d{2}:\d{2}:\d{2}\.\d{3})><c>\s*([^<]+?)</c>')

def to_sec(s):
    p = s.split(':')
    return int(p[0])*3600 + int(p[1])*60 + float(p[2])

words_timed = []
for m in word_pat.finditer(text):
    t_sec = to_sec(m.group(1))
    w = m.group(2).strip()
    words_timed.append((t_sec, w))

# Deduplicate identical consecutive timestamps/words
clean_words = []
for wt in words_timed:
    if not clean_words or (wt[0] != clean_words[-1][0] or wt[1] != clean_words[-1][1]):
        clean_words.append(wt)

print(f"Total word tokens parsed: {len(clean_words)}")
# Gaps between words
gaps = []
for i in range(len(clean_words)-1):
    gap = clean_words[i+1][0] - clean_words[i][0]
    if gap > 0.6: # pause longer than 600ms
        gaps.append((gap, clean_words[i][1], clean_words[i+1][1], clean_words[i][0]))

print(f"Significant pauses (>0.6s): {len(gaps)}")
for g in sorted(gaps, key=lambda x: x[0], reverse=True)[:10]:
    print(f"  {g[0]:.2f}s pause at {g[3]:.1f}s after '{g[1]}' before '{g[2]}'")
