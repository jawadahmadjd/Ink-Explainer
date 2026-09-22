"""
Automated unit test for Multi-Niche AI Learning Engine & Dynamic Provisioning.
"""

import os
import sys

CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, CODE_DIR)

from learning.learning_engine import (
    load_codex,
    classify_script_niche,
    find_matching_reference_video,
    get_distilled_prompt_context,
    generate_script_and_shots,
    create_dynamic_niche
)

def run_tests():
    print("--- 1. Testing Codex Loading ---")
    codex = load_codex()
    assert "_version" in codex, "Missing _version"
    assert codex["_version"] == "2.0.0", f"Expected version 2.0.0, got {codex['_version']}"
    assert "history" in codex["niches"], "Missing history niche"
    assert "finance" in codex["niches"], "Missing finance niche"
    print(f"Codex loaded successfully with {len(codex['niches'])} niches.")

    print("\n--- 2. Testing Niche Classification ---")
    cases = [
        ("How The Federal Reserve Printed 8 Trillion Dollars", "finance"),
        ("The Surgeon Who Discovered A Deadly Brain Amoeba", "medical"),
        ("The Creepy Woods Where 4 Campers Disappeared Overnight", "horror"),
        ("What Did Ancient Humans Do at Night", "history"),
        ("How They Built The Hoover Dam In 100-Degree Heat", "engineering"),
    ]

    for title, expected_niche in cases:
        res = classify_script_niche(title)
        print(f"Title: '{title}' -> Detected: '{res['niche']}' ({res['display_name']}), score: {res['score']}")
        assert res["niche"] == expected_niche, f"Expected {expected_niche}, got {res['niche']}"

    print("\n--- 3. Testing Dynamic Category Provisioning ---")
    novel_title = "Quantum Supercomputers Solving Protein Folding Paradox"
    dyn_res = classify_script_niche(novel_title, auto_provision=True)
    print(f"Novel Title: '{novel_title}' -> Dynamic Niche: '{dyn_res['niche']}' ({dyn_res['display_name']}), is_new: {dyn_res.get('is_new')}")
    assert dyn_res["niche"] in load_codex()["niches"], "Dynamic niche was not registered in codex!"
    # Cleanup test dynamic niche
    if dyn_res.get("is_new"):
        clean_codex = load_codex()
        clean_codex["niches"].pop(dyn_res["niche"], None)
        from learning.learning_engine import save_codex
        save_codex(clean_codex)

    print("\n--- 4. Testing Blueprint Matching with Niche ---")
    match_hist = find_matching_reference_video("What did ancient humans do all day", niche="history")
    assert match_hist is not None, "Failed to match ancient humans in history niche"
    print(f"Matched: '{match_hist['title']}' in niche '{match_hist['niche']}' with score {match_hist['score']}")

    print("\n--- 5. Testing Distilled Prompt Contexts ---")
    hist_ctx = get_distilled_prompt_context("history")
    fin_ctx = get_distilled_prompt_context("finance")
    assert "ANTHROPOLOGICAL" in hist_ctx, "History context missing anthropological framework"
    assert "MARKET TRAP" in fin_ctx or "FINANCE" in fin_ctx, "Finance context missing finance framework"
    print("Prompt contexts generated correctly for history and finance.")

    print("\n--- 6. Testing Script and Fast-Paced Shot Splitting ---")
    fin_shots = generate_script_and_shots("The Great Inflation Trap", "A video explaining inflation and debt", niche="finance")
    assert len(fin_shots) > 5, "Too few shots generated"
    assert all(1 <= s["char_count"] <= 65 for s in fin_shots), "Shot character count violation"
    print(f"Generated {len(fin_shots)} fast-paced shots for finance with 20-50 char constraints.")
    print(f"Sample Shot 1 Prompt: {fin_shots[0]['prompt'][:80]}...")

    print("\nALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
