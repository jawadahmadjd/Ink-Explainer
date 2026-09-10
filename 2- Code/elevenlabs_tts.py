"""
ElevenLabs TTS Integration Module
Loads configuration from .env or system environment variables:
- ELEVENLABS_API_KEY
- ELEVENLABS_VOICE_ID
- ELEVENLABS_MODEL_ID
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path

# Try loading python-dotenv if available
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

# ==============================================================================
# ELEVENLABS MODEL DIRECTORY & DOCUMENTATION
# ==============================================================================
ELEVENLABS_MODELS = {
    "eleven_multilingual_v2": {
        "name": "Eleven Multilingual v2",
        "description": "State-of-the-art emotional delivery across 29 languages. Highest nuance, richness, and stability. Ideal for storytelling and high-retention explainers.",
        "recommended_for": "YouTube Explainers, Audiobooks, Character Acting",
        "languages": 29
    },
    "eleven_turbo_v2_5": {
        "name": "Eleven Turbo v2.5",
        "description": "High-quality low-latency (~250-300ms) model across 32 languages. ~50% cheaper token/character pricing than v2.",
        "recommended_for": "Fast generation, long-form content on a budget, conversational agents",
        "languages": 32
    },
    "eleven_flash_v2_5": {
        "name": "Eleven Flash v2.5",
        "description": "Ultra-fast generation (~75ms latency) across 32 languages. Budget-friendly, ultra-rapid turnaround.",
        "recommended_for": "Real-time streaming, high volume drafts, rapid testing",
        "languages": 32
    },
    "eleven_turbo_v2": {
        "name": "Eleven Turbo v2",
        "description": "English-optimized high-speed model.",
        "recommended_for": "English-only low latency generation",
        "languages": 1
    },
    "eleven_multilingual_v1": {
        "name": "Eleven Multilingual v1",
        "description": "First-generation multilingual model (Legacy). Supports EN, DE, PL, ES, IT, FR, PT, HI.",
        "recommended_for": "Legacy compatibility",
        "languages": 8
    },
    "eleven_monolingual_v1": {
        "name": "Eleven English v1",
        "description": "First-generation English monolingual model (Legacy).",
        "recommended_for": "Legacy compatibility",
        "languages": 1
    }
}

def get_config():
    """Fetches and validates active ElevenLabs configuration."""
    api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB").strip()
    model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2").strip()

    # Voice settings
    stability = float(os.getenv("ELEVENLABS_STABILITY", "0.50"))
    similarity_boost = float(os.getenv("ELEVENLABS_SIMILARITY_BOOST", "0.75"))
    style = float(os.getenv("ELEVENLABS_STYLE", "0.15"))
    use_speaker_boost = os.getenv("ELEVENLABS_USE_SPEAKER_BOOST", "true").lower() == "true"

    return {
        "api_key": api_key,
        "voice_id": voice_id,
        "model_id": model_id,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": use_speaker_boost
        }
    }

def check_account_status(api_key=None):
    """Verifies API key and returns subscription info / character limits."""
    cfg = get_config()
    key = api_key or cfg["api_key"]
    if not key or key == "your_elevenlabs_api_key_here":
        return False, "ELEVENLABS_API_KEY is not set or still has default placeholder in .env"

    headers = {"xi-api-key": key}
    url = "https://api.elevenlabs.io/v1/user/subscription"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            used = data.get("character_count", 0)
            limit = data.get("character_limit", 0)
            tier = data.get("tier", "unknown")
            return True, f"Valid API Key! Tier: '{tier}', Characters: {used:,} / {limit:,} used."
        else:
            return False, f"HTTP {r.status_code}: {r.text}"
    except Exception as e:
        return False, f"Connection error: {e}"

def list_available_voices(api_key=None):
    """Lists available voices in the user's account."""
    cfg = get_config()
    key = api_key or cfg["api_key"]
    if not key or key == "your_elevenlabs_api_key_here":
        return []

    headers = {"xi-api-key": key}
    url = "https://api.elevenlabs.io/v1/voices"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json().get("voices", [])
    except Exception:
        pass
    return []

def generate_voiceover(text, output_path, voice_id=None, model_id=None):
    """Generates audio for given text and saves as MP3."""
    cfg = get_config()
    key = cfg["api_key"]
    v_id = voice_id or cfg["voice_id"]
    m_id = model_id or cfg["model_id"]

    if not key or key == "your_elevenlabs_api_key_here":
        print("[ERROR] Please set your valid ELEVENLABS_API_KEY in .env before generating audio.")
        return False

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{v_id}"
    headers = {
        "xi-api-key": key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "text": text,
        "model_id": m_id,
        "voice_settings": cfg["voice_settings"]
    }

    print(f"[ElevenLabs TTS] Requesting audio generation...")
    print(f"  Voice ID: {v_id}")
    print(f"  Model ID: {m_id}")
    print(f"  Text Length: {len(text)} chars")

    try:
        r = requests.post(url, json=payload, headers=headers, stream=True, timeout=120)
        if r.status_code == 200:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
            print(f"[ElevenLabs TTS] Audio successfully saved to: {output_path}")
            return True
        else:
            print(f"[ElevenLabs TTS Error] HTTP {r.status_code}: {r.text}")
            return False
    except Exception as e:
        print(f"[ElevenLabs TTS Exception] {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ElevenLabs TTS CLI Utility")
    parser.add_argument("--status", action="store_true", help="Check ElevenLabs API Key validity & credits")
    parser.add_argument("--voices", action="store_true", help="List available voice IDs in your account")
    parser.add_argument("--models", action="store_true", help="Display all supported ElevenLabs models")
    parser.add_argument("--test-phrase", type=str, default="", help="Generate test audio for custom phrase")
    parser.add_argument("--out", type=str, default="3- Finals/test_voiceover.mp3", help="Output path for audio")
    args = parser.parse_args()

    if args.models:
        print("\n========================================================")
        print("ALL SUPPORTED ELEVENLABS MODELS")
        print("========================================================")
        for mid, info in ELEVENLABS_MODELS.items():
            print(f"  [{mid}]")
            print(f"    Name:        {info['name']}")
            print(f"    Description: {info['description']}")
            print(f"    Recommended: {info['recommended_for']}")
            print(f"    Languages:   {info['languages']}")
            print("--------------------------------------------------------")
        sys.exit(0)

    cfg = get_config()
    print("========================================================")
    print("ELEVENLABS ENVIRONMENT CONFIGURATION")
    print(f"  API Key Configured: {'YES' if cfg['api_key'] and cfg['api_key'] != 'your_elevenlabs_api_key_here' else 'NO (Set in .env)'}")
    print(f"  Selected Voice ID:  {cfg['voice_id']}")
    print(f"  Selected Model ID:  {cfg['model_id']}")
    print("========================================================")

    if args.status:
        valid, msg = check_account_status()
        print(f"Account Status: {msg}")

    elif args.voices:
        voices = list_available_voices()
        if not voices:
            print("No voices returned. Make sure your ELEVENLABS_API_KEY is valid.")
        else:
            print(f"\nFound {len(voices)} available voices:")
            for v in voices:
                print(f"  - {v.get('name', 'Unknown')}: {v.get('voice_id')} (Category: {v.get('category', 'premade')})")

    elif args.test_phrase:
        generate_voiceover(args.test_phrase, args.out)
