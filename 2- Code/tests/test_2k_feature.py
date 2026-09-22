import os
import sys
import json
import zipfile
import io
import csv
import shutil
import unittest
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from modules.image_resolution import (
    get_image_dimensions,
    ensure_2k_image,
    build_project_2k_zip
)
from modules.stage4_image_gen import download_flow_image_2k
from web_ui import app

class Test2KImageFeature(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.test_title = "999- Test 2K Studio"
        dirs = config.get_project_dirs(cls.test_title)
        cls.dirs = dirs
        cls.finals_dir = dirs["finals_dir"]
        cls.final_img_dir = dirs["final_images_dir"]
        os.makedirs(cls.final_img_dir, exist_ok=True)
        
        # Create 2 mock shots
        cls.shot1_path = os.path.join(cls.final_img_dir, "shot_001.jpg")
        cls.shot2_path = os.path.join(cls.final_img_dir, "shot_002.jpg")
        
        # Shot 1: 1376x768 (1K)
        im1 = Image.new("RGB", (1376, 768), (255, 255, 255))
        im1.save(cls.shot1_path, "JPEG")
        
        # Shot 2: 2752x1536 (2K Native)
        im2 = Image.new("RGB", (2752, 1536), (255, 255, 255))
        im2.save(cls.shot2_path, "JPEG")
        
        # Create storyboard_master.csv
        csv_path = dirs["master_csv"]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["shot_num", "timecode", "voiceover", "description", "prompt"])
            writer.writerow([1, "00:00 - 00:03", "Test shot 1", "desc 1", "prompt 1"])
            writer.writerow([2, "00:03 - 00:06", "Test shot 2", "desc 2", "prompt 2"])

    @classmethod
    def tearDownClass(cls):
        # Cleanup mock project
        try:
            if os.path.exists(cls.finals_dir):
                shutil.rmtree(cls.finals_dir)
        except Exception:
            pass

    def test_01_get_image_dimensions(self):
        w1, h1 = get_image_dimensions(self.shot1_path)
        self.assertEqual((w1, h1), (1376, 768))
        
        w2, h2 = get_image_dimensions(self.shot2_path)
        self.assertEqual((w2, h2), (2752, 1536))

    def test_02_ensure_2k_image(self):
        scratch_out = os.path.join(config.PROJECT_ROOT, "scratch", "test_unit_2k.jpg")
        os.makedirs(os.path.dirname(scratch_out), exist_ok=True)
        
        out_path, w, h = ensure_2k_image(self.shot1_path, scratch_out)
        self.assertTrue(os.path.exists(scratch_out))
        self.assertEqual((w, h), (2752, 1536))
        
        with Image.open(scratch_out) as im:
            self.assertEqual(im.size, (2752, 1536))
            self.assertEqual(im.format, "JPEG")

    def test_03_build_project_2k_zip(self):
        buf, zip_name, count = build_project_2k_zip(self.test_title)
        self.assertEqual(count, 2)
        self.assertTrue(zip_name.endswith("_2K_Images.zip"))
        
        # Verify zip structure
        with zipfile.ZipFile(buf, "r") as zf:
            namelist = zf.namelist()
            self.assertEqual(len(namelist), 2)
            self.assertIn("2K_Images/shot_001.jpg", namelist)
            self.assertIn("2K_Images/shot_002.jpg", namelist)
            
            with zf.open("2K_Images/shot_001.jpg") as img_file:
                im = Image.open(img_file)
                self.assertEqual(im.size, (2752, 1536))

    def test_04_api_shots_includes_2k_metadata(self):
        resp = self.client.get(f"/api/shots?title={self.test_title}")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("shots", data)
        shots = data["shots"]
        self.assertEqual(len(shots), 2)
        
        shot1 = next(s for s in shots if s["shot_num"] == 1)
        self.assertEqual(shot1["width"], 1376)
        self.assertEqual(shot1["height"], 768)
        self.assertFalse(shot1["is_2k"])
        self.assertEqual(shot1["res_label"], "1K")
        self.assertTrue(shot1["has_image"])
        
        shot2 = next(s for s in shots if s["shot_num"] == 2)
        self.assertEqual(shot2["width"], 2752)
        self.assertEqual(shot2["height"], 1536)
        self.assertTrue(shot2["is_2k"])
        self.assertEqual(shot2["res_label"], "2K")

    def test_05_api_download_shot_2k(self):
        resp = self.client.get(f"/api/shot/download-2k?title={self.test_title}&shot_num=1")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("image/jpeg", resp.content_type)
        self.assertIn("attachment", resp.headers.get("Content-Disposition", ""))
        self.assertIn("shot_001_2K.jpg", resp.headers.get("Content-Disposition", ""))
        
        # Verify downloaded image is scaled to 2K
        im = Image.open(io.BytesIO(resp.data))
        self.assertEqual(im.size, (2752, 1536))

    def test_06_api_download_all_2k_zip(self):
        resp = self.client.get(f"/api/project/download-all-2k?title={self.test_title}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("application/zip", resp.content_type)
        self.assertIn(".zip", resp.headers.get("Content-Disposition", ""))
        
        with zipfile.ZipFile(io.BytesIO(resp.data), "r") as zf:
            self.assertEqual(len(zf.namelist()), 2)

    def test_07_api_export_2k_folder(self):
        resp = self.client.post("/api/project/export-2k-folder", json={"title": self.test_title})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("count"), 2)
        folder = data.get("folder")
        self.assertTrue(os.path.isdir(folder))
        self.assertTrue(os.path.exists(os.path.join(folder, "shot_001.jpg")))
        self.assertTrue(os.path.exists(os.path.join(folder, "shot_002.jpg")))

    def test_08_download_flow_image_2k_callable(self):
        self.assertTrue(callable(download_flow_image_2k))

if __name__ == "__main__":
    unittest.main()

