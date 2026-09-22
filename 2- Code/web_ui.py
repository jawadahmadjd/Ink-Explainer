"""
Interactive Autonomous Pipeline Web UI
Provides a web application to:
1. Input video link and trigger the pipeline step-by-step with ascending project numbering (N- Title).
2. Per-stage pause and standalone execution controls.
3. Interactive visual image gallery and selection gate before XML generation.
4. Clean canvas startup without pre-loaded images.
"""

import os
import sys
import json
import csv
import re
import shutil
import threading
import time
import subprocess
import urllib.request
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, Response

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

import config
from modules.stage1_postmortem import run_stage1_postmortem
from modules.stage2_script_prompts import run_stage2_script_prompts
from modules.stage3_voiceover import (
    run_stage3_voiceover,
    validate_elevenlabs_api_key,
    resume_elevenlabs_key_wait,
    cancel_elevenlabs_key_wait,
    get_stage3_progress
)
from modules.stage4_image_gen import (
    run_stage4_image_gen,
    safe_copy_file,
    pause_stage4,
    resume_stage4,
    cancel_stage4,
    download_flow_image_2k,
    is_stage4_paused,
    is_stage4_running,
    get_missing_shots
)
from modules.image_resolution import (
    get_image_dimensions,
    ensure_2k_image,
    pull_single_shot_2k_from_flow,
    build_project_2k_zip
)
from modules.stage5_timeline_xml import run_stage5_timeline_xml
from modules.stage6_reporter import PipelineReporter
from modules.srt_alignment import parse_srt, align_storyboard_with_srt
from learning.learning_engine import (
    load_codex,
    find_matching_reference_video,
    ingest_postmortem_to_codex,
    classify_script_niche,
    create_dynamic_niche
)
from modules.antigravity_bridge import (
    dispatch_task,
    get_active_task,
    load_active_task_context,
    apply_antigravity_script_and_storyboard,
    cancel_active_task,
    complete_task,
    wait_for_task_completion,
    synthesize_storyboard_from_script
)

app = Flask(__name__, template_folder=os.path.join(CODE_DIR, "templates"))
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Global pipeline state
STATE = {
    "state": "IDLE",
    "project_title": "",
    "task_description": "Clean canvas ready. Select a project or paste a URL to begin.",
    "pause_after_each_stage": False,
    "pause_requested": False,
    "step1": "WAITING",
    "step2": "WAITING",
    "step3": "WAITING",
    "step4": "WAITING",
    "step5": "WAITING",
    "step6": "WAITING",
    "logs": [
        f"[{datetime.now().strftime('%H:%M:%S')}] Ink Explainer Studio initialized.",
        f"[{datetime.now().strftime('%H:%M:%S')}] Clean canvas ready. Paste a video link or select an existing project."
    ],
    "stage4_progress": {
        "is_active": False,
        "shot_num": None,
        "index_in_run": 0,
        "total_in_run": 0,
        "completed_in_run": 0,
        "total_project_shots": 0,
        "completed_project_shots": 0,
        "run_percent": 0.0,
        "phase": "IDLE",
        "phase_text": "Ready",
        "model": "Nano Banana Pro",
        "resolution": "2K",
        "best_score": None,
        "last_approved_shot": None,
        "pacing_sec": 0.0
    }
}

def make_stage4_progress_callback(worker_type: str = "Range"):
    def on_progress(payload: dict):
        with LOG_LOCK:
            STATE["stage4_progress"] = payload
            phase = payload.get("phase", "")
            phase_text = payload.get("phase_text", "")
            shot_num = payload.get("shot_num")

            if phase in ("APPROVED", "COMPLETE", "HALTED", "CANCELLED"):
                add_log(f"[STAGE 4] {phase_text}")

            STATE["current_action"] = phase_text
            if phase == "APPROVED":
                last_shot = payload.get("last_approved_shot") or {}
                s_num = last_shot.get("shot_num") or shot_num
                score = last_shot.get("score")
                STATE["task_description"] = f"Approved Shot #{s_num:03d} (Score: {score}). {payload.get('completed_in_run')}/{payload.get('total_in_run')} complete."
            elif phase not in ("COMPLETE", "START"):
                STATE["task_description"] = phase_text
    return on_progress

LOG_LOCK = threading.Lock()
PAUSE_EVENT = threading.Event()
PAUSE_EVENT.set()  # set means running; cleared means paused
STOP_EVENT = threading.Event()

ELEVENLABS_POOL_CACHE = {
    "keys": [],
    "last_check": 0,
    "active_key": "",
    "pool_summary": {"total_keys": 0, "active_keys": 0, "total_remaining_chars": 0, "keys_detail": []}
}
_pool_lock = threading.Lock()
_pool_worker_running = False
REGEN_CACHE = {}

def check_chrome_flow_cdp_status() -> dict:
    """Check if Chrome DevTools CDP is listening on port 9222 and if flow.google.com is open."""
    for ep in config.CDP_ENDPOINTS:
        try:
            req = urllib.request.urlopen(f"{ep}/json", timeout=0.8)
            if req.status == 200:
                data = json.loads(req.read().decode("utf-8"))
                flow_tabs = [t for t in data if "flow.google.com" in t.get("url", "")]
                if flow_tabs:
                    return {
                        "connected": True,
                        "cdp_url": ep,
                        "flow_url": flow_tabs[0].get("url", ""),
                        "title": flow_tabs[0].get("title", ""),
                        "status_text": f"Connected to Google Flow via Chrome CDP ({ep})"
                    }
                else:
                    return {
                        "connected": True,
                        "cdp_url": ep,
                        "flow_url": "",
                        "title": "",
                        "status_text": "Chrome CDP Active (Port 9222) - Open flow.google.com in Chrome"
                    }
        except Exception:
            continue
    return {
        "connected": False,
        "cdp_url": "",
        "flow_url": "",
        "title": "",
        "status_text": "Chrome CDP Not Connected (Port 9222)"
    }

def _refresh_pool_worker(force: bool = False):
    """Background worker to check ElevenLabs key balances without blocking the UI."""
    global _pool_worker_running
    with _pool_lock:
        if _pool_worker_running:
            return
        now = time.time()
        if not force and (now - ELEVENLABS_POOL_CACHE["last_check"] < 60) and ELEVENLABS_POOL_CACHE["pool_summary"]["total_keys"] > 0:
            return
        _pool_worker_running = True

    def _do_work():
        global _pool_worker_running
        try:
            keys = config.get_elevenlabs_api_keys(force_reload=True)
            details = []
            total_remaining = 0
            active_count = 0
            for idx, k in enumerate(keys):
                info = validate_elevenlabs_api_key(k)
                is_valid = info.get("valid", False)
                rem = info.get("remaining_characters", 0)
                if is_valid:
                    active_count += 1
                    total_remaining += rem
                details.append({
                    "index": idx + 1,
                    "masked_key": f"{k[:4]}...{k[-4:]}" if len(k) > 8 else "****",
                    "valid": is_valid,
                    "remaining_characters": rem,
                    "character_limit": info.get("character_limit", 0),
                    "character_count": info.get("character_count", 0),
                    "tier": info.get("tier", "unknown"),
                    "status": info.get("status", "unknown"),
                    "error": info.get("error", "")
                })
            with _pool_lock:
                ELEVENLABS_POOL_CACHE["keys"] = keys
                ELEVENLABS_POOL_CACHE["last_check"] = time.time()
                ELEVENLABS_POOL_CACHE["pool_summary"] = {
                    "total_keys": len(keys),
                    "active_keys": active_count,
                    "total_remaining_chars": total_remaining,
                    "keys_detail": details
                }
        finally:
            with _pool_lock:
                _pool_worker_running = False

    t = threading.Thread(target=_do_work, daemon=True)
    t.start()

def get_cached_pool_summary(force: bool = False) -> dict:
    _refresh_pool_worker(force=force)
    with _pool_lock:
        return dict(ELEVENLABS_POOL_CACHE["pool_summary"])

def add_log(msg: str):
    with LOG_LOCK:
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}"
        STATE["logs"].append(entry)
        if len(STATE["logs"]) > 200:
            STATE["logs"].pop(0)
        print(entry)

def run_pipeline_worker(url: str, custom_title: str, model: str, pause_mode: bool, prompt: str = "", niche: str = ""):
    """Background worker executing the pipeline step by step with ascending folder numbering and niche awareness."""
    global STATE
    STATE["pause_after_each_stage"] = pause_mode

    # Resolve raw title
    if not custom_title and url:
        add_log("Fetching video metadata to determine ascending project folder...")
        try:
            res = subprocess.run(["yt-dlp", "--dump-json", "--no-warnings", url], capture_output=True, text=True, check=True)
            info = json.loads(res.stdout)
            raw_title = info.get("title", "Ink Explainer Video")
        except Exception as e:
            raw_title = "Ink Explainer Video"
    elif custom_title:
        raw_title = custom_title
    else:
        raw_title = "Ink Explainer Video"

    # Resolve niche if auto or empty
    if not niche or niche == "auto":
        clf = classify_script_niche(raw_title, prompt)
        niche = clf.get("niche", "history")
        add_log(f"Auto-classified niche: '{clf.get('display_name', niche.title())}' (Confidence: {int(clf.get('score', 0)*100)}%)")
    else:
        add_log(f"Selected niche: '{niche}'")

    project_folder = config.get_next_project_folder_name(raw_title, niche=niche)
    STATE["project_title"] = project_folder
    add_log(f"Assigned project folder in '{niche}': '{project_folder}'")

    try:
        # Step 1: Ingestion
        if url:
            STATE["state"] = "RUNNING_POSTMORTEM"
            STATE["step1"] = "RUNNING"
            STATE["task_description"] = f"Stage 1: Ingestion & Forensic Postmortem into '{project_folder}' (Niche: {niche})..."
            add_log(f"Starting Stage 1 for URL: {url} (Niche: {niche})")
            run_stage1_postmortem(url, custom_title=project_folder, niche=niche)
            STATE["step1"] = "COMPLETED"
            add_log(f"Stage 1 Ingestion & Postmortem completed (Trained '{niche}' niche).")

            if STATE["pause_after_each_stage"]:
                STATE["state"] = "PAUSED_AFTER_STAGE_1"
                STATE["task_description"] = "Stage 1 Complete. Paused for review. Click 'Continue' to advance to Stage 2."
                add_log("PAUSED: Stage 1 complete. Awaiting user continue...")
                PAUSE_EVENT.clear()
                PAUSE_EVENT.wait()
        else:
            STATE["step1"] = "SKIPPED (Manual Prompt Mode)"
            add_log("Mode B: Manual Title & Prompt Mode. Stage 1 Ingestion bypassed.")

        # Step 2: Script & Prompts (Handled by Antigravity)
        dirs = config.get_project_dirs(project_folder)
        has_existing_script = os.path.exists(dirs["master_csv"])
        has_transcript = os.path.exists(os.path.join(dirs["postmortem_dir"], "clean_transcript.txt"))

        if not has_existing_script:
            STATE["state"] = "AWAITING_ANTIGRAVITY_SCRIPT"
            STATE["step2"] = "AWAITING_ANTIGRAVITY"
            task_mode = "Repurposing Ingested Script" if has_transcript else "Creating Script From Topic"
            STATE["task_description"] = f"Awaiting Antigravity AI Engine ({task_mode}) for '{project_folder}' (Niche: {niche})..."
            add_log(f"Stage 2: Dispatched task to Antigravity AI Engine ({task_mode}) for '{project_folder}'. Waiting for Antigravity...")
        else:
            STATE["state"] = "RUNNING_SCRIPT"
            STATE["step2"] = "RUNNING"
            STATE["task_description"] = f"Stage 2: Syncing Script & Stick-Figure Prompts for '{project_folder}'..."
            add_log(f"Syncing existing script and prompts for '{project_folder}'...")

        run_stage2_script_prompts(project_folder, user_prompt=prompt, niche=niche)
        STATE["step2"] = "COMPLETED"
        add_log("Stage 2 Script & Storyboard Prompts ready.")

        if STATE["pause_after_each_stage"]:
            STATE["state"] = "PAUSED_AFTER_STAGE_2"
            STATE["task_description"] = "Stage 2 Complete. Paused for review. Click 'Continue' to advance to Stage 3."
            add_log("PAUSED: Stage 2 complete. Awaiting user continue...")
            PAUSE_EVENT.clear()
            PAUSE_EVENT.wait()

        # Step 3: Voiceover
        STATE["state"] = "RUNNING_VOICEOVER"
        STATE["step3"] = "RUNNING"
        STATE["task_description"] = "Stage 3: ElevenLabs Combined VO & Silence Normalization..."
        add_log("Generating ElevenLabs combined VO and normalizing silence (>300ms trimmed)...")
        run_stage3_voiceover(project_folder)
        STATE["step3"] = "COMPLETED"
        add_log("Stage 3 Voiceover master audio and millisecond alignments created.")

        if STATE["pause_after_each_stage"]:
            STATE["state"] = "PAUSED_AFTER_STAGE_3"
            STATE["task_description"] = "Stage 3 Complete. Paused for review. Click 'Continue' to advance to Stage 4."
            add_log("PAUSED: Stage 3 complete. Awaiting user continue...")
            PAUSE_EVENT.clear()
            PAUSE_EVENT.wait()

        # Step 4: Images
        STATE["state"] = "RUNNING_IMAGES"
        STATE["step4"] = "RUNNING"
        STATE["task_description"] = "Stage 4: Google Flow Autonomous Image Generation..."
        add_log(f"Starting Google Flow image generation with model {model}...")
        run_stage4_image_gen(project_folder, model=model)
        STATE["step4"] = "COMPLETED"
        add_log("Stage 4 Image generation complete.")

        # Step 5: PAUSE FOR IMAGE SELECTION GATE!
        STATE["state"] = "AWAITING_IMAGE_SELECTION"
        STATE["step5"] = "WAITING"
        STATE["task_description"] = "Image Selection Gate: Review shots in gallery below and click 'Approve & Build XML'."
        add_log("Pipeline reached Image Selection Gate. Review shots and approve!")

    except Exception as ex:
        STATE["state"] = "ERROR"
        STATE["task_description"] = f"Pipeline Error: {ex}"
        add_log(f"ERROR: {ex}")

