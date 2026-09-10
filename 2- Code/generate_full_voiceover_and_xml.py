"""
Comprehensive Voiceover & Timeline Assembly Pipeline
1. Generates full script via ElevenLabs (/v1/text-to-speech/{voice_id}/with-timestamps)
2. Assembles millisecond-precision character and word alignment map
3. Enforces SOP silence normalization rule:
   - If silence > 300ms: crop excess, leaving 150ms after current sentence and 150ms before next sentence
4. Normalizes master audio and exports MP3 & WAV
5. Maps all 334 shots to exact voiceover start/end timestamps
6. Generates FCP 7 XML (xmeml v4) timeline for Premiere Pro / DaVinci Resolve
"""

import os
import sys
import json
import base64
import re
import csv
import time
import requests
import numpy as np
import soundfile as sf
import subprocess
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "rPMkKgdwgIwqv4fXgR6N")
MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

VIDEO_SUBDIR = "1- What Did Ancient Humans Actually Do All Day"
FINALS_DIR = os.path.join(PROJECT_ROOT, "3- Finals", VIDEO_SUBDIR)
OUTPUT_VO_DIR = os.path.join(FINALS_DIR, "Voiceovers")
FINAL_IMAGES_DIR = os.path.join(FINALS_DIR, "Final selected images")
CSV_PATH = os.path.join(FINALS_DIR, "storyboard_master.csv")
SCRIPT_PATH = os.path.join(FINALS_DIR, "clean_ai_voiceover_script.txt")
XML_OUTPUT_PATH = os.path.join(FINALS_DIR, "storyboard_timeline.xml")

os.makedirs(OUTPUT_VO_DIR, exist_ok=True)

# ------------------------------------------------------------------------------
# STEP 1: SEGMENT SCRIPT INTO 3 NATURAL CHUNKS AT SENTENCE BOUNDARIES
# ------------------------------------------------------------------------------
with open(CSV_PATH, "r", encoding="utf-8") as f:
    rows = list(csv.reader(f))[1:]

assert len(rows) == 334, f"Expected 334 shots, found {len(rows)}"

chunk_defs = [
    {"name": "chunk_1", "start_idx": 0, "end_idx": 110},    # Shots 1-110
    {"name": "chunk_2", "start_idx": 110, "end_idx": 220},  # Shots 111-220
    {"name": "chunk_3", "start_idx": 220, "end_idx": 334},  # Shots 221-334
]

for cd in chunk_defs:
    cd_rows = rows[cd["start_idx"]:cd["end_idx"]]
    cd["text"] = " ".join(r[2].strip() for r in cd_rows)
    cd["shot_count"] = len(cd_rows)
    cd["char_count"] = len(cd["text"])

print("========================================================")
print("ELEVENLABS FULL SCRIPT GENERATION & TIMELINE PIPELINE")
print(f"Voice ID: {VOICE_ID} (Tyler - Clear US YouTube Creator Voice)")
print(f"Model ID: {MODEL_ID}")
print(f"Total Shots: {len(rows)}")
for cd in chunk_defs:
    print(f"  [{cd['name']}] Shots {cd['start_idx']+1:03d}-{cd['end_idx']:03d} | Chars: {cd['char_count']} | Words: {len(cd['text'].split())}")
print("========================================================\n")

# ------------------------------------------------------------------------------
# STEP 2: GENERATE CHUNKS WITH TIMESTAMPS FROM ELEVENLABS
# ------------------------------------------------------------------------------
def generate_chunk_with_timestamps(text, chunk_name):
    cache_mp3 = os.path.join(OUTPUT_VO_DIR, f"{chunk_name}_raw.mp3")
    cache_json = os.path.join(OUTPUT_VO_DIR, f"{chunk_name}_alignment.json")

    if os.path.exists(cache_mp3) and os.path.exists(cache_json):
        print(f"[CACHE HIT] Loading cached {chunk_name}...")
        with open(cache_json, "r", encoding="utf-8") as f:
            align_data = json.load(f)
        return cache_mp3, align_data

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": float(os.getenv("ELEVENLABS_STABILITY", "0.50")),
            "similarity_boost": float(os.getenv("ELEVENLABS_SIMILARITY_BOOST", "0.75")),
            "style": float(os.getenv("ELEVENLABS_STYLE", "0.15")),
            "use_speaker_boost": os.getenv("ELEVENLABS_USE_SPEAKER_BOOST", "true").lower() == "true"
        }
    }

    print(f"[API CALL] Generating {chunk_name} ({len(text)} chars)...")
    for attempt in range(3):
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=180)
            if r.status_code == 200:
                data = r.json()
                audio_bytes = base64.b64decode(data["audio_base64"])
                with open(cache_mp3, "wb") as f_out:
                    f_out.write(audio_bytes)
                
                align_data = data.get("alignment", {})
                with open(cache_json, "w", encoding="utf-8") as f_json:
                    json.dump(align_data, f_json, indent=2)
                
                print(f"  -> Successfully generated {chunk_name} ({len(audio_bytes)/1024:.1f} KB)")
                return cache_mp3, align_data
            else:
                print(f"  -> Attempt {attempt+1} error {r.status_code}: {r.text[:200]}")
                time.sleep(5)
        except Exception as e:
            print(f"  -> Attempt {attempt+1} exception: {e}")
            time.sleep(5)

    raise RuntimeError(f"Failed to generate {chunk_name} after 3 attempts.")

