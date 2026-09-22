import os
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

def render_demon_beast_svg(jaw_open=1.0, show_chomp=False):
    """
    jaw_open: 1.0 = wide open roaring attack (~38 deg)
              0.0 = snapped shut clamped on prey (~0 deg)
    """
    jaw_angle = 38.0 * jaw_open

    return f"""
    <g id="apex_inflation_demon">
      <!-- Defs & Gradients unique to beast -->
      <defs>
        <linearGradient id="beastSkinGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#ef4444"/>
          <stop offset="35%" stop-color="#dc2626"/>
          <stop offset="70%" stop-color="#991b1b"/>
          <stop offset="100%" stop-color="#450a0a"/>
        </linearGradient>
        <linearGradient id="beastPlateGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#1e1b4b"/>
          <stop offset="50%" stop-color="#0f172a"/>
          <stop offset="100%" stop-color="#020617"/>
        </linearGradient>
        <linearGradient id="beastUnderbellyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#f87171"/>
          <stop offset="50%" stop-color="#b91c1c"/>
          <stop offset="100%" stop-color="#7f1d1d"/>
        </linearGradient>
        <linearGradient id="hornGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#312e81"/>
          <stop offset="40%" stop-color="#1e1b4b"/>
          <stop offset="80%" stop-color="#0f172a"/>
          <stop offset="100%" stop-color="#020617"/>
        </linearGradient>
        <radialGradient id="eyeGlowGrad" cx="35%" cy="35%" r="65%">
          <stop offset="0%" stop-color="#fef08a"/>
          <stop offset="45%" stop-color="#f59e0b"/>
          <stop offset="85%" stop-color="#ea580c"/>
          <stop offset="100%" stop-color="#9a3412"/>
        </radialGradient>
        <radialGradient id="hellfireAura" cx="30%" cy="40%" r="60%">
          <stop offset="0%" stop-color="#ef4444" stop-opacity="0.45"/>
          <stop offset="40%" stop-color="#dc2626" stop-opacity="0.2"/>
          <stop offset="80%" stop-color="#450a0a" stop-opacity="0.05"/>
          <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
        </radialGradient>
        <filter id="beastGlowFx" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="8" result="blur"/>
          <feComposite in="SourceGraphic" in2="blur" operator="over"/>
        </filter>
      </defs>

      <!-- Hellfire Ambient Aura -->
      <ellipse cx="60" cy="10" rx="450" ry="320" fill="url(#hellfireAura)"/>

      <!-- 1. DORSAL SPIKE RIDGE (Along Neck & Spine) -->
      <g id="dorsal_spikes">
        <!-- Spikes extending backwards -->
        <polygon points="110,-120 180,-240 210,-110" fill="url(#beastPlateGrad)" stroke="#450a0a" stroke-width="4"/>
        <polygon points="180,-100 270,-220 290,-80" fill="url(#beastPlateGrad)" stroke="#450a0a" stroke-width="4"/>
        <polygon points="260,-80 360,-190 370,-50" fill="url(#beastPlateGrad)" stroke="#450a0a" stroke-width="4"/>
        <polygon points="340,-50 440,-150 450,-20" fill="url(#beastPlateGrad)" stroke="#450a0a" stroke-width="4"/>
      </g>

      <!-- 2. POWERFUL ARCHED MUSCULAR NECK & BODY -->
      <g id="muscular_neck">
        <!-- Main Muscular Neck Form (Tapering from heavy body on right to head on left) -->
        <path d="M -40 -80 
                 C 80 -140, 240 -120, 480 -60 
                 L 480 260 
                 C 300 270, 160 240, 0 170 
                 C -50 110, -60 0, -40 -80 Z" 
              fill="url(#beastSkinGrad)" stroke="#2b0505" stroke-width="8" stroke-linejoin="round"/>

        <!-- Armored Scute Plates on Upper Neck -->
        <path d="M 40 -95 C 160 -115, 300 -90, 460 -40 L 460 20 C 300 -30, 160 -40, 40 -30 Z" 
              fill="#991b1b" opacity="0.6" stroke="#450a0a" stroke-width="3"/>
        <path d="M 20 -15 C 150 -25, 290 0, 460 50 L 460 110 C 290 60, 150 40, 20 40 Z" 
              fill="#7f1d1d" opacity="0.5" stroke="#450a0a" stroke-width="3"/>

        <!-- Scaled Ventral Underbelly -->
        <path d="M 0 130 C 130 170, 280 200, 480 215 L 480 260 C 300 270, 160 240, 0 170 Z" 
              fill="url(#beastUnderbellyGrad)" stroke="#2b0505" stroke-width="5"/>
        <line x1="70" y1="152" x2="120" y2="208" stroke="#450a0a" stroke-width="4.5" stroke-linecap="round"/>
        <line x1="160" y1="172" x2="210" y2="228" stroke="#450a0a" stroke-width="4.5" stroke-linecap="round"/>
        <line x1="260" y1="188" x2="310" y2="242" stroke="#450a0a" stroke-width="4.5" stroke-linecap="round"/>
        <line x1="360" y1="202" x2="410" y2="252" stroke="#450a0a" stroke-width="4.5" stroke-linecap="round"/>
      </g>

      <!-- 3. MASSIVE CURVED SWEEPING HORNS -->
      <g id="horns">
        <!-- Far Horn (Darker Silhouette) -->
        <path d="M -30 -90 C 0 -220, 100 -310, 260 -290 C 150 -260, 60 -190, 25 -80 Z" 
              fill="#090d16" stroke="#2b0505" stroke-width="6" stroke-linejoin="round"/>
        <path d="M 40 -190 C 100 -250, 170 -275, 240 -275" fill="none" stroke="#6366f1" stroke-width="3.5" opacity="0.6" stroke-linecap="round"/>

        <!-- Near Primary Horn (Sweeping, Majestic, Armored) -->
        <path d="M -70 -70 C -40 -230, 80 -320, 240 -310 C 120 -270, 20 -180, -10 -45 Z" 
              fill="url(#hornGrad)" stroke="#2b0505" stroke-width="8" stroke-linejoin="round"/>
        <!-- Horn Specular Edge -->
        <path d="M -30 -120 C 0 -220, 80 -285, 210 -290" fill="none" stroke="#a855f7" stroke-width="5" stroke-linecap="round" opacity="0.8"/>
        <path d="M -20 -95 C 10 -180, 70 -245, 170 -260" fill="none" stroke="#fb7185" stroke-width="3" stroke-linecap="round" opacity="0.6"/>

        <!-- Secondary Crown Spike -->
        <polygon points="-110,-55 -150,-120 -80,-75" fill="url(#beastPlateGrad)" stroke="#2b0505" stroke-width="4.5"/>
      </g>

      <!-- 4. HINGED LOWER JAW RIG (Hinge Pivot at (0, 30)) -->
      <!-- Jaw opens by rotating around (0, 30). In SVG +Y is down, so positive rotation swings DOWN -->
      <g id="lower_jaw_rig" transform="translate(0, 30) rotate({jaw_angle}) translate(0, -30)">
        <!-- Inside Throat Cavern (Dark Blood Crimson & Black) -->
        <path d="M -240 30 C -160 5, -30 0, 10 30 C -20 80, -130 90, -230 45 Z" fill="#120406"/>
        
        <!-- Sinister Barb Tongue with Venom / Flame Sparks -->
        <path d="M -160 32 Q -70 12, 0 30 Q -60 55, -150 40 Z" fill="#e11d48" stroke="#881337" stroke-width="3"/>
        <circle cx="-120" cy="30" r="3" fill="#fde047"/>
        <circle cx="-80" cy="24" r="2.5" fill="#f59e0b"/>

        <!-- Lower Jaw Bone (Aggressive Underbite & Armored Chin) -->
        <path d="M -260 30 
                 C -230 95, -120 120, 10 35 
                 C -10 90, -120 115, -230 45 Z" 
              fill="url(#beastSkinGrad)" stroke="#2b0505" stroke-width="8" stroke-linejoin="round"/>

        <!-- Heavy Armored Chin Scute -->
        <path d="M -255 40 C -225 85, -150 105, -70 90 L -110 110 C -180 112, -235 88, -255 40 Z" 
              fill="#7f1d1d" stroke="#2b0505" stroke-width="4"/>

        <!-- Lower Jaw Razor Fangs (Daggers Pointing UP) -->
        <g id="lower_fangs">
          <!-- Colossal Lower Canine Tusk (Overlaps outside upper snout when closed) -->
          <polygon points="-245,34 -220,-30 -202,36" fill="#ffffff" stroke="#2b0505" stroke-width="4"/>
          <polygon points="-198,36 -180,-14 -164,38" fill="#ffffff" stroke="#2b0505" stroke-width="3.5"/>
          <polygon points="-160,38 -144,-2 -130,40" fill="#ffffff" stroke="#2b0505" stroke-width="3"/>
          <polygon points="-126,40 -114,6 -100,40" fill="#ffffff" stroke="#2b0505" stroke-width="3"/>
          <polygon points="-96,40 -85,12 -74,40" fill="#ffffff" stroke="#2b0505" stroke-width="2.5"/>
        </g>
      </g>

      <!-- 5. UPPER CRANIUM, SNOUT & RAZOR FANGS -->
      <g id="upper_cranium">
        <!-- Main Skull Contour (Fierce, Chiseled Predator Profile) -->
        <path d="M -50 -70 
                 C -120 -95, -200 -75, -270 5 
                 C -240 28, -170 26, -90 22 
                 C -20 20, 10 -10, -10 -50 Z" 
              fill="url(#beastSkinGrad)" stroke="#2b0505" stroke-width="8" stroke-linejoin="round"/>

        <!-- Snout Armored Ridge & Contour Lines -->
        <path d="M -120 -60 C -180 -50, -225 -20, -255 5" fill="none" stroke="#f87171" stroke-width="5.5" stroke-linecap="round" opacity="0.65"/>
        <path d="M -80 -45 C -140 -35, -185 -10, -215 12" fill="none" stroke="#fca5a5" stroke-width="4" stroke-linecap="round" opacity="0.45"/>

        <!-- Nostril & Smoldering Embers -->
        <ellipse cx="-245" cy="-2" rx="15" ry="9" fill="#090507" stroke="#2b0505" stroke-width="3" transform="rotate(-15 -245 -2)"/>
        <path d="M -260 -8 Q -310 -35, -280 -75 Q -255 -38, -240 -20" fill="none" stroke="#fdba74" stroke-width="4" stroke-linecap="round" stroke-dasharray="12 8" opacity="0.85"/>
        <circle cx="-290" cy="-45" r="5" fill="#f59e0b" filter="url(#beastGlowFx)"/>
        <circle cx="-315" cy="-65" r="7" fill="#ef4444" filter="url(#beastGlowFx)"/>
        <circle cx="-330" cy="-50" r="4" fill="#fbbf24" filter="url(#beastGlowFx)"/>

        <!-- PREDATORY EYE & HEAVY OBSIDIAN BROW -->
        <g id="demon_eye" transform="translate(-125, -25)">
          <!-- Deep Dark Socket -->
          <polygon points="-48,-14 15,-32 52,-4 15,20 -42,16" fill="#090507" stroke="#2b0505" stroke-width="4"/>
          <!-- Glowing Sulfur-Gold Iris -->
          <ellipse cx="4" cy="-3" rx="36" ry="17" fill="url(#eyeGlowGrad)" stroke="#2b0505" stroke-width="2.5" transform="rotate(-5)"/>
          <!-- Vertical Razor Slit Pupil -->
          <polygon points="-2,-15 4,-2 -2,13 -7,-2" fill="#090d16"/>
          <!-- Gloss Specular Highlights -->
          <circle cx="-6" cy="-6" r="4.5" fill="#ffffff"/>
          <circle cx="11" cy="-1" r="2.5" fill="#ffffff" opacity="0.8"/>
          <!-- Armored Obsidian Brow (Heavy, Menacing) -->
          <path d="M -60 -20 C -25 -48, 25 -44, 62 -4 C 25 -22, -18 -28, -48 -14 Z" 
                fill="url(#beastPlateGrad)" stroke="#2b0505" stroke-width="5" stroke-linejoin="round"/>
        </g>

        <!-- Upper Razor Dagger Fangs (Pointing DOWN) -->
        <g id="upper_fangs">
          <polygon points="-80,22 -68,44 -58,22" fill="#ffffff" stroke="#2b0505" stroke-width="3"/>
          <polygon points="-110,22 -96,48 -84,22" fill="#ffffff" stroke="#2b0505" stroke-width="3.5"/>
          <polygon points="-140,22 -124,56 -112,22" fill="#ffffff" stroke="#2b0505" stroke-width="3.5"/>
          <polygon points="-175,20 -158,62 -142,20" fill="#ffffff" stroke="#2b0505" stroke-width="4"/>
          <!-- Colossal Saber Tooth -->
          <polygon points="-218,14 -194,76 -176,18" fill="#ffffff" stroke="#2b0505" stroke-width="4.5"/>
          <!-- Front Snout Fang -->
          <polygon points="-254,4 -236,50 -220,10" fill="#ffffff" stroke="#2b0505" stroke-width="4"/>
        </g>
      </g>

      <!-- 6. REACHING PREDATOR TALON CLAW (Clutching Forward into Frame) -->
      <g id="predator_arm" transform="translate(-10, 95) rotate(-12)">
        <!-- Muscular Arm Forelimb -->
        <path d="M 50 -20 C -15 20, -80 50, -160 40" fill="none" stroke="#2b0505" stroke-width="38" stroke-linecap="round"/>
        <path d="M 50 -20 C -15 20, -80 50, -160 40" fill="none" stroke="url(#beastSkinGrad)" stroke-width="28" stroke-linecap="round"/>
        <!-- Armored Elbow Scute -->
        <polygon points="40,-30 90,-55 55,5" fill="url(#beastPlateGrad)" stroke="#2b0505" stroke-width="4"/>
        
        <!-- Wrist & Razor Talons -->
        <g transform="translate(-160, 40)">
          <!-- Wrist Joint -->
          <circle cx="0" cy="0" r="22" fill="#7f1d1d" stroke="#2b0505" stroke-width="4.5"/>
          <!-- 3 Curved Obsidian & Bone Claws -->
          <path d="M -8 -12 Q -48 -18 -75 -40 Q -42 6 -8 6 Z" fill="#ffffff" stroke="#2b0505" stroke-width="4"/>
          <path d="M -12 2 Q -65 10 -90 -10 Q -48 28 -10 18 Z" fill="#ffffff" stroke="#2b0505" stroke-width="4.5"/>
          <path d="M -8 16 Q -54 40 -70 26 Q -38 48 -6 26 Z" fill="#ffffff" stroke="#2b0505" stroke-width="4"/>
        </g>
      </g>

      <!-- 7. COMIC IMPACT CHOMP BURST FX (At Jaw Closure) -->
      {'''
      <g id="chomp_fx" transform="translate(-200, 30)" filter="url(#beastGlowFx)">
        <!-- Outer Shockwave Blast Star -->
        <polygon points="0,-105 35,-35 115,-60 55,0 120,55 40,35 50,120 -15,50 -90,105 -50,20 -120,-15 -35,-35" 
                 fill="#fbbf24" stroke="#dc2626" stroke-width="7"/>
        <!-- Inner Core Star -->
        <polygon points="0,-75 25,-25 85,-45 40,0 90,40 28,25 35,90 -10,38 -65,75 -35,15 -85,-10 -25,-25" 
                 fill="#ffffff" stroke="#f59e0b" stroke-width="4"/>
        <text x="0" y="16" font-family="'Impact', 'Arial Black', sans-serif" font-size="44" font-weight="900" fill="#dc2626" text-anchor="middle" letter-spacing="3">CHOMP!</text>
      </g>
      ''' if show_chomp else ''}

      <!-- 8. HERALDIC GOLD & OBSIDIAN BADGE -->
      <g transform="translate(80, -185)" filter="url(#beastGlowFx)">
        <polygon points="-140,-34 140,-34 160,14 0,52 -160,14" fill="#0f172a" stroke="#f59e0b" stroke-width="5.5"/>
        <polygon points="-132,-28 132,-28 150,10 0,45 -150,10" fill="#7f1d1d" stroke="#ef4444" stroke-width="2.5"/>
        <text x="0" y="4" font-family="'Montserrat', 'Impact', sans-serif" font-size="32" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="4">INFLATION</text>
        <text x="0" y="30" font-family="'Inter', sans-serif" font-size="11" font-weight="900" fill="#fde047" text-anchor="middle" letter-spacing="2.5">THE WEALTH DESTROYER</text>
      </g>
    </g>
    """

