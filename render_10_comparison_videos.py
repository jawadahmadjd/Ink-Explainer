import os
import cv2
import numpy as np
import math
import subprocess

proj_dir = r"d:\Tools of Jawad\25- Ink Explainers\3- Finals\history\2- What Did Ancient Humans Do at Night"
base_dir = os.path.join(proj_dir, "animation_comparison_test")
out_dir = os.path.join(proj_dir, "animation_comparison_test", "renders")
os.makedirs(out_dir, exist_ok=True)

FPS = 24
DURATION_SEC = 3.5
TOTAL_FRAMES = int(FPS * DURATION_SEC) # 84 frames
WIDTH = 1920
HEIGHT = 1080

print(f"Rendering 10 animation comparison videos: {TOTAL_FRAMES} frames @ {FPS} fps ({WIDTH}x{HEIGHT})")

def get_base_img(sid):
    p = os.path.join(base_dir, f"base_shot_{sid:03d}_1080.jpg")
    img = cv2.imread(p)
    if img is None:
        raise FileNotFoundError(f"Missing base image: {p}")
    return img

def create_video_writer(out_path):
    cmd = [
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
        out_path
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc

# ------------------------------------------------------------------------------
# 1. AUTHENTIC LINE BOIL ENGINE (Squigglevision / Living Cel)
# ------------------------------------------------------------------------------
np.random.seed(42)
boil_maps = []
for i in range(4): # 4 cyclical boil phases at 8 fps (changes every 3 frames)
    # Low-frequency smooth displacement vector field
    grid_y, grid_x = np.mgrid[0:HEIGHT, 0:WIDTH].astype(np.float32)
    noise_x = cv2.GaussianBlur(np.random.uniform(-4.0, 4.0, (HEIGHT//8, WIDTH//8)).astype(np.float32), (15, 15), 5.0)
    noise_y = cv2.GaussianBlur(np.random.uniform(-4.0, 4.0, (HEIGHT//8, WIDTH//8)).astype(np.float32), (15, 15), 5.0)
    noise_x = cv2.resize(noise_x, (WIDTH, HEIGHT)) * 1.6
    noise_y = cv2.resize(noise_y, (WIDTH, HEIGHT)) * 1.6
    map_x = grid_x + noise_x
    map_y = grid_y + noise_y
    boil_maps.append((map_x, map_y))

def apply_line_boil(img, frame_idx):
    boil_idx = (frame_idx // 3) % 4
    map_x, map_y = boil_maps[boil_idx]
    warped = cv2.remap(img, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # Ensure white paper stays pure white (> 248)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    white_mask = gray > 248
    warped[white_mask] = img[white_mask]
    return warped

# ------------------------------------------------------------------------------
# 2. VECTOR DRAWING PRIMITIVES (MinutePhysics Style)
# ------------------------------------------------------------------------------
def draw_line(canvas, p1, p2, color=(0, 0, 0), thickness=6):
    cv2.line(canvas, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), color, thickness, cv2.LINE_AA)

def draw_circle(canvas, center, radius, color=(0, 0, 0), fill=(255, 255, 255), thickness=6):
    c = (int(center[0]), int(center[1]))
    r = int(radius)
    if fill is not None:
        cv2.circle(canvas, c, r, fill, -1, cv2.LINE_AA)
    cv2.circle(canvas, c, r, color, thickness, cv2.LINE_AA)

def draw_fk_limb(canvas, root, l1, l2, theta1_deg, theta2_deg, color=(0, 0, 0), thickness=6):
    t1 = math.radians(theta1_deg)
    t2 = math.radians(theta2_deg)
    j1 = (root[0] + l1 * math.sin(t1), root[1] + l1 * math.cos(t1))
    j2 = (j1[0] + l2 * math.sin(t1 + t2), j1[1] + l2 * math.cos(t1 + t2))
    draw_line(canvas, root, j1, color, thickness)
    draw_line(canvas, j1, j2, color, thickness)
    return j1, j2

# ==============================================================================
# SCENE 1: SHOT 083 (Campfire Village)
# ==============================================================================
def render_scene1_method2():
    print("Rendering Scene 1 - Method 2 (Ambient Fire & Line Boil)...")
    base = get_base_img(83)
    out_path = os.path.join(out_dir, "scene1_shot083_method2_procedural_fire_boil.mp4")
    proc = create_video_writer(out_path)
    
    # Campfire hearth center
    fx, fy = 960, 680
    
    # Pre-spawn 40 embers
    embers = [{'x': fx + np.random.uniform(-40, 40),
               'y': fy + np.random.uniform(-20, 20),
               'vx': np.random.uniform(-1.0, 1.0),
               'vy': np.random.uniform(-3.5, -1.8),
               'size': np.random.uniform(2, 5),
               'life': np.random.uniform(0.1, 1.0)} for _ in range(45)]
    
    for f in range(TOTAL_FRAMES):
        t = f / FPS
        frame = apply_line_boil(base, f)
        
        # Draw dynamic animated flame tongues
        flame_h = 75 + 18 * math.sin(t * 14.0) + 12 * math.cos(t * 22.0)
        pts_outer = [
            [fx - 55, fy + 20],
            [fx - 30 + 10*math.sin(t*18), fy - flame_h * 0.5],
            [fx + 15*math.sin(t*15), fy - flame_h],
            [fx + 30 + 10*math.cos(t*19), fy - flame_h * 0.6],
            [fx + 55, fy + 20]
        ]
        pts_inner = [
            [fx - 30, fy + 15],
            [fx - 15 + 6*math.sin(t*22), fy - flame_h * 0.4],
            [fx + 8*math.sin(t*20), fy - flame_h * 0.75],
            [fx + 15 + 6*math.cos(t*24), fy - flame_h * 0.45],
            [fx + 30, fy + 15]
        ]
        
        cv2.fillPoly(frame, [np.array(pts_outer, dtype=np.int32)], (30, 140, 255), cv2.LINE_AA) # Orange
        cv2.polylines(frame, [np.array(pts_outer, dtype=np.int32)], True, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.fillPoly(frame, [np.array(pts_inner, dtype=np.int32)], (60, 220, 255), cv2.LINE_AA) # Yellow core
        cv2.polylines(frame, [np.array(pts_inner, dtype=np.int32)], True, (0, 0, 0), 2, cv2.LINE_AA)
        
        # Update and draw floating embers
        for e in embers:
            e['x'] += e['vx'] + 0.8 * math.sin(t * 8.0 + e['y']*0.05)
            e['y'] += e['vy']
            e['life'] += 0.02
            if e['y'] < fy - 220 or e['life'] > 1.0:
                e['x'] = fx + np.random.uniform(-40, 40)
                e['y'] = fy + np.random.uniform(-10, 20)
                e['life'] = 0.0
                
            alpha = max(0.0, min(1.0, 1.0 - (fy - e['y']) / 220.0))
            cv2.circle(frame, (int(e['x']), int(e['y'])), int(e['size']), (40, 160, 255), -1, cv2.LINE_AA)
            cv2.circle(frame, (int(e['x']), int(e['y'])), max(1, int(e['size']-2)), (200, 240, 255), -1, cv2.LINE_AA)
            
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print("  Done Scene 1 Method 2!")

def render_scene1_method3():
    print("Rendering Scene 1 - Method 3 (FK Character Kinematics around Fire)...")
    base = get_base_img(83)
    out_path = os.path.join(out_dir, "scene1_shot083_method3_fk_character_rig.mp4")
    proc = create_video_writer(out_path)
    
    # Campfire position
    fx, fy = 960, 680
    
    for f in range(TOTAL_FRAMES):
        t = f / FPS
        frame = base.copy()
        
        # 1. Left stick figure kneeling/warming hands (sitting at x=830, y=740)
        lx, ly = 810, 740
        b_torso = 4 * math.sin(2 * math.pi * 0.6 * t) # Breathing
        pelvis_l = (lx, ly + b_torso)
        neck_l = (lx + 8, ly - 70 + b_torso)
        head_l = (neck_l[0] + 5, neck_l[1] - 25)
        
        draw_line(frame, pelvis_l, neck_l, (0, 0, 0), 7)
        draw_circle(frame, head_l, 22, (0, 0, 0), (255, 255, 255), 7)
        # Legs folded
        draw_fk_limb(frame, pelvis_l, 35, 35, 75, 90, (0, 0, 0), 7)
        # Arms warming toward fire
        s_ang = 60 + 6 * math.sin(2 * math.pi * 0.8 * t)
        e_ang = 25 + 5 * math.cos(2 * math.pi * 0.8 * t)
        draw_fk_limb(frame, (neck_l[0]-2, neck_l[1]+10), 38, 38, s_ang, e_ang, (0, 0, 0), 6)
        
        # 2. Right stick figure standing/gesturing (x=1110, y=710)
        rx, ry = 1110, 710
        r_torso = 3 * math.sin(2 * math.pi * 0.5 * t + 1.0)
        pelvis_r = (rx, ry + r_torso)
        neck_r = (rx - 5, ry - 90 + r_torso)
        head_r = (neck_r[0] - 5, neck_r[1] - 25)
        
        draw_line(frame, pelvis_r, neck_r, (0, 0, 0), 7)
        draw_circle(frame, head_r, 22, (0, 0, 0), (255, 255, 255), 7)
        # Standing legs
        draw_fk_limb(frame, pelvis_r, 45, 45, 10, 0, (0, 0, 0), 7)
        draw_fk_limb(frame, pelvis_r, 45, 45, -12, 10, (0, 0, 0), 7)
        # Right arm pointing to fire / storytelling gesture
        arm_s = -45 + 15 * math.sin(2 * math.pi * 0.7 * t)
        arm_e = 30 + 10 * math.cos(2 * math.pi * 0.7 * t)
        draw_fk_limb(frame, (neck_r[0]+2, neck_r[1]+10), 36, 36, arm_s, arm_e, (0, 0, 0), 6)
        
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print("  Done Scene 1 Method 3!")

# ==============================================================================
# SCENE 2: SHOT 064 (Stick Figure Walking Toward Predator Eyes)
# ==============================================================================
def render_scene2_method2():
    print("Rendering Scene 2 - Method 2 (Ambient Eyes Pulse & Grass Boil)...")
    base = get_base_img(64)
    out_path = os.path.join(out_dir, "scene2_shot064_method2_procedural_eyes_boil.mp4")
    proc = create_video_writer(out_path)
    
    # Predator eyes location (approx x=1540, y=720 in shot 064)
    ex1, ey1 = 1520, 715
    ex2, ey2 = 1565, 715
    
    for f in range(TOTAL_FRAMES):
        t = f / FPS
        frame = apply_line_boil(base, f)
        
        # Breathing pulse intensity
        pulse = 0.7 + 0.3 * math.sin(t * 5.0)
        
        # Blink every 2.0 seconds: close eyelids for 6 frames
        blink_phase = (t % 2.0)
        eyelid_h = 1.0
        if 1.6 < blink_phase < 1.75:
            eyelid_h = 0.15 # Eyes blink shut!
            
        for ex, ey in [(ex1, ey1), (ex2, ey2)]:
            # Glowing yellow almond eye
            axes = (int(16 * pulse), max(2, int(10 * pulse * eyelid_h)))
            cv2.ellipse(frame, (ex, ey), axes, 0, 0, 360, (30, 230, 255), -1, cv2.LINE_AA) # Yellow glow
            # Slit pupil
            if eyelid_h > 0.3:
                cv2.ellipse(frame, (ex, ey), (3, max(2, int(8 * eyelid_h))), 0, 0, 360, (0, 0, 0), -1, cv2.LINE_AA)
            cv2.ellipse(frame, (ex, ey), axes, 0, 0, 360, (0, 0, 0), 3, cv2.LINE_AA)
            
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print("  Done Scene 2 Method 2!")

def render_scene2_method3():
    print("Rendering Scene 2 - Method 3 (FK Stick Figure Walking Gait)...")
    base = get_base_img(64)
    out_path = os.path.join(out_dir, "scene2_shot064_method3_fk_character_walk.mp4")
    proc = create_video_writer(out_path)
    
    walk_speed = 70.0 # px per second
    start_x = 350
    ground_y = 860
    
    for f in range(TOTAL_FRAMES):
        t = f / FPS
        frame = base.copy()
        
        # Walking gait math (trigonometric Forward Kinematics)
        cur_x = start_x + walk_speed * t
        gait_freq = 1.8 # Strides per second
        cycle = 2 * math.pi * gait_freq * t
        
        # Pelvis vertical bounce
        bounce = 7 * abs(math.sin(cycle))
        pelvis = (cur_x, ground_y - 110 - bounce)
        
        # Torso lean forward 7 degrees
        torso_len = 80
        neck = (pelvis[0] + 12, pelvis[1] - torso_len)
        head = (neck[0] + 5, neck[1] - 30)
        
        # 1. Back leg
        thigh_len = 50
        shin_len = 50
        h_ang2 = -28 * math.sin(cycle)
        k_ang2 = max(0, -55 * math.cos(cycle))
        draw_fk_limb(frame, pelvis, thigh_len, shin_len, h_ang2, k_ang2, (50, 50, 50), 6)
        
        # 2. Back arm
        arm1_len = 40
        arm2_len = 40
        as_ang2 = 25 * math.sin(cycle)
        ae_ang2 = 20 - 15 * math.sin(cycle)
        draw_fk_limb(frame, (neck[0]-2, neck[1]+10), arm1_len, arm2_len, as_ang2, ae_ang2, (50, 50, 50), 6)
        
        # 3. Torso & Head
        draw_line(frame, pelvis, neck, (0, 0, 0), 8)
        draw_circle(frame, head, 26, (0, 0, 0), (255, 255, 255), 8)
        
        # 4. Front leg (FK with natural knee flexion)
        h_ang1 = 28 * math.sin(cycle)
        k_ang1 = max(0, 55 * math.cos(cycle)) # No backward bending
        draw_fk_limb(frame, pelvis, thigh_len, shin_len, h_ang1, k_ang1, (0, 0, 0), 8)
        
        # 5. Front arm
        as_ang1 = -25 * math.sin(cycle)
        ae_ang1 = 20 + 15 * math.sin(cycle)
        draw_fk_limb(frame, (neck[0]+2, neck[1]+10), arm1_len, arm2_len, as_ang1, ae_ang1, (0, 0, 0), 8)
        
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print("  Done Scene 2 Method 3!")

# ==============================================================================
# SCENE 3: SHOT 143 (Starry Night Sky & Constellations)
# ==============================================================================
def render_scene3_method2():
    print("Rendering Scene 3 - Method 2 (Ambient Twinkling Stars & Cel Boil)...")
    base = get_base_img(143)
    out_path = os.path.join(out_dir, "scene3_shot143_method2_procedural_stars_twinkle.mp4")
    proc = create_video_writer(out_path)
    
    # Pre-generate 50 star positions in the upper sky (y < 650)
    np.random.seed(143)
    stars = []
    for _ in range(65):
        stars.append({
            'x': int(np.random.uniform(80, 1840)),
            'y': int(np.random.uniform(60, 580)),
            'base_r': np.random.uniform(3, 7),
            'freq': np.random.uniform(1.2, 3.5),
            'phase': np.random.uniform(0, 2*math.pi)
        })
        
    for f in range(TOTAL_FRAMES):
        t = f / FPS
        frame = apply_line_boil(base, f)
        
        # Draw twinkling stars with 4-point comic sparkles
        for s in stars:
            pulse = 0.5 + 0.5 * math.sin(t * s['freq'] * 2 * math.pi + s['phase'])
            r = int(s['base_r'] * (0.6 + 0.8 * pulse))
            cv2.circle(frame, (s['x'], s['y']), r, (255, 255, 255), -1, cv2.LINE_AA)
            cv2.circle(frame, (s['x'], s['y']), r, (0, 0, 0), 2, cv2.LINE_AA)
            
            # 4-point cross diffraction sparkle on brightest stars
            if pulse > 0.65:
                cross_len = int(r * 2.5 * pulse)
                draw_line(frame, (s['x'] - cross_len, s['y']), (s['x'] + cross_len, s['y']), (0, 0, 0), 2)
                draw_line(frame, (s['x'], s['y'] - cross_len), (s['x'], s['y'] + cross_len), (0, 0, 0), 2)
                draw_line(frame, (s['x'] - cross_len + 1, s['y']), (s['x'] + cross_len - 1, s['y']), (255, 255, 255), 1)
                draw_line(frame, (s['x'], s['y'] - cross_len + 1), (s['x'], s['y'] + cross_len - 1), (255, 255, 255), 1)
                
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print("  Done Scene 3 Method 2!")

def render_scene3_method3():
    print("Rendering Scene 3 - Method 3 (FK Stargazer Tilt & Point Gesture)...")
    base = get_base_img(143)
    out_path = os.path.join(out_dir, "scene3_shot143_method3_fk_character_stargaze.mp4")
    proc = create_video_writer(out_path)
    
    # Position of stargazer stick figure in foreground
    cx, cy = 680, 880
    
    for f in range(TOTAL_FRAMES):
        t = f / FPS
        frame = base.copy()
        
        # Breathing chest
        breath = 3 * math.sin(2 * math.pi * 0.4 * t)
        pelvis = (cx, cy)
        neck = (cx + 5, cy - 105 + breath)
        
        # Smooth interpolation: head tilts back to gaze skyward over first 1.5s
        tilt_factor = min(1.0, t / 1.5)
        neck_tilt_deg = -10 - 28 * tilt_factor # Head tilts upward
        head = (neck[0] - 25 * math.sin(math.radians(-neck_tilt_deg)), neck[1] - 28 * math.cos(math.radians(-neck_tilt_deg)))
        
        # Static standing legs
        draw_fk_limb(frame, pelvis, 55, 55, 12, 0, (0, 0, 0), 8)
        draw_fk_limb(frame, pelvis, 55, 55, -12, 5, (0, 0, 0), 8)
        
        # Torso & Head
        draw_line(frame, pelvis, neck, (0, 0, 0), 8)
        draw_circle(frame, head, 28, (0, 0, 0), (255, 255, 255), 8)
        
        # Left arm resting
        draw_fk_limb(frame, (neck[0]-4, neck[1]+12), 42, 42, 20, 15, (0, 0, 0), 7)
        
        # Right arm smoothly rises to point at the constellations
        arm_raise = min(1.0, max(0.0, (t - 0.5) / 1.5))
        # Smooth cosine ease in-out
        ease_arm = 0.5 - 0.5 * math.cos(math.pi * arm_raise)
        s_angle = 15 - 120 * ease_arm # Points up toward sky
        e_angle = 15 - 10 * ease_arm
        draw_fk_limb(frame, (neck[0]+4, neck[1]+12), 44, 44, s_angle, e_angle, (0, 0, 0), 7)
        
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print("  Done Scene 3 Method 3!")

# ==============================================================================
# SCENE 4: SHOT 088 (Eureka Lightbulb Idea)
# ==============================================================================
def render_scene4_method2():
    print("Rendering Scene 4 - Method 2 (Ambient Electric Bulb Shockwaves & Boil)...")
    base = get_base_img(88)
    out_path = os.path.join(out_dir, "scene4_shot088_method2_procedural_electric_bulb.mp4")
    proc = create_video_writer(out_path)
    
    # Lightbulb center in shot 088
    bx, by = 960, 310
    
    for f in range(TOTAL_FRAMES):
        t = f / FPS
        frame = apply_line_boil(base, f)
        
        # Radiant electric shockwaves bursting outward
        pulse_phase = (t * 2.5) % 1.0
        wave_r = int(50 + 85 * pulse_phase)
        wave_alpha = int(255 * (1.0 - pulse_phase))
        
        overlay = frame.copy()
        cv2.circle(overlay, (bx, by), wave_r, (40, 210, 255), 4, cv2.LINE_AA) # Glowing electric yellow
        # Radiating burst lines
        for ang_deg in range(0, 360, 30):
            rad = math.radians(ang_deg)
            r1 = wave_r - 15
            r2 = wave_r + 15
            p1 = (int(bx + r1 * math.cos(rad)), int(by + r1 * math.sin(rad)))
            p2 = (int(bx + r2 * math.cos(rad)), int(by + r2 * math.sin(rad)))
            draw_line(overlay, p1, p2, (0, 0, 0), 3)
            
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print("  Done Scene 4 Method 2!")

def render_scene4_method3():
    print("Rendering Scene 4 - Method 3 (FK Eureka Jump & Arm Thrust)...")
    base = get_base_img(88)
    out_path = os.path.join(out_dir, "scene4_shot088_method3_fk_character_eureka.mp4")
    proc = create_video_writer(out_path)
    
    cx = 960
    base_ground_y = 860
    
    for f in range(TOTAL_FRAMES):
        t = f / FPS
        frame = base.copy()
        
        # Jump cycle: 1.6s per loop
        loop_t = t % 1.6
        if loop_t < 0.4:
            # Anticipation crouch
            p = loop_t / 0.4
            jump_y = 20 * math.sin(p * math.pi) # Dips down
            knee_flex = 35 * p
            arm_thrust = -20 * p
        elif loop_t < 1.0:
            # Airborne hop
            p = (loop_t - 0.4) / 0.6
            jump_y = -65 * math.sin(p * math.pi) # Launches up
            knee_flex = 5 * (1.0 - p)
            arm_thrust = 110 * math.sin(p * math.pi * 0.8) # Throws arm up pointing at bulb!
        else:
            # Settle / standing
            jump_y = 0
            knee_flex = 0
            arm_thrust = 0
            
        pelvis = (cx, base_ground_y - 110 + jump_y)
        neck = (cx, pelvis[1] - 85)
        head = (cx, neck[1] - 28)
        
        # Legs
        draw_fk_limb(frame, pelvis, 50, 50, -10 + knee_flex*0.3, knee_flex, (0, 0, 0), 8)
        draw_fk_limb(frame, pelvis, 50, 50, 10 - knee_flex*0.3, knee_flex, (0, 0, 0), 8)
        
        # Torso & Head
        draw_line(frame, pelvis, neck, (0, 0, 0), 8)
        draw_circle(frame, head, 27, (0, 0, 0), (255, 255, 255), 8)
        
        # Left arm (balancing)
        draw_fk_limb(frame, (neck[0]-4, neck[1]+10), 40, 40, -45 - arm_thrust*0.4, 30, (0, 0, 0), 7)
        # Right arm (thrusting up pointing at lightbulb!)
        draw_fk_limb(frame, (neck[0]+4, neck[1]+10), 42, 42, 25 - arm_thrust, 15, (0, 0, 0), 7)
        
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print("  Done Scene 4 Method 3!")

# ==============================================================================
# SCENE 5: SHOT 090 (Cartoon Leopard Sulking Away)
# ==============================================================================
def render_scene5_method2():
    print("Rendering Scene 5 - Method 2 (Ambient Sulking Boil & Animated Tears)...")
    base = get_base_img(90)
    out_path = os.path.join(out_dir, "scene5_shot090_method2_procedural_sulking_boil.mp4")
    proc = create_video_writer(out_path)
    
    # Tear drop start position near leopard face (x=460, y=520)
    tx_base, ty_base = 460, 520
    
    for f in range(TOTAL_FRAMES):
        t = f / FPS
        frame = apply_line_boil(base, f)
        
        # Animated falling cartoon tear drop (repeats every 1.2s)
        cycle_t = t % 1.2
        ty = ty_base + 120 * (cycle_t / 1.2) ** 1.6
        tx = tx_base + 5 * math.sin(cycle_t * 6.0)
        
        # Tear drop shape
        cv2.circle(frame, (int(tx), int(ty)), 6, (255, 180, 50), -1, cv2.LINE_AA) # Blue-cyan ink tear
        cv2.circle(frame, (int(tx), int(ty)), 6, (0, 0, 0), 2, cv2.LINE_AA)
        
        # Splash when landing
        if cycle_t > 1.05:
            splash_r = int(14 * (cycle_t - 1.05) / 0.15)
            cv2.ellipse(frame, (int(tx), int(ty_base + 120)), (splash_r, splash_r//2), 0, 0, 360, (0, 0, 0), 2, cv2.LINE_AA)
            
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print("  Done Scene 5 Method 2!")

def render_scene5_method3():
    print("Rendering Scene 5 - Method 3 (FK Quadruped Dragging Gait & Tail Physics)...")
    base = get_base_img(90)
    out_path = os.path.join(out_dir, "scene5_shot090_method3_fk_character_leopard_walk.mp4")
    proc = create_video_writer(out_path)
    
    # Leopard spine root
    lx, ly = 720, 680
    
    for f in range(TOTAL_FRAMES):
        t = f / FPS
        frame = base.copy()
        
        # Sulking quadruped walk gait math
        step_cycle = 2 * math.pi * 1.4 * t
        
        # Head bobs low in sadness
        head_bob = 8 * math.sin(step_cycle)
        head_pos = (lx - 160, ly - 30 + head_bob)
        shoulder = (lx - 80, ly - 50 + head_bob*0.4)
        pelvis = (lx + 80, ly - 45)
        
        # Draw spine
        draw_line(frame, shoulder, pelvis, (0, 0, 0), 10)
        draw_line(frame, shoulder, head_pos, (0, 0, 0), 9)
        draw_circle(frame, head_pos, 32, (0, 0, 0), (255, 255, 255), 9)
        
        # 1. Front Left Leg
        fl_ang1 = 20 * math.sin(step_cycle)
        fl_ang2 = max(0, 35 * math.cos(step_cycle))
        draw_fk_limb(frame, shoulder, 45, 45, fl_ang1, fl_ang2, (0, 0, 0), 8)
        
        # 2. Front Right Leg
        fr_ang1 = -20 * math.sin(step_cycle)
        fr_ang2 = max(0, -35 * math.cos(step_cycle))
        draw_fk_limb(frame, shoulder, 45, 45, fr_ang1, fr_ang2, (50, 50, 50), 7)
        
        # 3. Rear Left Leg
        rl_ang1 = -22 * math.sin(step_cycle + 0.5)
        rl_ang2 = max(0, -35 * math.cos(step_cycle + 0.5))
        draw_fk_limb(frame, pelvis, 48, 48, rl_ang1, rl_ang2, (0, 0, 0), 8)
        
        # 4. Rear Right Leg
        rr_ang1 = 22 * math.sin(step_cycle + 0.5)
        rr_ang2 = max(0, 35 * math.cos(step_cycle + 0.5))
        draw_fk_limb(frame, pelvis, 48, 48, rr_ang1, rr_ang2, (50, 50, 50), 7)
        
        # 5. Tail Physics (Multi-segment traveling wave)
        tail_cur = pelvis
        tail_seg_len = 22
        for seg in range(6):
            tail_wave = 15 * math.sin(step_cycle * 1.5 - seg * 0.7)
            seg_ang = math.radians(45 + seg * 12 + tail_wave)
            next_pt = (tail_cur[0] + tail_seg_len * math.cos(seg_ang), tail_cur[1] + tail_seg_len * math.sin(seg_ang))
            draw_line(frame, tail_cur, next_pt, (0, 0, 0), max(3, 8 - seg))
            tail_cur = next_pt
            
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print("  Done Scene 5 Method 3!")

if __name__ == '__main__':
    render_scene1_method2()
    render_scene1_method3()
    render_scene2_method2()
    render_scene2_method3()
    render_scene3_method2()
    render_scene3_method3()
    render_scene4_method2()
    render_scene4_method3()
    render_scene5_method2()
    render_scene5_method3()
    print("\nALL 10 COMPARISON VIDEOS RENDERED SUCCESSFULLY!")

