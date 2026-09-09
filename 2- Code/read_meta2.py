import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('video_info.json', encoding='utf-16') as f:
    d = json.load(f)

print("Description:\n", d.get("description"))
