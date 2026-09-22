import math
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

def generate_refined_pacman(mouth_angle_deg=28.0):
    """
    Classic, clean, iconic Pac-Man monster:
    - Circle facing LEFT with genuine SVG pie-cut mouth that opens and closes
    - Interlocking sharp triangular teeth (alternating positions)
    - Angry cartoon eyebrow & eye looking down at the cash
    - Bold "INFLATION" lettering stamped cleanly on the body
    """
    R = 150
    rad = math.radians(mouth_angle_deg)
    
    # Upper & lower lip points
    ux = -R * math.cos(rad)
    uy = -R * math.sin(rad)
    lx = -R * math.cos(rad)
    ly = R * math.sin(rad)
    
    # Pac-Man circular wedge path (opens to the left)
    body_path = f"M 0 0 L {ux:.1f} {uy:.1f} A {R} {R} 0 1 1 {lx:.1f} {ly:.1f} Z"

    # Interlocking teeth:
    # Upper teeth at t = [0.22, 0.48, 0.74]
    # Lower teeth at t = [0.35, 0.61, 0.87]
    upper_teeth = []
    lower_teeth = []
    tooth_w = 26
    tooth_h = 24

    for t in [0.24, 0.50, 0.76]:
        # Upper jaw: tip points down (+Y)
        bx0 = ux * (t - 0.08)
        by0 = uy * (t - 0.08)
        bx1 = ux * (t + 0.08)
        by1 = uy * (t + 0.08)
        tip_x = (ux * t) - math.sin(rad) * tooth_h
        tip_y = (uy * t) + math.cos(rad) * tooth_h
        upper_teeth.append(f'<polygon points="{bx0:.1f},{by0:.1f} {tip_x:.1f},{tip_y:.1f} {bx1:.1f},{by1:.1f}" fill="#ffffff" stroke="#3b0707" stroke-width="3"/>')

    for t in [0.37, 0.63, 0.89]:
        # Lower jaw: tip points up (-Y)
        bx0 = lx * (t - 0.08)
        by0 = ly * (t - 0.08)
        bx1 = lx * (t + 0.08)
        by1 = ly * (t + 0.08)
        tip_x = (lx * t) - math.sin(rad) * tooth_h
        tip_y = (ly * t) - math.cos(rad) * tooth_h
        lower_teeth.append(f'<polygon points="{bx0:.1f},{by0:.1f} {tip_x:.1f},{tip_y:.1f} {bx1:.1f},{by1:.1f}" fill="#ffffff" stroke="#3b0707" stroke-width="3"/>')

    return f"""
    <g id="pacman_monster">
      <!-- Subtle Dark Red Glow -->
      <filter id="pacGlow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#7f1d1d" flood-opacity="0.6"/>
      </filter>

      <!-- Inside Mouth Dark Cavern (Only visible when open) -->
      <path d="M 0 0 L {ux:.1f} {uy:.1f} L {lx:.1f} {ly:.1f} Z" fill="#180c10"/>

      <!-- Main Vibrant Red Circular Body with Moving Mouth Cutout -->
      <path d="{body_path}" 
            fill="#ef4444" 
            stroke="#450a0a" 
            stroke-width="7" 
            stroke-linejoin="round"
            filter="url(#pacGlow)"/>

      <!-- Interlocking Sharp White Teeth -->
      <g id="teeth">
        {' '.join(upper_teeth)}
        {' '.join(lower_teeth)}
      </g>

      <!-- Angry Characterful Eye -->
      <g id="angry_eye" transform="translate(15, -75)">
        <circle cx="0" cy="0" r="26" fill="#fef08a" stroke="#450a0a" stroke-width="4"/>
        <circle cx="-10" cy="3" r="12" fill="#0f172a"/>
        <circle cx="-6" cy="-1" r="4" fill="#ffffff"/>
        <!-- Fierce Slanted Brow -->
        <polygon points="-36,-12 24,-32 28,-22 -32,-2" fill="#450a0a"/>
      </g>

      <!-- Clean "INFLATION" Badge on Body -->
      <g transform="translate(50, 8)">
        <rect x="-75" y="-22" width="150" height="44" rx="12" fill="#450a0a" stroke="#ffffff" stroke-width="2"/>
        <text x="0" y="9" 
              font-family="'Impact', 'Arial Black', sans-serif" 
              font-size="28" 
              font-weight="900" 
              fill="#ffffff" 
              text-anchor="middle" 
              letter-spacing="2">
          INFLATION
        </text>
      </g>
    </g>
    """

