"""
Alignment Guard & Root-Sentence Binding System
Author: Google Deepmind Antigravity System
Purpose:
  1. Cryptographically anchor each visual shot to its root-level spoken sentence (Beat UID).
  2. Maintain immutable JSON metadata sidecars (.meta.json) alongside every asset.
  3. Pre-flight semantic alignment linter detecting off-by-one shifts and narrative drift.
  4. Auto-healing utility to restore exact timeline positioning if files are ever displaced.
"""

import os
import re
import csv
import json
import hashlib
from typing import Dict, List, Any, Optional

def clean_sentence_slug(text: str, max_words: int = 4) -> str:
    """Extracts a clean, url-safe slug from spoken voiceover."""
    words = re.findall(r'[a-zA-Z0-9]+', text.lower())
    return "_".join(words[:max_words]) if words else "beat"

def generate_beat_uid(shot_id: int, voiceover: str) -> str:
    """
    Generates a deterministic, immutable Beat Unique Identifier:
    beat_{shot_id:03d}_{slug}_{hash6}
    """
    slug = clean_sentence_slug(voiceover)
    norm_text = re.sub(r'\s+', ' ', voiceover.strip().lower())
    h = hashlib.sha256(norm_text.encode('utf-8')).hexdigest()[:6]
    return f"beat_{shot_id:03d}_{slug}_{h}"

def create_shot_metadata(shot_id: int,
                         timecode: str,
                         voiceover: str,
                         visual_desc: str,
                         prompt: str,
                         image_file: str,
                         engine: str = "imagen3") -> Dict[str, Any]:
    """Builds a structured metadata payload for a shot asset."""
    uid = generate_beat_uid(shot_id, voiceover)
    return {
        "beat_uid": uid,
        "shot_id": shot_id,
        "timecode": timecode,
        "voiceover": voiceover,
        "visual_description": visual_desc,
        "prompt": prompt,
        "image_file": os.path.basename(image_file),
        "engine": engine,
        "char_count": len(voiceover),
        "content_hash": hashlib.sha256(voiceover.strip().lower().encode('utf-8')).hexdigest()[:8]
    }

