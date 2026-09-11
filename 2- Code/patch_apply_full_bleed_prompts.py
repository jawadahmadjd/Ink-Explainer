"""
Script to apply precision fixes to apply_full_bleed_prompts.py
Eliminating all historical offsets in:
- Region 2 (shots 97-100)
- Region 3 (shots 133-196)
- Region 4 (shots 313-334)
"""
import re

FILE_PATH = r"d:\Tools of Jawad\25- Ink Explainers\2- Code\apply_full_bleed_prompts.py"

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. FIX REGION 2: Shots 97-100
region2_old = """    elif shot_id in [97]:
        char_style = "prehistoric stick figure lounging on mossy boulder, flat muted colors"
        bg = "sunny riverbank background with mossy rocks, green grass, and blue water"
        action = "hunter relaxing back on mossy rock watching white clouds drift across sunny sky"
    elif shot_id in [98]:
        char_style = "flat muted colors"
        bg = "wide prehistoric river valley background with golden sun rising over horizon"
        action = "sun rising over winding river valley casting long golden morning shadows across mist"
    elif shot_id in [99]:
        char_style = "flat muted colors"
        bg = "prehistoric village campsite background with leather lean-to shelters and smoking stone hearths at dawn"
        action = "panoramic view of quiet Paleolithic camp with small skin shelters and thin smoke curls at sunrise"
    elif shot_id in [100]:
        char_style = "silhouette of flock of birds flying, flat muted colors"
        bg = "pale orange sunrise sky background over misty birch tree canopy"
        action = "flock of birds silhouette flying across soft dawn sky as morning light hits treetops" """

region2_new = """    elif shot_id in [97]:
        char_style = "flat muted colors"
        bg = "wide prehistoric river valley background with golden sun rising over horizon"
        action = "sun rising over winding river valley casting long golden morning shadows across mist with stylized sun rays"
    elif shot_id in [98]:
        char_style = "flat muted colors"
        bg = "prehistoric village campsite background with leather lean-to shelters and smoking stone hearths at dawn"
        action = "panoramic view of quiet Paleolithic camp with three stone hearths sending thin curls of woodsmoke into dawn air"
    elif shot_id in [99]:
        char_style = "flat muted colors"
        bg = "wide peaceful river landscape background at dawn with misty birch forest along banks"
        action = "sun rising over misty birch forest canopy and winding river with soft golden morning light"
    elif shot_id in [100]:
        char_style = "silhouette of flock of birds flying, flat muted colors"
        bg = "pale orange sunrise sky background over misty birch tree canopy"
        action = "flock of birds silhouette flying across soft pale orange dawn sky as morning light touches the treetops" """

if region2_old in content:
    content = content.replace(region2_old, region2_new)
    print("Region 2 successfully patched.")
else:
    print("WARNING: Region 2 pattern not found exactly as expected.")

# 2. FIX REGION 3: Shots 133-196
# Locate start of 133 to 197
pattern_r3 = re.compile(r'    elif shot_id in \[133\]:.*?elif shot_id in \[197\]:', re.DOTALL)

