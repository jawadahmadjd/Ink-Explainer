"""
Stage 2: Google Gemini Autonomous Script Repurposing & Storyboard Prompt Engine
Author: Google DeepMind Antigravity System
Purpose:
  1. 100% autonomous 1-click script repurposing from reference transcripts (SOP 03).
  2. 100% autonomous script creation from user prompts & topics.
  3. MinutePhysics stick-figure prompt synthesis with 20-65 character elastic pacing.
  4. Robust multi-model cascade with instant verification and graceful fallback.
"""

import os
import sys
import json
import re
import csv
import time
from typing import Dict, List, Any, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from learning.learning_engine import (
    split_script_into_elastic_steps,
    generate_smart_scene_description,
    classify_script_niche,
    load_codex,
    find_matching_reference_video
)

CANDIDATE_MODELS = [
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-pro-latest",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro"
]

CHARACTER_KEYWORDS = [
    "human", "person", "man", "woman", "hunter", "gatherer", "child", "people",
    "farmer", "ancestor", "forager", "tribesman", "warrior", "priest", "worker",
    "figure", "someone", "they", "we", "you", "crowd", "family", "men", "women",
    "hand", "hands", "eyes", "body", "face", "standing", "sitting", "walking", "running"
]

def is_likely_character_shot(vo_text: str, visual_desc: str) -> bool:
    """Detects whether shot features human characters."""
    combined = (vo_text + " " + visual_desc).lower()
    return any(re.search(r"\b" + re.escape(kw) + r"\b", combined) for kw in CHARACTER_KEYWORDS)

def format_stick_figure_prompt(visual_description: str, is_character: bool, niche: str = None) -> str:
    """Format prompt strictly with full bleed and stick figure standards, respecting niche visual tokens."""
    color_palette = "Flat muted earthy color palette with subtle paper texture."
    if niche:
        try:
            codex = load_codex()
            n_data = codex.get("niches", {}).get(niche, {})
            color_palette = n_data.get("visual_style", {}).get("color_palette", color_palette)
        except Exception:
            pass

    clean_desc = visual_description.strip()
    if is_character:
        base_prefix = (
            "Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art. "
            "Hand-drawn doodle comic style, Casually Explained and MinutePhysics aesthetic. "
            "All human characters MUST be drawn strictly as simple, minimalist stick figures: "
            "thin black line bodies, plain empty white circle heads, minimal dot eyes, simple neutral line mouths. "
            f"Full bleed edge-to-edge illustration, grounded background environment completely filling 16:9 widescreen frame without borders. {color_palette}"
        )
        return f"{base_prefix} Scene depicts: {clean_desc}"
    else:
        non_char_prefix = (
            "Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art. "
            "Hand-drawn doodle comic style, Casually Explained and MinutePhysics aesthetic. "
            f"Full bleed edge-to-edge illustration, grounded background environment, completely filling the 16:9 widescreen frame without borders, "
            f"matted margins, or white card edges. {color_palette}"
        )
        return f"{non_char_prefix} Detailed illustration of: {clean_desc}"

def get_gemini_client(api_key: Optional[str] = None):
    """Configures and returns the genai module if a key is present."""
    try:
        import google.generativeai as genai
    except ImportError:
        return None

    key = api_key or config.get_gemini_api_key()
    if not key:
        return None

    try:
        genai.configure(api_key=key.strip())
        return genai
    except Exception as e:
        print(f"[GEMINI WARNING] Failed to configure google.generativeai: {e}")
        return None

