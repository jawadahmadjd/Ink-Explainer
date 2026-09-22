"""
Central Configuration & Environment Loader for Ink Explainer Autonomous Pipeline
Defines directories, API credentials, silence rules, model cascades, and scoring parameters.
"""

import os
import sys
import re
import json
from pathlib import Path
from dotenv import load_dotenv

# Ensure safe UTF-8 terminal encoding on Windows without charmap crashes
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(ENV_FILE)

def ensure_system_paths():
    """Ensures static FFmpeg, FFprobe, and local bin tools are registered in system PATH."""
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()
    except Exception:
        pass
    try:
        import imageio_ffmpeg
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_bin and os.path.exists(ffmpeg_bin):
            ffmpeg_dir = os.path.dirname(ffmpeg_bin)
            if ffmpeg_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
    except Exception:
        pass

ensure_system_paths()

# ------------------------------------------------------------------------------
# DIRECTORY PATHS
# ------------------------------------------------------------------------------
CODE_DIR = os.path.join(PROJECT_ROOT, "2- Code")
POSTMORTEM_ROOT = os.path.join(PROJECT_ROOT, "1- Postmartum")
FINALS_ROOT = os.path.join(PROJECT_ROOT, "3- Finals")
ROOT_CANONICAL_IMAGES_DIR = os.path.join(PROJECT_ROOT, "Final selected images")

def sanitize_title(title: str) -> str:
    # Strip illegal Windows path characters (< > : " / \ | ? *)
    clean = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_", "'", ".", "(", ")")).strip()
    clean = re.sub(r"\s+", " ", clean)
    return clean

KNOWN_NICHES = ["history", "finance", "medical", "horror", "engineering"]

def get_all_niche_names() -> list:
    """Discovers all niche directories from disk and defaults."""
    niches = set(KNOWN_NICHES)
    for root in [POSTMORTEM_ROOT, FINALS_ROOT]:
        if os.path.exists(root):
            for entry in os.listdir(root):
                full = os.path.join(root, entry)
                if os.path.isdir(full) and not entry.startswith(".") and not re.match(r"^\d+\s*-\s*", entry):
                    niches.add(entry.lower())
    return sorted(list(niches))

def resolve_project_niche_and_title(video_title: str, niche: str = None) -> tuple:
    """
    Intelligently resolves the niche and clean folder name for any project.
    Handles:
      1. Explicit path with slash: 'finance/1- Title' -> ('finance', '1- Title')
      2. Explicit niche argument: '1- Title', niche='finance' -> ('finance', '1- Title')
      3. Existing on disk: scans niche subdirectories (e.g. 'history/1- Title')
      4. Legacy flat folder: returns ('', '1- Title')
      5. New unassigned project: returns (niche or 'history', 'clean_title')
    """
    norm_title = video_title.replace("\\", "/").strip()
    if "/" in norm_title:
        parts = [p.strip() for p in norm_title.split("/") if p.strip()]
        if len(parts) >= 2:
            n_part = parts[0].lower()
            title_part = sanitize_title(parts[-1])
            return n_part, title_part

    clean_title = sanitize_title(video_title)
    if niche and niche != "auto":
        clean_niche = niche.lower().strip()
        return clean_niche, clean_title

    # Search on disk across all niche subdirectories
    all_niches = get_all_niche_names()
    for n in all_niches:
        for root in [FINALS_ROOT, POSTMORTEM_ROOT]:
            candidate = os.path.join(root, n, clean_title)
            if os.path.isdir(candidate):
                return n, clean_title

    # Check flat root legacy
    for root in [FINALS_ROOT, POSTMORTEM_ROOT]:
        candidate = os.path.join(root, clean_title)
        if os.path.isdir(candidate):
            return "", clean_title

    # Default for new projects
    target_niche = (niche or "history").lower().strip() if (niche and niche != "auto") else "history"
    return target_niche, clean_title

