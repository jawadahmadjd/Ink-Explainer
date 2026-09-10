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
import threading
import time
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

import config
from modules.stage1_postmortem import run_stage1_postmortem
from modules.stage2_script_prompts import run_stage2_script_prompts
from modules.stage3_voiceover import run_stage3_voiceover
from modules.stage4_image_gen import run_stage4_image_gen, safe_copy_file
from modules.stage5_timeline_xml import run_stage5_timeline_xml
from modules.stage6_reporter import PipelineReporter
from learning.learning_engine import (
    load_codex,
    find_matching_reference_video,
    ingest_postmortem_to_codex
)

app = Flask(__name__, template_folder=os.path.join(CODE_DIR, "templates"))

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
    ]
}

LOG_LOCK = threading.Lock()
PAUSE_EVENT = threading.Event()
PAUSE_EVENT.set()  # set means running; cleared means paused

def add_log(msg: str):
    with LOG_LOCK:
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}"
        STATE["logs"].append(entry)
        if len(STATE["logs"]) > 200:
            STATE["logs"].pop(0)
        print(entry)

def run_pipeline_worker(url: str, custom_title: str, model: str, pause_mode: bool, prompt: str = ""):
    """Background worker executing the pipeline step by step with ascending folder numbering."""
    global STATE
    STATE["pause_after_each_stage"] = pause_mode

    # Auto-number project if new URL
    if not custom_title and url:
        add_log("Fetching video metadata to determine ascending project folder...")
        try:
            res = subprocess.run(["yt-dlp", "--dump-json", "--no-warnings", url], capture_output=True, text=True, check=True)
            info = json.loads(res.stdout)
            raw_title = info.get("title", "Ink Explainer Video")
        except Exception as e:
            raw_title = "Ink Explainer Video"
        project_folder = config.get_next_project_folder_name(raw_title)
    elif custom_title:
        project_folder = config.get_next_project_folder_name(custom_title)
    else:
        project_folder = config.get_next_project_folder_name("Ink Explainer Video")

    STATE["project_title"] = project_folder
    add_log(f"Assigned project folder: '{project_folder}'")

    try:
        # Step 1: Ingestion
        if url:
            STATE["state"] = "RUNNING_POSTMORTEM"
            STATE["step1"] = "RUNNING"
            STATE["task_description"] = f"Stage 1: Ingestion & Forensic Postmortem into '{project_folder}'..."
            add_log(f"Starting Stage 1 for URL: {url}")
            run_stage1_postmortem(url, custom_title=project_folder)
            STATE["step1"] = "COMPLETED"
            add_log("Stage 1 Ingestion & Postmortem completed.")

            if STATE["pause_after_each_stage"]:
                STATE["state"] = "PAUSED_AFTER_STAGE_1"
                STATE["task_description"] = "Stage 1 Complete. Paused for review. Click 'Continue' to advance to Stage 2."
                add_log("PAUSED: Stage 1 complete. Awaiting user continue...")
                PAUSE_EVENT.clear()
                PAUSE_EVENT.wait()
        else:
            STATE["step1"] = "SKIPPED (Manual Prompt Mode)"
            add_log("Mode B: Manual Title & Prompt Mode. Stage 1 Ingestion bypassed.")

        # Step 2: Script & Prompts
        STATE["state"] = "RUNNING_SCRIPT"
        STATE["step2"] = "RUNNING"
        STATE["task_description"] = "Stage 2: Script & Stick-Figure Prompts..."
        add_log("Generating script and full-bleed stick-figure prompts (16-32 char pacing)...")
        run_stage2_script_prompts(project_folder, user_prompt=prompt)
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

def run_single_stage_worker(folder_name: str, stage_num: int, url: str, model: str):
    """Execute a single standalone stage."""
    global STATE
    title = folder_name
    dirs = config.get_project_dirs(title)

    try:
        if stage_num == 1:
            if not url:
                add_log("Error: Stage 1 requires a YouTube URL.")
                return
            new_folder = config.get_next_project_folder_name("Ink Explainer Video")
            STATE["project_title"] = new_folder
            STATE["state"] = "RUNNING_POSTMORTEM"
            STATE["step1"] = "RUNNING"
            add_log(f"Running standalone Stage 1 into '{new_folder}'...")
            run_stage1_postmortem(url, custom_title=new_folder)
            STATE["step1"] = "COMPLETED"
            STATE["state"] = "COMPLETED"
            add_log(f"Standalone Stage 1 complete in '{new_folder}'.")

        elif stage_num == 2:
            STATE["state"] = "RUNNING_SCRIPT"
            STATE["step2"] = "RUNNING"
            add_log(f"Running standalone Stage 2 for '{title}'...")
            run_stage2_script_prompts(title)
            STATE["step2"] = "COMPLETED"
            STATE["state"] = "COMPLETED"
            add_log(f"Standalone Stage 2 complete for '{title}'.")

        elif stage_num == 3:
            STATE["state"] = "RUNNING_VOICEOVER"
            STATE["step3"] = "RUNNING"
            add_log(f"Running standalone Stage 3 for '{title}'...")
            run_stage3_voiceover(title, force_regenerate=True)
            STATE["step3"] = "COMPLETED"
            STATE["state"] = "COMPLETED"
            add_log(f"Standalone Stage 3 complete for '{title}'.")

        elif stage_num == 4:
            STATE["state"] = "RUNNING_IMAGES"
            STATE["step4"] = "RUNNING"
            add_log(f"Running standalone Stage 4 for '{title}' on {model}...")
            run_stage4_image_gen(title, model=model)
            STATE["step4"] = "COMPLETED"
            STATE["state"] = "COMPLETED"
            add_log(f"Standalone Stage 4 complete for '{title}'.")

        elif stage_num == 6:
            STATE["state"] = "ASSEMBLING_XML"
            STATE["step6"] = "RUNNING"
            add_log(f"Running standalone Stage 6 for '{title}'...")
            run_stage5_timeline_xml(title)
            STATE["step6"] = "COMPLETED"
            STATE["state"] = "COMPLETED"
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
    return jsonify(STATE)

