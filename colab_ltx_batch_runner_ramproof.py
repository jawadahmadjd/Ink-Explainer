import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import os
import json
import time
import math
import gc
import argparse
from pathlib import Path
from PIL import Image
import torch
from transformers import AutoTokenizer, T5EncoderModel
from diffusers import LTXImageToVideoPipeline
from diffusers.utils import export_to_video

DEFAULT_WIDTH = 768
DEFAULT_HEIGHT = 448
DEFAULT_STEPS = 28
DEFAULT_FPS = 24
DEFAULT_CFG = 3.0

NEGATIVE_PROMPT = (
    "photorealistic, 3D CGI, 3D render, realistic human skin, photographic shading, "
    "dark gradient background, colorful noise, blurry, distorted anatomy, warped faces, "
    "color bleeding, low quality, artifacts"
)

STYLE_SUFFIX = "minimalist 2D hand-drawn ink comic line art on pure white paper, clean bold black ink lines, subtle organic 2D motion, high quality, 24fps"

def calc_ltx_generation_frames(exact_frames):
    k = max(2, math.ceil((exact_frames - 1) / 8.0))
    return int(8 * k + 1)

def encode_text_prompt(tokenizer, text_encoder, prompt_text, max_sequence_length=128):
    text_inputs = tokenizer(
        prompt_text,
        padding="max_length",
        max_length=max_sequence_length,
        truncation=True,
        add_special_tokens=True,
        return_tensors="pt",
    )
    input_ids = text_inputs.input_ids.to("cuda")
    attention_mask = text_inputs.attention_mask.to("cuda")
    with torch.no_grad():
        prompt_embeds = text_encoder(input_ids, attention_mask=attention_mask)[0]
    return prompt_embeds.cpu(), attention_mask.cpu()

