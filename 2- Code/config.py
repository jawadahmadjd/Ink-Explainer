"""
Central Configuration & Environment Loader for Ink Explainer Autonomous Pipeline
Defines directories, API credentials, silence rules, model cascades, and scoring parameters.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(ENV_FILE)

# ------------------------------------------------------------------------------
# DIRECTORY PATHS
# ------------------------------------------------------------------------------
CODE_DIR = os.path.join(PROJECT_ROOT, "2- Code")
POSTMORTEM_ROOT = os.path.join(PROJECT_ROOT, "1- Postmartum")
FINALS_ROOT = os.path.join(PROJECT_ROOT, "3- Finals")
ROOT_CANONICAL_IMAGES_DIR = os.path.join(PROJECT_ROOT, "Final selected images")

def sanitize_title(title: str) -> str:
    clean = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_", "'", "?", "!", ".", "(", ")")).strip()
    return clean

def get_project_dirs(video_title: str):
    clean_title = sanitize_title(video_title)
    postmortem_dir = os.path.join(POSTMORTEM_ROOT, clean_title)
    finals_dir = os.path.join(FINALS_ROOT, clean_title)
    final_images_dir = os.path.join(finals_dir, "Final selected images")
    voiceovers_dir = os.path.join(finals_dir, "Voiceovers")
    raw_images_dir = os.path.join(finals_dir, "flow_generated_images")
    
    return {
        "title": clean_title,
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
# ELEVENLABS TTS CONFIGURATION
# ------------------------------------------------------------------------------
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
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
MANDATORY_STICK_FIGURE_STYLE = (
    "Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art. "
    "All human characters MUST be minimalist white-filled black-outlined stick figures with simple circular heads, "
    "pure solid white head fill, clean bold black comic outlines, simple black stick limbs, zero realistic human anatomy, "
    "and zero flesh skin tones. Hand-drawn doodle comic style, Casually Explained and MinutePhysics aesthetic. "
    "Full bleed edge-to-edge illustration, grounded background environment, completely filling the 16:9 widescreen frame without borders, "
    "matted margins, or white card edges. Flat muted earthy color palette with subtle paper texture."
)
