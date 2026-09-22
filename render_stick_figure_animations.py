import os
import cv2
import numpy as np
import math
import subprocess
import shutil

out_dir = r"D:\Tools of Jawad\25- Ink Explainers\3- Finals\history\2- What Did Ancient Humans Do at Night\stick_figure_animations"
scratch = r"C:\Users\Jawad Ahmad\.gemini\antigravity-ide\brain\e85170a8-cdfc-460a-9d43-125ee49fc1ca\scratch"
os.makedirs(out_dir, exist_ok=True)
os.makedirs(scratch, exist_ok=True)

FPS = 30
DURATION = 4.0 # 4 seconds seamless loop
TOTAL_FRAMES = int(FPS * DURATION) # 120 frames
WIDTH = 2560
HEIGHT = 1440

def make_video_and_gif(frames, base_name):
    mp4_path = os.path.join(out_dir, f"{base_name}.mp4")
    gif_path = os.path.join(out_dir, f"{base_name}.gif")
    scratch_mp4 = os.path.join(scratch, f"{base_name}.mp4")
    scratch_gif = os.path.join(scratch, f"{base_name}.gif")
    
    # 1. Broadcast MP4
    cmd_mp4 = [
        'ffmpeg', '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{WIDTH}x{HEIGHT}',
        '-pix_fmt', 'bgr24',
        '-r', str(FPS),
        '-i', '-',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'medium',
        '-crf', '18',
        mp4_path
    ]
    proc = subprocess.Popen(cmd_mp4, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for f in frames:
        proc.stdin.write(f.tobytes())
    proc.stdin.close()
    proc.wait()
    shutil.copy(mp4_path, scratch_mp4)
    
    # 2. Smooth Looping GIF
    cmd_gif = [
        'ffmpeg', '-y',
        '-i', mp4_path,
        '-vf', 'fps=15,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer',
        gif_path
    ]
    subprocess.run(cmd_gif, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.copy(gif_path, scratch_gif)
    print(f"  -> Generated {base_name}.mp4 and {base_name}.gif successfully!")

def transform_overlay(base_bg, cutout, dx=0, dy=0, angle_deg=0, scale_x=1.0, scale_y=1.0, anchor=(0, 0)):
    ax, ay = anchor
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    
    M = np.array([
        [scale_x * cos_a, -scale_y * sin_a, ax + dx - ax * scale_x * cos_a + ay * scale_y * sin_a],
        [scale_x * sin_a,  scale_y * cos_a, ay + dy - ax * scale_x * sin_a - ay * scale_y * cos_a]
    ], dtype=np.float32)
    
    warped = cv2.warpAffine(cutout, M, (WIDTH, HEIGHT), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
    alpha = (warped[:, :, 3] / 255.0)[:, :, None]
    out = (warped[:, :, :3] * alpha + base_bg * (1.0 - alpha)).astype(np.uint8)
    return out

# Living line boil maps
np.random.seed(101)
boil_maps = []
for i in range(4):
    grid_y, grid_x = np.mgrid[0:HEIGHT, 0:WIDTH].astype(np.float32)
    nx = cv2.GaussianBlur(np.random.uniform(-1.8, 1.8, (HEIGHT//16, WIDTH//16)).astype(np.float32), (9, 9), 2.5)
    ny = cv2.GaussianBlur(np.random.uniform(-1.8, 1.8, (HEIGHT//16, WIDTH//16)).astype(np.float32), (9, 9), 2.5)
    nx = cv2.resize(nx, (WIDTH, HEIGHT)) * 1.0
    ny = cv2.resize(ny, (WIDTH, HEIGHT)) * 1.0
    boil_maps.append((grid_x + nx, grid_y + ny))

def apply_boil(cutout, frame_idx):
    idx = (frame_idx // 3) % 4
    mx, my = boil_maps[idx]
    warped = cv2.remap(cutout, mx, my, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
    return warped

# ==============================================================================
# ANIMATION 1: SHOT 001 (Hallway Walk Idle)
# ==============================================================================
def render_shot_001():
    print("Rendering Shot 001 (Hallway Walk / Pacing Idle)...")
    bg = cv2.imread(os.path.join(out_dir, "bg_clean_shot_001.jpg"))
    cut = cv2.imread(os.path.join(out_dir, "cutout_shot_001.png"), cv2.IMREAD_UNCHANGED)
    
    anchor = (1280, 1260) # Foot placement anchor
    frames = []
    
    for f in range(TOTAL_FRAMES):
        t = f / FPS
        tau = 2 * math.pi * t / DURATION
        
        # Walk bobbing: 2 full cycles over duration
        dy = -7.0 * math.sin(4 * tau) # Vertical bobbing
        dx = 3.0 * math.cos(2 * tau)  # Gentle stride sway
        tilt = 1.2 * math.sin(2 * tau) # Subtle forward/backward lean
        scale_y = 1.0 + 0.015 * math.sin(4 * tau) # Organic squash & stretch
        
        # Apply subtle living line boil
        boiled_cut = apply_boil(cut, f)
        frame = transform_overlay(bg, boiled_cut, dx=dx, dy=dy, angle_deg=tilt, scale_x=1.0, scale_y=scale_y, anchor=anchor)
        frames.append(frame)
        
    make_video_and_gif(frames, "animated_shot_001")

# ==============================================================================
# ANIMATION 2: SHOT 007 (Annoyed Hips Idle & Ceiling Lamp Pulse)
# ==============================================================================
def render_shot_007():
    print("Rendering Shot 007 (Annoyed Hips Idle & Lamp Pulse)...")
    bg = cv2.imread(os.path.join(out_dir, "bg_clean_shot_007.jpg"))
    cut = cv2.imread(os.path.join(out_dir, "cutout_shot_007.png"), cv2.IMREAD_UNCHANGED)
    
    anchor = (1880, 1080) # Hips anchor
    frames = []
    
    for f in range(TOTAL_FRAMES):
        t = f / FPS
        tau = 2 * math.pi * t / DURATION
        
        # Deep rhythmic breathing: 2 full breath cycles
        dy = -4.0 * math.sin(2 * tau)
        tilt = -1.8 + 2.0 * math.sin(2 * tau) # Looking up at light with subtle annoyed tilt
        scale_y = 1.0 + 0.018 * math.sin(2 * tau)
        scale_x = 1.0 - 0.008 * math.sin(2 * tau) # Chest breathing volume preservation
        
        # Background radiant lamp subtle warmth pulsation
        lamp_pulse = 1.0 + 0.035 * math.sin(3 * tau)
        bg_pulsed = cv2.convertScaleAbs(bg, alpha=lamp_pulse, beta=0)
        
        boiled_cut = apply_boil(cut, f)
        frame = transform_overlay(bg_pulsed, boiled_cut, dx=0, dy=dy, angle_deg=tilt, scale_x=scale_x, scale_y=scale_y, anchor=anchor)
        frames.append(frame)
        
    make_video_and_gif(frames, "animated_shot_007")

# ==============================================================================
# ANIMATION 3: SHOT 014 (Cosmic Zero-G Void Drift)
# ==============================================================================
def render_shot_014():
    print("Rendering Shot 014 (Zero-G Cosmic Void Floating)...")
    bg = cv2.imread(os.path.join(out_dir, "bg_clean_shot_014.jpg"))
    cut = cv2.imread(os.path.join(out_dir, "cutout_shot_014.png"), cv2.IMREAD_UNCHANGED)
    
    anchor = (1280, 750) # Center of mass anchor
    frames = []
    
    for f in range(TOTAL_FRAMES):
        t = f / FPS
        tau = 2 * math.pi * t / DURATION
        
        # Weightless zero-G orbital floating: smooth circular Lissajous drift
        dx = 28.0 * math.sin(tau)
        dy = 38.0 * math.cos(tau)
        # Gentle weightless angular tumble
        tilt = 4.5 * math.sin(tau + 0.4)
        # Gentle breathing / relaxation
        scale = 1.0 + 0.015 * math.sin(2 * tau)
        
        boiled_cut = apply_boil(cut, f)
        frame = transform_overlay(bg, boiled_cut, dx=dx, dy=dy, angle_deg=tilt, scale_x=scale, scale_y=scale, anchor=anchor)
        frames.append(frame)
        
    make_video_and_gif(frames, "animated_shot_014")

if __name__ == "__main__":
    render_shot_001()
    render_shot_007()
    render_shot_014()
    print("All 3 animations rendered successfully!")
