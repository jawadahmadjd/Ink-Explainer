import gzip
import xml.etree.ElementTree as ET
import json
import csv
import os
import shutil

TICKS_PER_FRAME_24FPS = 10584000000 # 254016000000 / 24
TICKS_PER_SEC = 254016000000

# 1. Load Whisper alignment and storyboard
PROJECT_DIR = r"d:\Tools of Jawad\25- Ink Explainers\3- Finals\history\2- What Did Ancient Humans Do at Night"
WORDS_JSON = os.path.join(PROJECT_DIR, "Voiceovers", "words_alignment.json")
CSV_PATH = os.path.join(PROJECT_DIR, "storyboard_master.csv")
SHOTS_ALIGN_PATH = os.path.join(PROJECT_DIR, "Voiceovers", "shots_timing_alignment.json")
XML_PATH = os.path.join(PROJECT_DIR, "storyboard_timeline.xml")
PRPROJ_PATH = os.path.join(PROJECT_DIR, "Ancient nights.prproj")
SYNCED_PRPROJ_PATH = os.path.join(PROJECT_DIR, "Ancient nights_100_percent_synced.prproj")

with open(WORDS_JSON, "r", encoding="utf-8") as f:
    wdata = json.load(f)

whisper_words = wdata["words"]
audio_dur = wdata.get("duration_sec", 496.96)

from difflib import SequenceMatcher
import re

def clean_word(w):
    return re.sub(r"[^\w]", "", w.lower())

whisper_tokens = [clean_word(w["word"]) for w in whisper_words]

with open(CSV_PATH, "r", encoding="utf-8") as f:
    csv_rows = list(csv.reader(f))
header = csv_rows[0]
rows = csv_rows[1:]

all_shot_tokens = []
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
    for w in words:
        all_shot_tokens.append(w)

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

total_frames = int(round(audio_dur * 24))
cut_frames = [0]
for s_num in range(2, 362):
    raw_start = shot_speech_start[s_num]
    raw_f = int(round(raw_start * 24))
    min_f = cut_frames[-1] + 1
    cut_f = max(raw_f, min_f)
    cut_frames.append(cut_f)

cut_frames.append(total_frames)

# A. Save shots_timing_alignment.json
shots_alignment = []
for i in range(len(rows)):
    s_num = int(rows[i][0])
    st_f = cut_frames[i]
    en_f = cut_frames[i+1]
    dur_f = en_f - st_f
    st_sec = round(st_f / 24.0, 3)
    en_sec = round(en_f / 24.0, 3)
    dur_sec = round(en_sec - st_sec, 3)
    shots_alignment.append({
        "shot_num": s_num,
        "start_frame": st_f,
        "end_frame": en_f,
        "duration_frames": dur_f,
        "start_sec": st_sec,
        "end_sec": en_sec,
        "duration_sec": dur_sec,
        "vo_text": rows[i][2].strip(),
        "desc": rows[i][3].strip(),
        "image_file": f"shot_{s_num:03d}.jpg"
    })

with open(SHOTS_ALIGN_PATH, "w", encoding="utf-8") as f:
    json.dump(shots_alignment, f, indent=2)
print(f"Updated {SHOTS_ALIGN_PATH} (361 shots, 0 gaps, 0 overlaps)")

