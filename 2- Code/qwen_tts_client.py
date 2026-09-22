"""
Qwen3-TTS Colab Client for VS Code
Connects directly to your running Google Colab T4 GPU instance to generate voiceovers.
"""

import os
import shutil
import argparse
from pathlib import Path
from gradio_client import Client

# Default Colab URL (update this whenever you start a new Colab session)
DEFAULT_COLAB_URL = "https://6042f908b7d6c7d644.gradio.live/"

# Available speakers in Qwen3-TTS CustomVoice:
# "Ryan" (Deep, confident male narrator - great for explainers)
# "Serena" (Clear, professional female narrator)
# "Aiden", "Dylan", "Eric", "Ono_anna", "Sohee", "Uncle_fu", "Vivian"

def generate_voiceover(
    text: str,
    output_path: str,
    colab_url: str = DEFAULT_COLAB_URL,
    speaker: str = "Ryan",
    instruction: str = "clear, confident documentary narrator",
    language: str = "English"
) -> str:
    """
    Sends text to your remote Colab GPU and downloads the generated WAV file.
    """
    colab_url = colab_url.strip().rstrip("/") + "/"
    print(f"Connecting to Google Colab GPU at: {colab_url}")
    client = Client(colab_url)
    
    print(f"Generating VO with speaker '{speaker}'...")
    audio_temp_path, status = client.predict(
        text=text.strip(),
        speaker=speaker,
        instruction=instruction,
        language=language,
        api_name="/generate_voice"
    )
    
    # Ensure target output directory exists
    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy downloaded temp file to target location
    shutil.copy(audio_temp_path, str(out_file))
    print(f"VO Saved successfully to: {out_file}")
    return str(out_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate VO using Qwen3-TTS on Google Colab")
    parser.add_argument("--text", type=str, help="Text to speak")
    parser.add_argument("--file", type=str, help="Path to text file to read script from")
    parser.add_argument("--output", type=str, default="voiceover_output.wav", help="Path to save output .wav")
    parser.add_argument("--speaker", type=str, default="Ryan", help="Speaker name (e.g. Ryan, Serena, Aiden)")
    parser.add_argument("--instruction", type=str, default="clear, confident documentary narrator", help="Style/tone instruction")
    parser.add_argument("--url", type=str, default=DEFAULT_COLAB_URL, help="Colab Gradio Live URL")
    
    args = parser.parse_args()
    
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            script_text = f.read()
    elif args.text:
        script_text = args.text
    else:
        script_text = "Welcome back. Today we are exploring how ancient civilizations lived."
        print(f"No text provided. Using default demo sentence: '{script_text}'")
        
    generate_voiceover(
        text=script_text,
        output_path=args.output,
        colab_url=args.url,
        speaker=args.speaker,
        instruction=args.instruction
    )

