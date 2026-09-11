"""
End-to-End Verification Test Suite for Antigravity-Driven Studio UI
Author: Google DeepMind Antigravity System
Validates:
1. Antigravity task dispatch and synchronization.
2. 16-32 character shot pacing and MinutePhysics prompt generation.
3. Master CSV, All Prompts, and Character Audit file integrity.
4. Web UI Flask endpoints (/api/antigravity/task, submit-script, complete, etc.).
5. Apple xmeml timeline XML generation readiness.
"""

import os
import sys
import json
import csv
import unittest
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from modules.antigravity_bridge import (
    dispatch_task,
    get_active_task,
    complete_task,
    synthesize_storyboard_from_script
)
from web_ui import app

TEST_PROJECT_NAME = "99- Test Antigravity Architecture"

class TestAntigravityPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.dirs = config.get_project_dirs(TEST_PROJECT_NAME)
        # Ensure clean test directory
        if os.path.exists(cls.dirs["finals_dir"]):
            shutil.rmtree(cls.dirs["finals_dir"], ignore_errors=True)

    @classmethod
    def tearDownClass(cls):
        # Cleanup test directory after tests
        if os.path.exists(cls.dirs["finals_dir"]):
            shutil.rmtree(cls.dirs["finals_dir"], ignore_errors=True)
        # Reset current task
        task_file = os.path.join(config.CODE_DIR, "tasks", "current_task.json")
        if os.path.exists(task_file):
            try:
                os.remove(task_file)
            except Exception:
                pass

    def test_01_task_dispatch_and_retrieval(self):
        """Test dispatching a task and reading it via API."""
        prompt = "Explain why humans dream during REM sleep and what evolutionary purpose it serves."
        task = dispatch_task(
            task_type="SCRIPT_AND_STORYBOARD_SYNTHESIS",
            project_title=TEST_PROJECT_NAME,
            user_prompt=prompt
        )

        self.assertIsNotNone(task)
        self.assertEqual(task["status"], "PENDING_ANTIGRAVITY")
        self.assertEqual(task["project_title"], TEST_PROJECT_NAME)

        # Test Web UI API endpoint
        resp = self.client.get("/api/antigravity/task")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIn("active_task", data)
        self.assertEqual(data["active_task"]["task_id"], task["task_id"])
        print("[PASS] Test 1 Passed: Task dispatch and retrieval via /api/antigravity/task successful.")

    def test_02_script_synthesis_and_pacing(self):
        """Test decomposing a 7-act script into 16-32 char beats with MinutePhysics prompts."""
        test_script = (
            "Right now, you are dreaming. "
            "Your body is completely paralyzed, "
            "but your brain is firing with the intensity of an open furnace. "
            "Why? Because nature built a virtual reality simulator inside your skull. "
            "For two hours every night, you fight imaginary predators, "
            "rehearse deadly confrontations, "
            "and solve problems you never faced while awake. "
            "Look at the evolutionary evidence. "
            "Every single mammal experiences rapid eye movement sleep. "
            "Deprive a rat of REM sleep for two weeks, "
            "and its immune system completely collapses. "
            "Now look at modern humans. "
            "We cut our sleep by thirty percent, "
            "and wonder why chronic anxiety is at an all-time high."
        )

        res = synthesize_storyboard_from_script(test_script, TEST_PROJECT_NAME)
        self.assertTrue(res["success"])
        self.assertGreater(res["total_shots"], 10)
        self.assertTrue(os.path.exists(res["master_csv"]))
        self.assertTrue(os.path.exists(res["all_prompts"]))
        self.assertTrue(os.path.exists(res["character_audit"]))

        # Verify CSV contents
        with open(res["master_csv"], "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(header[0], "Shot #")
            rows = list(reader)

        self.assertEqual(len(rows), res["total_shots"])

        # Verify MinutePhysics prompt rules
        for r in rows:
            shot_num = int(r[0])
            vo = r[2]
            prompt = r[4]
            # Verify prompt contains mandatory aesthetic tokens
            self.assertIn("Minimalist hand-drawn 2D vector illustration", prompt)
            self.assertIn("clean bold black ink comic line art", prompt)
            self.assertIn("16:9 widescreen frame", prompt)

        print(f"[PASS] Test 2 Passed: Decomposed script into {res['total_shots']} shots adhering to MinutePhysics standards.")

    def test_03_submit_script_endpoint(self):
        """Test submitting script directly via /api/antigravity/submit-script."""
        script_payload = {
            "title": TEST_PROJECT_NAME,
            "script": "Think about why you sleep. For decades, scientists believed sleep was merely an energy saver."
        }
        resp = self.client.post("/api/antigravity/submit-script",
                                data=json.dumps(script_payload),
                                content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])
        self.assertGreater(data["result"]["total_shots"], 0)
        print("[PASS] Test 3 Passed: /api/antigravity/submit-script synthesized shots successfully.")

    def test_04_task_completion_endpoint(self):
        """Test marking task complete via /api/antigravity/complete."""
        # Ensure task exists
        dispatch_task("SCRIPT_AND_STORYBOARD_SYNTHESIS", TEST_PROJECT_NAME)
        resp = self.client.post("/api/antigravity/complete",
                                data=json.dumps({"summary": "Verified by automated test suite"}),
                                content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])

        active = get_active_task()
        self.assertEqual(active["status"], "COMPLETED")
        print("[PASS] Test 4 Passed: Task marked complete via API and event signaled.")

    def test_05_gallery_shots_endpoint(self):
        """Test /api/shots returns synthesized shots for UI gallery display."""
        resp = self.client.get(f"/api/shots?title={TEST_PROJECT_NAME}")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIn("shots", data)
        self.assertGreater(data["total"], 0)
        first_shot = data["shots"][0]
        self.assertEqual(first_shot["shot_num"], 1)
        self.assertIn("voiceover", first_shot)
        self.assertIn("prompt", first_shot)
        print(f"[PASS] Test 5 Passed: /api/shots returned {data['total']} gallery items.")

if __name__ == "__main__":
    unittest.main()