# B. Update storyboard_master.csv
updated_csv_rows = [header]
for i, r in enumerate(rows):
    st_sec = shots_alignment[i]["start_sec"]
    en_sec = shots_alignment[i]["end_sec"]
    st_m = int(st_sec // 60)
    st_s = st_sec % 60
    en_m = int(en_sec // 60)
    en_s = en_sec % 60
    tc_str = f"{st_m:02d}:{st_s:04.1f} - {en_m:02d}:{en_s:04.1f}"
    r_copy = list(r)
    r_copy[1] = tc_str
    updated_csv_rows.append(r_copy)

with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(updated_csv_rows)
print(f"Updated {CSV_PATH} with speech-aligned timecodes")

# C. Update storyboard_timeline.xml
# Re-run Stage 5 timeline generator
import sys
sys.path.insert(0, r"d:\Tools of Jawad\25- Ink Explainers\2- Code")
from modules.stage5_timeline_xml import run_stage5_timeline_xml
xml_res = run_stage5_timeline_xml("2- What Did Ancient Humans Do at Night", fps=24)
print(f"Updated {XML_PATH} with 24fps 2560x1440 sequence: {xml_res}")

# D. Patch Ancient nights.prproj and create Ancient nights_100_percent_synced.prproj
with gzip.open(PRPROJ_PATH, "rb") as f:
    prproj_xml = f.read()

root = ET.fromstring(prproj_xml)
obj_map = {elem.attrib["ObjectID"]: elem for elem in root if "ObjectID" in elem.attrib}
video_items = root.findall(".//VideoClipTrackItem")

print(f"Patching {len(video_items)} VideoClipTrackItems in prproj...")
for i in range(min(len(video_items), 361)):
    item = video_items[i]
    st_ticks = cut_frames[i] * TICKS_PER_FRAME_24FPS
    en_ticks = cut_frames[i+1] * TICKS_PER_FRAME_24FPS
    dur_ticks = en_ticks - st_ticks

    # TrackItem start / end
    track_item = item.find(".//TrackItem")
    if track_item is not None:
        st_elem = track_item.find("Start")
        if i == 0:
            if st_elem is not None:
                track_item.remove(st_elem)
        else:
            if st_elem is None:
                st_elem = ET.SubElement(track_item, "Start")
            st_elem.text = str(st_ticks)
        
        en_elem = track_item.find("End")
        if en_elem is None:
            en_elem = ET.SubElement(track_item, "End")
        en_elem.text = str(en_ticks)

    # SubClip -> VideoClip InPoint / OutPoint
    subclip_ref = item.find(".//SubClip")
    if subclip_ref is not None:
        sub_id = subclip_ref.attrib.get("ObjectRef")
        if sub_id and sub_id in obj_map:
            sub_elem = obj_map[sub_id]
            clip_ref = sub_elem.find(".//Clip")
            if clip_ref is not None:
                clip_id = clip_ref.attrib.get("ObjectRef")
                if clip_id and clip_id in obj_map:
                    video_clip_elem = obj_map[clip_id]
                    in_elem = video_clip_elem.find(".//InPoint")
                    out_elem = video_clip_elem.find(".//OutPoint")
                    if in_elem is not None: in_elem.text = "0"
                    if out_elem is not None: out_elem.text = str(dur_ticks)

# Patch Adjustment Layer if present
if len(video_items) > 361:
    adj_item = video_items[361]
    adj_track = adj_item.find(".//TrackItem")
    if adj_track is not None:
        adj_end = adj_track.find("End")
        if adj_end is not None:
            adj_end.text = str(cut_frames[-1] * TICKS_PER_FRAME_24FPS)
    adj_subclip = adj_item.find(".//SubClip")
    if adj_subclip is not None:
        sub_id = adj_subclip.attrib.get("ObjectRef")
        if sub_id and sub_id in obj_map:
            sub_elem = obj_map[sub_id]
            clip_ref = sub_elem.find(".//Clip")
            if clip_ref is not None:
                clip_id = clip_ref.attrib.get("ObjectRef")
                if clip_id and clip_id in obj_map:
                    vc = obj_map[clip_id]
                    out_elem = vc.find(".//OutPoint")
                    if out_elem is not None:
                        out_elem.text = str(cut_frames[-1] * TICKS_PER_FRAME_24FPS)

# Serialize back to gzipped XML
updated_prproj_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)

# Write to Ancient nights_100_percent_synced.prproj
with gzip.open(SYNCED_PRPROJ_PATH, "wb") as f_out:
    f_out.write(updated_prproj_bytes)
print(f"Created 100% synced Premiere project: {SYNCED_PRPROJ_PATH}")

# Backup original and write to Ancient nights.prproj as well
shutil.copy2(PRPROJ_PATH, PRPROJ_PATH + ".backup")
with gzip.open(PRPROJ_PATH, "wb") as f_out:
    f_out.write(updated_prproj_bytes)
print(f"Updated {PRPROJ_PATH} directly (original backed up to .backup)")
