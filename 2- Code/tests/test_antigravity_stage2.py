import os
import sys
import json
import csv
import shutil
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from modules.antigravity_bridge import (
    dispatch_task,
    get_active_task,
    load_active_task_context,
    apply_antigravity_script_and_storyboard,
    cancel_active_task,
    complete_task,
    CURRENT_TASK_FILE
)
from web_ui import app, STATE

class TestAntigravityStage2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.test_title = "997- Test Antigravity Stage2 Studio"
        dirs = config.get_project_dirs(cls.test_title)
        cls.dirs = dirs
        cls.finals_dir = dirs["finals_dir"]
        cls.pm_dir = dirs["postmortem_dir"]
        os.makedirs(cls.finals_dir, exist_ok=True)
        os.makedirs(cls.pm_dir, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        try:
            if os.path.exists(cls.finals_dir):
                shutil.rmtree(cls.finals_dir, ignore_errors=True)
            if os.path.exists(cls.pm_dir):
                shutil.rmtree(cls.pm_dir, ignore_errors=True)
        except Exception:
            pass

    def setUp(self):
        cancel_active_task()

    def tearDown(self):
        cancel_active_task()

    def test_dispatch_task_repurposing(self):
        ref_transcript = "This is a sample reference transcript about ancient human hunting techniques and campfire survival."
        task = dispatch_task(
            task_type="SCRIPT_REPURPOSING_AND_STORYBOARD",
            project_title=self.test_title,
            reference_transcript=ref_transcript,
            niche="history"
        )
        self.assertEqual(task["status"], "PENDING_ANTIGRAVITY")
        self.assertEqual(task["project_title"], self.test_title)
        self.assertEqual(task["task_type"], "SCRIPT_REPURPOSING_AND_STORYBOARD")
        self.assertTrue(task["input_payload"]["is_repurposing"])
        self.assertGreater(task["input_payload"]["reference_word_count"], 0)

        # Verify load_active_task_context
        loaded = load_active_task_context()
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["task_id"], task["task_id"])
        self.assertIn("ancient human hunting", loaded["input_payload"]["reference_transcript_full"])

    def test_dispatch_task_creation_from_topic(self):
        task = dispatch_task(
            task_type="SCRIPT_CREATION_AND_STORYBOARD",
            project_title=self.test_title,
            user_prompt="Explain why we dream in a witty MinutePhysics comic style",
            niche="history"
        )
        self.assertEqual(task["task_type"], "SCRIPT_CREATION_AND_STORYBOARD")
        self.assertFalse(task["input_payload"]["is_repurposing"])
        self.assertIn("Explain why we dream", task["input_payload"]["user_prompt"])

    def test_apply_antigravity_script_and_storyboard(self):
        task = dispatch_task(
            task_type="SCRIPT_CREATION_AND_STORYBOARD",
            project_title=self.test_title,
            user_prompt="Test Prompt"
        )
        script = (
            "Later tonight, you will flick a tiny light switch and complain about the bulb. "
            "For ninety-nine percent of human history, that switch never existed. "
            "When the sun went down, predators with built-in night vision came out to play."
        )

        res = apply_antigravity_script_and_storyboard(
            project_title=self.test_title,
            script_text=script,
            niche="history",
            task_id=task["task_id"]
        )

        self.assertTrue(res["success"])
        self.assertGreater(res["total_shots"], 0)
        self.assertTrue(os.path.exists(res["master_csv"]))
        self.assertTrue(os.path.exists(res["all_prompts"]))
        self.assertTrue(os.path.exists(res["script_txt"]))

        # Verify task is marked completed
        active = get_active_task()
        self.assertEqual(active["status"], "COMPLETED")

    def test_api_antigravity_endpoints(self):
        # 1. Dispatch task
        dispatch_task(
            task_type="SCRIPT_REPURPOSING_AND_STORYBOARD",
            project_title=self.test_title,
            reference_transcript="Sample transcript text for testing the REST API."
        )

        # 2. Test GET /api/antigravity/task
        res = self.client.get("/api/antigravity/task")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIn("ANTIGRAVITY TASK", data["copyable_prompt"])
        self.assertEqual(data["task"]["project_title"], self.test_title)

        # 3. Test POST /api/antigravity/complete
        complete_res = self.client.post("/api/antigravity/complete", json={
            "project_title": self.test_title,
            "script_text": "A quick funny test script beat one. A quick funny test script beat two."
        })
        self.assertEqual(complete_res.status_code, 200)
        cdata = json.loads(complete_res.data)
        self.assertTrue(cdata["success"])
        self.assertGreater(cdata["total_shots"], 0)

    def test_cancel_active_task(self):
        dispatch_task(
            task_type="SCRIPT_CREATION_AND_STORYBOARD",
            project_title=self.test_title
        )
        self.assertEqual(get_active_task()["status"], "PENDING_ANTIGRAVITY")

        cancelled = cancel_active_task(reason="Test cancellation")
        self.assertTrue(cancelled)
        self.assertEqual(get_active_task()["status"], "CANCELLED")

if __name__ == "__main__":
    unittest.main()