def run_single_stage_worker(folder_name: str, stage_num: int, url: str, model: str, niche: str = "", only_missing: bool = False):
    """Execute a single standalone stage with optional niche specification."""
    global STATE
    title = folder_name
    dirs = config.get_project_dirs(title)

    try:
        if stage_num == 1:
            if not url:
                add_log("Error: Stage 1 requires a YouTube URL.")
                return
            raw_title = "Ink Explainer Video"
            try:
                meta_res = subprocess.run(["yt-dlp", "--dump-json", "--no-warnings", url], capture_output=True, text=True, check=True)
                raw_title = json.loads(meta_res.stdout).get("title", "Ink Explainer Video")
            except Exception:
                pass
            new_folder = config.get_next_project_folder_name(raw_title, niche=niche or None)
            STATE["project_title"] = new_folder
            STATE["state"] = "RUNNING_POSTMORTEM"
            STATE["step1"] = "RUNNING"
            STATE["task_description"] = f"Ingesting and analyzing '{new_folder}'..."
            add_log(f"Running standalone Stage 1 into '{new_folder}' (Niche: {niche or 'Auto'})...")
            run_stage1_postmortem(url, custom_title=new_folder, niche=niche or None)
            STATE["step1"] = "COMPLETED"
            STATE["state"] = "COMPLETED"
            STATE["task_description"] = f"Stage 1 Postmortem complete for '{new_folder}'. Ready for Stage 2 (Script & Storyboard)."
            add_log(f"Standalone Stage 1 complete in '{new_folder}'.")

        elif stage_num == 2:
            dirs = config.get_project_dirs(title)
            has_existing_script = os.path.exists(dirs["master_csv"])
            has_transcript = os.path.exists(os.path.join(dirs["postmortem_dir"], "clean_transcript.txt"))

            if not has_existing_script:
                STATE["state"] = "AWAITING_ANTIGRAVITY_SCRIPT"
                STATE["step2"] = "AWAITING_ANTIGRAVITY"
                task_mode = "Repurposing Ingested Script" if has_transcript else "Creating Script From Topic"
                STATE["task_description"] = f"Awaiting Antigravity AI Engine ({task_mode}) for '{title}' (Niche: {niche or 'Auto'})..."
                add_log(f"Standalone Stage 2: Dispatched task to Antigravity AI Engine ({task_mode}) for '{title}'...")
            else:
                STATE["state"] = "RUNNING_SCRIPT"
                STATE["step2"] = "RUNNING"
                STATE["task_description"] = f"Syncing storyboard and MinutePhysics prompts for '{title}'..."
                add_log(f"Running standalone Stage 2 for '{title}'...")

            run_stage2_script_prompts(title, niche=niche or None)
            STATE["step2"] = "COMPLETED"
            STATE["state"] = "COMPLETED"
            STATE["task_description"] = f"Stage 2 Storyboard & Prompts complete for '{title}'. Ready for Stage 3 (Voiceover)."
            add_log(f"Standalone Stage 2 complete for '{title}'.")

        elif stage_num == 3:
            STATE["state"] = "RUNNING_VOICEOVER"
            STATE["step3"] = "RUNNING"
            STATE["task_description"] = f"Generating ElevenLabs Voiceover for '{title}'..."
            add_log(f"Running standalone Stage 3 for '{title}'...")
            run_stage3_voiceover(title, force_regenerate=True)
            STATE["step3"] = "COMPLETED"
            STATE["state"] = "COMPLETED"
            STATE["task_description"] = f"Stage 3 Voiceover complete for '{title}'. Ready for Stage 4 (Images)."
            add_log(f"Standalone Stage 3 complete for '{title}'.")

        elif stage_num == 4:
            STATE["state"] = "RUNNING_IMAGES"
            STATE["step4"] = "RUNNING"
            mode_desc = " (Only Missing)" if only_missing else ""
            STATE["task_description"] = f"Generating stick-figure images via Google Flow CDP for '{title}' on {model}{mode_desc}..."
            cb = make_stage4_progress_callback("Standalone")
            run_stage4_image_gen(title, model=model, only_missing=only_missing, status_callback=cb)
            STATE["step4"] = "COMPLETED"
            STATE["state"] = "COMPLETED"
            STATE["task_description"] = f"Stage 4 Images complete for '{title}'. Ready for Stage 5/6 (Review & XML)."
            add_log(f"Standalone Stage 4 complete for '{title}'.")

        elif stage_num == 6:
            STATE["state"] = "ASSEMBLING_XML"
            STATE["step6"] = "RUNNING"
            STATE["task_description"] = f"Assembling Premiere/FCP Timeline XML for '{title}'..."
            add_log(f"Running standalone Stage 6 for '{title}'...")
            run_stage5_timeline_xml(title)
            STATE["step6"] = "COMPLETED"
            STATE["state"] = "COMPLETED"
            STATE["task_description"] = f"Stage 6 Timeline XML assembled for '{title}'."
            add_log(f"Standalone Stage 6 Timeline XML assembled for '{title}'.")

    except Exception as ex:
        STATE["state"] = "ERROR"
        STATE["task_description"] = f"Stage {stage_num} Error: {ex}"
        add_log(f"ERROR in Stage {stage_num}: {ex}")

# -----------------------------------------------------------------------------
# FLASK ROUTES
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/projects")
def get_projects():
    """Return all available project folders."""
    projects = config.list_all_projects()
    return jsonify(projects)

@app.route("/api/status")
def get_status():
    st = dict(STATE)

    # Live check on stage 4 pause and running state
    s4_paused = is_stage4_paused()
    s4_running = is_stage4_running()

    if s4_paused and (st.get("step4") == "RUNNING" or st.get("state") in ("RUNNING_IMAGES", "RUNNING")):
        st["step4"] = "PAUSED"
        st["state"] = "PAUSED_IMAGES"
        st["task_description"] = "Stage 4 Image Generation paused. Click 'Resume' to continue."

    raw_state = st.get("state", "IDLE")
    is_error = bool(raw_state == "ERROR")
    is_paused = bool(
        not is_error and (
            "PAUSED" in raw_state or 
            st.get("step4") == "PAUSED" or 
            (s4_paused and st.get("step4") in ("RUNNING", "PAUSED")) or
            (not PAUSE_EVENT.is_set())
        )
    )

    is_running = bool(
        not is_error and not is_paused and (
            raw_state.startswith("RUNNING_") or 
            raw_state in ("RUNNING", "ASSEMBLING_XML", "AWAITING_ANTIGRAVITY_SCRIPT") or
            s4_running or
            st.get("step1") == "RUNNING" or
            st.get("step2") == "RUNNING" or
            st.get("step3") == "RUNNING" or
            st.get("step4") == "RUNNING" or
            st.get("step6") == "RUNNING"
        )
    )

    # Determine active stage (1, 2, 3, 4, 6)
    active_stage = None
    if raw_state == "RUNNING_POSTMORTEM" or st.get("step1") == "RUNNING":
        active_stage = 1
    elif raw_state in ("RUNNING_SCRIPT", "AWAITING_ANTIGRAVITY_SCRIPT") or st.get("step2") == "RUNNING":
        active_stage = 2
    elif raw_state == "RUNNING_VOICEOVER" or st.get("step3") == "RUNNING":
        active_stage = 3
    elif raw_state in ("RUNNING_IMAGES", "RUNNING") or st.get("step4") == "RUNNING" or s4_running:
        active_stage = 4
    elif raw_state == "ASSEMBLING_XML" or st.get("step6") == "RUNNING":
        active_stage = 6

    # Determine paused stage (1, 2, 3, 4)
    paused_stage = None
    if raw_state == "PAUSED_AFTER_STAGE_1":
        paused_stage = 1
    elif raw_state == "PAUSED_AFTER_STAGE_2":
        paused_stage = 2
    elif raw_state in ("PAUSED_AFTER_STAGE_3", "PAUSED_ELEVENLABS_KEY_EXHAUSTED"):
        paused_stage = 3
    elif raw_state == "PAUSED_IMAGES" or st.get("step4") == "PAUSED" or (s4_paused and (active_stage == 4 or st.get("step4") in ("RUNNING", "PAUSED"))):
        paused_stage = 4

    # Current action description
    if is_running:
        action_names = {
            1: "Ingestion & Forensic Postmortem (Stage 01)",
            2: "Compiling Script & Storyboard Prompts (Stage 02)",
            3: "Generating Combined Voiceover (Stage 03)",
            4: "Generating Autonomous Images on Google Flow (Stage 04)",
            6: "Assembling Final NLE Timeline XML (Stage 06)"
        }
        current_action = action_names.get(active_stage, f"Executing: {raw_state}")
    elif is_paused:
        current_action = f"Paused at Stage {paused_stage}" if paused_stage else f"Paused: {raw_state}"
    elif raw_state == "COMPLETED":
        current_action = "Stage / Pipeline Completed"
    elif raw_state == "ERROR":
        current_action = f"Error: {st.get('task_description', 'Pipeline failure')}"
    else:
        current_action = "Idle / Ready"

    st["is_running"] = is_running
    st["is_paused"] = is_paused
    st["active_stage"] = active_stage
    st["paused_stage"] = paused_stage
    st["current_action"] = current_action

    return jsonify(st)

@app.route("/api/start", methods=["POST"])
def start_pipeline():
    data = request.json or {}
    url = data.get("url", "").strip()
    title = data.get("title", "").strip()
    model = data.get("model", "Nano Banana Pro")
    niche = data.get("niche", "").strip()
    pause_mode = bool(data.get("pause_after_each_stage", False))

    if STATE["state"].startswith("RUNNING_"):
        return jsonify({"success": False, "message": "Pipeline is already running."}), 400

    PAUSE_EVENT.set()
    th = threading.Thread(target=run_pipeline_worker, args=(url, title, model, pause_mode, "", niche), daemon=True)
    th.start()

    return jsonify({"success": True, "message": "Pipeline launched successfully!"})

@app.route("/api/learning-stats")
@app.route("/api/learning_stats")
def get_learning_stats():
    """Return learning codex stats, partitioned niches, and reference index."""
    codex = load_codex()
    metadata = codex.get("metadata", {})
    niches = codex.get("niches", {})
    global_medians = codex.get("global_fallback_medians", {})

    niche_list = []
    ref_list = []

    for n_key, n_val in niches.items():
        bps = n_val.get("reference_blueprints", {})
        niche_list.append({
            "key": n_key,
            "display_name": n_val.get("display_name", n_key.title()),
            "description": n_val.get("description", ""),
            "videos_analyzed": n_val.get("videos_analyzed", len(bps)),
            "running_medians": n_val.get("running_medians", global_medians),
            "keywords": n_val.get("keywords", [])[:8],
            "blueprints_count": len(bps)
        })
        for k, v in bps.items():
            ref_list.append({
                "niche": n_key,
                "niche_display": n_val.get("display_name", n_key.title()),
                "title": v.get("title", k),
                "folder_name": v.get("folder_name", ""),
                "cuts_count": v.get("cuts_count", 0),
                "duration_sec": v.get("duration_sec", 0),
                "hook": v.get("hook", "")
            })

    niches_map = {item["key"]: item for item in niche_list}

    return jsonify({
        "success": True,
        "version": codex.get("_version", "2.0.0"),
        "total_analyzed": metadata.get("total_videos_analyzed", len(ref_list)),
        "active_niches_count": len(niche_list),
        "last_updated": metadata.get("last_updated", ""),
        "global_medians": global_medians,
        "medians": global_medians,
        "niches": niche_list,
        "niches_map": niches_map,
        "references": ref_list
    })

