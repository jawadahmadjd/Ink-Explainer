/**
 * SCENE ASSETS ENGINE: SCENES 2 THROUGH 5 (REVISION 3 - POLISHED ASSETS & TANGENT ROCKET)
 * 
 * Features:
 * - Iconic Menacing Inflation Monster (Pac-Man style with sharp white teeth & dollar crumbs)
 * - Zero-Overflow Vector Purchasing Power Badge
 * - Rocket Tangent Tracking using Orchestrator Bezier Calculus
 * - Deconflicted Scene 4 Layout with Victory Pose Character
 */

import { renderCharacter } from './agent1_character.js';
import { clamp, lerp, easeOutBack } from './agent5_continuity.js';
import { getQuadraticBezierPointAndTangent } from './orchestrator_engine.js';

export function formatCurrency(num) {
  return '$' + Math.round(num).toLocaleString('en-US');
}

/**
 * SCENE 2: The Mattress Stash (4.75s - 9.70s)
 */
export function renderScene2(t) {
  const p = clamp((t - 4.75) / 4.55, 0, 1);
  const counterVal = formatCurrency(lerp(0, 54000, Math.min(p * 1.3, 1)));
  const yearVal = Math.min(30, Math.max(1, Math.round(lerp(1, 30, p))));
  const mattressLift = lerp(0, -18, Math.sin(p * Math.PI) * 0.9);

  return `
    <rect width="1920" height="1080" fill="#0f172a"/>
    <g opacity="0.06">
      ${Array.from({ length: 20 }).map((_, i) => `<rect x="${i * 100}" y="0" width="50" height="1080" fill="#ffffff"/>`).join('')}
    </g>

    <!-- 30-Year Wall Clock -->
    <g transform="translate(1540, 240)">
      <circle cx="0" cy="0" r="75" fill="#1e293b" stroke="#38bdf8" stroke-width="5"/>
      <circle cx="0" cy="0" r="62" fill="#ffffff"/>
      <line x1="0" y1="0" x2="0" y2="-45" stroke="#0f172a" stroke-width="5" stroke-linecap="round" transform="rotate(${p * 2160})"/>
      <line x1="0" y1="0" x2="0" y2="-32" stroke="#ef4444" stroke-width="4" stroke-linecap="round" transform="rotate(${p * 180})"/>
      <circle cx="0" cy="0" r="6" fill="#0f172a"/>
      <rect x="-80" y="90" width="160" height="42" rx="21" fill="#1e293b" stroke="#38bdf8" stroke-width="3"/>
      <text x="0" y="117" font-family="'Impact', 'Arial Black', sans-serif" font-size="20" font-weight="900" fill="#38bdf8" text-anchor="middle">YEAR ${yearVal} / 30</text>
    </g>

    <!-- Bed & Mattress Rig -->
    <g id="bed_rig" transform="translate(480, 560)">
      <rect x="-320" y="-120" width="640" height="240" rx="14" fill="#78350f" stroke="#451a03" stroke-width="6"/>
      <rect x="-300" y="-100" width="600" height="200" rx="10" fill="#92400e" stroke="#451a03" stroke-width="4"/>
      <rect x="-340" y="100" width="680" height="120" rx="8" fill="#451a03"/>
      <rect x="-330" y="210" width="40" height="120" fill="#291102" rx="4"/>
      <rect x="290" y="210" width="40" height="120" fill="#291102" rx="4"/>

      <!-- Cash Stash -->
      <g transform="translate(0, 80)">
        <rect x="-140" y="-40" width="280" height="60" rx="6" fill="#065f46" stroke="#047857" stroke-width="3"/>
        <rect x="-135" y="-35" width="270" height="50" rx="4" fill="#10b981"/>
        <text x="0" y="-2" font-family="'Impact', 'Arial Black', sans-serif" font-size="22" font-weight="bold" fill="#064e3b" text-anchor="middle">$$$ CASH STASH $$$</text>
      </g>

      <!-- Mattress -->
      <g transform="translate(-310, 80) rotate(${mattressLift}) translate(310, -80)">
        <rect x="-315" y="-30" width="630" height="85" rx="14" fill="#000000" opacity="0.35" transform="translate(4, 8)"/>
        <rect x="-315" y="-30" width="630" height="85" rx="14" fill="#f8fafc" stroke="#0f172a" stroke-width="5"/>
        <line x1="-315" y1="12" x2="315" y2="12" stroke="#cbd5e1" stroke-width="3" stroke-dasharray="16 16"/>
        <path d="M -315 10 L -315 55 L 120 55 L 120 10 Z" fill="#3b82f6" opacity="0.85"/>
      </g>
    </g>

    <!-- Character in Stashing Pose -->
    <g transform="translate(980, 480)">
      ${renderCharacter({
        pose: "STASHING",
        headTilt: 4,
        blink: 0,
        breathScale: 1.0 + Math.sin(t * 4) * 0.015,
        browPosition: 0.6,
        eyeLookX: 2,
        eyeLookY: 1
      })}
    </g>

    <!-- Hero Rolling Odometer Badge -->
    <g transform="translate(960, 160)" filter="url(#badgeGlow)">
      <rect x="-290" y="-55" width="580" height="110" rx="55" fill="#047857" stroke="#10b981" stroke-width="6"/>
      <rect x="-284" y="-49" width="568" height="98" rx="49" fill="url(#badgeGradient)" stroke="#34d399" stroke-width="2.5"/>
      <text x="0" y="-18" font-family="'Inter', sans-serif" font-size="16" font-weight="800" fill="#a7f3d0" text-anchor="middle" letter-spacing="2">MATTRESS SAVINGS (30 YEARS)</text>
      <text x="0" y="32" font-family="'Arial Black', 'Impact', sans-serif" font-size="52" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="2">
        ${counterVal}
      </text>
    </g>
  `;
}

