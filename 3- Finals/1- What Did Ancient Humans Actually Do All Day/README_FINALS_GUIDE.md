# Final Production Deliverables Guide

This directory contains all finalized production assets:

## 1. Master Files Overview

| File | Format | Description | Primary Use Case |
| :--- | :--- | :--- | :--- |
| **ll_prompts.txt** | Text Book (181 KB) | All 334 prompts formatted shot-by-shot with Shot #, Timecodes, Spoken VO lines, Visual descriptions, and full prompt. | The ultimate master prompting guidebook for generation. |
| **ll_prompts_raw.txt** | Raw Text (126 KB) | Exactly 334 prompts, one per line with zero extra headers or dialogue text. | Bulk automation, API generation scripts, or fast copy-pasting. |
| **storyboard_master.csv** | CSV Spreadsheet (167 KB) | Complete production database with 5 columns: Shot #, Time, Spoken VO script, Visual description, Exact Prompt. | Spreadsheet tracking, video editing timeline marker import. |
| **storyboard_master.md** | Markdown Table (171 KB) | Full Markdown table version of the 334-shot storyboard. | Visual reference and project documentation. |
| **clean_ai_voiceover_script.txt** | Plain Text (13 KB) | Uninterrupted spoken script with stage directions and shot numbers removed. | Direct copy-paste into AI TTS (ElevenLabs, OpenAI Voice). |
| **clean_script.txt** | Plain Text (14 KB) | Full script with original act headers and narrative demarcation. | Script reading and editorial review. |

---

## 2. Pacing & Timecode Calibration
- **Formula**: 1,000 characters = 60 seconds (1 second = 16.667 characters).
- **Total Duration**: ~12 minutes 52 seconds (772 seconds).
- **Shot Density**: 334 discrete shots (averaging ~2.3 seconds per cut).

---

## 3. Voiceover Generation Recommendations
- **Recommended Voice Profile**: Warm, intellectual, contemplative baritone (fundamental frequency ~120 Hz - 130 Hz).
- **Recommended Voice IDs (ElevenLabs)**: Marcus, Adam, or custom baritone narrator.
- **Pacing**: ~220-225 WPM.
- **Loudness**: -14 to -12 LUFS, True Peak: -1.0 dBFS.
