import csv
import re

# Comprehensive script to update all 334 prompts in storyboard_master.csv and storyboard_master.md
# Applying the proven Full-Bleed Edge-to-Edge formula with zero border matting.

def get_shot_elements(shot_id, text, visual):
    # Determine Character Style, Background, and Action
    
    # --- ACT 1: MODERN GRID VS OPEN HORIZON (1 - 44) ---
    if shot_id in [1]:
        char_style = "flat muted colors"
        bg = "cozy bedroom background with warm beige walls, wooden floor, and wooden bed headboard in the soft background"
        action = "extreme close-up of a red twin-bell mechanical alarm clock on a wooden nightstand with vibration motion lines, hands pointing to 6:30"
    elif shot_id in [2]:
        char_style = "stick-figure character with round white head and anxious expressive face, flat muted colors"
        bg = "modern bedroom background with beige wall, wooden nightstand, and bed with crumpled blankets"
        action = "stick figure sitting up in bed staring closely at a glowing smartphone screen displaying a crowded calendar grid"
    elif shot_id in [3]:
        char_style = "flat muted colors"
        bg = "dark bedroom at night with dark navy blue walls and wooden bedside table"
        action = "close-up of a bright smartphone screen face-up on a white pillow casting cold blue light across the dark sheets"
    elif shot_id in [4]:
        char_style = "stick-figure character with round white head and exhausted expression, flat muted colors"
        bg = "cozy modern bedroom background with warm beige walls, wooden floorboards, and wooden bed frame"
        action = "tired stick figure swinging legs out of bed onto the floor, rubbing sleepy eyes with both hands"
    elif shot_id in [5]:
        char_style = "stick-figure character with round white head and expressive worried face, flat muted colors"
        bg = "dark cozy bedroom at night with dark navy blue walls, dark wooden floorboards, simple bed with pillow and standing floor lamp in background"
        action = "stick figure sitting up in bed holding a glowing smartphone, screen casting a soft blue cone of light onto his face"
    elif shot_id in [6]:
        char_style = "stick-figure character looking stressed, flat muted colors"
        bg = "modern morning bedroom background with bedside lamp and window with morning daylight"
        action = "stick figure looking with wide eyes at an urgent red exclamation mark corporate meeting alert popping up on smartphone"
    elif shot_id in [7]:
        char_style = "flat muted colors"
        bg = "modern office desk background with wooden surface, pen holder, and laptop screen"
        action = "close-up of digital calendar schedule showing solid back-to-back blocks with zero empty space from morning to evening"
    elif shot_id in [8]:
        char_style = "stick-figure character with lonely expression, flat muted colors"
        bg = "grey office cubicle background with desk, computer screen, and office chair"
        action = "plastic-wrapped sandwich sitting untouched next to a small desk clock with a countdown timer ticking away"
    elif shot_id in [9]:
        char_style = "stick-figure character with angry frustrated expression, flat muted colors"
        bg = "city street traffic background viewed through a car windshield with steering wheel and red taillights"
        action = "stick figure tightly gripping the steering wheel of a car stuck in bumper-to-bumper city traffic jam"
    elif shot_id in [10]:
        char_style = "stick-figure characters packed together with tired expressions, flat muted colors"
        bg = "subway train car interior background with metal handrails, train windows, and seated passenger silhouettes"
        action = "stick figures packed shoulder-to-shoulder in crowded subway car all staring silently down at glowing phone screens"
    elif shot_id in [11]:
        char_style = "stick-figure character with round white head and tired drooping eyes, flat muted colors"
        bg = "corporate office interior background with grey fabric cubicle partition walls, wooden desk, glowing computer monitor, and overhead fluorescent ceiling light"
        action = "exhausted stick figure hunched over typing on a laptop with a white coffee mug on the desk"
    elif shot_id in [12]:
        char_style = "stick-figure character with overwhelmed dizzy face, flat muted colors"
        bg = "corporate office cubicle background with stacked papers and glowing monitor"
        action = "stressed stick figure surrounded by a cloud of floating unread message notification badges and email icons"
    elif shot_id in [13]:
        char_style = "stick-figure character with weary face, flat muted colors"
        bg = "dark bedroom at night with dark slate walls, wooden nightstand, and bed"
        action = "stick figure lying down under duvet in dark room staring up at the ceiling with faint screen reflection"
    elif shot_id in [14]:
        char_style = "flat muted colors"
        bg = "dark bedroom nightstand background with table lamp base and glass of water"
        action = "close-up of a hand with finger hovering over a digital smartphone screen ready to toggle the morning alarm"
    elif shot_id in [15]:
        char_style = "flat muted colors"
        bg = "dark bedroom nightstand background with soft ambient night shadow"
        action = "macro shot of smartphone display sliding alarm switch to green with text reading alarm set for 6:00 AM"
    elif shot_id in [16]:
        char_style = "flat muted colors"
        bg = "cinematic transitional landscape where modern wallpaper peels back into open prehistoric river valley"
        action = "transitional split concept where a modern digital clock dissolves into swirling prehistoric dust and river mist"
    elif shot_id in [17]:
        char_style = "prehistoric stick-figure hunter with wild hair wearing a simple brown fur pelt, flat muted colors"
        bg = "wide prehistoric savannah landscape background with flat tan dirt ground, rolling green hills, a winding blue river, and a soft pastel pink and orange sunrise sky"
        action = "prehistoric stick figure standing tall on a grassy ridge stretching his arms wide toward the morning sun"
    elif shot_id in [18]:
        char_style = "flat muted colors"
        bg = "panoramic untouched Paleolithic wilderness background with morning mist rising over golden grassland, winding river, and distant blue mountains"
        action = "wide panoramic shot of pure untouched nature at sunrise with soft clouds and flying birds, no buildings or roads"
    elif shot_id in [19]:
        char_style = "prehistoric stick-figure hunter standing proud with hands on hips, flat muted colors"
        bg = "high limestone cliff ledge background overlooking a vast lush prehistoric river basin at dawn"
        action = "hunter standing tall and completely relaxed on cliff edge gazing out across miles of open fertile wilderness"
    elif shot_id in [20]:
        char_style = "flat muted colors"
        bg = "clean prehistoric campsite background with sandy dirt ground, limestone boulder, and tall dry grass"
        action = "close-up of ancient possessions laid neatly: a knapped flint spearhead on wood shaft and two folded reindeer fur pelts"
    elif shot_id in [21]:
        char_style = "flat muted colors"
        bg = "prehistoric campsite ground background with dry sandy earth and small river pebbles"
        action = "small morning campfire crackling gently inside a neat circular ring of river stones with thin white smoke rising"
    elif shot_id in [22]:
        char_style = "prehistoric stick-figure hunter with relaxed smiling face, flat muted colors"
        bg = "prehistoric savannah ridge background with golden morning sunlight and soft breeze"
        action = "hunter yawning contentedly and stretching his arms high above his head in the warm morning sunshine"
    elif shot_id in [23]:
        char_style = "prehistoric stick-figure hunter with thoughtful curious expression, flat muted colors"
        bg = "prehistoric open hillside background with golden grass and blue sky with drifting white clouds"
        action = "hunter resting hand on chin looking up at the sky with peaceful, genuinely curious eyes"
    elif shot_id in [24]:
        char_style = "flat muted colors"
        bg = "prehistoric open sky background with soft white clouds"
        action = "creative thought bubble showing three peaceful choices: a leaping river fish, a mountain hiking trail, and a shady nap tree"
    elif shot_id in [25]:
        char_style = "modern stick-figure character with arms crossed and skeptical frowning face, flat muted colors"
        bg = "cozy modern living room background with dark wooden floor, grey sofa, potted houseplant, and warm beige wall"
        action = "modern stick figure sitting on sofa with crossed arms and furrowed brow, skeptical question marks hovering above"
    elif shot_id in [26]:
        char_style = "stick-figure character running in panic, flat muted colors"
        bg = "comic thought bubble frame background over living room wall"
        action = "cartoon stick figure running with comedic flailing legs away from a roaring stylized sabertooth cat"
    elif shot_id in [27]:
        char_style = "stick-figure character shivering wrapped in thin blanket, flat muted colors"
        bg = "dark prehistoric cave interior background with rough stone walls, dripping icicles, and cold winter wind"
        action = "cartoon stick figure shivering with chattering teeth inside a dark damp cave surrounded by ice stalactites"
    elif shot_id in [28]:
        char_style = "stick-figure character looking down with hungry sad face, flat muted colors"
        bg = "dim prehistoric cave background with cold rocky floor"
        action = "stick figure looking sadly into an empty wooden bowl with squiggly hunger lines radiating from stomach"
    elif shot_id in [29]:
        char_style = "flat muted colors"
        bg = "vintage study background with wooden library desk and warm wall"
        action = "open vintage history textbook with pages displayed, a giant bold red ink rubber stamp reading MYTH across the page"
    elif shot_id in [30]:
        char_style = "flat muted colors"
        bg = "educational classroom background with clean chalkboard wall and wooden floor"
        action = "chalkboard diagram showing an upward sloping ramp depicting evolution from hunched ape to modern stick figure at computer"
    elif shot_id in [31]:
        char_style = "modern stick-figure character looking stressed with head in hands, flat muted colors"
        bg = "modern smart home interior background with microwave, robot vacuum, smart TV, and laptop"
        action = "modern stick figure sitting on floor surrounded by high-tech appliances looking completely overwhelmed and exhausted"
    elif shot_id in [32]:
        char_style = "tired stick figure running inside wheel, flat muted colors"
        bg = "conceptual workplace background with giant clock gears on wall"
        action = "stick figure running endlessly inside a giant ticking clock gear wheel like a hamster"
    elif shot_id in [33]:
        char_style = "flat muted colors"
        bg = "office desk surface background with coffee ring stains"
        action = "hand-drawn paper bill receipt with a bold red stamp reading: FORTY HOURS A WEEK TO ESCAPE ANCIENT MISERY"
    elif shot_id in [34]:
        char_style = "primitive hunched stick figure dragging knuckles, flat muted colors"
        bg = "muddy swampy prehistoric ground background with murky puddles and bare trees"
        action = "hunched primitive stick figure dragging knuckles in mud with comically exaggerated confused face"
    elif shot_id in [35]:
        char_style = "stick figure sprinting in frantic panic, flat muted colors"
        bg = "dramatic volcanic canyon background with falling boulders and storm clouds"
        action = "cartoon stick figure dodging falling boulders and fleeing from shadows in over-the-top panic"
    elif shot_id in [36]:
        char_style = "flat muted colors"
        bg = "bright modern kitchen background with clean countertop and tile wall"
        action = "smiling cheerful cartoon lineup of modern gadgets: smartphone, robotic vacuum, microwave, and dishwasher"
    elif shot_id in [37]:
        char_style = "flat muted colors"
        bg = "tropical beach background with two palm trees, white sand, and blue ocean"
        action = "an empty relaxing hammock strung between two palm trees with a giant red hanging tag reading UNAVAILABLE"
    elif shot_id in [38]:
        char_style = "proud exhausted stick figure with dark eye circles, flat muted colors"
        bg = "corporate office hallway background with glass doors and water cooler"
        action = "tired stick figure with bloodshot eyes proudly wearing a large gold medal engraved with the word BURNOUT"
    elif shot_id in [39]:
        char_style = "modern stick figure staring with wide shocked eyes, flat muted colors"
        bg = "office breakroom background with laminate counter and coffee machine"
        action = "modern stick figure holding a white ceramic coffee mug, staring deeply into the black coffee in existential shock"
    elif shot_id in [40]:
        char_style = "modern stick figure looking through window, flat muted colors"
        bg = "modern office interior looking out through a window with vertical metal bars"
        action = "office worker looking through window bars at a free ancient hunter running across a sunlit green hill outside"
    elif shot_id in [41]:
        char_style = "flat muted colors"
        bg = "clean wooden desk surface background"
        action = "a golden illuminated parchment contract tearing cleanly down the middle with official wax seal broken"
    elif shot_id in [42]:
        char_style = "stick figure crouching behind shield, flat muted colors"
        bg = "office cubicle background with incoming flying emails and deadlines"
        action = "stressed office worker crouching behind a round wooden shield painted with the word EXCUSES"
    elif shot_id in [43]:
        char_style = "flat muted colors"
        bg = "overgrown grassy cemetery background under grey sky"
        action = "cracked stone gravestone carved with the text: NO LEISURE, ONLY ENDLESS PREHISTORIC TOIL"
    elif shot_id in [44]:
        char_style = "stick-figure archaeologist in explorer sun hat and khaki vest, flat muted colors"
        bg = "archaeological excavation trench background with layered brown soil strata, excavation grid poles, and pale blue sky"
        action = "archaeologist kneeling in dirt trench carefully using a small brush and trowel to uncover ancient soil layers"

    # --- ACT 2: FORENSIC AUTOPSY — THE DIRT DOESN'T LIE (45 - 96) ---
    elif shot_id in [45]:
        char_style = "flat muted colors"
        bg = "archaeological dig site trench background with stratified earth walls and measuring stick"
        action = "archaeological dig site showing two ancient fossil graves uncovered side by side in dry earth strata with exposed skeletal remains"
    elif shot_id in [46]:
        char_style = "flat muted colors"
        bg = "archaeological dig site trench background with stratified earth walls and measuring stick"
        action = "macro view of ancient fossil human bones resting cleanly in excavated dry sediment strata"
    elif shot_id in [47]:
        char_style = "flat muted colors"
        bg = "bioarchaeology laboratory background with clean wooden research examination table, magnifying lenses, and measurement calipers"
        action = "laboratory examination table with precision brass calipers, magnifying glass, and ancient skull specimens laid on cloth"
    elif shot_id in [48]:
        char_style = "flat muted colors"
        bg = "museum laboratory background with neutral grey walls"
        action = "two clean display tables side by side with neat labels reading Paleolithic Hunter and Neolithic Farmer"
    elif shot_id in [49]:
        char_style = "flat muted colors"
        bg = "hand-drawn map background of ancient Near East with parchment texture"
        action = "illustrated map of the Fertile Crescent highlighting the green floodplains of the Tigris and Euphrates rivers"
    elif shot_id in [50]:
        char_style = "flat muted colors"
        bg = "archaeological dig site diagram background"
        action = "detailed overhead excavation trench map showing numbered grid squares, soil depths, and red burial flags"
    elif shot_id in [51]:
        char_style = "flat muted colors"
        bg = "historical timeline diagram background on textured paper"
        action = "chronological arrow graphic showing transition from a flint spear icon into a curved sickle farming icon"
    elif shot_id in [52]:
        char_style = "flat muted colors"
        bg = "ancient agricultural landscape background under pale sky"
        action = "furrowed brown plowed field with neat rows of tiny green wheat seedlings sprouting from soil"
    elif shot_id in [53]:
        char_style = "flat muted colors"
        bg = "clean forensic laboratory examination background with measuring scale bar"
        action = "split-screen horizontal comparison showing two complete human skeletons laid out side by side on clean surface"
    elif shot_id in [54]:
        char_style = "stick-figure scientist with wide amazed eyes, flat muted colors"
        bg = "laboratory background with microscope and reference books on shelf"
        action = "scientist holding a large round magnifying glass to eye, mouth open in astonished surprise"
    elif shot_id in [55]:
        char_style = "flat muted colors"
        bg = "clean museum display background with soft neutral lighting"
        action = "full anatomical view of Skeleton A: tall frame, broad shoulders, dense leg bones, and perfectly straight spine"
    elif shot_id in [56]:
        char_style = "prehistoric hunter carrying spear, flat muted colors"
        bg = "glacial steppe landscape background with vast open tundra, distant snow peaks, and cold blue sky"
        action = "silhouette of tall hunter carrying wooden spear striding confidently along high steppe ridge"
    elif shot_id in [57]:
        char_style = "flat muted colors"
        bg = "forensic measurement background with vertical height scale"
        action = "height comparison chart showing Skeleton A standing tall at the 5 foot 11 inch mark beside shorter figures"
    elif shot_id in [58]:
        char_style = "flat muted colors"
        bg = "medical diagram background on clean beige canvas"
        action = "cross-section illustration of a human thigh bone showing remarkably thick, dense cortical bone walls"
    elif shot_id in [59]:
        char_style = "athletic stick figure running and jumping, flat muted colors"
        bg = "open sports arena track background with hurdles"
        action = "athletic stick figure clearing a hurdle with dynamic muscular motion lines showing supreme physical fitness"
    elif shot_id in [60]:
        char_style = "flat muted colors"
        bg = "triptych panel background showing three nature scenes"
        action = "three illustrated circular icons: hiking steep rocky mountain, wading through river current, climbing tall tree"
    elif shot_id in [61]:
        char_style = "prehistoric stick figure balancing gracefully, flat muted colors"
        bg = "mountain river gorge background with rushing water below and evergreen trees"
        action = "hunter balancing with ease while walking across a fallen tree trunk spanning a mountain stream"
    elif shot_id in [62]:
        char_style = "flat muted colors"
        bg = "anatomical diagram background on clean paper"
        action = "close-up illustration of human knee joint bones showing perfectly smooth cartilage surfaces with zero wear"
    elif shot_id in [63]:
        char_style = "flat muted colors"
        bg = "clean laboratory examination background"
        action = "macro illustration of hunter skull jaws showing wide dental arch and perfectly aligned clean white teeth"
    elif shot_id in [64]:
        char_style = "flat muted colors"
        bg = "clean light blue background with sparkle accents"
        action = "isolated clean white molar tooth doodle with brilliant sparkle glint lines radiating from enamel"
    elif shot_id in [65]:
        char_style = "flat muted colors"
        bg = "bathroom shelf background with mirror"
        action = "modern plastic toothbrush and floss container crossed out with a bold hand-drawn red X"
    elif shot_id in [66]:
        char_style = "flat muted colors"
        bg = "wooden table background with natural woven mat"
        action = "artful arrangement of wild food diet: cracked walnuts, ripe blackberries, roasted lean meat slices, and wild roots"
    elif shot_id in [67]:
        char_style = "flat muted colors"
        bg = "microscopic view circular frame background"
        action = "microscopic view showing diverse, friendly round bacteria cells floating in harmony in healthy oral biome"
    elif shot_id in [68]:
        char_style = "flat muted colors"
        bg = "clean forensic laboratory background"
        action = "pan across to Skeleton B: smaller frame, hunched neck vertebrae, compressed spinal discs, and shorter limbs"
    elif shot_id in [69]:
        char_style = "early Neolithic stick-figure farmer with tired face, flat muted colors"
        bg = "muddy farming field background with primitive stone quern and tilled dirt"
        action = "farmer kneeling in mud pushing heavy grinding hand-stone back and forth on flat stone slab"
    elif shot_id in [70]:
        char_style = "flat muted colors"
        bg = "valley landscape where forest has been cleared away for muddy agricultural plots under overcast sky"
        action = "wide view of cleared valley with bare brown tilled fields replacing ancient forest"
    elif shot_id in [71]:
        char_style = "flat muted colors"
        bg = "height measurement scale background"
        action = "height chart showing Skeleton B dropping four inches shorter to the 5 foot 6 inch mark"
    elif shot_id in [72]:
        char_style = "flat muted colors"
        bg = "medical pathology diagram background"
        action = "close-up illustration of lumbar spinal vertebrae showing crushed discs and jagged arthritic bone spurs"
    elif shot_id in [73]:
        char_style = "female farmer stick figure bending forward, flat muted colors"
        bg = "mud-brick hut courtyard background with grain baskets"
        action = "female farmer kneeling on knees leaning forward pushing heavy stone pestle on saddle quern"
    elif shot_id in [74]:
        char_style = "flat muted colors"
        bg = "anatomical diagram background"
        action = "detailed illustration of human foot bones showing metatarsals bent and curled with arthritic swelling"
    elif shot_id in [75]:
        char_style = "kneeling stick figure frozen in place, flat muted colors"
        bg = "dirt ground background with giant clock dial overlay"
        action = "clock face with hour hand sweeping 8 hours while kneeling figure remains trapped grinding grain"
    elif shot_id in [76]:
        char_style = "calloused hands pushing stone, flat muted colors"
        bg = "stone grain grinding slab background with flour dust"
        action = "close-up of hands pushing stone pestle across saddle quern with coarse flour spilling onto mat"
    elif shot_id in [77]:
        char_style = "flat muted colors"
        bg = "anatomical bone diagram background"
        action = "illustration of human clavicle collarbone showing deep grooves and stress wear from hauling heavy sacks"
    elif shot_id in [78]:
        char_style = "flat muted colors"
        bg = "clean forensic laboratory background"
        action = "farmer skull jaw open showing severely decayed black tooth cavities, broken molars, and bone abscesses"
    elif shot_id in [79]:
        char_style = "flat muted colors"
        bg = "hearth cooking background with clay pot"
        action = "sticky wheat porridge bubbling thickly inside an ancient terracotta cooking pot over fire"
    elif shot_id in [80]:
        char_style = "cartoon bacteria bugs with pickaxes, flat muted colors"
        bg = "close-up yellowed tooth enamel background"
        action = "mischievous cartoon bacteria bugs chipping away at tooth enamel creating a deep dark cavity"
    elif shot_id in [81]:
        char_style = "flat muted colors"
        bg = "cross section bone diagram background"
        action = "anatomical cross section of jawbone showing painful dark abscess cavity eroding through bone"
    elif shot_id in [82]:
        char_style = "flat muted colors"
        bg = "macro bone texture background"
        action = "close-up of skull eye socket bone showing spongy sieve-like porous pitting texture"
    elif shot_id in [83]:
        char_style = "flat muted colors"
        bg = "medical reference chart background"
        action = "medical chart label pointing to bone porosity reading: Porotic Hyperostosis - Nutritional Stress"
    elif shot_id in [84]:
        char_style = "malnourished stick figure with hollow cheeks, flat muted colors"
        bg = "bare mud hut interior background with wooden spoon"
        action = "stick figure sitting sadly beside a bowl of plain gray boiled grain porridge looking frail and weak"
    elif shot_id in [85]:
        char_style = "flat muted colors"
        bg = "windy desert field background with cracked earth"
        action = "cracked ancient stone monument carved with wheat stalks crumbling into dusty pieces"
    elif shot_id in [86]:
        char_style = "farmer stick figure clutching aching lower back, flat muted colors"
        bg = "endless plowed wheat field background under blazing sun"
        action = "exhausted farmer standing in furrow clutching aching lower back with lightning pain zigzags"
    elif shot_id in [87]:
        char_style = "flat muted colors"
        bg = "circular nutritional chart background on clean paper"
        action = "colorful wheel chart displaying 80 different wild species: fruits, seeds, nuts, roots, fish, and meats"
    elif shot_id in [88]:
        char_style = "energetic prehistoric stick figure leaping over log, flat muted colors"
        bg = "lush green prehistoric forest background with sunbeams streaming through leaves"
        action = "healthy hunter leaping gracefully over a mossy fallen log with energetic strength"
    elif shot_id in [89]:
        char_style = "tall prehistoric stick figure smiling warmly, flat muted colors"
        bg = "open sunny river valley background with wildflowers and blue sky"
        action = "hunter standing tall in sunshine with clear healthy skin, upright posture, and smiling full teeth"
    elif shot_id in [90]:
        char_style = "mother holding infant gently, flat muted colors"
        bg = "warm prehistoric leather shelter interior background with glowing stone hearth"
        action = "mother sitting cross-legged near fire cradling baby wrapped in soft warm fur blanket"
    elif shot_id in [91]:
        char_style = "flat muted colors"
        bg = "grassy hillside background under soft blue sky with drifting clouds"
        action = "small gentle grave mound marked with smooth river stones and blooming wild mountain flowers"
    elif shot_id in [92]:
        char_style = "flat muted colors"
        bg = "chalkboard background with chalk dust"
        action = "chalkboard showing statistical math: high infant mortality dragging average lifespan down to 35"
    elif shot_id in [93]:
        char_style = "strong middle-aged hunter running with steady stride, flat muted colors"
        bg = "open grassy plain background with distant herd of deer"
        action = "healthy 50-year-old hunter running with effortless rhythmic stride across golden meadow"
    elif shot_id in [94]:
        char_style = "wise elder stick figure with white beard and animated gestures, flat muted colors"
        bg = "evening prehistoric camp background with glowing campfire and attentive listeners"
        action = "70-year-old hunter with long white beard gesturing expressively while telling story to young tribe members"
    elif shot_id in [95]:
        char_style = "calloused skilled hands of elder, flat muted colors"
        bg = "sunlit camp ground background"
        action = "close-up of elder hands skillfully whittling a smooth wooden bowl using a sharp flint scraper"
    elif shot_id in [96]:
        char_style = "modern stick figure tapping chin with thoughtful expression, flat muted colors"
        bg = "cozy modern study background with desk and glowing lightbulb"
        action = "modern stick figure tapping chin thoughtfully as glowing idea lightbulb appears overhead"

    # --- ACT 3: A DAY IN THE LIFE & THE 15-HOUR MATH (97 - 179) ---
    elif shot_id in [97]:
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
        action = "flock of birds silhouette flying across soft pale orange dawn sky as morning light touches the treetops"
    elif shot_id in [101]:
        char_style = "stick figure waking up gently with peaceful stretch, flat muted colors"
        bg = "shelter interior background with soft bedding of dried pine needles and furs"
        action = "prehistoric stick figure waking up gradually and sitting up with peaceful yawn on bed of leaves"
    elif shot_id in [102]:
        char_style = "flat muted colors"
        bg = "morning forest foliage background with sunlight flares"
        action = "macro close-up of glistening morning dewdrops on green leaves with golden sunlight refraction"
    elif shot_id in [103]:
        char_style = "two stick figures kneeling by hearth, flat muted colors"
        bg = "camp fire pit background with circular river stones and gray ash"
        action = "two stick figures gently blowing on red embers until a golden flame licks dry grass"
    elif shot_id in [104]:
        char_style = "group of five stick figures sitting in circle, flat muted colors"
        bg = "campground background around smoking hearth in morning light"
        action = "tribe members sitting together sharing a steamed broth from a hollow stone cup and chatting"
    elif shot_id in [105]:
        char_style = "hands sharing food wrapped in leaves, flat muted colors"
        bg = "camp hearth background with morning sunlight"
        action = "close-up of hands offering roasted hazelnuts and strips of dried venison wrapped in green leaves"
    elif shot_id in [106]:
        char_style = "stick figures laughing together, flat muted colors"
        bg = "prehistoric camp background with shelter in rear"
        action = "stick figure playfully puffing cheeks and imitating an animal while family members laugh"
    elif shot_id in [107]:
        char_style = "stick figure resting against tree trunk, flat muted colors"
        bg = "sunny forest clearing background with ancient oak tree"
        action = "stick figure leaning back against tree trunk with eyes closed and completely relaxed posture"
    elif shot_id in [108]:
        char_style = "flat muted colors"
        bg = "open blue sky background over autumn trees"
        action = "corporate clipboard with red URGENT stamp floating upward and dissolving into colorful autumn leaves"
    elif shot_id in [109]:
        char_style = "two hunters standing holding spears, flat muted colors"
        bg = "prehistoric camp edge background looking out at savannah"
        action = "two hunters standing up with wooden spears, inspecting flint points in morning sun"
    elif shot_id in [110]:
        char_style = "steady hands binding spearhead, flat muted colors"
        bg = "camp workspace background on wooden log"
        action = "close-up of hands tightly wrapping wet animal sinew cord around a sharp flint spear blade"
    elif shot_id in [111]:
        char_style = "three hunters walking abreast as equal partners, flat muted colors"
        bg = "wide golden African savannah background with dry grass and acacia trees"
        action = "three hunters walking side by side across sunny grassland with relaxed, confident strides"
    elif shot_id in [112]:
        char_style = "young hunter and elder kneeling, flat muted colors"
        bg = "sandy savannah dirt trail background"
        action = "young hunter watching respectfully as elder points to fresh animal footprint in sandy trail"
    elif shot_id in [113]:
        char_style = "three hunters jogging in rhythm, flat muted colors"
        bg = "open savannah trail background with heat shimmer on horizon"
        action = "three hunters moving in smooth, effortless rhythmic endurance jog along game trail"
    elif shot_id in [114]:
        char_style = "hunter kneeling and touching snapped twig, flat muted colors"
        bg = "thorny bush savannah background"
        action = "hunter touching broken branch and observing animal track with sharp focused senses"
    elif shot_id in [115]:
        char_style = "flat muted colors"
        bg = "sunny African savannah background with golden grassland, dry dirt game trail, sparse acacia trees, and pale blue sky"
        action = "anatomical diagram of upright human body with stylized sweat droplets showing full-body cooling system"
    elif shot_id in [116]:
        char_style = "hunter face in profile, flat muted colors"
        bg = "sunlit savannah trail background"
        action = "close-up profile of hunter forehead with tiny beads of sweat evaporating in gentle breeze"
    elif shot_id in [117]:
        char_style = "antelope sprinting with speed blur, flat muted colors"
        bg = "dusty savannah plain background"
        action = "antelope galloping with rapid speed lines kicking up dust cloud, leaving hunters far behind"
    elif shot_id in [118]:
        char_style = "antelope standing under bush panting, flat muted colors"
        bg = "hot dry savannah background with heat waves"
        action = "antelope standing in shade of thorny acacia bush panting heavily with tongue out and heat lines"
    elif shot_id in [119]:
        char_style = "two hunters walking steadily in background, flat muted colors"
        bg = "vast open savannah horizon background"
        action = "hunters maintaining steady, unhurried walking pace in the distance under hot sun"
    elif shot_id in [120]:
        char_style = "flat muted colors"
        bg = "sky background showing sun moving across daytime arc"
        action = "sun arc moving across sky from 10 AM to 2 PM while small hunter figures maintain steady jog"
    elif shot_id in [121]:
        char_style = "antelope lying down exhausted, flat muted colors"
        bg = "shady spot under acacia tree on dry grass"
        action = "exhausted antelope lying down safely in shade, completely overheated and unable to run further"
    elif shot_id in [122]:
        char_style = "group of women and older children walking with bags, flat muted colors"
        bg = "sun-dappled woodland background with birch tree trunks, green berry brambles, wildflowers, and soft mossy ground"
        action = "foraging party strolling peacefully through open woodland carrying woven plant fiber bags"
    elif shot_id in [123]:
        char_style = "flat muted colors"
        bg = "mental landscape map background"
        action = "stylized map diagram showing marked locations of wild berries, root clusters, beehives, and mushrooms"
    elif shot_id in [124]:
        char_style = "pointed wooden digging stick in dark soil, flat muted colors"
        bg = "forest floor soil background with fallen leaves"
        action = "wooden digging stick levering a plump wild root bulb cleanly out of moist dark earth"
    elif shot_id in [125]:
        char_style = "hands picking dark purple berries, flat muted colors"
        bg = "wild thorny bramble bush background with green leaves"
        action = "hands gently plucking ripe blackberries into a woven basket with sunlight filtering through"
    elif shot_id in [126]:
        char_style = "young boy pointing up at hollow tree, flat muted colors"
        bg = "ancient oak forest background"
        action = "boy pointing excitedly up into hollow tree trunk where wild golden honey drips down bark"
    elif shot_id in [127]:
        char_style = "mother feeding sweet berry to smiling child, flat muted colors"
        bg = "mossy fallen log in sunlit forest clearing background"
        action = "mother sitting on fallen log feeding a fresh wild berry to smiling child sitting beside her"
    elif shot_id in [128]:
        char_style = "flat muted colors"
        bg = "forest floor background"
        action = "woven basket overflowing with colorful wild harvest: orange roots, purple berries, nuts, and leafy greens"
    elif shot_id in [129]:
        char_style = "foraging group resting peacefully under grand oak tree, flat muted colors"
        bg = "lush shady forest canopy background"
        action = "women and children relaxing under large oak tree with full harvest bags sitting beside them"
    elif shot_id in [130]:
        char_style = "flat muted colors"
        bg = "clear blue sky background over tree canopy"
        action = "bright sun positioned just past noon mark in blue sky, indicating early afternoon"
    elif shot_id in [131]:
        char_style = "hunters and foragers walking along river trail, flat muted colors"
        bg = "riverbank trail background with flowing water and reeds"
        action = "both groups meeting on river trail walking back toward camp together laughing and sharing stories"
    elif shot_id in [132]:
        char_style = "camp hearth fire roaring with cooking spit, flat muted colors"
        bg = "prehistoric campsite background under afternoon sun"
        action = "campfire roaring with roasted meat cooking on wooden spit and wild roots baking in hot coals"
    elif shot_id in [133]:
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
    elif shot_id in [197]:
        char_style = "hands using stone pestle to grind pigments, flat muted colors"
        bg = "cave ground workspace background"
        action = "hands using stone pestle to grind black manganese and red ochre powders in stone bowl"
    elif shot_id in [198]:
        char_style = "artist using hollow bone tube to blow pigment, flat muted colors"
        bg = "rough limestone wall background with torchlight"
        action = "artist blowing red pigment spray through hollow bone tube against stone wall"
    elif shot_id in [199]:
        char_style = "flat muted colors"
        bg = "cave rock wall background illuminated by warm golden torchlight"
        action = "magnificent cave painting of galloping wild horses glowing in warm flickering torchlight"
    elif shot_id in [200]:
        char_style = "artist holding torch high admiring grand painted wall, flat muted colors"
        bg = "colossal painted cave chamber background"
        action = "artist stepping back with torch held high admiring completed painted wall with reverent joy"
    elif shot_id in [201]:
        char_style = "flat muted colors"
        bg = "clean display background on textured pelt"
        action = "detailed illustration of delicate prehistoric necklace crafted from polished wolf teeth and amber"
    elif shot_id in [202]:
        char_style = "flat muted colors"
        bg = "hand-drawn map background of snowy Russian plains"
        action = "map of Russian plains with pin labeled Sunghir 30,000 Years Ago"
    elif shot_id in [203]:
        char_style = "two prehistoric people in tailored fur parkas walking, flat muted colors"
        bg = "Ice Age tundra background with deep white snowdrifts, pine trees coated in frost, and cold twilight sky with soft green aurora"
        action = "two prehistoric hunters in tailored hooded fur parkas walking across snow-covered tundra"
    elif shot_id in [204]:
        char_style = "flat muted colors"
        bg = "archaeological grave excavation background"
        action = "overhead grave diagram showing two young skeletons laid out side by side surrounded by red ochre"
    elif shot_id in [205]:
        char_style = "flat muted colors"
        bg = "pale ivory bone background"
        action = "macro view of thousands of tiny polished mammoth ivory beads arranged in dense decorative rows"
    elif shot_id in [206]:
        char_style = "flint blade scoring curved mammoth tusk, flat muted colors"
        bg = "prehistoric workshop background on wood slab"
        action = "sharp flint stone burin tool carving precise grooves into a thick curved mammoth ivory tusk"
    elif shot_id in [207]:
        char_style = "modern researcher hands using flint chisel, flat muted colors"
        bg = "modern archaeology lab table background"
        action = "modern researcher hands using authentic flint chisel to shape small ivory bead replica"
    elif shot_id in [208]:
        char_style = "tiny flint drill bit piercing ivory bead, flat muted colors"
        bg = "macro workbench background"
        action = "close-up of tiny flint stone micro-drill piercing microscopic hole through delicate ivory bead"
    elif shot_id in [209]:
        char_style = "single polished ivory bead held between fingers, flat muted colors"
        bg = "soft light studio background"
        action = "single polished mammoth ivory bead held up between fingers showing silky smooth luster"
    elif shot_id in [210]:
        char_style = "flat muted colors"
        bg = "chalkboard background with white chalk math"
        action = "chalkboard calculation showing 10,000 beads multiplied by 45 minutes equals 7,500 hours of labor"
    elif shot_id in [211]:
        char_style = "stick figure standing thoughtfully looking down, flat muted colors"
        bg = "archaeological excavation site background"
        action = "stick figure standing in quiet contemplation looking down at the magnificent ancient grave"
    elif shot_id in [212]:
        char_style = "gentle elder sitting by fire carving ivory bead, flat muted colors"
        bg = "warm winter hearth interior background"
        action = "gentle elder sitting by fire patiently shaping an ivory bead and dropping it into a full bowl"
    elif shot_id in [213]:
        char_style = "hands using bone needle to sew ivory beads on garment, flat muted colors"
        bg = "cozy fur shelter background"
        action = "hands using delicate bone needle and sinew to sew rows of ivory beads onto soft fur parka"
    elif shot_id in [214]:
        char_style = "flat muted colors"
        bg = "snowy forest burial mound background under winter sky"
        action = "soft white snowflakes falling gently over burial mound marked with upright mammoth tusk"
    elif shot_id in [215]:
        char_style = "stick figure standing tall looking up at green aurora ribbons, flat muted colors"
        bg = "freezing Arctic night sky background with vibrant green aurora borealis"
        action = "stick figure standing proudly on snow looking up in awe at glowing northern lights"
    elif shot_id in [216]:
        char_style = "group of tribe members in fur coats embracing near fire, flat muted colors"
        bg = "snowy camp background with warm roaring fire"
        action = "family members sitting close together embracing warmly beside roaring campfire in snow"
    elif shot_id in [217]:
        char_style = "flat muted colors"
        bg = "close-up of glowing orange and red charcoal embers crackling in campfire"
        action = "macro shot of radiant glowing orange and red charcoal embers with tiny heat sparks"
    elif shot_id in [218]:
        char_style = "flat muted colors"
        bg = "academic desk background"
        action = "illustrated journal cover of PNAS reading: Embers of Society by Polly Wiessner"
    elif shot_id in [219]:
        char_style = "flat muted colors"
        bg = "sandy desert campsite background"
        action = "vintage audio cassette recorder with reels turning on sand beside campfire logs"
    elif shot_id in [220]:
        char_style = "flat muted colors"
        bg = "open field notebook background"
        action = "notebook page split into two neat columns comparing daytime conversations with nighttime conversations"
    elif shot_id in [221]:
        char_style = "two stick figures gesturing while dividing meat, flat muted colors"
        bg = "daytime camp ground background under bright sun"
        action = "two figures standing over cuts of meat in daylight gesturing with hands dividing portions"
    elif shot_id in [222]:
        char_style = "flat muted colors"
        bg = "daytime speech bubble over camp background"
        action = "speech bubble filled with practical work icons: firewood, animal tracks, water gourd, digging stick"
    elif shot_id in [223]:
        char_style = "stick figure rolling eyes while another complains, flat muted colors"
        bg = "African village camp background in late afternoon turning to deep violet twilight, with thatch huts and dry savannah horizon"
        action = "stick figure rolling eyes with crossed arms while another gestures with irritated complaint lines"
    elif shot_id in [224]:
        char_style = "modern office stick figures gossiping, flat muted colors"
        bg = "modern office breakroom background with water cooler"
        action = "two office workers holding coffee cups gossiping beside water cooler with comic speech bubbles"
    elif shot_id in [225]:
        char_style = "flat muted colors"
        bg = "dramatic sunset horizon background turning from bright orange into deep indigo twilight"
        action = "sun dipping beneath distant horizon turning savannah sky from blazing orange to deep violet"
    elif shot_id in [226]:
        char_style = "hands placing wooden digging tools on ground at dusk, flat muted colors"
        bg = "campground twilight background"
        action = "close-up of hands laying wooden digging sticks and spears on ground as darkness falls"
    elif shot_id in [227]:
        char_style = "warm circle of ten stick figures sitting close together, flat muted colors"
        bg = "prehistoric night campsite background with dark navy blue sky, small white crescent moon, star dots, and faint leather teepee huts in the background"
        action = "warm glowing orange campfire in center casting golden light onto circle of stick figures listening to story"
    elif shot_id in [228]:
        char_style = "elder stick figure standing near fire gesturing, flat muted colors"
        bg = "campfire night background with flickering shadows on ground"
        action = "elder stick figure standing near fire with expressive arms raised telling dramatic epic tale"
    elif shot_id in [229]:
        char_style = "elder pointing up to night sky where stars glow, flat muted colors"
        bg = "dark night sky background with brilliant constellations"
        action = "elder pointing up into starry sky where connected star dots form glowing constellation of hunters"
    elif shot_id in [230]:
        char_style = "young stick figure puffing cheeks imitating funny animal, flat muted colors"
        bg = "warm campfire circle background"
        action = "young man puffing cheeks and waving ears imitating warthog as entire tribe erupts in laughter"
    elif shot_id in [231]:
        char_style = "two women clapping rhythm sticks and singing, flat muted colors"
        bg = "firelit night camp background"
        action = "two women clapping hollow wooden sticks together in musical rhythm, singing with open mouths"
    elif shot_id in [232]:
        char_style = "two men who previously argued now smiling and sharing drink, flat muted colors"
        bg = "warm campfire circle background"
        action = "two men who argued during day now smiling and clinking wooden cups together by fire"
    elif shot_id in [233]:
        char_style = "golden embers drifting up into starry galaxy, flat muted colors"
        bg = "deep night sky background filled with Milky Way galaxy"
        action = "glowing golden embers and sparks rising gracefully from campfire into vast swirling galaxy"
    elif shot_id in [234]:
        char_style = "flat muted colors"
        bg = "wooden platter on grass background"
        action = "clean illustration of roasted wild root and lean venison steak on rustic wooden tray"
    elif shot_id in [235]:
        char_style = "warm radiant glow of campfire illuminating circle of smiling faces, flat muted colors"
        bg = "night campsite background with dark shadows"
        action = "radiant golden firelight illuminating a circle of united smiling human faces connected in song"
    elif shot_id in [236]:
        char_style = "flat muted colors"
        bg = "wide landscape view of three glowing campfire dots under starry night sky"
        action = "panoramic night view showing three small warm campfire lights glowing on vast dark plains under stars"

    # --- ACT 5: THE LOST ARCHITECTURE OF SLEEP (237 - 265) ---
    elif shot_id in [237]:
        char_style = "figures curling up in soft furs around stones, flat muted colors"
        bg = "tranquil night camp background with dark charcoal night sky, silver crescent moon, scattered white star dots, and soft dying embers"
        action = "campfire coals fading to gentle deep red as tribe members curl up under fur blankets around hearth"
    elif shot_id in [238]:
        char_style = "flat muted colors"
        bg = "night sky background over peaceful sleeping camp"
        action = "slender white crescent moon shining softly over sleeping prehistoric campsite under open sky"
    elif shot_id in [239]:
        char_style = "modern stick figure sitting up in bed with panic eyes, flat muted colors"
        bg = "simple hand-drawn modern dark bedroom background with streetlamp light filtering through window blinds and glowing blue alarm clock on nightstand"
        action = "modern stick figure sitting bolt upright in bed in pitch black room with eyes wide in sudden panic"
    elif shot_id in [240]:
        char_style = "flat muted colors"
        bg = "dark bedroom nightstand background"
        action = "digital alarm clock glowing 03:14 in bright electric blue digits across dark bedroom"
    elif shot_id in [241]:
        char_style = "frustrated stick figure holding head as countdown clock ticks, flat muted colors"
        bg = "dark bedroom background with floating math formulas"
        action = "stick figure gripping head with math formula overlay showing countdown of 3 hours left before alarm"
    elif shot_id in [242]:
        char_style = "tangled stick figure kicking bedsheets with frustration, flat muted colors"
        bg = "bedroom bed background in dark shadows"
        action = "stick figure tangled in twisted bedsheets, kicking pillow in frustration with angry squiggly lines"
    elif shot_id in [243]:
        char_style = "flat muted colors"
        bg = "modern nightstand background with lamp and water glass"
        action = "prescription pill bottle labeled SLEEP AID sitting beside water glass on modern nightstand"
    elif shot_id in [244]:
        char_style = "cartoon alarm clock jumping and ringing with soundwaves, flat muted colors"
        bg = "bedroom background with waking stick figure"
        action = "cartoon alarm clock jumping up and down vibrating furiously with harsh jagged ringing lines"
    elif shot_id in [245]:
        char_style = "flat muted colors"
        bg = "vintage woodcut illustration background on aged parchment"
        action = "woodcut illustration of 16th-century peasants waking peacefully by candlelight at midnight"
    elif shot_id in [246]:
        char_style = "flat muted colors"
        bg = "circadian sleep research laboratory background with calm blue ambient lighting and digital brainwave monitor screens"
        action = "sleep clinic monitor displaying natural two-wave circadian brainwave sleep cycle graphs"
    elif shot_id in [247]:
        char_style = "flat muted colors"
        bg = "sleep cycle timeline background on clean paper"
        action = "two smooth rhythmic wave graphs along timeline labeled First Sleep and Second Sleep"
    elif shot_id in [248]:
        char_style = "hunter curling up peacefully under fur blanket, flat muted colors"
        bg = "prehistoric shelter background as dusk turns to deep night"
        action = "ancient hunter curling up comfortably under reindeer pelt as twilight fades into silent night"
    elif shot_id in [249]:
        char_style = "hunter opening eyes smoothly without alarm, flat muted colors"
        bg = "moonlit prehistoric shelter interior background"
        action = "hunter opening eyes calmly and feeling completely refreshed in soft blue moonlight"
    elif shot_id in [250]:
        char_style = "two figures awake in moonlit camp, flat muted colors"
        bg = "peaceful midnight campsite background under brilliant silver starry sky, with soft glowing campfire coals and quiet tents"
        action = "gentle moonlight illuminating quiet campsite where two figures sit peacefully by glowing coals"
    elif shot_id in [251]:
        char_style = "calm stick figure taking deep breath looking up at stars, flat muted colors"
        bg = "open wilderness night sky background with Milky Way"
        action = "hunter standing outside tent taking slow deep breath while looking up at brilliant silver galaxy"
    elif shot_id in [252]:
        char_style = "gentle hands placing two dry sticks on embers watching golden flame, flat muted colors"
        bg = "hearth stones background in soft darkness"
        action = "gentle hands placing two small dry branches on glowing embers, watching tiny golden flame flicker"
    elif shot_id in [253]:
        char_style = "hunter taking slow refreshing sip from leather canteen, flat muted colors"
        bg = "night camp background under starry sky"
        action = "hunter kneeling beside stone hearth taking a slow refreshing drink of cold water from canteen"
    elif shot_id in [254]:
        char_style = "two stick figures sitting back to back under blanket whispering softly, flat muted colors"
        bg = "moonlit tent exterior background with soft embers"
        action = "two figures sitting together wrapped in fur blanket, whispering softly with affectionate smiles"
    elif shot_id in [255]:
        char_style = "shooting star streaking across deep velvet sky framed by tree branches, flat muted colors"
        bg = "deep midnight sky background with silhouetted trees"
        action = "shooting star leaving brilliant white streak across deep velvet night sky framed by quiet branches"
    elif shot_id in [256]:
        char_style = "flat muted colors"
        bg = "anatomical brain cross section background"
        action = "brain illustration glowing with serene soft blue light showing release of prolactin and oxytocin"
    elif shot_id in [257]:
        char_style = "peaceful stick figure with closed eyes surrounded by soft radiant aura, flat muted colors"
        bg = "calm midnight wilderness background"
        action = "stick figure sitting in peaceful meditation surrounded by gentle radiant aura of deep calm"
    elif shot_id in [258]:
        char_style = "hunter yawning contentedly and pulling furry blanket back over shoulders, flat muted colors"
        bg = "cozy shelter interior background in moonlight"
        action = "hunter yawning softly and crawling back under warm fur covers feeling pleasantly drowsy"
    elif shot_id in [259]:
        char_style = "hunter sleeping deeply with peaceful smile as night sky turns soft blue, flat muted colors"
        bg = "shelter interior background with pre-dawn light"
        action = "hunter fast asleep with relaxed peaceful smile as stars slowly fade outside tent"
    elif shot_id in [260]:
        char_style = "first ray of golden morning sun entering shelter illuminating face, flat muted colors"
        bg = "shelter opening background at dawn"
        action = "first beam of warm morning sunlight entering shelter opening, illuminating smiling waking face"
    elif shot_id in [261]:
        char_style = "flat muted colors"
        bg = "modern glass skyscraper city background at night with thousands of blinding electric windows and streetlights"
        action = "sprawling modern metropolis blazing with millions of harsh electric office windows and streetlights"
    elif shot_id in [262]:
        char_style = "stick figure running frantically on treadmill inside giant ticking clock, flat muted colors"
        bg = "conceptual clock interior background"
        action = "exhausted stick figure running on treadmill inside giant ticking alarm clock mechanism"
    elif shot_id in [263]:
        char_style = "stick figure staring at ceiling illuminated by harsh streetlamp light, flat muted colors"
        bg = "dark bedroom background with orange light through window"
        action = "stick figure staring blankly at bedroom ceiling illuminated by harsh orange streetlamp glare"
    elif shot_id in [264]:
        char_style = "flat muted colors"
        bg = "medical clipboard background"
        action = "doctor notepad with bold red handwritten word INSOMNIA circled with red marker pen"
    elif shot_id in [265]:
        char_style = "silhouette of ancient hunter standing in quiet wilderness under stars, flat muted colors"
        bg = "peaceful wilderness under night sky background with deep velvet blue sky, brilliant silver Milky Way galaxy, and silhouetted tree branches"
        action = "silhouette of ancient hunter standing tall under vast starlit sky, breathing in deep silent peace"

    # --- ACT 6: THE AGRICULTURAL TRAP (266 - 315) ---
    elif shot_id in [266]:
        char_style = "flat muted colors"
        bg = "prehistoric river valley background with dramatic dark storm clouds gathering over golden grassy plains"
        action = "dramatic dark storm clouds gathering ominous shadows over wide golden river valley plains"
    elif shot_id in [267]:
        char_style = "joyful hunter family relaxing and laughing by sunny riverbank, flat muted colors"
        bg = "sunny prehistoric river landscape background with wildflowers"
        action = "hunter family skipping flat stones across river and laughing together in warm sunshine"
    elif shot_id in [268]:
        char_style = "flat muted colors"
        bg = "muddy agricultural plowed furrow background"
        action = "large hand-drawn black ink question mark planted into wet furrowed agricultural soil"
    elif shot_id in [269]:
        char_style = "split comparison: hunter with spear vs farmer collapsed over plow, flat muted colors"
        bg = "split background: sunny savannah vs muddy field"
        action = "side-by-side: hunter whistling freely with spear vs farmer collapsed exhausted over wooden plow"
    elif shot_id in [270]:
        char_style = "flat muted colors"
        bg = "ancient village perimeter background with wooden fence"
        action = "heavy rustic wooden gate swinging open slowly into muddy fenced animal pen"
    elif shot_id in [271]:
        char_style = "flat muted colors"
        bg = "dirt ground forest background"
        action = "primitive deadfall trigger trap made of heavy wooden log, trigger stick, and stone weight"
    elif shot_id in [272]:
        char_style = "flat muted colors"
        bg = "conceptual time background on clean paper"
        action = "hourglass with golden grains of sand falling slowly one by one into an accumulating deep pile"
    elif shot_id in [273]:
        char_style = "flat muted colors"
        bg = "map of Fertile Crescent with wild wheat grasses growing across green hills"
        action = "hand-drawn map of ancient Near East showing green hills where wild cereal grains grow naturally"
    elif shot_id in [274]:
        char_style = "flat muted colors"
        bg = "cracked dry earth background with withered prehistoric brush under harsh sun"
        action = "severe drought scene with parched cracked mud and dried wild bushes showing climate swing"
    elif shot_id in [275]:
        char_style = "hand gently brushing over ripe wild wheat stalks, flat muted colors"
        bg = "riverbank garden background with damp muddy soil furrows, small wild wheat plots, and woven twig fences"
        action = "fingers gently stroking golden ears of wild wheat growing in moist soil along riverbank"
    elif shot_id in [276]:
        char_style = "flat muted colors"
        bg = "underground pit cross section background"
        action = "stone storage pit dug into earth lined with dry straw filled to brim with harvested wheat grains"
    elif shot_id in [277]:
        char_style = "stick figure carrying two clay pots of water pouring on grain plot, flat muted colors"
        bg = "riverbank garden plot background with small fence"
        action = "stick figure carrying two clay jars pouring river water onto a small patch of green wheat grass"
    elif shot_id in [278]:
        char_style = "hands separating fat wheat grains from dry chaff into small bowl, flat muted colors"
        bg = "rustic shelter floor background"
        action = "careful hands selecting the largest, plumpest seeds from harvested chaff into a clay bowl"
    elif shot_id in [279]:
        char_style = "stick figure smiling proudly with hands on hips looking at garden plot, flat muted colors"
        bg = "small fenced riverbank garden background"
        action = "stick figure standing proudly with hands on hips admiring small thriving plot of cultivated grain"
    elif shot_id in [280]:
        char_style = "flat muted colors"
        bg = "warm shelter interior background with small hearth fire"
        action = "large terracotta jar filled with dry grain sitting safely inside cozy winter shelter beside hearth"
    elif shot_id in [281]:
        char_style = "flat muted colors"
        bg = "clean off-white background with subtle red aura"
        action = "single ear of ripe golden wheat isolated with a subtle ominous red glowing outline"
    elif shot_id in [282]:
        char_style = "mother holding child in forest setting with gentle nurturing atmosphere, flat muted colors"
        bg = "lush green forest clearing background"
        action = "hunter mother sitting against tree nursing a four-year-old child in peaceful forest"
    elif shot_id in [283]:
        char_style = "flat muted colors"
        bg = "growth chart diagram background"
        action = "child growth timeline chart showing weaning milestone occurring naturally at the age 4 mark"
    elif shot_id in [284]:
        char_style = "small group of 25 stick figures walking peacefully through vast landscape, flat muted colors"
        bg = "wide untouched savannah valley background"
        action = "small band of twenty-five hunter-gatherers walking peacefully across vast green valley"
    elif shot_id in [285]:
        char_style = "clay spoon feeding soft cooked grain porridge to small infant, flat muted colors"
        bg = "mud hut interior background with ceramic pots"
        action = "mother using ceramic spoon to feed warm soft cooked grain porridge to a one-year-old baby"
    elif shot_id in [286]:
        char_style = "smiling baby sitting on mat eating warm porridge with ceramic spoon, flat muted colors"
        bg = "mud-brick house floor background"
        action = "happy chubby infant sitting on straw mat happily eating porridge from a terracotta bowl"
    elif shot_id in [287]:
        char_style = "flat muted colors"
        bg = "weaning timeline comparison chart background"
        action = "growth chart arrow dropping sharply from age 4 milestone down to age 1 milestone"
    elif shot_id in [288]:
        char_style = "flat muted colors"
        bg = "population timeline diagram background"
        action = "timeline packed tightly with baby icons appearing in rapid succession every eighteen months"
    elif shot_id in [289]:
        char_style = "crowd diagram showing stick figure population multiplying exponentially, flat muted colors"
        bg = "village settlement layout background"
        action = "crowd visualization showing stick figure icons multiplying rapidly from 25 to 75 to 300"
    elif shot_id in [290]:
        char_style = "small simple camp of five leather tents by riverbank, flat muted colors"
        bg = "peaceful river valley background with forest"
        action = "small quaint hunter camp with five leather teepee shelters nestled beside clean river"
    elif shot_id in [291]:
        char_style = "crowded ancient mud-brick village with dozens of packed houses, flat muted colors"
        bg = "crowded ancient Neolithic village background with packed mud-brick flat-roof houses, narrow dirt alleys, and ceramic storage jars"
        action = "dense mud-brick agricultural town with packed flat roofs, narrow muddy alleys, and crowds of people"
    elif shot_id in [292]:
        char_style = "flat muted colors"
        bg = "dusty dirt ground background"
        action = "heavy wooden deadfall animal trap crashing down violently onto the ground with dust cloud"
    elif shot_id in [293]:
        char_style = "hunters standing in barren forest looking around with empty hands no game, flat muted colors"
        bg = "cleared stump forest background with no wildlife"
        action = "three hunters standing with spears looking around an overhunted empty forest with zero game"
    elif shot_id in [294]:
        char_style = "flat muted colors"
        bg = "bare trampled muddy earth background"
        action = "empty woven basket lying upside down on bare trampled dirt with no edible roots in sight"
    elif shot_id in [295]:
        char_style = "stick figure trying to walk toward forest blocked by crowd of villagers, flat muted colors"
        bg = "village boundary edge background"
        action = "stick figure trying to walk toward green woods but blocked by a dense crowd of hungry villagers"
    elif shot_id in [296]:
        char_style = "worried mother surrounded by three small hungry children crying for food, flat muted colors"
        bg = "mud hut doorway background"
        action = "distressed mother standing outside hut surrounded by crying hungry toddlers pulling at her skirt"
    elif shot_id in [297]:
        char_style = "stick figure standing in field with heavy wooden hoe looking trapped, flat muted colors"
        bg = "extensive agricultural field background with plowed brown mud furrows, rows of ripe golden wheat, and distant hazy hills under hot sun"
        action = "stick figure standing exhausted in mud furrow holding a heavy wooden hoe, shoulders slumped in defeat"
    elif shot_id in [298]:
        char_style = "two men straining forward pulling heavy wooden plow through thick mud, flat muted colors"
        bg = "endless muddy agricultural field background"
        action = "two farmers straining with ropes pulling a heavy wooden plow through thick wet clay soil"
    elif shot_id in [299]:
        char_style = "stick figure crawling on knees under scorching sun pulling weeds from wheat, flat muted colors"
        bg = "dense wheat field background under blazing sun"
        action = "farmer on hands and knees pulling stubborn thorny weeds from wheat rows under baking heat"
    elif shot_id in [300]:
        char_style = "stick figure carrying heavy wooden yoke with two sloshing water buckets, flat muted colors"
        bg = "irrigation canal background in agricultural field"
        action = "farmer with shaking legs carrying a heavy wooden yoke across shoulders with two full water buckets"
    elif shot_id in [301]:
        char_style = "massive stone storehouse with doorway showing stacks of grain sacks, flat muted colors"
        bg = "ancient village center background with stone buildings"
        action = "massive multi-story stone granary storehouse with open doors revealing hundreds of grain sacks"
    elif shot_id in [302]:
        char_style = "workers climbing wooden ladder carrying heavy grain baskets into silo, flat muted colors"
        bg = "tall granary tower background"
        action = "line of workers climbing high wooden ladder carrying heavy woven grain baskets into silo roof"
    elif shot_id in [303]:
        char_style = "shadowy figures on distant hilltop watching stone granary with greedy eyes, flat muted colors"
        bg = "desert ridge background overlooking village"
        action = "silhouette raiders holding clubs standing on distant ridge watching the village grain storehouse"
    elif shot_id in [304]:
        char_style = "raiders with clubs and torches charging toward ancient village gate, flat muted colors"
        bg = "village perimeter wall background at dusk"
        action = "band of raiders brandishing torches and wooden clubs charging toward village gate"
    elif shot_id in [305]:
        char_style = "workers lifting heavy stone blocks building high defensive wall around village, flat muted colors"
        bg = "ancient fortified city background with massive stone perimeter walls, wooden granary towers, and battlements under hazy sky"
        action = "team of workers using wooden levers to hoist giant limestone blocks to build a high perimeter wall"
    elif shot_id in [306]:
        char_style = "two armed guards with copper spears standing atop stone watchtower, flat muted colors"
        bg = "stone city wall battlements background under blue sky"
        action = "two guards holding long spears standing vigilant atop the stone battlements of the city wall"
    elif shot_id in [307]:
        char_style = "ancient scribe holding stylus pressing tally marks into wet clay tablet, flat muted colors"
        bg = "palace archive room background with clay tablet shelves"
        action = "scribe sitting cross-legged pressing cuneiform numbers and grain counts into a wet clay tablet"
    elif shot_id in [308]:
        char_style = "official taking grain sacks from humble farmer family standing outside hut, flat muted colors"
        bg = "mud-brick village street background"
        action = "stern official in robes taking half the grain sacks from a weeping farmer family outside their hut"
    elif shot_id in [309]:
        char_style = "king sitting on carved stone throne holding royal scepter giving orders, flat muted colors"
        bg = "grand ancient palace hall background with stone pillars"
        action = "king crowned in gold sitting on high stone throne pointing royal scepter to command soldiers"
    elif shot_id in [310]:
        char_style = "flat muted colors"
        bg = "split background connecting field to stone palace"
        action = "heavy iron chain wrapping around farmer wooden hoe and extending directly to the king palace gate"
    elif shot_id in [311]:
        char_style = "flat muted colors"
        bg = "overhead valley map background carved into geometric parcels"
        action = "illustrated map of green valley divided into rigid square parcels by stone walls and boundary markers"
    elif shot_id in [312]:
        char_style = "flat muted colors"
        bg = "ancient stone city square background"
        action = "stone sundial in city square casting a sharp dark shadow marking the rigid division of hours"
    elif shot_id in [313]:
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
    else: # 334    else: # 334
        char_style = "prehistoric hunter family laughing warmly together around glowing hearth, flat muted colors"
        bg = "simple hand-drawn peaceful wilderness landscape background at dusk with curling wisps of woodsmoke"
        action = "simple retro alarm clock doodle dissolving softly into a curling wisp of campfire smoke over wide open wilderness"

    prompt = f"Minimalist hand-drawn 2D vector illustration, clean bold black ink comic line art, {char_style}, {bg}, {action}, full bleed edge-to-edge composition, no borders, no frames, widescreen 16:9 aspect ratio"
    return prompt

# Read the current CSV
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
    
    new_prompt = get_shot_elements(shot_id, text, visual)
    updated_rows.append([shot_id, time_str, text, visual, new_prompt])

# Write updated CSV
with open('storyboard_master.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(updated_rows)

# Write updated Markdown
with open('storyboard_master.md', 'w', encoding='utf-8') as f:
    f.write("# Master Production Storyboard (334 Full-Bleed Hand-Drawn Prompts)\n\n")
    f.write("| Shot | Time | Spoken VO script | Visual description | Exact Prompt for google nano banana pro |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- |\n")
    for r in updated_rows:
        t_clean = r[2].replace("|", "/")
        v_clean = r[3].replace("|", "/")
        p_clean = r[4].replace("|", "/")
        f.write(f"| {r[0]} | {r[1]} | {t_clean} | {v_clean} | `{p_clean}` |\n")

print(f"Successfully converted all {len(updated_rows)} prompts to Full-Bleed Edge-to-Edge format!")

