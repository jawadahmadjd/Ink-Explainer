/**
 * MASTER CHARACTER LIBRARY: THE INFOGRAPHICS SKELETAL RIG (REVISION 3 - TRUE HUMAN MOVEMENT)
 * 
 * 1. 2D Forward Kinematics (FK) Joint Hierarchy:
 *    - Neck: Base (0, 20) -> Head pivot (0, 10), tilt [-18 deg, +18 deg]
 *    - Left Arm:  Shoulder (-52, 36) -> Elbow (L1=65) -> Wrist (L2=55) -> Hand
 *    - Right Arm: Shoulder (+52, 36) -> Elbow (L1=65) -> Wrist (L2=55) -> Hand
 *    - Left Leg:  Hip (-22, 155) -> Knee (L1=60) -> Ankle (L2=55) -> Shoe
 *    - Right Leg: Hip (+22, 155) -> Knee (L1=60) -> Ankle (L2=55) -> Shoe
 * 
 * 2. True Human Biomechanical Laws:
 *    - Upper arm swings outward/upward:
 *      * Left:  alpha_s = 90 deg + theta_s
 *      * Right: alpha_s = 90 deg - theta_s
 *    - Elbow flexes UPWARD and TOWARD BODY (flexion):
 *      * Left:  alpha_f = alpha_s + theta_e  (Forearm bends UP-IN toward head/chest)
 *      * Right: alpha_f = alpha_s - theta_e  (Forearm bends UP-IN toward head/chest)
 *    - Elbow Flexion Range: theta_e in [0 deg, 140 deg] (Zero backward bending)
 *    - Shoulder Range: theta_s in [-20 deg, 155 deg] (Zero 360-degree spin)
 * 
 * 3. Airtight Prop Attachment:
 *    - Banknote is clamped directly inside the hand's fingers at (Wx, Wy)
 *    - Hand palm behind bill -> Bill -> Thumb & curled fingers in front of bill (Zero mid-air floating)
 */

export const MASTER_CHARACTER_SPEC = {
  version: "3.0.0-human-kinematics",
  name: "Infographics Host (The $5 Investor)",
  proportions: {
    height: 380,
    headWidth: 120,
    headHeight: 140,
    torsoWidth: 116,
    torsoHeight: 135,
    armUpperLength: 65,
    armForeLength: 55,
    legThighLength: 60,
    legShinLength: 55
  },
  palette: {
    skin: "#fcd5b4",
    skinShadow: "#f0b992",
    blush: "#fb7185",
    hoodieMain: "#2563eb",
    hoodieShadow: "#1d4ed8",
    hoodieDrawstring: "#f8fafc",
    hair: "#1e1e1e",
    mouthDark: "#881337",
    pants: "#1e293b",
    pantsOutline: "#0f172a",
    shoes: "#f8fafc",
    shoesStripe: "#ef4444",
    billMain: "#10b981",
    billLight: "#ecfdf5",
    billDark: "#065f46"
  },
  jointPivots: {
    neck: { x: 0, y: 10 },
    leftShoulder: { x: -52, y: 36 },
    rightShoulder: { x: 52, y: 36 },
    leftHip: { x: -22, y: 155 },
    rightHip: { x: 22, y: 155 }
  }
};

export function clampBiometrics(val, min, max) {
  return Math.min(Math.max(val, min), max);
}

/**
 * Forward Kinematics Arm Solver (True Human Biomechanics)
 * @param {'left' | 'right'} side
 * @param {number} shoulderAngle - degrees from resting down [0 = straight down, 30 = down-out, 90 = horizontal, 140 = high up]
 * @param {number} elbowFlexion  - degrees of inward bend [0 = straight, 90 = right-angle bend UPWARD, 130 = hand near chest/face]
 */
