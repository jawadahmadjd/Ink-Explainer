"""
Qwen3-TTS Automated Voice Cloning Pipeline (Google Colab -> VS Code)
===================================================================
Automatically reads:
  1. Your daily Colab URL from .env (QWEN_COLAB_URL)
  2. Your voice sample from 0- Voice Profiles/sample.wav (QWEN_VOICE_SAMPLE)
  3. Your transcript from 0- Voice Profiles/transcript.txt (QWEN_VOICE_TRANSCRIPT)

Features:
  - Smart Paragraph & Sentence Chunking (prevents timeouts on long scripts)
  - Seamless 300ms Silence-Normalized Audio Concatenation
  - Direct output saving to your project folders
"""

import os
import re
import sys
import time
import argparse
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
import soundfile as sf
from gradio_client import Client, handle_file

# Safe UTF-8 encoding for Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load configuration from workspace .env
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(WORKSPACE_ROOT / ".env")


def smart_chunk_text(text: str, max_chars: int = 1800) -> list[str]:
    """
    Splits long scripts into natural thematic chapters strictly under max_chars (< 2000 for Qwen 1.7B).
    Ensures cuts occur only at complete sentence and paragraph conclusions,
    preventing pitch spikes, robotic resets, or abrupt stitching artifacts.
    """
    text = text.strip()
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    
    chunks = []
    current_chunk = []
    current_len = 0
    
    for p in paragraphs:
        # Split paragraph into complete sentences ending with . ! ?
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|(?<=[.!?][\"\'])\s+', p) if s.strip()]
        for s in sentences:
            s_len = len(s)
            proj_len = current_len + (1 if current_chunk else 0) + s_len
            if proj_len > max_chars and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [s]
                current_len = s_len
            else:
                current_chunk.append(s)
                current_len = proj_len
                
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks


def generate_cloned_voiceover(
    script_text: str,
    output_path: str,
    sample_path: str = None,
    transcript: str = None,
    colab_url: str = None,
    pause_seconds: float = 0.3,
    use_xvector: bool = False,
    language: str = "English"
) -> str:
    """
    Clones the voice from sample_path and synthesizes script_text via Colab GPU.
    """
    # 1. Resolve Colab URL
    colab_url = colab_url or os.getenv("QWEN_COLAB_URL")
    if not colab_url:
        raise ValueError("Colab URL not found! Please set QWEN_COLAB_URL in .env or pass --url.")
    colab_url = colab_url.strip().rstrip("/") + "/"

    # 2. Resolve Voice Sample (.mp3 preferred, falls back to .wav)
    if not sample_path:
        env_sample = os.getenv("QWEN_VOICE_SAMPLE")
        if env_sample and (WORKSPACE_ROOT / env_sample).exists():
            sample_path = env_sample
        elif (WORKSPACE_ROOT / "0- Voice Profiles/sample.mp3").exists():
            sample_path = "0- Voice Profiles/sample.mp3"
        elif (WORKSPACE_ROOT / "0- Voice Profiles/sample.wav").exists():
            sample_path = "0- Voice Profiles/sample.wav"
        else:
            sample_path = "0- Voice Profiles/sample.mp3"

    ref_audio_file = (WORKSPACE_ROOT / sample_path).resolve()
    if not ref_audio_file.exists():
        raise FileNotFoundError(f"Voice sample file not found: {ref_audio_file}\nPlease place sample.mp3 into '0- Voice Profiles/'")

    # 3. Resolve Transcript
    if not transcript:
        trans_path = os.getenv("QWEN_VOICE_TRANSCRIPT", "0- Voice Profiles/transcript.txt")
        trans_file = (WORKSPACE_ROOT / trans_path).resolve()
        if trans_file.exists():
            with open(trans_file, "r", encoding="utf-8") as f:
                transcript = f.read().strip()
        else:
            transcript = ""

    if not transcript and not use_xvector:
        print("[Warning] No transcript found. Falling back to x-vector only mode.")
        use_xvector = True

    # 4. Chunk the script or load pre-chunked JSON
    if isinstance(script_text, str) and script_text.strip().endswith(".json") and os.path.exists(script_text.strip()):
        import json
        with open(script_text.strip(), "r", encoding="utf-8") as jf:
            jdata = json.load(jf)
            chunks = [c["text"] for c in jdata.get("chunks", [])]
    else:
        chunks = smart_chunk_text(script_text, max_chars=1800)
    print(f"==================================================")
    print(f"[QWEN3-TTS] Voice Cloning Pipeline")
    print(f"==================================================")
    print(f"Connecting to: {colab_url}")
    print(f"Voice Sample:  {ref_audio_file.name}")
    print(f"Transcript:    \"{transcript[:60]}...\"" if transcript else "Mode: x-vector (No transcript)")
    print(f"Script Chunks: {len(chunks)} chunk(s)")
    print(f"==================================================")

    # Set 10-minute timeout so httpx never drops connection while Colab is computing
    client = Client(colab_url, httpx_kwargs={"timeout": 600.0})
    ref_audio_upload = handle_file(str(ref_audio_file))

    audio_segments = []
    target_sr = None

    for idx, chunk in enumerate(chunks, 1):
        word_count = len(chunk.split())
        print(f"[{idx}/{len(chunks)}] Synthesizing ({word_count} words)... ", end="", flush=True)
        start_t = time.time()
        
        success = False
        last_error = None
        for attempt in range(1, 4):
            try:
                temp_wav_path, status = client.predict(
                    target_text=chunk,
                    ref_audio=ref_audio_upload,
                    ref_text=transcript if not use_xvector else "",
                    language=language,
                    use_xvector=use_xvector,
                    api_name="/generate_voice_clone"
                )
                success = True
                break
            except Exception as e:
                last_error = e
                if attempt < 3:
                    print(f"\n[Warning] Attempt {attempt} failed ({e}). Retrying in 3s...", end="", flush=True)
                    time.sleep(3)
        
        if not success:
            print(f"\n[ERROR] Chunk {idx} failed after 3 attempts: {last_error}")
            raise last_error

        elapsed = time.time() - start_t
        print(f"Done ({elapsed:.1f}s)")
        data, sr = sf.read(temp_wav_path)
        if target_sr is None:
            target_sr = sr
        audio_segments.append(data)

    # 5. Concatenate with clean silence pause
    print("Stitching audio segments...")
    silence_frames = int(target_sr * pause_seconds)
    silence = np.zeros(silence_frames, dtype=audio_segments[0].dtype)

    combined_audio = []
    for i, seg in enumerate(audio_segments):
        combined_audio.append(seg)
        if i < len(audio_segments) - 1:
            combined_audio.append(silence)

    final_waveform = np.concatenate(combined_audio)

    # 6. Save final file (supports .mp3 and .wav)
    out_file = (WORKSPACE_ROOT / output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    if out_file.suffix.lower() == ".mp3":
        try:
            sf.write(str(out_file), final_waveform, target_sr, format='MP3')
        except Exception:
            temp_wav = out_file.with_suffix(".temp.wav")
            sf.write(str(temp_wav), final_waveform, target_sr)
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(temp_wav), "-b:a", "192k", str(out_file)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            temp_wav.unlink(missing_ok=True)
    else:
        sf.write(str(out_file), final_waveform, target_sr)

    duration_sec = len(final_waveform) / target_sr
    print(f"[SUCCESS] Voiceover generated and saved:")
    print(f"   Path:     {out_file}")
    print(f"   Duration: {duration_sec:.1f} seconds ({duration_sec/60:.1f} mins)")
    print(f"==================================================")
    return str(out_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Cloned Voiceover with Qwen3-TTS via Google Colab")
    parser.add_argument("--script", "--file", dest="file", type=str, help="Path to text file containing voiceover script")
    parser.add_argument("--text", type=str, help="Direct text string to synthesize")
    parser.add_argument("--output", type=str, default="3- Finals/cloned_voiceover.mp3", help="Output audio path (.mp3 or .wav)")
    parser.add_argument("--sample", type=str, help="Path to custom reference voice sample (defaults to .env)")
    parser.add_argument("--transcript", type=str, help="Custom transcript text (defaults to .env)")
    parser.add_argument("--url", type=str, help="Colab URL (defaults to .env)")
    parser.add_argument("--pause", type=float, default=0.3, help="Pause between paragraphs in seconds (default: 0.3)")
    parser.add_argument("--xvector", action="store_true", help="Force x-vector only mode without transcript")

    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            script_content = f.read()
    elif args.text:
        script_content = args.text
    else:
        script_content = "This is a demonstration of the automated voice cloning pipeline running from VS Code directly to Google Colab."
        print(f"No text/file specified. Using demo sentence: '{script_content}'")

    generate_cloned_voiceover(
        script_text=script_content,
        output_path=args.output,
        sample_path=args.sample,
        transcript=args.transcript,
        colab_url=args.url,
        pause_seconds=args.pause,
        use_xvector=args.xvector
    )
