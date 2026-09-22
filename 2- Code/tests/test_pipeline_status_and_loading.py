import os
import sys
import unittest
import json

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, CODE_DIR)

import web_ui
from modules.stage4_image_gen import is_stage4_paused, pause_stage4, resume_stage4

class TestPipelineStatusAndLoading(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = web_ui.app.test_client()

    def setUp(self):
        # Reset STATE
        web_ui.STATE["state"] = "IDLE"
        web_ui.STATE["step1"] = "WAITING"
        web_ui.STATE["step2"] = "WAITING"
        web_ui.STATE["step3"] = "WAITING"
        web_ui.STATE["step4"] = "WAITING"
        web_ui.STATE["step6"] = "WAITING"
        web_ui.STATE["pause_requested"] = False
        web_ui.STATE["task_description"] = "Clean canvas ready."
        web_ui.PAUSE_EVENT.set()
        resume_stage4()

    def test_01_status_structure_and_defaults(self):
        """Verify /api/status returns the required telemetry fields for button & stage control."""
        res = self.client.get("/api/status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        
        self.assertIn("is_running", data)
        self.assertIn("is_paused", data)
        self.assertIn("active_stage", data)
        self.assertIn("paused_stage", data)
        self.assertIn("current_action", data)
        
        self.assertFalse(data["is_running"])
        self.assertFalse(data["is_paused"])
        self.assertIsNone(data["active_stage"])
        self.assertIsNone(data["paused_stage"])
        self.assertEqual(data["current_action"], "Idle / Ready")

    def test_02_pause_and_resume_pipeline(self):
        """Verify pipeline pause and resume endpoints toggle state and flags."""
        res = self.client.post("/api/pause")
        self.assertEqual(res.status_code, 200)
        p_data = res.get_json()
        self.assertTrue(p_data["success"])
        
        st_res = self.client.get("/api/status")
        st = st_res.get_json()
        self.assertTrue(web_ui.STATE["pause_requested"])

        # Resume
        r_res = self.client.post("/api/resume")
        self.assertEqual(r_res.status_code, 200)
        self.assertFalse(web_ui.STATE["pause_requested"])

    def test_03_stage4_pause_and_resume(self):
        """Verify Stage 4 local pause/resume triggers is_stage4_paused cleanly."""
        res_pause = self.client.post("/api/stage4/pause")
        self.assertEqual(res_pause.status_code, 200)
        self.assertTrue(is_stage4_paused())

        res_resume = self.client.post("/api/stage4/resume")
        self.assertEqual(res_resume.status_code, 200)
        self.assertFalse(is_stage4_paused())

    def test_04_status_active_and_paused_stage_telemetry(self):
        """Verify that get_status accurately maps executing and paused stages."""
        # Stage 1 Running
        web_ui.STATE["state"] = "RUNNING_POSTMORTEM"
        web_ui.STATE["step1"] = "RUNNING"
        st = self.client.get("/api/status").get_json()
        self.assertTrue(st["is_running"])
        self.assertEqual(st["active_stage"], 1)

        # Stage 2 Running
        web_ui.STATE["state"] = "RUNNING_SCRIPT"
        web_ui.STATE["step1"] = "COMPLETED"
        web_ui.STATE["step2"] = "RUNNING"
        st = self.client.get("/api/status").get_json()
        self.assertTrue(st["is_running"])
        self.assertEqual(st["active_stage"], 2)

        # Stage 2 Paused for review
        web_ui.STATE["state"] = "PAUSED_AFTER_STAGE_2"
        web_ui.STATE["step2"] = "COMPLETED"
        st = self.client.get("/api/status").get_json()
        self.assertFalse(st["is_running"])
        self.assertTrue(st["is_paused"])
        self.assertEqual(st["paused_stage"], 2)

        # Stage 4 Paused Images
        web_ui.STATE["state"] = "PAUSED_IMAGES"
        web_ui.STATE["step4"] = "PAUSED"
        st = self.client.get("/api/status").get_json()
        self.assertTrue(st["is_paused"])
        self.assertEqual(st["paused_stage"], 4)

        # Reset
        web_ui.STATE["state"] = "IDLE"
        web_ui.STATE["step4"] = "WAITING"
        st = self.client.get("/api/status").get_json()
        self.assertFalse(st["is_running"])
        self.assertFalse(st["is_paused"])

    def test_05_frontend_html_elements_and_css_present(self):
        """Verify that index.html contains all new CSS classes, banner elements, and JS functions."""
        html_path = os.path.join(CODE_DIR, "templates", "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        # CSS classes
        self.assertIn(".btn-spinner", html)
        self.assertIn(".btn-loading", html)
        self.assertIn(".is-running", html)
        self.assertIn(".is-paused", html)
        self.assertIn(".is-resume-ready", html)
        self.assertIn(".toast-container", html)
        self.assertIn(".toast", html)

        # HTML elements
        self.assertIn('id="liveExecutionPill"', html)
        self.assertIn('id="backendFailureBanner"', html)
        self.assertIn('id="backendFailureMsg"', html)
        self.assertIn('id="btnPauseStage4"', html)
        self.assertIn('id="btnResumeStage4"', html)

        # JS functions
        self.assertIn("function showToast(", html)
        self.assertIn("function showBackendError(", html)
        self.assertIn("function dismissBackendError(", html)
        self.assertIn("function setButtonLoading(", html)
        self.assertIn("function executeWithLoading(", html)

if __name__ == "__main__":
    unittest.main()

