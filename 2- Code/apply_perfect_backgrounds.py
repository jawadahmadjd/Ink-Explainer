import csv
import re

def get_exact_background(shot_id):
    # Act 1: Modern vs Ancient Hook (1 - 44)
    if shot_id in [1, 2, 3, 4, 5, 6, 7, 8]:
        return "simple hand-drawn cozy bedroom background with beige wall, wooden plank floor, bedside nightstand with lamp, and bed with pillow"
    elif shot_id == 9:
        return "simple hand-drawn city street traffic background viewed through a car windshield with steering wheel and taillights"
    elif shot_id == 10:
        return "simple hand-drawn subway train car interior background with metal handrails, train windows, and adjacent passenger silhouettes"
    elif shot_id in [11, 12]:
        return "simple hand-drawn modern office background with grey fabric cubicle partition walls, wooden desk, and computer monitor"
    elif shot_id in [13, 14, 15]:
        return "simple hand-drawn dark bedroom background at night with dark shadows, bedside table, and faint blue smartphone glow"
    elif shot_id in [16, 17, 18, 19, 20, 21, 22, 23, 24]:
        return "simple hand-drawn prehistoric savannah landscape background with flat tan dirt ground, gentle green rolling hills, winding blue river, and soft pastel pink dawn sky"
    elif shot_id in [25, 26]:
        return "simple hand-drawn cozy living room background with dark wooden floor, grey sofa, potted houseplant, and warm beige wall"
    elif shot_id in [27, 28]:
        return "simple hand-drawn dark prehistoric cave interior background with rough stone walls, dripping icicles, and cold winter wind"
    elif shot_id in [29, 30, 31]:
        return "simple hand-drawn vintage study background with wooden library desk, open textbooks, and chalkboard diagram wall"
    elif shot_id in [32, 33, 34, 35, 36, 37, 38, 39, 40]:
        return "simple hand-drawn modern office environment background with cubicle walls, water cooler, desk with coffee mug, and wall clock"
    elif shot_id in [41, 42, 43, 44]:
        return "simple hand-drawn archaeological dig site background with layered brown soil trench, excavation grid poles, and pale blue sky"

    # Act 2: Forensic Skeletons (45 - 96)
    elif shot_id in [45, 46, 47]:
        return "simple hand-drawn bioarchaeology laboratory background with clean wooden research examination table, magnifying lenses, and measurement calipers"
    elif 48 <= shot_id <= 65:
        return "simple hand-drawn clean archaeological examination background with light tan sediment ground, measurement scale bar, and soft neutral lighting"
    elif 66 <= shot_id <= 78:
        return "simple hand-drawn ancient Neolithic farming settlement background with muddy plowed soil, crude stone quern slab, and distant thatched huts"
    elif 79 <= shot_id <= 85:
        return "simple hand-drawn medical anthropology laboratory background with clean display table, anatomical skull charts, and neutral wall"
    elif 86 <= shot_id <= 96:
        return "simple hand-drawn lush prehistoric forest background with tall green trees, sunny clearing, blooming wildflowers, and riverbank"

    # Act 3: A Day in the Life (97 - 179)
    elif 97 <= shot_id <= 108:
        return "simple hand-drawn prehistoric campsite background at sunrise with sandy dirt ground, small leather lean-to shelters, and smoking stone hearth fire"
    elif 109 <= shot_id <= 124:
        return "simple hand-drawn sunny African savannah background with golden grassland, dry dirt game trail, sparse acacia trees, and pale blue sky"
    elif 125 <= shot_id <= 134:
        return "simple hand-drawn sun-dappled woodland background with birch tree trunks, green berry brambles, wild flowers, and soft mossy ground"
    elif 135 <= shot_id <= 140:
        return "simple hand-drawn shady camp background under large oak tree canopy with campfire pit, roasted food on stones, and reed sleeping mats"
    elif 141 <= shot_id <= 157:
        return "simple hand-drawn Kalahari desert background with pale orange cracked sand dunes, sparse thorny acacia bushes, and shimmering heat horizon"
    elif 158 <= shot_id <= 164:
        return "simple hand-drawn expedition field camp background with vintage canvas tent, wooden foldout table, world map, and field notebooks"
    elif 165 <= shot_id <= 169:
        return "simple hand-drawn wide open prehistoric savannah background with golden grass under warm sunny sky"
    elif 170 <= shot_id <= 179:
        return "simple hand-drawn modern apartment and kitchen background with wooden floor, kitchen counter with dishwasher and microwave, and city window view"

    # Act 4: Play, Art & Firelight (180 - 236)
    elif 180 <= shot_id <= 187:
        return "simple hand-drawn sunny river meadow background with green grass, smooth river pebbles, blooming yellow wildflowers, and blue sky"
    elif 188 <= shot_id <= 200:
        return "simple hand-drawn subterranean limestone cave interior background with textured rock walls, stalactites, and warm flickering golden torchlight glow"
    elif 201 <= shot_id <= 215:
        return "simple hand-drawn Ice Age tundra background with deep white snowdrifts, pine trees coated in frost, and cold twilight sky with soft green aurora"
    elif 216 <= shot_id <= 222:
        return "simple hand-drawn African village camp background in late afternoon turning to deep violet twilight, with thatch huts and dry savannah horizon"
    elif 223 <= shot_id <= 236:
        return "simple hand-drawn night campsite background with dark navy blue sky, glowing orange campfire casting warm shadows on dirt ground, and circle of listeners"

    # Act 5: Sleep & The Watch (237 - 265)
    elif 237 <= shot_id <= 238:
        return "simple hand-drawn tranquil night camp background with dark charcoal night sky, silver crescent moon, scattered white star dots, and soft dying embers"
    elif 239 <= shot_id <= 244:
        return "simple hand-drawn modern dark bedroom background with streetlamp light filtering through window blinds and glowing blue alarm clock on nightstand"
    elif 245 <= shot_id <= 247:
        return "simple hand-drawn circadian sleep research laboratory background with calm blue ambient lighting and digital brainwave monitor screens"
    elif 248 <= shot_id <= 260:
        return "simple hand-drawn peaceful midnight campsite background under brilliant silver starry sky, with soft glowing campfire coals and quiet tents"
    elif 261 <= shot_id <= 264:
        return "simple hand-drawn modern glass skyscraper city background at night with thousands of blinding electric windows and streetlights"
    elif shot_id == 265:
        return "simple hand-drawn peaceful wilderness under night sky background with deep velvet blue sky, brilliant silver Milky Way galaxy, and silhouetted tree branches"

    # Act 6: The Agricultural Trap (266 - 315)
    elif 266 <= shot_id <= 273:
        return "simple hand-drawn prehistoric river valley background with dramatic dark storm clouds gathering over golden grassy plains"
    elif 274 <= shot_id <= 282:
        return "simple hand-drawn riverbank garden background with damp muddy soil furrows, small wild wheat plots, and woven twig fences"
    elif 283 <= shot_id <= 292:
        return "simple hand-drawn crowded ancient Neolithic village background with packed mud-brick flat-roof houses, narrow dirt alleys, and ceramic storage jars"
    elif 293 <= shot_id <= 304:
        return "simple hand-drawn extensive agricultural field background with plowed brown mud furrows, rows of ripe golden wheat, and distant hazy hills under hot sun"
    elif 305 <= shot_id <= 315:
        return "simple hand-drawn ancient fortified city background with massive stone perimeter walls, wooden granary towers, and battlements under hazy sky"

    # Act 7: Full-Circle Outro (316 - 334)
    elif 316 <= shot_id <= 321:
        return "simple hand-drawn modern cozy bedroom background at night with dark wood floor, bedside table with warm lamp glow, and comfortable bed"
    elif 322 <= shot_id <= 327:
        return "simple hand-drawn modern suburban neighborhood and park background with autumn trees, wooden park bench, and peaceful walking path"
    elif shot_id in [328]:
        return "simple hand-drawn rustic cabin porch background overlooking calm lake at golden sunrise"
    elif shot_id in [329]:
        return "simple hand-drawn pine forest trail background with sunlight filtering through tall green trees"
    elif shot_id in [330]:
        return "simple hand-drawn modern bathroom background with mirror mounted over white ceramic sink and warm light"
    elif shot_id in [331]:
        return "simple hand-drawn modern office room background with dark chalkboard wall and wooden desk"
    elif shot_id in [332]:
        return "simple hand-drawn high prehistoric mountain ridge background with open sky at sunset"
    elif shot_id in [333]:
        return "simple hand-drawn warm prehistoric campsite background under starry sky with glowing campfire and tents"
    else: # 334
        return "simple hand-drawn peaceful wilderness landscape background at dusk with curling wisps of woodsmoke"

