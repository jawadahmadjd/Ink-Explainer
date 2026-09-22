"""
End-to-End Test Suite for Manual Prompts & Manual Timestamps (SRT File)
Tests both the backend engines, API routes, and Flask client end-to-end.
"""

import os
import sys
import json
import csv
import shutil
import unittest
import io

CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

import config
import web_ui
from modules.srt_alignment import parse_srt, align_storyboard_with_srt

TEST_PROJECT_NAME = "999- Automated Test Project"
TEST_NICHE = "history"

class TestPromptsAndSrtEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        web_ui.app.config["TESTING"] = True
        cls.client = web_ui.app.test_client()

        # Create a mock project for end-to-end testing
        dirs = config.get_project_dirs(TEST_PROJECT_NAME, niche=TEST_NICHE)
        cls.dirs = dirs
        os.makedirs(dirs["finals_dir"], exist_ok=True)
        os.makedirs(dirs["voiceovers_dir"], exist_ok=True)
        os.makedirs(dirs["final_images_dir"], exist_ok=True)

        # Initial storyboard CSV
        cls.csv_path = dirs["master_csv"]
        header = ["Shot #", "Time", "Spoken VO script", "Visual description", "Exact Prompt for google nano banana pro"]
        rows = [
            header,
            [1, "00:00.0 - 00:02.5", "Later tonight, you are going to walk into a room.", "Stick figure walking into a dark room.", "Minimalist 2D doodle stick figure walking into room."],
            [2, "00:02.5 - 00:05.0", "flick a light switch, and completely take for granted that the dark goes away.", "Stick figure flipping a switch.", "Minimalist 2D doodle stick figure flipping switch."],
            [3, "00:05.0 - 00:07.5", "For nearly all of human history, that was not an option.", "Primitive stick figure looking up at starry night sky.", "Minimalist 2D doodle stick figure under starry night sky."]
        ]
        with open(cls.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        # Create sample SRT file
        cls.sample_srt = """1
00:00:00,500 --> 00:00:02,800
Later tonight, you are going to walk into a room,

2
00:00:02,800 --> 00:00:05,400
flick a light switch, and completely take for granted that the dark goes away.

3
00:00:05,400 --> 00:00:08,200
For nearly all of human history, that was not an option.
"""
        cls.srt_path = os.path.join(dirs["voiceovers_dir"], "test_narration.srt")
        with open(cls.srt_path, "w", encoding="utf-8") as f:
            f.write(cls.sample_srt)

        # Set active project
        web_ui.STATE["project_title"] = f"{TEST_NICHE}/{TEST_PROJECT_NAME}"

    @classmethod
    def tearDownClass(cls):
        # Cleanup mock project
        if os.path.exists(cls.dirs["finals_dir"]):
            shutil.rmtree(cls.dirs["finals_dir"], ignore_errors=True)
        if os.path.exists(cls.dirs["postmortem_dir"]):
            shutil.rmtree(cls.dirs["postmortem_dir"], ignore_errors=True)

    def test_01_parse_srt(self):
        cues = parse_srt(self.sample_srt)
        self.assertEqual(len(cues), 3)
        self.assertEqual(cues[0]["start_sec"], 0.5)
        self.assertEqual(cues[0]["end_sec"], 2.8)
        self.assertEqual(cues[2]["end_sec"], 8.2)

    def test_02_align_storyboard_with_srt_engine(self):
        result = align_storyboard_with_srt(
            video_title=f"{TEST_NICHE}/{TEST_PROJECT_NAME}",
            srt_path_or_content=self.srt_path,
            fps=24
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["shots_count"], 3)
        self.assertEqual(result["srt_cues_count"], 3)
        self.assertTrue(result["zero_gap_overlap_verified"])

        # Check that shots_timing_alignment.json exists and is valid
        align_file = os.path.join(self.dirs["voiceovers_dir"], "shots_timing_alignment.json")
        self.assertTrue(os.path.exists(align_file))
        with open(align_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["start_frame"], 0)
        self.assertGreater(data[1]["start_frame"], data[0]["start_frame"])
        self.assertGreater(data[2]["start_frame"], data[1]["start_frame"])

    def test_03_api_get_prompts(self):
        res = self.client.get(f"/api/prompts/get?title={TEST_NICHE}/{TEST_PROJECT_NAME}")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["total_shots"], 3)
        self.assertIn("room", data["shots"][0]["prompt"])

    def test_04_api_save_manual_prompts_structured(self):
        updated_shots = [
            {
                "shot_num": 1,
                "prompt": "CUSTOM MANUAL PROMPT 1: Stick figure with glowing flashlight.",
                "voiceover": "Later tonight, walking into a room.",
                "description": "Flashlight in dark room",
                "timecode": "00:00.0 - 00:02.5"
            },
            {
                "shot_num": 2,
                "prompt": "CUSTOM MANUAL PROMPT 2: Stick figure pressing neon light switch.",
                "voiceover": "Flicking a switch.",
                "description": "Neon light switch",
                "timecode": "00:02.5 - 00:05.0"
            },
            {
                "shot_num": 3,
                "prompt": "CUSTOM MANUAL PROMPT 3: Campfire stick figure under ancient stars.",
                "voiceover": "Human history options.",
                "description": "Campfire under stars",
                "timecode": "00:05.0 - 00:08.2"
            }
        ]
        res = self.client.post(
            "/api/prompts/save-manual",
            json={"title": f"{TEST_NICHE}/{TEST_PROJECT_NAME}", "shots": updated_shots}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["total_shots"], 3)

        # Verify all_prompts.txt
        all_prompts_file = self.dirs["all_prompts_txt"]
        self.assertTrue(os.path.exists(all_prompts_file))
        with open(all_prompts_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("CUSTOM MANUAL PROMPT 1", content)
        self.assertIn("CUSTOM MANUAL PROMPT 3", content)

    def test_05_api_save_manual_prompts_bulk_text(self):
        bulk_text = """Shot 1: Bulk updated prompt 1 for testing.
Shot 2: Bulk updated prompt 2 for testing.
Shot 3: Bulk updated prompt 3 for testing.
Shot 4: Added shot 4 from bulk text.
"""
        res = self.client.post(
            "/api/prompts/save-manual",
            json={"title": f"{TEST_NICHE}/{TEST_PROJECT_NAME}", "raw_prompts": bulk_text}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["total_shots"], 4)

    def test_06_api_inspect_srt(self):
        res = self.client.get(f"/api/timestamps/inspect-srt?title={TEST_NICHE}/{TEST_PROJECT_NAME}")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["has_srt"])
        self.assertEqual(data["default_file"]["cue_count"], 3)

    def test_07_api_upload_srt(self):
        new_srt_bytes = io.BytesIO(self.sample_srt.encode("utf-8"))
        res = self.client.post(
            "/api/timestamps/upload-srt",
            data={
                "title": f"{TEST_NICHE}/{TEST_PROJECT_NAME}",
                "srt_file": (new_srt_bytes, "uploaded_subtitles.srt")
            },
            content_type="multipart/form-data"
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["cue_count"], 3)
        self.assertTrue(os.path.exists(data["file_path"]))

    def test_08_api_align_srt(self):
        res = self.client.post(
            "/api/timestamps/align-srt",
            json={
                "title": f"{TEST_NICHE}/{TEST_PROJECT_NAME}",
                "srt_path": self.srt_path,
                "fps": 24
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["result"]["zero_gap_overlap_verified"])

    def test_09_frontend_html_elements_present(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        # Mode A and Mode B
        self.assertIn('id="tabModeLink"', html)
        self.assertIn('id="tabModePrompt"', html)
        self.assertIn('id="panelModeLink"', html)
        self.assertIn('id="panelModePrompt"', html)
        self.assertIn('id="manualTitle"', html)
        self.assertIn('id="manualPrompt"', html)
        self.assertIn('id="btnStartFromPrompt"', html)

        # Stage buttons
        self.assertIn('id="btnManualPrompts"', html)
        self.assertIn('id="btnOpenManualSrtModal"', html)

        # Modals
        self.assertIn('id="manualPromptsModalBackdrop"', html)
        self.assertIn('id="manualSrtModalBackdrop"', html)
        self.assertIn('id="btnSaveManualPrompts"', html)
        self.assertIn('id="btnProceedManualSrt"', html)

        # Optional SRT attachment in Manual VO modal
        self.assertIn('id="manualVoSrtPathInput"', html)
        self.assertIn('id="manualVoSrtFileInput"', html)

if __name__ == "__main__":
    unittest.main()

