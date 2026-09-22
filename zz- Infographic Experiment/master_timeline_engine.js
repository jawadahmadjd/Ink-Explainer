/**
 * MASTER TIMELINE ENGINE (REVISION 3 - ORCHESTRATOR COMPLIANT)
 * 
 * Features:
 * - Integrates all 5 scenes under the Orchestrator's spatial zoning protocol
 * - Renders single-layer 18 chunked non-overlapping subtitles (ZERO DUPLICATION)
 * - Applies Agent 5's 50% Midpoint Scene Switching
 */

import { computeScene1Frame } from './scene1_animator.js';
import { renderScene2, renderScene3, renderScene4, renderScene5 } from './scene2_scene5_assets.js';
import { getContinuityState } from './agent5_continuity.js';
import { renderChunkedCaptions, CHUNKED_SUBTITLES } from './orchestrator_engine.js';

export function computeMasterFrame(currentTime) {
  const t = Math.min(Math.max(currentTime, 0), 26.85);
  const continuity = getContinuityState(t);

  let sceneContent = '';

  // 50% Midpoint Scene Selection
  if (continuity.activeBaseScene === 1) {
    sceneContent = computeScene1Frame(t);
  } else if (continuity.activeBaseScene === 2) {
    sceneContent = renderScene2(t);
  } else if (continuity.activeBaseScene === 3) {
    sceneContent = renderScene3(t);
  } else if (continuity.activeBaseScene === 4) {
    sceneContent = renderScene4(t);
  } else {
    sceneContent = renderScene5(t);
  }

  // Single-Source-of-Truth Chunked Captions (from Orchestrator)
  const captionSvg = renderChunkedCaptions(t);

  return `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="100%" height="100%" style="display:block; overflow:hidden;">
      <defs>
        <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#000000" flood-opacity="0.55"/>
        </filter>
        <filter id="badgeGlow" x="-30%" y="-30%" width="160%" height="160%">
          <feDropShadow dx="0" dy="8" stdDeviation="16" flood-color="#10b981" flood-opacity="0.5"/>
        </filter>
        <linearGradient id="badgeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#065f46"/>
          <stop offset="100%" stop-color="#047857"/>
        </linearGradient>
        <linearGradient id="beastSkin" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#ef4444"/>
          <stop offset="40%" stop-color="#dc2626"/>
          <stop offset="80%" stop-color="#991b1b"/>
          <stop offset="100%" stop-color="#450a0a"/>
        </linearGradient>
        <linearGradient id="beastBelly" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#f87171"/>
          <stop offset="100%" stop-color="#b91c1c"/>
        </linearGradient>
        <linearGradient id="eyeGlow" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#fef08a"/>
          <stop offset="60%" stop-color="#f59e0b"/>
          <stop offset="100%" stop-color="#d97706"/>
        </linearGradient>
        <filter id="monsterGlow" x="-30%" y="-30%" width="160%" height="160%">
          <feDropShadow dx="0" dy="8" stdDeviation="16" flood-color="#dc2626" flood-opacity="0.6"/>
        </filter>
      </defs>

      <!-- AGENT 5 CAMERA & CONTINUITY RIG -->
      <g transform="translate(${960 + continuity.screenShakeX}, ${540 + continuity.screenShakeY}) scale(${continuity.cameraScale}) translate(${-960 + continuity.cameraX}, ${-540 + continuity.cameraY})">
        <!-- Scene Base Layer -->
        ${sceneContent}
        <!-- Continuity Transition Overlay (whip lines, diagonal wipe, climax burst) -->
        ${continuity.transitionOverlaySvg}
      </g>

      <!-- FIXED CAPTIONS LAYER (Zone: y = 860 to 1080) -->
      ${captionSvg}
    </svg>
  `;
}
