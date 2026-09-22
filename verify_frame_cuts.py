import gzip
import xml.etree.ElementTree as ET
import json
import csv
import os

TICKS_PER_FRAME_24FPS = 10584000000 # 254016000000 / 24
TICKS_PER_SEC = 254016000000

# 1. Load the perfect alignment
with open(r"3- Finals/history/2- What Did Ancient Humans Do at Night/Voiceovers/words_alignment.json", "r") as f:
    wdata = json.load(f)

whisper_words = wdata["words"]
audio_dur = wdata.get("duration_sec", 496.96)

# Load perfect alignment we generated
from difflib import SequenceMatcher
import re

def clean_word(w):
    return re.sub(r"[^\w]", "", w.lower())

whisper_tokens = [clean_word(w["word"]) for w in whisper_words]

with open(r"3- Finals/history/2- What Did Ancient Humans Do at Night/storyboard_master.csv", "r", encoding="utf-8") as f:
    rows = list(csv.reader(f))[1:]

all_shot_tokens = []
token_to_shot = []
shot_first_token_idx = {}

for r in rows:
    s_num = int(r[0])
    vo = r[2].strip()
    if "closing contemplative frame" in vo.lower():
        continue
    words = [clean_word(w) for w in vo.split() if clean_word(w)]
    if not words:
        continue
    shot_first_token_idx[s_num] = len(all_shot_tokens)
    for w_i, w in enumerate(words):
        all_shot_tokens.append(w)
        token_to_shot.append((s_num, w_i))

sm = SequenceMatcher(None, all_shot_tokens, whisper_tokens)

token_to_whisper = {}
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        for offset in range(i2 - i1):
            token_to_whisper[i1 + offset] = j1 + offset
    elif tag == "replace":
        num_shot = i2 - i1
        num_whisp = j2 - j1
        for offset in range(num_shot):
            whisp_offset = int(offset * num_whisp / num_shot)
            token_to_whisper[i1 + offset] = min(j1 + whisp_offset, len(whisper_words) - 1)
    elif tag == "delete":
        for offset in range(i2 - i1):
            token_to_whisper[i1 + offset] = min(j1, len(whisper_words) - 1)

shot_speech_start = {}
for s_num in range(1, 361):
    if s_num in shot_first_token_idx:
        tok_idx = shot_first_token_idx[s_num]
        w_idx = token_to_whisper.get(tok_idx, 0)
        shot_speech_start[s_num] = whisper_words[w_idx]["start_sec"]

shot_speech_start[361] = round(whisper_words[-1]["end_sec"], 3)

# Build 24fps frame cut points
total_frames = int(round(audio_dur * 24))
cut_frames = [0]
for s_num in range(2, 362):
    raw_start = shot_speech_start[s_num]
    raw_f = int(round(raw_start * 24))
    min_f = cut_frames[-1] + 1
    cut_f = max(raw_f, min_f)
    cut_frames.append(cut_f)

cut_frames.append(total_frames)

print(f"Total cut frames: {len(cut_frames)} (expected 362)")
print(f"First 5 cut frames: {cut_frames[:5]}")
print(f"Last 5 cut frames: {cut_frames[-5:]}")

# Check that frames are strictly increasing
for i in range(len(cut_frames) - 1):
    assert cut_frames[i+1] > cut_frames[i], f"Non-increasing frames at {i}: {cut_frames[i]} >= {cut_frames[i+1]}"

print("Frame boundaries verified 100% strictly increasing!")

