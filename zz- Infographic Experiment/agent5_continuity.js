/**
 * AGENT 5: CONTINUITY & TRANSITION DIRECTOR (REVISION 3 - 50% MIDPOINT SWITCHING)
 * 
 * Enforces the Golden Motion Graphics Rule:
 * Base scene N switches to scene N+1 at the EXACT MIDPOINT of the transition overlay
 * when the screen is fully masked or covered, ensuring zero visual pops or abrupt cuts.
 */

export function easeInOutCubic(x) {
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
}

export function easeOutBack(x) {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
}

export function clamp(val, min, max) {
  return Math.min(Math.max(val, min), max);
}

export function lerp(a, b, t) {
  return a + (b - a) * t;
}

export function getContinuityState(currentTime) {
  const t = clamp(currentTime, 0, 26.85);

  let activeBaseScene = 1;
  let cameraX = 0;
  let cameraY = 0;
  let cameraScale = 1.0;
  let screenShakeX = 0;
  let screenShakeY = 0;
  let transitionOverlaySvg = '';

  // 1. SCENE 1 (0.00s - 4.40s)
  if (t < 4.40) {
    activeBaseScene = 1;
    cameraScale = lerp(1.0, 1.04, t / 4.40);
  }
  // TRANSITION 1 -> 2 (4.40s - 5.10s, Midpoint: 4.75s)
  else if (t >= 4.40 && t < 5.10) {
    const p = (t - 4.40) / 0.70;
    const eased = easeInOutCubic(p);
    
    // 50% MIDPOINT RULE: Switch base scene at 4.75s (p = 0.5)
    activeBaseScene = (p < 0.5) ? 1 : 2;
    
    // Camera whip pan
    cameraX = lerp(0, -1920, eased);
    if (activeBaseScene === 2) {
      cameraX += 1920; // Re-anchor camera to Scene 2 origin
    }

    const whipOpacity = Math.sin(p * Math.PI) * 0.7;
    transitionOverlaySvg = `
      <g id="whip_speed_lines" opacity="${whipOpacity}">
        <rect x="0" y="0" width="1920" height="1080" fill="#020617" opacity="${whipOpacity * 0.6}"/>
        <line x1="100" y1="220" x2="1820" y2="220" stroke="#38bdf8" stroke-width="6" stroke-dasharray="160 80"/>
        <line x1="200" y1="540" x2="1720" y2="540" stroke="#ffffff" stroke-width="8" stroke-dasharray="240 100"/>
        <line x1="80" y1="820" x2="1840" y2="820" stroke="#38bdf8" stroke-width="6" stroke-dasharray="180 90"/>
      </g>
    `;
  }
  // 2. SCENE 2 (5.10s - 9.30s)
  else if (t >= 5.10 && t < 9.30) {
    activeBaseScene = 2;
    cameraScale = lerp(1.0, 1.05, (t - 5.10) / 4.20);
  }
  // TRANSITION 2 -> 3 (9.30s - 10.10s, Midpoint: 9.70s)
  else if (t >= 9.30 && t < 10.10) {
    const p = (t - 9.30) / 0.80;
    const eased = easeInOutCubic(p);
    
    // 50% MIDPOINT RULE: Switch base scene at 9.70s
    activeBaseScene = (p < 0.5) ? 2 : 3;

    cameraScale = lerp(1.05, 1.35, eased);
    cameraY = lerp(0, 60, eased);
    if (activeBaseScene === 3) {
      cameraScale = lerp(1.35, 1.0, (p - 0.5) * 2);
      cameraY = lerp(60, 0, (p - 0.5) * 2);
    }
  }
  // 3. SCENE 3 (10.10s - 15.70s)
  else if (t >= 10.10 && t < 15.70) {
    activeBaseScene = 3;
    // WRONG! Stamp screen shake at 12.04s - 12.50s
    if (t >= 12.04 && t < 12.50) {
      const shakeProgress = (t - 12.04) / 0.46;
      const decay = 1 - shakeProgress;
      screenShakeX = Math.sin(t * 70) * 20 * decay;
      screenShakeY = Math.cos(t * 80) * 16 * decay;
    }
    cameraScale = 1.0;
  }
  // TRANSITION 3 -> 4 (15.70s - 16.50s, Midpoint: 16.10s)
  else if (t >= 15.70 && t < 16.50) {
    const p = (t - 15.70) / 0.80;
    const eased = easeInOutCubic(p);

    // 50% MIDPOINT RULE: Switch from Scene 3 to Scene 4 at 16.10s (p = 0.5)
    activeBaseScene = (p < 0.5) ? 3 : 4;

    const wipeX = lerp(-800, 2800, eased);
    transitionOverlaySvg = `
      <g id="diagonal_wipe">
        <!-- Giant Solid Emerald Energy Shield -->
        <polygon points="${wipeX - 600},-120 ${wipeX + 600},-120 ${wipeX + 200},1200 ${wipeX - 1000},1200" 
                 fill="#10b981"/>
        <line x1="${wipeX + 600}" y1="-120" x2="${wipeX + 200}" y2="1200" 
              stroke="#34d399" stroke-width="24"/>
        <line x1="${wipeX + 620}" y1="-120" x2="${wipeX + 220}" y2="1200" 
              stroke="#ffffff" stroke-width="8"/>
      </g>
    `;
  }
  // 4. SCENE 4 (16.50s - 24.80s)
  else if (t >= 16.50 && t < 24.80) {
    activeBaseScene = 4;
    cameraScale = lerp(1.0, 1.06, (t - 16.50) / 8.30);
  }
  // TRANSITION 4 -> 5 (24.80s - 25.35s, Midpoint: 25.07s)
  else if (t >= 24.80 && t < 25.35) {
    const p = (t - 24.80) / 0.55;

    // 50% MIDPOINT RULE: Switch from Scene 4 to Scene 5 at 25.07s (p = 0.5)
    activeBaseScene = (p < 0.5) ? 4 : 5;

    const burstScale = lerp(0.1, 4.5, easeOutBack(p));
    const burstOpacity = clamp(Math.sin(p * Math.PI) * 1.4, 0, 1);
    transitionOverlaySvg = `
      <g id="climax_burst" transform="translate(960, 540) scale(${burstScale})" opacity="${burstOpacity}">
        <circle cx="0" cy="0" r="450" fill="#facc15" opacity="0.9"/>
        <circle cx="0" cy="0" r="320" fill="#ffffff"/>
        <polygon points="0,-500 45,-90 500,0 90,45 0,500 -45,90 -500,0 -90,-45" fill="#f59e0b"/>
      </g>
    `;
  }
  // 5. SCENE 5 (25.35s - 26.85s)
  else {
    activeBaseScene = 5;
    cameraScale = lerp(1.0, 1.04, (t - 25.35) / 1.50);
  }

  return {
    t,
    activeBaseScene,
    cameraX,
    cameraY,
    cameraScale,
    screenShakeX,
    screenShakeY,
    transitionOverlaySvg
  };
}