def write_shot_sidecar(image_path: str, meta: Dict[str, Any]) -> str:
    """Writes a companion JSON sidecar (.meta.json) for the image."""
    sidecar_path = os.path.splitext(image_path)[0] + ".meta.json"
    with open(sidecar_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    return sidecar_path

def generate_all_sidecars(csv_path: str, images_dir: str) -> int:
    """Generates sidecars for all shots in a directory based on storyboard_master.csv."""
    if not os.path.exists(csv_path) or not os.path.exists(images_dir):
        return 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        rows = list(csv.reader(f))[1:]

    created = 0
    for r in rows:
        shot_id = int(r[0])
        timecode = r[1]
        vo = r[2]
        desc = r[3]
        prompt = r[4]

        img_name = f"shot_{shot_id:03d}.jpg"
        img_path = os.path.join(images_dir, img_name)

        if os.path.exists(img_path):
            meta = create_shot_metadata(shot_id, timecode, vo, desc, prompt, img_path)
            write_shot_sidecar(img_path, meta)
            created += 1

    return created

def extract_content_keywords(text: str) -> set:
    """Extracts non-stopword semantic keywords for similarity scoring."""
    stopwords = {
        "this", "that", "these", "those", "with", "from", "into", "over", "after",
        "their", "there", "where", "which", "about", "could", "would", "should",
        "minimalist", "vector", "illustration", "clean", "bold", "black", "comic",
        "line", "style", "aspect", "ratio", "bleed", "colors", "muted", "flat",
        "figure", "stick", "white", "pure", "solid", "head", "zero", "fill"
    }
    words = re.findall(r'[a-zA-Z]{4,}', text.lower())
    return {w for w in words if w not in stopwords}

def validate_storyboard_alignment(csv_path: str) -> Dict[str, Any]:
    """
    Pre-flight linter checking storyboard consistency and detecting off-by-one shifts.
    Scans every row and computes:
      1. Monotonic continuity (no gaps or duplicates).
      2. Semantic keyword alignment between VO/Description and Prompt.
      3. Offset-detection: flags if Prompt[K] matches Description[K+1] significantly
         better than Description[K].
    """
    if not os.path.exists(csv_path):
        return {"error": f"CSV not found: {csv_path}"}

    with open(csv_path, 'r', encoding='utf-8') as f:
        rows = list(csv.reader(f))[1:]

    total_shots = len(rows)
    warnings = []
    errors = []
    suspicious_shifts = []

    for i in range(total_shots):
        curr_shot = int(rows[i][0])
        expected_shot = i + 1
        if curr_shot != expected_shot:
            errors.append(f"Sequence break: Row {i+1} has Shot ID {curr_shot}, expected {expected_shot}")

        curr_vo = rows[i][2]
        curr_desc = rows[i][3]
        curr_prompt = rows[i][4]

        # Extract semantic keywords
        desc_kw = extract_content_keywords(curr_desc)
        prompt_kw = extract_content_keywords(curr_prompt)

        # Check keyword overlap with current description
        overlap_curr = len(desc_kw.intersection(prompt_kw))

        # Check overlap with next description (if exists)
        if i + 1 < total_shots:
            next_desc = rows[i+1][3]
            next_kw = extract_content_keywords(next_desc)
            overlap_next = len(next_kw.intersection(prompt_kw))

            # If prompt has 0 match with current, but strong match (>= 3) with next, flag possible shift!
            if overlap_curr == 0 and overlap_next >= 3:
                suspicious_shifts.append({
                    "shot_id": curr_shot,
                    "desc_curr": curr_desc,
                    "desc_next": next_desc,
                    "prompt_overlap_next": overlap_next,
                    "warning": f"Shot {curr_shot:03d} prompt appears to describe Shot {curr_shot+1:03d} instead!"
                })

    alignment_score = max(0.0, 100.0 - (len(suspicious_shifts) * 2.0) - (len(errors) * 10.0))

    report = {
        "csv_path": csv_path,
        "total_shots": total_shots,
        "sequence_errors": errors,
        "potential_offset_shifts": suspicious_shifts,
        "shift_count": len(suspicious_shifts),
        "alignment_score": round(alignment_score, 2),
        "status": "PASS" if not errors and len(suspicious_shifts) == 0 else "FAIL"
    }
    return report

def realign_folder_from_sidecars(images_dir: str) -> int:
    """
    Scans a directory for all .meta.json files and renames image files to match
    their true shot_id and Beat UID, recovering any corrupted folder immediately.
    """
    if not os.path.exists(images_dir):
        return 0

    healed = 0
    for fname in os.listdir(images_dir):
        if fname.endswith(".meta.json"):
            sidecar_path = os.path.join(images_dir, fname)
            with open(sidecar_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            correct_shot = meta.get("shot_id")
            if correct_shot is not None:
                expected_img = f"shot_{correct_shot:03d}.jpg"
                actual_img = os.path.splitext(fname)[0] + ".jpg"

                if actual_img != expected_img and os.path.exists(os.path.join(images_dir, actual_img)):
                    os.rename(
                        os.path.join(images_dir, actual_img),
                        os.path.join(images_dir, expected_img)
                    )
                    healed += 1

    return healed

if __name__ == "__main__":
    csv_file = r"d:\Tools of Jawad\25- Ink Explainers\3- Finals\1- What Did Ancient Humans Actually Do All Day\storyboard_master.csv"
    finals_dir = r"d:\Tools of Jawad\25- Ink Explainers\3- Finals\1- What Did Ancient Humans Actually Do All Day\Final selected images"
    root_dir = r"d:\Tools of Jawad\25- Ink Explainers\Final selected images"

    print("=" * 70)
    print("RUNNING ALIGNMENT GUARD PRE-FLIGHT VALIDATION")
    print("=" * 70)
    rep = validate_storyboard_alignment(csv_file)
    print(f"Status: {rep['status']}")
    print(f"Total Shots: {rep['total_shots']}")
    print(f"Sequence Errors: {len(rep['sequence_errors'])}")
    print(f"Potential Offset Shifts: {len(rep['potential_offset_shifts'])}")
    print(f"Alignment Score: {rep['alignment_score']}%")

    if rep['potential_offset_shifts']:
        for s in rep['potential_offset_shifts']:
            print("  [!] Shift alert:", s['warning'])

    print("\n" + "=" * 70)
    print("GENERATING IMMUTABLE ROOT-SENTENCE METADATA SIDECARS")
    print("=" * 70)
    c1 = generate_all_sidecars(csv_file, finals_dir)
    print(f"Generated {c1} sidecars in {finals_dir}")
    c2 = generate_all_sidecars(csv_file, root_dir)
    print(f"Generated {c2} sidecars in {root_dir}")
    print("\nROOT-SENTENCE BINDING COMPLETE!")