export function solveArmKinematics(side, shoulderAngle, elbowFlexion) {
  const S = (side === 'left') 
    ? { x: MASTER_CHARACTER_SPEC.jointPivots.leftShoulder.x, y: MASTER_CHARACTER_SPEC.jointPivots.leftShoulder.y }
    : { x: MASTER_CHARACTER_SPEC.jointPivots.rightShoulder.x, y: MASTER_CHARACTER_SPEC.jointPivots.rightShoulder.y };

  // Biomechanical safety constraints
  const sClamped = clampBiometrics(shoulderAngle, -20, 155);
  const eClamped = clampBiometrics(elbowFlexion, 0, 140); // Elbow cannot bend backward!

  const L1 = MASTER_CHARACTER_SPEC.proportions.armUpperLength;
  const L2 = MASTER_CHARACTER_SPEC.proportions.armForeLength;

  let alphaS, alphaF;
  if (side === 'left') {
    // Upper arm swings outward to the left (90 deg is straight down, 90 + s swings to left and up)
    alphaS = (90 + sClamped) * (Math.PI / 180);
    // Flexion bends UPWARD and TOWARDS the head/chest (increasing angle toward -Y)
    alphaF = (90 + sClamped + eClamped) * (Math.PI / 180);
  } else {
    // Upper arm swings outward to the right (90 deg is straight down, 90 - s swings to right and up)
    alphaS = (90 - sClamped) * (Math.PI / 180);
    // Flexion bends UPWARD and TOWARDS the head/chest (decreasing angle toward -Y)
    alphaF = (90 - sClamped - eClamped) * (Math.PI / 180);
  }

  const Ex = S.x + L1 * Math.cos(alphaS);
  const Ey = S.y + L1 * Math.sin(alphaS);

  const Wx = Ex + L2 * Math.cos(alphaF);
  const Wy = Ey + L2 * Math.sin(alphaF);

  // Angle of the forearm in degrees
  const forearmDeg = alphaF * (180 / Math.PI);

  return {
    shoulder: S,
    elbow: { x: Ex, y: Ey },
    wrist: { x: Wx, y: Wy },
    forearmAngle: forearmDeg,
    shoulderAngleClamped: sClamped,
    elbowFlexionClamped: eClamped
  };
}

/**
 * Forward Kinematics Leg Solver
 */
export function solveLegKinematics(side, hipAngle = 0, kneeFlexion = 0) {
  const H = (side === 'left')
    ? { x: MASTER_CHARACTER_SPEC.jointPivots.leftHip.x, y: MASTER_CHARACTER_SPEC.jointPivots.leftHip.y }
    : { x: MASTER_CHARACTER_SPEC.jointPivots.rightHip.x, y: MASTER_CHARACTER_SPEC.jointPivots.rightHip.y };

  const hClamped = clampBiometrics(hipAngle, -25, 35);
  const kClamped = clampBiometrics(kneeFlexion, 0, 110);

  const Lthigh = MASTER_CHARACTER_SPEC.proportions.legThighLength;
  const Lshin = MASTER_CHARACTER_SPEC.proportions.legShinLength;

  const alphaH = (90 + hClamped) * (Math.PI / 180);
  const Kx = H.x + Lthigh * Math.cos(alphaH);
  const Ky = H.y + Lthigh * Math.sin(alphaH);

  // Knee backward flexion
  const alphaK = (90 + hClamped - kClamped) * (Math.PI / 180);
  const Ax = Kx + Lshin * Math.cos(alphaK);
  const Ay = Ky + Lshin * Math.sin(alphaK);

  return {
    hip: H,
    knee: { x: Kx, y: Ky },
    ankle: { x: Ax, y: Ay }
  };
}

/**
 * 5 Canonical Verified Human Poses (Natural Biomechanical Movements)
 */
