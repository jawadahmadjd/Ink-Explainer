"""
Generate Voiceovers for First 5 Sentences using ElevenLabs
Saves to: 3- Finals/1- What Did Ancient Humans Actually Do All Day/Voiceovers
"""

import os
import sys
import json
import re
import requests
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "q0IMILNRPxOgtBTS4taI")
MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "3- Finals", "1- What Did Ancient Humans Actually Do All Day", "Voiceovers")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# First 5 sentences
SENTENCES = [
    "Right now, your existence is sliced into little colored boxes on a glowing screen.",
    "Before your feet hit the floor, you look at a glass rectangle to see who owns your morning, who owns your afternoon, and how many minutes you get for lunch.",
    "You sprint through honking traffic, cram onto a packed subway train, and trade ten hours of your life answering messages from strangers.",
    "And tonight, before you sleep, you will set that same machine to scream at you again.",
    "Now, rewind forty-five thousand years."
]

def generate_tts_file(text, out_file):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
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

    print(f"Generating: '{text[:60]}...'")
    r = requests.post(url, json=payload, headers=headers, stream=True, timeout=60)
    if r.status_code == 200:
        with open(out_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        size_kb = os.path.getsize(out_file) / 1024.0
        print(f"  -> Saved: {os.path.basename(out_file)} ({size_kb:.1f} KB)")
        return True
    else:
        print(f"  -> Error {r.status_code}: {r.text}")
        return False

print("========================================================")
print("ELEVENLABS FIRST 5 SENTENCES VOICEOVER GENERATION")
print(f"Voice ID: {VOICE_ID} (Drew - Casual, Curious & Fun)")
print(f"Model ID: {MODEL_ID}")
print(f"Target Directory: {OUTPUT_DIR}")
print("========================================================\n")

# 1. Generate individual sentences
manifest = []
for idx, sent in enumerate(SENTENCES, 1):
    filename = f"sentence_{idx:02d}.mp3"
    filepath = os.path.join(OUTPUT_DIR, filename)
    success = generate_tts_file(sent, filepath)
    manifest.append({
        "index": idx,
        "filename": filename,
        "text": sent,
        "character_count": len(sent),
        "success": success
    })

# 2. Generate combined audio for first 5 sentences
combined_text = " ".join(SENTENCES)
combined_file = os.path.join(OUTPUT_DIR, "first_5_sentences_combined.mp3")
print("\nGenerating combined audio for all 5 sentences...")
combined_success = generate_tts_file(combined_text, combined_file)

# Save manifest
manifest_path = os.path.join(OUTPUT_DIR, "voiceover_manifest.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump({
        "voice_id": VOICE_ID,
        "voice_name": "Drew - Casual, Curious & Fun",
        "model_id": MODEL_ID,
        "combined_file": "first_5_sentences_combined.mp3",
        "sentences": manifest
    }, f, indent=2)

print("\nAll 5 sentences + combined voiceover generated successfully!")