raw_chunk_results = []
for cd in chunk_defs:
    mp3_path, align = generate_chunk_with_timestamps(cd["text"], cd["name"])
    raw_chunk_results.append({
        "name": cd["name"],
        "text": cd["text"],
        "mp3_path": mp3_path,
        "alignment": align
    })

# ------------------------------------------------------------------------------
# STEP 3: CONVERT TO PCM AUDIO & CONCATENATE WITH TIMING OFFSETS
# ------------------------------------------------------------------------------
print("\n[AUDIO STITCHING] Decoding and stitching audio chunks with sample precision...")
stitched_pcm_list = []
unified_characters = []
unified_starts = []
unified_ends = []
current_time_offset = 0.0
sample_rate = None

for cr in raw_chunk_results:
    # Convert MP3 to WAV in memory using ffmpeg
    cmd = ["ffmpeg", "-y", "-i", cr["mp3_path"], "-f", "wav", "-ar", "44100", "-ac", "1", "-"]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    
    # Read PCM from WAV bytes using soundfile
    import io
    data, sr = sf.read(io.BytesIO(proc.stdout), dtype="float32")
    if sample_rate is None:
        sample_rate = sr
    
    duration = len(data) / sample_rate
    stitched_pcm_list.append(data)

    # Offset character timestamps
    chars = cr["alignment"].get("characters", [])
    starts = cr["alignment"].get("character_start_times_seconds", [])
    ends = cr["alignment"].get("character_end_times_seconds", [])

    for c, s, e in zip(chars, starts, ends):
        unified_characters.append(c)
        unified_starts.append(s + current_time_offset)
        unified_ends.append(e + current_time_offset)

    current_time_offset += duration

master_pcm = np.concatenate(stitched_pcm_list)
print(f"Total raw audio duration: {len(master_pcm)/sample_rate:.2f}s ({len(master_pcm)} samples @ {sample_rate}Hz)")

# ------------------------------------------------------------------------------
# STEP 4: ASSEMBLE WORDS AND IDENTIFY SENTENCE BOUNDARIES
# ------------------------------------------------------------------------------
words = []
cur_word_chars = []
cur_word_start = None
cur_word_end = None

for c, s, e in zip(unified_characters, unified_starts, unified_ends):
    if not c.isspace():
        if cur_word_start is None:
            cur_word_start = s
        cur_word_chars.append(c)
        cur_word_end = e
    else:
        if cur_word_chars:
            w_str = "".join(cur_word_chars)
            is_end = bool(re.search(r'[.!?]["\']?$', w_str))
            words.append({
                "word": w_str,
                "start": cur_word_start,
                "end": cur_word_end,
                "is_sentence_end": is_end
            })
            cur_word_chars = []
            cur_word_start = None
            cur_word_end = None

if cur_word_chars:
    w_str = "".join(cur_word_chars)
    is_end = bool(re.search(r'[.!?]["\']?$', w_str))
    words.append({
        "word": w_str,
        "start": cur_word_start,
        "end": cur_word_end,
        "is_sentence_end": is_end
    })

print(f"Total parsed words: {len(words)}")
sentence_end_indices = [i for i, w in enumerate(words) if w["is_sentence_end"]]
print(f"Total sentences detected: {len(sentence_end_indices)}")

# ------------------------------------------------------------------------------
# STEP 5: ENFORCE 300ms SILENCE NORMALIZATION (150ms TAIL + 150ms LEAD)
# ------------------------------------------------------------------------------
print("\n[SILENCE NORMALIZATION] Applying SOP rule: >300ms silence capped to 150ms + 150ms...")
cuts = [] # list of (cut_start_sec, cut_end_sec)

for idx in sentence_end_indices[:-1]:
    cur_end = words[idx]["end"]
    next_start = words[idx+1]["start"]
    gap = next_start - cur_end

    if gap > 0.300:
        # Keep 150ms after cur_end, keep 150ms before next_start
        cut_start = cur_end + 0.150
        cut_end = next_start - 0.150
        if cut_end > cut_start:
            cuts.append((cut_start, cut_end, gap))

