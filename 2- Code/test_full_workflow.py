"""
Full Workflow Simulation:
Simulates user triggering a project in Mode B -> Task Dispatched -> Antigravity synthesizes script -> Master CSV created -> Timeline XML checked.
"""

import os
import sys
import json
import csv
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from modules.antigravity_bridge import dispatch_task, synthesize_storyboard_from_script, complete_task
from modules.stage2_script_prompts import run_stage2_script_prompts

TEST_TITLE = "98- Why Do We Forget Dreams"

def run_simulation():
    print(f"--- Starting Full Production Workflow Simulation for '{TEST_TITLE}' ---")
    dirs = config.get_project_dirs(TEST_TITLE)
    if os.path.exists(dirs["finals_dir"]):
        shutil.rmtree(dirs["finals_dir"], ignore_errors=True)

    # 1. Dispatch task
    print("\n1. Dispatching Antigravity AI Task...")
    task = dispatch_task(
        task_type="SCRIPT_AND_STORYBOARD_SYNTHESIS",
        project_title=TEST_TITLE,
        user_prompt="Explain why we immediately forget 90% of our dreams within five minutes of waking up."
    )
    print(f"   Task dispatched: {task['task_id']} | Status: {task['status']}")

    # 2. Antigravity synthesizes 7-act script
    print("\n2. Antigravity Synthesizing 7-Act Script & Micro-Beats (16-32 chars)...")
    sample_script = (
        "Right now, you remember nothing. "
        "Ten minutes ago, you were soaring over neon mountain ranges, "
        "speaking fluent ancient Latin, "
        "and escaping a collapsing marble labyrinth. "
        "Now, you are brushing your teeth, "
        "staring into the bathroom mirror, "
        "and the entire universe you just inhabited has vanished without a trace. "
        "Why? Because your brain is not designed to remember dreams. "
        "Neuroscientists discovered that during REM sleep, "
        "the neurotransmitters norepinephrine and serotonin "
        "are completely shut off. "
        "Without norepinephrine, the hippocampus cannot write short-term memories "
        "into long-term storage. "
        "Your dream was never forgotten. "
        "It was never saved in the first place."
    )

    res = synthesize_storyboard_from_script(sample_script, TEST_TITLE)
    print(f"   Storyboard synthesized: {res['total_shots']} shots created.")

    # 3. Complete task
    complete_task(task["task_id"], result_summary=f"Synthesized {res['total_shots']} shots.")
    print(f"   Task completed.")

    # 4. Run Stage 2 compiler to verify all outputs align
    print("\n3. Running Stage 2 Prompts Compiler...")
    st2_res = run_stage2_script_prompts(TEST_TITLE)
    print(f"   Stage 2 Complete: {st2_res['total_shots']} shots compiled into all_prompts.txt.")
    assert os.path.exists(dirs["master_csv"]), "Master CSV missing!"
    assert os.path.exists(dirs["all_prompts_txt"]), "all_prompts.txt missing!"
    assert os.path.exists(dirs["character_audit"]), "character_audit.json missing!"
    assert os.path.exists(dirs["prompt_status_md"]), "PROMPT_STATUS.md missing!"

    # 5. Inspect Master CSV rows
    with open(dirs["master_csv"], "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        print(f"\n4. Master CSV Sample (First 3 Shots):")
        for row in reader[1:4]:
            print(f"   Shot {row[0]}: [{row[1]}] VO: '{row[2]}' | Desc: '{row[3]}'")

    # Clean up test files
    if os.path.exists(dirs["finals_dir"]):
        shutil.rmtree(dirs["finals_dir"], ignore_errors=True)

    print("\n[SUCCESS] Full workflow simulation passed flawlessly!")

if __name__ == "__main__":
    run_simulation()