/**
 * Renders the iconic Pac-Man Inflation Monster:
 * A clean red circle with a real moving mouth wedge, sharp interlocking teeth,
 * an angry brow & eye, and "INFLATION" written boldly across its body.
 */
function renderPacmanMonster(mouthAngleDeg) {
  const R = 150;
  const rad = (mouthAngleDeg * Math.PI) / 180;
  const ux = -R * Math.cos(rad);
  const uy = -R * Math.sin(rad);
  const lx = -R * Math.cos(rad);
  const ly = R * Math.sin(rad);

  const bodyPath = `M 0 0 L ${ux.toFixed(1)} ${uy.toFixed(1)} A ${R} ${R} 0 1 1 ${lx.toFixed(1)} ${ly.toFixed(1)} Z`;

  // Interlocking sharp triangular teeth
  const upperTeeth = [0.24, 0.50, 0.76].map(t => {
    const bx0 = ux * (t - 0.08);
    const by0 = uy * (t - 0.08);
    const bx1 = ux * (t + 0.08);
    const by1 = uy * (t + 0.08);
    const tipX = ux * t - Math.sin(rad) * 24;
    const tipY = uy * t + Math.cos(rad) * 24;
    return `<polygon points="${bx0.toFixed(1)},${by0.toFixed(1)} ${tipX.toFixed(1)},${tipY.toFixed(1)} ${bx1.toFixed(1)},${by1.toFixed(1)}" fill="#ffffff" stroke="#3b0707" stroke-width="3"/>`;
  }).join('');

  const lowerTeeth = [0.37, 0.63, 0.89].map(t => {
    const bx0 = lx * (t - 0.08);
    const by0 = ly * (t - 0.08);
    const bx1 = lx * (t + 0.08);
    const by1 = ly * (t + 0.08);
    const tipX = lx * t - Math.sin(rad) * 24;
    const tipY = ly * t - Math.cos(rad) * 24;
    return `<polygon points="${bx0.toFixed(1)},${by0.toFixed(1)} ${tipX.toFixed(1)},${tipY.toFixed(1)} ${bx1.toFixed(1)},${by1.toFixed(1)}" fill="#ffffff" stroke="#3b0707" stroke-width="3"/>`;
  }).join('');

  return `
    <g id="pacman_inflation_monster">
      <!-- Dark Inside Mouth Throat Wedge -->
      <path d="M 0 0 L ${ux.toFixed(1)} ${uy.toFixed(1)} L ${lx.toFixed(1)} ${ly.toFixed(1)} Z" fill="#180c10"/>

      <!-- Main Vibrant Red Circular Body with Moving Mouth Cutout -->
      <path d="${bodyPath}" fill="#ef4444" stroke="#450a0a" stroke-width="7" stroke-linejoin="round" filter="url(#softShadow)"/>

      <!-- Sharp Interlocking Teeth -->
      <g id="teeth">
        ${upperTeeth}
        ${lowerTeeth}
      </g>

      <!-- Angry Characterful Eye -->
      <g id="angry_eye" transform="translate(15, -75)">
        <circle cx="0" cy="0" r="26" fill="#fef08a" stroke="#450a0a" stroke-width="4"/>
        <circle cx="-10" cy="3" r="12" fill="#0f172a"/>
        <circle cx="-6" cy="-1" r="4" fill="#ffffff"/>
        <!-- Slanted Angry Eyebrow -->
        <polygon points="-36,-12 24,-32 28,-22 -32,-2" fill="#450a0a"/>
      </g>

      <!-- Bold "INFLATION" Typography Centered on the Body -->
      <g transform="translate(50, 8)">
        <rect x="-75" y="-22" width="150" height="44" rx="12" fill="#450a0a" stroke="#ffffff" stroke-width="2"/>
        <text x="0" y="9" font-family="'Impact', 'Arial Black', sans-serif" font-size="28" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="2">
          INFLATION
        </text>
      </g>
    </g>
  `;
}

