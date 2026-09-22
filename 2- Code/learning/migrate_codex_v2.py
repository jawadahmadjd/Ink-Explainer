"""
Migration script: Upgrades ai_learning_codex.json to v2.0.0 multi-niche architecture.
Preserves existing blueprints under 'history' and establishes starter niches (finance, medical, horror, engineering).
"""

import os
import json
import shutil
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CODEX_PATH = os.path.join(CURRENT_DIR, "ai_learning_codex.json")
BACKUP_PATH = os.path.join(CURRENT_DIR, "ai_learning_codex_v1_backup.json")

def migrate(force: bool = False):
    if not os.path.exists(CODEX_PATH):
        print(f"Error: {CODEX_PATH} not found.")
        return

    with open(CODEX_PATH, "r", encoding="utf-8") as f:
        old_codex = json.load(f)

    if not force and old_codex.get("_version") == "2.0.0" and len(old_codex.get("niches", {})) == 5:
        print("Codex is already at version 2.0.0 with 5 niches.")
        return

    if os.path.exists(BACKUP_PATH):
        with open(BACKUP_PATH, "r", encoding="utf-8") as bf:
            backup_codex = json.load(bf)
            old_blueprints = backup_codex.get("reference_blueprints", {})
    else:
        old_blueprints = old_codex.get("reference_blueprints", {})
        if "history" in old_codex.get("niches", {}):
            old_blueprints = old_codex["niches"]["history"].get("reference_blueprints", {})
        shutil.copyfile(CODEX_PATH, BACKUP_PATH)
        print(f"Backed up existing codex to {BACKUP_PATH}")
    old_medians = old_codex.get("running_medians", {
        "wpm": 224.6,
        "avg_cut_interval_sec": 2.51,
        "hook_cut_interval_sec": 1.2,
        "words_per_minute_range": [215.0, 235.0],
        "target_chars_per_shot_min": 16,
        "target_chars_per_shot_max": 32,
        "lufs_integrated": -12.28,
        "loudness_range_lra": 2.5,
        "max_pause_between_shots_ms": 300
    })

    v2_codex = {
        "_version": "2.0.0",
        "_description": "Multi-Niche AI Learning Codex with categorized statistical training bases and dynamic niche provisioning.",
        "metadata": {
            "total_videos_analyzed": len(old_blueprints),
            "active_niches_count": 5,
            "last_updated": datetime.now().isoformat()
        },
        "global_fallback_medians": old_medians,
        "pacing_rules": {
            "target_char_range": [16, 32],
            "punctuation_dividers": [",", ".", ";", "?", "!", ":", "—", "–", "\n"],
            "divider_rule_description": "Every punctuation mark acts as a mandatory divider to create a new shot regardless of character shortness. Non-punctuated text longer than 32 chars is subdivided at natural word boundaries targeting 16-32 chars per beat."
        },
        "niches": {
            "history": {
                "display_name": "History & Archaeology",
                "description": "Deep time, ancient humans, civilizations, empires, and evolutionary anthropology.",
                "keywords": [
                    "ancient", "human", "history", "empire", "archaeology", "century", "war", "ancestor",
                    "cave", "fossil", "king", "civilization", "stone age", "hunter", "gatherer", "rome",
                    "egypt", "iran", "persia", "medieval", "dynasty", "bc", "ad", "prehistoric"
                ],
                "videos_analyzed": len(old_blueprints),
                "running_medians": old_medians,
                "narrative_framework": {
                    "name": "7-Act Anthropological & Deep-Time Retention Arc",
                    "structure": [
                        { "act": 1, "name": "The Modern Trap (Opening Hook)", "pacing": "Ultra-fast (1.0s - 1.5s per cut)", "formula": "Second-person indictment ('You'), relatable modern friction, contrast snap into deep time." },
                        { "act": 2, "name": "Dismantling the Myth via Hard Evidence", "pacing": "Moderate (2.0s - 2.5s per cut)", "formula": "Shatter conventional wisdom using forensic skeletal bioarchaeology or physical artifacts." },
                        { "act": 3, "name": "Sensory Day-in-the-Life Immersion", "pacing": "Dynamic (2.2s - 2.8s per cut)", "formula": "Walk through a vivid chronological day. Highlight an evolutionary superpower (persistence hunting, sweating)." },
                        { "act": 4, "name": "The Empirical Paradigm Shift", "pacing": "Moderate (2.5s per cut)", "formula": "Cite rigorous stopwatch field research or global comparative data proving counter-intuitive truths." },
                        { "act": 5, "name": "The Human Core (Art, Leisure & Storytelling)", "pacing": "Lyrical (2.5s - 3.0s per cut)", "formula": "Explore what humans did with their 120 hours of leisure (cave art, beads, storytelling around fire)." },
                        { "act": 6, "name": "The Biological Mismatch", "pacing": "Intimate (2.0s - 2.5s per cut)", "formula": "Connect modern ailments (insomnia, anxiety) to ancient evolutionary adaptations (biphasic sleep)." },
                        { "act": 7, "name": "The Trap Closes & Modern Irony", "pacing": "Punchy (1.5s - 2.2s per cut)", "formula": "Progress created unintended entrapment (agriculture, granaries, taxes), ending on poignant philosophical irony." }
                    ]
                },
                "visual_style": {
                    "art_style": "Minimalist hand-drawn 2D vector line art, bold black ink comic contours, expressive stick-figure characters (MinutePhysics & Casually Explained aesthetic).",
                    "framing": "Full bleed edge-to-edge illustration, grounded environment completely filling 16:9 widescreen frame without borders.",
                    "color_palette": "Flat muted earthy tones (charcoal ink, paper parchment, terracotta, ochre, slate blue)."
                },
                "reference_blueprints": old_blueprints
            },
            "finance": {
                "display_name": "Finance & Economics",
                "description": "Wealth creation, markets, investing, banking, debt, inflation, currencies, and corporate breakdowns.",
                "keywords": [
                    "money", "dollar", "finance", "financial", "bank", "invest", "stock", "crypto", "inflation",
                    "debt", "economy", "market", "billionaire", "trade", "wealth", "fed", "federal reserve", "interest rate",
                    "credit", "wall street", "recession", "gdp", "tax", "fund", "venture", "profit", "capital",
                    "trillion", "billion", "currency", "saving", "saver", "price", "bubble", "interest", "fiat"
                ],
                "videos_analyzed": 0,
                "running_medians": {
                    "wpm": 232.0,
                    "avg_cut_interval_sec": 2.2,
                    "hook_cut_interval_sec": 1.1,
                    "words_per_minute_range": [220.0, 245.0],
                    "target_chars_per_shot_min": 16,
                    "target_chars_per_shot_max": 30
                },
                "narrative_framework": {
                    "name": "7-Act Market Trap & Capital Reveal Arc",
                    "structure": [
                        { "act": 1, "name": "The Wallet Trap (Opening Hook)", "pacing": "Rapid-fire (1.0s - 1.4s per cut)", "formula": "Second-person indictment on purchasing power loss, stealth taxes, or invisible financial drainage." },
                        { "act": 2, "name": "Dismantling the Wall Street Myth", "pacing": "Fast (1.8s - 2.2s per cut)", "formula": "Shatter conventional retail investor advice using cold ledger balances and macro-economic data." },
                        { "act": 3, "name": "The Cash Flow Engine (Mechanics)", "pacing": "Dynamic (2.0s - 2.5s per cut)", "formula": "Visual diagrammatic walkthrough of where every dollar flows through the banking/corporate funnel." },
                        { "act": 4, "name": "The Empirical Arbitrage Shift", "pacing": "Moderate (2.2s per cut)", "formula": "Historical balance sheet case study revealing how top 0.1% exploit debt vs income disparity." },
                        { "act": 5, "name": "Psychology of Greed & Panic", "pacing": "Punchy (2.0s per cut)", "formula": "Behavioral economics breakdown of market bubbles, FOMO mania, and panic sell-offs." },
                        { "act": 6, "name": "The Systemic Mismatch (Inflation Illusion)", "pacing": "Intimate (2.0s - 2.4s per cut)", "formula": "Contrast nominal paper wealth gains against real basket-of-goods purchasing decay." },
                        { "act": 7, "name": "The Capital Escape & Modern Irony", "pacing": "Punchy (1.5s - 2.0s per cut)", "formula": "Ending insight on financial sovereignty, concluding with high-impact economic realism." }
                    ]
                },
                "visual_style": {
                    "art_style": "Minimalist hand-drawn 2D vector line art, clean bold black ink comic contours, expressive stick-figure investors and bankers.",
                    "framing": "Full bleed edge-to-edge illustration, grounded financial charts and cityscape environments without white borders.",
                    "color_palette": "Clean contrast black ink, crisp white, emerald dollar green, gold bullion accents, subtle ledger grid texture."
                },
                "reference_blueprints": {}
            },
            "medical": {
                "display_name": "Medical & Biology",
                "description": "Human physiology, clinical mysteries, pathology, neuroscience, cellular biology, and medical breakthroughs.",
                "keywords": [
                    "doctor", "disease", "virus", "brain", "heart", "surgery", "medicine", "patient",
                    "cell", "syndrome", "hospital", "bacteria", "organ", "dna", "cancer", "immune",
                    "diagnosis", "symptom", "blood", "drug", "infection", "vaccine", "neuron", "biology",
                    "amoeba", "pathology", "clinical", "organism", "cellular", "pathogen"
                ],
                "videos_analyzed": 0,
                "running_medians": {
                    "wpm": 218.0,
                    "avg_cut_interval_sec": 2.4,
                    "hook_cut_interval_sec": 1.2,
                    "words_per_minute_range": [210.0, 230.0],
                    "target_chars_per_shot_min": 16,
                    "target_chars_per_shot_max": 32
                },
                "narrative_framework": {
                    "name": "7-Act Clinical Case Study & Cellular Mechanism Arc",
                    "structure": [
                        { "act": 1, "name": "The Subtle Symptom (Opening Hook)", "pacing": "Urgent (1.2s per cut)", "formula": "Seemingly innocuous physical complaint that masks an alarming physiological cascade." },
                        { "act": 2, "name": "Diagnostic Dead-Ends", "pacing": "Deliberate (2.2s per cut)", "formula": "Standard blood panels and scans return normal; clinicians confront an elusive anomaly." },
                        { "act": 3, "name": "Cellular Crime Scene", "pacing": "Dynamic (2.2s - 2.6s per cut)", "formula": "Zoom into microscopic vascular or receptor level revealing molecular saboteurs." },
                        { "act": 4, "name": "The Biological Mechanism Breakthrough", "pacing": "Moderate (2.4s per cut)", "formula": "The exact biochemical pathway discovered under electron microscopy or clinical trial." },
                        { "act": 5, "name": "The Immune Counter-Offensive", "pacing": "Action-oriented (2.0s per cut)", "formula": "How pharmaceutical molecules or bodily antibodies engage the pathology." },
                        { "act": 6, "name": "The Prognosis & Survival Window", "pacing": "High tension (1.8s - 2.2s per cut)", "formula": "The race against organ failure or irreversible tissue decay." },
                        { "act": 7, "name": "The Evolutionary Defense & Modern Lesson", "pacing": "Reflective (2.0s per cut)", "formula": "Why the human body evolved this vulnerability and what it teaches us about survival." }
                    ]
                },
                "visual_style": {
                    "art_style": "Minimalist hand-drawn 2D comic art, anatomical line art cross-sections, stick clinicians and patients.",
                    "framing": "Full bleed 16:9 widescreen, clean clinical white backdrops, floating cellular diagrams.",
                    "color_palette": "Charcoal black line art, surgical teal, arterial red, aseptic white, subtle grid paper texture."
                },
                "reference_blueprints": {}
            },
            "horror": {
                "display_name": "Horror & Mystery",
                "description": "Psychological dread, eerie phenomena, unsolved disappearances, dark lore, and true crime enigmas.",
                "keywords": [
                    "horror", "creepy", "ghost", "dark", "nightmare", "mystery", "forest", "monster",
                    "cabin", "haunted", "unsolved", "disappeared", "fear", "death", "abandoned",
                    "cursed", "shadow", "woods", "killer", "whisper", "scream", "stalker",
                    "camper", "vanished", "eerie", "night", "woods"
                ],
                "videos_analyzed": 0,
                "running_medians": {
                    "wpm": 198.0,
                    "avg_cut_interval_sec": 3.0,
                    "hook_cut_interval_sec": 1.4,
                    "words_per_minute_range": [190.0, 210.0],
                    "target_chars_per_shot_min": 14,
                    "target_chars_per_shot_max": 28
                },
                "narrative_framework": {
                    "name": "7-Act Atmospheric Suspense & Dread Escalation Arc",
                    "structure": [
                        { "act": 1, "name": "The Disturbance (Opening Hook)", "pacing": "Ominous (1.2s - 1.5s per cut)", "formula": "A routine evening or familiar setting fractured by an uncanny, unexplainable detail." },
                        { "act": 2, "name": "Rational Explanations Collapse", "pacing": "Creeping (2.6s per cut)", "formula": "Every logical deduction is forensically ruled out." },
                        { "act": 3, "name": "Isolation & Looming Dread", "pacing": "Claustrophobic (3.0s per cut)", "formula": "Communication lines severed, geographical distance, darkness engulfing the environment." },
                        { "act": 4, "name": "The First Encounter", "pacing": "Shock cut (1.2s bursts)", "formula": "Fleeting glimpse of the unnatural entity in the peripheral line art." },
                        { "act": 5, "name": "The Archive of Prior Victims", "pacing": "Investigative (2.5s per cut)", "formula": "Discovering historical records proving this happened before." },
                        { "act": 6, "name": "The Tipping Point of Survival", "pacing": "Frantic (1.8s - 2.2s per cut)", "formula": "A desperate physical struggle or flight through pitch-black terrain." },
                        { "act": 7, "name": "The Lingering Void", "pacing": "Haunting (2.8s - 3.5s per cut)", "formula": "The mystery remains open, leaving a cold lingering chill." }
                    ]
                },
                "visual_style": {
                    "art_style": "High-contrast minimalist 2D line art, heavy black shadows, trembling ink contours, terrified stick figures.",
                    "framing": "Full bleed 16:9 widescreen, pitch black void, flickering flashlight cones, mist and silhouette trees.",
                    "color_palette": "Deep void black, blood crimson accent, ghostly pale yellow, cold moonlight grey."
                },
                "reference_blueprints": {}
            },
            "engineering": {
                "display_name": "Engineering & Technology",
                "description": "Mega-projects, physics puzzles, industrial disasters, aerospace triumphs, computing, and machines.",
                "keywords": [
                    "engine", "rocket", "bridge", "machine", "physics", "robot", "concrete", "steel",
                    "turbine", "reactor", "computer", "architecture", "megaproject", "disaster",
                    "tunnel", "space", "pressure", "thrust", "aerodynamics", "failure", "invention",
                    "dam", "hoover dam", "structural", "construction", "mechanics"
                ],
                "videos_analyzed": 0,
                "running_medians": {
                    "wpm": 222.0,
                    "avg_cut_interval_sec": 2.3,
                    "hook_cut_interval_sec": 1.2,
                    "words_per_minute_range": [215.0, 235.0],
                    "target_chars_per_shot_min": 16,
                    "target_chars_per_shot_max": 32
                },
                "narrative_framework": {
                    "name": "7-Act Engineering Dilemma & Physics Tipping-Point Arc",
                    "structure": [
                        { "act": 1, "name": "The Impossible Spec (Opening Hook)", "pacing": "Direct (1.2s per cut)", "formula": "Audacious engineering goal confronting an unyielding law of physics or thermodynamics." },
                        { "act": 2, "name": "The Fatal Flaw in Standard Design", "pacing": "Analytical (2.2s per cut)", "formula": "Why conventional materials or geometry collapse under simulated stress." },
                        { "act": 3, "name": "The Radical Prototype", "pacing": "Dynamic (2.2s - 2.5s per cut)", "formula": "Breakdown of the unconventional mechanical innovation that defies intuition." },
                        { "act": 4, "name": "The Stress Test & Trial by Fire", "pacing": "High tension (1.8s - 2.2s per cut)", "formula": "Live telemetry under extreme thermal or pressure limits." },
                        { "act": 5, "name": "The Microscopic Failure Vector", "pacing": "Precision forensic (2.4s per cut)", "formula": "How a single loose rivet or micro-fracture jeopardizes the entire machine." },
                        { "act": 6, "name": "The Redesign Triumph", "pacing": "Fast & rhythmic (2.0s per cut)", "formula": "Clever mechanical elegance solving the dilemma permanently." },
                        { "act": 7, "name": "The New Frontier & Engineering Legacy", "pacing": "Inspiring (2.0s per cut)", "formula": "How this solution unlocked modern skyscrapers, rocketry, or microchips." }
                    ]
                },
                "visual_style": {
                    "art_style": "Minimalist isometric line art schematics, technical blueprint cross-sections, stick engineers with hard hats.",
                    "framing": "Full bleed 16:9 widescreen, technical drafting grid backdrop, clean dimension lines.",
                    "color_palette": "Blueprint cyan line art, technical drafting white, hazard safety orange, steel grey."
                },
                "reference_blueprints": {}
            }
        }
    }

    with open(CODEX_PATH, "w", encoding="utf-8") as f:
        json.dump(v2_codex, f, indent=2)

    print(f"Successfully migrated codex to v2.0.0 with {len(v2_codex['niches'])} niches.")
    print(f"Preserved {len(old_blueprints)} reference blueprints in 'history' niche.")

if __name__ == "__main__":
    migrate()