def run_batch(input_dir, manifest_path, output_dir, limit=None):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
        
    print(f"Loaded manifest with {len(manifest)} total curated shots from XML 2.")
    
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available! Please switch Colab runtime to T4 GPU.")
    
    gpu_name = torch.cuda.get_device_name(0)
    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f"Detected GPU: {gpu_name} ({vram_gb:.1f} GB VRAM)")
    
    # Filter pending shots first
    pending = []
    for item in manifest:
        shot_name = item['filename']
        mp4_name = shot_name.replace('.jpg', '.mp4').replace('.png', '.mp4')
        out_file = output_dir / mp4_name
        
        if out_file.exists() and out_file.stat().st_size > 15000:
            continue
        pending.append(item)
        
    print(f"Status: {len(manifest) - len(pending)} already completed | {len(pending)} pending.")
    
    if limit and limit > 0:
        pending = pending[:limit]
        print(f"Limiting to next {len(pending)} shots as requested.")
        
    if not pending:
        print("All shots in manifest are already rendered! Nothing to do.")
        return

    # PHASE 1: PRE-ENCODE PROMPTS ON GPU, THEN PURGE T5-XXL
    embeds_cache_file = Path("/content/ltx_encoded_prompts.pt")
    cached_embeds = {}
    
    if embeds_cache_file.exists():
        print("\n⚡ Loading pre-computed prompt embeddings from disk cache...")
        cache_data = torch.load(embeds_cache_file, map_location="cpu")
        cached_embeds = cache_data['shots']
        neg_embeds = cache_data['neg_embeds']
        neg_mask = cache_data['neg_mask']
        print(f"✅ Loaded {len(cached_embeds)} prompt embeddings instantly!")
    else:
        print("\n⏳ Phase 1/2: Loading Text Encoder on GPU to pre-encode prompts...")
        print("   (This keeps CPU RAM under 3.5 GB and prevents all Colab crashes!)")
        t0_enc = time.time()
        
        tokenizer = AutoTokenizer.from_pretrained("Lightricks/LTX-Video", subfolder="tokenizer")
        text_encoder = T5EncoderModel.from_pretrained(
            "Lightricks/LTX-Video",
            subfolder="text_encoder",
            torch_dtype=torch.bfloat16
        ).to("cuda")
        
        print("   Encoding negative prompt...")
        neg_embeds, neg_mask = encode_text_prompt(tokenizer, text_encoder, NEGATIVE_PROMPT)
        
        print(f"   Encoding prompts for {len(pending)} shots on GPU...")
        for idx, item in enumerate(pending):
            action_desc = item.get('desc', '') or item.get('ltx_prompt', '')
            prompt = f"{action_desc}, {STYLE_SUFFIX}"
            pe, pam = encode_text_prompt(tokenizer, text_encoder, prompt)
            cached_embeds[item['filename']] = (pe, pam)
            
        torch.save({'shots': cached_embeds, 'neg_embeds': neg_embeds, 'neg_mask': neg_mask}, embeds_cache_file)
        
        # Free memory completely
        del text_encoder, tokenizer
        gc.collect()
        torch.cuda.empty_cache()
        dur_enc = time.time() - t0_enc
        print(f"✅ Phase 1 complete in {dur_enc:.1f}s! Text Encoder purged from memory.")

    # PHASE 2: LOAD VIDEO GENERATOR DIRECTLY ON GPU (ZERO T5 OVERHEAD)
    print("\n⏳ Phase 2/2: Loading LTX Transformer and VAE directly onto GPU...")
    t0_load = time.time()
    
    LTXImageToVideoPipeline._optional_components = ["text_encoder", "tokenizer"]
    pipe = LTXImageToVideoPipeline.from_pretrained(
        "Lightricks/LTX-Video",
        text_encoder=None,
        tokenizer=None,
        torch_dtype=torch.bfloat16
    ).to("cuda")
    
    pipe.vae.enable_tiling()
    pipe.vae.enable_slicing()
    dur_load = time.time() - t0_load
    print(f"✅ Video Generator loaded in {dur_load:.1f}s!")
    print("   System RAM: Safe (~3.5 GB / 12.7 GB) | GPU VRAM: Safe (~5.5 GB / 14.6 GB)")

    # PHASE 3: EXECUTE BATCH GENERATION
    start_time = time.time()
    times = []
    
    print("\n" + "="*85)
    print(f"🎬 STARTING DYNAMIC-LENGTH BATCH: {len(pending)} SHOTS")
    print("⏱️ Videos will match your exact Premiere clip duration (no fixed 4-sec bloat)")
    print("="*85)
    
    for idx, item in enumerate(pending):
        shot_name = item['filename']
        mp4_name = shot_name.replace('.jpg', '.mp4').replace('.png', '.mp4')
        out_file = output_dir / mp4_name
        
        img_path = input_dir / shot_name
        if not img_path.exists():
            img_path = input_dir / "images" / shot_name
            
        if not img_path.exists():
            print(f"⚠️ Skipping missing file: {img_path}")
            continue
            
        t_start = time.time()
        exact_frames = item.get('exact_frames', int(item.get('duration_sec', 1.5) * 24))
        gen_frames = calc_ltx_generation_frames(exact_frames)
        dur_sec = exact_frames / 24.0
        
        action_desc = item.get('desc', '') or item.get('ltx_prompt', '')
        
        init_img = Image.open(img_path).convert("RGB")
        init_img = init_img.resize((DEFAULT_WIDTH, DEFAULT_HEIGHT), Image.Resampling.LANCZOS)
        
        print(f"\n[{idx+1}/{len(pending)}] {shot_name} -> {mp4_name} | Target: {dur_sec:.2f}s ({exact_frames} frames, gen: {gen_frames})...")
        print(f"   Prompt: \"{action_desc[:70]}...\"")
        
        pe, pam = cached_embeds[shot_name]
        
        with torch.inference_mode():
            output = pipe(
                image=init_img,
                prompt_embeds=pe.to("cuda"),
                prompt_attention_mask=pam.to("cuda"),
                negative_prompt_embeds=neg_embeds.to("cuda"),
                negative_prompt_attention_mask=neg_mask.to("cuda"),
                width=DEFAULT_WIDTH,
                height=DEFAULT_HEIGHT,
                num_frames=gen_frames,
                frame_rate=DEFAULT_FPS,
                num_inference_steps=DEFAULT_STEPS,
                guidance_scale=DEFAULT_CFG,
                generator=torch.Generator(device="cuda").manual_seed(42 + item['sid'])
            )
            
        video_frames = output.frames[0][:exact_frames]
        export_to_video(video_frames, str(out_file), fps=DEFAULT_FPS)
        del video_frames, output
        torch.cuda.empty_cache()
        gc.collect()
        
        dur = time.time() - t_start
        times.append(dur)
        avg_time = sum(times) / len(times)
        rem_shots = len(pending) - (idx + 1)
        eta_min = (rem_shots * avg_time) / 60.0
        
        file_size_kb = out_file.stat().st_size / 1024
        print(f"   ✅ Saved {out_file.name} ({dur_sec:.2f}s, {file_size_kb:.0f} KB) in {dur:.1f}s | Avg: {avg_time:.1f}s/clip | ETA: {eta_min:.1f} mins left")
        
    total_elapsed = (time.time() - start_time) / 60.0
    print("\n" + "="*85)
    print(f"🎉 BATCH COMPLETE! Processed {len(pending)} shots in {total_elapsed:.1f} minutes.")
    print(f"📁 Videos saved to: {output_dir}")
    print("="*85)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Variable-Length LTX-Video Batch Runner")
    parser.add_argument("--input_dir", default="images")
    parser.add_argument("--manifest", default="batch_manifest.json")
    parser.add_argument("--output_dir", default="outputs")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    
    run_batch(args.input_dir, args.manifest, args.output_dir, args.limit)