def validate_gemini_key(api_key: Optional[str] = None) -> Tuple[bool, str, List[str]]:
    """
    Validates Gemini API key by probing list_models and generating a minimal test completion.
    Returns: (is_valid, status_message, list_of_available_models)
    """
    key = (api_key if api_key is not None else config.get_gemini_api_key()).strip()
    if not key:
        return False, "No Gemini API key provided. Please add your GEMINI_API_KEY in Settings or .env.", []

    try:
        import google.generativeai as genai
    except ImportError:
        return False, "Python package 'google-generativeai' is not installed.", []

    try:
        genai.configure(api_key=key)
        available_names = []
        try:
            for m in genai.list_models():
                if "generateContent" in getattr(m, "supported_generation_methods", []):
                    clean_name = m.name.replace("models/", "")
                    available_names.append(clean_name)
        except Exception as ex:
            err_str = str(ex)
            if "403" in err_str or "denied" in err_str.lower():
                return False, f"Gemini API Denied (403): Project access denied. Ensure you are using a standard Google AI Studio key.", []
            return False, f"Gemini API Error: {err_str}", []

        # Find best candidate
        chosen_model = None
        for candidate in CANDIDATE_MODELS:
            if candidate in available_names:
                chosen_model = candidate
                break
        if not chosen_model and available_names:
            chosen_model = available_names[0]

        if not chosen_model:
            return False, "No generateContent-compatible Gemini models found for this key.", []

        # Probe with minimal generation
        try:
            m = genai.GenerativeModel(chosen_model)
            resp = m.generate_content("Ping", generation_config={"max_output_tokens": 5})
            if resp and resp.text:
                return True, f"Gemini API active and verified using model '{chosen_model}'.", available_names
            return True, f"Gemini API connected with model '{chosen_model}'.", available_names
        except Exception as probe_ex:
            p_err = str(probe_ex)
            if "403" in p_err or "denied" in p_err.lower():
                return False, f"Gemini API Denied (403): {p_err}", available_names
            if "404" in p_err or "not found" in p_err.lower() or "no longer available" in p_err.lower():
                # Try next available model
                for alt in available_names[:3]:
                    if alt != chosen_model:
                        try:
                            m2 = genai.GenerativeModel(alt)
                            resp2 = m2.generate_content("Ping", generation_config={"max_output_tokens": 5})
                            if resp2 and resp2.text:
                                return True, f"Gemini API verified using alternate model '{alt}'.", available_names
                        except Exception:
                            continue
            return False, f"Gemini probe test failed: {p_err}", available_names

    except Exception as e:
        return False, f"Gemini validation error: {str(e)}", []

def get_best_working_model(genai_module, api_key: Optional[str] = None):
    """Finds the best functioning generative model instance, testing candidates in cascade."""
    available_names = []
    try:
        for m in genai_module.list_models():
            if "generateContent" in getattr(m, "supported_generation_methods", []):
                available_names.append(m.name.replace("models/", ""))
    except Exception:
        pass

    candidates = [c for c in CANDIDATE_MODELS if not available_names or c in available_names]
    if not candidates and available_names:
        candidates = available_names

    for model_name in candidates:
        try:
            model = genai_module.GenerativeModel(model_name)
            test_resp = model.generate_content("OK", generation_config={"max_output_tokens": 2})
            if test_resp and test_resp.text:
                return model, model_name
        except Exception as e:
            err = str(e)
            if "404" in err or "no longer available" in err:
                continue
            if "403" in err or "denied" in err.lower():
                raise PermissionError(f"Gemini API access denied (403): {err}")
            continue

    fallback_name = candidates[0] if candidates else "gemini-1.5-flash"
    return genai_module.GenerativeModel(fallback_name), fallback_name