/**
 * SCENE 3: The Inflation Threat & Wrong! Stamp (9.70s - 16.10s)
 */
export function renderScene3(t) {
  const isPostStamp = t >= 12.04;
  const stampProgress = clamp((t - 12.04) / 0.22, 0, 1);
  const stampScale = lerp(3.5, 1.0, easeOutBack(stampProgress));

  // Monster Timeline: enters at 12.80s, strikes and chomps cash at 13.70s
  const isMonsterActive = t >= 12.80;
  const isBitten = t >= 13.70;

  // Lunge position: accelerates in from offscreen right (2100) to cash stack (1070)
  const lungeProgress = clamp((t - 12.80) / 0.90, 0, 1);
  const easedLunge = 1 - Math.pow(1 - lungeProgress, 3);
  const monsterX = lerp(2100, 1070, easedLunge);

  // Authentic Pac-Man Mouth Chomping Motion
  let mouthAngle = 6;
  if (t < 13.70) {
    // Dynamic chomping mouth as it rushes in
    mouthAngle = 22 + 16 * Math.sin((t - 12.80) * 16);
  } else {
    // Steady chewing on the bitten money
    mouthAngle = 8 + 6 * Math.sin((t - 13.70) * 10);
  }

  return `
    <rect width="1920" height="1080" fill="#180c10"/>
    <circle cx="960" cy="540" r="800" fill="#450a0a" opacity="${isPostStamp ? '0.8' : '0.2'}"/>

    <!-- CHARACTER: Uses Rigged PANIC_SHOCK pose with zero arm tangling -->
    <g transform="translate(440, 480)">
      ${renderCharacter({
        pose: isPostStamp ? "PANIC_SHOCK" : "IDLE",
        headTilt: isPostStamp ? -8 : 3,
        blink: 0,
        breathScale: 1.0 + Math.sin(t * 8) * 0.02,
        browPosition: isPostStamp ? -1.0 : 0.4,
        eyeLookX: isPostStamp ? 3 : 0,
        eyeLookY: isPostStamp ? -1 : 0
      })}
    </g>

    <!-- CASH STACK (Full Intact vs Bitten Severed) -->
    <g transform="translate(920, 520)">
      ${!isBitten ? `
        <rect x="-130" y="-75" width="260" height="150" rx="14" fill="#047857" stroke="#064e3b" stroke-width="4" transform="translate(6, 10)"/>
        <rect x="-130" y="-75" width="260" height="150" rx="14" fill="#10b981" stroke="#047857" stroke-width="5"/>
        <rect x="-115" y="-60" width="230" height="120" rx="10" fill="#ecfdf5" stroke="#059669" stroke-width="3"/>
        <circle cx="0" cy="0" r="36" fill="#d1fae5" stroke="#059669" stroke-width="2"/>
        <text x="0" y="12" font-family="'Impact', 'Arial Black', sans-serif" font-size="44" font-weight="900" fill="#065f46" text-anchor="middle">$54,000</text>
      ` : `
        <!-- Severed Left Half with Clean Jagged Bite Mark -->
        <path d="M -130 -75 L 0 -75 C -15 -45 -35 -15 0 0 C -25 25 -10 50 10 75 L -130 75 Z" fill="#10b981" stroke="#047857" stroke-width="5"/>
        <path d="M -115 -60 L -10 -60 C -25 -35 -40 -10 -10 0 C -30 20 -15 40 0 60 L -115 60 Z" fill="#ecfdf5"/>
        <text x="-68" y="6" font-family="'Impact', 'Arial Black', sans-serif" font-size="34" font-weight="900" fill="#065f46" text-anchor="middle">$27K</text>
        <text x="-68" y="28" font-family="'Inter', sans-serif" font-size="16" font-weight="900" fill="#047857" text-anchor="middle">(-50%)</text>
        
        <!-- Flying Dollar Scraps -->
        <g transform="translate(45, -50) rotate(25)"><rect x="-16" y="-10" width="32" height="20" rx="3" fill="#10b981" stroke="#047857" stroke-width="2"/><text x="0" y="4" font-size="10" font-weight="900" fill="#ffffff" text-anchor="middle">$</text></g>
        <g transform="translate(65, 40) rotate(-30)"><rect x="-14" y="-9" width="28" height="18" rx="3" fill="#34d399" stroke="#047857" stroke-width="2"/><text x="0" y="4" font-size="10" font-weight="900" fill="#ffffff" text-anchor="middle">$</text></g>
        <circle cx="30" cy="-60" r="6" fill="#34d399"/>
        <circle cx="55" cy="70" r="5" fill="#10b981"/>
      `}
    </g>

    <!-- AUTHENTIC PAC-MAN INFLATION MONSTER (Moving Mouth Wedge + Teeth + INFLATION) -->
    ${isMonsterActive ? `
      <g transform="translate(${monsterX}, 520)">
        ${renderPacmanMonster(mouthAngle)}
      </g>
    ` : ''}

    <!-- COMIC IMPACT CHOMP! BURST ON BITE -->
    ${(t >= 13.70 && t < 14.20) ? `
      <g transform="translate(970, 520) scale(${lerp(1.15, 0.5, clamp((t - 13.70) / 0.50, 0, 1))})" opacity="${clamp((14.20 - t) / 0.20, 0, 1)}">
        <polygon points="0,-60 18,-18 60,-32 28,0 65,28 20,18 25,60 -8,25 -45,55 -22,12 -60,-8 -16,-16" 
                 fill="#fbbf24" stroke="#dc2626" stroke-width="5"/>
        <polygon points="0,-44 14,-14 44,-24 22,0 48,20 15,14 18,44 -6,18 -34,40 -16,8 -44,-6 -12,-12" 
                 fill="#ffffff" stroke="#f59e0b" stroke-width="2.5"/>
        <text x="0" y="9" font-family="'Impact', 'Arial Black', sans-serif" font-size="26" font-weight="900" fill="#dc2626" text-anchor="middle" letter-spacing="2">CHOMP!</text>
      </g>
    ` : ''}

    <!-- "WRONG!" GIANT RUBBER STAMP -->
    ${isPostStamp ? `
      <g transform="translate(960, 220) rotate(-14) scale(${stampScale})" filter="url(#softShadow)">
        <rect x="-240" y="-60" width="480" height="120" rx="16" fill="#dc2626" stroke="#ffffff" stroke-width="8"/>
        <rect x="-225" y="-45" width="450" height="90" rx="10" fill="none" stroke="#ffffff" stroke-width="4" stroke-dasharray="14 10"/>
        <text x="0" y="24" font-family="'Impact', 'Arial Black', sans-serif" font-size="82" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="6">WRONG!</text>
      </g>
    ` : ''}

    <!-- ZERO-OVERFLOW PURCHASING POWER BADGE (Vector Chevron + Auto-Fitting Bounds) -->
    ${isBitten ? `
      <g id="purchasing_power_badge" transform="translate(960, 830)" filter="url(#softShadow)">
        <!-- Expanded 640px Pill (Zero Overflow) -->
        <rect x="-320" y="-46" width="640" height="92" rx="46" fill="#450a0a" stroke="#dc2626" stroke-width="5"/>
        <!-- Clean SVG Vector Downward Chevron -->
        <g transform="translate(-245, 0)">
          <polygon points="0,14 -14,-8 14,-8" fill="#ef4444" stroke="#ffffff" stroke-width="2"/>
        </g>
        <text x="25" y="10" font-family="'Montserrat', 'Arial Black', sans-serif" font-size="28" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="1">
          PURCHASING POWER: <tspan fill="#fca5a5" font-weight="900">-50%</tspan>
        </text>
      </g>
    ` : ''}
  `;
}

