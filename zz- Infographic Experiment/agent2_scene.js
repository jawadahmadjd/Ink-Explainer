/**
 * AGENT 2: SCENE ENVIRONMENT DESIGNER (REVISION 2 - POLISHED COMPOSITION)
 * 
 * Refinements:
 * - Repositioned popping question marks to lateral diagonals (framing character without badge collision)
 * - Enhanced calendar page drop shadows, rich paper curl, and staggered framing
 * - Elevated hero badge with sparkling golden coins and luminous emerald halo
 */

export function renderSceneEnvironment(options = {}) {
  const {
    calendarOffset = 0,     // drift progress (0 to 1)
    badgeScale = 1,          // pop-in scale
    badgeOpacity = 1,        // fade in
    questionScale = 1,       // question mark burst scale
    questionOpacity = 1,     // question mark opacity
    gridPulse = 1            // ambient grid pulse
  } = options;

  // 5 floating calendar pages with smooth staggered drift
  const calendarSheets = [
    { day: "MON", date: "01", baseX: 240, baseY: 340, rot: -14, driftX: calendarOffset * 60, driftY: -calendarOffset * 25 },
    { day: "TUE", date: "02", baseX: 360, baseY: 180, rot: 12, driftX: calendarOffset * 85, driftY: -calendarOffset * 40 },
    { day: "WED", date: "03", baseX: 1540, baseY: 200, rot: -18, driftX: -calendarOffset * 70, driftY: -calendarOffset * 30 },
    { day: "THU", date: "04", baseX: 1680, baseY: 390, rot: 15, driftX: -calendarOffset * 50, driftY: -calendarOffset * 20 },
    { day: "FRI", date: "05", baseX: 1500, baseY: 600, rot: -8, driftX: -calendarOffset * 90, driftY: -calendarOffset * 35 }
  ];

  return `
    <defs>
      <!-- Background Radial Studio Glow -->
      <radialGradient id="bgStudioGlow" cx="50%" cy="45%" r="65%">
        <stop offset="0%" stop-color="#1e293b"/>
        <stop offset="60%" stop-color="#0f172a"/>
        <stop offset="100%" stop-color="#020617"/>
      </radialGradient>

      <!-- Badge Glow & Gradient -->
      <linearGradient id="badgeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#065f46"/>
        <stop offset="100%" stop-color="#047857"/>
      </linearGradient>

      <linearGradient id="coinGold" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#fef08a"/>
        <stop offset="50%" stop-color="#f59e0b"/>
        <stop offset="100%" stop-color="#b45309"/>
      </linearGradient>

      <!-- Eye Clip Paths -->
      <clipPath id="leftEyeClip">
        <ellipse cx="0" cy="0" rx="14" ry="17"/>
      </clipPath>
      <clipPath id="rightEyeClip">
        <ellipse cx="0" cy="0" rx="14" ry="17"/>
      </clipPath>

      <!-- Drop Shadows -->
      <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#000000" flood-opacity="0.55"/>
      </filter>
      <filter id="badgeGlow" x="-30%" y="-30%" width="160%" height="160%">
        <feDropShadow dx="0" dy="8" stdDeviation="16" flood-color="#10b981" flood-opacity="0.5"/>
      </filter>
    </defs>

    <!-- 1. STUDIO BACKGROUND -->
    <rect width="1920" height="1080" fill="url(#bgStudioGlow)"/>

    <!-- Subtle Motion Grid -->
    <g id="ambient_grid" opacity="${0.12 * gridPulse}">
      <path d="M 0 180 L 1920 180 M 0 360 L 1920 360 M 0 540 L 1920 540 M 0 720 L 1920 720 M 0 900 L 1920 900" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="8 12"/>
      <path d="M 320 0 L 320 1080 M 640 0 L 640 1080 M 960 0 L 960 1080 M 1280 0 L 1280 1080 M 1600 0 L 1600 1080" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="8 12"/>
      <circle cx="960" cy="500" r="680" fill="none" stroke="#38bdf8" stroke-width="2" stroke-dasharray="16 24" opacity="0.3"/>
    </g>

    <!-- 2. AMBIENT FLOATING GOLD COINS -->
    <g id="ambient_coins" opacity="0.8">
      <!-- Coin 1 -->
      <g transform="translate(${380 - calendarOffset * 30}, ${640 - calendarOffset * 40}) rotate(${calendarOffset * 45})">
        <ellipse cx="0" cy="0" rx="26" ry="26" fill="url(#coinGold)" stroke="#78350f" stroke-width="3.5" filter="url(#softShadow)"/>
        <ellipse cx="0" cy="0" rx="19" ry="19" fill="none" stroke="#fef08a" stroke-width="2"/>
        <text x="0" y="9" font-family="'Impact', 'Arial Black', sans-serif" font-size="22" font-weight="bold" fill="#78350f" text-anchor="middle">$</text>
      </g>
      <!-- Coin 2 -->
      <g transform="translate(${1620 + calendarOffset * 40}, ${700 - calendarOffset * 30}) rotate(${-calendarOffset * 60})">
        <ellipse cx="0" cy="0" rx="20" ry="20" fill="url(#coinGold)" stroke="#78350f" stroke-width="3" filter="url(#softShadow)"/>
        <ellipse cx="0" cy="0" rx="14" ry="14" fill="none" stroke="#fef08a" stroke-width="1.5"/>
        <text x="0" y="7" font-family="'Impact', 'Arial Black', sans-serif" font-size="16" font-weight="bold" fill="#78350f" text-anchor="middle">$</text>
      </g>
    </g>

    <!-- 3. FLYING CALENDAR PAGES ("every single day") -->
    <g id="calendar_pages">
      ${calendarSheets.map(sheet => `
        <g transform="translate(${sheet.baseX + sheet.driftX}, ${sheet.baseY + sheet.driftY}) rotate(${sheet.rot})" filter="url(#softShadow)">
          <!-- Page Body -->
          <rect x="-46" y="-56" width="92" height="112" rx="8" fill="#ffffff" stroke="#0f172a" stroke-width="4"/>
          <!-- Red Header Bar -->
          <path d="M -46 -48 C -46 -53 -41 -56 -36 -56 L 36 -56 C 41 -56 46 -43 46 -48 L 46 -24 L -46 -24 Z" fill="#ef4444" stroke="#0f172a" stroke-width="3"/>
          <!-- Perforated Holes -->
          <circle cx="-22" cy="-40" r="3.5" fill="#ffffff" stroke="#991b1b" stroke-width="1.5"/>
          <circle cx="22" cy="-40" r="3.5" fill="#ffffff" stroke="#991b1b" stroke-width="1.5"/>
          <!-- Day Name -->
          <text x="0" y="-30" font-family="'Impact', 'Arial Black', sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle" letter-spacing="1">${sheet.day}</text>
          <!-- Big Date Number -->
          <text x="0" y="26" font-family="'Arial Black', 'Impact', sans-serif" font-size="38" font-weight="900" fill="#0f172a" text-anchor="middle">${sheet.date}</text>
          <!-- Page Corner Fold -->
          <polygon points="30,56 46,40 46,56" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
        </g>
      `).join('')}
    </g>

    <!-- 4. POPPING QUESTION MARKS (Positioned to Lateral Flanks) -->
    <g id="question_marks" transform="translate(960, 480) scale(${questionScale})" opacity="${questionOpacity}">
      <!-- Left Electric Yellow Question Mark -->
      <g transform="translate(-290, -110) rotate(-16)">
        <ellipse cx="0" cy="0" rx="38" ry="38" fill="#facc15" stroke="#0f172a" stroke-width="4.5" filter="url(#softShadow)"/>
        <text x="0" y="15" font-family="'Impact', 'Arial Black', sans-serif" font-size="48" font-weight="900" fill="#0f172a" text-anchor="middle">?</text>
        <!-- Burst Sparks -->
        <line x1="-32" y1="-32" x2="-48" y2="-48" stroke="#facc15" stroke-width="4.5" stroke-linecap="round"/>
        <line x1="0" y1="-44" x2="0" y2="-64" stroke="#facc15" stroke-width="4.5" stroke-linecap="round"/>
        <line x1="-44" y1="0" x2="-64" y2="0" stroke="#facc15" stroke-width="4.5" stroke-linecap="round"/>
      </g>

      <!-- Right Vibrant Cyan Question Mark -->
      <g transform="translate(290, -120) rotate(18)">
        <ellipse cx="0" cy="0" rx="34" ry="34" fill="#38bdf8" stroke="#0f172a" stroke-width="4.5" filter="url(#softShadow)"/>
        <text x="0" y="13" font-family="'Impact', 'Arial Black', sans-serif" font-size="42" font-weight="900" fill="#0f172a" text-anchor="middle">?</text>
        <!-- Burst Sparks -->
        <line x1="28" y1="-28" x2="44" y2="-44" stroke="#38bdf8" stroke-width="4.5" stroke-linecap="round"/>
        <line x1="42" y1="0" x2="58" y2="0" stroke="#38bdf8" stroke-width="4.5" stroke-linecap="round"/>
      </g>
    </g>

    <!-- 5. HERO INFOGRAPHIC PILL BADGE: "$5.00 / DAY" -->
    <g id="hero_badge" transform="translate(960, 160) scale(${badgeScale})" opacity="${badgeOpacity}" filter="url(#badgeGlow)">
      <!-- Outer Border Shell -->
      <rect x="-250" y="-56" width="500" height="112" rx="56" fill="#047857" stroke="#10b981" stroke-width="6"/>
      <!-- Inner High-Contrast Fill -->
      <rect x="-244" y="-50" width="488" height="100" rx="50" fill="url(#badgeGradient)" stroke="#34d399" stroke-width="2.5"/>
      
      <!-- Gold Coin Icon -->
      <g transform="translate(-170, 0)">
        <ellipse cx="0" cy="0" rx="38" ry="38" fill="url(#coinGold)" stroke="#78350f" stroke-width="4.5"/>
        <ellipse cx="0" cy="0" rx="30" ry="30" fill="none" stroke="#fef08a" stroke-width="2.5"/>
        <text x="0" y="13" font-family="'Impact', 'Arial Black', sans-serif" font-size="36" font-weight="bold" fill="#78350f" text-anchor="middle">$</text>
      </g>

      <!-- Text: "$5.00 / DAY" -->
      <text x="45" y="15" font-family="'Arial Black', 'Impact', sans-serif" font-size="54" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="2">
        $5.00 <tspan fill="#6ee7b7" font-size="38" font-weight="800">/ DAY</tspan>
      </text>

      <!-- Sparkle Star -->
      <g transform="translate(205, -28)">
        <polygon points="0,-16 5,-5 16,0 5,5 0,16 -5,5 -16,0 -5,-5" fill="#fef08a"/>
      </g>
    </g>
  `;
}
