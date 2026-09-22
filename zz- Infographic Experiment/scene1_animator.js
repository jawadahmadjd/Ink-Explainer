/**
 * AGENT 3: KINETIC ANIMATOR (SCENE 1 ENGINE)
 * Drives Scene 1 visuals and character presentation
 */

import { renderCharacter } from './agent1_character.js';
import { renderSceneEnvironment } from './agent2_scene.js';

function easeOutBack(x) {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
}

function clamp(val, min, max) {
  return Math.min(Math.max(val, min), max);
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

export function computeScene1Frame(currentTime, includeCaptions = false) {
  const t = clamp(currentTime, 0, 4.85);

  // Character Entrance Bounce (0.0s to 0.75s)
  let charY = 0;
  let charScale = 1;
  if (t < 0.75) {
    const p = t / 0.75;
    const eased = easeOutBack(p);
    charY = lerp(160, 0, eased);
    charScale = lerp(0.85, 1, eased);
  }

  // Head Tilt & Wonder
  let headTilt = 0;
  if (t < 1.2) {
    headTilt = lerp(0, -5, t / 1.2);
  } else if (t < 2.8) {
    const p = (t - 1.2) / 1.6;
    headTilt = lerp(-5, 6, p);
  } else {
    const p = (t - 2.8) / 2.05;
    headTilt = lerp(6, -2, p);
  }

  // Eye Blink Cycle (2.30s and 4.05s)
  let blink = 0;
  if ((t >= 2.30 && t <= 2.45) || (t >= 4.05 && t <= 4.20)) {
    blink = 1;
  }

  // Eye Gaze
  let eyeLookX = (t > 1.2 && t < 2.5) ? -2.5 : Math.sin(t * 1.5) * 1.2;
  let eyeLookY = (t > 1.2 && t < 2.5) ? -1 : 0;

  // Hero Badge Pop-in
  let badgeScale = 0;
  let badgeOpacity = 0;
  if (t >= 1.30) {
    const p = clamp((t - 1.30) / 0.45, 0, 1);
    badgeScale = easeOutBack(p);
    badgeOpacity = clamp(p * 2, 0, 1);
  }

  // Question Marks Pop
  let questionScale = 0;
  let questionOpacity = 0;
  if (t >= 0.35 && t < 2.9) {
    const p = clamp((t - 0.35) / 0.4, 0, 1);
    questionScale = easeOutBack(p);
    questionOpacity = (t > 2.4) ? clamp(1 - (t - 2.4) / 0.5, 0, 1) : 1;
  }

  // Calendar Sheets Drift
  let calendarOffset = (t >= 1.8) ? (t - 1.8) / 3.05 : 0;

  // Subtle Idle Breathing
  const breathScale = 1.0 + Math.sin(t * 4.5) * 0.015;

  const sceneEnvironmentSvg = renderSceneEnvironment({
    calendarOffset,
    badgeScale,
    badgeOpacity,
    questionScale,
    questionOpacity,
    gridPulse: 1 + Math.sin(t * 2) * 0.2
  });

  const characterSvg = renderCharacter({
    pose: (t >= 1.05) ? "PRESENT_BILL" : "IDLE",
    headTilt,
    blink,
    breathScale,
    browPosition: clamp(t / 2.0, 0, 1),
    eyeLookX,
    eyeLookY,
    billScale: clamp((t - 1.05) / 0.4, 0, 1)
  });

  return `
    <g id="scene1_container">
      ${sceneEnvironmentSvg}
      <g id="character_wrapper" transform="translate(960, ${465 + charY}) scale(${charScale})">
        ${characterSvg}
      </g>
    </g>
  `;
}
