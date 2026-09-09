import csv

# We will create compile_full_storyboard.py containing the full 350-shot list
with open("compile_full_storyboard.py", "w", encoding="utf-8") as f:
    f.write('''import csv

# The Master 350-Shot Production Dataset
# Mapping Rule: 1000 characters = 60 seconds (1 sec = 16.6667 chars)

master_shots = []

def add(act_name, text, visual, subject):
    prompt = f"Minimalist hand-drawn black ink line art, clean doodle stick-figure illustration, expressive face, flat muted colors, cream off-white background (#FAF8F5), {subject}, clean 2D vector style, editorial cartoon, no text, 16:9 aspect ratio"
    master_shots.append({
        "act": act_name,
        "text": text,
        "visual": visual,
        "prompt": prompt
    })
''')

print("compile_full_storyboard.py initialized")