export const CANONICAL_POSES = {
  POSE_IDLE: {
    name: "Idle Rest",
    description: "Relaxed standing pose with arms hanging comfortably beside torso",
    leftArm: { shoulderAngle: 12, elbowFlexion: 12 },
    rightArm: { shoulderAngle: 12, elbowFlexion: 12 },
    headTilt: 0,
    mouth: "smile",
    billScale: 0
  },
  POSE_PRESENT_BILL: {
    name: "Present $5 Bill",
    description: "Elbow bent naturally; forearm raised UPWARD holding $5 banknote at chest level",
    leftArm: { shoulderAngle: 28, elbowFlexion: 92 },
    rightArm: { shoulderAngle: 15, elbowFlexion: 20 },
    headTilt: 4,
    mouth: "inquisitive",
    billScale: 1.0
  },
  POSE_STASHING: {
    name: "Stashing Under Mattress",
    description: "Both arms angled forward-down into mattress stash; focused downward gaze",
    leftArm: { shoulderAngle: 40, elbowFlexion: 35 },
    rightArm: { shoulderAngle: 12, elbowFlexion: 15 },
    headTilt: 6,
    mouth: "smile",
    billScale: 0.85
  },
  POSE_PANIC_SHOCK: {
    name: "Inflation Panic & Shock",
    description: "Both hands raised UP beside cheeks/ears in alarm; wide terrified eyes & agape mouth",
    leftArm: { shoulderAngle: 70, elbowFlexion: 80 },
    rightArm: { shoulderAngle: 70, elbowFlexion: 80 },
    headTilt: -8,
    mouth: "open_gasp",
    billScale: 0
  },
  POSE_VICTORY: {
    name: "S&P 500 Victory Celebration",
    description: "Both arms raised high in triumphant V-shape celebration into the sky",
    leftArm: { shoulderAngle: 140, elbowFlexion: 15 },
    rightArm: { shoulderAngle: 140, elbowFlexion: 15 },
    headTilt: -4,
    mouth: "victory_grin",
    billScale: 0
  }
};

export function verifyPoseBiometrics(poseParams) {
  const diagnostics = [];
  let isValid = true;

  if (poseParams.leftArm.elbowFlexion < 0) {
    isValid = false;
    diagnostics.push(`Left elbow hyperextended backwards (${poseParams.leftArm.elbowFlexion} deg). Must be >= 0 deg.`);
  }
  if (poseParams.rightArm.elbowFlexion < 0) {
    isValid = false;
    diagnostics.push(`Right elbow hyperextended backwards (${poseParams.rightArm.elbowFlexion} deg). Must be >= 0 deg.`);
  }
  if (poseParams.leftArm.shoulderAngle > 165 || poseParams.leftArm.shoulderAngle < -30) {
    isValid = false;
    diagnostics.push(`Left shoulder out of human range (${poseParams.leftArm.shoulderAngle} deg).`);
  }
  if (poseParams.rightArm.shoulderAngle > 165 || poseParams.rightArm.shoulderAngle < -30) {
    isValid = false;
    diagnostics.push(`Right shoulder out of human range (${poseParams.rightArm.shoulderAngle} deg).`);
  }

  return {
    valid: isValid,
    score: isValid ? 100 : 0,
    diagnostics: diagnostics.length ? diagnostics : ["All joints within strict anatomical bounds (Zero backward bends, zero 360-degree spins)."]
  };
}

/**
 * Render FK Limb with sleeve, cuff, and tight prop grip
 */
