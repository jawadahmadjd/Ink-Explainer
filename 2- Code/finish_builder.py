import csv

# We append Acts 3, 4, 5, 6, 7 to trim_and_build_350.py

more_code = '''
# --- ACT 3: A DAY IN THE LIFE & THE 15-HOUR MATH (03:00 - 05:45) [85 shots, ~2,720 chars] ---
act3 = [
    ("Let us reconstruct an ordinary morning", "Paleolithic camp at dawn with three smoking hearths.", "panoramic view of Paleolithic camp with small skin shelters at dawn"),
    ("fifty thousand years ago.", "Sun rising over misty birch forest and river.", "sun rising over misty birch tree grove with golden light"),
    ("The camp stirs when sunlight touches the trees.", "Flock of birds flying across pale orange dawn sky.", "flock of birds flying across pale orange dawn sky over trees"),
    ("Nobody is jolted awake by an electric buzzer.", "Stick figure waking up gently on bed of soft leaves.", "stick figure waking up gently on soft leaves and furs"),
    ("People wake gradually as birds sing.", "Dewdrops glistening on green leaves in morning sun.", "close-up of glistening morning dewdrops on leaves with sun flares"),
    ("The first hour belongs to the fire.", "Two stick figures blowing gently on glowing hearth coals.", "two stick figures kneeling by stone hearth blowing on embers"),
    ("Everyone gathers in the morning warmth,", "Group of five figures sitting in circle sharing warm drink.", "group of stick figures sitting in circle sharing warm broth"),
    ("chewing roasted nuts or dried meat,", "Hands sharing roasted nuts and dried meat strips.", "hands sharing roasted nuts and dried meat strips wrapped in leaves"),
    ("laughing and sharing dreams from the night.", "Stick figure gesturing funny animal ears making others laugh.", "stick figure gesturing with hands imitating animal ears as friends laugh"),
    ("No emails to check. No unread messages.", "Stick figure leaning back against tree trunk with clear mind.", "stick figure resting against tree trunk looking completely relaxed"),
    ("No boss needing a report by ten AM.", "Corporate clipboard floating away dissolving into autumn leaves.", "corporate clipboard floating away into sky dissolving into leaves"),
    ("Around nine in the morning, work begins.", "Two hunters holding smooth spears inspecting flint tips.", "two hunters standing up holding wooden spears inspecting flint points"),
    ("A small hunting team checks their gear.", "Hands tightly binding flint spearhead with wet sinew cord.", "close-up of hands wrapping sinew cord around flint spearhead"),
    ("They work with autonomy, not under orders.", "Three hunters walking as equal partners across golden grassland.", "three hunters walking abreast as equal partners across sunny savannah"),
    ("Skill earns respect here, not obedience.", "Young stick figure watching elder inspect footprint in sand.", "young stick figure watching respectfully as elder points to animal track"),
    ("Hunting is not frantic hand-to-hand combat.", "Three hunters moving in smooth rhythmic endurance jog.", "three hunters moving in smooth rhythmic jog along game trail"),
    ("It is an exercise in ecological endurance.", "Hunter kneeling to inspect broken twig with focused eyes.", "hunter kneeling to inspect snapped twig on bush with sharp focus"),
    ("Humans have a unique biological superpower:", "Anatomy diagram of upright human body with sweat cooling droplets.", "anatomical diagram of upright human body with sweat cooling droplets"),
    ("we sweat across our entire body surface.", "Profile of hunter face with sweat evaporating in breeze.", "profile of hunter face with beads of sweat evaporating in breeze"),
    ("An antelope is faster in a sprint,", "Antelope sprinting fast with speed lines leaving hunter behind.", "antelope sprinting with speed lines leaving hunter far behind"),
    ("but it cannot sweat. It must pant to cool down.", "Antelope standing under bush panting with heat waves.", "antelope standing under thorny bush panting with heat waves"),
    ("So hunters don't try to outrun it.", "Two hunters walking steadily in background without rushing.", "two hunters walking steadily in background without rushing"),
    ("They simply jog behind it for hours", "Sun arc across sky showing passage of hours as hunters jog.", "sun arc across sky showing passage of hours while hunters jog"),
    ("until the animal overheats and rests.", "Exhausted antelope lying down in shade unable to run.", "exhausted antelope lying down in shade completely tired out"),
    ("Meanwhile, the gathering group is at work.", "Women and children walking through sun-dappled woodland.", "group of women and older children walking through forest with bags"),
    ("They know every edible plant for miles.", "Stylized map showing icons of roots, berries, honey, mushrooms.", "stylized landscape map showing icons of roots, berries, and herbs"),
    ("They know where wild onions hide in the soil,", "Pointed digging stick levering plump wild root out of earth.", "wooden digging stick popping fat wild root out of dark soil"),
    ("where blackberries ripen in early autumn,", "Hands gently plucking ripe purple berries into woven basket.", "hands gently plucking ripe dark purple berries into woven basket"),
    ("and where wild bees have honey in trees.", "Boy pointing excitedly at honey dripping from hollow tree.", "young stick figure pointing excitedly at honey in hollow tree trunk"),
    ("This is not desperate scavenging.", "Mother feeding sweet berry to smiling child on fallen log.", "mother feeding sweet berry to smiling child on fallen log"),
    ("It is a stroll through an open supermarket.", "Woven basket filled with colorful wild fruits and roots.", "woven basket filled with diverse colorful wild fruits and roots"),
    ("And because they know their territory,", "Foraging group resting under oak tree with full baskets.", "foraging group resting under grand oak tree with full baskets"),
    ("gathering doesn't take all day.", "Bright sun positioned just past noon mark in blue sky.", "bright sun positioned just past noon mark in clear blue sky"),
    ("By early afternoon, everyone is in camp.", "Hunters and foragers meeting on river path walking together.", "hunters and foragers meeting on path walking back to camp"),
    ("Food is roasted communally over the fire.", "Campfire roaring gently with roasted meat and tubers.", "campfire roaring gently with roasted meat on spit and tubers baking"),
    ("Everyone eats until their bellies are full.", "Group of figures around fire with satisfied relaxed postures.", "group of figures sitting around fire with satisfied full smiles"),
    ("And then... the working day is over.", "Stick figure laying down spear, stretching out on grass mat.", "stick figure laying down wooden spear and relaxing on grass mat"),
    ("In 1963, anthropologist Richard Lee", "Young researcher walking with backpack into desert scrub.", "young anthropologist in field clothes walking across desert scrub"),
    ("traveled to the Kalahari Desert in Botswana,", "Hand-drawn map of northern Botswana with expedition route.", "hand-drawn map of northern Botswana with dotted expedition route"),
    ("one of the harshest environments on Earth.", "Harsh desert landscape with heat mirage over cracked sand.", "harsh desert landscape with heat mirage over cracked sand"),
    ("He lived with the Ju/'hoansi hunter-gatherers.", "Anthropologist sitting with tribal group writing in journal.", "anthropologist sitting cross-legged with tribal group writing notes"),
    ("He carried a notebook, calendar, and stopwatch.", "Hand clicking vintage chrome stopwatch with second hand.", "close-up of hand clicking vintage chrome stopwatch"),
    ("For four weeks, Lee timed every single hour", "Open notebook showing neat columns of recorded hours.", "open notebook showing neat columns of recorded activity hours"),
    ("spent on hunting, gathering, and making tools.", "Four icons: digging roots, tracking game, cracking nuts, sewing.", "four neat icons: digging roots, tracking game, cracking nuts, sewing"),
    ("Economists had assumed primitives worked", "Old newspaper headline claiming primitive humans lived in toil.", "old newspaper headline claiming primitive humans lived in constant toil"),
    ("eighty hours a week just to survive.", "Cartoon caveman sweating under boulder labeled 80 hours.", "cartoon caveman sweating under boulder labeled 80 hour work week"),
    ("The actual number shocked science.", "Chalkboard with bold white chalk number: 17.1 HOURS.", "giant chalkboard with bold clean handwritten chalk number 17.1 HOURS"),
    ("The average adult spent seventeen hours a week", "24-hour clock circle showing 2.5-hour green slice labeled work.", "24 hour clock circle showing small 2.5 hour green slice labeled work"),
    ("providing complete sustenance for the group.", "Wooden platter filled with roasted meat and mongongo nuts.", "wooden platter filled with roasted meat and rich mongongo nuts"),
    ("That is about two and a half hours a day.", "Stick figure taking a casual morning walk with sun timer.", "stick figure taking brisk enjoyable stroll with sun timer"),
    ("And they weren't starving.", "Chart showing healthy caloric intake of 2140 calories.", "infographic chart showing healthy intake of 2140 calories"),
    ("Lee found each adult consumed 2,100 calories,", "Healthy hunter smiling and flexing arm showing lean muscle.", "healthy hunter smiling and flexing arm showing lean natural muscle"),
    ("with over ninety grams of protein daily.", "Meal plate with grilled venison, crushed nuts, and berries.", "healthy meal plate with grilled venison, crushed nuts, and berries"),
    ("They had food security in severe droughts,", "Split comparison: withered modern corn vs resilient wild roots.", "split comparison: withered corn crop vs resilient deep wild roots"),
    ("because wild plants survive climate extremes.", "Diagram showing deep resilient taproot holding water in sand.", "cutaway diagram showing deep resilient taproot holding water"),
    ("Critics claimed the Kalahari was a fluke.", "Two cartoon men in business suits at podium arguing.", "two cartoon men in business suits at podium arguing"),
    ("So researchers traveled across the globe.", "Silhouette of expedition airplane flying across world map.", "silhouette of small expedition airplane flying over world map"),
    ("They studied the Hadza in Tanzania:", "Map pin dropping on East Africa Rift Valley near lake.", "hand-drawn map of East Africa Rift Valley with pin labeled Hadza"),
    ("fifteen hours of work per week.", "Digital display box showing green numbers 15.0 HOURS.", "clean digital display box showing green numbers 15.0 HOURS PER WEEK"),
    ("They studied the Gunwinggu in Australia:", "Map pin dropping on tropical wetlands of Arnhem Land.", "hand-drawn map of Arnhem Land Australia with wetlands icon"),
    ("sixteen hours of work per week.", "Digital display box showing green numbers 16.2 HOURS.", "clean digital display box showing green numbers 16.2 HOURS PER WEEK"),
    ("They studied the Aché in Paraguay:", "Map pin dropping on dense South American rainforest.", "hand-drawn map of Paraguay rainforest with jungle canopy icon"),
    ("nineteen hours of work per week.", "Digital display box showing green numbers 19.1 HOURS.", "clean digital display box showing green numbers 19.1 HOURS PER WEEK"),
    ("Four continents. Four different ecosystems.", "Four quadrant grid: desert, savannah, wetland, jungle.", "four quadrant grid showing desert, savannah, wetland, and rainforest"),
    ("Every time, the math returned the same verdict:", "Hand-drawn wooden gavel coming down on sound block.", "hand-drawn wooden gavel coming down on sound block with impact lines"),
    ("fifteen to twenty hours of labor a week.", "Bold center text banner reading THE 15-HOUR WORK WEEK.", "bold center text banner reading THE 15-HOUR WORK WEEK on cream canvas"),
    ("That was the price of prehistoric life.", "Hunter resting under shade tree whistling peacefully.", "hunter resting peacefully under shade tree whistling with hands behind head"),
    ("The remaining one hundred and twenty waking hours", "Pie chart with 85 percent colored yellow labeled YOUR TIME.", "pie chart of weekly hours with 85 percent colored bright yellow"),
    ("belonged entirely and unconditionally to them.", "Wide field of golden grass illuminated by afternoon sun.", "wide field of golden grass illuminated by gentle afternoon sunlight"),
    ("Now look back at your own week.", "Modern stick figure in cubicle staring at monitor in dismay.", "modern stick figure sitting in office cubicle staring at computer in dismay"),
    ("You work forty, fifty, sixty hours.", "Red bar showing 55 hours modern worker vs 17 hours hunter.", "tall red bar showing 55 hours modern worker vs small green bar 17 hours"),
    ("You commute ten hours in traffic jams.", "City highway at night with river of red car brake lights.", "city highway at night with long river of red brake lights in gridlock"),
    ("You spend fifteen hours on chores and bills.", "Tired stick figure pushing grocery cart down sterile aisle.", "tired stick figure pushing overloaded grocery cart down sterile aisle"),
    ("We invented robot vacuums to save time.", "Cartoon robot vacuum bumping against sofa leg confused.", "cartoon robotic vacuum cleaner bumping against sofa leg"),
    ("We invented dishwashers so we didn't scrub.", "Modern kitchen dishwasher with door open showing plates.", "modern kitchen dishwasher with door slightly open showing clean plates"),
    ("We invented email to work in milliseconds.", "Digital envelope flying through network fiber lines.", "digital envelope flying through network fiber lines at speed of light"),
    ("Yet you have far less leisure time", "Modern stick figure looking down at open empty palms sad.", "modern stick figure looking down at open empty palms with sadness"),
    ("than a hunter who owned only a spear.", "Side-by-side: stressed modern man in suit vs calm hunter.", "side-by-side: stressed modern man in suit vs calm hunter under tree"),
    ("Where did all our time go?", "Antique pocket watch breaking open with brass gears spilling.", "antique pocket watch breaking open with brass gears tumbling out"),
    ("The hunter didn't need to save time.", "Hunter kneeling observing green beetle on leaf with awe.", "hunter kneeling down observing green beetle crawling across leaf"),
    ("Time wasn't a currency to be spent.", "Peaceful river flowing through meadow with wild flowers.", "peaceful river flowing through meadow with wild flowers along banks"),
    ("Time was the water he swam in.", "Hunter wading playfully into clear river under blue sky.", "hunter wading playfully into sparkling clear river water under blue sky")
]

# --- ACT 4: CULTURE, PLAY & FIRELIGHT (05:45 - 07:45) [65 shots, ~2,080 chars] ---
act4 = [
    ("What did they do with twelve free hours?", "Stick figure sitting in grass looking around playfully.", "stick figure sitting comfortably in grass looking around cheerful"),
    ("They did what free humans naturally do.", "Two children chasing yellow butterfly through flowers.", "two prehistoric children chasing bright yellow butterfly in meadow"),
    ("They played games. They invented sports.", "Four stick figures laughing playing tug of war with rope.", "four stick figures laughing while playing tug of war with leather rope"),
    ("Archaeologists find stones carved with tally marks,", "Smooth river stones carved with geometric tally grooves.", "smooth oval river stones decorated with carved geometric tally marks"),
    ("and animal knucklebones polished like dice.", "Polished deer ankle bones resting on sand like dice.", "polished deer ankle bones resting on sand like antique dice"),
    ("They wrestled, raced, and practiced archery.", "Two stick figures wrestling on grass while friends cheer.", "two stick figures wrestling on grass surrounded by cheering spectators"),
    ("They visited neighboring bands miles away.", "Two travelers greeting friendly tribe on ridge warmly.", "two travelers greeting friendly tribe on ridge with open arms"),
    ("And they created breathtaking art.", "Cave wall covered in blown red ochre hand stencils.", "ancient cave wall illuminated by torchlight covered in hand stencils"),
    ("Consider Chauvet Cave in southern France.", "Map of southern France with pin pointing to river gorge.", "hand-drawn map of southern France with pin pointing to limestone gorge"),
    ("Thirty-six thousand years ago, artists walked in.", "Silhouette of artist holding smoking torch entering cave.", "silhouette of Paleolithic artist holding burning torch entering dark cave"),
    ("They didn't just paint near the sunlit mouth.", "Cross section diagram of deep cave passage descending 400m.", "cross section diagram of deep underground cave passage descending 400m"),
    ("They walked a quarter-mile into total darkness,", "Artist crouching through narrow limestone rock tunnel.", "artist crouching through low limestone tunnel with warm torchlight"),
    ("through freezing stone passages without light.", "Grand cavern chamber with giant stalactites in torchlight.", "grand underground cavern chamber with giant stalactites in torchlight"),
    ("And on those hidden walls, they painted.", "Charcoal cave painting of four lion heads with depth.", "charcoal cave painting of four lion heads with dramatic shading"),
    ("They used stone curves to give muscles depth.", "Limestone rock contour incorporated into shoulder of rhino.", "bulging limestone rock contour incorporated into shoulder of woolly rhino"),
    ("They painted running bison with extra legs", "Cave drawing of bison with multiple legs creating motion.", "cave drawing of galloping bison with multiple legs creating motion effect"),
    ("to simulate cinematic movement in torchlight.", "Close-up of bison legs flickering in simulated animation.", "close-up of cave painting of bison with flickering torchlight animation"),
    ("They gathered animal fat, made stone torches,", "Hands using stone pestle to grind charcoal and red ochre.", "hands using stone pestle to grind black manganese and red ochre"),
    ("and worked in choking subterranean smoke.", "Artist using hollow bone tube to blow pigment spray on rock.", "artist using hollow bone tube to blow charcoal pigment spray on wall"),
    ("Why? Not for calories. Not for money.", "Painting of wild horses glowing in warm golden torchlight.", "magnificent cave painting of wild horses glowing in warm torchlight"),
    ("They did it purely for the awe of creation.", "Artist holding torch high admiring finished wall with joy.", "artist holding torch high admiring grand painted wall with reverent joy"),
    ("They had the free time to care about beauty.", "Necklace crafted from polished wolf teeth and amber beads.", "detailed illustration of necklace crafted from wolf teeth and amber"),
    ("Look at the site of Sunghir in Russia.", "Map of snowy Russian plains with pin labeled Sunghir.", "hand-drawn map of snowy Russian plains with pin labeled Sunghir"),
    ("Thirty thousand years ago, in the Ice Age,", "Two people in tailored fur parkas walking on snowy tundra.", "prehistoric people wearing tailored fur parkas walking on snowy tundra"),
    ("a band buried two children in a single grave.", "Grave diagram of two young skeletons surrounded by ochre.", "archaeological grave diagram of two young skeletons in red ochre"),
    ("On their bones lay ten thousand beads", "Macro shot of hundreds of tiny circular ivory beads in rows.", "macro shot of hundreds of tiny circular ivory beads in patterns"),
    ("carved from the tusks of woolly mammoths.", "Flint blade carefully scoring curved mammoth ivory tusk.", "flint blade carefully scoring and grooving a mammoth ivory tusk"),
    ("Archaeologists replicated those ivory beads.", "Modern researcher hands using flint stone chisel on ivory.", "modern researcher hands using flint stone chisel to shape ivory bead"),
    ("Each bead took forty-five minutes to grind,", "Flint drill bit piercing microscopic hole through ivory.", "macro shot of tiny flint drill bit piercing hole through ivory bead"),
    ("polish, and drill with a stone micro-borer.", "Single polished ivory bead held delicately between fingers.", "single polished mammoth ivory bead held between fingers showing hole"),
    ("Ten thousand beads equals thousands of hours.", "Chalkboard showing calculation: 10,000 beads x 45 min.", "chalkboard calculation showing thousands of hours of labor in chalk"),
    ("Think about what that represents.", "Stick figure standing thoughtfully looking at ancient grave.", "stick figure standing thoughtfully looking down at beautiful grave"),
    ("A community spent months carving ivory beads", "Elder sitting by fire carving ivory bead dropping into bowl.", "gentle elder sitting by fire carving ivory bead dropping it into bowl"),
    ("simply to sew them into garments for children,", "Hands using bone needle to sew ivory beads onto child parka.", "hands using fine bone needle to sew rows of ivory beads on fur garment"),
    ("and bury them in the frozen earth forever.", "Soft white snowflakes falling over snowy grave mound.", "soft white snowflakes falling gently over snowy mound marked by tusk"),
    ("That is not a species clawing for survival.", "Stick figure standing tall looking up at green aurora.", "stick figure standing tall looking up at green aurora ribbons in sky"),
    ("That is an affluent society with time to love.", "Group of tribe members in fur coats embracing near fire.", "group of tribe members in fur coats sitting close embracing near fire"),
    ("And then came the firelight.", "Close-up of glowing orange and red charcoal embers.", "close-up of glowing orange and red charcoal embers crackling in campfire"),
    ("In 2014, anthropologist Polly Wiessner", "Hand-drawn journal cover: Embers of Society by Wiessner.", "hand-drawn scientific journal cover with title Embers of Society"),
    ("published forty years of recordings in Botswana.", "Vintage cassette recorder with reels turning by campfire.", "vintage audio cassette recorder with reels turning next to fire in sand"),
    ("She classified conversations by time of day.", "Notebook page split comparing daytime talk and night talk.", "notebook page split into two columns comparing day talk and night talk"),
    ("During daylight, conversation was practical.", "Two figures in daylight gesturing dividing cuts of meat.", "two stick figures in daylight gesturing dividing cuts of meat on grass"),
    ("Seventy-five percent was about chores,", "Daytime speech bubble filled with practical work icons.", "daytime speech bubble filled with practical icons: firewood, footprints"),
    ("meat shares, complaints, and camp gossip.", "Stick figure rolling eyes as another gestures with complaint.", "stick figure rolling eyes while another gestures with complaint lines"),
    ("Just like an office water-cooler.", "Modern office water cooler scene with two figures gossiping.", "modern office water cooler scene with two figures gossiping with coffee"),
    ("But at sunset, the mood transformed.", "Sunset horizon turning from bright orange to deep indigo.", "dramatic sunset horizon turning from bright orange to deep indigo"),
    ("Without light, chores had to stop.", "Hands placing wooden digging tools on ground at dusk.", "hands placing tools on ground as darkness settles over camp"),
    ("The campfire became a stage.", "Warm circle of ten figures sitting close around fire.", "warm circle of ten stick figures sitting close together around fire"),
    ("Eighty-one percent of night talk was stories.", "Elder standing near fire gesturing telling dramatic tale.", "elder stick figure standing near fire gesturing with arms telling tale"),
    ("They told origin myths of the constellations.", "Elder pointing up to night sky where stars form hunters.", "elder pointing up to night sky where stars form hunter constellation"),
    ("They mimicked animal calls with humor.", "Young stick figure puffing cheeks imitating funny animal.", "young stick figure puffing cheeks imitating funny animal as friends laugh"),
    ("They sang polyphonic songs and told jokes.", "Two women clapping rhythm sticks singing with open mouths.", "two women clapping hollow rhythm sticks together singing with open mouths"),
    ("They healed daytime feuds with laughter.", "Two men who previously argued now smiling sharing drink.", "two men who were previously arguing now smiling and sharing warm drink"),
    ("Firelight talk was where culture was born.", "Golden embers drifting up from campfire into starry galaxy.", "golden embers and sparks drifting up from campfire into starry galaxy"),
    ("Daytime fed the human belly.", "Clean illustration of roasted root and lean meat on tray.", "clean illustration of roasted root and lean meat on wooden tray"),
    ("Nighttime created the human soul.", "Warm radiant glow of fire illuminating united human faces.", "warm radiant glow of campfire illuminating circle of smiling faces"),
    ("And they had that stage every single night.", "Wide landscape view of three campfire dots under stars.", "wide landscape view of three glowing campfire dots under starry sky")
]

# --- ACT 5: THE LOST ARCHITECTURE OF SLEEP (07:45 - 08:55) [35 shots, ~1,120 chars] ---
act5 = [
    ("When embers faded, they slept.", "Campfire fading to dark red as figures curl up in furs.", "campfire coals fading to dark red as figures curl up in soft furs"),
    ("Sleep worked differently than today.", "Slender white crescent moon shining over sleeping tribe.", "slender white crescent moon shining gently over sleeping tribe"),
    ("If you wake at three AM now, you panic.", "Modern stick figure sitting up in bed in pitch black room.", "modern stick figure sitting up in bed in dark room with panic eyes"),
    ("You check your phone: 03:14 AM.", "Digital alarm clock glowing 03:14 in electric blue.", "digital alarm clock glowing 03:14 in bright electric blue in bedroom"),
    ("You calculate remaining hours with dread.", "Frustrated stick figure holding head as countdown ticks.", "frustrated stick figure holding head as countdown clock shows 3 hours"),
    ("You toss, turn, and feel broken.", "Tangled stick figure kicking bedsheets with frustration.", "tangled stick figure kicking bedsheets with squiggly frustration lines"),
    ("You think you have insomnia.", "Prescription pill bottle on modern nightstand with glass.", "prescription pill bottle on modern nightstand with water glass"),
    ("You don't have insomnia; you have an alarm.", "Cartoon alarm clock jumping up and down ringing harshly.", "cartoon alarm clock jumping up and down ringing with jagged soundwaves"),
    ("For millennia, humans slept in two phases.", "Vintage woodcut of peasants waking calmly by candlelight.", "vintage woodcut illustration of peasants waking calmly by candlelight"),
    ("Circadian trials show sleep is biphasic.", "Sleep clinic monitor showing two-wave brainwave cycles.", "sleep research lab monitor showing natural two-wave brainwave cycles"),
    ("First sleep, and second sleep.", "Two smooth wave graphs on timeline labeled First and Second.", "two smooth wave graphs on timeline labeled First Sleep and Second Sleep"),
    ("You fell asleep at dusk around eight.", "Hunter curling up peacefully under thick fur as dark falls.", "hunter curling up peacefully under thick fur blanket as darkness settles"),
    ("Four hours later, you woke naturally.", "Hunter opening eyes smoothly without alarm in moonlit tent.", "hunter opening eyes smoothly without alarm feeling relaxed in tent"),
    ("At one in the morning began 'the watch.'", "Gentle blue moonlight illuminating peaceful quiet camp.", "gentle blue moonlight illuminating peaceful quiet camp with two awake"),
    ("It was not a time of anxious racing thoughts.", "Calm stick figure taking deep breath looking up at stars.", "calm stick figure taking deep breath looking up at silver Milky Way"),
    ("It was a tranquil, peaceful hour.", "Gentle hands placing two dry sticks on embers watching flame.", "gentle hands placing two dry sticks on embers watching golden flame"),
    ("People checked the fire, sipped cool water,", "Hunter taking slow refreshing sip of water from canteen.", "hunter taking slow refreshing sip of water from leather canteen"),
    ("whispered softly with a partner,", "Two stick figures sitting back to back under blanket talking.", "two stick figures sitting back to back under blanket whispering softly"),
    ("or watched the quiet constellations turn.", "Shooting star streaking across deep velvet night sky.", "shooting star streaking across deep velvet sky framed by tree branches"),
    ("The waking midnight brain releases prolactin,", "Brain cross-section glowing with soft calming blue light.", "stylized brain cross-section glowing with soft calming blue hormonal light"),
    ("producing deep serenity and tranquility.", "Peaceful stick figure with closed eyes surrounded by calm.", "peaceful stick figure with closed eyes surrounded by soft radiant aura"),
    ("Then, after an hour of peace,", "Hunter yawning contentedly pulling blanket over shoulders.", "hunter yawning contentedly and pulling furry blanket back over shoulders"),
    ("they slipped into their second sleep", "Hunter sleeping deeply with peaceful smile as sky lightens.", "hunter sleeping deeply with peaceful smile as night sky turns soft blue"),
    ("and woke with the rising sun.", "First ray of morning sun entering shelter illuminating face.", "first ray of golden morning sun entering shelter illuminating face"),
    ("We dismantled that natural rhythm.", "Modern glass skyscraper city glowing with blinding lights.", "modern glass skyscraper city glowing with thousands of blinding lights"),
    ("We turned sleep into a race against an alarm.", "Stick figure running frantically on treadmill in clock.", "stick figure running frantically on treadmill inside giant ticking clock"),
    ("When biology wakes us at night,", "Stick figure staring at ceiling under streetlamp glare.", "stick figure staring at ceiling illuminated by harsh streetlamp light"),
    ("we pathologize it and call it disease.", "Medical clipboard with word INSOMNIA circled in red.", "medical clipboard with word INSOMNIA circled with red marker pen"),
    ("It's not disease. It is your body remembering.", "Silhouette of hunter standing in quiet wilderness under stars.", "silhouette of ancient hunter standing in quiet wilderness under stars")
]

# --- ACT 6: THE AGRICULTURAL TRAP (08:55 - 10:35) [48 shots, ~1,540 chars] ---
act6 = [
    ("Which brings us to the great paradox:", "Dramatic dark storm clouds gathering over golden savannah.", "dramatic dark storm clouds gathering over peaceful golden savannah"),
    ("if foraging was healthier, freer, and leisurely,", "Joyful scene of hunter family laughing by sunny river.", "joyful scene of hunter family relaxing and laughing by sunny riverbank"),
    ("why did humanity ever give it up?", "Large hand-drawn question mark planted in plowed furrow.", "large hand-drawn question mark planted in muddy agricultural furrow"),
    ("Why trade fifteen hours for fifty of toil?", "Side-by-side: hunter whistling vs farmer collapsed on plow.", "side-by-side: hunter whistling with spear vs farmer collapsed over plow"),
    ("The answer is: nobody chose to give it up.", "Heavy rustic wooden gate swinging open slowly into pen.", "heavy rustic wooden gate swinging open slowly into muddy fenced pen"),
    ("Humanity fell into an irreversible trap.", "Hand-drawn primitive deadfall trigger trap made of log.", "hand-drawn primitive deadfall trigger trap made of heavy log and stick"),
    ("A trap so gradual no generation saw it.", "Hourglass with sand falling one grain at a time in pile.", "hourglass with sand falling one grain at a time into deep pile"),
    ("Twelve thousand years ago in the Middle East,", "Map of Fertile Crescent with wild wheat grasses on hills.", "map of Fertile Crescent with wild wheat grasses growing across green hills"),
    ("climate swings brought colder winter droughts.", "Cracked dry earth with dead brush showing severe drought.", "cracked dry earth with dead brush showing severe prehistoric drought"),
    ("Bands noticed wild wheat and barley", "Hand gently brushing over ripe wild wheat stalks by river.", "hand gently brushing over ripe wild wheat stalks growing along riverbank"),
    ("stored remarkably well through the winter.", "Underground stone storage pit lined with straw with grain.", "underground stone storage pit lined with straw filled with grain seeds"),
    ("So they tended patches. They watered them.", "Stick figure carrying clay pots of water pouring on plot.", "stick figure carrying two clay pots of water pouring on grain plot"),
    ("They weeded soil. They saved the best seeds.", "Hands separating fat wheat grains from chaff into bowl.", "hands separating fat wheat grains from dry chaff into small bowl"),
    ("It seemed like a brilliant insurance policy.", "Stick figure smiling proudly with hands on hips at plot.", "stick figure smiling proudly with hands on hips looking at garden plot"),
    ("More stored grain meant less winter dread.", "Warm shelter interior with full grain jar by hearth fire.", "warm shelter interior with full grain jar sitting safely by hearth fire"),
    ("But wheat contained a biological trigger.", "Single golden wheat stalk isolated on white with red aura.", "single golden wheat stalk isolated on white background with red aura"),
    ("Wild fibrous food requires years of nursing,", "Mother holding child in forest setting nurturing softly.", "mother holding child in forest setting with gentle nurturing atmosphere"),
    ("keeping birth spacing at four years.", "Growth chart showing forager child weaning at age four.", "growth chart showing child weaning timeline reaching age four milestone"),
    ("The population stayed small and balanced.", "Small group of 25 stick figures walking in vast valley.", "small group of 25 stick figures walking peacefully through vast landscape"),
    ("Cooked wheat porridge changed the formula.", "Clay spoon feeding soft cooked grain porridge to infant.", "clay spoon feeding soft cooked grain porridge to small infant"),
    ("Starch is easy for young guts to digest.", "Smiling baby sitting on mat eating warm porridge bowl.", "smiling baby sitting on mat eating warm porridge with ceramic spoon"),
    ("Mothers could wean babies at age one.", "Growth chart arrow dropping from age 4 down to age 1.", "growth chart arrow dropping from age 4 down to age 1 milestone"),
    ("Birth spacing collapsed to eighteen months.", "Timeline packed tightly with baby icons appearing rapidly.", "timeline packed tightly with baby icons appearing one after another"),
    ("The population exploded exponentially.", "Crowd diagram showing stick figure population multiplying.", "crowd diagram showing stick figure population multiplying exponentially"),
    ("Within generations, twenty-five foragers", "Small simple camp of five leather tents by riverbank.", "small simple camp of five leather tents by riverbank"),
    ("became three hundred hungry villagers.", "Crowded ancient mud-brick village with packed houses.", "crowded ancient mud-brick village with dozens of packed houses"),
    ("And suddenly, the trap snapped shut.", "Heavy wooden deadfall trap slamming down hard with dust.", "heavy wooden deadfall trap slamming down hard on ground with dust cloud"),
    ("Three hundred people cannot live on wild game.", "Hunters standing in barren forest looking around empty.", "hunters standing in barren forest looking around with empty hands no game"),
    ("There are not enough roots in fifty miles.", "Empty woven basket upside down on bare trampled earth.", "empty woven basket upside down on bare trampled muddy earth"),
    ("You cannot go back to hunting.", "Stick figure trying to walk to forest blocked by crowd.", "stick figure trying to walk toward forest blocked by crowd of villagers"),
    ("If you stop farming, your children starve.", "Worried mother surrounded by hungry children crying.", "worried mother surrounded by three small hungry children crying for food"),
    ("You are trapped in the soil.", "Stick figure standing in field with heavy wooden hoe.", "stick figure standing in field with heavy wooden hoe looking trapped"),
    ("Now you must plow more fields.", "Two men straining forward pulling heavy plow in mud.", "two men straining forward pulling heavy wooden plow through thick mud"),
    ("You must weed from sunrise to sunset.", "Stick figure on knees in heat pulling weeds from wheat.", "stick figure crawling on knees under scorching sun pulling weeds from wheat"),
    ("You must dig irrigation till your arms shake.", "Stick figure carrying heavy wooden yoke with water buckets.", "stick figure carrying heavy wooden yoke with two sloshing water buckets"),
    ("Grain is harvested all at once, in bulk.", "Massive stone storehouse with doorway showing grain sacks.", "massive stone storehouse with doorway showing stacks of grain sacks"),
    ("You must store it inside granaries.", "Workers climbing ladder carrying heavy grain into silo.", "workers climbing wooden ladder carrying heavy grain baskets into silo"),
    ("And when granaries are full of food,", "Shadowy figures on distant ridge watching granary greedily.", "shadowy figures on distant hilltop watching stone granary with greedy eyes"),
    ("other starving villages come to take it.", "Raiders with clubs and torches charging at village gate.", "raiders with clubs and torches charging toward ancient village gate"),
    ("So you build walls. Thick stone walls.", "Workers lifting heavy blocks building defensive city wall.", "workers lifting heavy stone blocks building high defensive wall around village"),
    ("You need guards on those battlements.", "Two guards standing on stone city wall holding spears.", "two guards standing on battlements of stone city wall holding spears"),
    ("You need scribes to tally the grain sacks.", "Ancient scribe pressing tally marks into wet clay tablet.", "ancient scribe holding stylus pressing tally marks into wet clay tablet"),
    ("You need taxes to feed the soldiers.", "Official taking grain sacks from weeping farmer family.", "official taking grain sacks from humble farmer family standing outside hut"),
    ("You need a king to command the army.", "King on carved stone throne holding royal scepter sternly.", "king sitting on carved stone throne holding royal scepter giving orders"),
    ("And just like that, human freedom vanished.", "Stylized chain wrapping around hoe linking to palace.", "stylized chain wrapping around farmer wooden hoe linking to grand palace"),
    ("Property was born. Borders were drawn.", "Map of valley carved into parcels with stone walls.", "map of green valley carved up into rigid geometric parcels with walls"),
    ("Time belonged to the harvest and the king.", "Stone sundial in city square casting sharp dark shadow.", "stone sundial in city square casting sharp dark shadow marking hours"),
    ("Freedom was traded for a fence.", "Farmer leaning on hoe watching wild birds soaring free.", "farmer leaning heavily on hoe looking longingly at wild birds soaring free")
]

# --- ACT 7: THE FULL-CIRCLE MIRROR (10:35 - 11:12) [20 shots, ~720 chars] ---
act7 = [
    ("Tonight, you will crawl into bed.", "Modern cozy bedroom at night with soft warm bedside lamp.", "modern cozy bedroom at night with soft warm lamp on nightstand"),
    ("You will reach for your smartphone.", "Hand reaching out toward glowing phone next to water glass.", "hand reaching out toward glowing smartphone resting next to water glass"),
    ("You will set that chime for six-thirty AM.", "Phone screen setting alarm toggle green for 6:30 AM.", "close-up of phone screen setting alarm toggle with green checkmark for 6:30 AM"),
    ("You will spend the next forty years", "Time-lapse of stick figure aging at office desk.", "time-lapse illustration of stick figure aging at desk hair turning gray"),
    ("sitting in traffic, answering emails,", "Stick figure looking out rainy bus window at city buildings.", "stick figure looking out rain-streaked bus window at grey city buildings"),
    ("paying down a mortgage on drywall,", "Stick figure signing mortgage papers across from banker.", "stick figure signing official mortgage papers across desk from bank officer"),
    ("saving dollars into an index fund,", "Glass piggy bank filling with coins as calendar flips.", "glass piggy bank filling with gold coins while calendar pages flip"),
    ("hoping that someday, if your body works,", "Elderly stick figure with walking cane on park bench.", "elderly modern stick figure with walking cane smiling gently on park bench"),
    ("you can finally retire.", "Bold center text banner reading RETIREMENT on canvas.", "bold center text banner reading RETIREMENT on clean cream canvas"),
    ("And what is the dream of retirement?", "Dream bubble showing fishing, forest hiking, warm baking.", "dream bubble showing three scenes: fishing at lake, forest hiking, baking"),
    ("To wake with the sun. Nowhere to be.", "Older stick figure on cabin porch watching golden sunrise.", "older stick figure on wooden cabin porch watching peaceful golden sunrise"),
    ("To walk in woods with no clock in pocket.", "Stick figure strolling on pine needle trail in sunbeams.", "stick figure strolling along pine forest path with sunbeams through branches"),
    ("To cook slow fresh food with your hands.", "Hands chopping fresh garden vegetables on rustic board.", "hands chopping fresh garden vegetables and herbs on rustic wooden board"),
    ("To take afternoon naps in the shade.", "Stick figure relaxing in hammock between fruit trees.", "stick figure relaxing in hammock strung between two fruit trees in breeze"),
    ("To sit by a fire at night with loved ones,", "Older friends sitting around backyard fire pit laughing.", "group of older friends sitting around cozy stone fire pit laughing"),
    ("telling stories and watching the stars.", "Group looking up in awe at glowing stars and Milky Way.", "group of friends looking up in awe at glowing stars and Milky Way"),
    ("Do you see the crushing irony?", "Modern stick figure looking in mirror with deep thought.", "modern stick figure looking into bathroom mirror with deep thoughtful face"),
    ("You work forty-five years of your life", "Chalkboard timeline showing 45 years leading to question mark.", "chalkboard timeline showing 45 years of office desks leading to question mark"),
    ("hoping to buy back the exact freedom", "Golden glowing silhouette of hunter free on mountain ridge.", "golden glowing silhouette of prehistoric hunter standing free on ridge"),
    ("your ancestors lived from birth to death.", "Hunter family laughing warmly together around hearth.", "prehistoric hunter family laughing warmly together around glowing hearth"),
    ("And they would find it strange you traded it away.", "Simple alarm clock doodle fading into curling woodsmoke.", "simple alarm clock doodle fading away into curling wisp of woodsmoke on canvas")
]

# Combine all acts
all_shots = act1 + act2 + act3 + act4 + act5 + act6 + act7
print(f"Total calibrated shots: {len(all_shots)}")

cumulative_chars = 0
storyboard = []

for i, (text, visual, subject) in enumerate(all_shots):
    prompt = f"Minimalist hand-drawn black ink line art, clean doodle stick-figure illustration, expressive face, flat muted colors, cream off-white background (#FAF8F5), {subject}, clean 2D vector style, editorial cartoon, no text, 16:9 aspect ratio"
    
    char_count = len(text)
    start_sec = cumulative_chars * 60.0 / 1000.0
    end_sec = (cumulative_chars + char_count) * 60.0 / 1000.0
    cumulative_chars += char_count
    
    start_m, start_s = int(start_sec // 60), start_sec % 60
    end_m, end_s = int(end_sec // 60), end_sec % 60
    time_str = f"{start_m:02d}:{start_s:04.1f} - {end_m:02d}:{end_s:04.1f}"
    
    storyboard.append({
        "shot_id": i + 1,
        "time": time_str,
        "text": text,
        "visual": visual,
        "prompt": prompt
    })

total_duration_sec = cumulative_chars * 60.0 / 1000.0
print(f"Total characters: {cumulative_chars}")
print(f"Total duration: {int(total_duration_sec // 60):02d}:{total_duration_sec % 60:04.1f} ({total_duration_sec:.1f} seconds)")

# 1. Clean Voiceover Script for AI Voiceover
with open("clean_ai_voiceover_script.txt", "w", encoding="utf-8") as f:
    full_script = " ".join([s["text"] for s in storyboard])
    f.write(full_script)

# 2. Complete CSV File
with open("storyboard_master.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Shot #", "Time", "Spoken VO script", "Visual description", "Exact Prompt for google nano banana pro"])
    for s in storyboard:
        writer.writerow([s["shot_id"], s["time"], s["text"], s["visual"], s["prompt"]])

# 3. Complete Markdown File
with open("storyboard_master.md", "w", encoding="utf-8") as f:
    f.write("# Master Production Storyboard (350 Shots)\\n\\n")
    f.write("| Shot | Time | Spoken VO script | Visual description | Exact Prompt for google nano banana pro |\\n")
    f.write("| :--- | :--- | :--- | :--- | :--- |\\n")
    for s in storyboard:
        t_clean = s["text"].replace("|", "/")
        v_clean = s["visual"].replace("|", "/")
        p_clean = s["prompt"].replace("|", "/")
        f.write(f"| {s['shot_id']} | {s['time']} | {t_clean} | {v_clean} | `{p_clean}` |\\n")

print("All production files successfully generated!")
'''

with open("trim_and_build_350.py", "a", encoding="utf-8") as f:
    f.write(more_code)

print("trim_and_build_350.py ready to execute.")