# Read current CSV
with open('storyboard_master.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f))

header = rows[0]
data_rows = rows[1:]

updated_rows = []
for row in data_rows:
    shot_id = int(row[0])
    time_str = row[1]
    text = row[2]
    visual = row[3]
    old_prompt = row[4]
    
    # Extract specific subject/action from old prompt
    # Old pattern: ... flat muted colors, [OLD BG], [SUBJECT], clean editorial doodle art style, no text, 16:9 aspect ratio
    # Or just use the clean visual description
    subject = visual
    bg = get_exact_background(shot_id)
    
    new_prompt = f"Minimalist hand-drawn 2D vector illustration, clean black ink comic line art, stick-figure character with round white head and expressive face, flat muted colors, {bg}, {subject}, clean editorial doodle art style, no text, 16:9 aspect ratio"
    
    updated_rows.append([shot_id, time_str, text, visual, new_prompt])

# Write updated CSV
with open('storyboard_master.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(updated_rows)

# Write updated Markdown
with open('storyboard_master.md', 'w', encoding='utf-8') as f:
    f.write("# Master Production Storyboard (334 Shots with Precise Hand-Drawn Backgrounds)\n\n")
    f.write("| Shot | Time | Spoken VO script | Visual description | Exact Prompt for google nano banana pro |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- |\n")
    for r in updated_rows:
        t_clean = r[2].replace("|", "/")
        v_clean = r[3].replace("|", "/")
        p_clean = r[4].replace("|", "/")
        f.write(f"| {r[0]} | {r[1]} | {t_clean} | {v_clean} | `{p_clean}` |\n")

print(f"Successfully updated all {len(updated_rows)} shots with exact scene-matched hand-drawn backgrounds!")