function renderRiggedArm(side, kinematics, opts = {}) {
  const { shoulder, elbow, wrist, forearmAngle } = kinematics;
  const { showBill = false, billScale = 1.0, isSkeleton = false } = opts;
  const p = MASTER_CHARACTER_SPEC.palette;

  const sx = shoulder.x, sy = shoulder.y;
  const ex = elbow.x, ey = elbow.y;
  const wx = wrist.x, wy = wrist.y;

  // Sleeve cuff perpendicular to forearm
  const cuffRot = forearmAngle + 90;

  return `
    <g id="${side}_arm_rig">
      <!-- Outer Dark Stroke Limb Underlayer -->
      <path d="M ${sx} ${sy} L ${ex} ${ey} L ${wx} ${wy}" 
            fill="none" stroke="#0f172a" stroke-width="34" stroke-linecap="round" stroke-linejoin="round"/>
      
      <!-- Blue Hoodie Sleeve Fill Layer -->
      <path d="M ${sx} ${sy} L ${ex} ${ey} L ${wx} ${wy}" 
            fill="none" stroke="${p.hoodieMain}" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/>
      
      <!-- Elbow Joint Crease Accent -->
      <circle cx="${ex}" cy="${ey}" r="5" fill="${p.hoodieShadow}" opacity="0.6"/>

      <!-- Sleeve Cuff at Wrist -->
      <ellipse cx="${wx}" cy="${wy}" rx="9" ry="14" fill="${p.hoodieShadow}" stroke="#0f172a" stroke-width="3.5" 
               transform="rotate(${cuffRot} ${wx} ${wy})"/>

      <!-- Hand Palm (behind bill) -->
      <g transform="translate(${wx}, ${wy})">
        <circle cx="0" cy="0" r="14" fill="${p.skin}" stroke="#0f172a" stroke-width="3.5"/>
      </g>

      <!-- $5 Banknote (Physically held in hand grip) -->
      ${showBill ? `
        <g id="five_dollar_bill" transform="translate(${wx - 10}, ${wy - 26}) rotate(-10) scale(${billScale})">
          <rect x="-70" y="-40" width="140" height="80" rx="8" fill="#000000" opacity="0.4" transform="translate(5, 6)"/>
          <rect x="-70" y="-40" width="140" height="80" rx="8" fill="${p.billMain}" stroke="#064e3b" stroke-width="3.5"/>
          <rect x="-64" y="-34" width="128" height="68" rx="6" fill="${p.billLight}" stroke="#059669" stroke-width="2"/>
          
          <!-- Corner 5s -->
          <rect x="-60" y="-30" width="15" height="15" rx="2" fill="#d1fae5" stroke="#10b981" stroke-width="1"/>
          <text x="-52" y="-19" font-family="'Impact', 'Arial Black', sans-serif" font-size="12" font-weight="900" fill="#065f46" text-anchor="middle">5</text>
          <rect x="45" y="-30" width="15" height="15" rx="2" fill="#d1fae5" stroke="#10b981" stroke-width="1"/>
          <text x="53" y="-19" font-family="'Impact', 'Arial Black', sans-serif" font-size="12" font-weight="900" fill="#065f46" text-anchor="middle">5</text>
          <rect x="-60" y="15" width="15" height="15" rx="2" fill="#d1fae5" stroke="#10b981" stroke-width="1"/>
          <text x="-52" y="26" font-family="'Impact', 'Arial Black', sans-serif" font-size="12" font-weight="900" fill="#065f46" text-anchor="middle">5</text>
          <rect x="45" y="15" width="15" height="15" rx="2" fill="#d1fae5" stroke="#10b981" stroke-width="1"/>
          <text x="53" y="26" font-family="'Impact', 'Arial Black', sans-serif" font-size="12" font-weight="900" fill="#065f46" text-anchor="middle">5</text>

          <!-- Lincoln Oval -->
          <ellipse cx="0" cy="0" rx="22" ry="27" fill="#d1fae5" stroke="#047857" stroke-width="2"/>
          <path d="M -9 16 C -9 5 -5 -2 0 -3 C 5 -2 9 5 9 16 Z" fill="#065f46"/>
          <circle cx="0" cy="-7" r="8" fill="#065f46"/>

          <rect x="-38" y="-29" width="76" height="8" rx="2" fill="#047857"/>
          <text x="0" y="-23" font-family="'Arial Black', sans-serif" font-size="5.5" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="1">UNITED STATES OF AMERICA</text>
          <rect x="-30" y="21" width="60" height="7" rx="2" fill="#047857"/>
          <text x="0" y="26" font-family="'Impact', 'Arial Black', sans-serif" font-size="6.5" font-weight="bold" fill="#ffffff" text-anchor="middle" letter-spacing="1">FIVE DOLLARS</text>
        </g>
      ` : ''}

      <!-- Front Hand Grip: Thumb and Curled Fingers clamping onto the bill -->
      <g transform="translate(${wx}, ${wy})">
        <!-- Thumb clamping front -->
        <path d="M 6 -8 C 12 -4 8 8 2 6" fill="${p.skin}" stroke="#0f172a" stroke-width="3.5"/>
        <!-- Curled front fingers -->
        <path d="M -8 4 C -12 12 -4 18 2 12" fill="${p.skin}" stroke="#0f172a" stroke-width="3"/>
        <path d="M -6 -2 C -12 6 -4 14 4 8" fill="${p.skin}" stroke="#0f172a" stroke-width="3"/>
      </g>

      <!-- Optional Skeleton Diagnostic Overlay -->
      ${isSkeleton ? `
        <g id="${side}_arm_bones" stroke="#10b981" stroke-width="3" stroke-dasharray="4 2">
          <line x1="${sx}" y1="${sy}" x2="${ex}" y2="${ey}"/>
          <line x1="${ex}" y1="${ey}" x2="${wx}" y2="${wy}"/>
          <circle cx="${sx}" cy="${sy}" r="7" fill="#10b981" stroke="#ffffff" stroke-width="2"/>
          <circle cx="${ex}" cy="${ey}" r="7" fill="#10b981" stroke="#ffffff" stroke-width="2"/>
          <circle cx="${wx}" cy="${wy}" r="7" fill="#10b981" stroke="#ffffff" stroke-width="2"/>
        </g>
      ` : ''}
    </g>
  `;
}