@app.route("/api/learning/niche", methods=["POST"])
def api_create_niche():
    """Dynamically register a new niche category in the codex."""
    data = request.json or {}
    display_name = (data.get("display_name") or data.get("name") or "").strip()
    key = (data.get("key") or data.get("slug") or "").strip()
    description = (data.get("description") or "").strip()
    keywords = data.get("keywords", [])
    wpm = float(data.get("wpm", 220.0))
    visual_tokens = data.get("visual_tokens", "")

    if not display_name:
        return jsonify({"success": False, "message": "Display Name is required."}), 400
    if not key:
        key = re.sub(r'[^a-zA-Z0-9_]', '_', display_name.lower().strip()).strip('_')

    running_med = {"wpm": wpm}
    res = create_dynamic_niche(
        key,
        display_name,
        description=description,
        keywords=keywords,
        running_medians=running_med,
        visual_tokens=visual_tokens
    )
    add_log(f"Codex: Dynamically created new niche category '{display_name}' ({key}).")
    return jsonify({"success": True, "niche": res, "key": key, "slug": key})

@app.route("/api/check-title-match", methods=["POST"])
def check_title_match():
    """Check if input title matches an existing reference video and detect its niche."""
    data = request.json or {}
    title = data.get("title", "").strip()
    niche = data.get("niche", "").strip() or None
    if not title:
        return jsonify({"matched": False})

    clf = classify_script_niche(title, auto_provision=False)
    target_niche = niche if (niche and niche != "auto") else clf.get("niche")
    match = find_matching_reference_video(title, niche=target_niche)

    codex = load_codex()
    active_niche_key = target_niche or clf.get("niche", "history")
    niche_obj = codex.get("niches", {}).get(active_niche_key, {})
    niche_medians = niche_obj.get("running_medians", codex.get("global_fallback_medians", {}))

    resp = {
        "matched": bool(match),
        "detected_niche": clf.get("niche", "history"),
        "detected_display": clf.get("display_name", "History & Archaeology"),
        "niche": active_niche_key,
        "niche_display": niche_obj.get("display_name", clf.get("display_name", "History")),
        "niche_name": niche_obj.get("display_name", clf.get("display_name", "History")),
        "niche_medians": niche_medians,
        "global_medians": codex.get("global_fallback_medians", {}),
        "confidence": clf.get("score", 0.0)
    }
    if match:
        bp = match.get("blueprint", {})
        resp.update({
            "title": match.get("title", ""),
            "score": match.get("score", 0),
            "niche": match.get("niche", active_niche_key),
            "niche_display": match.get("niche_display", niche_obj.get("display_name", "History")),
            "niche_name": match.get("niche_display", niche_obj.get("display_name", "History")),
            "hook": bp.get("hook", ""),
            "core_thesis": bp.get("core_thesis", ""),
            "acts": bp.get("story_progression", [])
        })
    return jsonify(resp)

@app.route("/api/start-from-prompt", methods=["POST"])
def start_from_prompt():
    """Launch pipeline from manual title and creative prompt with niche awareness."""
    data = request.json or {}
    title = data.get("title", "").strip()
    prompt = data.get("prompt", "").strip()
    model = data.get("model", "Nano Banana Pro")
    niche = data.get("niche", "").strip()
    pause_mode = bool(data.get("pause_after_each_stage", False))

    if not title:
        return jsonify({"success": False, "message": "Video Title is required."}), 400

    if STATE["state"].startswith("RUNNING_"):
        return jsonify({"success": False, "message": "Pipeline is already running."}), 400

    PAUSE_EVENT.set()
    th = threading.Thread(target=run_pipeline_worker, args=("", title, model, pause_mode, prompt, niche), daemon=True)
    th.start()

    return jsonify({"success": True, "message": "Pipeline launched from creative prompt!"})

@app.route("/api/run-stage", methods=["POST"])
def run_stage():
    """Run a specific standalone stage with optional niche."""
    data = request.json or {}
    folder_name = data.get("folder_name", "").strip() or STATE.get("project_title", "").strip()
    stage_num = int(data.get("stage_num", 1))
    url = data.get("url", "").strip()
    model = data.get("model", "Nano Banana Pro")
    niche = data.get("niche", "").strip()
    only_missing = bool(data.get("only_missing", False))

    if stage_num != 1 and not folder_name:
        return jsonify({"success": False, "message": f"Stage {stage_num} requires an existing project folder to be selected."}), 400

    if STATE["state"].startswith("RUNNING_"):
        return jsonify({"success": False, "message": "Another task is already running."}), 400

    PAUSE_EVENT.set()
    th = threading.Thread(target=run_single_stage_worker, args=(folder_name, stage_num, url, model, niche, only_missing), daemon=True)
    th.start()

    return jsonify({"success": True, "message": f"Stage {stage_num} launched!"})

@app.route("/api/pause", methods=["POST"])
def pause_pipeline():
    """Request pause of running pipeline or stage."""
    STATE["pause_after_each_stage"] = True
    STATE["pause_requested"] = True
    pause_stage4()
    if STATE.get("step4") == "RUNNING" or STATE.get("state") in ("RUNNING_IMAGES", "RUNNING"):
        STATE["state"] = "PAUSED_IMAGES"
        STATE["step4"] = "PAUSED"
        STATE["task_description"] = "Stage 4 Image Generation paused. Click Resume to continue generating."
        add_log("PAUSED: Stage 4 Image Generation paused.")
    else:
        add_log("PAUSE REQUESTED: Pipeline will pause after the active stage.")
    return jsonify({
        "success": True, 
        "message": "Pause requested. Pipeline will pause after current stage, or image stream is paused.",
        "state": STATE.get("state")
    })

@app.route("/api/resume", methods=["POST"])
def resume_pipeline():
    """Resume execution when paused after a stage or during Stage 4."""
    STATE["pause_requested"] = False
    if STATE.get("step4") == "PAUSED" or STATE.get("state") == "PAUSED_IMAGES":
        STATE["state"] = "RUNNING_IMAGES"
        STATE["step4"] = "RUNNING"
        STATE["task_description"] = "Resuming Google Flow image generation..."
        add_log("RESUMED: Resuming Stage 4 Google Flow image generation...")
    elif STATE.get("state") == "PAUSED_AFTER_STAGE_1":
        STATE["state"] = "RUNNING_SCRIPT"
        STATE["step2"] = "RUNNING"
        add_log("RESUMED: Advancing to Stage 2 (Script & Prompts)...")
    elif STATE.get("state") == "PAUSED_AFTER_STAGE_2":
        STATE["state"] = "RUNNING_VOICEOVER"
        STATE["step3"] = "RUNNING"
        add_log("RESUMED: Advancing to Stage 3 (Voiceover)...")
    elif STATE.get("state") == "PAUSED_AFTER_STAGE_3":
        STATE["state"] = "RUNNING_IMAGES"
        STATE["step4"] = "RUNNING"
        add_log("RESUMED: Advancing to Stage 4 (Images)...")
    else:
        add_log("RESUMED: Resuming pipeline execution...")
    resume_stage4()
    PAUSE_EVENT.set()
    return jsonify({"success": True, "message": "Pipeline resumed successfully.", "state": STATE.get("state")})

@app.route("/api/stop", methods=["POST"])
def stop_pipeline():
    """Immediately stop and cancel any running pipeline execution."""
    STOP_EVENT.set()
    cancel_stage4()
    PAUSE_EVENT.set()
    STATE["state"] = "IDLE"
    STATE["task_description"] = "Pipeline stopped by user. Canvas ready."
    add_log("STOPPED: Pipeline execution cancelled by user. Reset to Idle.")
    return jsonify({"success": True, "message": "Pipeline stopped successfully."})

@app.route("/api/test/set-state", methods=["POST"])
def api_test_set_state():
    """Test helper to set pipeline state for automated UI verification."""
    data = request.json or {}
    for k, v in data.items():
        if k in STATE:
            STATE[k] = v
    if data.get("is_paused"):
        PAUSE_EVENT.clear()
    elif data.get("is_paused") is False:
        PAUSE_EVENT.set()
    return jsonify({"success": True, "state": STATE})

@app.route("/api/stream-logs")
def stream_logs():
    """Stream live logs and status over SSE (Server-Sent Events)."""
    def generate():
        last_idx = 0
        while True:
            with LOG_LOCK:
                curr_logs = list(STATE.get("logs", []))
                curr_state = STATE.get("state", "IDLE")
            if len(curr_logs) > last_idx:
                new_logs = curr_logs[last_idx:]
                last_idx = len(curr_logs)
                payload = {
                    "logs": new_logs,
                    "state": curr_state,
                    "chrome_flow": check_chrome_flow_cdp_status(),
                    "stage4_progress": STATE.get("stage4_progress")
                }
                yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(1.0)
    return Response(generate(), mimetype="text/event-stream")

# -----------------------------------------------------------------------------
# ANTIGRAVITY AI ENGINE BRIDGE ROUTES
# -----------------------------------------------------------------------------
@app.route("/api/antigravity/task", methods=["GET"])
def api_get_antigravity_task():
    """Return the active Antigravity task with full payload and copyable prompt."""
    task = load_active_task_context()
    if not task:
        return jsonify({"success": False, "task": None, "active_task": None, "message": "No active Antigravity task."})

    inp = task.get("input_payload", {})
    ref_preview = inp.get("reference_transcript_preview", "")
    full_ref = inp.get("reference_transcript_full", ref_preview)
    niche = task.get("niche", "history")
    project = task.get("project_title", "")
    task_type = task.get("task_type", "")

    copyable_prompt = (
        f"ANTIGRAVITY TASK: {task_type}\n"
        f"Project: {project}\n"
        f"Niche: {niche}\n"
        f"Mandate: Repurpose/Create 100% original, witty 7-act script (Casually Explained / MinutePhysics style) "
        f"and compile into storyboard_master.csv with MinutePhysics stick-figure comic prompts.\n\n"
        f"Reference Transcript Preview ({inp.get('reference_word_count', 0)} words):\n"
        f"{full_ref[:800]}..."
    )

    return jsonify({
        "success": True,
        "task": task,
        "active_task": task,
        "copyable_prompt": copyable_prompt
    })

@app.route("/api/antigravity/complete", methods=["POST"])
def api_complete_antigravity_task():
    """Allows Antigravity or client to submit a completed script/storyboard."""
    data = request.json or {}
    project = data.get("project_title") or (get_active_task() or {}).get("project_title")
    script_text = data.get("script_text") or data.get("script", "")
    custom_shots = data.get("custom_shots") or data.get("shots")
    summary = data.get("summary")

    if not project:
        task = get_active_task()
        project = task.get("project_title") if task else None

    if not project:
        return jsonify({"success": False, "error": "No project title specified and no active task."}), 400

    if script_text or custom_shots:
        res = apply_antigravity_script_and_storyboard(
            project_title=project,
            script_text=script_text,
            custom_shots=custom_shots,
            niche=data.get("niche"),
            task_id=data.get("task_id")
        )
        add_log(f"Antigravity task completed for '{project}' ({res.get('total_shots', 0)} shots).")
        return jsonify({
            "success": True,
            "total_shots": res.get("total_shots", 0),
            "message": f"Storyboard for '{project}' applied and task completed."
        })
    else:
        task = get_active_task()
        if task:
            complete_task(task.get("task_id"), result_summary=summary or "Task marked complete via API")
            add_log(f"Antigravity AI Engine completed task: {summary or 'Task completed'}")
            return jsonify({"success": True, "message": "Task marked complete!"})
        return jsonify({"success": False, "message": "No active task found."}), 404

@app.route("/api/antigravity/cancel", methods=["POST"])
def api_cancel_antigravity_task():
    """Cancels the active Antigravity task and unblocks waiting threads."""
    cancel_active_task(reason="Cancelled via Web UI")
    add_log("Active Antigravity task cancelled.")
    return jsonify({"success": True, "message": "Active task cancelled."})

@app.route("/api/antigravity/submit-script", methods=["POST"])
def api_submit_script():
    """Directly submit synthesized script/shots to build storyboard CSV and complete task."""
    data = request.json or {}
    title = data.get("title", STATE["project_title"]).strip()
    script = data.get("script", "").strip()
    shots = data.get("shots", [])

    if not title:
        return jsonify({"success": False, "message": "Project title is required."}), 400
    if not script and not shots:
        return jsonify({"success": False, "message": "Script text or shots array is required."}), 400

    add_log(f"Antigravity AI Engine synthesizing storyboard for '{title}'...")
    res = synthesize_storyboard_from_script(script, title, custom_shots=shots)
    task = get_active_task()
    if task and task.get("project_title") == title:
        complete_task(task.get("task_id"), result_summary=f"Synthesized {res['total_shots']} shots.")

    add_log(f"Antigravity synthesized {res['total_shots']} shots (20-50 char pacing) for '{title}'.")
    return jsonify({"success": True, "result": res})

