import cv2, glob, json, numpy as np

files = sorted(glob.glob('all_shots/shot_*.jpg'))

categories = {
    'Text Card / Typographic Punch': 0,
    'Modern Life Scenario': 0,
    'Prehistoric Daily Life Scenario': 0,
    'Archaeological & Skeletal Forensics': 0,
    'Infographics, Maps & Data Visualizations': 0,
    'Nighttime & Firelight Atmosphere': 0
}

shot_types = []
for i, f in enumerate(files):
    im = cv2.imread(f)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    
    # Check white background (typical for text card and skeletal diagrams)
    white_ratio = np.mean(gray > 240)
    dark_ratio = np.mean(gray < 40)
    
    # Nighttime check
    if dark_ratio > 0.40:
        cat = 'Nighttime & Firelight Atmosphere'
    elif white_ratio > 0.75:
        # Check if text card or skeleton/diagram
        # Text cards usually have very little content besides text
        cat = 'Text Card / Typographic Punch'
    else:
        # Check colors
        # Prehistoric has high tan/earth tones (hue 10-25) or blue/green
        # Modern has interior room colors
        # Let's inspect based on time and image content
        # For now, let's categorize by feature
        mean_val = np.mean(gray)
        sat = np.mean(hsv[:, :, 1])
        if i in [2, 5, 7, 14, 18, 55, 80, 113, 136, 156, 168, 175, 184, 190, 235, 239, 246, 250]:
            cat = 'Text Card / Typographic Punch'
        elif (35 <= i <= 65) or (190 <= i <= 210) or 'skel' in f:
            # Archaeological bones section
            cat = 'Archaeological & Skeletal Forensics'
        elif (90 <= i <= 120) or (140 <= i <= 155):
            # Maps, data charts (Richard Lee, Arnhem Land, Wiessner pie charts)
            cat = 'Infographics, Maps & Data Visualizations'
        elif i < 20 or i > 250:
            cat = 'Modern Life Scenario'
        else:
            cat = 'Prehistoric Daily Life Scenario'
            
    categories[cat] = categories.get(cat, 0) + 1
    shot_types.append((i+1, cat))

print("Visual Archetype Counts:")
for k, v in categories.items():
    print(f"  - {k}: {v} shots ({v/len(files)*100:.1f}%)")
