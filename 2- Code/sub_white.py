import cv2, glob, numpy as np

files = sorted(glob.glob('all_shots/shot_*.jpg'))

text_cards = []
isolated_drawings = []
for i in range(len(files)):
    gray = cv2.cvtColor(cv2.imread(files[i]), cv2.COLOR_BGR2GRAY)
    if np.mean(gray > 240) > 0.75:
        # Check text card vs drawing: text cards have black pixels mostly in center line
        # Isolated drawings have larger connected dark clusters
        contours, _ = cv2.findContours((gray < 220).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        areas = [cv2.contourArea(c) for c in contours]
        if max(areas, default=0) > 10000:
            isolated_drawings.append(i+1)
        else:
            text_cards.append(i+1)

print(f"White background shots: {len(text_cards) + len(isolated_drawings)}")
print(f"  - Pure text / punch title cards: {len(text_cards)}")
print(f"  - Isolated spot illustrations on white background: {len(isolated_drawings)}")
