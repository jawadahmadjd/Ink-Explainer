"""
Stage 3: Full Combined Voiceover Production & Silence Normalization (ElevenLabs)
Generates combined voiceover with millisecond timestamps, enforces SOP silence normalization
(>300ms trimmed to 150ms tail + 150ms head cushion), and exports master MP3/WAV.
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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

import threading

ELEVENLABS_KEY_EVENT = threading.Event()
ELEVENLABS_KEY_EVENT.set()
VOICEOVER_CANCELLED = False

class Stage3CancelledException(Exception):
    """Raised when the user cancels voiceover generation during a key wait."""
    pass

def pause_wait_for_elevenlabs_key(reason: str = "Quota Exceeded"):
    """Pause execution and signal web UI that a fresh ElevenLabs API key is needed."""
    ELEVENLABS_KEY_EVENT.clear()
    try:
        from web_ui import STATE, add_log
        STATE["elevenlabs_key_needed"] = True
        STATE["state"] = "PAUSED_ELEVENLABS_KEY_EXHAUSTED"
        STATE["task_description"] = f"ElevenLabs API Key Pool Exhausted: {reason}. Enter a new API key to resume."
        add_log(f"[STAGE 3 PAUSE] {reason}. Awaiting new API key from user...")
    except Exception as e:
        print(f"[STAGE 3 PAUSE] {reason}. Awaiting new API key... ({e})")

def resume_elevenlabs_key_wait():
    """Resume execution after new ElevenLabs API key is saved."""
    global VOICEOVER_CANCELLED
    VOICEOVER_CANCELLED = False
    try:
        from web_ui import STATE, add_log
        STATE["elevenlabs_key_needed"] = False
        if STATE.get("state") == "PAUSED_ELEVENLABS_KEY_EXHAUSTED":
            STATE["state"] = "RUNNING_VOICEOVER"
            STATE["task_description"] = "Resuming voiceover generation with new ElevenLabs API key..."
        add_log("New ElevenLabs API key received. Resuming voiceover generation...")
    except Exception:
        pass
    ELEVENLABS_KEY_EVENT.set()

def cancel_elevenlabs_key_wait():
    """Signal Stage 3 to cancel waiting, save progress cleanly on disk, and exit."""
    global VOICEOVER_CANCELLED
    VOICEOVER_CANCELLED = True
    try:
        from web_ui import STATE, add_log
        STATE["elevenlabs_key_needed"] = False
        add_log("Cancel received: Terminating key wait and preserving voiceover progress...")
    except Exception:
        pass
    ELEVENLABS_KEY_EVENT.set()

def validate_elevenlabs_api_key(api_key: str) -> dict:
    """Validate ElevenLabs API key and return subscription / balance info."""
    if not api_key or not api_key.strip():
        return {"valid": False, "error": "Empty API key"}
    try:
        resp = requests.get(
            "https://api.elevenlabs.io/v1/user/subscription",
            headers={"xi-api-key": api_key.strip()},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            character_count = data.get("character_count", 0)
            character_limit = data.get("character_limit", 0)
            remaining = max(0, character_limit - character_count)
            tier = data.get("tier", "unknown")
            status = data.get("status", "active")
            return {
                "valid": True,
                "character_count": character_count,
                "character_limit": character_limit,
                "remaining_characters": remaining,
                "tier": tier,
                "status": status
            }
        else:
            return {"valid": False, "error": f"HTTP {resp.status_code}: {resp.text}"}
    except Exception as e:
        return {"valid": False, "error": str(e)}

def generate_chunk_with_timestamps(text: str, chunk_name: str, vo_dir: str, voice_id: str, model_id: str, force_regenerate: bool = False) -> tuple:
    """Generate audio chunk with character-level alignment via ElevenLabs API using key pool rotation and pause/resume."""
    cache_mp3 = os.path.join(vo_dir, f"{chunk_name}_raw.mp3")
    cache_json = os.path.join(vo_dir, f"{chunk_name}_alignment.json")

    if not force_regenerate and os.path.exists(cache_mp3) and os.path.exists(cache_json):
        print(f"  [CACHE HIT] Using existing {chunk_name}...")
        with open(cache_json, "r", encoding="utf-8") as f:
            align_data = json.load(f)
        return cache_mp3, align_data

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": config.ELEVENLABS_VOICE_SETTINGS
    }

    while True:
        if VOICEOVER_CANCELLED:
            raise Stage3CancelledException("Voiceover generation cancelled by user.")

        keys_pool = config.get_elevenlabs_api_keys(force_reload=True)
        if not keys_pool and config.ELEVENLABS_API_KEY:
            keys_pool = [config.ELEVENLABS_API_KEY]
        if not keys_pool:
            pause_wait_for_elevenlabs_key("No ElevenLabs API keys configured in pool")
            ELEVENLABS_KEY_EVENT.wait()
            if VOICEOVER_CANCELLED:
                raise Stage3CancelledException("Voiceover generation cancelled by user.")
            continue

        last_error = None
        key_worked = False

        for idx, api_key in enumerate(keys_pool):
            if VOICEOVER_CANCELLED:
                raise Stage3CancelledException("Voiceover generation cancelled by user.")

            headers = {
                "xi-api-key": api_key,
                "Content-Type": "application/json"
            }
            masked = f"...{api_key[-4:]}" if len(api_key) > 4 else "****"
            print(f"  [API CALL] Generating {chunk_name} ({len(text)} chars) via ElevenLabs Key #{idx+1} ({masked})...")
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=120)
                if resp.status_code == 200:
                    data = resp.json()
                    audio_b64 = data.get("audio_base64")
                    alignment = data.get("alignment", {})
                    audio_bytes = base64.b64decode(audio_b64)
                    with open(cache_mp3, "wb") as f:
                        f.write(audio_bytes)
                    with open(cache_json, "w", encoding="utf-8") as f:
                        json.dump(alignment, f)
                    return cache_mp3, alignment
                else:
                    err_text = resp.text
                    last_error = f"HTTP {resp.status_code}: {err_text}"
                    print(f"  [KEY FAILOVER] ElevenLabs Key #{idx+1} error ({resp.status_code}): {last_error[:100]}. Trying next key...")
                    continue
            except Exception as ex:
                last_error = str(ex)
                print(f"  [KEY FAILOVER] ElevenLabs Key #{idx+1} exception: {ex}. Trying next key...")
                continue

        # All keys in current pool failed
        print(f"\n  [ELEVENLABS POOL EXHAUSTED] All {len(keys_pool)} keys failed. Prompting user for new key...")
        pause_wait_for_elevenlabs_key(f"Quota exceeded across all {len(keys_pool)} keys in pool")
        ELEVENLABS_KEY_EVENT.wait()
        if VOICEOVER_CANCELLED:
            raise Stage3CancelledException("Voiceover generation cancelled by user.")

def build_word_alignments(characters: list, char_starts: list, char_ends: list) -> list:
    """Reconstruct words and their millisecond timing from character alignments."""
    words = []
    curr_chars = []
    word_start = None
    last_end = 0.0

    for ch, st, en in zip(characters, char_starts, char_ends):
        if ch.isspace():
            if curr_chars and word_start is not None:
                word_str = "".join(curr_chars).strip()
                if word_str:
                    words.append({
                        "word": word_str,
                        "start_sec": round(word_start, 3),
                        "end_sec": round(last_end, 3),
                        "start_ms": int(word_start * 1000),
                        "end_ms": int(last_end * 1000)
                    })
                curr_chars = []
                word_start = None
        else:
            if word_start is None:
                word_start = st
            curr_chars.append(ch)
            last_end = en

    if curr_chars and word_start is not None:
        word_str = "".join(curr_chars).strip()
        if word_str:
            words.append({
                "word": word_str,
                "start_sec": round(word_start, 3),
                "end_sec": round(last_end, 3),
                "start_ms": int(word_start * 1000),
                "end_ms": int(last_end * 1000)
            })

    return words

def find_nearest_zero_crossing(audio: np.ndarray, sample_idx: int, window: int = 200) -> int:
    """Find zero-crossing sample nearest to index to prevent audio clicks."""
    start = max(0, sample_idx - window)
    end = min(len(audio) - 1, sample_idx + window)
    if start >= end:
        return sample_idx
    sub = audio[start:end]
    zero_crossings = np.where(np.diff(np.sign(sub)))[0] + start
    if len(zero_crossings) == 0:
        return sample_idx
    closest = zero_crossings[np.argmin(np.abs(zero_crossings - sample_idx))]
    return int(closest)

def run_stage3_voiceover(video_title: str, force_regenerate: bool = False, voice_id: str = None, model_id: str = None) -> dict:
    """
    Execute full combined voiceover production with millisecond word alignment and SOP silence normalization.
    """
    dirs = config.get_project_dirs(video_title)
    vo_dir = dirs["voiceovers_dir"]
    os.makedirs(vo_dir, exist_ok=True)

    active_voice = voice_id or config.ELEVENLABS_VOICE_ID
    active_model = model_id or config.ELEVENLABS_MODEL_ID

    master_csv_path = dirs["master_csv"]
    if not os.path.exists(master_csv_path):
        raise FileNotFoundError(f"Missing master CSV: {master_csv_path}. Run Stage 2 first.")

    with open(master_csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))[1:]

    total_shots = len(rows)

    # 1. Natural paragraph chunking (at sentence boundaries, ~100-115 shots each)
    chunk_size = max(1, total_shots // 3)
    chunk_defs = [
        {"name": "chunk_1", "start_idx": 0, "end_idx": min(chunk_size, total_shots)},
        {"name": "chunk_2", "start_idx": min(chunk_size, total_shots), "end_idx": min(chunk_size * 2, total_shots)},
        {"name": "chunk_3", "start_idx": min(chunk_size * 2, total_shots), "end_idx": total_shots}
    ]
    # Filter empty chunks if small script
    chunk_defs = [cd for cd in chunk_defs if cd["start_idx"] < cd["end_idx"]]

    for cd in chunk_defs:
        cd_rows = rows[cd["start_idx"]:cd["end_idx"]]
        cd["text"] = " ".join(r[2].strip() for r in cd_rows)
        cd["shot_count"] = len(cd_rows)
        cd["char_count"] = len(cd["text"])

    print(f"\n[STAGE 3] ElevenLabs Combined VO Generation for '{video_title}'")
    print(f"Voice ID: {active_voice} | Model ID: {active_model}")
    print(f"Total Chunks: {len(chunk_defs)} | Total Shots: {total_shots}")

    # Check if normalized master already exists and force_regenerate is False
    master_mp3_path = os.path.join(vo_dir, "voiceover_master_normalized.mp3")
    master_wav_path = os.path.join(vo_dir, "voiceover_master_normalized.wav")
    words_align_path = os.path.join(vo_dir, "words_alignment.json")
    shots_align_path = os.path.join(vo_dir, "shots_timing_alignment.json")

    if not force_regenerate and os.path.exists(master_mp3_path) and os.path.exists(words_align_path) and os.path.exists(shots_align_path):
        print(f"[CACHE HIT] Full normalized master VO and alignments already exist in: {vo_dir}")
        with open(words_align_path, "r", encoding="utf-8") as f:
            words = json.load(f)
        with open(shots_align_path, "r", encoding="utf-8") as f:
            shots = json.load(f)
        return {
            "master_mp3": master_mp3_path,
            "master_wav": master_wav_path,
            "words_alignment": words_align_path,
            "shots_alignment": shots_align_path,
            "total_words": len(words),
            "total_shots": len(shots)
        }

    # 2. Generate chunks
    rendered_chunks = []
    for cd in chunk_defs:
        mp3_p, align_d = generate_chunk_with_timestamps(cd["text"], cd["name"], vo_dir, active_voice, active_model)
        rendered_chunks.append({
            "name": cd["name"],
            "mp3_path": mp3_p,
            "alignment": align_d,
            "text": cd["text"],
            "start_shot": cd["start_idx"] + 1,
            "end_shot": cd["end_idx"]
        })

    # 3. Concatenate and convert to WAV
    print("Concatenating audio chunks and decoding to uncompressed WAV...")
    temp_concat_list = os.path.join(vo_dir, "concat_list.txt")
    with open(temp_concat_list, "w", encoding="utf-8") as f:
        for rc in rendered_chunks:
            f.write(f"file '{rc['mp3_path'].replace(os.sep, '/')}'\n")

    raw_combined_wav = os.path.join(vo_dir, "voiceover_raw_combined.wav")
    ffmpeg_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", temp_concat_list,
        "-ar", "44100", "-ac", "1",
        raw_combined_wav
    ]
    subprocess.run(ffmpeg_concat, check=True, capture_output=True)
    if os.path.exists(temp_concat_list):
        os.remove(temp_concat_list)

    # 4. Assemble global word alignment map
    global_words = []
    chunk_time_offset = 0.0

    for rc in rendered_chunks:
        # Get chunk audio duration via soundfile
        c_audio, c_sr = sf.read(rc["mp3_path"])
        c_dur = len(c_audio) / float(c_sr)

        align = rc["alignment"]
        chars = align.get("characters", [])
        starts = align.get("character_start_times_seconds", [])
        ends = align.get("character_end_times_seconds", [])

        c_words = build_word_alignments(chars, starts, ends)
        for w in c_words:
            global_words.append({
                "word": w["word"],
                "start_sec": round(w["start_sec"] + chunk_time_offset, 3),
                "end_sec": round(w["end_sec"] + chunk_time_offset, 3),
                "start_ms": int((w["start_sec"] + chunk_time_offset) * 1000),
                "end_ms": int((w["end_sec"] + chunk_time_offset) * 1000)
            })

        chunk_time_offset += c_dur

    print(f"Total Words Aligned: {len(global_words)}")

    # 5. Map words to sentences/shots
    # Each shot has its VO sentence text
    shot_alignments = []
    word_ptr = 0
    total_w = len(global_words)

    for r in rows:
        shot_num = int(r[0])
        vo_txt = r[2].strip()
        vo_words = vo_txt.split()
        num_w = len(vo_words)

        if num_w == 0:
            last_end = shot_alignments[-1]["end_sec"] if shot_alignments else 0.0
            shot_alignments.append({
                "shot_num": shot_num,
                "voiceover": vo_txt,
                "start_sec": last_end,
                "end_sec": last_end + 1.0,
                "start_ms": int(last_end * 1000),
                "end_ms": int((last_end + 1.0) * 1000)
            })
            continue

        s_start = global_words[min(word_ptr, total_w - 1)]["start_sec"]
        end_idx = min(word_ptr + num_w - 1, total_w - 1)
        s_end = global_words[end_idx]["end_sec"]
        word_ptr = min(word_ptr + num_w, total_w)

        shot_alignments.append({
            "shot_num": shot_num,
            "voiceover": vo_txt,
            "start_sec": s_start,
            "end_sec": s_end,
            "start_ms": int(s_start * 1000),
            "end_ms": int(s_end * 1000)
        })

    # 6. SOP Silence Normalization Engine
    # If silence between shot i and shot i+1 > 300ms, trim to 150ms after current + 150ms before next (300ms total)
    print("Applying SOP Silence Normalization (>300ms trimmed to 150ms tail + 150ms head cushion)...")
    audio, sr = sf.read(raw_combined_wav)
    
    max_silence_s = config.MAX_SILENCE_MS / 1000.0
    tail_cushion_s = config.SILENCE_TAIL_CUSHION_MS / 1000.0
    head_cushion_s = config.SILENCE_HEAD_CUSHION_MS / 1000.0
    allowed_pause_s = tail_cushion_s + head_cushion_s

    audio_segments = []
    last_cut_sample = 0
    time_shift = 0.0

    for i in range(len(shot_alignments) - 1):
        curr_shot = shot_alignments[i]
        next_shot = shot_alignments[i+1]

        pause_duration = next_shot["start_sec"] - curr_shot["end_sec"]
        if pause_duration > max_silence_s:
            # Cut boundary: curr_shot["end_sec"] + tail_cushion_s to next_shot["start_sec"] - head_cushion_s
            cut_start_s = curr_shot["end_sec"] + tail_cushion_s
            cut_end_s = next_shot["start_sec"] - head_cushion_s
            excess_s = cut_end_s - cut_start_s

            if excess_s > 0.02:
                cut_start_samp = find_nearest_zero_crossing(audio, int(cut_start_s * sr))
                cut_end_samp = find_nearest_zero_crossing(audio, int(cut_end_s * sr))

                audio_segments.append(audio[last_cut_sample:cut_start_samp])
                last_cut_sample = cut_end_samp
                time_shift += (cut_end_samp - cut_start_samp) / float(sr)

                # Shift all subsequent shots and words
                for j in range(i + 1, len(shot_alignments)):
                    shot_alignments[j]["start_sec"] -= (cut_end_samp - cut_start_samp) / float(sr)
                    shot_alignments[j]["end_sec"] -= (cut_end_samp - cut_start_samp) / float(sr)
                    shot_alignments[j]["start_ms"] = int(shot_alignments[j]["start_sec"] * 1000)
                    shot_alignments[j]["end_ms"] = int(shot_alignments[j]["end_sec"] * 1000)

                # Also shift global words
                for w in global_words:
                    if w["start_sec"] >= cut_end_s:
                        w["start_sec"] -= (cut_end_samp - cut_start_samp) / float(sr)
                        w["end_sec"] -= (cut_end_samp - cut_start_samp) / float(sr)
                        w["start_ms"] = int(w["start_sec"] * 1000)
                        w["end_ms"] = int(w["end_sec"] * 1000)

    # Append remaining audio
    audio_segments.append(audio[last_cut_sample:])
    normalized_audio = np.concatenate(audio_segments)

    # Save normalized WAV
    sf.write(master_wav_path, normalized_audio, sr, subtype="PCM_16")

    # Encode normalized MP3 at 192k
    ffmpeg_mp3 = [
        "ffmpeg", "-y", "-i", master_wav_path,
        "-codec:a", "libmp3lame", "-b:a", "192k",
        master_mp3_path
    ]
    subprocess.run(ffmpeg_mp3, check=True, capture_output=True)

    # Remove temporary raw combined wav
    if os.path.exists(raw_combined_wav):
        os.remove(raw_combined_wav)

    # Save final alignment JSONs
    with open(words_align_path, "w", encoding="utf-8") as f:
        json.dump(global_words, f, indent=2)
    with open(shots_align_path, "w", encoding="utf-8") as f:
        json.dump(shot_alignments, f, indent=2)

    total_dur_sec = round(len(normalized_audio) / float(sr), 2)
    print(f"\n-> [STAGE 3 COMPLETE] Master VO created: {master_mp3_path} ({total_dur_sec}s, {len(global_words)} words)")
    return {
        "master_mp3": master_mp3_path,
        "master_wav": master_wav_path,
        "words_alignment": words_align_path,
        "shots_alignment": shots_align_path,
        "total_words": len(global_words),
        "total_shots": len(shot_alignments),
        "duration_sec": total_dur_sec
    }

def get_stage3_progress(video_title: str) -> dict:
    """Get current voiceover progress and completed chunks for a project."""
    dirs = config.get_project_dirs(video_title)
    vo_dir = dirs["voiceovers_dir"]
    prog_file = os.path.join(vo_dir, "stage3_progress.json")
    completed = []
    if os.path.exists(prog_file):
        try:
            with open(prog_file, "r", encoding="utf-8") as f:
                completed = json.load(f)
        except Exception:
            pass
    raw_mp3s = [f for f in os.listdir(vo_dir) if f.endswith(".mp3")] if os.path.exists(vo_dir) else []
    master_exists = os.path.exists(os.path.join(dirs["finals_dir"], "voiceover_master_normalized.mp3"))
    status = "COMPLETED" if master_exists else ("PAUSED_KEY_NEEDED" if not ELEVENLABS_KEY_EVENT.is_set() else ("IN_PROGRESS" if completed else "NOT_STARTED"))
    return {
        "status": status,
        "completed_chunks": len(completed) or len(raw_mp3s),
        "project_title": video_title
    }

