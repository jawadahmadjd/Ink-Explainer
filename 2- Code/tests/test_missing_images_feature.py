import os
import sys
import json
import csv
import shutil
import unittest
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from modules.stage4_image_gen import (
    get_missing_shots,
    has_valid_final_image,
    run_stage4_image_gen,
    update_production_status,
    update_prompt_status_md
)
from web_ui import app, STATE

class TestMissingImagesFeature(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.test_title = "998- Test Missing Feature Studio"
        dirs = config.get_project_dirs(cls.test_title)
        cls.dirs = dirs
        cls.finals_dir = dirs["finals_dir"]
        cls.final_img_dir = dirs["final_images_dir"]
        os.makedirs(cls.final_img_dir, exist_ok=True)

        # Create master CSV with 5 shots
        csv_path = dirs["master_csv"]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["shot_num", "timecode", "voiceover", "description", "prompt"])
            for i in range(1, 6):
                writer.writerow([i, f"00:0{i} - 00:0{i+1}", f"Test voiceover {i}", f"Description {i}", f"Stick figure prompt {i}"])

        # Create character_audit.json mock file
        audit_path = dirs["character_audit"]
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump([{"shot_num": i, "category": "VALID_STICK_FIGURE"} for i in range(1, 6)], f)

    @classmethod
    def tearDownClass(cls):
        try:
            if os.path.exists(cls.finals_dir):
                shutil.rmtree(cls.finals_dir)
        except Exception:
            pass

    def setUp(self):
        # Clean final image directory before each test
        for f in os.listdir(self.final_img_dir):
            p = os.path.join(self.final_img_dir, f)
            if os.path.isfile(p):
                os.remove(p)

    def _create_mock_image(self, shot_num: int, ext: str = ".jpg", zero_byte: bool = False):
        path = os.path.join(self.final_img_dir, f"shot_{shot_num:03d}{ext}")
        if zero_byte:
            with open(path, "wb") as f:
                pass
        else:
            im = Image.new("RGB", (100, 100), (255, 255, 255))
            fmt = "PNG" if ext == ".png" else "JPEG"
            im.save(path, fmt)
        return path

    def tearDown(self):
        from modules.stage4_image_gen import cancel_stage4
        from web_ui import STATE
        cancel_stage4()
        STATE["state"] = "IDLE"
        STATE["step4"] = "WAITING"
        STATE["project_title"] = ""

    def test_has_valid_final_image(self):
        # When no image exists
        self.assertFalse(has_valid_final_image(self.final_img_dir, 1))

        # When a 0-byte file exists
        self._create_mock_image(1, zero_byte=True)
        self.assertFalse(has_valid_final_image(self.final_img_dir, 1))

        # When valid jpg exists
        self._create_mock_image(1, ext=".jpg", zero_byte=False)
        self.assertTrue(has_valid_final_image(self.final_img_dir, 1))

        # When valid png exists
        self._create_mock_image(2, ext=".png", zero_byte=False)
        self.assertTrue(has_valid_final_image(self.final_img_dir, 2))

    def test_get_missing_shots_all_present(self):
        for i in range(1, 6):
            self._create_mock_image(i)
        missing = get_missing_shots(self.test_title)
        self.assertEqual(missing, [])

    def test_get_missing_shots_with_gaps_and_zero_byte(self):
        # Generate shots 1 and 3 only
        self._create_mock_image(1)
        self._create_mock_image(3)
        # Create zero-byte corrupt file for shot 5
        self._create_mock_image(5, zero_byte=True)

        # Expected missing: 2, 4, 5
        missing = get_missing_shots(self.test_title)
        self.assertEqual(missing, [2, 4, 5])

        # Test with range filter
        missing_range1 = get_missing_shots(self.test_title, start_shot=1, end_shot=3)
        self.assertEqual(missing_range1, [2])

        missing_range2 = get_missing_shots(self.test_title, start_shot=3, end_shot=5)
        self.assertEqual(missing_range2, [4, 5])

    def test_api_get_missing_shots_endpoint(self):
        self._create_mock_image(1)
        self._create_mock_image(3)

        res = self.client.get(f"/api/stage4/missing-shots?title={self.test_title}")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["total_shots"], 5)
        self.assertEqual(data["missing_count"], 3)
        self.assertEqual(data["missing_shots"], [2, 4, 5])
        self.assertEqual(data["generated_shots"], 2)

    from unittest.mock import patch

    @patch("web_ui.run_stage4_image_gen")
    def test_api_generate_missing_stage4_with_missing(self, mock_gen):
        mock_gen.return_value = {"completed_in_run": 3}
        self._create_mock_image(1)
        self._create_mock_image(2)

        res = self.client.post("/api/stage4/generate-missing", json={
            "folder_name": self.test_title,
            "start_shot": 1,
            "end_shot": 5,
            "model": "Nano Banana Pro",
            "resolution": "2k"
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["missing_count"], 3)
        self.assertEqual(data["missing_shots"], [3, 4, 5])

    def test_api_generate_missing_stage4_zero_missing(self):
        for i in range(1, 6):
            self._create_mock_image(i)

        res = self.client.post("/api/stage4/generate-missing", json={
            "folder_name": self.test_title
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["missing_count"], 0)
        self.assertEqual(data["missing_shots"], [])
        self.assertIn("already have images", data["message"])

    @patch("web_ui.run_stage4_image_gen")
    def test_api_run_range_with_only_missing_flag(self, mock_gen):
        mock_gen.return_value = {"completed_in_run": 4}
        self._create_mock_image(1)

        res = self.client.post("/api/stage4/run-range", json={
            "folder_name": self.test_title,
            "start_shot": 1,
            "end_shot": 5,
            "only_missing": True,
            "model": "Nano Banana Pro",
            "resolution": "2k"
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])

    def test_real_project_missing_images_detection(self):
        # Validate against actual project in 3- Finals
        real_title = "3- What Did Ancient Humans Do When It Rained All Week"
        dirs = config.get_project_dirs(real_title)
        if os.path.exists(dirs["master_csv"]):
            missing = get_missing_shots(real_title)
            self.assertIsInstance(missing, list)

            res = self.client.get(f"/api/stage4/missing-shots?title={real_title}")
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertEqual(data["total_shots"], 215)
            self.assertEqual(data["missing_count"], len(missing))
            self.assertEqual(data["generated_shots"], 215 - len(missing))
            self.assertEqual(data["missing_shots"], missing)

    def test_update_production_status(self):
        update_production_status(
            finals_dir=self.finals_dir,
            shot_num=3,
            total_shots=5,
            completed_count=2,
            status="INJECTING",
            note="Injecting prompt for shot 3",
            active_model="Nano Banana Pro",
            last_image_info={"shot_num": 2, "filename": "shot_002.jpg", "score": 9.5}
        )
        status_path = os.path.join(self.finals_dir, "production_status.json")
        self.assertTrue(os.path.exists(status_path))
        with open(status_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["current_shot"], 3)
        self.assertEqual(data["total_shots"], 5)
        self.assertEqual(data["completed_count"], 2)
        self.assertEqual(data["status"], "INJECTING")
        self.assertEqual(data["active_model"], "Nano Banana Pro")
        self.assertEqual(data["last_image"]["shot_num"], 2)

    def test_update_prompt_status_md(self):
        rows = [
            ["1", "00:01 - 00:02", "VO 1", "Desc 1", "Prompt 1"],
            ["2", "00:02 - 00:03", "VO 2", "Desc 2", "Prompt 2"]
        ]
        self._create_mock_image(1)
        update_prompt_status_md(
            video_title=self.test_title,
            finals_dir=self.finals_dir,
            total_shots=2,
            completed_count=1,
            rows=rows
        )
        md_path = os.path.join(self.finals_dir, "PROMPT_STATUS.md")
        self.assertTrue(os.path.exists(md_path))
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("# Storyboard Generation Live Status Tracker", content)
        self.assertIn("Overall Progress", content)
        self.assertIn("50.0%", content)
        self.assertIn("| #001 | 00:01 - 00:02 |", content)

    def test_run_stage4_status_callback_all_complete(self):
        for i in range(1, 6):
            self._create_mock_image(i)
        events = []
        res = run_stage4_image_gen(
            video_title=self.test_title,
            start_shot=1,
            end_shot=5,
            only_missing=True,
            status_callback=lambda evt: events.append(evt)
        )
        self.assertEqual(res["completed_in_run"], 0)
        self.assertTrue(len(events) >= 1)
        last_evt = events[-1]
        self.assertEqual(last_evt["phase"], "COMPLETE")
        self.assertEqual(last_evt["completed_project_shots"], 5)
        self.assertEqual(last_evt["total_project_shots"], 5)

    def test_api_stage4_production_status_endpoint(self):
        # Update status file
        update_production_status(
            finals_dir=self.finals_dir,
            shot_num=4,
            total_shots=5,
            completed_count=3,
            status="SCORING",
            note="Evaluating candidate images"
        )
        STATE["stage4_progress"] = {
            "active": True,
            "phase": "SCORING",
            "current_shot": 4,
            "total_shots": 5,
            "completed_shots": 3,
            "percent": 60.0,
            "status_text": "Scoring candidates"
        }

        res = self.client.get(f"/api/stage4/production-status?title={self.test_title}")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIsNotNone(data["production_status"])
        self.assertEqual(data["production_status"]["current_shot"], 4)
        self.assertEqual(data["stage4_progress"]["phase"], "SCORING")


if __name__ == "__main__":
    unittest.main()
