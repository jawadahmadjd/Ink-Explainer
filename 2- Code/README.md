# Autonomous Ink Explainer Production Architecture (`2- Code/`)

This directory contains the complete source code, stage modules, web interface, and tools for the **Autonomous Ink Explainer Video Production Pipeline** (Stages 1 through 6).

---

## 1. Directory Structure

```
2- Code/
├── pipeline_orchestrator.py      # Master CLI runner orchestrating all stages
├── web_ui.py                     # Flask web server powering the interactive Web UI
├── config.py                     # Central configuration, .env loader, model cascades, silence rules
├── learning/                     # Distilled AI Learning Engine (Zero Bloat Codex)
│   ├── ai_learning_codex.json    # Statistical medians (224.6 WPM, 2.5s cuts), 7-act retention formulas, reference blueprints
│   └── learning_engine.py        # Pacing divider engine (16-32 chars), fuzzy title matcher, prompt context builder
├── templates/
│   └── index.html                # Single-page modern responsive UI with dual-mode switch & image review gate
├── modules/
│   ├── __init__.py
│   ├── stage1_postmortem.py      # Stage 1: Ingestion, yt-dlp download, ffmpeg cuts, audio LUFS & auto-codex training
│   ├── stage2_script_prompts.py  # Stage 2: Script formatting, reference matching & 16-32 char stick-figure prompt compiler
│   ├── stage3_voiceover.py       # Stage 3: ElevenLabs combined VO production & silence normalization
│   ├── stage4_image_gen.py       # Stage 4: Google Flow CDP runner, model cascade, CV evaluator
│   ├── stage5_timeline_xml.py    # Stage 5: Apple xmeml v4 XML sequence timeline generator
│   └── stage6_reporter.py        # Stage 6: Execution telemetry, timestamps, and work report generator
├── archive/                      # Historical exploratory & test scripts (git-ignored)
└── README.md                     # This documentation file
```

---

## 2. Stage Modules & Workflow

### Distilled AI Learning Engine (`learning/learning_engine.py`)
- **Zero Context Bloating**: Maintains running mathematical medians and modular narrative blueprints rather than dumping raw transcripts into LLM context (~1,500 token budget).
- **Reference Title Matching**: Automatically detects if an input video title matches an existing analyzed project in `1- Postmartum/` (using combined token containment and fuzzy string similarity). When matched, mirrors the original video's ideation thesis, opening hook formula, and 7-act progression arc.
- **Fast-Paced Image Pacing Standard**:
  - Enforces an average cadence of **1 image cut every 16 to 32 characters** based on natural word boundaries.
  - **Mandatory Punctuation Dividers**: Every comma (`,`), period (`.`), semicolon (`;`), question mark (`?`), exclamation point (`!`), colon (`:`), and dash (`—`) acts as a hard divider that creates a new shot beat immediately, **no matter how short that word or clause is** (e.g. *"Why?"* is 4 characters, but receives its own isolated shot beat and image).

### Stage 1: Ingestion & Forensic Postmortem (`modules/stage1_postmortem.py`)
- **Purpose**: Ingests any reference YouTube video URL and extracts complete forensic data.
- **Tools**: `yt-dlp`, `ffmpeg`, `ffprobe`.
- **Output**: Saved to `1- Postmartum/{N}- {Video Title}/`:
  - `video_low.mp4`: Lightweight local reference video.
  - `video_info.json`: Video metadata, tags, and chapter markers.
  - `transcript.en-orig.vtt`: Timecoded subtitle cues.
  - `clean_transcript.txt`: Deduplicated continuous spoken text.
  - `cuts_data.json`: Visual shot cut timestamps detected via FFmpeg scene filter.
  - `README_POSTMORTEM_REPORT.md`: Comprehensive forensic report (WPM, scene cuts, loudness LUFS, LRA, True Peak).

### Stage 2: Script & Stick-Figure Storyboard Prompts (`modules/stage2_script_prompts.py`)
- **Purpose**: Formats the narration script and compiles 16:9 full-bleed comic prompts enforcing strict stick-figure character rules.
- **Character Standard**:
  - Minimalist white-filled black-outlined stick figures (MinutePhysics / Casually Explained style).
  - Simple circular heads with pure solid white fill and bold black comic contours.
  - Simple black stick limbs (0 flesh tones, 0 realistic human anatomy).
  - 100% full-bleed edge-to-edge environment grounding (zero matted margins or white borders).
- **Output**: Saved to `3- Finals/{N}- {Video Title}/`:
  - `clean_ai_voiceover_script.txt`: Complete narration text.
  - `storyboard_master.csv`: 5-column database (Shot, Timecode, Voiceover, Description, Prompt).
  - `all_prompts.txt`: Prompt book with live `[STATUS: COMPLETED]` / `[STATUS: PENDING]` tags.
  - `character_audit.json`: 334-shot character compliance audit database.
  - `PROMPT_STATUS.md`: Real-time visual progress tracker.