region3_new = """    elif shot_id in [133]:
        char_style = "group of stick figures sitting with full bellies, flat muted colors"
        bg = "shady camp background under oak canopy"
        action = "tribe members sitting back against shelters patting satisfied bellies with relaxed smiles"
    elif shot_id in [134]:
        char_style = "stick figure laying down spear and relaxing on grass mat, flat muted colors"
        bg = "shady prehistoric camp background under large oak tree canopy with campfire pit, roasted food on stones, and reed sleeping mats"
        action = "hunter setting down wooden spear and stretching out on a woven grass mat under shade tree"
    elif shot_id in [135]:
        char_style = "young anthropologist in field clothes with notebook, flat muted colors"
        bg = "vintage field expedition background with dry scrub"
        action = "young researcher in sun hat walking with backpack and journal into desert wilderness"
    elif shot_id in [136]:
        char_style = "flat muted colors"
        bg = "hand-drawn map background of northern Botswana and Kalahari"
        action = "map showing the Kalahari Desert basin with dotted expedition trail leading to Dobe region"
    elif shot_id in [137]:
        char_style = "flat muted colors"
        bg = "harsh desert landscape background with shimmering heat mirage over cracked sand dunes and thorny scrub"
        action = "wide view of scorching sun beating down on dry cracked sand dunes and sparse thorny bushes"
    elif shot_id in [138]:
        char_style = "anthropologist sitting cross-legged with tribal group, flat muted colors"
        bg = "thatched grass shade shelter in desert background"
        action = "researcher sitting with Ju/'hoansi tribe members writing careful notes in field journal"
    elif shot_id in [139]:
        char_style = "hand holding vintage stopwatch, flat muted colors"
        bg = "desert sand background with notebook"
        action = "close-up of hand clicking vintage chrome analog stopwatch with ticking second hand"
    elif shot_id in [140]:
        char_style = "flat muted colors"
        bg = "Kalahari desert background with pale orange cracked sand dunes, sparse thorny acacia bushes, and shimmering heat horizon"
        action = "open field notebook showing neat handwritten columns of daily hours for hunting, gathering, and leisure"
    elif shot_id in [141]:
        char_style = "flat muted colors"
        bg = "grid chart background on clean paper"
        action = "four clean icons: digging roots, tracking antelope, cracking mongongo nuts, sewing hide garments"
    elif shot_id in [142]:
        char_style = "flat muted colors"
        bg = "vintage newspaper background"
        action = "vintage newspaper article headline reading: Stone Age Poverty and Constant Struggle for Food"
    elif shot_id in [143]:
        char_style = "cartoon caveman sweating under heavy boulder, flat muted colors"
        bg = "rocky cliff background"
        action = "cartoon caveman hunched over sweating under massive stone labeled 80-Hour Work Week"
    elif shot_id in [144]:
        char_style = "flat muted colors"
        bg = "large dark chalkboard background with white chalk"
        action = "giant chalkboard displaying bold handwritten white chalk numbers: 17.1 HOURS PER WEEK"
    elif shot_id in [145]:
        char_style = "flat muted colors"
        bg = "24-hour circular daily wheel background"
        action = "clock circle chart showing small 2.5-hour green slice labeled daily work, rest of wheel open"
    elif shot_id in [146]:
        char_style = "flat muted colors"
        bg = "wooden platter on grass background"
        action = "wooden platter filled with rich roasted meat and abundant protein-packed mongongo nuts"
    elif shot_id in [147]:
        char_style = "stick figure taking brisk enjoyable stroll, flat muted colors"
        bg = "sunny meadow background with wildflowers and sun timer"
        action = "stick figure enjoying casual morning stroll through meadow with sun timer showing 2.5 hours passed"
    elif shot_id in [148]:
        char_style = "flat muted colors"
        bg = "clean nutritional infographic chart background"
        action = "infographic bar chart displaying 2,140 daily calories and 93 grams of protein"
    elif shot_id in [149]:
        char_style = "healthy hunter flexing bicep with energetic smile, flat muted colors"
        bg = "desert campsite background in afternoon light"
        action = "hunter smiling proudly and flexing lean athletic arm with vitality sparkle lines"
    elif shot_id in [150]:
        char_style = "flat muted colors"
        bg = "clean wooden dining board background"
        action = "balanced meal plate with grilled venison, crushed nuts, wild beans, and fresh berries"
    elif shot_id in [151]:
        char_style = "flat muted colors"
        bg = "split comparison background: withered field vs deep desert root"
        action = "side-by-side comparison: withered dead modern corn crop versus deep thriving wild desert root"
    elif shot_id in [152]:
        char_style = "flat muted colors"
        bg = "cutaway soil cross section background"
        action = "diagram showing deep resilient desert taproot storing water several meters underground"
    elif shot_id in [153]:
        char_style = "two cartoon men in business suits at podium, flat muted colors"
        bg = "academic lecture hall background with debate microphone"
        action = "two economists in suits waving hands angrily at debate podium protesting the Kalahari data"
    elif shot_id in [154]:
        char_style = "flat muted colors"
        bg = "world map background with dotted flight lines"
        action = "small expedition airplane silhouette flying across world map connecting Africa, Australia, South America"
    elif shot_id in [155]:
        char_style = "flat muted colors"
        bg = "hand-drawn map of East Africa Rift Valley with pin"
        action = "map pin dropping near sparkling blue Lake Eyasi in Tanzania labeled Hadza Hunter-Gatherers"
    elif shot_id in [156]:
        char_style = "flat muted colors"
        bg = "clean digital display screen background"
        action = "digital display box flashing bright green numbers: 15.0 HOURS PER WEEK"
    elif shot_id in [157]:
        char_style = "flat muted colors"
        bg = "hand-drawn map of tropical northern Australia"
        action = "map pin dropping on wetlands of Arnhem Land Australia with water lily icon"
    elif shot_id in [158]:
        char_style = "flat muted colors"
        bg = "clean digital display screen background"
        action = "digital display box flashing bright green numbers: 16.2 HOURS PER WEEK"
    elif shot_id in [159]:
        char_style = "flat muted colors"
        bg = "hand-drawn map of South America rainforest"
        action = "map pin dropping on dense green Paraguay jungle canopy labeled Aché Foragers"
    elif shot_id in [160]:
        char_style = "flat muted colors"
        bg = "clean digital display screen background"
        action = "digital display box flashing bright green numbers: 19.1 HOURS PER WEEK"
    elif shot_id in [161]:
        char_style = "flat muted colors"
        bg = "four quadrant grid background showing desert, savannah, wetland, and rainforest"
        action = "four split quadrants comparing desert dunes, golden savannah, tropical wetlands, and rainforest canopy"
    elif shot_id in [162]:
        char_style = "flat muted colors"
        bg = "judicial courtroom background on wood surface"
        action = "hand-drawn wooden gavel coming down firmly on sound block with sharp impact lines"
    elif shot_id in [163]:
        char_style = "flat muted colors"
        bg = "wide open prehistoric savannah background with golden grass under warm sunny sky"
        action = "bold center text banner reading THE 15-HOUR WORK WEEK on warm golden field"
    elif shot_id in [164]:
        char_style = "hunter resting under shade tree whistling, flat muted colors"
        bg = "peaceful savannah meadow background with shade tree"
        action = "hunter lying back with hands clasped behind head under leafy branch, whistling peacefully"
    elif shot_id in [165]:
        char_style = "flat muted colors"
        bg = "weekly hours circular pie chart background"
        action = "pie chart with 85 percent colored vibrant golden yellow labeled YOUR TIME TO LIVE"
    elif shot_id in [166]:
        char_style = "flat muted colors"
        bg = "golden savannah landscape background in afternoon light"
        action = "wide panoramic view of golden fields glowing in late afternoon sun with breeze moving grass"
    elif shot_id in [167]:
        char_style = "modern stick figure sitting in cubicle staring at monitor, flat muted colors"
        bg = "corporate office cubicle background with grey walls and glowing computer screen"
        action = "modern stick figure sitting in chair looking at computer monitor with expression of stunned disbelief"
    elif shot_id in [168]:
        char_style = "flat muted colors"
        bg = "comparison bar chart background"
        action = "tall red bar showing 55 hours modern worker vs small green bar showing 17 hours hunter"
    elif shot_id in [169]:
        char_style = "flat muted colors"
        bg = "city highway at night background with long river of red brake lights in gridlock"
        action = "endless traffic jam on city highway at dusk with red taillights stretching into distance"
    elif shot_id in [170]:
        char_style = "tired stick figure pushing grocery cart down sterile aisle, flat muted colors"
        bg = "fluorescent supermarket aisle background with packed shelves"
        action = "exhausted stick figure pushing overloaded grocery cart under cold supermarket fluorescent lights"
    elif shot_id in [171]:
        char_style = "robot vacuum bumping into furniture, flat muted colors"
        bg = "modern living room floor background"
        action = "cartoon robotic vacuum cleaner bumping repeatedly into sofa leg with confusion squiggles"
    elif shot_id in [172]:
        char_style = "flat muted colors"
        bg = "modern apartment and kitchen background with wooden floor, kitchen counter with dishwasher and microwave, and city window view"
        action = "modern stainless steel dishwasher with door slightly open showing rows of clean plates"
    elif shot_id in [173]:
        char_style = "flat muted colors"
        bg = "digital network fiber lines background"
        action = "digital email envelope icon shooting through glowing network fiber lines at speed of light"
    elif shot_id in [174]:
        char_style = "modern stick figure looking down at open empty palms sad, flat muted colors"
        bg = "empty modern apartment living room background"
        action = "modern stick figure looking down at open empty palms with sad bewildered expression"
    elif shot_id in [175]:
        char_style = "split screen comparison: stressed suit vs calm hunter, flat muted colors"
        bg = "split background: office cubicle vs sunny tree"
        action = "side-by-side comparison: stressed businessman clutching tie vs relaxed hunter smiling under tree"
    elif shot_id in [176]:
        char_style = "flat muted colors"
        bg = "wooden tabletop background"
        action = "antique brass pocket watch breaking open with gears, springs, and cogs tumbling across floor"
    elif shot_id in [177]:
        char_style = "hunter kneeling down observing green beetle, flat muted colors"
        bg = "forest floor background with lush green plants"
        action = "hunter kneeling quietly in grass watching a shiny green beetle crawl across a leaf with fascination"
    elif shot_id in [178]:
        char_style = "flat muted colors"
        bg = "peaceful river flowing through meadow with wildflowers along banks"
        action = "clear river winding naturally through green meadows with wildflowers and zero dams"
    elif shot_id in [179]:
        char_style = "hunter wading into clear river water, flat muted colors"
        bg = "sparkling clear mountain river background with blue sky"
        action = "hunter wading playfully into shallow river, splashing cool water and smiling"
    elif shot_id in [180]:
        char_style = "stick figure sitting comfortably in grass looking around cheerful, flat muted colors"
        bg = "sunny river meadow background with green grass, smooth river pebbles, blooming yellow wildflowers, and blue sky"
        action = "prehistoric stick figure sitting comfortably in tall grass, looking around with playful curious smile"
    elif shot_id in [181]:
        char_style = "two children chasing yellow butterfly in meadow, flat muted colors"
        bg = "sunny wildflower field background with gentle breeze"
        action = "two prehistoric children laughing while chasing a bright yellow butterfly through tall meadow grass"
    elif shot_id in [182]:
        char_style = "four stick figures playing tug of war with rope, flat muted colors"
        bg = "grassy meadow background with cheering friends"
        action = "four stick figures laughing heartily while pulling on a thick braided leather tug-of-war rope"
    elif shot_id in [183]:
        char_style = "flat muted colors"
        bg = "clean archaeological display background on linen"
        action = "smooth river stones carved with clean geometric tally marks and notched calendar grooves"
    elif shot_id in [184]:
        char_style = "flat muted colors"
        bg = "smooth sandy surface background"
        action = "polished deer ankle knucklebones resting on smooth sand with carved dots resembling ancient dice"
    elif shot_id in [185]:
        char_style = "two stick figures wrestling on grass with cheering friends, flat muted colors"
        bg = "sunny camp meadow background with cheering crowd"
        action = "two prehistoric stick figures wrestling playfully on soft green grass while friends cheer around them"
    elif shot_id in [186]:
        char_style = "two traveling stick figures greeting neighboring tribe, flat muted colors"
        bg = "open grassy plateau background with distant shelters"
        action = "two friendly traveling stick figures with walking sticks greeting a welcoming neighboring tribal camp with open arms"
    elif shot_id in [187]:
        char_style = "flat muted colors"
        bg = "cave stone wall background with torchlight"
        action = "cave stone wall covered in overlapping blown red ochre and yellow pigment hand stencils"
    elif shot_id in [188]:
        char_style = "flat muted colors"
        bg = "hand-drawn map background of southern France"
        action = "illustrated parchment map of southern France with glowing pin pointing to the Ardèche River gorge"
    elif shot_id in [189]:
        char_style = "silhouette of prehistoric artist holding smoking torch, flat muted colors"
        bg = "dark rocky cave entrance background"
        action = "silhouette of prehistoric artist holding a smoking wooden torch entering the dark rocky mouth of Chauvet Cave"
    elif shot_id in [190]:
        char_style = "flat muted colors"
        bg = "geological cutaway cave diagram background"
        action = "cross-section cutaway diagram of deep cave system showing steep narrow passages descending deep underground"
    elif shot_id in [191]:
        char_style = "prehistoric artist crawling through narrow limestone tunnel, flat muted colors"
        bg = "claustrophobic dark rocky tunnel background"
        action = "artist crouching low and crawling through extremely narrow rough limestone rock tunnel with smoking torch ahead"
    elif shot_id in [192]:
        char_style = "flat muted colors"
        bg = "enormous cave cathedral chamber with glittering calcite crystals"
        action = "breathtaking grand cavern chamber opening up with massive glittering stalactites illuminated by warm flickering torchlight"
    elif shot_id in [193]:
        char_style = "flat muted colors"
        bg = "limestone rock wall background in warm torchlight"
        action = "spectacular charcoal cave painting of four lion heads rendered with incredible anatomical shading and artistic depth"
    elif shot_id in [194]:
        char_style = "flat muted colors"
        bg = "rough textured rock wall background"
        action = "close-up of undulating limestone cave wall showing how natural rock curves form the physical back and shoulder of a painted bison"
    elif shot_id in [195]:
        char_style = "flat muted colors"
        bg = "warm limestone wall background with flickering shadow"
        action = "famous cave drawing of galloping bison with eight legs sketched along the wall creating early animation motion effect"
    elif shot_id in [196]:
        char_style = "flat muted colors"
        bg = "prehistoric cave limestone wall background illuminated by warm golden flickering torchlight"
        action = "extreme close-up of charcoal cave painting showing galloping bison multiple overlapping legs flickering under warm flame creating the illusion of cinematic animation movement"
    elif shot_id in [197]:"""

