# Ink Explainer — Video Storyboard Generation & AI Curation Engine

An automated production pipeline, computer vision scoring framework, and continuous learning studio for generating full-length explainer video storyboards with Google Flow.

Designed for the 334-shot explainer: **"What Did Ancient Humans Actually Do All Day?"** (12:52 runtime) in clean minimalist black ink comic line art style.

---

## Architecture Overview

```
Ink-Explainer/
├── 1- Postmartum/                       # Analysis of reference video & structure
│   ├── clean_transcript.txt            # Word-timed master transcript
│   ├── cuts_data.json                  # Pacing & scene breakdown
│   ├── transcript.en-orig.vtt          # Timecoded subtitle track
│   └── README_POSTMORTEM_REPORT.md     # Full narrative analysis & cadence
├── 2- Code/                            # Production automation & curation studio
│   ├── run_full_production_pipeline.py # End-to-end Google Flow Playwright runner
│   ├── run_qa_dashboard.py             # Lightweight HTTP curation server (Port 8507)
│   ├── storyboard_qa_dashboard.html    # Standalone continuous-scroll curation UI
│   ├── run_regeneration_queue.py       # Automated re-generation queue processor
│   ├── update_prompt_status_tracker.py # Real-time Markdown status generator
│   └── ...                             # Prompt builders, parsers & test harnesses
├── 3- Finals/                          # Master script, prompt dataset & logs
│   ├── storyboard_master.csv           # 334-shot prompts with exact timecodes & visual actions
│   ├── selection_log.csv               # Selection history with OpenCV quality scores
│   ├── ai_learning_log.json            # AI differential reflections & user feedback
│   ├── regeneration_queue.json         # Queue for shots requiring re-generation
│   └── production_status.json          # Production state tracker
├── SOP.md                              # Standard Operating Procedures & failsafe cascade rules
├── PROMPT_STATUS.md                    # Live generation progress tracker (334/334 completed)
└── README.md                           # Project documentation
```

---

## Key Capabilities

### 1. Automated Google Flow Automation (`run_full_production_pipeline.py`)
- **Failsafe Model Cascade**: Automatically cascades across `Nano Banana Pro` -> `Nano Banana 2` -> `Nano Banana 2 Lite` upon persistent generation failures or timeouts.
- **Dynamic Pacing & Cooldown**: Implements 10–30s randomized pacing intervals between generations to preserve browser and session stability.
- **Partial Variation Fallback**: When Flow generates 1 of 2 requested variations, computer vision automatically assesses viability and preserves usable frames without stalling.
- **OpenCV Quality Scoring**: Calculates edge sharpness (Laplacian variance), subject prominence (center vs. periphery contrast), dynamic range, and information entropy, penalizing framing artifacts.

### 2. Storyboard Visual Curation & AI Learning Studio (`run_qa_dashboard.py`)
- **Above-and-Below Architecture**: Full-width header and voiceover strip above; dual 16:9 widescreen variations side-by-side in the center; AI differential reflections and open-ended feedback below.
- **Continuous Rapid-Skim Feed**: Continuous vertical scroll through all 334 shots with real-time search and filter tabs (`All Shots`, `Ready / Completed`, `Your Overrides`, `Re-gen Queued`, `Pending`).
- **Active AI Learning**: Records user overrides, differential OpenCV analysis, and open-ended user feedback ("Why did you choose this image?") directly into `ai_learning_log.json`.
- **1-Click Quick Tags**: Rapid feedback tagging (`+ Emotion / Face`, `+ Story Fidelity`, `+ Cleaner / Simpler`, `+ Action Framing`, `+ Bolder Ink`).
- **Non-Destructive Live Sync**: In-place DOM updates prevent scroll jumps or loss of typed inputs during background polling.

### 3. Automated Re-generation Queue Runner (`run_regeneration_queue.py`)
- Any shot marked with `Neither Works (Re-generate)` on the dashboard is queued with custom critique.
- The queue runner connects to the active Flow session, applies refined prompts with user directions, generates fresh variations, and updates the finals catalog.

---

## Quick Start

### Prerequisites
- Python 3.10+
- Chrome running with remote debugging enabled (`--remote-debugging-port=9222`)
- Dependencies:
  ```bash
  pip install playwright opencv-python numpy
  playwright install chromium
  ```

### Running the Visual Curation Studio
Launch the curation dashboard on **Port 8507**:
```bash
python "2- Code/run_qa_dashboard.py"
```
Open [http://localhost:8507](http://localhost:8507) in your browser.

### Running the Production Pipeline
```bash
python "2- Code/run_full_production_pipeline.py" --start 1 --end 334
```

### Processing Re-generation Requests
```bash
python "2- Code/run_regeneration_queue.py"
```

---

## Master Script Details
- **Total Shots**: 334
- **Runtime**: 12:52.0
- **Visual Style**: Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art, graphic novel aesthetic, cinematic 16:9 widescreen composition.
- **Status**: 334 / 334 (100%) generated, verified, and logged.