### Stage 3: ElevenLabs Combined Voiceover & Silence Normalization (`modules/stage3_voiceover.py`)
- **Purpose**: Generates high-fidelity narration via ElevenLabs and applies sample-accurate silence normalization.
- **Generation Mode**: **ALWAYS COMBINED** (never sentence-by-sentence) using `/v1/text-to-speech/{voice_id}/with-timestamps` to preserve natural human breath and cadence.
- **Active Voice**: Configured in `.env` (default: Tyler, Voice ID `q0IMILNRPxOgtBTS4taI`, Model `eleven_multilingual_v2`).
- **SOP Silence Normalization Engine**:
  - Scans all pauses between sentences.
  - If silence $> 300	ext{ms}$: crops excess silence, preserving **150ms tail cushion after current sentence** and **150ms head cushion before next sentence** (300ms total natural pause).
  - Splices audio at nearest zero-crossing samples.
  - Recalibrates downstream timestamps sample-accurately.
- **Output**: Saved to `3- Finals/{N}- {Video Title}/Voiceovers/`:
  - `voiceover_master_normalized.mp3` & `voiceover_master_normalized.wav`
  - `words_alignment.json`: Millisecond timestamps for every spoken word.
  - `shots_timing_alignment.json`: Exact millisecond start/end cues for each shot.

### Stage 4: Google Flow Autonomous Image Generation (`modules/stage4_image_gen.py`)
- **Purpose**: Automates image generation and curation on Google Flow via Chrome DevTools CDP.
- **Chrome CDP Binding**: Connects via port 9222 (checking IPv6 `[::1]:9222` and IPv4 `127.0.0.1:9222`).
- **Model Cascade**: Priority cascade: `Nano Banana Pro > Nano Banana 2 > Nano Banana 2 Lite`.
- **Instant Limit Bypass**: Detects usage limit / quota warning banners and shifts immediately to the next model in the cascade without stalling.
- **Multi-Metric Computer Vision Scoring**: Evaluates sharpness (Laplacian variance), contrast, dynamic range, stick-figure validation (-40 penalty for non-stick faces/flesh tones), and border penalty (-50 for white card borders).
- **Canonical Storage**: Winning variations are copied strictly to `Final selected images/` (`3- Finals/{N}- {Video Title}/Final selected images/`).

### Stage 5: Apple xmeml Sequence XML Assembly (`modules/stage5_timeline_xml.py`)
- **Purpose**: Assembles a non-linear editor sequence XML for Premiere Pro, Final Cut Pro, or DaVinci Resolve.
- **Format**: Apple `xmeml` v4 XML @ 24 fps.
- **Audio Track 1**: Master normalized voiceover audio from frame 0 to end.
- **Video Track 1**: All storyboard images mapped to their exact voiceover sentence timestamps with zero black gaps.
- **Output**: Saved to `3- Finals/{N}- {Video Title}/storyboard_timeline.xml`.

### Stage 6: Telemetry & Execution Reporting (`modules/stage6_reporter.py`)
- **Purpose**: Tracks pipeline execution milestones, start/end timestamps, elapsed stage durations, and error alerts.
- **Output**: Prints a formatted summary table to the console and generates `3- Finals/{N}- {Video Title}/EXECUTION_REPORT.md`.

---

## 3. Master Runners & Web Interface

### A. CLI Master Orchestrator (`pipeline_orchestrator.py`)
Run the entire pipeline or specific stages from the command line:
```bash
# Run full pipeline for a new YouTube video:
python "2- Code/pipeline_orchestrator.py" --url "https://www.youtube.com/watch?v=..." --mode auto

# Run specific stages on an existing project:
python "2- Code/pipeline_orchestrator.py" --title "1- What Did Ancient Humans Actually Do All Day" --stage 3,5

# Regenerate specific shots in Google Flow:
python "2- Code/pipeline_orchestrator.py" --title "1- What Did Ancient Humans Actually Do All Day" --stage 4 --shots 127,129,131 --model "Nano Banana 2"
```

### B. Interactive Web UI (`web_ui.py`)
Launch the browser-based dashboard:
```bash
python "2- Code/web_ui.py"
# or double-click launch_ui.bat in the project root
```
Access at `http://localhost:5000`:
- **Clean Canvas by Default**: Starts completely fresh with zero images preloaded.
- **Project Selector**: Choose any existing project folder to inspect its assets or execute standalone stages.
- **Ascending Numbering**: Pasting a new URL automatically assigns the next sequential prefix (`1- ...`, `2- ...`, `3- ...`).
- **Interactive Image Selection Gate**: Review shots, compare generated variations, swap images with one click, and approve before assembling the Apple XML sequence.
- **Step-by-Step Pause Mode**: Option to pause after each stage for manual review.

---

## 4. Configuration (`config.py`)
Global parameters, directories, and thresholds:
- `MAX_SILENCE_MS = 300`: Silence threshold for trimming.
- `SILENCE_TAIL_CUSHION_MS = 150` & `SILENCE_HEAD_CUSHION_MS = 150`: Padding around cuts.
- `MODEL_CASCADE = ["Nano Banana Pro", "Nano Banana 2", "Nano Banana 2 Lite"]`
- `TARGET_VARIATIONS = 2`
- `ASPECT_RATIO = "16:9"` (1376 × 768 native render)
- Sourced from `.env` (`ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`, `ELEVENLABS_MODEL_ID`).\n