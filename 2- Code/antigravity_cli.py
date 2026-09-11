"""
Antigravity CLI Utility
Author: Google DeepMind Antigravity System
Command-line interface for:
1. Inspecting pending Antigravity tasks.
2. Submitting synthesized scripts and decomposing into 16-32 char storyboard beats.
3. Marking tasks complete to resume automated pipeline execution.
"""

import os
import sys
import argparse
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from modules.antigravity_bridge import (
    get_active_task,
    complete_task,
    dispatch_task,
    synthesize_storyboard_from_script
)

def main():
    parser = argparse.ArgumentParser(description="Antigravity AI Engine CLI")
    parser.add_argument("--status", action="store_true", help="Check current active task status")
    parser.add_argument("--complete", action="store_true", help="Mark active task as completed")
    parser.add_argument("--project", type=str, help="Project folder name (e.g. '2- Why We Sleep')")
    parser.add_argument("--script-file", type=str, help="Path to text file containing narration script")
    parser.add_argument("--script-text", type=str, help="Raw script text to synthesize")
    parser.add_argument("--summary", type=str, default="Completed via Antigravity CLI", help="Task completion summary")

    args = parser.parse_args()

    if args.status:
        task = get_active_task()
        if task:
            print("="*60)
            print("ACTIVE ANTIGRAVITY TASK:")
            print(f"Task ID:    {task.get('task_id')}")
            print(f"Type:       {task.get('task_type')}")
            print(f"Project:    {task.get('project_title')}")
            print(f"Status:     {task.get('status')}")
            print(f"Created At: {task.get('created_at')}")
            payload = task.get("input_payload", {})
            print(f"Title:      {payload.get('title')}")
            print(f"Prompt:     {payload.get('user_prompt')}")
            print("="*60)
        else:
            print("No active pending task.")
        return

    if args.script_file or args.script_text:
        project = args.project
        if not project:
            task = get_active_task()
            if task:
                project = task.get("project_title")
            else:
                print("Error: --project is required when no active task exists.")
                sys.exit(1)

        script_content = args.script_text or ""
        if args.script_file:
            with open(args.script_file, "r", encoding="utf-8") as f:
                script_content = f.read()

        if not script_content.strip():
            print("Error: Script content is empty.")
            sys.exit(1)

        print(f"Synthesizing storyboard for '{project}'...")
        res = synthesize_storyboard_from_script(script_content, project)
        print(f"Success! Generated {res['total_shots']} shots adhering to 16-32 char pacing.")
        print(f"Master CSV: {res['master_csv']}")

        # Complete task if active
        task = get_active_task()
        if task and task.get("project_title") == project:
            complete_task(task.get("task_id"), result_summary=f"Synthesized {res['total_shots']} shots.")
            print("Active task marked COMPLETED.")
        return

    if args.complete:
        task = get_active_task()
        if task:
            complete_task(task.get("task_id"), result_summary=args.summary)
            print(f"Task {task.get('task_id')} marked COMPLETED.")
        else:
            print("No active task to complete.")
        return

    parser.print_help()

if __name__ == "__main__":
    main()