@app.route("/api/select-project", methods=["POST"])
def select_project():
    """Synchronize user project selection from UI to backend STATE."""
    data = request.json or {}
    title = data.get("title", "").strip()
    STATE["project_title"] = title
    if STATE["state"] == "ERROR":
        STATE["state"] = "IDLE"
        STATE["task_description"] = f"Ready. Selected project '{title}'." if title else "Clean canvas ready."
    return jsonify({"success": True, "project_title": title, "state": STATE["state"]})

@app.route("/api/reset-state", methods=["POST"])
def reset_state():
    """Clear error and reset pipeline state to IDLE."""
    STATE["state"] = "IDLE"
    STATE["task_description"] = "Clean canvas ready. Select a project or paste a URL to begin."
    STATE["step1"] = "WAITING"
    STATE["step2"] = "WAITING"
    STATE["step3"] = "WAITING"
    STATE["step4"] = "WAITING"
    STATE["step5"] = "WAITING"
    STATE["step6"] = "WAITING"
    return jsonify({"success": True})


@app.route("/api/shots")
def get_shots():
    title = request.args.get("title", STATE["project_title"]).strip()
    if not title:
        return jsonify({"shots": [], "total": 0})

    dirs = config.get_project_dirs(title)
    csv_path = dirs["master_csv"]
    final_img_dir = dirs["final_images_dir"]
    raw_img_dir = dirs["raw_images_dir"]
    audit_json = dirs["character_audit"]

    if not os.path.exists(csv_path):
        return jsonify({"shots": [], "total": 0})

    audit_map = {}
    if os.path.exists(audit_json):
        try:
            with open(audit_json, "r", encoding="utf-8") as f:
                audit_map = {d["shot_num"]: d for d in json.load(f)}
        except Exception:
            pass

    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))[1:]

    shots = []
    for r in rows:
        shot_num = int(r[0])
        tc = r[1]
        vo = r[2]
        desc = r[3]
        prompt = r[4] if len(r) > 4 else desc

        img_name = f"shot_{shot_num:03d}.jpg"
        img_full = os.path.join(final_img_dir, img_name)
        has_img = os.path.exists(img_full)
        w, h = get_image_dimensions(img_full) if has_img else (0, 0)
        is_2k = (w >= 2000)
        res_label = "2K" if is_2k else ("1K" if has_img else "")

        rec = audit_map.get(shot_num, {})
        category = rec.get("category", "VALID_STICK_FIGURE")
        score = rec.get("cv_info", {}).get("total_score", 95.0)

        # Detect variations
        variations = []
        for v_idx in range(1, 4):
            var_file = f"shot_{shot_num:03d}_regen_var_{v_idx}.jpg"
            var_full = os.path.join(raw_img_dir, var_file)
            if not os.path.exists(var_full):
                var_file = f"shot_{shot_num:03d}_var_{v_idx}.jpg"
                var_full = os.path.join(raw_img_dir, var_file)

            if os.path.exists(var_full):
                variations.append({
                    "var_idx": v_idx,
                    "filename": var_file,
                    "url": f"/images/{dirs['title']}/flow_generated_images/{var_file}",
                    "score": round(score - (v_idx - 1) * 3.0, 1),
                    "is_selected": (v_idx == 1)
                })

        shots.append({
            "shot_num": shot_num,
            "timecode": tc,
            "voiceover": vo,
            "description": desc,
            "prompt": prompt,
            "category": category,
            "score": score,
            "has_image": has_img,
            "width": w,
            "height": h,
            "is_2k": is_2k,
            "res_label": res_label,
            "image_url": f"/images/{dirs['title']}/Final selected images/{img_name}",
            "variations": variations
        })

    return jsonify({"shots": shots, "total": len(shots)})

@app.route("/api/select-image", methods=["POST"])
def select_image():
    data = request.json or {}
    title = data.get("title", STATE["project_title"])
    shot_num = int(data.get("shot_num", 0))
    var_filename = data.get("filename", "")

    dirs = config.get_project_dirs(title)
    final_img_dir = dirs["final_images_dir"]
    raw_img_dir = dirs["raw_images_dir"]

    src = os.path.join(raw_img_dir, var_filename)
    dst = os.path.join(final_img_dir, f"shot_{shot_num:03d}.jpg")

    if os.path.exists(src):
        safe_copy_file(src, dst)
        root_dst = os.path.join(config.ROOT_CANONICAL_IMAGES_DIR, f"shot_{shot_num:03d}.jpg")
        if os.path.exists(config.ROOT_CANONICAL_IMAGES_DIR):
            safe_copy_file(src, root_dst)

        add_log(f"Shot {shot_num:03d}: Selected variation '{var_filename}' as active image.")
        return jsonify({"success": True, "message": f"Shot {shot_num:03d} updated!"})
    else:
        return jsonify({"success": False, "message": f"Variation file not found: {var_filename}"}), 404

@app.route("/api/approve-and-build-xml", methods=["POST"])
def approve_and_build_xml():
    data = request.json or {}
    title = data.get("title", STATE["project_title"])

    STATE["state"] = "ASSEMBLING_XML"
    STATE["step5"] = "COMPLETED"
    STATE["step6"] = "RUNNING"
    add_log(f"Assembling Apple xmeml v4 timeline XML for '{title}'...")

    try:
        xml_res = run_stage5_timeline_xml(title)
        add_log(f"Timeline XML Sequence created at: {xml_res['xml_path']}")

        STATE["step6"] = "COMPLETED"
        STATE["state"] = "COMPLETED"
        STATE["task_description"] = "Production complete! Apple xmeml XML timeline ready."
        add_log("Production complete! XML timeline ready for Premiere Pro / DaVinci Resolve.")

        return jsonify({
            "success": True,
            "message": "Timeline XML built successfully!",
            "xml_path": xml_res["xml_path"]
        })
    except Exception as ex:
        STATE["state"] = "ERROR"
        STATE["step6"] = "FAILED"
        STATE["task_description"] = f"XML Assembly Error: {ex}"
        add_log(f"ERROR assembling XML: {ex}")
        return jsonify({"success": False, "error": str(ex)}), 500

# ------------------------------------------------------------------------------
# ELEVENLABS KEY POOL & VOICE MANAGEMENT ENDPOINTS
# ------------------------------------------------------------------------------
@app.route("/api/elevenlabs/keys", methods=["GET", "POST"])
def manage_elevenlabs_keys():
    if request.method == "POST":
        data = request.json or {}
        keys = data.get("keys", [])
        if isinstance(keys, str):
            keys = [k.strip() for k in re.split(r"[,\n]+", keys) if k.strip()]
        config.set_elevenlabs_api_keys(keys)
        summary = get_cached_pool_summary(force=True)
        return jsonify({"success": True, "message": "ElevenLabs keys updated", "pool_summary": summary})
    return jsonify({"success": True, "pool_summary": get_cached_pool_summary()})

@app.route("/api/elevenlabs/voices", methods=["GET"])
def get_elevenlabs_voices():
    keys = config.get_elevenlabs_api_keys()
    if not keys:
        return jsonify({"success": False, "error": "No ElevenLabs API key found in pool."}), 400
    last_err = None
    for k in keys:
        try:
            resp = requests.get("https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": k}, timeout=10)
            if resp.status_code == 200:
                voices_data = resp.json().get("voices", [])
                formatted = []
                for v in voices_data:
                    formatted.append({
                        "voice_id": v.get("voice_id"),
                        "name": v.get("name"),
                        "category": v.get("category", "premade"),
                        "preview_url": v.get("preview_url", ""),
                        "labels": v.get("labels", {})
                    })
                return jsonify({
                    "success": True,
                    "active_voice_id": config.ELEVENLABS_VOICE_ID,
                    "voices": formatted
                })
            else:
                last_err = f"HTTP {resp.status_code}: {resp.text}"
        except Exception as e:
            last_err = str(e)
    return jsonify({"success": False, "error": last_err or "Failed to fetch voices"}), 500

