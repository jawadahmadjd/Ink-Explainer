import os
import sys
import unittest

CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from modules.srt_alignment import parse_srt, align_storyboard_with_srt

class TestSrtAlignment(unittest.TestCase):
    def test_parse_srt_string(self):
        srt_content = """1
00:00:01,000 --> 00:00:03,500
Hello world, this is a test.

2
00:00:03,500 --> 00:00:06,250
Second subtitle line here.
"""
        cues = parse_srt(srt_content)
        self.assertEqual(len(cues), 2)
        self.assertEqual(cues[0]["index"], 1)
        self.assertEqual(cues[0]["start_sec"], 1.0)
        self.assertEqual(cues[0]["end_sec"], 3.5)
        self.assertEqual(cues[0]["text"], "Hello world, this is a test.")
        self.assertEqual(cues[1]["start_sec"], 3.5)
        self.assertEqual(cues[1]["end_sec"], 6.25)

    def test_parse_real_srt_file(self):
        real_srt = os.path.join(
            os.path.dirname(CODE_DIR),
            "3- Finals", "history", "2- What Did Ancient Humans Do at Night", "Ancient Night SRT.srt"
        )
        if os.path.exists(real_srt):
            cues = parse_srt(real_srt)
            self.assertGreater(len(cues), 100)
            self.assertGreater(cues[-1]["end_sec"], 400.0)

if __name__ == "__main__":
    unittest.main()