scene3_demo_html = f"""<!DOCTYPE html>
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
  <h1>Refined Pac-Man Monster in Scene 3 Context</h1>
  <div class="row">
    <!-- Frame 1: Chomping in Mid-Air -->
    <div class="card">
      <h3>1. Chomping Approach (Mouth Open 28&deg;)</h3>
      <svg width="650" height="480" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">
        <rect width="1920" height="1080" fill="#180c10"/>
        <circle cx="960" cy="540" r="800" fill="#450a0a" opacity="0.6"/>

        <!-- WRONG! Stamp -->
        <g transform="translate(960, 220) rotate(-14)">
          <rect x="-240" y="-60" width="480" height="120" rx="16" fill="#dc2626" stroke="#ffffff" stroke-width="8"/>
          <rect x="-225" y="-45" width="450" height="90" rx="10" fill="none" stroke="#ffffff" stroke-width="4" stroke-dasharray="14 10"/>
          <text x="0" y="24" font-family="'Impact', 'Arial Black', sans-serif" font-size="82" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="6">WRONG!</text>
        </g>

        <!-- Intact Cash Stack -->
        <g transform="translate(920, 520)">
          <rect x="-130" y="-75" width="260" height="150" rx="14" fill="#047857" stroke="#064e3b" stroke-width="4" transform="translate(6, 10)"/>
          <rect x="-130" y="-75" width="260" height="150" rx="14" fill="#10b981" stroke="#047857" stroke-width="5"/>
          <rect x="-115" y="-60" width="230" height="120" rx="10" fill="#ecfdf5" stroke="#059669" stroke-width="3"/>
          <circle cx="0" cy="0" r="36" fill="#d1fae5" stroke="#059669" stroke-width="2"/>
          <text x="0" y="12" font-family="'Impact', 'Arial Black', sans-serif" font-size="44" font-weight="900" fill="#065f46" text-anchor="middle">$54,000</text>
        </g>

        <!-- Pac-Man Approaching (Mouth Open) -->
        <g transform="translate(1380, 520)">
          {generate_refined_pacman(mouth_angle_deg=28.0)}
        </g>
      </svg>
    </div>

    <!-- Frame 2: Clamped Down on Cash -->
    <div class="card">
      <h3>2. Clamped Down & Cash Bitten (Mouth Clamped 5&deg;)</h3>
      <svg width="650" height="480" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">
        <rect width="1920" height="1080" fill="#180c10"/>
        <circle cx="960" cy="540" r="800" fill="#450a0a" opacity="0.6"/>

        <!-- WRONG! Stamp -->
        <g transform="translate(960, 220) rotate(-14)">
          <rect x="-240" y="-60" width="480" height="120" rx="16" fill="#dc2626" stroke="#ffffff" stroke-width="8"/>
          <rect x="-225" y="-45" width="450" height="90" rx="10" fill="none" stroke="#ffffff" stroke-width="4" stroke-dasharray="14 10"/>
          <text x="0" y="24" font-family="'Impact', 'Arial Black', sans-serif" font-size="82" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="6">WRONG!</text>
        </g>

        <!-- Bitten Severed Cash Stack -->
        <g transform="translate(920, 520)">
          <path d="M -130 -75 L 10 -75 C -10 -40 -35 -15 5 0 C -25 25 -10 50 15 75 L -130 75 Z" fill="#10b981" stroke="#047857" stroke-width="5"/>
          <path d="M -115 -60 L 0 -60 C -15 -35 -35 -10 0 0 C -20 20 -5 40 5 60 L -115 60 Z" fill="#ecfdf5"/>
          <text x="-55" y="12" font-family="'Impact', 'Arial Black', sans-serif" font-size="38" font-weight="900" fill="#065f46" text-anchor="middle">$27K</text>
          
          <!-- Flying Dollar Crumbs -->
          <g transform="translate(50, -50) rotate(25)"><rect x="-16" y="-10" width="32" height="20" rx="3" fill="#10b981" stroke="#047857" stroke-width="2"/><text x="0" y="4" font-size="10" font-weight="900" fill="#ffffff" text-anchor="middle">$</text></g>
          <g transform="translate(70, 40) rotate(-30)"><rect x="-14" y="-9" width="28" height="18" rx="3" fill="#34d399" stroke="#047857" stroke-width="2"/><text x="0" y="4" font-size="10" font-weight="900" fill="#ffffff" text-anchor="middle">$</text></g>
          <circle cx="35" cy="-60" r="6" fill="#34d399"/>
          <circle cx="60" cy="70" r="5" fill="#10b981"/>
        </g>

        <!-- Pac-Man Clamped on Cash (Mouth Clamped) -->
        <g transform="translate(1070, 520)">
          {generate_refined_pacman(mouth_angle_deg=5.0)}
          <!-- Comic Impact CHOMP! Starburst -->
          <g transform="translate(-140, 0)">
            <polygon points="0,-65 20,-20 65,-35 32,0 70,30 22,20 28,65 -8,28 -50,60 -25,12 -65,-8 -18,-18" 
                     fill="#fbbf24" stroke="#dc2626" stroke-width="5"/>
            <polygon points="0,-48 15,-15 48,-26 24,0 52,22 16,15 20,48 -6,20 -38,45 -18,9 -48,-6 -14,-14" 
                     fill="#ffffff" stroke="#f59e0b" stroke-width="2.5"/>
            <text x="0" y="10" font-family="'Impact', 'Arial Black', sans-serif" font-size="28" font-weight="900" fill="#dc2626" text-anchor="middle" letter-spacing="2">CHOMP!</text>
          </g>
        </g>

        <!-- Zero-Overflow Purchasing Power Badge -->
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
html_path = exp_dir / "test_pacman_demo.html"
with open(html_path, "w", encoding="utf-8") as f:
    f.write(scene3_demo_html)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 700})
        await page.goto(html_path.as_uri())
        await page.screenshot(path=str(exp_dir / "test_pacman_demo_result.png"))
        await browser.close()
    print("Screenshot saved to test_pacman_demo_result.png")

asyncio.run(main())