scene3_preview_html = f"""<!DOCTYPE html>
<html>
<head>
  <style>
    body {{ background: #070a12; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; font-family: sans-serif; }}
    .row {{ display: flex; gap: 30px; margin-top: 20px; }}
    .card {{ background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 16px; text-align: center; }}
    svg {{ background: #180c10; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); }}
  </style>
</head>
<body>
  <h1>Scene 3 Beast Redesign: Gaping Maw vs Biting Cash Stack</h1>
  <div class="row">
    <!-- Frame A: Gaping Lunge -->
    <div class="card">
      <h3>Beat 4: Beast Lunging (Jaw Gaping Wide)</h3>
      <svg width="650" height="500" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">
        <rect width="1920" height="1080" fill="#180c10"/>
        <circle cx="960" cy="540" r="800" fill="#450a0a" opacity="0.75"/>

        <!-- WRONG! Rubber Stamp -->
        <g transform="translate(960, 200) rotate(-14) scale(1.0)" filter="url(#beastGlowFx)">
          <rect x="-240" y="-60" width="480" height="120" rx="16" fill="#dc2626" stroke="#ffffff" stroke-width="8"/>
          <rect x="-225" y="-45" width="450" height="90" rx="10" fill="none" stroke="#ffffff" stroke-width="4" stroke-dasharray="14 10"/>
          <text x="0" y="24" font-family="'Impact', 'Arial Black', sans-serif" font-size="82" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="6">WRONG!</text>
        </g>

        <!-- Full Intact Cash Stack $54,000 -->
        <g transform="translate(880, 560)">
          <!-- 3D Banknote Shadow -->
          <rect x="-140" y="-80" width="280" height="160" rx="16" fill="#022c22" opacity="0.6" transform="translate(8, 14)"/>
          <!-- 3D Banknote Stack Layers -->
          <rect x="-140" y="-70" width="280" height="150" rx="14" fill="#047857" stroke="#064e3b" stroke-width="4"/>
          <rect x="-140" y="-80" width="280" height="150" rx="14" fill="#10b981" stroke="#047857" stroke-width="5"/>
          <!-- Bill Inner Border -->
          <rect x="-124" y="-66" width="248" height="122" rx="10" fill="#ecfdf5" stroke="#059669" stroke-width="3"/>
          <circle cx="0" cy="-5" r="42" fill="#d1fae5" stroke="#059669" stroke-width="2"/>
          <text x="0" y="8" font-family="'Impact', 'Arial Black', sans-serif" font-size="40" font-weight="900" fill="#065f46" text-anchor="middle">$54,000</text>
          <!-- Gold Security Band -->
          <rect x="-25" y="-80" width="50" height="150" fill="#fbbf24" opacity="0.4"/>
          <line x1="-25" y1="-80" x2="-25" y2="70" stroke="#d97706" stroke-width="2"/>
          <line x1="25" y1="-80" x2="25" y2="70" stroke="#d97706" stroke-width="2"/>
        </g>

        <!-- Beast Lunging into frame from right (Jaw Open 100%) -->
        <g transform="translate(1380, 520) scale(1.1)">
          {render_demon_beast_svg(jaw_open=1.0, show_chomp=False)}
        </g>
      </svg>
    </div>

    <!-- Frame B: Biting Down Hard -->
    <div class="card">
      <h3>Beat 5: Beast Clamped Down (Cash Severed in Half)</h3>
      <svg width="650" height="500" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">
        <rect width="1920" height="1080" fill="#180c10"/>
        <circle cx="960" cy="540" r="800" fill="#450a0a" opacity="0.75"/>

        <!-- WRONG! Rubber Stamp -->
        <g transform="translate(960, 200) rotate(-14) scale(1.0)">
          <rect x="-240" y="-60" width="480" height="120" rx="16" fill="#dc2626" stroke="#ffffff" stroke-width="8"/>
          <rect x="-225" y="-45" width="450" height="90" rx="10" fill="none" stroke="#ffffff" stroke-width="4" stroke-dasharray="14 10"/>
          <text x="0" y="24" font-family="'Impact', 'Arial Black', sans-serif" font-size="82" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="6">WRONG!</text>
        </g>

        <!-- SEVERED CASH STACK (Bitten 50% Off) -->
        <g transform="translate(880, 560)">
          <!-- Severed Left Half with Ragged Bite Mark -->
          <path d="M -140 -80 
                   L 20 -80 
                   C 0 -50, -30 -20, 10 0 
                   C -25 30, -10 60, 25 70 
                   L -140 70 Z" 
                fill="#10b981" stroke="#047857" stroke-width="5"/>
          <path d="M -124 -66 
                   L 10 -66 
                   C -8 -40, -40 -15, 0 0 
                   C -35 25, -20 50, 15 56 
                   L -124 56 Z" 
                fill="#ecfdf5" stroke="#059669" stroke-width="2.5"/>
          <text x="-65" y="8" font-family="'Impact', 'Arial Black', sans-serif" font-size="34" font-weight="900" fill="#065f46" text-anchor="middle">$27,000</text>
          
          <!-- Flying Shredded Banknote Scraps -->
          <g transform="translate(60, -60) rotate(32)">
            <rect x="-22" y="-12" width="44" height="24" rx="4" fill="#10b981" stroke="#047857" stroke-width="2"/>
            <text x="0" y="5" font-family="sans-serif" font-size="12" font-weight="900" fill="#ffffff" text-anchor="middle">$</text>
          </g>
          <g transform="translate(90, 45) rotate(-28)">
            <rect x="-20" y="-11" width="40" height="22" rx="4" fill="#34d399" stroke="#065f46" stroke-width="2"/>
            <text x="0" y="5" font-family="sans-serif" font-size="11" font-weight="900" fill="#ffffff" text-anchor="middle">$</text>
          </g>
          <g transform="translate(45, 80) rotate(15)">
            <rect x="-16" y="-9" width="32" height="18" rx="3" fill="#10b981" stroke="#047857" stroke-width="2"/>
          </g>
          <circle cx="45" cy="-80" r="6" fill="#34d399"/>
          <circle cx="110" cy="-10" r="8" fill="#10b981"/>
          <circle cx="80" cy="95" r="5" fill="#6ee7b7"/>
        </g>

        <!-- Beast Clamped Down on Cash Stack (Jaw Angle 0 deg, mouth clamped) -->
        <g transform="translate(1120, 520) scale(1.1)">
          {render_demon_beast_svg(jaw_open=0.0, show_chomp=True)}
        </g>

        <!-- PURCHASING POWER BADGE -->
        <g transform="translate(960, 830)">
          <rect x="-320" y="-46" width="640" height="92" rx="46" fill="#450a0a" stroke="#dc2626" stroke-width="5"/>
          <polygon points="-245,14 -259,-8 -231,-8" fill="#ef4444" stroke="#ffffff" stroke-width="2"/>
          <text x="25" y="10" font-family="'Montserrat', 'Arial Black', sans-serif" font-size="28" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="1">
            PURCHASING POWER: <tspan fill="#fca5a5" font-weight="900">-50%</tspan>
          </text>
        </g>
      </svg>
    </div>
  </div>
</body>
</html>"""

exp_dir = Path(__file__).resolve().parent
html_path = exp_dir / "test_kaiju_v3.html"
with open(html_path, "w", encoding="utf-8") as f:
    f.write(scene3_preview_html)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 750})
        await page.goto(html_path.as_uri())
        await page.screenshot(path=str(exp_dir / "test_kaiju_v3_result.png"))
        await browser.close()
    print("Screenshot saved to test_kaiju_v3_result.png")

asyncio.run(main())
