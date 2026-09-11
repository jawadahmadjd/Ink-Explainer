"""
Precision Production Realignment for All 334 Shots
Maps every shot directly from flow_generated_images and generated assets
to both Final selected images directories.
"""
import os
import shutil
import glob

FLOW_DIR = r"d:\Tools of Jawad\25- Ink Explainers\3- Finals\1- What Did Ancient Humans Actually Do All Day\flow_generated_images"
BRAIN_DIR = r"C:\Users\Jawad Ahmad\.gemini\antigravity\brain\46ddaee4-4215-40bf-a068-80849852819a"

DEST_DIRS = [
    r"d:\Tools of Jawad\25- Ink Explainers\3- Finals\1- What Did Ancient Humans Actually Do All Day\Final selected images",
    r"d:\Tools of Jawad\25- Ink Explainers\Final selected images"
]

NEW_SHOTS = {
    45: os.path.join(BRAIN_DIR, "shot_045_ancient_graves_1789040031257.jpg"),
    99: os.path.join(BRAIN_DIR, "shot_099_sunrise_misty_birch_1789047668107.jpg"),
    196: os.path.join(BRAIN_DIR, "shot_196_bison_motion_legs_1789047714834.jpg"),
}

def get_best_flow_image(shot_num):
    """Finds the primary selected or regen_var_1/var_1 image in flow_generated_images."""
    candidates = [
        os.path.join(FLOW_DIR, f"shot_{shot_num:03d}_regen_var_1.jpg"),
        os.path.join(FLOW_DIR, f"shot_{shot_num:03d}_regen_var_2.jpg"),
        os.path.join(FLOW_DIR, f"shot_{shot_num:03d}_var_1.jpg"),
        os.path.join(FLOW_DIR, f"shot_{shot_num:03d}_var_2.jpg"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    # fallback glob
    matches = glob.glob(os.path.join(FLOW_DIR, f"shot_{shot_num:03d}*.jpg"))
    if matches:
        return matches[0]
    return None

def build_full_mapping():
    mapping = {}
    
    # Shots 1 to 44: direct 1-to-1
    for s in range(1, 45):
        mapping[s] = get_best_flow_image(s)
        
    # Shot 45: New generated
    mapping[45] = NEW_SHOTS[45]
    
    # Shots 46 to 63: shifted by +1 in flow (flow K-1 -> dest K)
    for s in range(46, 64):
        mapping[s] = get_best_flow_image(s - 1)
        
    # Shot 64: direct 64
    mapping[64] = get_best_flow_image(64)
    
    # Shots 65 to 96: direct 1-to-1
    for s in range(65, 97):
        mapping[s] = get_best_flow_image(s)
        
    # Region 2: Shots 97-100
    mapping[97] = get_best_flow_image(98) # sunrise over winding river valley
    mapping[98] = get_best_flow_image(99) # paleolithic camp at dawn with smoking hearths
    mapping[99] = NEW_SHOTS[99]          # NEW: sun rising over misty birch forest and river
    mapping[100] = get_best_flow_image(100) # flock of birds
    
    # Shots 101 to 132: direct 1-to-1
    for s in range(101, 133):
        mapping[s] = get_best_flow_image(s)
        
    # Region 3: Shots 133-196 (flow K+1 -> dest K)
    for s in range(133, 196):
        mapping[s] = get_best_flow_image(s + 1)
    mapping[196] = NEW_SHOTS[196] # NEW: bison legs flickering in torchlight
    
    # Shots 197 to 312: direct 1-to-1
    for s in range(197, 313):
        mapping[s] = get_best_flow_image(s)
        
    # Region 4: Shots 313-334 (flow K+1 -> dest K)
    for s in range(313, 334):
        mapping[s] = get_best_flow_image(s + 1)
        
    # Shot 334: Closing alarm clock dissolving in woodsmoke
    c334 = os.path.join(FLOW_DIR, "shot_334_regen_var_1.jpg")
    if not os.path.exists(c334):
        c334 = get_best_flow_image(334)
    mapping[334] = c334
    
    return mapping

def deploy_all():
    print("=" * 80)
    print("DEPLOYING FULL REALIGNMENT ACROSS ALL 334 SHOTS")
    print("=" * 80)
    
    mapping = build_full_mapping()
    
    # Verify all 334 exist
    missing = []
    for s in range(1, 335):
        src = mapping.get(s)
        if not src or not os.path.exists(src):
            missing.append((s, src))
            
    if missing:
        print(f"ERROR: {len(missing)} shots have missing source files:")
        for m in missing:
            print(f"  Shot {m[0]:03d} -> {m[1]}")
        return False
        
    print(f"Verified all 334 source image files exist!")
    
    for d in DEST_DIRS:
        print(f"\nDeploying to: {d}...")
        os.makedirs(d, exist_ok=True)
        for s in range(1, 335):
            src = mapping[s]
            dst = os.path.join(d, f"shot_{s:03d}.jpg")
            shutil.copy2(src, dst)
            
        # Also deploy preserved alternates
        alts = {
            "shot_064_alt_dental_exam.jpg": os.path.join(FLOW_DIR, "shot_063_regen_var_2.jpg"),
            "shot_097_alt_hunter_lounging.jpg": os.path.join(FLOW_DIR, "shot_097_var_1.jpg"),
            "shot_133_alt_meat_dist.jpg": os.path.join(FLOW_DIR, "shot_133_var_1.jpg"),
            "shot_313_alt_civilization_symbols.jpg": os.path.join(FLOW_DIR, "shot_313_var_1.jpg"),
        }
        for alt_name, alt_src in alts.items():
            if os.path.exists(alt_src):
                shutil.copy2(alt_src, os.path.join(d, alt_name))
                
        print(f"Successfully deployed 334 shots + 4 alternates to {d}")

    print("\nALL 334 SHOTS SUCCESSFULLY REALIGNED!")
    return True

if __name__ == "__main__":
    deploy_all()

