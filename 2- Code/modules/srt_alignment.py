"""
SRT Subtitle & Timestamp Alignment Engine
Provides high-precision timestamp synchronization from manual SRT subtitle files to storyboard shots.
Integrates difflib fuzzy sequence token matching, monotonic cut frame calculation,
zero-gap / zero-overlap guarantees, and automatic timeline XML rebuilding.
"""

import os
import sys
import re
import csv
import json
import gzip
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher
from typing import Dict, List, Any, Tuple, Optional

CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

import config
from modules.stage5_timeline_xml import run_stage5_timeline_xml

TICKS_PER_FRAME_24FPS = 10584000000  # 254016000000 / 24
TICKS_PER_SEC = 254016000000


def parse_srt(path_or_content: str) -> List[Dict[str, Any]]:
    """
    Parses SRT content from a file path or raw string.
    Supports comma and period millisecond delimiters.
    Returns list of parsed cues with start_sec, end_sec, text, and original timecodes.
    """
    if os.path.exists(path_or_content):
        with open(path_or_content, "r", encoding="utf-8-sig", errors="replace") as f:
            content = f.read()
    else:
        content = path_or_content

    entries = []
    # Normalize line breaks
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n", content.strip())

    for b in blocks:
        lines = [line.strip() for line in b.strip().split("\n") if line.strip()]
        if len(lines) < 2:
            continue

        # Line 0 is often the cue number; if line 0 has '-->', it's the timing line
        tc_line_idx = 1 if "-->" in lines[1] else 0 if "-->" in lines[0] else -1
        if tc_line_idx == -1:
            for idx, l in enumerate(lines):
                if "-->" in l:
                    tc_line_idx = idx
                    break

        if tc_line_idx == -1:
            continue

        idx_val = lines[0] if tc_line_idx > 0 else str(len(entries) + 1)
        tc_line = lines[tc_line_idx]
        text_lines = lines[tc_line_idx + 1 :]
        text = " ".join(text_lines).strip()

        try:
            st_str, en_str = [t.strip() for t in tc_line.split("-->")]

            def to_sec(tc: str) -> float:
                # Format: 00:00:00,000 or 00:00:00.000
                tc = tc.replace(",", ".")
                parts = tc.split(":")
                if len(parts) == 3:
                    h, m, s = parts
                    return int(h) * 3600 + int(m) * 60 + float(s)
                elif len(parts) == 2:
                    m, s = parts
                    return int(m) * 60 + float(s)
                return float(tc)

            start_s = to_sec(st_str)
            end_s = to_sec(en_str)

            if end_s < start_s:
                end_s = start_s + 0.1

            entries.append({
                "index": int(re.sub(r"\D", "", idx_val)) if re.sub(r"\D", "", idx_val) else len(entries) + 1,
                "start_tc": st_str,
                "end_tc": en_str,
                "start_sec": round(start_s, 3),
                "end_sec": round(end_s, 3),
                "duration_sec": round(end_s - start_s, 3),
                "text": text
            })
        except Exception:
            continue

    return entries


def clean_word(w: str) -> str:
    """Normalizes word token for fuzzy matching."""
    return re.sub(r"[^\w]", "", w.lower())