print(f"Found {len(cuts)} inter-sentence pauses exceeding 300ms.")

# Splicing audio array cleanly
new_pcm_chunks = []
last_pos = 0.0
total_removed_sec = 0.0

# Pre-calculate time shift function
def get_shifted_time(orig_time):
    shift = 0.0
    for cs, ce, _ in cuts:
        if orig_time >= ce:
            shift += (ce - cs)
        elif orig_time > cs:
            shift += (orig_time - cs)
            break
    return orig_time - shift

for cs, ce, orig_gap in cuts:
    # Append audio up to cut_start
    start_sample = int(round(last_pos * sample_rate))
    end_sample = int(round(cs * sample_rate))
    new_pcm_chunks.append(master_pcm[start_sample:end_sample])
    total_removed_sec += (ce - cs)
    last_pos = ce

# Append remainder of audio
final_sample = int(round(last_pos * sample_rate))
new_pcm_chunks.append(master_pcm[final_sample:])

normalized_pcm = np.concatenate(new_pcm_chunks)
normalized_duration = len(normalized_pcm) / sample_rate

print(f"Normalized audio duration: {normalized_duration:.2f}s (removed {total_removed_sec:.2f}s of excess dead air)")

# Recalibrate word timestamps
normalized_words = []
for w in words:
    normalized_words.append({
        "word": w["word"],
        "start": round(get_shifted_time(w["start"]), 3),
        "end": round(get_shifted_time(w["end"]), 3),
        "is_sentence_end": w["is_sentence_end"]
    })

# Export normalized master audio files (WAV & MP3)
norm_wav_path = os.path.join(OUTPUT_VO_DIR, "voiceover_master_normalized.wav")
norm_mp3_path = os.path.join(OUTPUT_VO_DIR, "voiceover_master_normalized.mp3")