@app.route("/api/elevenlabs/set_voice", methods=["POST"])
@app.route("/api/elevenlabs/set-voice", methods=["POST"])
def set_active_voice():
    data = request.json or {}
    voice_id = data.get("voice_id", "").strip()
    voice_name = data.get("name", "").strip()
    if not voice_id:
        return jsonify({"success": False, "error": "Voice ID is required"}), 400
    config.ELEVENLABS_VOICE_ID = voice_id
    if os.path.exists(config.ENV_FILE):
        with open(config.ENV_FILE, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        has_v = False
        new_lines = []
        for line in lines:
            if line.startswith("ELEVENLABS_VOICE_ID="):
                new_lines.append(f"ELEVENLABS_VOICE_ID={voice_id}\n")
                has_v = True
            else:
                new_lines.append(line)
        if not has_v:
            new_lines.append(f"ELEVENLABS_VOICE_ID={voice_id}\n")
        with open(config.ENV_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    add_log(f"Active ElevenLabs Voice set to: '{voice_name or voice_id}' ({voice_id})")
    return jsonify({"success": True, "voice_id": voice_id, "name": voice_name})

@app.route("/api/elevenlabs/validate_key", methods=["POST"])
@app.route("/api/elevenlabs/validate-key", methods=["POST"])
def api_validate_elevenlabs_key():
    data = request.json or {}
    key = (data.get("api_key") or data.get("key") or "").strip()
    res = validate_elevenlabs_api_key(key)
    return jsonify(res)

@app.route("/api/elevenlabs/check_pool", methods=["GET", "POST"])
@app.route("/api/elevenlabs/check-pool", methods=["GET", "POST"])
def api_check_elevenlabs_pool():
    force = request.args.get("force", "false").lower() in ("true", "1", "yes") or request.method == "POST"
    summary = get_cached_pool_summary(force=force)
    return jsonify({"success": True, "pool_summary": summary})

@app.route("/api/elevenlabs/pool_summary", methods=["GET"])
@app.route("/api/elevenlabs/pool-summary", methods=["GET"])
def api_get_elevenlabs_pool_summary():
    force = request.args.get("force", "false").lower() in ("true", "1", "yes")
    return jsonify({"success": True, "pool_summary": get_cached_pool_summary(force=force)})

@app.route("/api/elevenlabs/cancel_key_wait", methods=["POST"])
@app.route("/api/elevenlabs/cancel-key-wait", methods=["POST"])
def api_cancel_elevenlabs_key_wait():
    cancel_elevenlabs_key_wait()
    title = STATE.get("project_title", "")
    prog = get_stage3_progress(title) if title else {}
    add_log(f"User cancelled key input for project '{title}'. Voiceover progress preserved cleanly on disk.")
    return jsonify({
        "success": True,
        "message": "Voiceover generation paused. Your progress has been safely saved on disk! You can resume anytime.",
        "progress": prog
    })

@app.route("/api/elevenlabs/add_key", methods=["POST"])
@app.route("/api/elevenlabs/add-key", methods=["POST"])
def api_add_elevenlabs_key():
    data = request.json or {}
    raw_input = (data.get("api_key") or data.get("key") or "").strip()
    if not raw_input:
        return jsonify({"success": False, "error": "API Key cannot be empty."}), 400
    new_keys = [k.strip() for k in re.split(r"[,\n]+", raw_input) if k.strip()]
    if not new_keys:
        return jsonify({"success": False, "error": "No valid API keys found in input."}), 400

    val = validate_elevenlabs_api_key(new_keys[0])
    if not val.get("valid"):
        return jsonify({"success": False, "error": f"Key validation failed: {val.get('error', 'Invalid ElevenLabs API Key')}"}), 400

    current_keys = config.get_elevenlabs_api_keys()
    for k in reversed(new_keys):
        if k in current_keys:
            current_keys.remove(k)
        current_keys.insert(0, k)
    config.set_elevenlabs_api_keys(current_keys)
    summary = get_cached_pool_summary(force=True)
    resume_elevenlabs_key_wait()

    rem = val.get("remaining_characters", 0)
    tier = str(val.get("tier", "Active")).capitalize()
    msg = f"Key verified ({tier} Tier, {rem:,} chars remaining)! Added to pool. Resuming voiceover generation..."
    add_log(f"Added fresh ElevenLabs key ({tier}, {rem} chars). Active pool size: {len(current_keys)}.")
    return jsonify({
        "success": True,
        "message": msg,
        "validation": val,
        "tier": tier,
        "remaining_characters": rem,
        "pool_summary": summary
    })

# ------------------------------------------------------------------------------
# IN-APP SETTINGS & DIRECTORY EXPLORER ENDPOINTS
# ------------------------------------------------------------------------------
@app.route("/api/settings", methods=["GET"])
@app.route("/api/settings/get", methods=["GET"])
def api_get_settings():
    config.reload_env_keys()
    gemini = os.getenv("GEMINI_API_KEY", "")
    google = os.getenv("GOOGLE_API_KEY", "")
    tmpl_data = {}
    tmpl_file = config.get_prompt_templates_file()
    if os.path.exists(tmpl_file):
        try:
            with open(tmpl_file, "r", encoding="utf-8") as f:
                tmpl_data = json.load(f)
        except Exception:
            pass
    eleven_keys = config.get_elevenlabs_api_keys()
    return jsonify({
        "success": True,
        "gemini_api_key": f"{gemini[:4]}...{gemini[-4:]}" if len(gemini) > 8 else ("****" if gemini else ""),
        "has_gemini_key": bool(gemini),
        "google_api_key": f"{google[:4]}...{google[-4:]}" if len(google) > 8 else ("****" if google else ""),
        "has_google_key": bool(google),
        "elevenlabs_keys": eleven_keys,
        "elevenlabs_api_keys": eleven_keys,
        "voice_id": config.ELEVENLABS_VOICE_ID,
        "elevenlabs_voice_id": config.ELEVENLABS_VOICE_ID,
        "model_id": config.ELEVENLABS_MODEL_ID,
        "max_silence_ms": config.MAX_SILENCE_MS,
        "projects_dir": config.FINALS_ROOT,
        "active_template": config.get_active_prompt_template(),
        "prompt_templates": tmpl_data.get("templates", []),
        "active_template_id": tmpl_data.get("active_template_id", "minutephysics_default"),
        "niches": config.get_all_niche_names()
    })

@app.route("/api/settings", methods=["POST"])
@app.route("/api/settings/save", methods=["POST"])
def api_save_settings():
    data = request.json or {}
    gemini = data.get("gemini_api_key", "").strip()
    google = data.get("google_api_key", "").strip()
    voice_id = (data.get("voice_id") or data.get("elevenlabs_voice_id") or "").strip()
    keys = data.get("elevenlabs_api_keys") if "elevenlabs_api_keys" in data else data.get("elevenlabs_keys")
    active_tmpl_id = data.get("active_template_id", "").strip()
    custom_base_prompt = data.get("custom_base_prompt", "").strip()
    projects_dir = data.get("projects_dir", "").strip()

    env_lines = []
    if os.path.exists(config.ENV_FILE):
        with open(config.ENV_FILE, "r", encoding="utf-8", errors="replace") as f:
            env_lines = f.readlines()

    def update_key_in_lines(lines, key_name, value):
        if not value: return lines
        found = False
        new_lines = []
        for l in lines:
            if l.startswith(f"{key_name}="):
                new_lines.append(f"{key_name}={value}\n")
                found = True
            else:
                new_lines.append(l)
        if not found:
            new_lines.append(f"{key_name}={value}\n")
        return new_lines

    if gemini and not gemini.startswith("****") and not "..." in gemini:
        env_lines = update_key_in_lines(env_lines, "GEMINI_API_KEY", gemini)
    if google and not google.startswith("****") and not "..." in google:
        env_lines = update_key_in_lines(env_lines, "GOOGLE_API_KEY", google)
    if voice_id:
        env_lines = update_key_in_lines(env_lines, "ELEVENLABS_VOICE_ID", voice_id)
    if projects_dir:
        env_lines = update_key_in_lines(env_lines, "PROJECTS_DIR", projects_dir)

    with open(config.ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(env_lines)

    if keys is not None:
        if isinstance(keys, str):
            keys = [k.strip() for k in re.split(r"[,\n]+", keys) if k.strip()]
        config.set_elevenlabs_api_keys(keys)

    tmpl_file = config.get_prompt_templates_file()
    if os.path.exists(tmpl_file):
        try:
            with open(tmpl_file, "r", encoding="utf-8") as f:
                tdata = json.load(f)
            if active_tmpl_id:
                tdata["active_template_id"] = active_tmpl_id
            if custom_base_prompt:
                custom_item = next((t for t in tdata.get("templates", []) if t.get("id") == "custom"), None)
                if custom_item:
                    custom_item["base_prompt"] = custom_base_prompt
                else:
                    tdata.setdefault("templates", []).append({
                        "id": "custom",
                        "name": "Custom User Base Template",
                        "base_prompt": custom_base_prompt,
                        "character_style": "stick-figure"
                    })
            with open(tmpl_file, "w", encoding="utf-8") as f:
                json.dump(tdata, f, indent=2)
        except Exception as e:
            print(f"Error updating template file: {e}")

    config.reload_env_keys()
    add_log("Settings successfully saved and reloaded.")
    return jsonify({"success": True, "message": "Settings & API Keys saved successfully!"})

@app.route("/api/open_folder", methods=["POST"])
@app.route("/api/project/open-folder", methods=["POST"])
def api_open_project_folder():
    data = request.json or {}
    title = data.get("title") or STATE["project_title"]
    if not title:
        return jsonify({"success": False, "error": "No project title specified"}), 400
    dirs = config.get_project_dirs(title)
    pdir = dirs["finals_dir"] if os.path.exists(dirs["finals_dir"]) else dirs["postmortem_dir"]
    os.makedirs(pdir, exist_ok=True)
    try:
        if sys.platform == "win32":
            os.startfile(pdir)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", pdir])
        else:
            subprocess.Popen(["xdg-open", pdir])
        return jsonify({"success": True, "path": pdir})
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)}), 500

@app.route("/api/open_projects_folder", methods=["POST"])
@app.route("/api/projects/open-root-folder", methods=["POST"])
def api_open_projects_root_folder():
    pdir = config.FINALS_ROOT
    os.makedirs(pdir, exist_ok=True)
    try:
        if sys.platform == "win32":
            os.startfile(pdir)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", pdir])
        else:
            subprocess.Popen(["xdg-open", pdir])
        return jsonify({"success": True, "path": pdir})
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)}), 500

# ------------------------------------------------------------------------------
# PROJECT MANAGEMENT & CUSTOM SCRIPT ENDPOINTS
# ------------------------------------------------------------------------------
@app.route("/api/create_project", methods=["POST"])
@app.route("/api/project/create", methods=["POST"])
def api_create_project():
    data = request.json or {}
    raw_title = data.get("title", "").strip()
    niche = data.get("niche", "history").strip().lower()
    if not raw_title:
        return jsonify({"success": False, "error": "Project title is required"}), 400
    folder_name = config.get_next_project_folder_name(raw_title, niche)
    dirs = config.get_project_dirs(folder_name, niche)
    os.makedirs(dirs["postmortem_dir"], exist_ok=True)
    os.makedirs(dirs["finals_dir"], exist_ok=True)
    os.makedirs(dirs["final_images_dir"], exist_ok=True)
    os.makedirs(dirs["voiceovers_dir"], exist_ok=True)
    STATE["project_title"] = dirs["relative_path"]
    STATE["state"] = "IDLE"
    add_log(f"Created new project: {dirs['relative_path']}")
    return jsonify({"success": True, "project_title": dirs["relative_path"], "folder_name": folder_name, "niche": niche, "message": f"Project '{dirs['relative_path']}' created!"})

@app.route("/api/rename_project", methods=["POST"])
@app.route("/api/project/rename", methods=["POST"])
def api_rename_project():
    data = request.json or {}
    old_title = data.get("old_title", "").strip()
    new_title = data.get("new_title", "").strip()
    if not old_title or not new_title:
        return jsonify({"success": False, "error": "Both old and new titles required"}), 400
    old_dirs = config.get_project_dirs(old_title)
    clean_new = config.sanitize_title(new_title)
    niche = old_dirs["niche"]
    new_dirs = config.get_project_dirs(clean_new, niche)
    renamed = False
    for root, d_old, d_new in [(config.FINALS_ROOT, old_dirs["finals_dir"], new_dirs["finals_dir"]),
                                (config.POSTMORTEM_ROOT, old_dirs["postmortem_dir"], new_dirs["postmortem_dir"])]:
        if os.path.exists(d_old) and not os.path.exists(d_new):
            os.rename(d_old, d_new)
            renamed = True
    if renamed:
        STATE["project_title"] = new_dirs["relative_path"]
        add_log(f"Renamed project from '{old_title}' to '{new_dirs['relative_path']}'")
        return jsonify({"success": True, "new_title": new_dirs["relative_path"], "message": f"Project renamed to '{new_dirs['relative_path']}'!"})
    return jsonify({"success": False, "error": "Project directory not found or target name already exists"}), 400

@app.route("/api/delete_project", methods=["POST"])
@app.route("/api/project/delete", methods=["POST"])
def api_delete_project():
    data = request.json or {}
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"success": False, "error": "Project title required"}), 400
    dirs = config.get_project_dirs(title)
    for pdir in [dirs["finals_dir"], dirs["postmortem_dir"]]:
        if os.path.exists(pdir):
            shutil.rmtree(pdir, ignore_errors=True)
    if STATE["project_title"] == title or STATE["project_title"] == dirs["relative_path"]:
        STATE["project_title"] = ""
        STATE["state"] = "IDLE"
    add_log(f"Deleted project '{title}'")
    return jsonify({"success": True, "message": f"Project '{title}' deleted successfully."})

@app.route("/api/save_custom_script", methods=["POST"])
@app.route("/api/script/save-custom", methods=["POST"])
def save_custom_script():
    data = request.json or {}
    title = data.get("title") or STATE["project_title"]
    script_text = data.get("script", "").strip()
    if not title:
        return jsonify({"success": False, "error": "No project specified"}), 400
    if not script_text:
        return jsonify({"success": False, "error": "Custom script cannot be empty"}), 400
    dirs = config.get_project_dirs(title)
    os.makedirs(dirs["finals_dir"], exist_ok=True)
    script_path = dirs["script_txt"]
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_text)
    add_log(f"Saved custom script ({len(script_text)} chars) for '{title}'")
    return jsonify({"success": True, "script_path": script_path, "message": "Custom VO script saved! Ready for Stage 2 & 3."})

@app.route("/api/get_clean_script", methods=["GET"])
@app.route("/api/script/get", methods=["GET"])
def get_clean_script():
    title = request.args.get("title") or STATE["project_title"]
    if not title:
        return jsonify({"success": False, "error": "No project specified"}), 400
    dirs = config.get_project_dirs(title)
    candidates = [
        dirs["script_txt"],
        os.path.join(dirs["finals_dir"], "clean_voiceover_script.txt"),
        os.path.join(dirs["postmortem_dir"], "clean_transcript.txt")
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                with open(c, "r", encoding="utf-8") as f:
                    content = f.read()
                words = content.split()
                return jsonify({
                    "success": True,
                    "content": content,
                    "script": content,
                    "title": title,
                    "file_path": c,
                    "word_count": len(words),
                    "char_count": len(content),
                    "est_minutes": round(len(words) / 150.0, 1),
                    "source_file": os.path.basename(c)
                })
            except Exception as ex:
                return jsonify({"success": False, "error": str(ex)}), 500
    return jsonify({"success": False, "content": "", "script": "", "word_count": 0, "char_count": 0, "est_minutes": 0, "source_file": ""})

# ------------------------------------------------------------------------------
# MANUAL PROMPTS MANAGEMENT ENDPOINTS
# ------------------------------------------------------------------------------
@app.route("/api/prompts/get", methods=["GET"])
def api_get_prompts():
    title = request.args.get("title") or STATE.get("project_title") or ""
    if not title:
        return jsonify({"success": False, "error": "No project specified"}), 400
    dirs = config.get_project_dirs(title)
    csv_path = dirs["master_csv"]
    all_prompts_path = dirs["all_prompts_txt"]

    shots = []
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.reader(f))[1:]
        for r in rows:
            if not r:
                continue
            s_num = int(r[0])
            tc = r[1] if len(r) > 1 else ""
            vo = r[2] if len(r) > 2 else ""
            desc = r[3] if len(r) > 3 else ""
            prompt = r[4] if len(r) > 4 else desc
            shots.append({
                "shot_num": s_num,
                "timecode": tc,
                "voiceover": vo,
                "description": desc,
                "prompt": prompt
            })

    raw_prompts = ""
    if os.path.exists(all_prompts_path):
        with open(all_prompts_path, "r", encoding="utf-8") as f:
            raw_prompts = f.read()
    elif shots:
        raw_prompts = "\n\n".join(f"Shot {s['shot_num']}: {s['prompt']}" for s in shots)

    return jsonify({
        "success": True,
        "title": title,
        "total_shots": len(shots),
        "shots": shots,
        "raw_prompts": raw_prompts,
        "has_csv": os.path.exists(csv_path),
        "has_prompts_txt": os.path.exists(all_prompts_path)
    })