@app.route("/api/start", methods=["POST"])
def start_pipeline():
    data = request.json or {}
    url = data.get("url", "").strip()
    title = data.get("title", "").strip()
    model = data.get("model", "Nano Banana Pro")
    pause_mode = bool(data.get("pause_after_each_stage", False))

    if STATE["state"].startswith("RUNNING_"):
        return jsonify({"success": False, "message": "Pipeline is already running."}), 400

    PAUSE_EVENT.set()
    th = threading.Thread(target=run_pipeline_worker, args=(url, title, model, pause_mode), daemon=True)
    th.start()

    return jsonify({"success": True, "message": "Pipeline launched successfully!"})

@app.route("/api/learning-stats")
def get_learning_stats():
    """Return learning codex stats and reference index."""
    codex = load_codex()
    medians = codex.get("running_medians", {})
    metadata = codex.get("metadata", {})
    blueprints = codex.get("reference_blueprints", {})
    ref_list = []
    for k, v in blueprints.items():
        ref_list.append({
            "title": v.get("title", k),
            "folder_name": v.get("folder_name", ""),
            "cuts_count": v.get("cuts_count", 0),
            "duration_sec": v.get("duration_sec", 0),
            "hook": v.get("hook", "")
        })
    return jsonify({
        "total_analyzed": metadata.get("total_videos_analyzed", len(ref_list)),
        "last_updated": metadata.get("last_updated", ""),
        "medians": medians,
        "references": ref_list
    })

@app.route("/api/check-title-match", methods=["POST"])
def check_title_match():
    """Check if input title matches an existing analyzed reference video."""
    data = request.json or {}
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"matched": False})

    match = find_matching_reference_video(title)
    if match:
        bp = match.get("blueprint", {})
        return jsonify({
            "matched": True,
            "title": match.get("title", ""),
            "score": match.get("score", 0),
            "hook": bp.get("hook", ""),
            "core_thesis": bp.get("core_thesis", ""),
            "acts": bp.get("story_progression", [])
        })
    return jsonify({"matched": False})

@app.route("/api/start-from-prompt", methods=["POST"])
def start_from_prompt():
    """Launch pipeline from manual title and creative prompt."""
    data = request.json or {}
    title = data.get("title", "").strip()
    prompt = data.get("prompt", "").strip()
    model = data.get("model", "Nano Banana Pro")
    pause_mode = bool(data.get("pause_after_each_stage", False))

    if not title:
        return jsonify({"success": False, "message": "Video Title is required."}), 400

    if STATE["state"].startswith("RUNNING_"):
        return jsonify({"success": False, "message": "Pipeline is already running."}), 400

    PAUSE_EVENT.set()
    th = threading.Thread(target=run_pipeline_worker, args=("", title, model, pause_mode, prompt), daemon=True)
    th.start()

    return jsonify({"success": True, "message": "Pipeline launched from creative prompt!"})

@app.route("/api/run-stage", methods=["POST"])
def run_stage():
    """Run a specific standalone stage."""
    data = request.json or {}
    folder_name = data.get("folder_name", "").strip()
    stage_num = int(data.get("stage_num", 1))
    url = data.get("url", "").strip()
    model = data.get("model", "Nano Banana Pro")

    if stage_num != 1 and not folder_name:
        return jsonify({"success": False, "message": f"Stage {stage_num} requires an existing project folder to be selected."}), 400

    if STATE["state"].startswith("RUNNING_"):
        return jsonify({"success": False, "message": "Another task is already running."}), 400

    PAUSE_EVENT.set()
    th = threading.Thread(target=run_single_stage_worker, args=(folder_name, stage_num, url, model), daemon=True)
    th.start()

    return jsonify({"success": True, "message": f"Stage {stage_num} launched!"})

@app.route("/api/resume", methods=["POST"])
def resume_pipeline():
    """Resume execution when paused after a stage."""
    add_log("Resuming pipeline execution to next stage...")
    PAUSE_EVENT.set()
    return jsonify({"success": True, "message": "Resumed."})

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

@app.route("/images/<project_title>/<path:subpath>")
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