def get_next_project_folder_name(raw_title: str, niche: str = None) -> str:
    """
    Scans 1- Postmartum/ and 3- Finals/ to find the highest integer prefix,
    within the specified niche or globally, and returns '{next_index}- {clean_title}'.
    If raw_title already starts with an index (e.g. '1- Title'), keeps it.
    """
    clean = sanitize_title(raw_title)
    m = re.match(r"^(\d+)\s*-\s*(.+)$", clean)
    if m:
        return clean

    target_niche = (niche or "").lower().strip() if (niche and niche != "auto") else None
    existing_indices = []

    # Check target niche subfolders first
    roots_to_check = []
    if target_niche:
        roots_to_check.append(os.path.join(POSTMORTEM_ROOT, target_niche))
        roots_to_check.append(os.path.join(FINALS_ROOT, target_niche))
    else:
        # Check all niche subfolders + roots
        for root in [POSTMORTEM_ROOT, FINALS_ROOT]:
            roots_to_check.append(root)
            if os.path.exists(root):
                for sub in os.listdir(root):
                    sub_path = os.path.join(root, sub)
                    if os.path.isdir(sub_path):
                        roots_to_check.append(sub_path)

    for check_dir in roots_to_check:
        if os.path.exists(check_dir):
            for entry in os.listdir(check_dir):
                if os.path.isdir(os.path.join(check_dir, entry)):
                    match = re.match(r"^(\d+)\s*-\s*", entry)
                    if match:
                        existing_indices.append(int(match.group(1)))

    next_idx = (max(existing_indices) + 1) if existing_indices else 1
    return f"{next_idx}- {clean}"

def list_all_projects() -> list:
    """
    Discover all projects in 1- Postmartum and 3- Finals across all niche subdirectories
    with stage readiness metadata and niche tags.
    """
    discovered = {}
    all_niches = get_all_niche_names()

    for root_dir in [POSTMORTEM_ROOT, FINALS_ROOT]:
        if not os.path.exists(root_dir):
            continue

        for entry in os.listdir(root_dir):
            full_entry = os.path.join(root_dir, entry)
            if not os.path.isdir(full_entry) or entry.startswith("."):
                continue

            # Check if this directory is a niche folder
            if entry.lower() in all_niches or (not re.match(r"^\d+\s*-\s*", entry) and not entry.startswith("Final")):
                niche_name = entry.lower()
                for sub in os.listdir(full_entry):
                    sub_full = os.path.join(full_entry, sub)
                    if os.path.isdir(sub_full) and not sub.startswith("."):
                        discovered[sub] = niche_name
            else:
                # Legacy flat project
                if entry not in discovered:
                    discovered[entry] = "history"

    def sort_key(item):
        name = item[0]
        m = re.match(r"^(\d+)\s*-\s*", name)
        return (item[1], int(m.group(1)) if m else 9999)

    sorted_projects = sorted(discovered.items(), key=sort_key)
    projects = []

    NICHE_DISPLAY_MAP = {
        "history": "History & Archaeology",
        "finance": "Finance & Economics",
        "medical": "Medical & Biology",
        "horror": "Horror & Mystery",
        "engineering": "Engineering & Technology"
    }

    for name, p_niche in sorted_projects:
        dirs = get_project_dirs(name, niche=p_niche)
        pm_dir = dirs["postmortem_dir"]
        finals_dir = dirs["finals_dir"]

        has_pm = os.path.exists(os.path.join(pm_dir, "cuts_data.json")) or os.path.exists(os.path.join(pm_dir, "clean_transcript.txt"))
        has_script = os.path.exists(dirs["master_csv"])
        has_vo = (
            os.path.exists(os.path.join(dirs["voiceovers_dir"], "voiceover_master_normalized.mp3")) or 
            os.path.exists(os.path.join(dirs["voiceovers_dir"], "shots_timing_alignment.json"))
        )

        img_count = 0
        if os.path.exists(dirs["final_images_dir"]):
            img_count = len([f for f in os.listdir(dirs["final_images_dir"]) if f.lower().endswith((".jpg", ".png"))])

        has_xml = os.path.exists(dirs["timeline_xml"])

        m = re.match(r"^(\d+)\s*-\s*(.+)$", name)
        display_title = m.group(2) if m else name
        idx = int(m.group(1)) if m else None

        projects.append({
            "folder_name": name,
            "relative_path": f"{p_niche}/{name}" if p_niche else name,
            "index": idx,
            "display_title": display_title,
            "niche": p_niche or "history",
            "niche_display": NICHE_DISPLAY_MAP.get(p_niche, (p_niche or "history").replace("_", " ").title()),
            "has_postmortem": has_pm,
            "has_script": has_script,
            "has_vo": has_vo,
            "image_count": img_count,
            "has_images": img_count > 0,
            "has_xml": has_xml
        })

    return projects