@app.route("/api/prompts/save-manual", methods=["POST"])
def api_save_manual_prompts():
    data = request.json or {}
    title = data.get("title") or STATE.get("project_title") or ""
    if not title:
        return jsonify({"success": False, "error": "No project specified"}), 400

    dirs = config.get_project_dirs(title)
    finals_dir = dirs["finals_dir"]
    os.makedirs(finals_dir, exist_ok=True)
    os.makedirs(dirs["final_images_dir"], exist_ok=True)
    os.makedirs(dirs["raw_images_dir"], exist_ok=True)

    csv_path = dirs["master_csv"]
    all_prompts_path = dirs["all_prompts_txt"]

    shots_input = data.get("shots")
    raw_prompts_input = data.get("raw_prompts", "").strip()

    updated_rows = []
    header = ["Shot #", "Time", "Spoken VO script", "Visual description", "Exact Prompt for google nano banana pro"]

    if shots_input and isinstance(shots_input, list):
        existing_map = {}
        if os.path.exists(csv_path):
            with open(csv_path, "r", encoding="utf-8") as f:
                for r in list(csv.reader(f))[1:]:
                    if r:
                        existing_map[int(r[0])] = r

        for idx, item in enumerate(shots_input, 1):
            s_num = int(item.get("shot_num", idx))
            prompt = item.get("prompt", "").strip()
            vo = item.get("voiceover", "").strip()
            desc = item.get("description", "").strip() or prompt[:80]
            tc = item.get("timecode", "").strip()

            if s_num in existing_map:
                old = existing_map[s_num]
                tc = tc or (old[1] if len(old) > 1 else "")
                vo = vo or (old[2] if len(old) > 2 else "")
                desc = desc or (old[3] if len(old) > 3 else "")

            if not tc:
                s_time = (idx - 1) * 1.5
                e_time = idx * 1.5
                tc = f"{int(s_time//60):02d}:{s_time%60:04.1f} - {int(e_time//60):02d}:{e_time%60:04.1f}"

            updated_rows.append([s_num, tc, vo, desc, prompt])

    elif raw_prompts_input:
        lines = [line.strip() for line in raw_prompts_input.split("\n") if line.strip()]
        parsed_prompts = []
        for line in lines:
            m = re.match(r"^Shot\s*#?\s*(\d+)[\s:.\-]+(.*)$", line, re.IGNORECASE)
            if m:
                parsed_prompts.append((int(m.group(1)), m.group(2).strip()))
            else:
                parsed_prompts.append((len(parsed_prompts) + 1, line))

        existing_rows = []
        if os.path.exists(csv_path):
            with open(csv_path, "r", encoding="utf-8") as f:
                existing_rows = list(csv.reader(f))[1:]

        for idx, (s_num, p_text) in enumerate(parsed_prompts, 1):
            s_idx = idx
            if idx <= len(existing_rows):
                old = existing_rows[idx - 1]
                tc = old[1] if len(old) > 1 else ""
                vo = old[2] if len(old) > 2 else ""
                desc = old[3] if len(old) > 3 else p_text[:80]
            else:
                s_time = (idx - 1) * 1.5
                e_time = idx * 1.5
                tc = f"{int(s_time//60):02d}:{s_time%60:04.1f} - {int(e_time//60):02d}:{e_time%60:04.1f}"
                vo = f"Shot {idx}"
                desc = p_text[:80]

            updated_rows.append([s_idx, tc, vo, desc, p_text])
    else:
        return jsonify({"success": False, "error": "No shots or raw prompts provided"}), 400

    # Save to CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(updated_rows)

    # Save to all_prompts.txt
    all_prompts_content = []
    for r in updated_rows:
        all_prompts_content.append(f"Shot {r[0]}: {r[4]}")
    with open(all_prompts_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_prompts_content) + "\n")

    # Update PROMPT_STATUS.md
    prompt_status_md = dirs["prompt_status_md"]
    with open(prompt_status_md, "w", encoding="utf-8") as f:
        f.write(f"# Prompt Status Tracker: {title}\n\n")
        f.write(f"Total manual prompts configured: {len(updated_rows)}\n\n")
        f.write("| Shot # | Status | Prompt Excerpt |\n| --- | --- | --- |\n")
        for r in updated_rows:
            f.write(f"| #{int(r[0]):03d} | READY | {r[4][:60]}... |\n")

    add_log(f"Manual prompts updated for '{title}' ({len(updated_rows)} shots saved to CSV & all_prompts.txt)")
    return jsonify({
        "success": True,
        "message": f"Successfully updated {len(updated_rows)} manual prompts for '{title}'!",
        "total_shots": len(updated_rows)
    })

# ------------------------------------------------------------------------------
# CHROME FLOW CDP & PLAYWRIGHT REGENERATION ENDPOINTS
# ------------------------------------------------------------------------------
@app.route("/api/chrome_flow_status", methods=["GET"])
def get_chrome_flow_status():
    return jsonify(check_chrome_flow_cdp_status())

@app.route("/api/launch_chrome", methods=["POST"])
@app.route("/api/chrome/launch", methods=["POST"])
def api_launch_chrome():
    try:
        import chrome_launcher
        ok, msg = chrome_launcher.launch_chrome_flow_cdp()
        add_log(f"Chrome Launcher: {msg}")
        return jsonify({"success": ok, "message": msg})
    except Exception as ex:
        add_log(f"ERROR launching Chrome: {ex}")
        return jsonify({"success": False, "error": str(ex)}), 500

@app.route("/api/stage4/pause", methods=["POST"])
def api_pause_stage4():
    pause_stage4()
    if STATE.get("step4") == "RUNNING" or STATE.get("state") in ("RUNNING_IMAGES", "RUNNING"):
        STATE["state"] = "PAUSED_IMAGES"
        STATE["step4"] = "PAUSED"
        STATE["task_description"] = "Stage 4 Image Generation paused by user. Click Resume to continue."
    add_log("PAUSED: Stage 4 Image Generation PAUSED.")
    return jsonify({"success": True, "message": "Stage 4 Paused.", "state": STATE.get("state")})

@app.route("/api/stage4/resume", methods=["POST"])
def api_resume_stage4():
    resume_stage4()
    if STATE.get("step4") == "PAUSED" or STATE.get("state") == "PAUSED_IMAGES":
        STATE["state"] = "RUNNING_IMAGES"
        STATE["step4"] = "RUNNING"
        STATE["task_description"] = "Stage 4 Image Generation resumed."
    add_log("RESUMED: Stage 4 Image Generation RESUMED.")
    return jsonify({"success": True, "message": "Stage 4 Resumed.", "state": STATE.get("state")})

@app.route("/api/stage4/cancel", methods=["POST"])
def api_cancel_stage4():
    cancel_stage4()
    STATE["step4"] = "CANCELLED"
    STATE["state"] = "IDLE"
    STATE["task_description"] = "Stage 4 Image Generation cancelled."
    add_log("CANCELLED: Stage 4 Image Generation cancelled.")
    return jsonify({"success": True, "message": "Stage 4 Cancelled.", "state": STATE.get("state")})

@app.route("/api/stage4/range", methods=["POST"])
@app.route("/api/stage4/run-range", methods=["POST"])
def api_run_stage4_range():
    data = request.json or {}
    title = data.get("folder_name") or data.get("title") or STATE["project_title"]
    if not title:
        return jsonify({"success": False, "error": "Select an active project first."}), 400
    start_shot = int(data.get("start_shot", 1))
    end_shot = int(data.get("end_shot", 9999))
    model = data.get("model", "Nano Banana Pro")
    only_missing = bool(data.get("only_missing", False))
    force_all = False if only_missing else bool(data.get("force_all", True))
    resolution = (data.get("resolution") or getattr(config, "FLOW_IMAGE_RESOLUTION", "2k") or "2k").lower().strip()

    def range_worker():
        try:
            resume_stage4()
            STATE["step4"] = "RUNNING"
            STATE["state"] = "RUNNING_IMAGES"
            mode_tag = " [ONLY MISSING]" if only_missing else ""
            STATE["task_description"] = f"Running Stage 4 Image Generation ({resolution.upper()}){mode_tag} on Shots {start_shot} to {end_shot}..."
            add_log(f"Stage 4 Range Generation started for Shots {start_shot} to {end_shot} (Model: {model}, Res: {resolution.upper()}, Only Missing: {only_missing})")
            cb = make_stage4_progress_callback("Range")
            res = run_stage4_image_gen(
                video_title=title,
                start_shot=start_shot,
                end_shot=end_shot,
                model=model,
                force_all=force_all,
                resolution=resolution,
                only_missing=only_missing,
                status_callback=cb
            )
            STATE["step4"] = "COMPLETED"
            STATE["state"] = "IDLE"
            completed_cnt = res.get('completed_in_run', res.get('completed', 0))
            STATE["task_description"] = f"Stage 4 Range completed ({completed_cnt} shots)."
            add_log(f"Stage 4 Range Generation completed: {res}")
        except Exception as ex:
            cancel_stage4()
            STATE["step4"] = "FAILED"
            STATE["state"] = "ERROR"
            STATE["task_description"] = f"Stage 4 Range Error: {ex}"
            add_log(f"Stage 4 Range Error: {ex}")
        finally:
            if "stage4_progress" in STATE:
                STATE["stage4_progress"]["is_active"] = False

    t = threading.Thread(target=range_worker, daemon=True)
    t.start()
    return jsonify({"success": True, "message": f"Stage 4 Range ({start_shot}-{end_shot}) started in background."})

@app.route("/api/stage4/missing-shots", methods=["GET", "POST"])
def api_get_missing_shots():
    """Return count and list of shot numbers that do not have final images."""
    data = request.json if request.is_json else {}
    title = request.args.get("title") or request.args.get("folder_name") or data.get("title") or data.get("folder_name") or STATE.get("project_title", "").strip()
    if not title:
        return jsonify({"success": False, "error": "Select an active project first."}), 400

    start_shot = int(request.args.get("start_shot") or data.get("start_shot") or 1)
    end_shot_raw = request.args.get("end_shot") or data.get("end_shot")
    end_shot = int(end_shot_raw) if end_shot_raw else None

    missing = get_missing_shots(title, start_shot=start_shot, end_shot=end_shot)
    dirs = config.get_project_dirs(title)
    csv_path = dirs["master_csv"]
    total_shots = 0
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            total_shots = max(0, len(list(csv.reader(f))) - 1)

    generated_shots = max(0, total_shots - len(missing)) if total_shots >= len(missing) else 0

    return jsonify({
        "success": True,
        "project": title,
        "total_shots": total_shots,
        "generated_shots": generated_shots,
        "missing_count": len(missing),
        "missing_shots": missing
    })

@app.route("/api/stage4/generate-missing", methods=["POST"])
def api_generate_missing_stage4():
    """Trigger generation of all missing shots for the project or range."""
    data = request.json or {}
    title = data.get("folder_name") or data.get("title") or STATE.get("project_title", "").strip()
    if not title:
        return jsonify({"success": False, "error": "Select an active project first."}), 400

    start_shot = int(data.get("start_shot", 1))
    end_shot = int(data.get("end_shot", 9999))
    model = data.get("model", "Nano Banana Pro")
    resolution = (data.get("resolution") or getattr(config, "FLOW_IMAGE_RESOLUTION", "2k") or "2k").lower().strip()

    missing_shots = get_missing_shots(title, start_shot=start_shot, end_shot=end_shot)
    if not missing_shots:
        return jsonify({
            "success": True,
            "missing_count": 0,
            "missing_shots": [],
            "message": f"All shots for '{title}' already have images! Zero missing."
        })

    def missing_worker():
        try:
            resume_stage4()
            STATE["step4"] = "RUNNING"
            STATE["state"] = "RUNNING_IMAGES"
            preview_shots = missing_shots[:8]
            preview_str = ", ".join(f"#{s}" for s in preview_shots) + ("..." if len(missing_shots) > 8 else "")
            STATE["task_description"] = f"Generating {len(missing_shots)} missing images for '{title}' ({resolution.upper()}): {preview_str}"
            add_log(f"Stage 4 Missing Images Generation started: {len(missing_shots)} missing shots ({preview_str})")
            cb = make_stage4_progress_callback("Missing")
            res = run_stage4_image_gen(
                video_title=title,
                target_shots=missing_shots,
                model=model,
                resolution=resolution,
                only_missing=True,
                status_callback=cb
            )
            STATE["step4"] = "COMPLETED"
            STATE["state"] = "IDLE"
            completed_cnt = res.get('completed_in_run', len(missing_shots))
            STATE["task_description"] = f"Stage 4 Missing Images complete ({completed_cnt} shots generated)."
            add_log(f"Stage 4 Missing Images Generation complete: {res}")
        except Exception as ex:
            cancel_stage4()
            STATE["step4"] = "FAILED"
            STATE["state"] = "ERROR"
            STATE["task_description"] = f"Stage 4 Missing Images Error: {ex}"
            add_log(f"Stage 4 Missing Images Error: {ex}")
        finally:
            if "stage4_progress" in STATE:
                STATE["stage4_progress"]["is_active"] = False

    t = threading.Thread(target=missing_worker, daemon=True)
    t.start()
    return jsonify({
        "success": True,
        "missing_count": len(missing_shots),
        "missing_shots": missing_shots,
        "message": f"Stage 4 Missing Images ({len(missing_shots)} shots) started in background."
    })