match_r3 = pattern_r3.search(content)
if match_r3:
    content = content[:match_r3.start()] + region3_new + content[match_r3.end() - len("    elif shot_id in [197]:"):]
    print("Region 3 successfully patched.")
else:
    print("WARNING: Region 3 pattern not found.")

# 3. FIX REGION 4: Shots 313-334
pattern_r4 = re.compile(r'    elif shot_id in \[313\]:.*?else: # 334', re.DOTALL)

region4_new = """    elif shot_id in [313]:
        char_style = "farmer leaning heavily on hoe looking longingly at wild birds soaring free, flat muted colors"
        bg = "wheat field with boundary fence under open sky"
        action = "farmer leaning on hoe looking up with longing eyes at a flock of wild birds flying free over distant hills"
    elif shot_id in [314]:
        char_style = "modern stick figure crawling into bed, flat muted colors"
        bg = "simple hand-drawn modern cozy bedroom background at night with dark wood floor, bedside table with warm lamp glow, and comfortable bed"
        action = "stick figure pulling up soft duvet in modern bedroom, bedside lamp casting warm soft glow"
    elif shot_id in [315]:
        char_style = "hand reaching out toward glowing smartphone resting next to water glass, flat muted colors"
        bg = "bedside table background in warm night light"
        action = "hand reaching out from under blanket toward glowing smartphone sitting beside glass of water"
    elif shot_id in [316]:
        char_style = "flat muted colors"
        bg = "nightstand table background in dim lighting"
        action = "close-up of phone screen setting alarm toggle with green checkmark for 6:30 AM"
    elif shot_id in [317]:
        char_style = "time-lapse illustration of stick figure aging at desk hair turning gray, flat muted colors"
        bg = "corporate office cubicle background through the years"
        action = "time-lapse split showing stick figure at desk aging from 25 with dark hair to 65 with grey hair"
    elif shot_id in [318]:
        char_style = "stick figure looking out rain-streaked bus window at grey city buildings, flat muted colors"
        bg = "commuter bus interior background with wet window"
        action = "tired stick figure resting head against wet bus window looking at grey rainy city street"
    elif shot_id in [319]:
        char_style = "stick figure signing official mortgage papers across desk from bank officer, flat muted colors"
        bg = "bank office background with professional desk"
        action = "stick figure holding pen signing thick 30-year home mortgage contract across from banker"
    elif shot_id in [320]:
        char_style = "glass piggy bank filling with gold coins while calendar pages flip, flat muted colors"
        bg = "desk background with flipping calendar"
        action = "glass piggy bank slowly filling with gold coins as calendar pages flip rapidly past in background"
    elif shot_id in [321]:
        char_style = "elderly modern stick figure with walking cane smiling gently on park bench, flat muted colors"
        bg = "simple hand-drawn modern suburban neighborhood and park background with autumn trees, wooden park bench, and peaceful walking path"
        action = "elderly stick figure with white hair and cane sitting peacefully on wooden park bench under autumn trees"
    elif shot_id in [322]:
        char_style = "flat muted colors"
        bg = "peaceful autumn park background with gentle path"
        action = "bold clean banner across center reading RETIREMENT in warm friendly lettering"
    elif shot_id in [323]:
        char_style = "flat muted colors"
        bg = "dream bubble floating over park background"
        action = "dream bubble showing three scenes: fishing on calm lake, walking in pine woods, baking in kitchen"
    elif shot_id in [324]:
        char_style = "older stick figure on wooden cabin porch watching peaceful golden sunrise, flat muted colors"
        bg = "simple hand-drawn rustic cabin porch background overlooking calm lake at golden sunrise"
        action = "retired stick figure holding mug on wooden cabin porch watching calm golden sunrise over lake"
    elif shot_id in [325]:
        char_style = "stick figure strolling along pine forest path with sunbeams through branches, flat muted colors"
        bg = "simple hand-drawn pine forest trail background with sunlight filtering through tall green trees"
        action = "stick figure strolling slowly along pine-needle trail with hands in pockets and no watch"
    elif shot_id in [326]:
        char_style = "hands chopping fresh garden vegetables and herbs on rustic wooden board, flat muted colors"
        bg = "sunlit country kitchen counter background"
        action = "hands happily chopping fresh garden carrots, tomatoes, and herbs on rustic wooden cutting board"
    elif shot_id in [327]:
        char_style = "stick figure relaxing in hammock strung between two fruit trees in breeze, flat muted colors"
        bg = "peaceful backyard garden background with blooming fruit trees"
        action = "stick figure napping peacefully in a hammock swinging gently in the breeze under green fruit trees"
    elif shot_id in [328]:
        char_style = "group of older friends sitting around cozy stone fire pit laughing, flat muted colors"
        bg = "backyard garden background at night with dark trees"
        action = "group of retired friends sitting around rustic stone fire pit holding warm mugs and laughing"
    elif shot_id in [329]:
        char_style = "group of friends looking up in awe at glowing stars and Milky Way, flat muted colors"
        bg = "clear country night sky background filled with brilliant stars"
        action = "group of friends looking up in quiet wonder at the glowing Milky Way galaxy across the night sky"
    elif shot_id in [330]:
        char_style = "modern stick figure looking into bathroom mirror with deep thoughtful face, flat muted colors"
        bg = "simple hand-drawn modern bathroom background with mirror mounted over white ceramic sink and warm light"
        action = "modern stick figure leaning on white ceramic sink looking directly into mirror with profound realization"
    elif shot_id in [331]:
        char_style = "flat muted colors"
        bg = "modern office room background with dark chalkboard wall and wooden desk"
        action = "chalkboard timeline showing 45 years of office desks leading to a small question mark at retirement"
    elif shot_id in [332]:
        char_style = "golden glowing silhouette of prehistoric hunter standing free on ridge, flat muted colors"
        bg = "simple hand-drawn high prehistoric mountain ridge background with open sky at sunset"
        action = "glowing golden silhouette of ancient hunter standing tall on mountain ridge with arms open to wind"
    elif shot_id in [333]:
        char_style = "prehistoric hunter family laughing warmly together around glowing hearth, flat muted colors"
        bg = "simple hand-drawn peaceful wilderness landscape background at dusk with curling wisps of woodsmoke"
        action = "prehistoric hunter family sitting warmly together laughing around a crackling campfire in open wilderness"
    elif shot_id in [334]:
        char_style = "flat muted colors"
        bg = "simple hand-drawn peaceful wilderness landscape background at dusk with curling wisps of woodsmoke"
        action = "simple retro alarm clock doodle dissolving softly into a curling wisp of campfire smoke over wide open wilderness"
    else: # 334"""

match_r4 = pattern_r4.search(content)
if match_r4:
    content = content[:match_r4.start()] + region4_new + content[match_r4.end() - len("    else: # 334"):]
    print("Region 4 successfully patched.")
else:
    print("WARNING: Region 4 pattern not found.")

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patching complete!")

