import csv

csv_path = r"d:\Tools of Jawad\25- Ink Explainers\3- Finals\1- What Did Ancient Humans Actually Do All Day\storyboard_master.csv"
with open(csv_path, 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f))[1:]

row_dict = {int(r[0]): r for r in rows}

def extract_action(prompt):
    # Remove prefix and suffix
    prefix = "Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art"
    suffix = "full bleed edge-to-edge composition, no borders, no frames, widescreen 16:9 aspect ratio"
    p = prompt.replace(prefix, "").replace(suffix, "").strip(", ")
    return p

print("=" * 80)
print("INSPECTING CLUSTER 2: SHOTS 135 TO 205")
print("=" * 80)
for s in range(135, 206):
    if s not in row_dict:
        continue
    r = row_dict[s]
    vo = r[2]
    desc = r[3]
    action = extract_action(r[4])
    print(f"Shot {s:03d} | VO: {vo}")
    print(f"  DESC  : {desc}")
    print(f"  PROMPT: {action}")
    print("-" * 60)

print("\n" + "=" * 80)
print("INSPECTING CLUSTER 3: SHOTS 310 TO 334")
print("=" * 80)
for s in range(310, 335):
    if s not in row_dict:
        continue
    r = row_dict[s]
    vo = r[2]
    desc = r[3]
    action = extract_action(r[4])
    print(f"Shot {s:03d} | VO: {vo}")
    print(f"  DESC  : {desc}")
    print(f"  PROMPT: {action}")
    print("-" * 60)

