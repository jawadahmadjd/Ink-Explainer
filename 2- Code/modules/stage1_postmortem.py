"""
Stage 1: Video Ingestion & Forensic Postmortem
Extracts YouTube metadata, video reference, subtitles, scene cuts, audio LUFS profile, and generates Postmortem Report.
"""

import os
import sys
import json
import re
import subprocess
import shutil
from pathlib import Path

# Add parent to path for config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def check_dependencies():
    """Verify yt-dlp, ffmpeg, and ffprobe are available."""
    missing = []
    for cmd in ["yt-dlp", "ffmpeg", "ffprobe"]:
        if not shutil.which(cmd):
            missing.append(cmd)
    if missing:
        raise RuntimeError(f"Required system tools missing: {', '.join(missing)}. Please install them.")

def clean_vtt_subtitles(vtt_path: str) -> str:
    """Parse a WebVTT file and extract clean, deduplicated continuous spoken text."""
    if not os.path.exists(vtt_path):
        return ""
    
    with open(vtt_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    clean_lines = []
    seen = set()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("WEBVTT") or "-->" in line or line.isdigit() or line.startswith("Kind:") or line.startswith("Language:") or line.startswith("NOTE") or line.startswith("STYLE") or line.startswith("Region:"):
            continue
        # Remove formatting tags like <c>, </c>, <00:00:00.000>
        text = re.sub(r"<[^>]+>", "", line).strip()
        if text and text not in seen:
            clean_lines.append(text)
            seen.add(text)

    full_text = " ".join(clean_lines)
    # Normalize spaces
    full_text = re.sub(r"\s+", " ", full_text).strip()
    return full_text

def run_stage1_postmortem(video_url: str, custom_title: str = None) -> dict:
    """
    Execute complete Stage 1 forensic postmortem on a reference video URL.
    Returns dictionary with all extracted file paths and forensic metrics.
    """
    check_dependencies()
    print(f"\n[STAGE 1] Ingesting video URL: {video_url}")

    # 1. Fetch metadata via yt-dlp
    print("Fetching video metadata via yt-dlp...")
    meta_cmd = ["yt-dlp", "--dump-json", "--no-warnings", video_url]
    res = subprocess.run(meta_cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if res.returncode != 0:
        raise RuntimeError(f"yt-dlp failed to fetch metadata: {res.stderr.strip()}")

    info = json.loads(res.stdout)
    if custom_title:
        video_title = config.sanitize_title(custom_title)
    else:
        video_title = config.get_next_project_folder_name(info.get("title", "Ink Explainer Video"))
    dirs = config.get_project_dirs(video_title)
    pm_dir = dirs["postmortem_dir"]
    os.makedirs(pm_dir, exist_ok=True)

    # Save raw video_info.json
    info_json_path = os.path.join(pm_dir, "video_info.json")
    with open(info_json_path, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)

    duration = info.get("duration", 0)
    channel = info.get("uploader", info.get("channel", "Unknown Channel"))

    # 2. Download low-res video (video_low.mp4)
    video_low_path = os.path.join(pm_dir, "video_low.mp4")
    if not os.path.exists(video_low_path):
        print("Downloading reference video (low-res MP4)...")
        dl_cmd = [
            "yt-dlp",
            "-f", "worstvideo[ext=mp4]+worstaudio[ext=m4a]/worstvideo+worstaudio/worst[ext=mp4]/worst/best",
            "--merge-output-format", "mp4",
            "-o", video_low_path,
            video_url
        ]
        subprocess.run(dl_cmd, check=True)
    else:
        print(f"Reference video already exists at: {video_low_path}")

    # 3. Download subtitles / VTT
    vtt_path = os.path.join(pm_dir, "transcript.en-orig.vtt")
    if not os.path.exists(vtt_path):
        print("Extracting subtitles...")
        sub_cmd = [
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang", "en",
            "--skip-download",
            "-o", os.path.join(pm_dir, "transcript"),
            video_url
        ]
        subprocess.run(sub_cmd, check=False)
        # Find any generated .vtt
        for f in os.listdir(pm_dir):
            if f.startswith("transcript") and f.endswith(".vtt"):
                if f != "transcript.en-orig.vtt":
                    os.replace(os.path.join(pm_dir, f), vtt_path)
                break

    # 4. Clean transcript text
    clean_text = clean_vtt_subtitles(vtt_path)
    clean_txt_path = os.path.join(pm_dir, "clean_transcript.txt")
    if clean_text:
        with open(clean_txt_path, "w", encoding="utf-8") as f:
            f.write(clean_text)
    elif os.path.exists(clean_txt_path):
        with open(clean_txt_path, "r", encoding="utf-8") as f:
            clean_text = f.read()

    word_count = len(clean_text.split()) if clean_text else 0
    wpm = round((word_count / (duration / 60.0)), 1) if duration > 0 else 0.0

    # 5. Scene Cut Detection via FFmpeg
    cuts_json_path = os.path.join(pm_dir, "cuts_data.json")
    cuts_list = []
    if not os.path.exists(cuts_json_path) and os.path.exists(video_low_path):
        print("Detecting scene cuts via FFmpeg scene filter...")
        # Use ffprobe / ffmpeg to detect scene changes
        ff_cmd = [
            "ffprobe",
            "-show_frames",
            "-of", "compact=p=0",
            "-show_entries", "frame=pkt_pts_time,pict_type",
            "-f", "lavfi",
            f"movie='{video_low_path.replace(os.sep, '/')}',select='gt(scene,0.35)'"
        ]
        res = subprocess.run(ff_cmd, capture_output=True, text=True, check=False)
        pts_matches = re.findall(r"pkt_pts_time=([0-9.]+)", res.stdout)
        cut_times = [0.0] + sorted(list(set(float(t) for t in pts_matches)))
        
        for i in range(len(cut_times)):
            start_t = cut_times[i]
            end_t = cut_times[i+1] if i + 1 < len(cut_times) else float(duration)
            cuts_list.append({
                "shot_index": i + 1,
                "start_sec": round(start_t, 2),
                "end_sec": round(end_t, 2),
                "duration": round(end_t - start_t, 2)
            })

        with open(cuts_json_path, "w", encoding="utf-8") as f:
            json.dump(cuts_list, f, indent=2)
    elif os.path.exists(cuts_json_path):
        with open(cuts_json_path, "r", encoding="utf-8") as f:
            cuts_list = json.load(f)

    scene_cuts_count = len(cuts_list)
    avg_cut_interval = round(duration / scene_cuts_count, 2) if scene_cuts_count > 0 else 2.5

    # 6. Audio Forensic Profile via FFmpeg ebur128
    lufs = -14.0
    lra = 3.0
    true_peak = -1.0
    if os.path.exists(video_low_path):
        print("Analyzing audio loudness profile (EBU R128)...")
        ebur_cmd = [
            "ffmpeg", "-i", video_low_path,
            "-af", "ebur128=framelog=verbose",
            "-f", "null", "-"
        ]
        ebur_res = subprocess.run(ebur_cmd, capture_output=True, text=True, check=False)
        m_lufs = re.search(r"Integrated loudness:\s+I:\s+([-\d.]+)\s+LUFS", ebur_res.stderr)
        m_lra = re.search(r"Loudness range:\s+LRA:\s+([-\d.]+)\s+LU", ebur_res.stderr)
        m_tp = re.search(r"True peak:\s+Peak:\s+([-\d.]+)\s+dBFS", ebur_res.stderr)
        if m_lufs: lufs = float(m_lufs.group(1))
        if m_lra: lra = float(m_lra.group(1))
        if m_tp: true_peak = float(m_tp.group(1))

    # 7. Generate README_POSTMORTEM_REPORT.md
    report_md_path = os.path.join(pm_dir, "README_POSTMORTEM_REPORT.md")
    report_content = f"""# Master Forensic Postmortem: "{video_title}"

## 1. Reference Video Identity
- **Video Title**: {video_title}
- **Creator / Channel**: {channel}
- **URL**: {video_url}
- **Duration**: {int(duration // 60)}m {int(duration % 60)}s ({duration:.2f}s)
- **Total Word Count**: {word_count} words
- **Average Pacing**: {wpm} Words Per Minute (WPM)
- **Scene Cuts**: {scene_cuts_count} discrete cuts
- **Average Cut Interval**: {avg_cut_interval} seconds per shot

---

## 2. Audio & Voiceover Forensic Profile
- **Integrated Loudness**: {lufs:.2f} LUFS (Broadcast standard: -14 to -12 LUFS)
- **Loudness Range (LRA)**: {lra:.1f} LU
- **True Peak**: {true_peak:.1f} dBFS
- **Delivery**: Conversational, intimate, rhythmic explainer narration.

---

## 3. Visual Pacing & Art Direction Standards
- **Art Language**: Minimalist hand-drawn 2D vector comic line art, bold black ink doodle contours.
- **Character Standard**: Minimalist white-filled black-outlined stick figures (MinutePhysics / Casually Explained style: solid white head fill, bold black contour outline, simple stick limbs, 0 flesh skin tones, 0 realistic anatomy).
- **Framing**: Edge-to-edge full bleed widescreen (16:9), grounded background environments with zero white margins.
- **Cut Cadence**: Paced at ~{avg_cut_interval}s per image cut.

---

## 4. Generated Artifacts
- `video_low.mp4`: Reference copy.
- `video_info.json`: YouTube metadata and tags.
- `transcript.en-orig.vtt`: Timecoded original subtitles.
- `clean_transcript.txt`: Clean spoken narration.
- `cuts_data.json`: Millisecond-accurate scene cuts detected via FFmpeg.
"""
    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write(report_content.strip() + "\n")

    # 8. Auto-ingest into AI Learning Codex
    try:
        from learning.learning_engine import ingest_postmortem_to_codex
        ingest_postmortem_to_codex(pm_dir)
    except Exception as e:
        print(f"[CODEX INGEST NOTICE] {e}")

    print(f"\n-> [STAGE 1 COMPLETE] Postmortem Report generated at: {report_md_path}")
    return {
        "title": video_title,
        "duration": duration,
        "word_count": word_count,
        "cuts_count": scene_cuts_count,
        "lufs": lufs,
        "lra": lra,
        "postmortem_dir": pm_dir,
        "report_md": report_md_path,
        "clean_transcript": clean_txt_path,
        "cuts_json": cuts_json_path,
        "video_low": video_low_path
    }