@app.route("/api/stage4/production-status", methods=["GET"])
def api_get_stage4_production_status():
    """Return Arslan's production_status.json and PROMPT_STATUS.md for active project."""
    title = request.args.get("title") or request.args.get("folder_name") or STATE.get("project_title", "").strip()
    if not title:
        return jsonify({"success": False, "error": "Select a project first."}), 400
    dirs = config.get_project_dirs(title)
    status_file = dirs["production_status"]
    status_data = {}
    if os.path.exists(status_file):
        try:
            with open(status_file, "r", encoding="utf-8") as f:
                status_data = json.load(f)
        except Exception:
            pass

    md_file = dirs["prompt_status_md"]
    md_content = ""
    if os.path.exists(md_file):
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                md_content = f.read()
        except Exception:
            pass

    return jsonify({
        "success": True,
        "production_status": status_data,
        "prompt_status_md": md_content,
        "live_progress": STATE.get("stage4_progress", {}),
        "stage4_progress": STATE.get("stage4_progress", {})
    })

@app.route("/api/stage2/run-fallback", methods=["POST"])
def api_stage2_run_fallback():
    """Execute offline rule-based fallback for Stage 2."""
    data = request.json or {}
    folder_name = data.get("folder_name") or STATE.get("project_title", "").strip()
    if not folder_name:
        return jsonify({"success": False, "error": "No project specified."}), 400

    def fallback_worker():
        try:
            STATE["state"] = "RUNNING_SCRIPT"
            STATE["step2"] = "RUNNING"
            add_log(f"Running offline fallback Stage 2 for '{folder_name}'...")
            res = run_stage2_script_prompts(folder_name, use_offline_fallback=True)
            STATE["step2"] = "COMPLETED"
            STATE["state"] = "COMPLETED"
            add_log(f"Offline fallback Stage 2 complete for '{folder_name}' ({res.get('total_shots', 0)} shots).")
        except Exception as ex:
            STATE["state"] = "ERROR"
            STATE["step2"] = "ERROR"
            add_log(f"Offline fallback error: {ex}")

    t = threading.Thread(target=fallback_worker, daemon=True)
    t.start()
    return jsonify({"success": True, "message": f"Offline fallback started for '{folder_name}'."})

def get_chrome_flow_page(playwright_instance):
    """Safely connect to Chrome CDP and retrieve Google Flow page, returning (page, error_msg)."""
    for endpoint in config.CDP_ENDPOINTS:
        try:
            b = playwright_instance.chromium.connect_over_cdp(endpoint)
            for ctx in b.contexts:
                for pg in ctx.pages:
                    if "flow.google.com" in pg.url or "labs.google" in pg.url:
                        return pg, None
        except Exception:
            continue
    return None, "Google Flow tab not found in Chrome. Please open https://flow.google.com in Chrome."

@app.route("/api/regen/prepare", methods=["POST"])
@app.route("/api/shot/regen-prepare", methods=["POST"])
def regen_prepare():
    data = request.json or {}
    title = data.get("title") or STATE["project_title"]
    shot_num = int(data.get("shot_num", 0))
    prompt = data.get("prompt", "").strip()
    if not title or shot_num <= 0:
        return jsonify({"success": False, "error": "Missing shot_num or title"}), 400

    dirs = config.get_project_dirs(title)
    csv_path = dirs["master_csv"]
    if not prompt and os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.reader(f))[1:]
        for r in rows:
            if int(r[0]) == shot_num:
                prompt = r[4] if len(r) > 4 else r[3]
                break

    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            flow_page, err = get_chrome_flow_page(p)
            if not flow_page:
                return jsonify({"success": False, "error": err}), 500
            flow_page.bring_to_front()
            editor = flow_page.locator("div.prosemirror-editor div.ProseMirror, div.ProseMirror[contenteditable='true'], div.ProseMirror").first
            editor.click(timeout=4000)
            time.sleep(0.2)
            flow_page.keyboard.press("Control+A")
            flow_page.keyboard.press("Backspace")
            time.sleep(0.2)
            editor.fill(prompt)

            pre_urls = set(flow_page.evaluate("""() => {
                return Array.from(document.querySelectorAll('img'))
                    .filter(i => (i.src || '').includes('googleusercontent') || (i.src || '').includes('blob:'))
                    .map(i => i.src);
            }"""))
            REGEN_CACHE[shot_num] = list(pre_urls)
            add_log(f"Shot #{shot_num:03d}: Prompt injected into Chrome Flow editor.")
            return jsonify({"success": True, "message": "Prompt injected into Flow", "shot_num": shot_num, "prompt": prompt})
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)}), 500

@app.route("/api/regen/capture", methods=["POST"])
@app.route("/api/shot/regen-capture", methods=["POST"])
def regen_capture():
    data = request.json or {}
    title = data.get("title") or STATE["project_title"]
    shot_num = int(data.get("shot_num", 0))
    if not title or shot_num <= 0:
        return jsonify({"success": False, "error": "Missing shot_num or title"}), 400
    dirs = config.get_project_dirs(title)
    final_img_dir = dirs["final_images_dir"]
    raw_img_dir = dirs["raw_images_dir"]
    pre_urls = set(REGEN_CACHE.get(shot_num, []))

    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            flow_page, err = get_chrome_flow_page(p)
            if not flow_page:
                return jsonify({"success": False, "error": err}), 500
            flow_page.bring_to_front()
            new_tiles = flow_page.evaluate("""(preList) => {
                const preSet = new Set(preList || []);
                return Array.from(document.querySelectorAll('img'))
                    .filter(i => {
                        const s = i.src || '';
                        return (s.includes('googleusercontent') || s.includes('blob:')) && !preSet.has(s);
                    })
                    .map(i => i.src);
            }""", list(pre_urls))

            if not new_tiles:
                return jsonify({"success": False, "error": "No newly generated images found on Flow canvas yet."}), 404

            saved_files = []
            for v_idx, tile_url in enumerate(new_tiles[:2]):
                dest_file = os.path.join(raw_img_dir, f"shot_{shot_num:03d}_var{v_idx+1}.jpg")
                try:
                    resp = flow_page.request.get(tile_url)
                    if resp.status == 200:
                        with open(dest_file, "wb") as f_out:
                            f_out.write(resp.body())
                        saved_files.append(dest_file)
                except Exception as e:
                    print(f"Error saving var {v_idx+1}: {e}")

            if saved_files:
                final_path = os.path.join(final_img_dir, f"shot_{shot_num:03d}.jpg")
                res_setting = (data.get("resolution") or getattr(config, "FLOW_IMAGE_RESOLUTION", "2k") or "2k").lower().strip()
                downloaded_2k = False
                if res_setting == "2k":
                    best_tile_src = new_tiles[0] if new_tiles else None
                    downloaded_2k = download_flow_image_2k(flow_page, target_src=best_tile_src, dest_path=final_path)

                if not downloaded_2k or not os.path.exists(final_path):
                    safe_copy_file(saved_files[0], final_path)

                root_final = os.path.join(config.ROOT_CANONICAL_IMAGES_DIR, f"shot_{shot_num:03d}.jpg")
                if os.path.exists(config.ROOT_CANONICAL_IMAGES_DIR):
                    safe_copy_file(final_path, root_final)

                try:
                    run_stage5_timeline_xml(title)
                except Exception:
                    pass
                res_lbl = "2K Native Upscaled" if downloaded_2k else "1K Standard"
                add_log(f"Shot #{shot_num:03d}: Captured and updated image from Chrome Flow ({res_lbl}).")
                w, h = get_image_dimensions(final_path)
                return jsonify({
                    "success": True,
                    "saved_files": saved_files,
                    "final_image": f"shot_{shot_num:03d}.jpg",
                    "width": w,
                    "height": h,
                    "is_2k": (w >= 2000),
                    "res_label": res_lbl,
                    "message": f"Shot #{shot_num:03d} updated with {res_lbl} image!"
                })
            return jsonify({"success": False, "error": "Failed to download image tiles"}), 500
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)}), 500

@app.route("/api/regen/full", methods=["POST"])
@app.route("/api/shot/regen-full", methods=["POST"])
def regen_full():
    data = request.json or {}
    title = data.get("title") or STATE["project_title"]
    shot_num = int(data.get("shot_num", 0))
    prompt = data.get("prompt", "").strip()
    if not title or shot_num <= 0:
        return jsonify({"success": False, "error": "Missing shot_num or title"}), 400

    prep_res = regen_prepare()
    if getattr(prep_res, "status_code", 200) != 200:
        return prep_res

    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            flow_page, err = get_chrome_flow_page(p)
            if not flow_page:
                return jsonify({"success": False, "error": err}), 500
            flow_page.keyboard.press("Enter")
            pre_urls = set(REGEN_CACHE.get(shot_num, []))
            for _ in range(45):
                time.sleep(1.0)
                new_tiles = flow_page.evaluate("""(preList) => {
                    const preSet = new Set(preList || []);
                    return Array.from(document.querySelectorAll('img'))
                        .filter(i => {
                            const s = i.src || '';
                            return (s.includes('googleusercontent') || s.includes('blob:')) && !preSet.has(s);
                        })
                        .map(i => i.src);
                }""", list(pre_urls))
                if new_tiles:
                    break
        return regen_capture()
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)}), 500

