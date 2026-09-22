/**
 * AGENT 1: CHARACTER DESIGNER (REVISION 6 - FORWARD KINEMATICS SKELETAL RIG)
 * 
 * Powered by the canonical Master Character Library (character_library.js).
 * Enforces rigid movement pivots (Neck, Shoulders, Elbows, Wrists, Hips, Knees, Ankles)
 * and strict biomechanical limits:
 * - Elbows only bend inward [0 deg, 140 deg] (Zero backward hyperextension)
 * - Shoulders constrained to [-45 deg, +170 deg] (No 360-degree disjointed spins)
 * - 100% consistent across all scenes and future videos
 */

import { renderMasterCharacter, CANONICAL_POSES, MASTER_CHARACTER_SPEC, verifyPoseBiometrics } from './character_library.js';

export { CANONICAL_POSES, MASTER_CHARACTER_SPEC, verifyPoseBiometrics };

export function renderCharacter(options = {}) {
  return renderMasterCharacter(options);
}
