import csv
import json
import re

# Load the full script from clean_ai_voiceover_script.txt
with open("clean_ai_voiceover_script.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Let's see: how many words and characters is it?
print(f"Raw script characters: {len(text)}, words: {len(text.split())}")

# If we want exactly ~11,200 characters (11m 12s at 1000 chars = 60s):
# Let's inspect the target
target_chars = 11200
target_shots = 350
avg_chars_per_shot = target_chars / target_shots # ~32 chars
print(f"Target avg chars per shot: {avg_chars_per_shot:.1f}")

