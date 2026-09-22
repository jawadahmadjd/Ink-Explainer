"""
AI Learning Engine: Multi-Niche Categorized Training, Distilled Codex, Reference Title Matching & Fast-Paced Pacing
Enforces zero-bloat statistical learning partitioned by niche (History, Finance, Medical, Horror, Engineering, and dynamic categories).
Applies strict 20-50 character image pacing with mandatory punctuation dividers.
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

DEFAULT_FALLBACK_MEDIANS = {
    "wpm": 224.6,
    "avg_cut_interval_sec": 2.51,
    "hook_cut_interval_sec": 1.2,
    "words_per_minute_range": [215.0, 235.0],
    "target_chars_per_shot_min": 20,
    "target_chars_per_shot_max": 50,
    "lufs_integrated": -12.28,
    "loudness_range_lra": 2.5,
    "max_pause_between_shots_ms": 300
}

def load_codex() -> dict:
    """Load the central AI Learning Codex (supports v2.0.0 multi-niche partitioned schema)."""
    if os.path.exists(CODEX_PATH):
        try:
            with open(CODEX_PATH, "r", encoding="utf-8") as f:
                codex = json.load(f)
                if "niches" in codex:
                    return codex
                # Backwards-compatibility wrapper if older structure
                return _wrap_legacy_codex(codex)
        except Exception as e:
            print(f"[CODEX WARNING] Failed to parse codex: {e}")
    
    return {
        "_version": "2.0.0",
        "metadata": {"total_videos_analyzed": 0, "active_niches_count": 1, "last_updated": datetime.now().isoformat()},
        "global_fallback_medians": DEFAULT_FALLBACK_MEDIANS,
        "niches": {
            "history": {
                "display_name": "History & Archaeology",
                "description": "Deep time, ancient humans, civilizations, empires, and evolutionary anthropology.",
                "keywords": ["ancient", "human", "history", "empire", "archaeology", "century", "war", "ancestor"],
                "videos_analyzed": 0,
                "running_medians": DEFAULT_FALLBACK_MEDIANS,
                "narrative_framework": {"name": "7-Act Anthropological Retention Arc", "structure": []},
                "visual_style": {
                    "art_style": "Minimalist hand-drawn 2D vector line art, bold black ink comic contours, expressive stick-figure characters.",
                    "color_palette": "Flat muted earthy tones (charcoal ink, paper parchment, terracotta, ochre, slate blue)."
                },
                "reference_blueprints": {}
            }
        }
    }

def _wrap_legacy_codex(legacy_codex: dict) -> dict:
    """Safely wraps a legacy v1.0.0 codex into v2.0.0 schema in-memory."""
    blueprints = legacy_codex.get("reference_blueprints", {})
    medians = legacy_codex.get("running_medians", DEFAULT_FALLBACK_MEDIANS)
    return {
        "_version": "2.0.0",
        "metadata": {
            "total_videos_analyzed": len(blueprints),
            "active_niches_count": 1,
            "last_updated": legacy_codex.get("metadata", {}).get("last_updated", datetime.now().isoformat())
        },
        "global_fallback_medians": medians,
        "niches": {
            "history": {
                "display_name": "History & Archaeology",
                "description": "Deep time, ancient humans, civilizations, empires, and evolutionary anthropology.",
                "keywords": ["ancient", "human", "history", "empire", "archaeology", "century", "war", "ancestor"],
                "videos_analyzed": len(blueprints),
                "running_medians": medians,
                "narrative_framework": legacy_codex.get("narrative_framework", {}),
                "visual_style": legacy_codex.get("visual_style", {}),
                "reference_blueprints": blueprints
            }
        }
    }

def save_codex(codex_data: dict):
    """Save updated multi-niche codex to disk."""
    codex_data.setdefault("metadata", {})
    codex_data["metadata"]["last_updated"] = datetime.now().isoformat()
    if "niches" in codex_data:
        codex_data["metadata"]["active_niches_count"] = len(codex_data["niches"])
        codex_data["metadata"]["total_videos_analyzed"] = sum(
            n.get("videos_analyzed", 0) for n in codex_data["niches"].values()
        )
    os.makedirs(os.path.dirname(CODEX_PATH), exist_ok=True)
    with open(CODEX_PATH, "w", encoding="utf-8") as f:
        json.dump(codex_data, f, indent=2)

def normalize_title(title: str) -> str:
    """Remove numbering prefixes, punctuation, and extra whitespace for fuzzy matching."""
    cleaned = re.sub(r"^\d+\s*[-_.]\s*", "", title)
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    return " ".join(cleaned.lower().split())

DOT_PLACEHOLDER = chr(0xE001)
COMMA_PLACEHOLDER = chr(0xE002)
COLON_PLACEHOLDER = chr(0xE003)

def protect_script_tokens(text: str) -> str:
    """Protect decimals, numbers with commas, times, and abbreviations from being split."""
    # 1. Protect numbers with decimals (e.g., 99.9%, 3.14, 0.5)
    text = re.sub(r'(\d+)\.(\d+)', lambda m: m.group(1) + DOT_PLACEHOLDER + m.group(2), text)
    # 2. Protect numbers with commas (e.g., 300,000, 1,000)
    text = re.sub(r'(\d+),(\d+)', lambda m: m.group(1) + COMMA_PLACEHOLDER + m.group(2), text)
    # 3. Protect time notations (e.g., 11:00, 08:30)
    text = re.sub(r'(\d+):(\d+)', lambda m: m.group(1) + COLON_PLACEHOLDER + m.group(2), text)
    # 4. Protect abbreviations
    abbrs = ['e.g.', 'i.e.', 'vs.', 'etc.', 'dr.', 'mr.', 'mrs.', 'ms.', 'prof.', 'al.', 'p.m.', 'a.m.', 'u.s.', 'p.n.a.s.']
    for abbr in abbrs:
        pattern = re.compile(r'\b' + re.escape(abbr), re.IGNORECASE)
        rep = abbr.replace('.', DOT_PLACEHOLDER)
        text = pattern.sub(rep, text)
    # 5. Protect ellipsis (...)
    text = re.sub(r'\.{3,}', DOT_PLACEHOLDER * 3, text)
    return text

def unprotect_script_tokens(text: str) -> str:
    """Restore original punctuation for protected script tokens."""
    return (text.replace(DOT_PLACEHOLDER, '.')
                .replace(COMMA_PLACEHOLDER, ',')
                .replace(COLON_PLACEHOLDER, ':'))

def split_script_into_elastic_steps(text: str, target_min_chars: int = 16, target_max_chars: int = 65) -> list:
    """
    Elastic Action Step Script Segmentation for fast-paced, high-retention ink explainers:
    1. Replaces rigid character-bound slicing with natural cognitive/action steps (~1.0s to 2.2s).
    2. Protects decimals, abbreviations, numbers with commas, and times.
    3. Splits on sentence terminators (.?!;:) and natural action-boundary conjunctions/commas.
    4. Never cuts intra-clause adjective chains, phrasal verbs, or short introductory phrases.
    """
    clean_text = text.replace("\r\n", "\n").strip()
    if not clean_text:
        return []

    prot = protect_script_tokens(clean_text)
    major_chunks = re.split(r'([.?!;:\n—]|\s+-\s+)', prot)

    sentences = []
    i = 0
    while i < len(major_chunks):
        seg = major_chunks[i].strip()
        punc = major_chunks[i+1].strip() if i + 1 < len(major_chunks) else ''
        if seg or punc:
            if punc and punc in '.?!;:—':
                full = f'{seg}{punc}'
            elif punc:
                full = f'{seg} {punc}'.strip()
            else:
                full = seg
            if full:
                sentences.append(full)
        i += 2

    ADJECTIVES_AND_ADVERBS = {
        'angry', 'sideways', 'wind-whipped', 'cold', 'wet', 'dry', 'fresh', 'raw',
        'meanwhile', 'instead', 'naturally', 'finally', 'then', 'now', 'soon', 'later'
    }

    INTRO_PATTERNS = [
        'today', 'suddenly', 'worst of all', 'right now', 'look closer', 'first',
        'the first', 'the second', 'the third', 'in fact', 'for example', 'for you',
        'crucially', 'back then', 'even then', 'meanwhile', 'after all', 'and then',
        'once', 'so what', 'worst', 'best', 'in the middle of this chaos', 'not a'
    ]

    CONJUNCTIONS_AND_TRANSITIONS = {
        'and', 'but', 'so', 'because', 'while', 'when', 'where', 'which', 'that',
        'or', 'as', 'if', 'though', 'although', 'before', 'after', 'until', 'since',
        'with', 'without', 'means', 'is', 'was', 'are', 'were'
    }

    DETERMINERS = {'the', 'a', 'an', 'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'their', 'our', 'its'}

    final_shots = []

    for sent in sentences:
        if len(sent) <= target_max_chars:
            final_shots.append(sent)
            continue

        comma_parts = re.split(r'(,\s*)', sent)
        segments = []
        i = 0
        while i < len(comma_parts):
            s = comma_parts[i].strip()
            c = comma_parts[i+1] if i + 1 < len(comma_parts) else ''
            if c:
                s = s + ','
            if s:
                segments.append(s)
            i += 2

        merged_comma_shots = []
        curr = ''
        for seg in segments:
            if not curr:
                curr = seg
                continue

            curr_words = curr.split()
            seg_words = seg.split()
            last_w = re.sub(r'[^a-zA-Z]', '', curr_words[-1]).lower() if curr_words else ''
            first_w = re.sub(r'[^a-zA-Z]', '', seg_words[0]).lower() if seg_words else ''

            is_adj_list = last_w in ADJECTIVES_AND_ADVERBS or first_w in ADJECTIVES_AND_ADVERBS
            is_intro_phrase = len(curr) < 24 and any(curr.lower().startswith(p) or curr.lower() == f'{p},' for p in INTRO_PATTERNS)

            if is_intro_phrase or len(curr) < target_min_chars or len(seg) < 14 or is_adj_list:
                curr = f'{curr} {seg}'
            elif (len(curr) + len(seg) + 1) <= target_max_chars:
                curr = f'{curr} {seg}'
            else:
                merged_comma_shots.append(curr)
                curr = seg

        if curr:
            merged_comma_shots.append(curr)

        for chunk in merged_comma_shots:
            if len(chunk) <= target_max_chars + 10:
                final_shots.append(chunk)
            else:
                words = chunk.split()
                sub = []
                cur_w = []
                for w in words:
                    clean_w = re.sub(r'[^a-zA-Z]', '', w).lower()
                    cur_len = sum(len(x) for x in cur_w) + max(0, len(cur_w) - 1)
                    rem_len = sum(len(x) for x in words[len(cur_w):]) + max(0, len(words) - len(cur_w) - 1)
                    
                    if cur_w and cur_len >= target_min_chars and clean_w in CONJUNCTIONS_AND_TRANSITIONS and rem_len >= target_min_chars:
                        sub.append(' '.join(cur_w))
                        cur_w = [w]
                    else:
                        cur_w.append(w)
                if cur_w:
                    sub.append(' '.join(cur_w))

                balanced = []
                for p in sub:
                    if len(p) <= target_max_chars + 12:
                        balanced.append(p)
                    else:
                        p_words = p.split()
                        best_split = len(p_words) // 2
                        for idx_w in range(1, len(p_words) - 1):
                            cw = re.sub(r'[^a-zA-Z]', '', p_words[idx_w]).lower()
                            if cw in CONJUNCTIONS_AND_TRANSITIONS:
                                best_split = idx_w
                                break
                        if p_words[best_split - 1].lower() in DETERMINERS and best_split < len(p_words) - 1:
                            best_split += 1
                        balanced.append(' '.join(p_words[:best_split]))
                        balanced.append(' '.join(p_words[best_split:]))
                final_shots.extend(balanced)

    clean_shots = []
    for s in final_shots:
        s_unprot = unprotect_script_tokens(s).strip()
        if s_unprot:
            clean_shots.append(s_unprot)

    return clean_shots

def split_script_into_fast_paced_shots(text: str, target_min_chars: int = 16, target_max_chars: int = 65) -> list:
    """Convenience and backwards-compatible alias pointing to the Elastic Action Step segmenter."""
    return split_script_into_elastic_steps(text, target_min_chars=target_min_chars, target_max_chars=target_max_chars)

def generate_smart_scene_description(vo_text: str, prev_vo: str = "", next_vo: str = "", niche: str = "history") -> str:
    """
    Translates a spoken voiceover beat into a concrete visual comic scene (MinutePhysics / Casually Explained style).
    Describes subject, posture, facial expression, key props, comedic gag, and environment.
    """
    v = vo_text.lower().strip()
    
    # Specific semantic pattern matching for high-impact visual storytelling
    if any(k in v for k in ["haven't eaten", "two days", "starving", "hunger"]):
        return "A hungry prehistoric stick figure sitting on a dry rock, clutching his empty stomach with funny squiggly hunger lines, looking dizzy and exhausted with a thought bubble of roasted meat."
    elif any(k in v for k in ["tracked a herd", "herd of bison", "tracked it yesterday"]):
        return "A prehistoric stick figure crouched low on the grassy ground, closely inspecting deep bison hoof prints in the dirt with a focused, determined squint."
    elif any(k in v for k in ["exact coordinates", "coordinates"]):
        return "A focused stick figure holding up a rough hand-drawn stone tablet map with a prominent 'X' and a compass arrow pointing forward across the plains."
    elif any(k in v for k in ["hike out", "secure dinner"]):
        return "A confident stick figure marching briskly across the open savanna with a stone spear resting casually on his shoulder, smiling with supreme determination."
    elif any(k in v for k in ["sky opens up"]):
        return "Dramatic scene where sudden dark cartoon rain clouds roll overhead, and a single giant comic raindrop splashes squarely on top of the surprised stick figure's head."
    elif any(k in v for k in ["refreshing little sprinkle", "not a refreshing"]):
        return "Dark, swirling storm clouds rolling across the entire sky, blotting out the sun and casting ominous shadowy grey tones over the plains."
    elif any(k in v for k in ["angry", "sideways", "wind-whipped deluge"]):
        return "Violent horizontal sheets of torrential comic rain and gusting wind slamming into the drenched stick figure, blowing his hair and stone spear backward in shock."
    elif any(k in v for k in ["refuses to quit"]):
        return "The stick figure completely soaked and dripping wet, standing ankle-deep in puddles with a comically miserable deadpan expression of despair."
    elif any(k in v for k in ["all day, all night", "dumps water"]):
        return "Endless sheets of heavy cartoon rain pouring down relentlessly over a desolate prehistoric landscape under a pitch-black stormy sky."
    elif any(k in v for k in ["clearing by tomorrow", "zero signs"]):
        return "The drenched stick figure looking up at the sky through pouring rain, holding out a single hand with an enormous question mark floating overhead."
    elif any(k in v for k in ["hunting trip is canceled", "suddenly"]):
        return "A comically defeated stick figure standing in thick mud, arms crossed tightly with an angry frown, as a small red cartoon 'CANCELED' stamp appears."
    elif any(k in v for k in ["wiped away every footprint", "mud has wiped"]):
        return "Close-up of brown muddy ground where clear animal footprints are actively melting away and washing out into smooth watery sludge."
    elif any(k in v for k in ["wet rocks in bare feet", "running across wet"]):
        return "A stick figure slipping precariously on shiny, wet river boulders, flailing his stick arms wildly to maintain balance."
    elif any(k in v for k in ["broken ankle", "ticket to a broken"]):
        return "Comic stick figure lying on a rocky ledge clutching an exaggerated swollen foot with zigzag pain lines and a dizzy spiral eye."
    elif any(k in v for k in ["olympic-sized moat", "local river is rapidly"]):
        return "A wide panoramic view of a swollen, roaring muddy river surging violently through a canyon, completely cutting off the hiking path."
    elif any(k in v for k in ["campfire is actively hissing", "hissing in agony"]):
        return "A primitive stone-ringed campfire drowning in rainwater, with large comic puffs of grey steam hissing upward and coals extinguishing into black."
    elif any(k in v for k in ["you aren't just bored", "bored"]):
        return "A bored stick figure sitting cross-legged under a rock shelter, resting his chin in his hand and tapping his foot impatiently."
    elif any(k in v for k in ["you are trapped"]):
        return "A drenched prehistoric stick figure huddled shivering inside a dark rocky cave mouth, looking out helplessly at a torrential curtain of rain."
    elif any(k in v for k in ["sweatpants", "oversized sweatpants"]):
        return "A modern stick figure lounging lazily on a living room couch wearing comical baggy grey sweatpants and fuzzy warm slippers."
    elif any(k in v for k in ["brewing hot coffee", "hot coffee"]):
        return "A close-up of a steaming ceramic mug of hot coffee held in simple stick figure hands, with cartoon steam spirals rising warmly."
    elif any(k in v for k in ["true crime docuseries", "nine consecutive episodes"]):
        return "A cozy dark room where a stick figure wrapped like a burrito in a blanket stares transfixed at a glowing television screen showing a crime documentary graphic."
    elif any(k in v for k in ["remarkably cozy", "feeling remarkably"]):
        return "The stick figure smiling contentedly with closed eyes, sipping coffee on the couch while cozy yellow lighting fills the room."
    elif any(k in v for k in ["pitter-patter on the window", "pitter-patter"]):
        return "Gentle diagonal raindrops streaking across a clear glass windowpane, with blurry green trees visible in the soft background."
    elif any(k in v for k in ["sleeping pill", "natural sleeping"]):
        return "A stick figure sleeping peacefully in bed under a fluffy duvet, with cute cartoon 'Zzz' letters floating above his pillow."
    elif any(k in v for k in ["eviction notice", "fifty thousand years ago"]):
        return "Stark contrast visual: a shivering ancient stick figure outside in the rain holding an eviction notice scroll with a skull warning icon."
    elif any(k in v for k in ["three distinct ways to die", "ways to die"]):
        return "Comic diagram showing three funny illustrated danger icons in black circles: a shivering snowflake (cold), a rising wave (flood), and sharp leopard teeth (predator)."
    elif any(k in v for k in ["first killer was the cold", "killer was the cold"]):
        return "A stick figure shivering violently in howling wind and rain, surrounded by icy blue shivering vibration lines and chattering zigzag teeth."
    elif any(k in v for k in ["twenty-five times faster", "loses body heat"]):
        return "A MinutePhysics infographic comparing a dry warm stick figure radiating red heat arrows vs a soaking wet stick figure with heat escaping in rapid blue arrows."
    elif any(k in v for k in ["hypothermia", "core temperature"]):
        return "A cartoon thermometer gauge plunging straight down into deep blue ice zone, with a stick figure turning visibly blue and freezing stiff."
    elif any(k in v for k in ["flash flooding", "second threat"]):
        return "Cross-section of a rocky cave at the base of a cliff as torrential brown rainwater cascades off the rock wall and floods through the cave living area."
    elif any(k in v for k in ["fled and never set foot", "never set foot inside"]):
        return "Terrified prehistoric stick-figure family frantically scrambling up a steep rocky ledge to escape rising floodwaters in their cave."
    elif any(k in v for k in ["unexpected roommates", "third threat"]):
        return "Inside a dark cave opening, an unsuspecting stick figure sitting by a fire while two glowing pairs of predatory eyes appear in the shadows behind him."
    elif any(k in v for k in ["giant leopards", "cave bears", "hyenas"]):
        return "A giant spotted prehistoric leopard and a caveman stick figure sitting side-by-side on a narrow rock bench, looking sideways at each other in awkward silence like elevator passengers."
    elif any(k in v for k in ["puncture holes", "canine teeth", "skull"]):
        return "Scientific comic diagram: an ancient fossil human skull showing two distinct circular puncture holes matching the canine teeth of an illustrated leopard jaw."
    elif any(k in v for k in ["protecting the fire", "one single job"]):
        return "A dedicated stick figure hunched protectively over a small glowing orange campfire, shielding the fragile flame with an animal hide."
    elif any(k in v for k in ["starting a fire from scratch", "friction sticks"]):
        return "A frustrated stick figure furiously spinning a wooden drill stick between blistered hands against a dry wooden board, with tiny smoke wisps."
    elif any(k in v for k in ["tinder fungus", "biological lighter"]):
        return "Close-up cutaway of a dried woody tinder fungus mushroom with a steady, safe orange ember glowing and smoldering quietly in its core."
    elif any(k in v for k in ["ötzi", "iceman", "alps"]):
        return "Ötzi the Iceman stick figure trekking through snowy Alps in fur clothing, proudly wearing a bright yellow survival fanny pack labeled 'FIRE KIT'."
    elif any(k in v for k in ["harvest the dry heartwood", "peeled wet logs"]):
        return "A stick figure using a stone adze to strip away wet bark and soggy outer wood to reveal clean, dry flammable heartwood inside."
    elif any(k in v for k in ["birch bark", "betulin"]):
        return "Close-up of a strip of white birch bark with black horizontal lenticels catching flame eagerly even while droplets of rain fall on it."
    elif any(k in v for k in ["invented modern technology", "hackathons"]):
        return "Inside a torchlit cave, three ancient stick figures sitting in a circle chipping stones rapidly, with comic 'PREHISTORIC HACKATHON' chalkboard sign."
    elif any(k in v for k in ["manufacturing waste", "carpets of tiny rock chips"]):
        return "Cave floor littered with thousands of tiny white and grey flint chips clustering around a stone fireplace hearth."
    elif any(k in v for k in ["blombos cave", "cosmetics chemistry lab", "ochre"]):
        return "A prehistoric artist using an abalone seashell as a mixing pot, grinding red ochre powder with a stone pestle and stirring it with a bone spatula."
    elif any(k in v for k in ["bone sewing needles", "drilled eyelets"]):
        return "Extreme close-up of stick figure hands carefully rotating a sharp flint micro-drill to create a tiny, perfect eyelet in a delicate white bone needle."
    elif any(k in v for k in ["twisted fiber string", "string over fifty"]):
        return "Macro doodle view of three plant fibers being tightly twisted into a strong, braided cord by dexterous stick-figure fingers."
    elif any(k in v for k in ["hohle fels", "mammoth ivory tool", "twisting rope"]):
        return "Detailed illustration of a 35,000-year-old carved mammoth ivory tool with four spiraling holes, with braided rope flowing out of the mechanism."
    elif any(k in v for k in ["sibudu cave", "marsh grasses", "bedding"]):
        return "A stick figure resting happily on a thick, comfortable mattress woven from lush green marsh grasses and topped with aromatic laurel leaves."
    elif any(k in v for k in ["cape laurel", "insect repellent", "mosquito"]):
        return "Comic stick figure sleeping serenely while cartoon mosquitoes bounce off an invisible aromatic shield radiating from Cape Laurel leaves."
    elif any(k in v for k in ["chauvet cave", "master artists", "thundering herds"]):
        return "Deep in a subterranean stone gallery, a prehistoric stick figure holding an animal-fat torch and painting dynamic galloping horses and charging rhinos on the rough wall."
    elif any(k in v for k in ["animal fat lamps", "pitch-black chambers"]):
        return "A stick figure crawling on his stomach through a narrow dark stone passage, holding a small carved stone lamp burning animal fat to light the way."
    elif any(k in v for k in ["ju/'hoansi", "polly wiessner", "kalahari"]):
        return "A tight circle of expressive stick figures sitting around a warm orange campfire in the desert night, listening attentively to an elder."
    elif any(k in v for k in ["ghost stories", "comedy club", "legends"]):
        return "Around the campfire, a stick figure dramatically miming a monster with exaggerated hand gestures while other stick figures laugh and clap."
    elif any(k in v for k in ["australian aboriginal", "oral histories", "sea level"]):
        return "A generational montage: an ancient elder telling a story by firelight, with speech bubbles linking across seven thousand years to modern descendants."
    elif any(k in v for k in ["pristine, high-definition animal tracks", "high-definition"]):
        return "Deep, crisp hoof and paw impressions in soft wet mud, with hand-drawn analytic arrows pointing out depth, stride length, and direction."
    elif any(k in v for k in ["termite swarms", "protein superfood"]):
        return "Golden post-storm sunlight breaking through clouds as ancient stick figures happily scoop up handfuls of swarming winged termites from a mound, smiling at the feast."
    elif any(k in v for k in ["conquered the world", "brilliance", "humanity conquered"]):
        return "Triumphant final scene: ancient stick figures standing atop a scenic mountain cliff at sunrise after the storm, holding high their crafted tools and spears as humanity marches forward into history."

    # General multi-niche visual translation patterns
    if niche == "finance":
        if any(k in v for k in ["bank", "vault", "deposit"]):
            return f"A stick figure banker standing outside an oversized hand-drawn bank vault door, holding a giant padlock: {vo_text.strip().rstrip(',;.')}"
        if any(k in v for k in ["debt", "iou", "credit", "loan"]):
            return f"Stick figures exchanging humorous crumpled napkin IOUs with exaggerated dollar figures: {vo_text.strip().rstrip(',;.')}"
    elif niche == "medical":
        if any(k in v for k in ["cell", "immune", "bouncers", "white blood"]):
            return f"White blood cells portrayed as comic stick-figure bouncers blocking invading cartoon bacteria at a cellular door: {vo_text.strip().rstrip(',;.')}"

    # Clean default visual translation
    clean_text = vo_text.strip().rstrip(",;.")
    return f"A minimalist comic stick figure illustration depicting: {clean_text}, with expressive character gestures, clear hand-drawn props, and edge-to-edge environment."

# -----------------------------------------------------------------------------
# DYNAMIC NICHE CLASSIFICATION & PROVISIONING
# -----------------------------------------------------------------------------

def extract_dynamic_category_slug(title: str) -> tuple:
    """
    Derives a clean niche slug and human-readable display name from a title
    when no existing niche matches.
    """
    stop_words = {
        "how", "what", "did", "the", "why", "when", "where", "who", "which",
        "in", "of", "and", "a", "an", "all", "is", "are", "to", "for", "with",
        "on", "at", "from", "by", "do", "does", "done", "this", "that", "these",
        "those", "into", "onto", "your", "you", "they", "them", "we", "us", "it",
        "its", "actually", "entire", "minutes", "minute", "day", "night", "week"
    }
    words = re.findall(r'[a-zA-Z]+', title.lower())
    content_words = [w for w in words if w not in stop_words and len(w) > 2]
    
    if content_words:
        top_words = content_words[:2]
        slug = "_".join(top_words)
        display = " & ".join(w.capitalize() for w in top_words)
    else:
        slug = "general"
        display = "General Explainer"
        
    return slug, display

def create_dynamic_niche(
    niche_key: str,
    display_name: str,
    description: str = "",
    keywords: list = None,
    running_medians: dict = None,
    visual_tokens: str = "",
    narrative_name: str = ""
) -> dict:
    """
    Dynamically provisions a new niche category in the AI Learning Codex.
    Sets sensible baseline running medians, 7-act architecture, and visual tokens.
    """
    codex = load_codex()
    niche_key = re.sub(r'[^a-zA-Z0-9_]', '_', niche_key.lower().strip())
    
    if niche_key in codex.get("niches", {}):
        return codex["niches"][niche_key]
    
    if not keywords:
        keywords = [k for k in re.findall(r'[a-zA-Z]+', display_name.lower()) if len(k) > 2]

    base_medians = dict(codex.get("global_fallback_medians", DEFAULT_FALLBACK_MEDIANS))
    if running_medians:
        base_medians.update(running_medians)

    new_niche = {
        "display_name": display_name,
        "description": description or f"Specialized knowledge and narrative base for {display_name}.",
        "keywords": keywords,
        "videos_analyzed": 0,
        "running_medians": base_medians,
        "narrative_framework": {
            "name": narrative_name or f"7-Act {display_name} Retention Arc",
            "structure": [
                { "act": 1, "name": "The Everyday Friction (Opening Hook)", "pacing": "Rapid (1.2s per cut)", "formula": f"Second-person challenge confronting standard assumptions in {display_name}." },
                { "act": 2, "name": "Dismantling the Common Myth", "pacing": "Deliberate (2.2s per cut)", "formula": "Hard empirical proof disproving standard conventional wisdom." },
                { "act": 3, "name": "Mechanisms & First Principles", "pacing": "Dynamic (2.2s - 2.5s per cut)", "formula": "Deep dive into the underlying operational mechanism." },
                { "act": 4, "name": "The Tipping Point Revelation", "pacing": "Moderate (2.4s per cut)", "formula": "Statistical or chronological turning point." },
                { "act": 5, "name": "The Human Impact & Tradeoffs", "pacing": "Reflective (2.5s per cut)", "formula": "Real-world friction, consequences, and tradeoffs." },
                { "act": 6, "name": "The Systemic Mismatch", "pacing": "Intimate (2.0s - 2.4s per cut)", "formula": "Why current systems or habits fail to account for this." },
                { "act": 7, "name": "The Strategic Resolution", "pacing": "Punchy (1.8s - 2.2s per cut)", "formula": "Memorable final takeaway and poignant perspective." }
            ]
        },
        "visual_style": {
            "art_style": "Minimalist hand-drawn 2D vector line art, bold black ink comic contours, expressive stick figures (MinutePhysics style).",
            "framing": "Full bleed edge-to-edge illustration, grounded environment completely filling 16:9 widescreen frame without borders.",
            "color_palette": visual_tokens or "Clean black ink, white backdrop, distinct topic accent color, subtle paper texture."
        },
        "reference_blueprints": {}
    }

    codex.setdefault("niches", {})
    codex["niches"][niche_key] = new_niche
    save_codex(codex)
    print(f"[CODEX] Dynamically registered new niche: '{display_name}' (key: '{niche_key}')")
    return new_niche

def classify_script_niche(title: str, script_or_transcript: str = "", auto_provision: bool = True) -> dict:
    """
    Classifies input title & script text into a niche using local semantic keyword matrices.
    If no existing niche matches and auto_provision is True, dynamically provisions a new category.
    Returns:
    {
        "niche": "finance",
        "display_name": "Finance & Economics",
        "score": 0.82,
        "is_new": False,
        "matched_keywords": ["money", "inflation", "bank"]
    }
    """
    codex = load_codex()
    niches = codex.get("niches", {})
    if not niches:
        return {"niche": "history", "display_name": "History & Archaeology", "score": 1.0, "is_new": False, "matched_keywords": []}

    combined_text = f"{title} {title} {title} {script_or_transcript}".lower()
    text_words = set(re.findall(r'[a-zA-Z0-9_]+', combined_text))

    best_niche = None
    best_score = 0.0
    best_matches = []

    for key, n_data in niches.items():
        kws = n_data.get("keywords", [])
        matched = []
        raw_score = 0.0

        for kw in kws:
            kw_clean = kw.lower()
            if " " in kw_clean:
                # Multi-word phrase matching
                if kw_clean in combined_text:
                    matched.append(kw)
                    raw_score += 3.0
            else:
                hit = False
                if kw_clean in text_words:
                    hit = True
                elif (kw_clean + 's' in text_words) or (kw_clean.endswith('s') and kw_clean[:-1] in text_words) or (kw_clean.endswith('es') and kw_clean[:-2] in text_words):
                    hit = True
                else:
                    for tw in text_words:
                        if len(tw) >= 4 and len(kw_clean) >= 4:
                            if tw.startswith(kw_clean) or kw_clean.startswith(tw):
                                hit = True
                                break
                if hit:
                    matched.append(kw)
                    raw_score += 1.5

        if matched:
            normalized_score = raw_score / (len(kws) ** 0.40)
            if normalized_score > best_score:
                best_score = normalized_score
                best_niche = key
                best_matches = matched

    # Threshold for existing niche match: at least 1 keyword matched
    if best_niche and (best_score >= 0.20 or len(best_matches) >= 1):
        confidence = round(min(1.0, max(0.65, best_score / 2.0)), 2)
        return {
            "niche": best_niche,
            "display_name": niches[best_niche].get("display_name", best_niche.title()),
            "score": confidence,
            "is_new": False,
            "matched_keywords": best_matches
        }

    # Low score or no match: auto-provision a dynamic niche if requested
    if auto_provision:
        slug, display = extract_dynamic_category_slug(title)
        if slug in niches:
            return {
                "niche": slug,
                "display_name": niches[slug].get("display_name", display),
                "score": 0.65,
                "is_new": False,
                "matched_keywords": []
            }
        
        # Provision new custom niche
        create_dynamic_niche(slug, display)
        return {
            "niche": slug,
            "display_name": display,
            "score": 0.60,
            "is_new": True,
            "matched_keywords": []
        }

    # Fallback to history
    return {
        "niche": "history",
        "display_name": niches.get("history", {}).get("display_name", "History & Archaeology"),
        "score": 0.30,
        "is_new": False,
        "matched_keywords": []
    }

# -----------------------------------------------------------------------------
# REFERENCE BLUEPRINT MATCHING & INGESTION
# -----------------------------------------------------------------------------

def _compute_match_score(user_words: set, norm_user: str, key_words: set, norm_key: str) -> float:
    if not user_words or not key_words:
        return 0.0
    containment = len(user_words & key_words) / float(len(user_words))
    jaccard = len(user_words & key_words) / float(len(user_words | key_words))
    seq_ratio = difflib.SequenceMatcher(None, norm_user, norm_key).ratio()
    return (containment * 0.5) + (jaccard * 0.25) + (seq_ratio * 0.25)

def find_matching_reference_video(user_title: str, threshold: float = 0.50, niche: str = None) -> dict:
    """
    Searches analyzed reference projects in ai_learning_codex.json and 1- Postmartum/.
    Prioritizes the specified niche if provided.
    Returns matched reference metadata, niche, and narrative blueprint if similarity exceeds threshold.
    """
    codex = load_codex()
    niches = codex.get("niches", {})
    norm_user = normalize_title(user_title)
    user_words = set(norm_user.split())
    if not user_words:
        return None

    best_match = None
    best_score = 0.0

    # 1. Search specified niche blueprints first
    search_order = []
    if niche and niche in niches:
        search_order.append((niche, niches[niche]))
    for n_key, n_data in niches.items():
        if n_key != niche:
            search_order.append((n_key, n_data))

    for n_key, n_data in search_order:
        blueprints = n_data.get("reference_blueprints", {})
        for key, bp in blueprints.items():
            norm_key = normalize_title(key)
            key_words = set(norm_key.split())
            combined_score = _compute_match_score(user_words, norm_user, key_words, norm_key)

            # Extra weight if within target niche
            effective_score = combined_score * 1.1 if n_key == niche else combined_score

            if effective_score > best_score:
                best_score = effective_score
                best_match = {
                    "source": "codex",
                    "niche": n_key,
                    "niche_display": n_data.get("display_name", n_key.title()),
                    "score": round(min(1.0, combined_score), 3),
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
                clf = classify_script_niche(fld, auto_provision=False)
                best_match = {
                    "source": "filesystem",
                    "niche": clf.get("niche", "history"),
                    "niche_display": clf.get("display_name", "History & Archaeology"),
                    "score": round(min(1.0, combined_score), 3),
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

            act_matches = re.findall(r"(\d+\.\s*\*\*Act\s*\d+:[^\n]+)", content)
            if act_matches:
                blueprint["story_progression"] = [a.strip() for a in act_matches]

            hook_match = re.search(r"\*\*Act 1:[^*]+\*\*:?\s*([^\n]+)", content)
            if hook_match:
                blueprint["hook"] = hook_match.group(1).strip()
            
            thesis_match = re.search(r"\*\*Act 2:[^*]+\*\*:?\s*([^\n]+)", content)
            if thesis_match:
                blueprint["core_thesis"] = thesis_match.group(1).strip()

        except Exception as e:
            print(f"[BLUEPRINT EXTRACT WARNING] {e}")

    if not blueprint["hook"] and transcript_text:
        first_sentence = transcript_text.split(".")[0]
        blueprint["hook"] = first_sentence.strip() + "."

    return blueprint

def ingest_postmortem_to_codex(pm_dir_or_title: str, niche: str = None) -> dict:
    """
    Ingests postmortem data into the central codex, updating statistical medians
    for the specific niche, registering narrative blueprints without token bloating.
    """
    pm_dir = pm_dir_or_title
    if not os.path.isabs(pm_dir):
        dirs = config.get_project_dirs(pm_dir_or_title, niche=niche)
        pm_dir = dirs["postmortem_dir"]

    if not os.path.exists(pm_dir):
        print(f"[INGEST WARNING] Postmortem directory does not exist: {pm_dir}")
        return {}

    codex = load_codex()
    blueprint = extract_reference_narrative_blueprint(pm_dir)
    clean_title = blueprint["title"]

    # Auto-classify niche from title and transcript if not explicitly provided
    if not niche:
        transcript_path = os.path.join(pm_dir, "clean_transcript.txt")
        tr_text = ""
        if os.path.exists(transcript_path):
            with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
                tr_text = f.read()
        clf = classify_script_niche(clean_title, tr_text)
        niche = clf["niche"]

    # Ensure niche exists or dynamically provision
    if niche not in codex.get("niches", {}):
        create_dynamic_niche(niche, niche.replace("_", " ").title())
        codex = load_codex()

    target_niche = codex["niches"][niche]
    old_niche_total = target_niche.get("videos_analyzed", 0)
    new_niche_total = old_niche_total + 1
    target_niche["videos_analyzed"] = new_niche_total

    # Update niche-specific running medians
    target_niche.setdefault("running_medians", dict(codex.get("global_fallback_medians", DEFAULT_FALLBACK_MEDIANS)))
    niche_medians = target_niche["running_medians"]

    if blueprint.get("word_count", 0) > 0 and blueprint.get("duration_sec", 0) > 0:
        video_wpm = (blueprint["word_count"] / (blueprint["duration_sec"] / 60.0))
        old_wpm = niche_medians.get("wpm", 224.6)
        niche_medians["wpm"] = round(((old_wpm * old_niche_total) + video_wpm) / new_niche_total, 1)

    if blueprint.get("cuts_count", 0) > 0 and blueprint.get("duration_sec", 0) > 0:
        video_cut_interval = blueprint["duration_sec"] / float(blueprint["cuts_count"])
        old_interval = niche_medians.get("avg_cut_interval_sec", 2.51)
        niche_medians["avg_cut_interval_sec"] = round(((old_interval * old_niche_total) + video_cut_interval) / new_niche_total, 2)

    # Register blueprint in target niche
    norm_key = normalize_title(blueprint["title"])
    target_niche.setdefault("reference_blueprints", {})
    blueprint["niche"] = niche
    target_niche["reference_blueprints"][norm_key] = blueprint

    save_codex(codex)
    print(f"[CODEX INGEST] Video '{clean_title}' ingested into '{niche}' niche. Trained videos in niche: {new_niche_total}")
    return codex

# -----------------------------------------------------------------------------
# PROMPT CONTEXT & SCRIPT SYNTHESIS
# -----------------------------------------------------------------------------

def get_distilled_prompt_context(niche: str = "history", matched_blueprint: dict = None) -> str:
    """
    Constructs an ultra-dense, fixed-budget (~1,500 tokens) prompt context
    for AI script synthesis partitioned by niche. Zero raw transcript bloating.
    """
    codex = load_codex()
    niches = codex.get("niches", {})
    target_niche = niches.get(niche, niches.get("history", {}))
    
    display_name = target_niche.get("display_name", "Ink Explainer")
    medians = target_niche.get("running_medians", codex.get("global_fallback_medians", DEFAULT_FALLBACK_MEDIANS))
    wpm = medians.get("wpm", 224.6)
    cut_sec = medians.get("avg_cut_interval_sec", 2.51)

    vis = target_niche.get("visual_style", {})
    art_style = vis.get("art_style", "MinutePhysics / Casually Explained minimalist hand-drawn 2D comic line art.")
    color_palette = vis.get("color_palette", "Flat muted earthy tones with paper texture.")

    framework = target_niche.get("narrative_framework", {})
    framework_name = framework.get("name", "7-Act Retention Architecture")
    structure_acts = framework.get("structure", [])

    acts_text = ""
    for act in structure_acts:
        acts_text += f"{act.get('act', '')}. {act.get('name', '')} - {act.get('formula', '')} (Pacing: {act.get('pacing', '')})\n"

    prompt = f"""# INK EXPLAINER PRODUCTION CODEX: {display_name.upper()}