/**
 * Render Legs
 */
function renderRiggedLegs(leftLeg, rightLeg, isSkeleton = false) {
  const p = MASTER_CHARACTER_SPEC.palette;
  const lk = leftLeg.knee, la = leftLeg.ankle, lh = leftLeg.hip;
  const rk = rightLeg.knee, ra = rightLeg.ankle, rh = rightLeg.hip;

  return `
    <g id="legs_rig">
      <!-- Left Leg (Pants) -->
      <path d="M ${lh.x} ${lh.y} L ${lk.x} ${lk.y} L ${la.x} ${la.y}" 
            fill="none" stroke="#0f172a" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M ${lh.x} ${lh.y} L ${lk.x} ${lk.y} L ${la.x} ${la.y}" 
            fill="none" stroke="${p.pants}" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>
      
      <!-- Left Shoe -->
      <g transform="translate(${la.x}, ${la.y})">
        <path d="M -20 -10 L 16 -10 C 28 -10 28 10 16 10 L -24 10 C -32 10 -32 -10 -20 -10 Z" 
              fill="${p.shoes}" stroke="#0f172a" stroke-width="4" stroke-linejoin="round"/>
        <line x1="-26" y1="3" x2="22" y2="3" stroke="${p.shoesStripe}" stroke-width="3" stroke-linecap="round"/>
      </g>

      <!-- Right Leg (Pants) -->
      <path d="M ${rh.x} ${rh.y} L ${rk.x} ${rk.y} L ${ra.x} ${ra.y}" 
            fill="none" stroke="#0f172a" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M ${rh.x} ${rh.y} L ${rk.x} ${rk.y} L ${ra.x} ${ra.y}" 
            fill="none" stroke="${p.pants}" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>

      <!-- Right Shoe -->
      <g transform="translate(${ra.x}, ${ra.y})">
        <path d="M -16 -10 L 20 -10 C 32 -10 32 10 20 10 L -20 10 C -28 10 -28 -10 -16 -10 Z" 
              fill="${p.shoes}" stroke="#0f172a" stroke-width="4" stroke-linejoin="round"/>
        <line x1="-22" y1="3" x2="26" y2="3" stroke="${p.shoesStripe}" stroke-width="3" stroke-linecap="round"/>
      </g>

      <!-- Optional Skeleton Diagnostic Overlay -->
      ${isSkeleton ? `
        <g id="leg_bones" stroke="#10b981" stroke-width="3" stroke-dasharray="4 2">
          <line x1="${lh.x}" y1="${lh.y}" x2="${lk.x}" y2="${lk.y}"/>
          <line x1="${lk.x}" y1="${lk.y}" x2="${la.x}" y2="${la.y}"/>
          <line x1="${rh.x}" y1="${rh.y}" x2="${rk.x}" y2="${rk.y}"/>
          <line x1="${rk.x}" y1="${rk.y}" x2="${ra.x}" y2="${ra.y}"/>
          <circle cx="${lh.x}" cy="${lh.y}" r="6" fill="#10b981" stroke="#ffffff" stroke-width="2"/>
          <circle cx="${lk.x}" cy="${lk.y}" r="6" fill="#10b981" stroke="#ffffff" stroke-width="2"/>
          <circle cx="${la.x}" cy="${la.y}" r="6" fill="#10b981" stroke="#ffffff" stroke-width="2"/>
          <circle cx="${rh.x}" cy="${rh.y}" r="6" fill="#10b981" stroke="#ffffff" stroke-width="2"/>
          <circle cx="${rk.x}" cy="${rk.y}" r="6" fill="#10b981" stroke="#ffffff" stroke-width="2"/>
          <circle cx="${ra.x}" cy="${ra.y}" r="6" fill="#10b981" stroke="#ffffff" stroke-width="2"/>
        </g>
      ` : ''}
    </g>
  `;
}