sf.write(norm_wav_path, normalized_pcm, sample_rate)
cmd_mp3 = ["ffmpeg", "-y", "-i", norm_wav_path, "-b:a", "192k", norm_mp3_path]
subprocess.run(cmd_mp3, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
print(f"Saved master normalized audio to:\n  - {norm_mp3_path}\n  - {norm_wav_path}")

# Export words alignment JSON
words_json_path = os.path.join(OUTPUT_VO_DIR, "words_alignment.json")
with open(words_json_path, "w", encoding="utf-8") as f:
    json.dump(normalized_words, f, indent=2)

# ------------------------------------------------------------------------------
# STEP 6: MAP ALL 334 SHOTS TO NORMALIZED VOICEOVER TIMELINE
# ------------------------------------------------------------------------------
print("\n[SHOT MAPPING] Aligning 334 storyboard shots to normalized timestamps...")
shots_mapping = []
cur_word_idx = 0

for row in rows:
    shot_num = int(row[0])
    orig_tc = row[1]
    vo_text = row[2].strip()
    desc = row[3]

    shot_words_tokens = vo_text.split()
    shot_len = len(shot_words_tokens)

    # Match sequential words
    matched_words = []
    for k in range(shot_len):
        if cur_word_idx + k < len(normalized_words):
            matched_words.append(normalized_words[cur_word_idx + k])

    if matched_words:
        shot_start_sec = matched_words[0]["start"]
        shot_end_sec = matched_words[-1]["end"]
        cur_word_idx += shot_len
    else:
        shot_start_sec = shots_mapping[-1]["end_sec"] if shots_mapping else 0.0
        shot_end_sec = shot_start_sec + 1.0

    shots_mapping.append({
        "shot_num": shot_num,
        "vo_text": vo_text,
        "desc": desc,
        "start_sec": shot_start_sec,
        "end_sec": shot_end_sec,
        "duration_sec": round(shot_end_sec - shot_start_sec, 3),
        "image_file": f"shot_{shot_num:03d}.jpg"
    })

# Save shots timing alignment
shots_json_path = os.path.join(OUTPUT_VO_DIR, "shots_timing_alignment.json")
with open(shots_json_path, "w", encoding="utf-8") as f:
    json.dump(shots_mapping, f, indent=2)

print(f"Successfully mapped all {len(shots_mapping)} shots to millisecond-accurate timestamps.")

# ------------------------------------------------------------------------------
# STEP 7: BUILD FCP 7 XML (xmeml v4) TIMELINE FOR PREMIERE PRO & RESOLVE
# ------------------------------------------------------------------------------
print("\n[XML ASSEMBLY] Constructing Final Cut Pro / Premiere Pro XML timeline...")
FPS = 24
total_frames = int(round(normalized_duration * FPS))

def format_tc(seconds, fps=24):
    f = int(round(seconds * fps))
    hours = f // (fps * 3600)
    mins = (f % (fps * 3600)) // (fps * 60)
    secs = (f % (fps * 60)) // fps
    frames = f % fps
    return f"{hours:02d}:{mins:02d}:{secs:02d}:{frames:02d}"

# Build contiguous video clip items (each shot image stays on screen until next shot begins)
video_clipitems_xml = []
for i, s in enumerate(shots_mapping):
    shot_num = s["shot_num"]
    img_name = s["image_file"]
    img_abs_path = os.path.abspath(os.path.join(FINAL_IMAGES_DIR, img_name)).replace("\\", "/")

    start_sec = s["start_sec"]
    # End frame is next shot's start frame to avoid black gaps
    if i + 1 < len(shots_mapping):
        end_sec = shots_mapping[i+1]["start_sec"]
    else:
        end_sec = normalized_duration

    start_frame = int(round(start_sec * FPS))
    end_frame = int(round(end_sec * FPS))
    dur_frames = max(1, end_frame - start_frame)

    clip_xml = f"""            <clipitem id="clipitem-shot-{shot_num:03d}">
              <name>{img_name}</name>
              <duration>{dur_frames}</duration>
              <rate>
                <timebase>{FPS}</timebase>
                <ntsc>FALSE</ntsc>
              </rate>
              <start>{start_frame}</start>
              <end>{end_frame}</end>
              <in>0</in>
              <out>{dur_frames}</out>
              <file id="file-shot-{shot_num:03d}">
                <name>{img_name}</name>
                <pathurl>file://localhost/{img_abs_path}</pathurl>
                <rate>
                  <timebase>{FPS}</timebase>
                  <ntsc>FALSE</ntsc>
                </rate>
                <duration>{dur_frames}</duration>
                <media>
                  <video>
                    <samplecharacteristics>
                      <width>1376</width>
                      <height>768</height>
                    </samplecharacteristics>
                  </video>
                </media>
              </file>
            </clipitem>"""
    video_clipitems_xml.append(clip_xml)

audio_abs_path = os.path.abspath(norm_mp3_path).replace("\\", "/")
audio_clipitem_xml = f"""            <clipitem id="clipitem-master-voiceover">
              <name>voiceover_master_normalized.mp3</name>
              <duration>{total_frames}</duration>
              <rate>
                <timebase>{FPS}</timebase>
                <ntsc>FALSE</ntsc>
              </rate>
              <start>0</start>
              <end>{total_frames}</end>
              <in>0</in>
              <out>{total_frames}</out>
              <file id="file-master-voiceover">
                <name>voiceover_master_normalized.mp3</name>
                <pathurl>file://localhost/{audio_abs_path}</pathurl>
                <rate>
                  <timebase>{FPS}</timebase>
                  <ntsc>FALSE</ntsc>
                </rate>
                <duration>{total_frames}</duration>
                <media>
                  <audio>
                    <samplecharacteristics>
                      <depth>16</depth>
                      <samplerate>44100</samplerate>
                    </samplecharacteristics>
                    <channelcount>2</channelcount>
                  </audio>
                </media>
              </file>
            </clipitem>"""

xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
  <sequence id="sequence-ink-explainers-ancient-humans">
    <name>Ink Explainers - What Did Ancient Humans Actually Do All Day</name>
    <duration>{total_frames}</duration>
    <rate>
      <timebase>{FPS}</timebase>
      <ntsc>FALSE</ntsc>
    </rate>
    <timecode>
      <rate>
        <timebase>{FPS}</timebase>
        <ntsc>FALSE</ntsc>
      </rate>
      <string>00:00:00:00</string>
      <frame>0</frame>
      <displayformat>NDF</displayformat>
    </timecode>
    <media>
      <video>
        <format>
          <samplecharacteristics>
            <rate>
              <timebase>{FPS}</timebase>
              <ntsc>FALSE</ntsc>
            </rate>
            <width>1920</width>
            <height>1080</height>
            <anamorphic>FALSE</anamorphic>
            <pixelaspectratio>square</pixelaspectratio>
            <fielddominance>none</fielddominance>
          </samplecharacteristics>
        </format>
        <track>
{chr(10).join(video_clipitems_xml)}
        </track>
      </video>
      <audio>
        <track>
{audio_clipitem_xml}
        </track>
      </audio>
    </media>
  </sequence>
</xmeml>
"""

with open(XML_OUTPUT_PATH, "w", encoding="utf-8") as f_xml:
    f_xml.write(xml_content)

print(f"Generated NLE Timeline XML:\n  -> {XML_OUTPUT_PATH}")
print(f"Total Sequence Duration: {format_tc(normalized_duration, FPS)} ({total_frames} frames @ {FPS}fps)")
print("\n========================================================")
print("PIPELINE COMPLETED SUCCESSFULLY!")
print("========================================================")