def get_project_dirs(video_title: str, niche: str = None):
    resolved_niche, clean_title = resolve_project_niche_and_title(video_title, niche)

    if resolved_niche:
        postmortem_dir = os.path.join(POSTMORTEM_ROOT, resolved_niche, clean_title)
        finals_dir = os.path.join(FINALS_ROOT, resolved_niche, clean_title)
        rel_path = f"{resolved_niche}/{clean_title}"
    else:
        postmortem_dir = os.path.join(POSTMORTEM_ROOT, clean_title)
        finals_dir = os.path.join(FINALS_ROOT, clean_title)
        rel_path = clean_title

    final_images_dir = os.path.join(finals_dir, "Final selected images")
    voiceovers_dir = os.path.join(finals_dir, "Voiceovers")
    raw_images_dir = os.path.join(finals_dir, "flow_generated_images")

    return {
        "title": clean_title,
        "niche": resolved_niche or "history",
        "relative_path": rel_path,
        "postmortem_dir": postmortem_dir,
        "finals_dir": finals_dir,
        "final_images_dir": final_images_dir,
        "voiceovers_dir": voiceovers_dir,
        "raw_images_dir": raw_images_dir,
        "root_images_dir": ROOT_CANONICAL_IMAGES_DIR,
        "timeline_xml": os.path.join(finals_dir, "storyboard_timeline.xml"),
        "master_csv": os.path.join(finals_dir, "storyboard_master.csv"),
        "character_audit": os.path.join(finals_dir, "character_audit.json"),
        "selection_log": os.path.join(finals_dir, "selection_log.csv"),
        "production_status": os.path.join(finals_dir, "production_status.json"),
        "prompt_status_md": os.path.join(finals_dir, "PROMPT_STATUS.md"),
        "all_prompts_txt": os.path.join(finals_dir, "all_prompts.txt"),
        "script_txt": os.path.join(finals_dir, "clean_ai_voiceover_script.txt"),
    }

# ------------------------------------------------------------------------------
# GEMINI API CONFIGURATION (STAGE 2 SCRIPT REPURPOSING & PROMPTS)
# ------------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""

def get_gemini_api_key(force_reload: bool = False) -> str:
    """Returns the current Gemini API key, reloading .env if requested."""
    if force_reload:
        reload_env_keys()
    return GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""

def set_gemini_api_key(api_key: str):
    """Sets the Gemini API key in-memory and persists it to .env."""
    global GEMINI_API_KEY
    GEMINI_API_KEY = api_key.strip()
    sync_gemini_key_to_env(GEMINI_API_KEY)

def sync_gemini_key_to_env(api_key: str):
    """Safely updates GEMINI_API_KEY in .env file without wiping other credentials."""
    clean_key = api_key.strip()
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        has_key = False
        new_lines = []
        for line in lines:
            if line.startswith("GEMINI_API_KEY="):
                new_lines.append(f"GEMINI_API_KEY={clean_key}\n")
                has_key = True
            else:
                new_lines.append(line)
        if not has_key:
            new_lines.append(f"GEMINI_API_KEY={clean_key}\n")
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    else:
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write(f"GEMINI_API_KEY={clean_key}\n")

# ------------------------------------------------------------------------------
# ELEVENLABS TTS CONFIGURATION & DYNAMIC KEY POOL
# ------------------------------------------------------------------------------
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
_raw_keys = os.getenv("ELEVENLABS_API_KEYS", ELEVENLABS_API_KEY or "")
ELEVENLABS_API_KEYS = [k.strip() for k in re.split(r"[,\n]+", _raw_keys) if k.strip()]
if not ELEVENLABS_API_KEYS and ELEVENLABS_API_KEY:
    ELEVENLABS_API_KEYS = [ELEVENLABS_API_KEY.strip()]

def reload_env_keys():
    """Reloads .env file from disk to refresh API credentials after GUI updates."""
    global ELEVENLABS_API_KEY, ELEVENLABS_API_KEYS, ELEVENLABS_VOICE_ID, ELEVENLABS_MODEL_ID, GEMINI_API_KEY
    load_dotenv(ENV_FILE, override=True)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    _raw = os.getenv("ELEVENLABS_API_KEYS", ELEVENLABS_API_KEY or "")
    ELEVENLABS_API_KEYS = [k.strip() for k in re.split(r"[,\n]+", _raw) if k.strip()]
    if not ELEVENLABS_API_KEYS and ELEVENLABS_API_KEY:
        ELEVENLABS_API_KEYS = [ELEVENLABS_API_KEY.strip()]
    ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "q0IMILNRPxOgtBTS4taI")
    ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

def get_elevenlabs_api_keys(force_reload: bool = False) -> list:
    if force_reload:
        reload_env_keys()
    return list(ELEVENLABS_API_KEYS)

def set_elevenlabs_api_keys(keys_list: list):
    global ELEVENLABS_API_KEYS
    ELEVENLABS_API_KEYS = [k.strip() for k in keys_list if k.strip()]
    sync_keys_to_env_files(ELEVENLABS_API_KEYS)