/**
 * MASTER CHARACTER RENDERER
 */
export function renderMasterCharacter(options = {}) {
  const {
    pose = "POSE_IDLE",
    headTilt = null,
    blink = 0,
    breathScale = 1.0,
    browPosition = 0,
    eyeLookX = 0,
    eyeLookY = 0,
    billScale = null,
    showSkeleton = false,
    customJoints = null
  } = options;

  let preset = CANONICAL_POSES[pose] || CANONICAL_POSES.POSE_IDLE;
  if (pose === "IDLE") preset = CANONICAL_POSES.POSE_IDLE;
  if (pose === "PRESENT_BILL") preset = CANONICAL_POSES.POSE_PRESENT_BILL;
  if (pose === "STASHING") preset = CANONICAL_POSES.POSE_STASHING;
  if (pose === "PANIC_SHOCK") preset = CANONICAL_POSES.POSE_PANIC_SHOCK;
  if (pose === "VICTORY" || pose === "VICTORY_CELEBRATE") preset = CANONICAL_POSES.POSE_VICTORY;

  const leftShoulderAngle = (customJoints?.leftArm?.shoulderAngle !== undefined) ? customJoints.leftArm.shoulderAngle : preset.leftArm.shoulderAngle;
  const leftElbowFlexion = (customJoints?.leftArm?.elbowFlexion !== undefined) ? customJoints.leftArm.elbowFlexion : preset.leftArm.elbowFlexion;

  const rightShoulderAngle = (customJoints?.rightArm?.shoulderAngle !== undefined) ? customJoints.rightArm.shoulderAngle : preset.rightArm.shoulderAngle;
  const rightElbowFlexion = (customJoints?.rightArm?.elbowFlexion !== undefined) ? customJoints.rightArm.elbowFlexion : preset.rightArm.elbowFlexion;

  const actualHeadTilt = (headTilt !== null) ? headTilt : preset.headTilt;
  const actualBillScale = (billScale !== null) ? billScale : preset.billScale;

  const leftArmKine = solveArmKinematics('left', leftShoulderAngle, leftElbowFlexion);
  const rightArmKine = solveArmKinematics('right', rightShoulderAngle, rightElbowFlexion);

  const leftLegKine = solveLegKinematics('left', 0, 0);
  const rightLegKine = solveLegKinematics('right', 0, 0);

  const p = MASTER_CHARACTER_SPEC.palette;

  let mouthSvg = `
    <path d="M -12 -4 C -8 8 8 8 12 -4 C 6 4 -6 4 -12 -4 Z" 
          fill="${p.mouthDark}" stroke="#0f172a" stroke-width="3.5" stroke-linejoin="round"/>
    <path d="M -7 -2 C -3 2 3 2 7 -2" fill="#ffffff" stroke="none"/>
  `;

  if (preset.mouth === "open_gasp" || pose === "PANIC_SHOCK") {
    mouthSvg = `
      <ellipse cx="0" cy="-2" rx="14" ry="18" fill="${p.mouthDark}" stroke="#0f172a" stroke-width="3.5"/>
      <ellipse cx="0" cy="8" rx="8" ry="4" fill="${p.blush}"/>
    `;
  } else if (preset.mouth === "victory_grin" || pose === "VICTORY" || pose === "VICTORY_CELEBRATE") {
    mouthSvg = `
      <path d="M -16 -6 C -12 12 12 12 16 -6 Z" fill="${p.mouthDark}" stroke="#0f172a" stroke-width="3.5"/>
      <path d="M -12 -5 C -6 0 6 0 12 -5 Z" fill="#ffffff"/>
    `;
  }

  return `
    <g id="master_character_root" transform="scale(${breathScale * 1.35})">
      <!-- 1. LEGS -->
      ${renderRiggedLegs(leftLegKine, rightLegKine, showSkeleton)}

      <!-- 2. TORSO / HOODIE -->
      <g id="torso">
        <path d="M -58 25 C -60 25 -66 105 -50 160 L 50 160 C 66 105 60 25 58 25 C 38 16 -38 16 -58 25 Z" 
              fill="${p.hoodieMain}" stroke="#0f172a" stroke-width="4.5" stroke-linejoin="round"/>
        <path d="M 18 22 C 38 55 46 120 50 160 L 22 160 C 18 115 12 65 -6 22 Z" fill="${p.hoodieShadow}" opacity="0.45"/>
        <path d="M -34 98 L 34 98 L 42 146 L -42 146 Z" fill="${p.hoodieShadow}" stroke="#0f172a" stroke-width="3.5" stroke-linejoin="round"/>
        <path d="M -22 20 C -12 40 12 40 22 20" fill="none" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>
        <line x1="-10" y1="30" x2="-10" y2="64" stroke="${p.hoodieDrawstring}" stroke-width="3.5" stroke-linecap="round"/>
        <circle cx="-10" cy="67" r="3" fill="${p.hoodieDrawstring}"/>
        <line x1="10" y1="30" x2="10" y2="68" stroke="${p.hoodieDrawstring}" stroke-width="3.5" stroke-linecap="round"/>
        <circle cx="10" cy="71" r="3" fill="${p.hoodieDrawstring}"/>
      </g>

      <!-- 3. RIGHT ARM -->
      ${renderRiggedArm('right', rightArmKine, { showBill: false, isSkeleton: showSkeleton })}

      <!-- 4. HEAD & FACE -->
      <g id="head_group" transform="translate(0, 8) rotate(${actualHeadTilt})">
        <rect x="-18" y="-20" width="36" height="38" fill="${p.skinShadow}" stroke="#0f172a" stroke-width="4" rx="4"/>
        <path d="M -60 -75 C -60 -155 60 -155 60 -75 C 60 -5 44 20 0 24 C -44 20 -60 -5 -60 -75 Z" 
              fill="${p.skin}" stroke="#0f172a" stroke-width="4.5" stroke-linejoin="round"/>
        
        <ellipse cx="-42" cy="-45" rx="10" ry="6" fill="${p.blush}" opacity="0.4"/>
        <ellipse cx="42" cy="-45" rx="10" ry="6" fill="${p.blush}" opacity="0.4"/>
        <path d="M -60 -70 C -70 -70 -70 -48 -58 -46" fill="${p.skin}" stroke="#0f172a" stroke-width="4"/>
        <path d="M 60 -70 C 70 -70 70 -48 58 -46" fill="${p.skin}" stroke="#0f172a" stroke-width="4"/>

        <!-- Hair -->
        <path d="M -62 -85 C -66 -148 -14 -175 25 -170 C 58 -165 72 -135 66 -95 C 60 -86 52 -100 36 -104 C 20 -108 10 -98 -8 -102 C -28 -106 -45 -82 -62 -85 Z" 
              fill="${p.hair}" stroke="#0f172a" stroke-width="4.5" stroke-linejoin="round"/>
        <path d="M -60 -88 L -58 -62 L -50 -68 Z" fill="${p.hair}"/>
        <path d="M 60 -88 L 58 -62 L 50 -68 Z" fill="${p.hair}"/>

        <!-- Eyebrows -->
        <g id="eyebrows" transform="translate(0, ${-browPosition * 8})">
          <path d="M -42 -94 C -32 -108 -18 -104 -10 -96" fill="none" stroke="${p.hair}" stroke-width="5.5" stroke-linecap="round"/>
          <path d="M 10 -98 C 22 -112 38 -108 44 -94" fill="none" stroke="${p.hair}" stroke-width="5.5" stroke-linecap="round"/>
        </g>

        <!-- Eyes -->
        <g id="eyes">
          ${blink === 1 ? `
            <path d="M -40 -68 C -32 -58 -20 -58 -12 -68" fill="none" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round"/>
            <path d="M 12 -68 C 20 -58 32 -58 40 -68" fill="none" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round"/>
          ` : `
            <g transform="translate(-26, -72)">
              <ellipse cx="0" cy="0" rx="14" ry="17" fill="#ffffff" stroke="#0f172a" stroke-width="3.5"/>
              <circle cx="${eyeLookX}" cy="${eyeLookY}" r="7.5" fill="#0f172a"/>
              <circle cx="${eyeLookX + 3}" cy="${eyeLookY - 3}" r="3" fill="#ffffff"/>
              <circle cx="${eyeLookX - 2.5}" cy="${eyeLookY + 2.5}" r="1.5" fill="#ffffff"/>
            </g>
            <g transform="translate(26, -72)">
              <ellipse cx="0" cy="0" rx="14" ry="17" fill="#ffffff" stroke="#0f172a" stroke-width="3.5"/>
              <circle cx="${eyeLookX}" cy="${eyeLookY}" r="7.5" fill="#0f172a"/>
              <circle cx="${eyeLookX + 3}" cy="${eyeLookY - 3}" r="3" fill="#ffffff"/>
              <circle cx="${eyeLookX - 2.5}" cy="${eyeLookY + 2.5}" r="1.5" fill="#ffffff"/>
            </g>
          `}
        </g>

        <!-- Nose -->
        <path d="M -2 -58 C 4 -56 5 -48 -2 -44" fill="none" stroke="${p.skinShadow}" stroke-width="4.5" stroke-linecap="round"/>

        <!-- Mouth -->
        <g id="mouth" transform="translate(0, -28)">
          ${mouthSvg}
        </g>
      </g>

      <!-- 5. LEFT ARM (Holds $5 Banknote firmly) -->
      ${renderRiggedArm('left', leftArmKine, { 
        showBill: actualBillScale > 0, 
        billScale: actualBillScale, 
        isSkeleton: showSkeleton 
      })}

      <!-- 6. NECK SKELETON PIVOT -->
      ${showSkeleton ? `
        <circle cx="0" cy="10" r="8" fill="#10b981" stroke="#ffffff" stroke-width="2.5"/>
        <text x="0" y="-12" font-family="'Inter', sans-serif" font-size="11" font-weight="900" fill="#10b981" text-anchor="middle">NECK PIVOT</text>
      ` : ''}
    </g>
  `;
}
