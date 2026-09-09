# Pipeline Codebase & Utility Scripts

This folder archives all Python scripts developed for reverse-engineering the reference video, processing media stems, and building the 334-shot production database.

---

## Script Index & Purposes

### 1. Scene & Timing Calibration
- **`calibrate_350_shots.py`**: Calculates character density and shot boundaries to hit the target 330–400 shots under the $1,000\text{ chars} = 60\text{s}$ constraint.
- **`trim_and_build_350.py`**: Trims and breaks down script lines into micro-beats averaging 38 characters (~2.3s).
- **`word_timing.py`**: Computes word-level and sentence-level durations.

### 2. Prompt Engineering & Image Formatting
- **`apply_full_bleed_prompts.py`**: Injects full-bleed edge-to-edge prompt directives across all 334 rows, eliminating conflicting white/cream background tags.
- **`apply_perfect_backgrounds.py`**: Generates grounded environmental context for every indoor, outdoor, scientific, and transitional scene.
- **`update_all_backgrounds.py`**: Batch-updates storyboard tables with specific background cues.

### 3. Storyboard Compilers
- **`build_all_acts.py`**: Compiles raw act data into unified shots.
- **`data_part1.py`, `data_part2.py`, `data_part3.py`**: Shot definition chunks for Acts 1 through 7.
- **`finish_builder.py`**: Merges shot segments and outputs `storyboard_master.csv` and `storyboard_master.md`.
- **`generate_350_shots_master.py`**: Core assembly script for the 334-shot database.

### 4. Forensic Audio & Video Analysis
- **`deep_analysis.py`**: Runs PySceneDetect / FFmpeg scene cut detection on the source video.
- **`analyze_wav.py` & `probe_audio.py`**: Measures LUFS integrated loudness, dynamic range (LRA), and true peak levels.
- **`pitch_check.py`**: Analyzes voice fundamental frequency ($F_0$) to identify narrator pitch and vocal tone.
- **`extract_clips.py` & `extract_sub.py`**: Extracts audio stems and subtitle tracks from the reference video.

