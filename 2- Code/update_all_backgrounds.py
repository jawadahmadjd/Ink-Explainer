import csv
import re

# Script to inject specific, simple hand-drawn backgrounds into every shot prompt
# matching the exact visual style of the reference video (Ink Explainer).

def get_background(shot_id, text, visual):
    t = (text + " " + visual).lower()
    
    # Act 1 & Modern interiors
    if shot_id in [1, 2, 3, 4, 5, 6, 7, 8]:
        return "simple hand-drawn bedroom background with cream walls, wooden plank floor, bedside nightstand with lamp, and bed with pillow"
    elif shot_id in [9]:
        return "simple hand-drawn city traffic background viewed through car windshield with bumper-to-bumper cars and traffic lights"
    elif shot_id in [10]:
        return "simple hand-drawn subway car interior background with metal handrails, train windows, and seated passenger silhouettes"
    elif shot_id in [11, 12]:
        return "simple hand-drawn corporate office background with grey fabric cubicle partition walls, desk, computer monitor, and fluorescent ceiling light"
    elif shot_id in [13, 14, 15]:
        return "simple hand-drawn dark bedroom background at night with dark shadows, wooden nightstand, and faint blue phone glow"
    
    # Act 1: Prehistoric Dawn & Horizon
    elif shot_id in [16, 17, 18, 19, 20, 21, 22, 23, 24]:
        return "simple hand-drawn prehistoric savannah landscape background with flat tan dirt ground, gentle green rolling hills, winding blue river, and soft pastel pink dawn sky"
    
    # Act 1: Skeptical Modern Thoughts & Myths
    elif shot_id in [25, 26]:
        return "simple hand-drawn cozy living room background with dark wooden floor, grey sofa, potted houseplant, and warm beige wall"
    elif shot_id in [27, 28]:
        return "simple hand-drawn dark prehistoric cave background with rough stone walls, dripping icicles, and cold winter wind"
    elif shot_id in [29, 30, 31]:
        return "simple hand-drawn academic study background with wooden library desk, open books, and subtle chalkboard diagram wall"
    elif shot_id in [32, 33, 34, 35, 36, 37, 38, 39, 40]:
        return "simple hand-drawn modern office background with cubicle walls, water cooler, office desk, and wall clock"
    
    # Act 2: Archaeology & Bones
    elif shot_id in [41, 42, 43, 44]:
        return "simple hand-drawn archaeological dig site background with layered brown soil trench, excavation grid poles, and blue sky"
    elif shot_id in [45, 46, 47]:
        return "simple hand-drawn bioarchaeology laboratory background with clean wooden research examination table, magnifying lenses, and measurement calipers"
    elif 48 <= shot_id <= 65:
        return "simple hand-drawn clean archaeological examination background with light tan sediment ground, measurement scale bar, and soft neutral lighting"
    elif 66 <= shot_id <= 78:
        return "simple hand-drawn ancient mud-brick village background with brown plowed earth, stone quern slab, and distant simple thatched huts"
    elif 79 <= shot_id <= 85:
        return "simple hand-drawn forensic laboratory background with clean display table, medical skull diagrams, and neutral wall"
    elif 86 <= shot_id <= 97:
        return "simple hand-drawn lush prehistoric forest background with tall green trees, sunny clearing, blooming wildflowers, and riverbank"
    
    # Act 3: A Day in the Life (Morning & Camp)
    elif 98 <= shot_id <= 108:
        return "simple hand-drawn prehistoric campsite background at sunrise with sandy dirt ground, small leather lean-to shelters, and smoking stone hearth fire"
    elif 109 <= shot_id <= 120:
        return "simple hand-drawn open savannah background with golden grassland, dry dirt trail, and gentle blue morning sky"
    elif 121 <= shot_id <= 126:
        return "simple hand-drawn sunny African savannah background with dry yellow grass, scattered acacia trees, and distant low hills"
    elif 127 <= shot_id <= 135:
        return "simple hand-drawn sun-dappled woodland background with birch tree trunks, green berry brambles, and soft mossy ground"
    elif 136 <= shot_id <= 142:
        return "simple hand-drawn shady camp background under large oak tree canopy with campfire pit, roasted food on stones, and reed sleeping mats"
    
    # Act 3: Richard Lee Kalahari & Global Studies
    elif 143 <= shot_id <= 158:
        return "simple hand-drawn Kalahari desert background with pale orange cracked sand dunes, sparse thorny acacia bushes, and shimmering heat horizon"
    elif 159 <= shot_id <= 165:
        return "simple hand-drawn expedition study background with antique world map, wooden desk, vintage stopwatch, and field notebooks"
    elif 166 <= shot_id <= 170:
        return "simple hand-drawn diverse landscape background with split quadrants of desert dunes, savannah grassland, green wetlands, and dense jungle"
    
    # Act 3: Modern Comparison & Lost Time
    elif 171 <= shot_id <= 180:
        return "simple hand-drawn modern apartment and kitchen background with wooden floor, kitchen counter with dishwasher and microwave, and city window view"
    
    # Act 4: Play & Leisure
    elif 181 <= shot_id <= 188:
        return "simple hand-drawn sunny river meadow background with green grass, smooth river pebbles, blooming yellow wildflowers, and blue sky"
    
    # Act 4: Chauvet Cave Underground Art
    elif 189 <= shot_id <= 201:
        return "simple hand-drawn subterranean limestone cave interior background with textured rock walls, stalactites, and warm flickering golden torchlight glow"
    
    # Act 4: Sunghir Ice Age Burial
    elif 202 <= shot_id <= 216:
        return "simple hand-drawn Ice Age tundra background with deep white snowdrifts, pine trees coated in frost, and cold twilight sky with soft green aurora"
    
    # Act 4: Firelight Revolution (Polly Wiessner)
    elif 217 <= shot_id <= 223:
        return "simple hand-drawn African village camp background in late afternoon turning to deep violet twilight, with thatch huts and dry savannah horizon"
    elif 224 <= shot_id <= 236:
        return "simple hand-drawn night campsite background with dark navy blue sky, glowing orange campfire casting warm shadows on dirt ground, and circle of listeners"
    
    # Act 5: Biphasic Sleep & The Watch
    elif 237 <= shot_id <= 248:
        return "simple hand-drawn tranquil night camp background with dark charcoal night sky, silver crescent moon, scattered white star dots, and soft dying embers"
    elif 249 <= shot_id <= 255:
        return "simple hand-drawn modern dark bedroom background with streetlamp light filtering through window blinds and glowing blue alarm clock on nightstand"
    elif 256 <= shot_id <= 265:
        return "simple hand-drawn peaceful wilderness under night sky background with deep velvet blue sky, brilliant silver Milky Way galaxy, and silhouetted tree branches"
    
    # Act 6: The Agricultural Trap
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
    
    # Act 7: The Full-Circle Outro
    elif 316 <= shot_id <= 321:
        return "simple hand-drawn modern cozy bedroom background at night with dark wood floor, bedside table with warm lamp glow, and comfortable bed"
    elif 322 <= shot_id <= 327:
        return "simple hand-drawn modern suburban neighborhood and park background with autumn trees, wooden park bench, and peaceful walking path"
    elif 328 <= shot_id <= 331:
        return "simple hand-drawn tranquil lakeside porch background at sunset with calm water, pine trees, and wooden dock"
    elif shot_id in [332]:
        return "simple hand-drawn cozy backyard background at night with rustic stone fire pit, warm orange flames, and starry night sky"
    elif shot_id in [333]:
        return "simple hand-drawn prehistoric mountain ridge background at twilight with open starry sky and glowing campfire"
    else: # 334
        return "simple hand-drawn peaceful wilderness background at dusk with open horizon and faint curling wisps of woodsmoke"

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
    
    # Extract specific subject from old prompt
    # Old prompt format: Minimalist hand-drawn black ink line art, clean doodle stick-figure illustration, expressive face, flat muted colors, cream off-white background (#FAF8F5), {subject}, clean 2D vector style, editorial cartoon, no text, 16:9 aspect ratio
    m = re.search(r'cream off-white background \(#FAF8F5\),\s*(.*?),\s*clean 2D vector style', old_prompt)
    if m:
        subject = m.group(1)
    else:
        subject = visual
        
    bg = get_background(shot_id, text, visual)
    
    new_prompt = f"Minimalist hand-drawn 2D vector illustration, clean black ink comic line art, stick-figure character with round white head and expressive face, flat muted colors, {bg}, {subject}, clean editorial doodle art style, no text, 16:9 aspect ratio"
    
    updated_rows.append([shot_id, time_str, text, visual, new_prompt])

# Write updated CSV
with open('storyboard_master.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(updated_rows)

# Write updated Markdown
with open('storyboard_master.md', 'w', encoding='utf-8') as f:
    f.write("# Master Production Storyboard (334 Shots with Hand-Drawn Backgrounds)\n\n")
    f.write("| Shot | Time | Spoken VO script | Visual description | Exact Prompt for google nano banana pro |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- |\n")
    for r in updated_rows:
        t_clean = r[2].replace("|", "/")
        v_clean = r[3].replace("|", "/")
        p_clean = r[4].replace("|", "/")
        f.write(f"| {r[0]} | {r[1]} | {t_clean} | {v_clean} | `{p_clean}` |\n")

print(f"Successfully updated all {len(updated_rows)} shots with custom simple hand-drawn backgrounds!")

