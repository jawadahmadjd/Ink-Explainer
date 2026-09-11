import os
import shutil

DIRS = [
    r"d:\Tools of Jawad\25- Ink Explainers\3- Finals\1- What Did Ancient Humans Actually Do All Day\Final selected images",
    r"d:\Tools of Jawad\25- Ink Explainers\Final selected images"
]

NEW_SHOT_45_SRC = r"C:\Users\Jawad Ahmad\.gemini\antigravity\brain\46ddaee4-4215-40bf-a068-80849852819a\shot_045_ancient_graves_1789040031257.jpg"

def realign_directory(target_dir):
    print(f"\n=======================================================")
    print(f"Realigning folder: {target_dir}")
    print(f"=======================================================")
    
    if not os.path.exists(target_dir):
        print(f"Directory does not exist: {target_dir}")
        return
        
    # Backup/Preserve current shot_063.jpg as shot_064_alt_dental_exam.jpg
    p63 = os.path.join(target_dir, "shot_063.jpg")
    p64_alt = os.path.join(target_dir, "shot_064_alt_dental_exam.jpg")
    if os.path.exists(p63):
        print(f"Preserving existing shot_063.jpg -> shot_064_alt_dental_exam.jpg")
        shutil.copy2(p63, p64_alt)
        
    # Shift backwards from 62 down to 45
    # e.g. shot_062 -> shot_063, shot_061 -> shot_062, ..., shot_045 -> shot_046
    for idx in range(62, 44, -1):
        src_name = f"shot_{idx:03d}.jpg"
        dst_name = f"shot_{idx+1:03d}.jpg"
        src_path = os.path.join(target_dir, src_name)
        dst_path = os.path.join(target_dir, dst_name)
        
        if os.path.exists(src_path):
            print(f"Moving {src_name} -> {dst_name}")
            shutil.copy2(src_path, dst_path)
        else:
            print(f"Warning: {src_path} not found!")

    # Now copy newly generated image to shot_045.jpg
    p45 = os.path.join(target_dir, "shot_045.jpg")
    if os.path.exists(NEW_SHOT_45_SRC):
        print(f"Installing new Shot 45 visual -> {p45}")
        shutil.copy2(NEW_SHOT_45_SRC, p45)
    else:
        print(f"Error: New Shot 45 source image not found at {NEW_SHOT_45_SRC}")

    print("Re-indexing complete for:", target_dir)

if __name__ == "__main__":
    for d in DIRS:
        realign_directory(d)
    print("\nALL DIRECTORIES REALIGNED SUCCESSFULLY.")