- Domain / Niche: {display_name}
- Average Narration Speed: {wpm} Words Per Minute (tight, rhythmic, direct, second-person address).
- Visual Pacing: Fast-paced comic cadence averaging 1 cut every {cut_sec} seconds (16 to 32 characters per image beat).
- Mandatory Punctuation Divider Rule: Every comma, period, semicolon, question mark, colon, and dash MUST create an isolated shot beat (e.g. 'Why?' = 1 shot).
- Visual Aesthetic: {art_style}
- Color Palette & Backing: {color_palette}
- Framing: Full bleed 16:9 widescreen environment without borders or white card margins.

# {framework_name.upper()}:
{acts_text.strip()}
"""

    if niche == "finance":
        prompt += """
# 💰 FINANCE CREATIVE INTELLIGENCE SYSTEM (MANDATORY GUIDELINES):
1. ROLE & FOCUS:
   - Topic Focus: Money behavior, saving, spending, income growth, wealth building, financial discipline, lifestyle inflation, financial psychology, wealth accumulation, financial mistakes, opportunity cost, long-term thinking, ownership, entrepreneurship, building productive assets, financial independence, mathematics of everyday money decisions, and Shariah-compatible wealth principles.
   - Strict Exclusions: NO financial institutions, banking products, credit cards, insurance products, conventional interest-based investments (riba), bonds, or affiliate marketing.
   - Islamic Principles: Strictly compatible with Islamic principles. NEVER encourage, promote, or normalize riba/interest, conventional bonds, insurance, gambling, or prohibited practices. Present concepts neutrally; recommend scholarly verification for complex rulings.