/**
 * SCENE 4: S&P 500 Rocket Engine & $330,000+ Vault (16.10s - 25.07s)
 */
export function renderScene4(t) {
  const p = clamp((t - 16.10) / 8.0, 0, 1);
  const rocketProgress = clamp((t - 16.50) / 7.0, 0, 1);
  const counterVal = formatCurrency(lerp(54000, 330450, Math.pow(p, 1.8)));

  // S&P 500 Quadratic Curve Control Points
  const p0 = { x: 380, y: 800 };
  const p1 = { x: 860, y: 720 };
  const p2 = { x: 1420, y: 220 };

  // Calculate exact position AND mathematical tangent orientation
  const { x: rocketX, y: rocketY, angleDeg: rocketAngle } = getQuadraticBezierPointAndTangent(p0, p1, p2, rocketProgress);

  return `
    <rect width="1920" height="1080" fill="#022c22"/>
    <circle cx="960" cy="540" r="750" fill="#064e3b" opacity="0.4"/>
    
    <g opacity="0.15">
      <path d="M 0 200 L 1920 200 M 0 400 L 1920 400 M 0 600 L 1920 600 M 0 800 L 1920 800" stroke="#34d399" stroke-width="2"/>
      <path d="M 300 0 L 300 1080 M 600 0 L 600 1080 M 900 0 L 900 1080 M 1200 0 L 1200 1080 M 1500 0 L 1500 1080" stroke="#34d399" stroke-width="2"/>
    </g>

    <!-- S&P 500 EXPONENTIAL CURVE -->
    <g id="sp500_curve">
      <path d="M ${p0.x} ${p0.y} Q ${p1.x} ${p1.y} ${p2.x} ${p2.y}" fill="none" stroke="#10b981" stroke-width="12" stroke-linecap="round"/>
      <path d="M ${p0.x} ${p0.y} Q ${p1.x} ${p1.y} ${p2.x} ${p2.y}" fill="none" stroke="#a7f3d0" stroke-width="4" stroke-linecap="round"/>
      <circle cx="${p0.x}" cy="${p0.y}" r="10" fill="#ffffff" stroke="#10b981" stroke-width="4"/>
      <circle cx="860" cy="680" r="10" fill="#ffffff" stroke="#10b981" stroke-width="4"/>
      <circle cx="1180" cy="460" r="12" fill="#facc15" stroke="#10b981" stroke-width="4"/>
      <circle cx="${p2.x}" cy="${p2.y}" r="16" fill="#facc15" stroke="#ffffff" stroke-width="5"/>
    </g>

    <!-- TANGENT-ALIGNED STOCK ROCKET (Precisely follows mathematical curve direction) -->
    <g transform="translate(${rocketX}, ${rocketY}) rotate(${rocketAngle})" filter="url(#badgeGlow)">
      <!-- Flame Thruster -->
      <polygon points="-14,48 0,95 14,48" fill="#f59e0b"/>
      <polygon points="-7,48 0,78 7,48" fill="#fef08a"/>
      <!-- Rocket Hull -->
      <path d="M -24 48 L -24 -20 C -24 -58 0 -85 0 -85 C 0 -85 24 -58 24 -20 L 24 48 Z" fill="#ffffff" stroke="#0f172a" stroke-width="4"/>
      <polygon points="-24,18 -48,52 -24,42" fill="#ef4444" stroke="#0f172a" stroke-width="3"/>
      <polygon points="24,18 48,52 24,42" fill="#ef4444" stroke="#0f172a" stroke-width="3"/>
      <circle cx="0" cy="-14" r="11" fill="#38bdf8" stroke="#0f172a" stroke-width="3"/>
      <text x="0" y="28" font-family="'Impact', sans-serif" font-size="12" font-weight="900" fill="#10b981" text-anchor="middle">S&P</text>
    </g>

    <!-- CHARACTER: Relocated to Left Quadrant in VICTORY_CELEBRATE Pose (Clear Runway) -->
    <g transform="translate(420, 520)">
      ${renderCharacter({
        pose: "VICTORY_CELEBRATE",
        headTilt: -4,
        blink: 0,
        breathScale: 1.0 + Math.sin(t * 6) * 0.02,
        browPosition: 1.0,
        eyeLookX: 2,
        eyeLookY: -2
      })}
    </g>

    <!-- COMPARISON BOXES -->
    <!-- Left: $54K Mattress Box -->
    <g transform="translate(240, 260)">
      <rect x="-110" y="-60" width="220" height="120" rx="12" fill="#1e293b" stroke="#64748b" stroke-width="4"/>
      <text x="0" y="-25" font-family="'Inter', sans-serif" font-size="14" font-weight="700" fill="#94a3b8" text-anchor="middle">MATTRESS (0%)</text>
      <text x="0" y="15" font-family="'Impact', 'Arial Black', sans-serif" font-size="32" font-weight="900" fill="#cbd5e1" text-anchor="middle">$54,000</text>
      <text x="0" y="42" font-family="'Inter', sans-serif" font-size="12" font-weight="bold" fill="#ef4444" text-anchor="middle">Lost to Inflation</text>
    </g>

    <!-- Right: $330,000+ S&P 500 GOLD VAULT -->
    <g transform="translate(1540, 580)" filter="url(#badgeGlow)">
      <rect x="-190" y="-120" width="380" height="240" rx="20" fill="#065f46" stroke="#34d399" stroke-width="6"/>
      <rect x="-175" y="-105" width="350" height="210" rx="14" fill="url(#badgeGradient)"/>
      <text x="0" y="-60" font-family="'Inter', sans-serif" font-size="18" font-weight="900" fill="#a7f3d0" text-anchor="middle" letter-spacing="1">S&P 500 COMPOUND ENGINE</text>
      <text x="0" y="15" font-family="'Arial Black', 'Impact', sans-serif" font-size="52" font-weight="900" fill="#facc15" text-anchor="middle">
        ${counterVal}
      </text>
      <text x="0" y="65" font-family="'Impact', sans-serif" font-size="24" font-weight="bold" fill="#ffffff" text-anchor="middle">
        🚀 +600% PROFIT
      </text>
    </g>
  `;
}

