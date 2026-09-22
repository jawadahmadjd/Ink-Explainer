import os
import sys
import json
import csv
import shutil
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from modules.gemini_stage2 import (
    validate_gemini_key,
    format_stick_figure_prompt,
    is_likely_character_shot,
    repurpose_transcript_with_gemini,
    create_script_from_prompt_with_gemini,
    generate_storyboard_prompts_with_gemini,
    run_gemini_stage2
)
from modules.stage2_script_prompts import run_stage2_script_prompts
from web_ui import app

class TestGeminiStage2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.test_title = "996- Test Gemini Stage2 Autonomous Studio"
        cls.dirs = config.get_project_dirs(cls.test_title)
        cls.finals_dir = cls.dirs["finals_dir"]
        cls.pm_dir = cls.dirs["postmortem_dir"]
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

    def test_validate_gemini_key_empty(self):
        is_valid, msg, models = validate_gemini_key("")
        self.assertFalse(is_valid)
        self.assertIn("No Gemini API key", msg)
        self.assertEqual(models, [])

    @patch("google.generativeai.list_models")
    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_validate_gemini_key_success(self, mock_cfg, mock_model_cls, mock_list):
        # Mock model objects
        m1 = MagicMock()
        m1.name = "models/gemini-2.5-flash"
        m1.supported_generation_methods = ["generateContent"]
        mock_list.return_value = [m1]

        mock_inst = MagicMock()
        resp = MagicMock()
        resp.text = "Pong"
        mock_inst.generate_content.return_value = resp
        mock_model_cls.return_value = mock_inst

        is_valid, msg, models = validate_gemini_key("fake_valid_key_12345")
        self.assertTrue(is_valid)
        self.assertIn("gemini-2.5-flash", models)

    def test_format_stick_figure_prompt(self):
        char_prompt = format_stick_figure_prompt("A hunter staring at a campfire in disbelief", is_character=True, niche="history")
        self.assertIn("MinutePhysics", char_prompt)
        self.assertIn("white circle heads", char_prompt)
        self.assertIn("16:9 widescreen", char_prompt)
        self.assertIn("A hunter staring at a campfire", char_prompt)

        env_prompt = format_stick_figure_prompt("Map of ancient migration routes across continents", is_character=False, niche="history")
        self.assertIn("MinutePhysics", env_prompt)
        self.assertIn("Detailed illustration of:", env_prompt)

    def test_is_likely_character_shot(self):
        self.assertTrue(is_likely_character_shot("The hunter waited quietly", "A person crouches behind a rock"))
        self.assertFalse(is_likely_character_shot("The geological formation took millions of years", "A canyon with flowing river"))

    @patch("modules.gemini_stage2.get_best_working_model")
    @patch("modules.gemini_stage2.get_gemini_client")
    def test_repurpose_transcript_with_gemini(self, mock_get_client, mock_best_model):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_model = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = "Act 1: The Paradox Hook\n**Why did our ancestors run for hours just to eat roots?** It sounds ridiculous to someone ordering Uber Eats."
        mock_model.generate_content.return_value = mock_resp
        mock_best_model.return_value = (mock_model, "gemini-2.5-flash")

        result = repurpose_transcript_with_gemini(
            raw_transcript="Raw history text about endurance running.",
            video_title=self.test_title,
            niche="history",
            api_key="mock_key"
        )
        self.assertNotIn("Act 1:", result)
        self.assertNotIn("**", result)
        self.assertIn("ancestors run for hours", result)

    @patch("modules.gemini_stage2.get_best_working_model")
    @patch("modules.gemini_stage2.get_gemini_client")
    def test_generate_storyboard_prompts_json(self, mock_get_client, mock_best_model):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_model = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = json.dumps([
            {
                "shot_num": 1,
                "vo": "Why did our ancestors do this?",
                "description": "Caveman scratching head while staring at mammoth",
                "prompt": "Minimalist hand-drawn 2D vector stick figure caveman scratching head."
            },
            {
                "shot_num": 2,
                "vo": "Because hunger is a powerful motivator.",
                "description": "Stick figure stomach growling with empty thought bubble",
                "prompt": "Minimalist hand-drawn 2D vector stick figure with empty stomach."
            }
        ])
        mock_model.generate_content.return_value = mock_resp
        mock_best_model.return_value = (mock_model, "gemini-2.5-flash")

        shots = generate_storyboard_prompts_with_gemini(
            script_text="Why did our ancestors do this? Because hunger is a powerful motivator.",
            project_title=self.test_title,
            niche="history",
            api_key="mock_key"
        )
        self.assertEqual(len(shots), 2)
        self.assertEqual(shots[0]["shot_num"], 1)
        self.assertIn("ancestors", shots[0]["voiceover"])

    @patch("modules.gemini_stage2.repurpose_transcript_with_gemini")
    @patch("modules.gemini_stage2.generate_storyboard_prompts_with_gemini")
    def test_run_gemini_stage2_e2e(self, mock_gen_shots, mock_repurpose):
        mock_repurpose.return_value = "This is a full viral explainer script about human evolution and fire."
        mock_gen_shots.return_value = [
            {
                "shot_num": 1,
                "voiceover": "Humans discovered fire thousands of years ago.",
                "description": "Stick figure holding torch with surprised face",
                "prompt": "Minimalist 2D vector illustration of stick figure with torch."
            },
            {
                "shot_num": 2,
                "voiceover": "And instantly burned their dinner.",
                "description": "Stick figure looking at charred meat sadly",
                "prompt": "Minimalist 2D vector illustration of stick figure looking at burnt meat."
            }
        ]

        # Write clean_transcript.txt in postmortem dir
        with open(os.path.join(self.pm_dir, "clean_transcript.txt"), "w", encoding="utf-8") as f:
            f.write("Raw transcript about fire.")

        res = run_gemini_stage2(self.test_title, force_regenerate=True)
        self.assertTrue(res["success"])
        self.assertEqual(res["total_shots"], 2)

        # Verify all 5 production artifacts exist
        self.assertTrue(os.path.exists(self.dirs["master_csv"]))
        self.assertTrue(os.path.exists(self.dirs["script_txt"]))
        self.assertTrue(os.path.exists(self.dirs["all_prompts_txt"]))
        self.assertTrue(os.path.exists(self.dirs["character_audit"]))
        self.assertTrue(os.path.exists(self.dirs["prompt_status_md"]))

        # Verify master CSV content
        with open(self.dirs["master_csv"], "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            self.assertEqual(len(reader), 3) # Header + 2 shots
            self.assertEqual(reader[0][0], "Shot #")

        # Verify script txt content
        with open(self.dirs["script_txt"], "r", encoding="utf-8") as f:
            vo_content = f.read()
            self.assertIn("Humans discovered fire", vo_content)
            self.assertIn("burned their dinner", vo_content)

    def test_api_gemini_endpoints(self):
        # 1. GET /api/gemini/status
        res = self.client.get("/api/gemini/status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("configured", data)

        # 2. POST /api/gemini/key (updating key)
        res_post = self.client.post("/api/gemini/key", json={"key": "test_mock_gemini_key_abc123"})
        self.assertEqual(res_post.status_code, 200)
        post_data = res_post.get_json()
        self.assertTrue(post_data["success"])
        self.assertTrue(post_data["configured"])

if __name__ == "__main__":
    unittest.main()