def sync_keys_to_env_files(keys_list: list):
    """Safely updates ELEVENLABS_API_KEYS in .env file without wiping other credentials."""
    keys_str = ",".join([k.strip() for k in keys_list if k.strip()])
    first_key = keys_list[0].strip() if keys_list else ""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        has_keys = False
        has_single = False
        new_lines = []
        for line in lines:
            if line.startswith("ELEVENLABS_API_KEYS="):
                new_lines.append(f"ELEVENLABS_API_KEYS={keys_str}\n")
                has_keys = True
            elif line.startswith("ELEVENLABS_API_KEY="):
                new_lines.append(f"ELEVENLABS_API_KEY={first_key}\n")
                has_single = True
            else:
                new_lines.append(line)
        if not has_keys:
            new_lines.append(f"ELEVENLABS_API_KEYS={keys_str}\n")
        if not has_single:
            new_lines.append(f"ELEVENLABS_API_KEY={first_key}\n")
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    else:
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write(f"ELEVENLABS_API_KEYS={keys_str}\nELEVENLABS_API_KEY={first_key}\n")

# Default: Tyler - Clear US YouTube Creator Voice
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "q0IMILNRPxOgtBTS4taI")
ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

ELEVENLABS_VOICE_SETTINGS = {
    "stability": float(os.getenv("ELEVENLABS_STABILITY", "0.50")),
    "similarity_boost": float(os.getenv("ELEVENLABS_SIMILARITY_BOOST", "0.75")),
    "style": float(os.getenv("ELEVENLABS_STYLE", "0.15")),
    "use_speaker_boost": os.getenv("ELEVENLABS_USE_SPEAKER_BOOST", "true").lower() == "true",
}

# ------------------------------------------------------------------------------
# SILENCE NORMALIZATION RULES (SOP MANDATORY)
# ------------------------------------------------------------------------------
MAX_SILENCE_MS = 300
SILENCE_TAIL_CUSHION_MS = 150
SILENCE_HEAD_CUSHION_MS = 150

# ------------------------------------------------------------------------------
# GOOGLE FLOW IMAGE GENERATION CONFIGURATION
# ------------------------------------------------------------------------------
MODEL_CASCADE = [
    "Nano Banana Pro",
    "Nano Banana 2",
    "Nano Banana 2 Lite"
]

TARGET_VARIATIONS = 2
ASPECT_RATIO = "16:9"
TARGET_WIDTH = 1376
TARGET_HEIGHT = 768
TARGET_2K_WIDTH = 2752
TARGET_2K_HEIGHT = 1536
FLOW_IMAGE_RESOLUTION = "2k"  # Options: "2k" (Google Flow native upscaled), "1k" (raw canvas)

PACING_MIN_SEC = 10.0
PACING_MAX_SEC = 30.0

CDP_ENDPOINTS = [
    "http://[::1]:9222",
    "http://127.0.0.1:9222",
    "http://localhost:9222"
]

# ------------------------------------------------------------------------------
# STICK-FIGURE CHARACTER AND STYLE QUALITY RULES
# ------------------------------------------------------------------------------
MANDATORY_BASE_PROMPT = (
    "A minimalist 2D colored digital illustration webcomic style. Simple stick-figure aesthetic, "
    "doodle-style, vector minimalism, no gradients, no 3D shading, 16:9 aspect ratio."
)

MANDATORY_STICK_FIGURE_STYLE = (
    "Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art. "
    "All human characters MUST be minimalist white-filled black-outlined stick figures with simple circular heads, "
    "pure solid white head fill, clean bold black comic outlines, simple black stick limbs, zero realistic human anatomy, "
    "and zero flesh skin tones. Hand-drawn doodle comic style, Casually Explained and MinutePhysics aesthetic. "
    "Full bleed edge-to-edge illustration, grounded background environment, completely filling the 16:9 widescreen frame without borders, "
    "matted margins, or white card edges. Flat muted earthy color palette with subtle paper texture."
)

def get_prompt_templates_file() -> str:
    root_candidate = os.path.join(PROJECT_ROOT, "prompt_templates.json")
    if os.path.exists(root_candidate):
        return root_candidate
    code_candidate = os.path.join(CODE_DIR, "prompt_templates.json")
    return code_candidate

def get_active_prompt_template() -> dict:
    tmpl_path = get_prompt_templates_file()
    if os.path.exists(tmpl_path):
        try:
            with open(tmpl_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                active_id = data.get("active_template_id", "minutephysics_default")
                for t in data.get("templates", []):
                    if t.get("id") == active_id:
                        return t
        except Exception:
            pass
    return {
        "id": "minutephysics_default",
        "name": "MinutePhysics 2D Stick Figure (Standard)",
        "base_prompt": MANDATORY_BASE_PROMPT,
        "character_style": MANDATORY_STICK_FIGURE_STYLE
    }
