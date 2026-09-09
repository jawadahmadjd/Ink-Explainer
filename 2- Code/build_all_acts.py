import csv
import os

# Complete script and shot generation for the full 11m 12s video (350 shots)
# Timing rule: 1000 characters = 60 seconds (1 sec = 16.6667 chars)

acts = []

# ==========================================
# ACT 1: THE MODERN GRID VS THE OPEN HORIZON (00:00 - 01:20) ~42 shots
# ==========================================
act1 = [
    ("Right now, your entire existence is sliced", "Close-up of a digital alarm clock display flashing red digits on a nightstand.", "digital alarm clock flashing red 06:30 AM numbers on a dark wooden nightstand"),
    ("into little colored boxes on a glowing screen.", "Stick figure staring anxiously at a smartphone calendar packed with multicolored blocks.", "stick figure sitting in bed staring at glowing smartphone screen filled with colored calendar blocks"),
    ("Before your feet even hit the floor,", "Stick figure swinging legs out of bed onto cold wooden floor, rubbing tired eyes.", "stick figure in pajamas swinging feet onto bedroom floor looking exhausted and rubbing eyes"),
    ("you glanced at a glowing rectangle", "Hand holding a bright smartphone illuminating a dark bedroom in cold blue light.", "hand holding a glowing smartphone screen casting blue light on dark bedroom wall"),
    ("to see who owns your morning,", "A digital notification popup showing an urgent corporate email reminder.", "doodle of an urgent corporate calendar notification alert box with exclamation mark"),
    ("who owns your afternoon,", "Calendar app zooming in to show back-to-back meetings from noon to five.", "smartphone calendar showing packed schedule with no gaps between meetings"),
    ("and how many minutes you are permitted to eat lunch.", "A lonely sandwich in plastic wrap sitting next to a desk clock counting down 15 minutes.", "plastic wrapped sandwich sitting next to a small ticking desk clock"),
    ("You sprint through honking traffic,", "Stick figure gripping steering wheel in bumper-to-bumper city traffic jam.", "stick figure gripping steering wheel of car trapped in traffic jam with anger lines"),
    ("cram onto a crowded commuter train,", "Stick figure squished between faceless subway passengers staring down at phones.", "crowded subway car interior with stick figures packed tightly together staring down at screens"),
    ("and trade eight to ten hours of your waking life", "Stick figure hunched over a laptop under harsh fluorescent office ceiling lights.", "stick figure sitting at office cubicle typing on laptop under buzzing fluorescent lights"),
    ("answering messages from people you have never touched.", "Floating chat bubbles and unread notification badges multiplying around a stressed stick figure.", "stressed stick figure surrounded by floating unread chat bubble icons and email badges"),
    ("And tonight, before you finally close your eyes,", "Stick figure lying in bed in the dark, finger hovering over smartphone screen.", "stick figure lying in bed in dark room illuminated by faint phone screen"),
    ("you will set that same machine to scream at you again.", "Close-up of finger sliding an alarm toggle switch to ON for 06:00 AM.", "finger sliding digital smartphone toggle switch to enable morning alarm"),
    ("Now, rewind forty-five thousand years.", "Screen wipe transition: modern bedroom dissolves into an ancient limestone bluff.", "transitional doodle of modern clock dissolving into swirling prehistoric dust and river valley"),
    ("A man wakes up in the soft morning light.", "Paleolithic hunter-gatherer opening his eyes peacefully on a grassy hill at sunrise.", "prehistoric stick figure with wild hair opening eyes peacefully on hill at golden sunrise"),
    ("No alarm. No schedule. No calendar.", "Open horizon with pink and gold sky, gentle morning mist over distant trees.", "wide panoramic savannah landscape at dawn with soft pink clouds and gentle river mist"),
    ("Nowhere on planet Earth he is required to be.", "The hunter standing freely on a ridge, hands on hips, looking across endless wilderness.", "prehistoric stick figure standing tall on cliff edge looking across vast untouched valley"),
    ("He owns a flint spear, two animal hides, and a fire.", "Isolated spot illustration of a knapped flint spear, folded reindeer pelt, and small smoking hearth.", "isolated knapped flint spear, folded furry animal pelt, and ring of campfire stones"),
    ("He sits up, stretches his arms toward the sun,", "Hunter stretching his spine and yawning comfortably in the morning warmth.", "prehistoric stick figure stretching arms wide and yawning happily under warm morning sun"),
    ("and asks himself a question you have never been free to ask:", "Close-up of hunter's curious, peaceful face with hand resting on chin.", "curious expressive stick figure with thoughtful face looking up at clouds"),
    ("What do I actually want to do today?", "Bold conceptual thought bubble showing fishing, walking, or resting under a tree.", "thought bubble showing three choices: a river fish, a mountain trail, and a shady tree"),
    ("Now, your modern brain is already fighting this.", "Modern stick figure sitting on sofa with crossed arms, looking skeptical and frowning.", "modern stick figure with crossed arms looking skeptical with question marks around head"),
    ("You are thinking: Sure, that sounds idyllic,", "Thought bubble above modern person showing a stick figure running from a cartoon lion.", "modern stick figure imagining a terrified stick figure running away from a roaring lion"),
    ("but they died at twenty-five, froze in muddy caves,", "Doodle of a stick figure shivering in a dark cave with icicles.", "cartoon stick figure shivering in cave wrapped in thin blanket with cold wind lines"),
    ("and spent every waking second on the edge of starvation.", "Stick figure holding an empty wooden bowl with rumbling stomach lines.", "stick figure looking down at empty wooden bowl with dizzy hungry expression"),
    ("That is the story we tell ourselves to cope.", "An open history book with a giant red 'MYTH' stamp stamped across the page.", "old open textbook with red ink stamp saying myth across hand-drawn diagrams"),
    ("The comforting myth that history is a straight line", "A tilted ramp line going from primitive ape to modern businessman at computer.", "diagram of evolution ramp from hunched stick figure to modern stick figure at office desk"),
    ("from pure ancient misery to modern paradise.", "Modern stick figure sitting at desk looking stressed despite surrounded by gadgets.", "modern stick figure at desk surrounded by microwave, vacuum, phone, looking miserable"),
    ("We tell ourselves that our forty-hour work week", "Clock face turning like a hamster wheel with stick figure running inside.", "giant ticking clock gear turning into a hamster wheel with tired stick figure running inside"),
    ("is the price we pay for escaping prehistoric suffering.", "A bill receipt with bold red total: 'FORTY HOURS PER WEEK FOR SURVIVAL'.", "hand-drawn paper bill receipt stamped with red bold letters payment for comfort"),
    ("We assume ancient humans were wretched beasts", "Primitive ape-like figure dragging knuckles in mud with confused look.", "hunched stick figure dragging knuckles in muddy puddle with exaggerated confused expression"),
    ("who never had five minutes to sit in peace.", "Stick figure running in panic between falling rocks and roaring predators.", "stick figure running frantically between falling boulders and cartoon storm clouds"),
    ("We tell ourselves that technology set us free.", "A smartphone, microwave, vacuum cleaner, and laptop smiling in a cheerful row.", "smiling lineup of modern household appliances: smartphone, microwave, dishwasher, laptop"),
    ("We tell ourselves that progress bought us leisure.", "A hammock hanging between two palm trees with a giant red 'UNAVAILABLE' tag.", "beach hammock between two palm trees marked with bright red unavailable label tag"),
    ("And we wear our chronic exhaustion like a badge of honor.", "Modern stick figure proudly wearing a medal that says 'BURNOUT & 60 HOURS'.", "tired stick figure proudly displaying a gold medal that reads burned out and exhausted"),
    ("Because admitting the alternative is terrifying.", "Modern person staring into empty coffee mug with existential dread.", "modern stick figure staring deeply into empty white ceramic coffee cup with wide eyes"),
    ("Admitting that a caveman might have been freer than you", "Stick figure looking through window bars at an ancient hunter running on hill.", "modern person looking through window prison bars at free ancient hunter running across ridge"),
    ("breaks the fundamental promise of modern society.", "A glowing golden contract tearing down the middle into two ragged pieces.", "parchment paper contract with official seal tearing in half down the center"),
    ("So we cling to the myth of the brutal Stone Age.", "A shield with the word 'EXCUSES' protecting a stressed office worker.", "wooden defense shield labeled excuses held in front of tired office worker"),
    ("We tell ourselves they had no time to live.", "A cartoon tombstone marked: 'NO LEISURE, ONLY TOIL'.", "stone gravestone marked with text no free time only endless prehistoric toil"),
    ("But when bioarchaeologists actually dig into the earth,", "Archaeologist with sun hat kneeling in excavation trench carefully brushing soil with trowel.", "cartoon archaeologist in explorer hat using small trowel to brush away dirt in archaeological trench"),
    ("the physical evidence tells the exact opposite story.", "Two ancient grave pits uncovered in dry desert soil, revealing pristine fossil bones.", "archaeological excavation showing two exposed ancient graves in layered earth strata"),
    ("Because dirt doesn't lie. Look at the bones.", "Close-up of clean human fossil bones resting in excavated sediment.", "macro shot of ancient fossil human bones uncovered in clean archaeological sediment")
]
acts.append(("ACT 1: The Modern Grid vs The Open Horizon", act1))