def repurpose_transcript_with_gemini(
    raw_transcript: str,
    video_title: str,
    niche: str = "history",
    video_info: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> str:
    """
    Repurposes reference transcript into an original, witty 7-Act viral explainer script.
    Follows SOP 03 rules: 0% verbatim plagiarism, Casually Explained / MinutePhysics style.
    """
    genai = get_gemini_client(api_key)
    if not genai:
        raise ValueError("Google Gemini API client is not configured or missing key.")

    model, model_name = get_best_working_model(genai, api_key)
    print(f"[GEMINI SCRIPT ENGINE] Repurposing script using Gemini model: {model_name}")

    prompt = f"""You are the world-class head scriptwriter and creative director for an elite YouTube explainer channel producing minimalist 2D ink animation explainers (Casually Explained meets MinutePhysics).

YOUR MISSION:
Repurpose the following raw reference transcript into a 100% ORIGINAL, viral, high-retention video script titled:
"{video_title}" (Niche: {niche.upper()})

MANDATORY EDITORIAL RULES (SOP 03):
1. TONE & NARRATIVE ARCHITECTURE:
   - Tone: Witty, deadpan, self-effacing, relatable explainer narration in the style of 'Casually Explained' and 'MinutePhysics'.
   - Structure: Follow the 7-Act Retention Architecture:
       * Act 1: The Paradox Hook (undeniable modern vs ancestral contradiction; an impossible question).
       * Act 2: The Common Misconception (what pop culture / school taught vs reality).
       * Act 3: The Historical/Scientific Origin (prehistoric or evolutionary roots).
       * Act 4: The Hidden Mechanism (the physical gears explained with funny, simple visual analogies).
       * Act 5: The Turning Point / Catastrophic Failure (when the system fails or goes wrong).
       * Act 6: The Modern Parallel (how modern humans do the exact same thing with phones/emails/debt).
       * Act 7: The Unresolved Irony & Epilogue (dry, thought-provoking philosophical reflection).

2. ZERO PLAGIARISM REPURPOSING MANDATE:
   - 100% original phrasing (0% verbatim copy-pasting from reference).
   - Preserve all historical/scientific facts, archaeological sites, names, numbers, citations, and core thesis.
   - Transform dry academic explanations into funny, high-dopamine visual thought-experiments.

3. SCRIPT OUTPUT FORMAT:
   - Return ONLY the clean spoken narration text.
   - Do NOT include scene headers, stage directions, shot tags, or bracketed notes (e.g. no [Act 1], no [SFX], no Narrator:).
   - Use natural punctuation (periods, commas, em-dashes) for rhythmic cadence.

RAW REFERENCE TRANSCRIPT:
\"\"\"
{raw_transcript[:12000]}
\"\"\"
"""

    resp = model.generate_content(prompt)
    if not resp or not resp.text:
        raise RuntimeError("Gemini returned empty response for script repurposing.")

    clean_script = re.sub(r"\[.*?\]", "", resp.text)
    clean_script = re.sub(r"\*\*", "", clean_script)
    clean_script = re.sub(r"Act\s+\d+:\s*.*?\n", "", clean_script, flags=re.IGNORECASE)
    clean_script = re.sub(r"Narrator:\s*", "", clean_script, flags=re.IGNORECASE)
    clean_script = " ".join(clean_script.split()).strip()
    return clean_script

def create_script_from_prompt_with_gemini(
    user_prompt: str,
    video_title: str,
    niche: str = "history",
    api_key: Optional[str] = None
) -> str:
    """
    Creates an original 7-act viral explainer script from a topic / prompt using Gemini.
    """
    genai = get_gemini_client(api_key)
    if not genai:
        raise ValueError("Google Gemini API client is not configured or missing key.")

    model, model_name = get_best_working_model(genai, api_key)
    print(f"[GEMINI SCRIPT ENGINE] Synthesizing new script using Gemini model: {model_name}")

    prompt = f"""You are the world-class head scriptwriter and creative director for an elite YouTube explainer channel producing minimalist 2D ink animation explainers (Casually Explained meets MinutePhysics).

YOUR MISSION:
Write a viral, high-retention, funny educational script titled:
"{video_title}" (Niche: {niche.upper()})
User Concept / Topic Notes:
\"\"\"
{user_prompt}
\"\"\"

MANDATORY EDITORIAL RULES (SOP 03):
1. TONE & NARRATIVE ARCHITECTURE:
   - Tone: Witty, deadpan, self-effacing, relatable explainer narration (Casually Explained / MinutePhysics style).
   - Structure: Follow the 7-Act Retention Architecture:
       * Act 1: The Paradox Hook (undeniable modern vs ancestral contradiction; an impossible question).
       * Act 2: The Common Misconception (what pop culture / school taught vs reality).
       * Act 3: The Historical/Scientific Origin (the prehistoric/evolutionary root moment).
       * Act 4: The Hidden Mechanism (the physical gears broken down with simple visual analogies).
       * Act 5: The Turning Point / Catastrophic Failure (when the system goes wrong).
       * Act 6: The Modern Parallel (how modern humans do the exact same thing today).
       * Act 7: The Unresolved Irony & Epilogue (dry, thought-provoking philosophical punchline).

2. SCRIPT OUTPUT FORMAT:
   - Return ONLY the clean spoken narration text.
   - Do NOT include scene headers, stage directions, shot tags, or bracketed notes (e.g. no [Act 1], no [SFX], no Narrator:).
   - Use natural punctuation (periods, commas, em-dashes) for rhythmic cadence.
"""

    resp = model.generate_content(prompt)
    if not resp or not resp.text:
        raise RuntimeError("Gemini returned empty response for script creation.")

    clean_script = re.sub(r"\[.*?\]", "", resp.text)
    clean_script = re.sub(r"\*\*", "", clean_script)
    clean_script = re.sub(r"Act\s+\d+:\s*.*?\n", "", clean_script, flags=re.IGNORECASE)
    clean_script = re.sub(r"Narrator:\s*", "", clean_script, flags=re.IGNORECASE)
    clean_script = " ".join(clean_script.split()).strip()
    return clean_script

def generate_storyboard_prompts_with_gemini(
    script_text: str,
    project_title: str,
    niche: str = "history",
    cuts_data: Optional[List[Any]] = None,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Decomposes the script into Elastic Action Steps (~20-65 chars) and generates
    MinutePhysics stick-figure comic prompts via Gemini.
    Falls back gracefully to local elastic step splitter if JSON parsing fails.
    """
    genai = get_gemini_client(api_key)
    if not genai:
        return _local_storyboard_fallback(script_text, project_title, niche, cuts_data)

    try:
        model, model_name = get_best_working_model(genai, api_key)
    except Exception as e:
        print(f"[GEMINI PROMPT WARNING] Could not initialize Gemini model ({e}), using local fallback.")
        return _local_storyboard_fallback(script_text, project_title, niche, cuts_data)

    print(f"[GEMINI STORYBOARD ENGINE] Compiling stick-figure prompts using Gemini ({model_name})...")

    prompt = f"""You are an elite visual director for MinutePhysics stick-figure animated explainers.
Given the narration script below for "{project_title}" (Niche: {niche}), break it down into consecutive, atomic shots.

CRITICAL RULES:
1. PACING: Each shot must be an Elastic Action Step containing 20 to 65 characters of spoken voiceover (~1.0s to 2.2s per shot).
   Never orphan adjectives, articles, or cut mid-clause.
2. STICK-FIGURE STYLE:
   - All human characters MUST be drawn strictly as simple, minimalist stick figures:
     thin black line bodies, plain empty white circle heads, minimal dot eyes, simple neutral line mouths.
     Zero realistic human anatomy, zero flesh skin tones.
   - Hand-drawn doodle comic style, Casually Explained and MinutePhysics aesthetic.
   - Full bleed edge-to-edge illustration, grounded background environment completely filling 16:9 widescreen frame without borders.
3. OUTPUT FORMAT:
   Return ONLY a valid JSON array of objects. No markdown formatting, no code blocks, just raw JSON:
   [
     {{
       "shot_num": 1,
       "vo": "Exact spoken text for this micro-beat",
       "description": "Comedic visual gag description with stick figures and props",
       "prompt": "Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art. Hand-drawn doodle comic style, Casually Explained and MinutePhysics aesthetic. All human characters MUST be drawn strictly as simple, minimalist stick figures: thin black line bodies, plain empty white circle heads, minimal dot eyes, simple neutral line mouths. Full bleed edge-to-edge illustration, grounded background environment completely filling 16:9 widescreen frame without borders. Flat muted earthy color palette with subtle paper texture. Scene depicts: [specific comedic stick figure action]"
     }}
   ]

SCRIPT:
\"\"\"
{script_text[:10000]}
\"\"\"
"""

    try:
        resp = model.generate_content(prompt)
        text = (resp.text or "").strip()
        text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

        parsed = json.loads(text)
        if isinstance(parsed, list) and len(parsed) > 0:
            shots = []
            for i, item in enumerate(parsed, 1):
                vo = item.get("vo", "").strip()
                desc = item.get("description", "").strip()
                p = item.get("prompt", "").strip()
                if not p:
                    is_char = is_likely_character_shot(vo, desc)
                    p = format_stick_figure_prompt(desc, is_char, niche=niche)
                shots.append({
                    "shot_num": i,
                    "voiceover": vo,
                    "description": desc,
                    "prompt": p
                })
            return shots
    except Exception as ex:
        print(f"[GEMINI PROMPT WARNING] JSON parsing from Gemini failed ({ex}). Falling back to local elastic tokenizer.")

    return _local_storyboard_fallback(script_text, project_title, niche, cuts_data)

def _local_storyboard_fallback(
    script_text: str,
    project_title: str,
    niche: str = "history",
    cuts_data: Optional[List[Any]] = None
) -> List[Dict[str, Any]]:
    """Local deterministic fallback for prompt generation conforming strictly to MinutePhysics rules."""
    shot_texts = split_script_into_elastic_steps(script_text, target_min_chars=16, target_max_chars=65)
    shots = []
    for i, cut_vo in enumerate(shot_texts, 1):
        prev_vo = shot_texts[i-2] if i > 1 else ""
        next_vo = shot_texts[i] if i < len(shot_texts) else ""
        desc = generate_smart_scene_description(cut_vo, prev_vo=prev_vo, next_vo=next_vo, niche=niche)
        is_char = is_likely_character_shot(cut_vo, desc)
        prompt = format_stick_figure_prompt(desc, is_char, niche=niche)
        shots.append({
            "shot_num": i,
            "voiceover": cut_vo,
            "description": desc,
            "prompt": prompt
        })
    return shots

def run_gemini_stage2(
    video_title: str,
    custom_script_path: Optional[str] = None,
    user_prompt: Optional[str] = None,
    force_regenerate: bool = False,
    niche: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes 100% autonomous Stage 2 using Google Gemini API:
    1. Loads reference transcript or user prompt.
    2. Repurposes or synthesizes 7-Act script.
    3. Generates MinutePhysics stick-figure prompts for each elastic step.
    4. Writes storyboard_master.csv, clean_ai_voiceover_script.txt, all_prompts.txt,
       character_audit.json, and PROMPT_STATUS.md.
    """
    dirs = config.get_project_dirs(video_title)
    finals_dir = dirs["finals_dir"]
    postmortem_dir = dirs["postmortem_dir"]
    os.makedirs(finals_dir, exist_ok=True)
    os.makedirs(dirs["final_images_dir"], exist_ok=True)
    os.makedirs(dirs["voiceovers_dir"], exist_ok=True)
    os.makedirs(dirs["raw_images_dir"], exist_ok=True)

    master_csv_path = dirs["master_csv"]
    script_txt_path = dirs["script_txt"]
    all_prompts_path = dirs["all_prompts_txt"]
    audit_json_path = dirs["character_audit"]
    prompt_status_md = dirs["prompt_status_md"]

    # Detect or recover niche
    info_json_path = os.path.join(postmortem_dir, "video_info.json")
    vinfo = {}
    if os.path.exists(info_json_path):
        try:
            with open(info_json_path, "r", encoding="utf-8") as f:
                vinfo = json.load(f)
                if not niche:
                    niche = vinfo.get("niche")
        except Exception:
            pass
    if not niche:
        niche = classify_script_niche(video_title, user_prompt or "").get("niche", "history")

    cuts_path = os.path.join(postmortem_dir, "cuts_data.json")
    cuts_list = []
    if os.path.exists(cuts_path):
        try:
            with open(cuts_path, "r", encoding="utf-8") as f:
                cdata = json.load(f)
                cuts_list = cdata if isinstance(cdata, list) else cdata.get("cuts", [])
        except Exception:
            pass

    transcript_path = custom_script_path or os.path.join(postmortem_dir, "clean_transcript.txt")
    raw_text = ""
    if os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                raw_text = f.read().strip()
        except Exception:
            pass

    # 1. Script synthesis via Gemini
    if raw_text:
        print(f"[GEMINI STAGE 2] Repurposing reference script for '{video_title}' ({len(raw_text)} chars)...")
        script_text = repurpose_transcript_with_gemini(raw_text, video_title, niche=niche, video_info=vinfo, api_key=api_key)
    else:
        print(f"[GEMINI STAGE 2] Synthesizing script from topic prompt for '{video_title}'...")
        script_text = create_script_from_prompt_with_gemini(user_prompt or video_title, video_title, niche=niche, api_key=api_key)

    # 2. Shot and prompt synthesis
    shots = generate_storyboard_prompts_with_gemini(script_text, video_title, niche=niche, cuts_data=cuts_list, api_key=api_key)
    total_shots = len(shots)

    nominal_dur = 2.0
    rows = []
    audit_list = []
    prompt_lines = []

    for i, s in enumerate(shots, 1):
        vo = s.get("voiceover", "").strip()
        desc = s.get("description", "").strip()
        prompt = s.get("prompt", "").strip()

        s_time = (i - 1) * nominal_dur
        e_time = i * nominal_dur
        tc = f"{int(s_time // 60):02d}:{s_time % 60:04.1f} - {int(e_time // 60):02d}:{e_time % 60:04.1f}"

        rows.append([i, tc, vo, desc, prompt])

        img_path = os.path.join(dirs["final_images_dir"], f"shot_{i:03d}.jpg")
        img_exists = os.path.exists(img_path)
        is_char = is_likely_character_shot(vo, desc)
        status = "[STATUS: COMPLETED]" if img_exists else "[STATUS: PENDING]"

        prompt_lines.append(f"SHOT {i:03d} | {tc} | {status}")
        prompt_lines.append(f"VO: {vo}")
        prompt_lines.append(f"DESCRIPTION: {desc}")
        prompt_lines.append(f"PROMPT: {prompt}\n")

        category = "VALID_STICK_FIGURE" if is_char else "NO_CHARACTER"
        audit_list.append({
            "shot_num": i,
            "timecode": tc,
            "voiceover": vo,
            "description": desc,
            "category": category,
            "regen_needed": not img_exists,
            "reason": "Generated by Gemini Stage 2 Engine.",
            "stick_prompt": prompt,
            "cv_info": {"character_detected": is_char}
        })

    # 3. Write storyboard_master.csv
    with open(master_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Shot #", "Time", "Spoken VO script", "Visual description", "Exact Prompt for google nano banana pro"])
        writer.writerows(rows)

    # 4. Write clean_ai_voiceover_script.txt
    full_vo_text = " ".join(r[2] for r in rows if r[2])
    with open(script_txt_path, "w", encoding="utf-8") as f:
        f.write(full_vo_text + "\n")

    # 5. Write all_prompts.txt
    with open(all_prompts_path, "w", encoding="utf-8") as f:
        f.write("\n".join(prompt_lines))

    # 6. Write character_audit.json
    with open(audit_json_path, "w", encoding="utf-8") as f:
        json.dump(audit_list, f, indent=2)

    # 7. Write PROMPT_STATUS.md
    completed_count = sum(1 for r in rows if os.path.exists(os.path.join(dirs["final_images_dir"], f"shot_{int(r[0]):03d}.jpg")))
    pct = (completed_count / total_shots * 100.0) if total_shots > 0 else 0.0
    status_md = f"""# Storyboard Production Status: {video_title}

- **Total Shots**: {total_shots}
- **Completed Images**: {completed_count} / {total_shots} ({pct:.1f}%)
- **Pending Images**: {total_shots - completed_count}
- **Generated Engine**: Google Gemini API (Autonomous 1-Click)
- **Master CSV**: [`storyboard_master.csv`](storyboard_master.csv)
- **All Prompts Book**: [`all_prompts.txt`](all_prompts.txt)
- **Character Audit**: [`character_audit.json`](character_audit.json)
"""
    with open(prompt_status_md, "w", encoding="utf-8") as f:
        f.write(status_md)

    print(f"[GEMINI STAGE 2 COMPLETE] {total_shots} shots prepared for '{video_title}'.")
    return {
        "success": True,
        "engine": "gemini",
        "total_shots": total_shots,
        "completed_count": completed_count,
        "master_csv": master_csv_path,
        "script_txt": script_txt_path,
        "all_prompts": all_prompts_path,
        "audit_json": audit_json_path,
        "char_count": len(full_vo_text),
        "word_count": len(full_vo_text.split())
    }