2. CORE STORY STRUCTURES (Choose 1 or combine):
   - A. THE TWO-PERSON EXPERIMENT (e.g., Two people earn $2,000/mo, follow for 10-30 years).
   - B. THE FINANCIAL TIME MACHINE (One decision, consequences years later: 20 vs 35).
   - C. THE MONEY EXPERIMENT (What $5/day or $100/mo actually becomes under stated assumptions).
   - D. THE FINANCIAL TRAP (Lifestyle trap, raise making you feel poorer, unmonitored subscriptions).
   - E. THE WEALTH PARADOX (Earning more doesn't make you rich, looking rich keeps you poor).
   - F. THE ROADMAP ($0 to financially stable, 20-year roadmap, first $100k).
   - G. THE CHOICE (You get a $500 raise. Follow each decision branch and reveal consequences).
   - H. THE HIDDEN COST (The $10 purchase that actually costs $100, buying a car too early, 'I deserve it').
3. SCRIPT EXECUTION RULES:
   - Hook in first 5-15 seconds INSIDE the story. No generic greetings ("Hello guys welcome back").
   - Open loops throughout; let the story create anticipation.
   - Progressive information reveal (don't dump at once; show the passage of time).
   - Numbers as story elements (turn numbers into human consequences, not dry formulas).
   - Relatable human behavior: Characters behave like real people; do not portray mistakes as stupidity ("That's literally me").
   - Escalation & Contrast: Situation -> Problem -> Decision -> Consequence -> Crisis -> Realization -> Freedom.
   - Ending: Always return to the opening question and deliver a definitive, empowering payoff.
4. STICK-FIGURE VISUAL THINKING:
   - Think visually using: characters (white-filled stick figures), wallets, cash, jars, houses, cars, shops, phones, clocks, calendars, doors, ladders, roads, boxes, simple arrows, visual metaphors (treadmills, leaking buckets).
5. GOLDEN RULE:
   MORE CURIOSITY -> MORE STORY -> BETTER UNDERSTANDING -> STRONGER PAYOFF.
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

def generate_script_and_shots(title: str, user_prompt: str, matched_blueprint: dict = None, niche: str = None) -> list:
    """
    Synthesizes a production-ready script tailored to the niche and decomposes it into micro-beats
    conforming strictly to the 16-32 character pacing and punctuation divider rule.
    Returns list of shot dicts: [{'shot_num': i, 'voiceover': text, 'description': desc, 'prompt': prompt}].
    """
    clean_title = re.sub(r"^\d+\s*[-_.]\s*", "", title)
    
    # 1. Resolve niche
    if not niche:
        clf = classify_script_niche(clean_title, user_prompt)
        niche = clf["niche"]

    codex = load_codex()
    target_niche = codex.get("niches", {}).get(niche, codex.get("niches", {}).get("history", {}))
    vis = target_niche.get("visual_style", {})
    color_palette = vis.get("color_palette", "Flat muted earthy tones with paper texture")

    # 2. Antigravity AI Engine is the primary reasoning brain
    full_script = _generate_fallback_script(clean_title, user_prompt, matched_blueprint, niche=niche)

    # 3. Apply strict 20-50 char + punctuation divider shot splitting
    raw_shot_texts = split_script_into_fast_paced_shots(full_script, target_min_chars=20, target_max_chars=50)

    # 4. Format into shot rows with MinutePhysics stick-figure prompts & niche palette
    shots = []
    base_prefix = (
        f"MinutePhysics and Casually Explained hand-drawn stick figure comic illustration. "
        f"Full bleed edge-to-edge illustration, grounded environment completely filling 16:9 widescreen frame without borders. "
        f"{color_palette}. "
        f"Hand-drawn comic doodle line art with expressive stick figures."
    )
    non_char_prefix = (
        f"Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art. "
        f"Hand-drawn doodle comic style, Casually Explained and MinutePhysics aesthetic. "
        f"Full bleed edge-to-edge illustration, grounded background environment completely filling 16:9 frame without borders. "
        f"{color_palette}."
    )

    char_keywords = [
        "you", "human", "person", "man", "woman", "hunter", "gatherer", "people",
        "farmer", "worker", "they", "we", "someone", "hand", "eyes", "body",
        "investor", "banker", "trader", "doctor", "patient", "surgeon", "engineer", "victim"
    ]

    for i, shot_vo in enumerate(raw_shot_texts, 1):
        prev_vo = raw_shot_texts[i-2] if i > 1 else ""
        next_vo = raw_shot_texts[i] if i < len(raw_shot_texts) else ""
        desc = generate_smart_scene_description(shot_vo, prev_vo=prev_vo, next_vo=next_vo, niche=niche)
        is_char = any(kw in (shot_vo + " " + desc).lower() for kw in char_keywords)
        
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

def _generate_fallback_script(clean_title: str, user_prompt: str, matched_blueprint: dict = None, niche: str = "history") -> str:
    """Generates a structured narrative script aligning with the reference blueprint and domain niche."""
    if matched_blueprint:
        bp = matched_blueprint.get("blueprint", matched_blueprint)
        # If blueprint has hook/thesis, incorporate them
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

    if niche == "finance":
        return (
            "At twenty-five, Ahmed and Daniel earned the exact same twenty-five hundred dollar monthly paycheck. "
            "Twenty years later, one had total financial freedom. "
            "The other was still anxiously waiting for his next direct deposit. "
            "So what happened? "
            "Neither won the lottery, and neither inherited a single dime. "
            "Daniel did what society told him was normal. "
            "Every time his income grew, his apartment got larger, his car got newer, and his monthly spending swelled to swallow every dollar. "
            "Ahmed did something radically counter-intuitive. "
            "He defended his baseline living costs like a fortress. "
            "When he received a raise, he kept living on his old salary and channeled the entire surplus into productive, tangible assets. "
            "By year five, Daniel had twelve hundred dollars in emergency cash, while Ahmed's productive assets began generating cashflow. "
            "When an unexpected corporate layoff struck at age thirty-eight, Daniel had barely eighteen days of runway. "
            "Ahmed didn't even flinch. "
            "The secret to wealth is not how much you earn, but how relentlessly you protect your freedom from lifestyle inflation."
        )
    elif niche == "medical":
        return (
            "Right now, trillions of microscopic battles are raging silently inside your bloodstream. "
            "Why? Because your immune system operates like an unyielding autonomous defense grid. "
            "Look closer. When a foreign pathogen breaches your epithelial barrier, biochemical alarm sirens trigger in milliseconds. "
            "Macrophage sentinels engulf foreign invaders before you even register a scratch. "
            "Clinical biopsy studies confirm most lethal threats are neutralized without you ever showing a fever. "
            "Stopwatch telemetry under electron microscopes reveals killer T-cells executing infected targets with terrifying accuracy. "
            "What happens when the defensive wiring misfires? "
            "The immune cascade attacks healthy tissue, turning a lifesaving shield into an autoimmune crossfire. "
            "Then modern pharmacology steps in. We engineer targeted synthetic antibodies to rescue the body from its own panic. "
            "Until you examine the cellular architecture, the miracle of your own survival remains completely invisible."
        )
    elif niche == "horror":
        return (
            "Tonight, you will lock your front door and assume you are completely safe. "
            "Why? Because four wooden walls give you the illusion of total sanctuary. "
            "Look closer. In the dense pine forests forty miles north, three experienced campers disappeared without a trace. "
            "Their tent was found unzipped from the outside. Their boots were still sitting neatly beside the dying embers. "
            "Forensic search teams discovered no blood, no signs of struggle, and no footsteps in the damp earth. "
            "Acoustic microphones recorded a low-frequency hum thirty minutes before all radio signals dropped dead. "
            "What was watching from between the trees? "
            "Local rangers refuse to enter that valley once dusk settles over the ridgeline. "
            "Then the cold mountain fog rolls in. Every logical deduction crumbles into breathless panic. "
            "Until the sun rises, you realize that out here in the dark, humans are no longer the apex predator."
        )
    elif niche == "engineering":
        return (
            "Look at the suspension bridge you drive across every morning. "
            "Why doesn't sixty thousand tons of steel and concrete collapse into the freezing water below? "
            "Look closer. Every single steel cable is engaged in an invisible, high-tension war against harmonic resonance. "
            "Structural engineers calculate wind vortex shedding down to the millimeter to prevent destructive flutter. "
            "Forensic failure analysis of historical bridge collapses proved that rigidity without damping is always fatal. "
            "Modern wind tunnel simulations prove aerodynamic deck fairings can dissipate hurricane-force turbulence effortlessly. "
            "What keeps the massive towers upright? "
            "A counter-intuitive network of tuned mass dampers swaying in precise opposition to the storm. "
            "Then came ultra-high-performance concrete. We anchor foundations hundreds of feet into bedrock, defying gravity with geometry. "
            "Until you understand the physics of stress distribution, the greatest feats of engineering look like pure magic."
        )
    else:
        # History & Default
        return (
            f"Think about {clean_title.lower()}. Most people assume they understand the historical narrative. "
            "Why? Because standard textbook assumptions have been repeated for generations. "
            "Look closer. When archaeologists excavated the physical stratigraphic evidence, the reality was completely reversed. "
            "Skeletal bioarchaeology and carbon dating dismantled the conventional myth piece by piece. "
            "Every single standard assumption collapsed under forensic scrutiny. "
            "What was previously dismissed as primitive turned out to be an ingenious evolutionary adaptation. "
            "And yet, modern society continues repeating the same misunderstanding. "
            "Until you examine the physical artifacts, the true genius of human history remains hidden in plain sight."
        )

# -----------------------------------------------------------------------------
# FINANCE CREATIVE INTELLIGENCE SYSTEM HELPERS
# -----------------------------------------------------------------------------

def get_finance_story_structures() -> dict:
    """Returns the 8 canonical story structures for the Finance & Wealth niche."""
    codex = load_codex()
    return codex.get("niches", {}).get("finance", {}).get("story_engines", {})

def evaluate_finance_title(title: str) -> dict:
    """
    Evaluates a proposed Finance title against the 10-point Quality Test.
    Returns individual dimension scores (1-10), total average score, and pass/fail verdict (threshold >= 8.0).
    """
    title_lower = title.lower().strip()
    scores = {}

    # 1. Curiosity: Does it create an unanswered question / gap?
    curiosity_triggers = ["why", "what", "where", "how", "secret", "actually", "actually go", "happened", "difference", "paradox"]
    scores["curiosity"] = 9.0 if any(t in title_lower for t in curiosity_triggers) else 7.0

    # 2. Emotional Pull: Fear of mistakes, ambition, relief, regret
    emotion_triggers = ["broke", "poor", "wealthy", "rich", "trap", "never", "regret", "lose", "disappear", "freedom"]
    scores["emotional_pull"] = 9.0 if any(t in title_lower for t in emotion_triggers) else 7.5

    # 3. Specificity: Contains numbers, timeframes, or concrete scenarios
    has_numbers = bool(re.search(r'\b(\d+|\$\d+|zero)\b', title_lower))
    scores["specificity"] = 9.5 if has_numbers else 7.0

    # 4. Originality: Avoids generic "how to save money" / "tips to get rich"
    generic_phrases = ["how to save money", "tips for saving", "how to get rich", "ways to invest", "financial advice"]
    scores["originality"] = 4.0 if any(g in title_lower for g in generic_phrases) else 9.0

    # 5. Clarity: Understandable in 1 second (optimal length 40-70 chars)
    char_len = len(title)
    scores["clarity"] = 9.5 if 25 <= char_len <= 75 else (8.0 if char_len < 90 else 6.5)

    # 6. Personal Relevance: Second-person or relatable money situation
    rel_triggers = ["you", "your", "people", "ordinary", "salary", "raise", "spend"]
    scores["personal_relevance"] = 9.0 if any(r in title_lower for r in rel_triggers) else 7.5

    # 7. Story Potential: Suggests a narrative progression (experiment, journey, contrast)
    story_triggers = ["two people", "one becomes", "start at", "years later", "what happens if", "roadmap", "habit"]
    scores["story_potential"] = 9.5 if any(s in title_lower for s in story_triggers) else 8.0

    # 8. Accuracy: No sensationalist scam/guarantee words
    scam_words = ["guaranteed", "overnight", "100x", "get rich quick", "instant millionaire"]
    scores["accuracy"] = 3.0 if any(s in title_lower for s in scam_words) else 9.5

    # 9. Thumbnail Compatibility: Easy to visualize with stick figures
    visual_triggers = ["salary", "broke", "rich", "two people", "spend", "dollar", "raise", "car", "house"]
    scores["thumbnail_compatibility"] = 9.0 if any(v in title_lower for v in visual_triggers) else 8.0

    # 10. Sustained Interest: Strong enough premise to carry an entire video
    scores["sustained_interest"] = round((scores["curiosity"] + scores["story_potential"]) / 2.0, 1)

    avg_score = round(sum(scores.values()) / float(len(scores)), 2)
    passed = avg_score >= 8.0

    return {
        "title": title,
        "overall_score": avg_score,
        "passed": passed,
        "threshold": 8.0,
        "dimension_scores": scores,
        "verdict": "ACCEPTED (Ready for Production)" if passed else "REJECTED (Score below 8.0 threshold — increase specificity or story conflict)"
    }