# ==========================================
# ACT 2: FORENSIC AUTOPSY — THE DIRT DOESN'T LIE (01:20 - 03:00) ~50 shots
# ==========================================
act2 = [
    ("In the late twentieth century, bioarchaeologists began", "A laboratory table with magnifying lenses, calipers, and prehistoric skull specimens.", "bioarchaeology lab table with measurement calipers, magnifying glass, and ancient skull"),
    ("running forensic comparisons on ancient skeletons.", "Side-by-side comparison tables labeled 'Paleolithic Hunter' and 'Neolithic Farmer'.", "two clean display tables side by side labeled hunter-gatherer and early farmer"),
    ("Across dig sites throughout the Fertile Crescent,", "Hand-drawn map of Middle East with Tigris and Euphrates rivers highlighted.", "hand-drawn map of ancient Mesopotamia and Levant with highlighted river valleys"),
    ("especially at sites like Abu Hureyra in modern Syria,", "Archaeological site map with excavation squares and burial markers.", "detailed excavation trench diagram with numbered grid squares and burial flags"),
    ("they found the exact centuries where hunting stopped", "Timeline chart showing transitional arrow from spear symbol to wheat sickle symbol.", "timeline graphic showing spear icon transitioning to curved agricultural sickle icon"),
    ("and agricultural grain farming began.", "Plowed brown dirt field with small green shoots emerging in neat rows.", "hand-drawn plowed agricultural field with small seedling wheat sprouts in furrowed earth"),
    ("And when you compare those two groups side by side,", "Split screen showing two complete skeletons laid out horizontally.", "split screen showing two complete human skeletons laid horizontally on white background"),
    ("the results are genuinely shocking.", "Close-up of scientist looking through magnifying glass with wide, surprised eyes.", "stick figure scientist peering through magnifying glass with astonished face"),
    ("Skeleton A belonged to a Paleolithic hunter-gatherer.", "Full view of Skeleton A: tall, long limbs, robust ribcage, straight spine.", "anatomical doodle of robust tall skeleton with thick straight spinal column"),
    ("He lived thirty thousand years ago.", "Atmospheric shot of hunter walking along glacial steppe with spear.", "silhouette of prehistoric hunter carrying spear walking along open steppe ridge"),
    ("He stood nearly five foot eleven inches tall.", "Height chart comparing tall hunter skeleton against shorter modern silhouettes.", "height measurement chart showing tall hunter reaching 5 foot 11 mark"),
    ("His cortical bone density—the thickness of his bone walls—", "Cross-section diagram of femur bone showing ultra-thick dense outer bone wall.", "cross-section diagram of human thigh bone showing remarkably thick dense bone walls"),
    ("was equal to that of an Olympic decathlete.", "Stick figure decathlete vaulting over hurdle with athletic motion lines.", "athletic stick figure running and jumping showing muscular strength lines"),
    ("His legs were built by a lifetime of varied movement:", "Three small icons: walking on uneven hills, wading in rivers, sprinting on plains.", "three icons showing hiking over rocks, wading across river, and sprinting across meadow"),
    ("walking across rocky hills, climbing trees, and tracking game.", "Hunter balancing gracefully on fallen log across a river gorge.", "prehistoric stick figure balancing on fallen tree trunk over mountain stream"),
    ("His bone joints show virtually no signs of repetitive strain wear.", "Close-up of knee joint bone surfaces: perfectly smooth, rounded, and lubricated.", "anatomical illustration of smooth clean knee joint cartilage and healthy bone surface"),
    ("And when researchers examined his jaws and teeth,", "Extreme close-up of hunter skull jaws: wide dental arch, perfectly spaced white teeth.", "hand-drawn skull jaw showing wide dental arch with full set of clean teeth"),
    ("they found something almost unheard of today:", "Dentist tool pointing to pristine tooth enamel with zero holes.", "magnifying glass inspecting tooth enamel showing completely smooth surface with zero cavities"),
    ("practically zero dental cavities.", "A clean white tooth sparkling with small shine lines around it.", "isolated clean molar tooth doodle with sparkle glint lines on white background"),
    ("Not because he brushed or flossed,", "Toothbrush and dental floss crossed out with a red X doodle.", "toothbrush and dental floss roll crossed out with red hand-drawn X"),
    ("but because he never touched refined starchy porridge or sugar.", "Wild foods arranged neatly: wild walnuts, berries, roasted lean venison, leafy greens.", "arranged wild diet illustration: walnuts, blackberries, roasted meat slices, wild roots"),
    ("His oral microbiome was balanced and healthy.", "Microscopic view of beneficial round bacteria floating harmoniously in saliva.", "scientific microscopic doodle of balanced friendly bacteria cells in oral microbiome"),
    ("Now turn your attention to Skeleton B.", "Pan across to Skeleton B: smaller frame, hunched cervical vertebrae, compressed discs.", "anatomical illustration of smaller hunched skeleton with compressed spine"),
    ("This is an early Neolithic wheat farmer", "Early farmer kneeling on damp dirt, pushing heavy stone back and forth.", "stick figure farmer kneeling in mud pushing heavy grinding stone back and forth"),
    ("who lived in the exact same valley eight thousand years later.", "The same river valley, but forests cut down and turned into muddy wheat plots.", "same landscape view but trees cleared away replaced by bare brown tilled fields"),
    ("He is four inches shorter than his hunting ancestor.", "Height chart showing farmer skeleton dropping down to five foot six inches.", "height comparison chart showing farmer skeleton dropping four inches lower"),
    ("His spine tells a brutal forensic story.", "Close-up of lumbar vertebrae showing jagged arthritic spurs and squashed discs.", "close-up diagram of spinal vertebrae showing crushed discs and arthritic bone spurs"),
    ("In female skeletons from these early farming villages,", "Female farmer stick figure kneeling on both knees over a flat saddle-quern.", "female stick figure kneeling on knees bending forward over stone grain saddle quern"),
    ("the toe bones are permanently deformed and arthritic", "Close-up of metatarsal toe bones bent backwards with arthritic swelling.", "detailed doodle of human foot bones showing curled deformed arthritic toe joints"),
    ("from kneeling on hard ground for six to eight hours every day,", "Clock dial showing 8 hours passing while stick figure stays frozen kneeling.", "clock face with shadow hand sweeping 8 hours while figure remains kneeling"),
    ("rubbing a heavy grinding stone back and forth to crush wheat.", "Two hands pushing stone pestle across hollow stone slab, grain flour spilling over.", "close-up of hands pushing stone hand-quern back and forth grinding grain flour"),
    ("Her collarbones show permanent grooving from bearing heavy loads.", "Collarbone illustration showing deep indentations from hauling grain sacks.", "diagram of human clavicle collarbone showing stress fractures and muscle wear grooves"),
    ("And his teeth? A nightmare of rot.", "Farmer skull jaws open: rotten brown cavities, broken molars, bone abscesses.", "skull jaw close-up showing severely decayed black cavities and jaw abscess pockets"),
    ("Sticky boiled grain porridge coated the enamel,", "Cooked wheat gruel bubbling stickily inside crude ceramic pot over fire.", "boiling sticky wheat porridge bubbling in ceramic clay cooking pot"),
    ("feeding bacteria that ate straight into the nerve pulp.", "Microscopic doodle of bacteria multiplying on yellowed tooth surface.", "cartoon bacteria bugs with pitchforks chipping away at tooth surface"),
    ("Dental abscesses eroded holes straight into the jawbone.", "Cross section of lower jaw showing inflamed dark cavity eating into jawbone.", "anatomical cross section of jawbone showing painful bone abscess and decay pocket"),
    ("His skull bones are full of tiny porous pits,", "Inner eye socket bone showing spongy sieve-like porous texture.", "close-up of skull eye socket showing porotic hyperostosis sponge-like bone pits"),
    ("a medical condition called porotic hyperostosis,", "Medical anatomical label pointing to bone porosity: 'Nutritional Stress'.", "medical diagram label pointing to skull bone pitting with text nutritional stress"),
    ("caused by chronic iron-deficiency anemia and malnutrition.", "Bowl of monotone boiled barley porridge next to a sad stick figure with hollow cheeks.", "bowl of plain gray grain porridge next to malnourished stick figure with hollow cheeks"),
    ("The invention of farming was not a triumph of human health.", "A cracked stone monument with wheat stalks carved into it crumbling down.", "hand-drawn cracked stone monument with wheat stalk carving crumbling into dust"),
    ("It was a physical disaster.", "Farmer stick figure clutching his aching lower back while holding a heavy hoe.", "stick figure farmer standing in field clutching sore lower back with pain lightning lines"),
    ("The hunter had a diverse diet of hundreds of wild species,", "A colorful wheel diagram showing 80 different wild plants, seeds, fruits, and meats.", "circular wheel chart showing colorful variety of wild fruits, nuts, roots, fish, meat"),
    ("rich in protein, vitamins, and minerals.", "Vibrant energetic stick figure leaping over a log in green woods.", "energetic healthy stick figure leaping gracefully over fallen log in lush forest"),
    ("He had dense bones, straight joints, and pristine teeth.", "The hunter standing tall and proud in sunlight, smiling with full teeth.", "tall prehistoric stick figure smiling warmly with clear healthy face in sunshine"),
    ("And what about lifespan?", "A cartoon hourglass with sand trickling down between two skull markers.", "hand-drawn hourglass with golden sand trickling down between two pillars"),
    ("Yes, infant mortality was harsh in the Stone Age.", "A mother cradling a baby wrapped in soft fur next to a warm hearth fire.", "gentle scene of mother holding baby wrapped in fur sitting near hearth fire"),
    ("Many children died before their fifth birthday.", "A small grave marked with wildflowers on a grassy hillside.", "small gentle grave mound marked with river stones and wild field flowers"),
    ("That pulled the mathematical average lifespan down into the thirties.", "A mathematical chalkboard showing average equation: 0 + 70 divided by 2 equals 35.", "chalkboard showing statistical average calculation with chalk numbers"),
    ("But if an ancient hunter survived childhood,", "A healthy middle-aged hunter running effortlessly alongside a galloping deer.", "strong middle-aged stick figure running with steady stride through meadow"),
    ("he routinely lived into his sixties and seventies,", "Elderly hunter with long white beard telling animated story to young listeners.", "wise elder stick figure with white beard gesturing expressively around campfire"),
    ("active, muscular, and carrying all his own teeth.", "The elder carving a wooden bowl with steady, capable hands.", "hands of elder with laugh lines skillfully whittling smooth wooden bowl with flint")
]
acts.append(("ACT 2: Forensic Autopsy — The Dirt Doesn't Lie", act2))

