import math
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

def generate_pacman_inflation_svg(mouth_angle_deg=30.0, is_bitten=False):
    """
    Classic clean Pac-Man monster facing LEFT.
    mouth_angle_deg: half-angle of mouth opening (e.g. 5 deg closed, 35 deg wide open).
    Mouth opens toward negative X (180 deg).
    Upper jaw line is at 180 + mouth_angle_deg (in SVG coords, where +Y is down, 
    so angle = 180 - mouth_angle_deg goes UP into -Y).
    Lower jaw line is at 180 + mouth_angle_deg goes DOWN into +Y.
    """
    R = 160 # Radius of Pac-Man body
    rad = math.radians(mouth_angle_deg)
    
    # Upper mouth lip point (facing left, angled UP)
    # x = -R * cos(rad), y = -R * sin(rad)
    ux = -R * math.cos(rad)
    uy = -R * math.sin(rad)
    
    # Lower mouth lip point (facing left, angled DOWN)
    # x = -R * cos(rad), y = +R * sin(rad)
    lx = -R * math.cos(rad)
    ly = R * math.sin(rad)
    
    # The SVG arc from upper lip (ux, uy) around the back of head to lower lip (lx, ly)
    # Arc is clockwise (sweep-flag = 1), large-arc-flag = 1 (since angle > 180)
    body_path = f"M 0 0 L {ux:.1f} {uy:.1f} A {R} {R} 0 1 1 {lx:.1f} {ly:.1f} Z"

    # Teeth generation along upper and lower jaw lines
    # Upper jaw goes from (0, 0) to (ux, uy).
    # We place 3-4 sharp triangular teeth along this line pointing into the mouth
    upper_teeth = []
    lower_teeth = []
    num_teeth = 4
    for i in range(1, num_teeth + 1):
        t0 = (i - 0.9) / num_teeth
        t1 = (i - 0.1) / num_teeth
        t_mid = (i - 0.5) / num_teeth
        
        # Base points along the upper jaw line (from (0,0) to (ux, uy))
        bx0 = ux * t0
        by0 = uy * t0
        bx1 = ux * t1
        by1 = uy * t1
        
        # Tooth tip points downward (perpendicular to jaw line into mouth)
        # Jaw unit vector: (cos_j, sin_j) = (-cos(rad), -sin(rad))
        # Normal pointing down into mouth: (sin_rad, -cos_rad)...
        # Since upper jaw goes from origin (-x, -y), perpendicular into mouth (+Y direction)
        # Let's compute exact tooth tip:
        tooth_h = 24
        # normal vector to (ux, uy) pointing into mouth:
        nx = math.sin(rad)
        ny = -math.cos(rad)
        # Note: if rad=0, ux=-R, uy=0. nx=0, ny=-1 (up). We want down (+Y), so nx = -math.sin(rad), ny = math.cos(rad)
        nx = -math.sin(rad)
        ny = math.cos(rad)
        
        tip_x = (ux * t_mid) + nx * tooth_h
        tip_y = (uy * t_mid) + ny * tooth_h
        upper_teeth.append(f'<polygon points="{bx0:.1f},{by0:.1f} {tip_x:.1f},{tip_y:.1f} {bx1:.1f},{by1:.1f}" fill="#ffffff" stroke="#450a0a" stroke-width="3"/>')
        
        # Lower jaw teeth: from (0,0) to (lx, ly)
        lbx0 = lx * t0
        lby0 = ly * t0
        lbx1 = lx * t1
        lby1 = ly * t1
        # Normal pointing UP into mouth: nx = math.sin(rad), ny = -math.cos(rad)
        ltip_x = (lx * t_mid) - nx * tooth_h
        ltip_y = (ly * t_mid) - ny * tooth_h
        lower_teeth.append(f'<polygon points="{lbx0:.1f},{lby0:.1f} {ltip_x:.1f},{ltip_y:.1f} {lbx1:.1f},{lby1:.1f}" fill="#ffffff" stroke="#450a0a" stroke-width="3"/>')

    upper_teeth_svg = "\n".join(upper_teeth)
    lower_teeth_svg = "\n".join(lower_teeth)

    return f"""
    <g id="pacman_inflation_monster">
      <!-- Outer Monster Glow -->
      <filter id="pacGlow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#7f1d1d" flood-opacity="0.5"/>
      </filter>

      <!-- Main Red Pac-Man Body with Pie-Cut Mouth -->
      <path d="{body_path}" 
            fill="#dc2626" 
            stroke="#450a0a" 
            stroke-width="8" 
            stroke-linejoin="round"
            filter="url(#pacGlow)"/>

      <!-- Sharp Upper & Lower Triangular Teeth -->
      <g id="pacman_teeth">
        {upper_teeth_svg}
        {lower_teeth_svg}
      </g>

      <!-- Angry Infographic Brow & Eye -->
      <g id="angry_eye" transform="translate(10, -85)">
        <!-- Eye Sclera -->
        <circle cx="0" cy="0" r="28" fill="#fef08a" stroke="#450a0a" stroke-width="4.5"/>
        <!-- Pupil Looking Forward/Down toward money -->
        <circle cx="-10" cy="2" r="13" fill="#0f172a"/>
        <circle cx="-6" cy="-2" r="4.5" fill="#ffffff"/>
        <!-- Fierce Slanted Angry Eyebrow -->
        <polygon points="-38,-14 26,-36 32,-24 -34,-2" fill="#450a0a"/>
      </g>

      <!-- Bold "INFLATION" Typography Centered on the Body -->
      <g transform="translate(45, 10)">
        <!-- Subtle dark backing banner for maximum readability -->
        <rect x="-85" y="-22" width="170" height="44" rx="10" fill="#450a0a" stroke="#ef4444" stroke-width="2.5"/>
        <text x="0" y="8" 
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

test_pacman_html = f"""<!DOCTYPE html>
<html>
<head>
  <style>
    body {{ background: #070a12; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; font-family: sans-serif; }}
    .row {{ display: flex; gap: 30px; margin-top: 20px; }}
    .card {{ background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 16px; text-align: center; }}
    svg {{ background: #180c10; border-radius: 8px; }}
  </style>
</head>
<body>
  <h1>Clean Pac-Man Monster with Mouth Moving & Teeth</h1>
  <div class="row">
    <div class="card">
      <h3>1. Wide Open Mouth (35&deg;)</h3>
      <svg width="400" height="400" viewBox="-220 -220 440 440" xmlns="http://www.w3.org/2000/svg">
        {generate_pacman_inflation_svg(mouth_angle_deg=35.0)}
      </svg>
    </div>

    <div class="card">
      <h3>2. Mid-Chomp (18&deg;)</h3>
      <svg width="400" height="400" viewBox="-220 -220 440 440" xmlns="http://www.w3.org/2000/svg">
        {generate_pacman_inflation_svg(mouth_angle_deg=18.0)}
      </svg>
    </div>

    <div class="card">
      <h3>3. Clamped Shut on Cash (4&deg;)</h3>
      <svg width="400" height="400" viewBox="-220 -220 440 440" xmlns="http://www.w3.org/2000/svg">
        {generate_pacman_inflation_svg(mouth_angle_deg=4.0)}
      </svg>
    </div>
  </div>
</body>
</html>"""

exp_dir = Path(__file__).resolve().parent
html_path = exp_dir / "test_pacman.html"
with open(html_path, "w", encoding="utf-8") as f:
    f.write(test_pacman_html)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 600})
        await page.goto(html_path.as_uri())
        await page.screenshot(path=str(exp_dir / "test_pacman_result.png"))
        await browser.close()
    print("Screenshot saved to test_pacman_result.png")

asyncio.run(main())
