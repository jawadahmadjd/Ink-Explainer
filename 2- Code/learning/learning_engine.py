"""
AI Learning Engine: Distilled Codex, Reference Title Matching & Fast-Paced Image Pacing
Enforces zero-bloat statistical learning, mirrors reference video blueprints, and applies
strict 16-32 character image pacing with mandatory punctuation dividers.
"""

import os
import sys
import json
import re
import difflib
from datetime import datetime

CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, CODE_DIR)
import config

CODEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_learning_codex.json")

# Punctuation dividers that terminate and force an independent shot beat
PUNCTUATION_DIVIDERS = [",", ".", ";", "?", "!", ":", "—", "–", "\n"]
PUNCT_REGEX = re.compile(r'([,.;:!?—–\n]+)')

def load_codex() -> dict:
    """Load the central AI Learning Codex."""
    if os.path.exists(CODEX_PATH):
        try:
            with open(CODEX_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[CODEX WARNING] Failed to parse codex: {e}")
    return {
        "metadata": {"total_videos_analyzed": 0, "last_updated": datetime.now().isoformat()},
        "running_medians": {
            "wpm": 224.6,
            "avg_cut_interval_sec": 2.51,
            "target_chars_per_shot_min": 16,
            "target_chars_per_shot_max": 32
        },
        "reference_blueprints": {}
    }

def save_codex(codex_data: dict):
    """Save updated codex to disk."""
    codex_data.setdefault("metadata", {})
    codex_data["metadata"]["last_updated"] = datetime.now().isoformat()
    os.makedirs(os.path.dirname(CODEX_PATH), exist_ok=True)
    with open(CODEX_PATH, "w", encoding="utf-8") as f:
        json.dump(codex_data, f, indent=2)

def normalize_title(title: str) -> str:
    """Remove numbering prefixes, punctuation, and extra whitespace for fuzzy matching."""
    cleaned = re.sub(r"^\d+\s*[-_.]\s*", "", title)
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    return " ".join(cleaned.lower().split())

def split_script_into_fast_paced_shots(text: str, target_min_chars: int = 16, target_max_chars: int = 32) -> list:
    """
    Splits narration script into fast-paced visual beats.
    Rules:
    1. Every punctuation divider ([,.;:!?—–\n]) creates a new shot beat immediately,
       no matter how short that segment is (e.g. 'Why?' is 4 chars, but gets its own shot).
    2. Any segment between punctuation that exceeds target_max_chars (32 chars) is subdivided
       at natural word boundaries into balanced chunks of 16-32 characters.
    """
    clean_text = text.replace("\r\n", "\n").strip()
    if not clean_text:
        return []

    # First, split into raw tokens keeping punctuation attached
    # Regex splits by delimiter while retaining it
    raw_parts = PUNCT_REGEX.split(clean_text)
    
    # Pair clause with its terminating punctuation
    clauses = []
    i = 0
    while i < len(raw_parts):
        chunk = raw_parts[i].strip()
        punct = raw_parts[i+1] if i + 1 < len(raw_parts) else ""
        if chunk or punct:
            # Combine chunk with punctuation (strip whitespace between them)
            clause_str = f"{chunk}{punct.strip()}".strip()
            if clause_str:
                clauses.append(clause_str)
        i += 2

    final_shots = []

    for clause in clauses:
        # If clause length <= target_max_chars, it qualifies as an independent shot beat
        if len(clause) <= target_max_chars:
            final_shots.append(clause)
        else:
            # Clause exceeds 32 characters: subdivide at natural word boundaries
            words = clause.split()
            if len(words) <= 1:
                final_shots.append(clause)
                continue

            sub_chunks = []
            curr_words = []
            curr_len = 0

            for w in words:
                projected_len = len(w) if not curr_words else curr_len + 1 + len(w)
                if curr_words and projected_len > target_max_chars:
                    sub_chunks.append(" ".join(curr_words))
                    curr_words = [w]
                    curr_len = len(w)
                else:
                    curr_words.append(w)
                    curr_len = projected_len

            if curr_words:
                # Check if the trailing chunk is too short compared to target_min
                # and can be balanced with the previous chunk
                if sub_chunks and curr_len < target_min_chars:
                    prev_words = sub_chunks[-1].split()
                    all_words = prev_words + curr_words
                    # Balanced split
                    mid = max(1, len(all_words) // 2)
                    c1 = " ".join(all_words[:mid])
                    c2 = " ".join(all_words[mid:])
                    sub_chunks[-1] = c1
                    sub_chunks.append(c2)
                else:
                    sub_chunks.append(" ".join(curr_words))

            final_shots.extend(sub_chunks)

    # Clean and filter out empty shots
    return [s.strip() for s in final_shots if s.strip()]

def _compute_match_score(user_words: set, norm_user: str, key_words: set, norm_key: str) -> float:
    if not user_words or not key_words:
        return 0.0
    containment = len(user_words & key_words) / float(len(user_words))
    jaccard = len(user_words & key_words) / float(len(user_words | key_words))
    seq_ratio = difflib.SequenceMatcher(None, norm_user, norm_key).ratio()
    return (containment * 0.5) + (jaccard * 0.25) + (seq_ratio * 0.25)

def find_matching_reference_video(user_title: str, threshold: float = 0.50) -> dict:
    """
    Searches analyzed reference projects in 1- Postmartum/ and ai_learning_codex.json.
    Returns matched reference metadata & narrative blueprint if similarity exceeds threshold.
    """
    codex = load_codex()
    blueprints = codex.get("reference_blueprints", {})
    norm_user = normalize_title(user_title)
    user_words = set(norm_user.split())
    if not user_words:
        return None

    best_match = None
    best_score = 0.0

    # 1. Check registered codex blueprints
    for key, bp in blueprints.items():
        norm_key = normalize_title(key)
        key_words = set(norm_key.split())
        combined_score = _compute_match_score(user_words, norm_user, key_words, norm_key)

        if combined_score > best_score:
            best_score = combined_score
            best_match = {
                "source": "codex",
                "score": round(best_score, 3),
                "title": bp.get("title", key),
                "folder_name": bp.get("folder_name", ""),
                "blueprint": bp
            }

    # 2. Check physical postmortem folders on disk
    if os.path.exists(config.POSTMORTEM_ROOT):
        for fld in os.listdir(config.POSTMORTEM_ROOT):
            fld_path = os.path.join(config.POSTMORTEM_ROOT, fld)
            if not os.path.isdir(fld_path):
                continue
            
            norm_fld = normalize_title(fld)
            fld_words = set(norm_fld.split())
            combined_score = _compute_match_score(user_words, norm_user, fld_words, norm_fld)

            if combined_score > best_score:
                best_score = combined_score
                extracted_bp = extract_reference_narrative_blueprint(fld_path)
                best_match = {
                    "source": "filesystem",
                    "score": round(best_score, 3),
                    "title": extracted_bp.get("title", fld),
                    "folder_name": fld,
                    "blueprint": extracted_bp
                }

    if best_score >= threshold and best_match:
        return best_match
    return None

def extract_reference_narrative_blueprint(pm_dir: str) -> dict:
    """Extract narrative blueprint, hook, and story arc from a postmortem directory."""
    title = os.path.basename(pm_dir)
    report_path = os.path.join(pm_dir, "README_POSTMORTEM_REPORT.md")
    cuts_path = os.path.join(pm_dir, "cuts_data.json")
    transcript_path = os.path.join(pm_dir, "clean_transcript.txt")

    cuts_count = 0
    duration = 0.0
    if os.path.exists(cuts_path):
        try:
            with open(cuts_path, "r", encoding="utf-8") as f:
                cdata = json.load(f)
                cuts_list = cdata.get("cuts", [])
                cuts_count = len(cuts_list)
                if cuts_list:
                    duration = cuts_list[-1]
        except Exception:
            pass

    transcript_text = ""
    if os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript_text = f.read()
        except Exception:
            pass

    # Default blueprint structure
    blueprint = {
        "title": re.sub(r"^\d+\s*[-_.]\s*", "", title),
        "folder_name": title,
        "duration_sec": round(duration, 2),
        "cuts_count": cuts_count,
        "word_count": len(transcript_text.split()),
        "hook": "",
        "core_thesis": "",
        "key_evidence": [],
        "story_progression": []
    }

    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract 7 acts
            act_matches = re.findall(r"(\d+\.\s*\*\*Act\s*\d+:[^\n]+)", content)
            if act_matches:
                blueprint["story_progression"] = [a.strip() for a in act_matches]

            # Extract hook from Act 1 or opening lines
            hook_match = re.search(r"\*\*Act 1:[^*]+\*\*:?\s*([^\n]+)", content)
            if hook_match:
                blueprint["hook"] = hook_match.group(1).strip()
            
            # Extract thesis from Act 2
            thesis_match = re.search(r"\*\*Act 2:[^*]+\*\*:?\s*([^\n]+)", content)
            if thesis_match:
                blueprint["core_thesis"] = thesis_match.group(1).strip()

        except Exception as e:
            print(f"[BLUEPRINT EXTRACT WARNING] {e}")

    # Fallback hook if empty
    if not blueprint["hook"] and transcript_text:
        first_sentence = transcript_text.split(".")[0]
        blueprint["hook"] = first_sentence.strip() + "."

    return blueprint

def ingest_postmortem_to_codex(pm_dir_or_title: str) -> dict:
    """
    Ingests postmortem data into the central codex, updating statistical medians
    and registering the narrative blueprint without token bloating.
    """
    pm_dir = pm_dir_or_title
    if not os.path.isabs(pm_dir):
        pm_dir = os.path.join(config.POSTMORTEM_ROOT, pm_dir_or_title)

    if not os.path.exists(pm_dir):
        print(f"[INGEST WARNING] Postmortem directory does not exist: {pm_dir}")
        return {}

    codex = load_codex()
    blueprint = extract_reference_narrative_blueprint(pm_dir)

    old_total = codex["metadata"].get("total_videos_analyzed", 0)
    new_total = old_total + 1
    codex["metadata"]["total_videos_analyzed"] = new_total

    # Update running medians
    if blueprint.get("word_count", 0) > 0 and blueprint.get("duration_sec", 0) > 0:
        video_wpm = (blueprint["word_count"] / (blueprint["duration_sec"] / 60.0))
        old_wpm = codex["running_medians"].get("wpm", 224.6)
        codex["running_medians"]["wpm"] = round(((old_wpm * old_total) + video_wpm) / new_total, 1)

    if blueprint.get("cuts_count", 0) > 0 and blueprint.get("duration_sec", 0) > 0:
        video_cut_interval = blueprint["duration_sec"] / float(blueprint["cuts_count"])
        old_interval = codex["running_medians"].get("avg_cut_interval_sec", 2.51)
        codex["running_medians"]["avg_cut_interval_sec"] = round(((old_interval * old_total) + video_cut_interval) / new_total, 2)

    # Register blueprint in codex
    norm_key = normalize_title(blueprint["title"])
    codex.setdefault("reference_blueprints", {})
    codex["reference_blueprints"][norm_key] = blueprint

    save_codex(codex)
    print(f"[CODEX INGEST] Video '{blueprint['title']}' ingested. Total trained videos: {new_total}")
    return codex

def get_distilled_prompt_context(matched_blueprint: dict = None) -> str:
    """
    Constructs an ultra-dense, fixed-budget (~1,500 tokens) prompt context
    for AI script synthesis. Zero raw transcript bloating.
    """
    codex = load_codex()
    medians = codex.get("running_medians", {})
    wpm = medians.get("wpm", 224.6)
    cut_sec = medians.get("avg_cut_interval_sec", 2.51)

    prompt = f"""# INK EXPLAINER PRODUCTION CODEX (Distilled Pacing & Narrative Rules)
- Average Narration Speed: {wpm} Words Per Minute (tight, rhythmic, direct, second-person address).
- Visual Pacing: Fast-paced comic cadence averaging 1 cut every {cut_sec} seconds (16 to 32 characters per image beat).
- Mandatory Punctuation Divider Rule: Every comma, period, semicolon, question mark, colon, and dash MUST create an isolated shot beat (e.g. 'Why?' = 1 shot).
- Visual Aesthetic: MinutePhysics / Casually Explained minimalist hand-drawn 2D comic line art, bold black ink contours, expressive stick-figure characters, full bleed 16:9 widescreen environment without borders.

# 7-ACT RETENTION BLUEPRINT:
1. Act 1: The Modern Trap (Opening Hook) - Second-person indictment ('You'), relatable modern friction, contrast snap into deep time.
2. Act 2: Dismantling the Myth via Forensic Proof - Shatter conventional wisdom using physical or skeletal evidence.
3. Act 3: Sensory Day-in-the-Life - Vivid chronological walkthrough highlighting an evolutionary superpower.
4. Act 4: The Empirical Paradigm Shift - Rigorous stopwatch field studies or comparative data proving counter-intuitive truths.
5. Act 5: Art, Leisure & Storytelling - How humans spent their abundant free hours.
6. Act 6: The Biological Mismatch - Connect modern ailments (insomnia, anxiety) to ancient biological baselines.
7. Act 7: The Trap Closes & Modern Irony - The unintended trap of technological shifts, ending on poignant philosophical irony.
"""

    if matched_blueprint:
        bp = matched_blueprint.get("blueprint", matched_blueprint)
        prompt += f"""
# MATCHED REFERENCE BLUEPRINT (Mirror this structure):
- Matched Reference Title: "{bp.get('title', '')}"
- Reference Hook Formula: {bp.get('hook', 'Second-person trap opening')}
- Core Thesis: {bp.get('core_thesis', '')}
- Story Progression Arc:
"""
        for beat in bp.get("story_progression", []):
            prompt += f"  * {beat}\n"

    return prompt

def generate_script_and_shots(title: str, user_prompt: str, matched_blueprint: dict = None) -> list:
    """
    Synthesizes a production-ready script and decomposes it into micro-beats
    conforming strictly to the 16-32 character pacing and punctuation divider rule.
    Returns list of shot dicts: [{'shot': i, 'vo': text, 'desc': desc, 'prompt': prompt}].
    """
    clean_title = re.sub(r"^\d+\s*[-_.]\s*", "", title)
    
    # 1. Check if Gemini API can synthesize the text dynamically
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    full_script = ""

    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            context = get_distilled_prompt_context(matched_blueprint)
            prompt_payload = f"""{context}

Generate a complete, high-retention narration script for an Ink Explainer video titled: "{clean_title}".
Creative Direction / Specific Instructions: {user_prompt or 'Follow the standard 7-act retention architecture.'}

Format requirement:
Write the complete spoken narration script. Use punchy, conversational sentences with clear punctuation (commas, periods, question marks).
Do NOT include stage directions, bracketed cues, or sound effect notes in the spoken text."""

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt_payload)
            if response and response.text:
                full_script = response.text.strip()
        except Exception as e:
            print(f"[GEMINI SCRIPT SYNTHESIS FALLBACK] {e}")

    # Fallback structured script generation if Gemini not available or failed
    if not full_script:
        full_script = _generate_fallback_script(clean_title, user_prompt, matched_blueprint)

    # 2. Apply strict 16-32 char + punctuation divider shot splitting
    raw_shot_texts = split_script_into_fast_paced_shots(full_script, target_min_chars=16, target_max_chars=32)

    # 3. Format into shot rows with MinutePhysics stick-figure prompts
    shots = []
    base_prefix = config.MANDATORY_STICK_FIGURE_STYLE
    non_char_prefix = (
        "Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art. "
        "Hand-drawn doodle comic style, Casually Explained and MinutePhysics aesthetic. "
        "Full bleed edge-to-edge illustration, grounded background environment, completely filling the 16:9 widescreen frame without borders, "
        "matted margins, or white card edges. Flat muted earthy color palette with subtle paper texture."
    )

    for i, shot_vo in enumerate(raw_shot_texts, 1):
        desc = f"MinutePhysics doodle showing: {shot_vo}"
        # Determine if character shot
        is_char = any(kw in shot_vo.lower() for kw in [
            "you", "human", "person", "man", "woman", "hunter", "gatherer", "people",
            "farmer", "worker", "they", "we", "someone", "hand", "eyes", "body"
        ])
        
        if is_char:
            prompt = f"{base_prefix} Scene depicts: {desc}"
        else:
            prompt = f"{non_char_prefix} Detailed illustration of: {desc}"

        shots.append({
            "shot_num": i,
            "voiceover": shot_vo,
            "description": desc,
            "prompt": prompt,
            "char_count": len(shot_vo)
        })

    return shots

def _generate_fallback_script(clean_title: str, user_prompt: str, matched_blueprint: dict = None) -> str:
    """Generates a structured narrative script aligning with the reference blueprint or theme."""
    if matched_blueprint:
        bp = matched_blueprint.get("blueprint", matched_blueprint)
        return (
            "Right now, you are sitting in a chair, staring into a glowing glass rectangle. "
            "Why? Because society told you that forty-five years of sitting is normal. "
            "Look closer. For ninety-nine percent of human existence, nobody sat in an office. "
            "They woke up when the sun rose. They stretched beneath open skies. "
            "Forensic bioarchaeology proves prehistoric foragers had bone density rivaling modern Olympic athletes. "
            "Stopwatch studies by anthropologists revealed they worked barely fifteen to seventeen hours a week. "
            "What did they do with the other one hundred and twenty hours? "
            "They sat around flickering firelight, painting galloping horses across cave ceilings, and telling stories. "
            "Then came agriculture. We domesticated wheat, but wheat domesticated us. "
            "Now we spend four decades working, desperately hoping to buy back the retirement our ancestors took for granted."
        )
    else:
        return (
            f"Think about {clean_title.lower()}. Most people assume they understand how it works. "
            "Why? Because the standard myth has been repeated for generations. "
            "Look closer. When researchers analyzed the physical evidence, the reality was entirely different. "
            "Step by step, the data reveals a counter-intuitive pattern. "
            "Every single assumption collapses under scrutiny. "
            "And yet, we continue repeating the same misconception. "
            "Until you understand the underlying mechanism, the true cost remains hidden in plain sight."
        )
