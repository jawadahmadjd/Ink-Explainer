#!/usr/bin/env python3
"""
Antigravity Stage 2 Automation & CLI Runner
Author: Google DeepMind Antigravity System
Purpose:
  Provides command-line and programmatic control for Antigravity-driven
  script repurposing, script creation, and visual prompt compilation.
"""

import os
import sys
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from modules.antigravity_bridge import (
    get_active_task,
    load_active_task_context,
    apply_antigravity_script_and_storyboard,
    complete_task,
    cancel_active_task,
    synthesize_storyboard_from_script
)

def print_active_task_status():
    """Display the active Antigravity task in a clear readable terminal dashboard."""
    task = load_active_task_context()
    if not task:
        print("\n[ANTIGRAVITY BRIDGE] No active pending task.")
        return None

    status = task.get("status", "UNKNOWN")
    task_type = task.get("task_type", "UNKNOWN")
    project = task.get("project_title", "UNKNOWN")
    niche = task.get("niche", "history")
    inp = task.get("input_payload", {})
    ref_wc = inp.get("reference_word_count", 0)
    has_ref = inp.get("has_reference_transcript", False)

    print("\n" + "=" * 65)
    print(f"  ANTIGRAVITY ACTIVE TASK: {task.get('task_id')}")
    print("=" * 65)
    print(f"  • Status         : {status}")
    print(f"  • Type           : {task_type}")
    print(f"  • Project Title  : {project}")
    print(f"  • Niche          : {niche.upper()}")
    print(f"  • Reference Script: {'Yes (' + str(ref_wc) + ' words)' if has_ref else 'None (From Scratch)'}")
    print(f"  • User Prompt    : {inp.get('user_prompt') or 'None'}")
    print(f"  • Created At     : {task.get('created_at')}")

    preview = inp.get("reference_transcript_preview", "")
    if preview:
        print("\n  [Reference Transcript Preview]:")
        print(f"  \"{preview[:300]}...\"")

    print("\n  [Instructions Summary]:")
    print("  - Tone: Witty, deadpan, Casually Explained / MinutePhysics style (SOP 03)")
    print("  - Never-Orphan grammar shield (~20-65 chars / 1.0s-2.2s per cut)")
    print("  - MinutePhysics stick figures (pure white heads, bold black lines, 16:9 full bleed)")
    print("=" * 65 + "\n")
    return task

def process_active_task_with_script(script_text: str = None, script_file: str = None, custom_shots: list = None):
    """Applies a synthesized script to the active task and unlocks the pipeline."""
    task = get_active_task()
    if not task:
        print("[ERROR] No active Antigravity task found to complete.")
        return False

    project = task["project_title"]
    niche = task.get("niche", "history")
    task_id = task.get("task_id")

    final_script = script_text or ""
    if script_file and os.path.exists(script_file):
        with open(script_file, "r", encoding="utf-8") as f:
            final_script = f.read()

    if not final_script and not custom_shots:
        print("[ERROR] Neither script text nor custom shots provided.")
        return False

    print(f"[ANTIGRAVITY RUNNER] Compiling storyboard and visual prompts for '{project}'...")
    res = apply_antigravity_script_and_storyboard(
        project_title=project,
        script_text=final_script,
        custom_shots=custom_shots,
        niche=niche,
        task_id=task_id
    )
    print(f"-> [SUCCESS] Compiled {res['total_shots']} shots into '{res['master_csv']}'.")
    print(f"-> Active task '{task_id}' COMPLETED. Studio pipeline will auto-resume.")
    return True

def auto_synthesize_active_task():
    """
    Synthesize the active task using Antigravity AI synthesis and blueprint matching.
    """
    task = load_active_task_context()
    if not task:
        print("[ERROR] No active task to synthesize.")
        return False

    project = task["project_title"]
    inp = task.get("input_payload", {})
    niche = task.get("niche", "history")
    ref_transcript = inp.get("reference_transcript_full") or inp.get("reference_transcript_preview", "")
    task_id = task.get("task_id")

    from modules.script_spinner import get_spun_script_for_title
    print(f"[ANTIGRAVITY AUTO-SYNTHESIS] Processing '{project}' (Niche: {niche})...")

    # If reference matches blueprint or reference transcript exists, rewrite into witty spun script
    spun_script = get_spun_script_for_title(project, raw_transcript=ref_transcript)
    if not spun_script:
        spun_script = ref_transcript or inp.get("user_prompt", f"An entertaining explainer about {project}.")

    res = apply_antigravity_script_and_storyboard(
        project_title=project,
        script_text=spun_script,
        niche=niche,
        task_id=task_id
    )
    print(f"-> [SUCCESS] Auto-synthesized {res['total_shots']} shots for '{project}'.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Antigravity Stage 2 CLI Runner")
    parser.add_argument("--status", action="store_true", help="Print active pending task status")
    parser.add_argument("--auto", action="store_true", help="Auto-synthesize active task using Antigravity intelligence")
    parser.add_argument("--script-file", type=str, help="Path to text file containing synthesized script")
    parser.add_argument("--cancel", action="store_true", help="Cancel active task")

    args = parser.parse_args()

    if args.status:
        print_active_task_status()
    elif args.cancel:
        cancel_active_task()
        print("[ANTIGRAVITY RUNNER] Active task cancelled.")
    elif args.script_file:
        process_active_task_with_script(script_file=args.script_file)
    elif args.auto:
        auto_synthesize_active_task()
    else:
        print_active_task_status()
        print("Usage:")
        print("  python run_antigravity_stage2.py --status")
        print("  python run_antigravity_stage2.py --auto")
        print("  python run_antigravity_stage2.py --script-file <path_to_script.txt>")

if __name__ == "__main__":
    main()