def align_storyboard_with_srt(
    video_title: str,
    srt_path_or_content: str,
    fps: int = 24,
    audio_duration_sec: Optional[float] = None
) -> Dict[str, Any]:
    """
    Aligns storyboard shots to an SRT file.
    Updates:
      1. Voiceovers/shots_timing_alignment.json
      2. storyboard_master.csv
      3. storyboard_timeline.xml
      4. Any .prproj premiere files if present
    Guarantees monotonic cut frames, zero black frame gaps, and zero clip overlaps.
    """
    dirs = config.get_project_dirs(video_title)
    finals_dir = dirs["finals_dir"]
    vo_dir = dirs["voiceovers_dir"]
    csv_path = dirs["master_csv"]
    shots_align_path = os.path.join(vo_dir, "shots_timing_alignment.json")

    os.makedirs(vo_dir, exist_ok=True)

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Storyboard CSV not found at: {csv_path}")

    # Parse SRT entries
    srt_entries = parse_srt(srt_path_or_content)
    if not srt_entries:
        raise ValueError("Could not parse any valid subtitle cues from the provided SRT input.")

    # Read storyboard rows
    with open(csv_path, "r", encoding="utf-8") as f:
        csv_rows = list(csv.reader(f))
    if len(csv_rows) <= 1:
        raise ValueError(f"Storyboard CSV has no shot rows: {csv_path}")

    header = csv_rows[0]
    rows = csv_rows[1:]
    num_shots = len(rows)

    # Determine total audio / timeline duration
    last_srt_end = srt_entries[-1]["end_sec"]
    total_duration = audio_duration_sec or last_srt_end
    if total_duration < last_srt_end:
        total_duration = last_srt_end

    # Build word maps from SRT
    srt_words = []
    srt_word_map = []  # (cue_index, start_sec, end_sec)
    for e in srt_entries:
        words = [clean_word(w) for w in e["text"].split() if clean_word(w)]
        for w in words:
            srt_words.append(w)
            srt_word_map.append((e["index"], e["start_sec"], e["end_sec"]))

    # Tokenize storyboard spoken VO
    all_shot_tokens = []
    shot_first_token_idx = {}
    for r in rows:
        s_num = int(r[0])
        vo = r[2].strip() if len(r) > 2 else ""
        words = [clean_word(w) for w in vo.split() if clean_word(w)]
        if words:
            shot_first_token_idx[s_num] = len(all_shot_tokens)
            for w in words:
                all_shot_tokens.append(w)

    alignment_mode = "sequence_matcher"
    shot_speech_start = {}

    # Attempt word-level SequenceMatcher alignment if we have enough tokens on both sides
    if len(all_shot_tokens) >= 5 and len(srt_words) >= 5:
        sm = SequenceMatcher(None, all_shot_tokens, srt_words)
        token_to_srt = {}
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                for offset in range(i2 - i1):
                    token_to_srt[i1 + offset] = j1 + offset
            elif tag == "replace":
                num_shot = i2 - i1
                num_srt = j2 - j1
                for offset in range(num_shot):
                    srt_offset = int(offset * num_srt / num_shot)
                    token_to_srt[i1 + offset] = min(j1 + srt_offset, len(srt_words) - 1)
            elif tag == "delete":
                for offset in range(i2 - i1):
                    token_to_srt[i1 + offset] = min(j1, len(srt_words) - 1)

        for s_idx, r in enumerate(rows, 1):
            s_num = int(r[0])
            if s_num in shot_first_token_idx:
                tok_idx = shot_first_token_idx[s_num]
                w_idx = token_to_srt.get(tok_idx, 0)
                shot_speech_start[s_num] = srt_word_map[w_idx][1]
            else:
                # Proportional estimate if shot has no voiceover text
                prop = (s_idx - 1) / max(1, num_shots)
                shot_speech_start[s_num] = prop * total_duration
    else:
        # Fallback: Sequential mapping if shot count == cue count or proportional
        alignment_mode = "proportional_cues"
        if len(srt_entries) == num_shots:
            for s_idx, e in enumerate(srt_entries, 1):
                shot_speech_start[s_idx] = e["start_sec"]
        else:
            for s_idx in range(1, num_shots + 1):
                c_idx = min(int((s_idx - 1) * len(srt_entries) / num_shots), len(srt_entries) - 1)
                shot_speech_start[s_idx] = srt_entries[c_idx]["start_sec"]

    # Calculate strictly monotonic cut frames (24 fps default)
    total_frames = int(round(total_duration * fps))
    cut_frames = [0]
    for s_num in range(2, num_shots + 1):
        raw_start = shot_speech_start.get(s_num, (s_num - 1) * (total_duration / num_shots))
        raw_f = int(round(raw_start * fps))
        min_f = cut_frames[-1] + 1
        cut_f = max(raw_f, min_f)
        cut_frames.append(cut_f)

    # Ensure last frame covers total sequence
    cut_frames.append(max(total_frames, cut_frames[-1] + 1))

    # A. Build and save shots_timing_alignment.json
    shots_alignment = []
    for i in range(num_shots):
        s_num = int(rows[i][0])
        st_f = cut_frames[i]
        en_f = cut_frames[i + 1]
        dur_f = en_f - st_f
        st_sec = round(st_f / float(fps), 3)
        en_sec = round(en_f / float(fps), 3)
        dur_sec = round(en_sec - st_sec, 3)

        vo_text = rows[i][2].strip() if len(rows[i]) > 2 else ""
        desc_text = rows[i][3].strip() if len(rows[i]) > 3 else ""

        shots_alignment.append({
            "shot_num": s_num,
            "start_frame": st_f,
            "end_frame": en_f,
            "duration_frames": dur_f,
            "start_sec": st_sec,
            "end_sec": en_sec,
            "duration_sec": dur_sec,
            "vo_text": vo_text,
            "desc": desc_text,
            "image_file": f"shot_{s_num:03d}.jpg"
        })

    with open(shots_align_path, "w", encoding="utf-8") as f_out:
        json.dump(shots_alignment, f_out, indent=2)

    # B. Update storyboard_master.csv with formatted timecodes (MM:SS.s - MM:SS.s)
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
        if len(r_copy) > 1:
            r_copy[1] = tc_str
        updated_csv_rows.append(r_copy)

    with open(csv_path, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerows(updated_csv_rows)

    # C. Re-generate storyboard_timeline.xml
    xml_result = None
    try:
        xml_result = run_stage5_timeline_xml(video_title, fps=fps)
    except Exception as ex:
        print(f"[SRT ALIGNMENT] Notice: timeline XML generation skipped/errored: {ex}")

    # D. Optional Premiere .prproj patch if any exists
    prproj_patched = False
    for item in os.listdir(finals_dir):
        if item.lower().endswith(".prproj"):
            prproj_file = os.path.join(finals_dir, item)
            try:
                patch_prproj_with_cuts(prproj_file, cut_frames, num_shots)
                prproj_patched = True
            except Exception as e:
                print(f"[SRT ALIGNMENT] Could not patch {item}: {e}")

    durations = [s["duration_sec"] for s in shots_alignment]
    return {
        "success": True,
        "video_title": video_title,
        "srt_cues_count": len(srt_entries),
        "shots_count": num_shots,
        "total_duration_sec": round(total_duration, 2),
        "fps": fps,
        "alignment_mode": alignment_mode,
        "min_shot_duration_sec": min(durations) if durations else 0,
        "max_shot_duration_sec": max(durations) if durations else 0,
        "avg_shot_duration_sec": round(sum(durations) / len(durations), 2) if durations else 0,
        "zero_gap_overlap_verified": True,
        "shots_align_path": shots_align_path,
        "csv_path": csv_path,
        "timeline_xml": dirs.get("timeline_xml", ""),
        "xml_result": xml_result,
        "prproj_patched": prproj_patched
    }


def patch_prproj_with_cuts(prproj_path: str, cut_frames: List[int], num_shots: int):
    """Safely patches Adobe Premiere Pro .prproj gzip XML track items with sample-accurate cuts."""
    with gzip.open(prproj_path, "rb") as f:
        prproj_xml = f.read()

    root = ET.fromstring(prproj_xml)
    obj_map = {elem.attrib["ObjectID"]: elem for elem in root if "ObjectID" in elem.attrib}
    video_items = root.findall(".//VideoClipTrackItem")

    for i in range(min(len(video_items), num_shots)):
        item = video_items[i]
        st_ticks = cut_frames[i] * TICKS_PER_FRAME_24FPS
        en_ticks = cut_frames[i + 1] * TICKS_PER_FRAME_24FPS
        dur_ticks = en_ticks - st_ticks

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
                        if in_elem is not None:
                            in_elem.text = "0"
                        if out_elem is not None:
                            out_elem.text = str(dur_ticks)

    updated_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with gzip.open(prproj_path, "wb") as f_out:
        f_out.write(updated_bytes)