# ==========================================
# ACT 3: A DAY IN THE LIFE & THE 15-HOUR MATH (03:00 - 05:45) ~85 shots
# ==========================================
act3 = [
    ("So if he wasn't slaving away every second just to survive,", "Prehistoric hunter relaxing on a mossy boulder, watching clouds drift by.", "prehistoric stick figure lounging back on mossy rock watching white clouds drift"),
    ("what did a normal day actually look like?", "Sunrise clock showing morning dawn over prehistoric river valley.", "sunrise over winding river valley with stylized sun rays stretching across canvas"),
    ("Let us reconstruct an ordinary morning fifty thousand years ago.", "The camp coming alive at dawn: thin blue smoke rising from three family hearths.", "panoramic view of Paleolithic camp with small skin shelters and smoking fires at dawn"),
    ("The camp stirs when the light touches the treetops.", "Birds flying across sunrise sky over a grove of birch trees.", "flock of birds silhouette flying across pale orange dawn sky over trees"),
    ("Nobody is jolted awake by an electric buzzer.", "A peaceful stick figure yawning and sitting up from bed of soft pine needles.", "stick figure waking up gently on bed of soft leaves and furs inside shelter"),
    ("People wake up gradually as the forest sounds change.", "Dewdrops glistening on green leaves as morning sun warms the foliage.", "close-up of glistening morning dewdrops on leaves with sunlight flares"),
    ("The first hour of the day belongs to the fire.", "Tribe members sitting around hearth, blowing gently on glowing coals.", "two stick figures kneeling by stone hearth blowing gently on orange embers"),
    ("Everyone gathers in the morning warmth,", "Group of five stick figures sitting in a relaxed circle, sipping water from horn cups.", "group of stick figures sitting in relaxed circle sharing warm broth and smiling"),
    ("chewing pieces of dried meat or roasted nuts,", "Hand offering roasted hazelnuts and dried berries to a neighbor.", "hands sharing roasted nuts and dried meat strips wrapped in broad green leaves"),
    ("laughing, teasing, and sharing dreams from the night.", "Two stick figures laughing, one making funny hand gestures imitating an animal.", "stick figure gesturing with hands imitating animal ears while others laugh"),
    ("There are no emails to check. No unread messages.", "Stick figure resting back against tree trunk with completely clear mind.", "stick figure sitting against tree trunk looking completely relaxed with closed eyes"),
    ("No boss who needs a report by ten AM.", "A corporate clipboard with red 'URGENT' stamp floating into air and vanishing.", "corporate clipboard floating away into sky and dissolving into harmless autumn leaves"),
    ("Around nine in the morning, daily work begins.", "Two men picking up wooden spears and checking their flint tips.", "two hunters standing up holding smooth wooden spears and inspecting flint points"),
    ("A small hunting team checks their equipment.", "Hands binding a sharp flint blade to a wooden haft with wet animal sinew.", "detailed close-up of hands tightly wrapping wet sinew cord around flint spearhead"),
    ("They don't work under orders; they work with autonomy.", "Hunters walking side by side as equal partners across sunny savannah.", "three hunters walking abreast as equal partners across sunlit golden grassland"),
    ("Skill earns admiration here, not obedience.", "Young hunter watching elder hunter carefully examine animal footprint in dust.", "young stick figure watching respectfully as elder points to animal track in sand"),
    ("And hunting itself is not frantic combat.", "The three hunters walking at an easy, rhythmic jog along a dirt trail.", "three hunters moving in smooth rhythmic endurance jog along game trail"),
    ("It is an exercise in endurance and ecological reading.", "Hunter stopping to touch broken branch and smell the air with sharp senses.", "hunter kneeling to inspect snapped twig on bush with focused observant expression"),
    ("Humans possess a unique physiological superpower:", "Anatomy diagram highlighting human sweat glands and upright bipedal posture.", "anatomical diagram of upright human body with stylized sweat cooling droplets"),
    ("we sweat across our entire body surface.", "Close-up of forehead sweating lightly while moving steadily under hot sun.", "profile of hunter face with beads of sweat evaporating in breeze"),
    ("A zebra or kudu is much faster than you in a sprint,", "Antelope sprinting fast in dust cloud with speed blur lines.", "antelope sprinting with speed lines leaving hunter far behind in distance"),
    ("but it cannot sweat. It has to pant to shed heat.", "The antelope stopping under a bush, panting heavily with tongue out.", "antelope standing under thorny bush panting heavily with heat waves radiating off body"),
    ("So the hunters don't try to outrun the animal.", "Hunters walking steadily in the distance at an unhurried, constant pace.", "two hunters walking steadily in background without rushing"),
    ("They simply jog behind it for four or five hours", "Sun moving across sky from ten AM to two PM while hunters keep steady pace.", "sun arc across sky showing passage of hours while hunters maintain steady stride"),
    ("until the prey overheats and lies down exhausted.", "Antelope resting safely on grass under tree, unable to run further.", "exhausted antelope lying down in shade completely tired out"),
    ("Meanwhile, a mile away, the gathering group is at work.", "Women and children walking through open woodland carrying woven fiber bags.", "group of women and older children walking through sun-dappled forest with bags"),
    ("They know the location of every edible plant in forty square miles.", "Mental map overlay showing berries, roots, medicinal herbs across hills.", "stylized landscape map showing icons of roots, berries, honey hives, and mushrooms"),
    ("They know where wild onions hide beneath the soil,", "Digging stick levering a plump wild onion bulb out of dark earth.", "pointed wooden digging stick popping fat wild root out of moist dark soil"),
    ("where sweet berries ripen in early autumn,", "Hands picking ripe purple blackberries from wild thorny brambles.", "hands gently plucking ripe dark purple berries into woven basket"),
    ("and where wild bees have hidden comb in hollow trees.", "Boy pointing up into hollow oak tree where honey drips down bark.", "young stick figure pointing excitedly at honey dripping from hollow tree trunk")
]
acts.append(("ACT 3: A Day in the Life & The 15-Hour Math", act3))

# Let's write out the full list and run the compilation to verify total shots and length
print("Writing build script...")

