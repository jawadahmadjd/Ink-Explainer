import json

with open('video_info.json', encoding='utf-16') as f:
    d = json.load(f)

print("Title:", d.get("title"))
print("Tags:", d.get("tags"))
print("Categories:", d.get("categories"))
print("Description:\n", d.get("description"))