# ------------------------------------------------------------------------------
# MANUAL VOICEOVER PROCESSING ENDPOINTS
# ------------------------------------------------------------------------------
@app.route("/api/voiceover/inspect-existing", methods=["GET"])
def api_inspect_existing_voiceover():
    title = request.args.get("title") or STATE.get("project_title") or ""
    if not title:
        return jsonify({"has_audio": False, "error": "No project specified"})
    dirs = config.get_project_dirs(title)
    vo_dir = dirs["voiceovers_dir"]
    finals_dir = dirs["finals_dir"]

    candidates = [
        os.path.join(finals_dir, "voiceover_master_normalized.mp3"),
        os.path.join(finals_dir, "voiceover_master.mp3")
    ]
    if os.path.exists(vo_dir):
        for f in os.listdir(vo_dir):
            if f.lower().endswith((".mp3", ".wav", ".m4a")):
                candidates.append(os.path.join(vo_dir, f))

    found_audio = None
    for c in candidates:
        if os.path.exists(c) and os.path.getsize(c) > 0:
            found_audio = c
            break

    if not found_audio:
        return jsonify({"has_audio": False})

    size_mb = round(os.path.getsize(found_audio) / (1024 * 1024), 2)
    filename = os.path.basename(found_audio)
    duration_sec = 0
    sample_rate = 44100
    channels = 2
    try:
        import soundfile as sf
        info = sf.info(found_audio)
        duration_sec = round(info.duration, 2)
        sample_rate = info.samplerate
        channels = info.channels
    except Exception:
        duration_sec = round(os.path.getsize(found_audio) / 24000.0, 1)

    mins = int(duration_sec // 60)
    secs = int(duration_sec % 60)
    formatted_duration = f"{mins}:{secs:02d}"
    rel_path = os.path.relpath(found_audio, finals_dir).replace("\\", "/")
    audio_url = f"/projects/{title}/{rel_path}"

    return jsonify({
        "has_audio": True,
        "file_path": found_audio,
        "audio_url": audio_url,
        "audio_info": {
            "filename": filename,
            "duration_sec": duration_sec,
            "formatted_duration": formatted_duration,
            "size_mb": size_mb,
            "sample_rate": sample_rate,
            "channels": channels
        }
    })

@app.route("/api/voiceover/upload-manual", methods=["POST"])
def api_upload_manual_voiceover():
    title = request.form.get("title") or STATE.get("project_title") or ""
    if not title:
        return jsonify({"success": False, "error": "No project specified"}), 400
    if "audio_file" not in request.files:
        return jsonify({"success": False, "error": "No audio file provided"}), 400

    audio_file = request.files["audio_file"]
    if not audio_file.filename:
        return jsonify({"success": False, "error": "Empty filename"}), 400

    dirs = config.get_project_dirs(title)
    vo_dir = dirs["voiceovers_dir"]
    os.makedirs(vo_dir, exist_ok=True)

    from werkzeug.utils import secure_filename
    safe_name = secure_filename(audio_file.filename) or "manual_voiceover.mp3"
    dest_path = os.path.join(vo_dir, f"manual_{safe_name}")
    audio_file.save(dest_path)

    size_mb = round(os.path.getsize(dest_path) / (1024 * 1024), 2)
    duration_sec = 0
    sample_rate = 44100
    channels = 2
    try:
        import soundfile as sf
        info = sf.info(dest_path)
        duration_sec = round(info.duration, 2)
        sample_rate = info.samplerate
        channels = info.channels
    except Exception:
        duration_sec = round(os.path.getsize(dest_path) / 24000.0, 1)

    mins = int(duration_sec // 60)
    secs = int(duration_sec % 60)
    formatted_duration = f"{mins}:{secs:02d}"
    rel_path = os.path.relpath(dest_path, dirs["finals_dir"]).replace("\\", "/")
    audio_url = f"/projects/{title}/{rel_path}"

    add_log(f"Manual VO uploaded for '{title}': {safe_name} ({size_mb} MB)")
    return jsonify({
        "success": True,
        "file_path": dest_path,
        "audio_url": audio_url,
        "audio_info": {
            "filename": safe_name,
            "duration_sec": duration_sec,
            "formatted_duration": formatted_duration,
            "size_mb": size_mb,
            "sample_rate": sample_rate,
            "channels": channels
        }
    })

@app.route("/api/voiceover/process-manual", methods=["POST"])
def api_process_manual_voiceover():
    data = request.json or {}
    title = data.get("title") or STATE.get("project_title") or ""
    audio_path = data.get("audio_path") or ""
    srt_path = data.get("srt_path", "").strip()
    trim_silence = bool(data.get("trim_silence", True))
    use_whisper = bool(data.get("use_whisper", True))

    if not title:
        return jsonify({"success": False, "error": "No project specified"}), 400
    if not audio_path or not os.path.exists(audio_path):
        return jsonify({"success": False, "error": f"Audio file not found: {audio_path}"}), 400

    dirs = config.get_project_dirs(title)
    finals_dir = dirs["finals_dir"]
    master_norm = os.path.join(finals_dir, "voiceover_master_normalized.mp3")

    def manual_vo_worker():
        try:
            add_log(f"Starting manual VO processing for '{title}'...")
            STATE["state"] = "RUNNING_VOICEOVER"
            STATE["task_description"] = "Processing manual voiceover..."
            cmd = ["ffmpeg", "-y", "-i", audio_path, "-codec:a", "libmp3lame", "-b:a", "192k", master_norm]
            subprocess.run(cmd, check=True, capture_output=True)
            add_log(f"Manual voiceover normalized to: {master_norm}")

            # If an SRT file was attached, align timestamps immediately
            if srt_path and os.path.exists(srt_path):
                add_log(f"Aligning manual VO timestamps with SRT: {os.path.basename(srt_path)}...")
                try:
                    align_res = align_storyboard_with_srt(title, srt_path)
                    add_log(f"SRT timestamps aligned ({align_res.get('shots_count', 0)} shots, 0 gaps).")
                except Exception as srt_err:
                    add_log(f"Notice: SRT alignment error during VO processing: {srt_err}")
            else:
                try:
                    run_stage5_timeline_xml(title)
                    add_log("Timeline XML updated with manual voiceover.")
                except Exception as e:
                    add_log(f"XML update notice: {e}")

            STATE["state"] = "IDLE"
            STATE["task_description"] = "Manual voiceover processed and timeline updated."
        except Exception as ex:
            STATE["state"] = "ERROR"
            STATE["task_description"] = f"Manual voiceover error: {ex}"
            add_log(f"ERROR processing manual VO: {ex}")

    threading.Thread(target=manual_vo_worker, daemon=True).start()
    return jsonify({"success": True, "message": "Manual voiceover processing launched."})

# ------------------------------------------------------------------------------
# MANUAL SRT TIMESTAMPS ENDPOINTS
# ------------------------------------------------------------------------------
@app.route("/api/timestamps/inspect-srt", methods=["GET"])
def api_inspect_srt():
    title = request.args.get("title") or STATE.get("project_title") or ""
    if not title:
        return jsonify({"success": False, "has_srt": False, "error": "No project specified"})

    dirs = config.get_project_dirs(title)
    finals_dir = dirs["finals_dir"]
    vo_dir = dirs["voiceovers_dir"]

    candidates = []
    for d in [finals_dir, vo_dir]:
        if os.path.exists(d):
            for f in sorted(os.listdir(d)):
                if f.lower().endswith(".srt"):
                    full_p = os.path.join(d, f)
                    candidates.append(full_p)

    if not candidates:
        return jsonify({"success": True, "has_srt": False, "srt_files": []})

    best_srt = candidates[0]
    cues = parse_srt(best_srt)
    preview_cues = cues[:8] if cues else []
    total_dur = cues[-1]["end_sec"] if cues else 0

    return jsonify({
        "success": True,
        "has_srt": True,
        "default_file": {
            "path": best_srt,
            "filename": os.path.basename(best_srt),
            "cue_count": len(cues),
            "total_duration_sec": total_dur,
            "formatted_duration": f"{int(total_dur//60)}m {int(total_dur%60):02d}s",
            "preview_cues": preview_cues
        },
        "all_files": [{"filename": os.path.basename(p), "path": p} for p in candidates]
    })

@app.route("/api/timestamps/upload-srt", methods=["POST"])
def api_upload_srt():
    title = request.form.get("title") or STATE.get("project_title") or ""
    if not title:
        return jsonify({"success": False, "error": "No project specified"}), 400

    if "srt_file" not in request.files:
        return jsonify({"success": False, "error": "No SRT file uploaded"}), 400

    srt_file = request.files["srt_file"]
    if not srt_file.filename:
        return jsonify({"success": False, "error": "Empty filename"}), 400

    dirs = config.get_project_dirs(title)
    vo_dir = dirs["voiceovers_dir"]
    os.makedirs(vo_dir, exist_ok=True)

    from werkzeug.utils import secure_filename
    safe_name = secure_filename(srt_file.filename) or "manual_subtitles.srt"
    if not safe_name.lower().endswith(".srt"):
        safe_name += ".srt"

    dest_path = os.path.join(vo_dir, safe_name)
    srt_file.save(dest_path)

    cues = parse_srt(dest_path)
    total_dur = cues[-1]["end_sec"] if cues else 0

    add_log(f"SRT file uploaded for '{title}': {safe_name} ({len(cues)} cues, {total_dur:.1f}s)")
    return jsonify({
        "success": True,
        "file_path": dest_path,
        "filename": safe_name,
        "cue_count": len(cues),
        "total_duration_sec": total_dur,
        "formatted_duration": f"{int(total_dur//60)}m {int(total_dur%60):02d}s",
        "preview_cues": cues[:8]
    })

@app.route("/api/timestamps/align-srt", methods=["POST"])
def api_align_srt():
    data = request.json or {}
    title = data.get("title") or STATE.get("project_title") or ""
    srt_path = data.get("srt_path", "").strip()
    srt_content = data.get("srt_content", "").strip()
    fps = int(data.get("fps", 24))

    if not title:
        return jsonify({"success": False, "error": "No project specified"}), 400

    target_srt = srt_path or srt_content
    if not target_srt:
        dirs = config.get_project_dirs(title)
        for d in [dirs["finals_dir"], dirs["voiceovers_dir"]]:
            if os.path.exists(d):
                for f in sorted(os.listdir(d)):
                    if f.lower().endswith(".srt"):
                        target_srt = os.path.join(d, f)
                        break
            if target_srt:
                break

    if not target_srt:
        return jsonify({"success": False, "error": "No SRT file or subtitle text provided"}), 400

    try:
        res = align_storyboard_with_srt(title, target_srt, fps=fps)
        add_log(f"SRT Timestamps aligned for '{title}': {res['shots_count']} shots locked ({res['srt_cues_count']} cues, {res['total_duration_sec']}s, 0 gaps). Timeline XML regenerated.")
        return jsonify({
            "success": True,
            "result": res,
            "message": f"Successfully locked {res['shots_count']} shots to SRT timestamps! Timeline XML updated."
        })
    except Exception as ex:
        add_log(f"ERROR during SRT alignment: {ex}")
        return jsonify({"success": False, "error": str(ex)}), 500

# ------------------------------------------------------------------------------
# 2K IMAGE RESOLUTION & DOWNLOAD ENDPOINTS
# ------------------------------------------------------------------------------
@app.route("/api/shot/pull-flow-2k", methods=["POST"])
def api_pull_flow_2k():
    """Triggers native Google Flow 2K Upscaled download for a shot via Chrome CDP."""
    data = request.json or {}
    title = data.get("title") or STATE.get("project_title") or ""
    shot_num = int(data.get("shot_num", 0))
    if not title or shot_num <= 0:
        return jsonify({"success": False, "error": "Missing title or shot_num"}), 400

    try:
        res = pull_single_shot_2k_from_flow(title, shot_num)
        add_log(f"Shot #{shot_num:03d}: Pulled native 2K upscaled image from Google Flow ({res['width']}x{res['height']}).")
        return jsonify({
            "success": True,
            "message": f"Shot #{shot_num:03d} upgraded to 2K ({res['width']}x{res['height']})!",
            "result": res
        })
    except Exception as ex:
        add_log(f"Shot #{shot_num:03d} 2K pull error: {ex}")
        return jsonify({"success": False, "error": str(ex)}), 500

@app.route("/api/shot/download-2k", methods=["GET"])
def api_download_shot_2k():
    """Directly serves a single shot image as a 2K attachment download."""
    title = request.args.get("title", STATE.get("project_title", "")).strip()
    shot_num = int(request.args.get("shot_num", 0))
    if not title or shot_num <= 0:
        return "Missing title or shot_num", 400

    dirs = config.get_project_dirs(title)
    final_img_dir = dirs["final_images_dir"]
    img_name = f"shot_{shot_num:03d}.jpg"
    src_path = os.path.join(final_img_dir, img_name)

    if not os.path.exists(src_path):
        return f"Shot image {img_name} not found", 404

    # Cache directory for 2K images
    cache_2k_dir = os.path.join(dirs["finals_dir"], "Final selected images 2K")
    cached_path = os.path.join(cache_2k_dir, img_name)

    try:
        w, h = get_image_dimensions(src_path)
        if w >= 2500 and h >= 1400:
            target_file = src_path
        else:
            if not os.path.exists(cached_path):
                ensure_2k_image(src_path, cached_path)
            target_file = cached_path

        return send_from_directory(
            os.path.dirname(target_file),
            os.path.basename(target_file),
            as_attachment=True,
            download_name=f"shot_{shot_num:03d}_2K.jpg"
        )
    except Exception as ex:
        return f"Error preparing 2K image: {ex}", 500

@app.route("/api/project/download-all-2k", methods=["GET"])
def api_download_all_2k():
    """Generates and streams a .zip archive containing all project shots in 2K."""
    title = request.args.get("title", STATE.get("project_title", "")).strip()
    if not title:
        return "Missing project title", 400

    try:
        zip_buf, zip_name, count = build_project_2k_zip(title)
        add_log(f"Packaged {count} 2K images into '{zip_name}' for project '{title}'.")
        return Response(
            zip_buf.getvalue(),
            mimetype="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={zip_name}",
                "Content-Length": str(len(zip_buf.getvalue()))
            }
        )
    except Exception as ex:
        add_log(f"Error building 2K zip: {ex}")
        return f"Error creating 2K zip: {ex}", 500

@app.route("/api/project/export-2k-folder", methods=["POST"])
def api_export_2k_folder():
    """Converts/exports all final shots into 'Final selected images 2K/' folder on disk."""
    data = request.json or {}
    title = data.get("title") or STATE.get("project_title") or ""
    if not title:
        return jsonify({"success": False, "error": "Missing title"}), 400

    dirs = config.get_project_dirs(title)
    final_img_dir = dirs["final_images_dir"]
    cache_2k_dir = os.path.join(dirs["finals_dir"], "Final selected images 2K")
    os.makedirs(cache_2k_dir, exist_ok=True)

    if not os.path.exists(final_img_dir):
        return jsonify({"success": False, "error": "Final images directory does not exist"}), 404

    files = sorted([f for f in os.listdir(final_img_dir) if f.lower().startswith("shot_") and f.lower().endswith((".jpg", ".png", ".jpeg"))])
    count = 0
    for f in files:
        src = os.path.join(final_img_dir, f)
        dst = os.path.join(cache_2k_dir, f)
        ensure_2k_image(src, dst)
        count += 1

    add_log(f"Exported {count} 2K images to folder: {cache_2k_dir}")
    return jsonify({
        "success": True,
        "count": count,
        "folder": cache_2k_dir,
        "message": f"Successfully exported {count} 2K images to 'Final selected images 2K'!"
    })

@app.route("/images/<project_title>/<path:subpath>")
@app.route("/projects/<project_title>/<path:subpath>")
def serve_image(project_title, subpath):
    dirs = config.get_project_dirs(project_title)
    base = dirs["finals_dir"]
    full_path = os.path.join(base, subpath)
    dir_name = os.path.dirname(full_path)
    file_name = os.path.basename(full_path)
    if os.path.exists(full_path):
        return send_from_directory(dir_name, file_name)
    return "Image not found", 404

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("="*65)
    print(f"  INK EXPLAINER STUDIO WEB UI RUNNING")
    print(f"  Access local URL: http://localhost:{port}")
    print("="*65)
    app.run(host="0.0.0.0", port=port, debug=False)
