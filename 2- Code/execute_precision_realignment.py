import os
import shutil
import csv

FLOW_DIR = r"d:\Tools of Jawad\25- Ink Explainers\3- Finals\1- What Did Ancient Humans Actually Do All Day\flow_generated_images"
NEW_SHOT_45_SRC = r"C:\Users\Jawad Ahmad\.gemini\antigravity\brain\46ddaee4-4215-40bf-a068-80849852819a\shot_045_ancient_graves_1789040031257.jpg"

DEST_DIRS = [
    r"d:\Tools of Jawad\25- Ink Explainers\3- Finals\1- What Did Ancient Humans Actually Do All Day\Final selected images",
    r"d:\Tools of Jawad\25- Ink Explainers\Final selected images"
]

# Explicit 1-to-1 Mapping:
# Shot Target -> Source Image File (which contains the matching visual)
SOURCE_MAP = {
    45: NEW_SHOT_45_SRC,  # Newly generated: Two ancient fossil graves side-by-side in earth strata
    46: os.path.join(FLOW_DIR, "shot_045_regen_var_1.jpg"), # Macro view of ancient fossil human bones
    47: os.path.join(FLOW_DIR, "shot_046_regen_var_2.jpg"), # Laboratory table with brass calipers & skulls
    48: os.path.join(FLOW_DIR, "shot_047_regen_var_2.jpg"), # Two display tables Hunter vs Farmer
    49: os.path.join(FLOW_DIR, "shot_048_regen_var_2.jpg"), # Illustrated map of Fertile Crescent
    50: os.path.join(FLOW_DIR, "shot_049_var_2.jpg"),       # Detailed overhead excavation trench map
    51: os.path.join(FLOW_DIR, "shot_050_var_2.jpg"),       # Timeline arrow spear to sickle
    52: os.path.join(FLOW_DIR, "shot_051_var_1.jpg"),       # Plowed field with rows of wheat seedlings
    53: os.path.join(FLOW_DIR, "shot_052_regen_var_2.jpg"), # Split screen two human skeletons side by side
    54: os.path.join(FLOW_DIR, "shot_053_var_2.jpg"),       # Scientist holding large magnifying glass
    55: os.path.join(FLOW_DIR, "shot_054_var_2.jpg"),       # Full anatomical view of Skeleton A
    56: os.path.join(FLOW_DIR, "shot_055_regen_var_2.jpg"), # Silhouette of hunter with spear on steppe
    57: os.path.join(FLOW_DIR, "shot_056_regen_var_1.jpg"), # Height comparison chart at 5'11" mark
    58: os.path.join(FLOW_DIR, "shot_057_regen_var_2.jpg"), # Cross-section of thigh bone
    59: os.path.join(FLOW_DIR, "shot_058_var_2.jpg"),       # Athletic stick figure clearing hurdle
    60: os.path.join(FLOW_DIR, "shot_059_regen_var_1.jpg"), # Three circular icons: hiking, wading, climbing
    61: os.path.join(FLOW_DIR, "shot_060_var_1.jpg"),       # Hunter balancing across fallen log over stream
    62: os.path.join(FLOW_DIR, "shot_061_regen_var_1.jpg"), # Knee joint smooth cartilage surfaces
    63: os.path.join(FLOW_DIR, "shot_062_regen_var_1.jpg"), # Hunter skull jaws with wide dental arch
    64: os.path.join(FLOW_DIR, "shot_064_var_1.jpg"),       # Clean white molar tooth sparkling
}

ALT_SHOT_64 = os.path.join(FLOW_DIR, "shot_063_regen_var_2.jpg") # Dentist examining skull: "ANCIENT SKULL: ZERO CAVITIES"

def deploy():
    print("=" * 70)
    print("EXECUTING PRECISION REALIGNMENT OF SHOTS 45 - 64")
    print("=" * 70)
    
    # 1. Verify all sources exist
    missing = []
    for shot, src in SOURCE_MAP.items():
        if not os.path.exists(src):
            missing.append((shot, src))
    if not os.path.exists(ALT_SHOT_64):
        missing.append(("64_alt", ALT_SHOT_64))
        
    if missing:
        print("ERROR: Missing source files:", missing)
        return False
        
    print("All source files verified present.")
    
    # 2. Deploy to each target directory
    for d in DEST_DIRS:
        print(f"\nDeploying to: {d}")
        os.makedirs(d, exist_ok=True)
        
        # Copy primary shots
        for shot, src in SOURCE_MAP.items():
            dst_name = f"shot_{shot:03d}.jpg"
            dst_path = os.path.join(d, dst_name)
            shutil.copy2(src, dst_path)
            print(f"  [OK] Shot {shot:03d} <- {os.path.basename(src)} ({os.path.getsize(dst_path)} bytes)")
            
        # Copy alternate shot 64
        alt_dst = os.path.join(d, "shot_064_alt_dental_exam.jpg")
        shutil.copy2(ALT_SHOT_64, alt_dst)
        print(f"  [OK] Alt Shot 64 <- {os.path.basename(ALT_SHOT_64)} ({os.path.getsize(alt_dst)} bytes)")

    # 3. Update selection_log.csv in finals dir
    sel_csv = r"d:\Tools of Jawad\25- Ink Explainers\3- Finals\1- What Did Ancient Humans Actually Do All Day\selection_log.csv"
    if os.path.exists(sel_csv):
        print(f"\nAppending realigned entries to {sel_csv}...")
        with open(sel_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["--- REALIGNED BATCH SHOTS 45-63 ---", "", "", "", "", "2026-09-10T17:35:00"])
            for shot, src in SOURCE_MAP.items():
                writer.writerow([str(shot), "realigned", os.path.basename(src), "100.0", f"Realiged Shot {shot}", "2026-09-10T17:35:00"])
            writer.writerow(["64_alt", "realigned", os.path.basename(ALT_SHOT_64), "100.0", "Alt Dental Exam Zero Cavities", "2026-09-10T17:35:00"])

    print("\nPRECISION REALIGNMENT COMPLETE!")
    return True

if __name__ == "__main__":
    deploy()