/**
 * SCENE 5: The Climax Call to Action (25.07s - 26.85s)
 */
export function renderScene5(t) {
  const p = clamp((t - 25.07) / 1.5, 0, 1);
  const ctaScale = lerp(0.8, 1.0, easeOutBack(p));
  const pulse = 1.0 + Math.sin(t * 8) * 0.03;

  return `
    <rect width="1920" height="1080" fill="#020617"/>
    <circle cx="960" cy="540" r="850" fill="#0f172a"/>
    <circle cx="960" cy="540" r="500" fill="#1e293b" opacity="0.6"/>

    <g transform="translate(960, 540) rotate(${t * 30})" opacity="0.25">
      ${Array.from({ length: 12 }).map((_, i) => `
        <line x1="0" y1="0" x2="0" y2="600" stroke="#facc15" stroke-width="4" stroke-dasharray="40 60" transform="rotate(${i * 30})"/>
      `).join('')}
    </g>

    <g transform="translate(960, 480) scale(${ctaScale * pulse})" filter="url(#badgeGlow)">
      <g transform="translate(0, -180)">
        <polygon points="0,-60 18,-18 60,0 18,18 0,60 -18,18 -60,0 -18,-18" fill="#facc15" stroke="#78350f" stroke-width="4"/>
      </g>
      <text x="0" y="0" font-family="'Impact', 'Arial Black', sans-serif" font-size="120" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="4">
        START TODAY.
      </text>
      <rect x="-340" y="50" width="680" height="80" rx="40" fill="#10b981" stroke="#34d399" stroke-width="4"/>
      <text x="0" y="105" font-family="'Arial Black', 'Impact', sans-serif" font-size="38" font-weight="900" fill="#022c22" text-anchor="middle" letter-spacing="2">
        $5 A DAY = $330,000+
      </text>
    </g>
  `;
}
