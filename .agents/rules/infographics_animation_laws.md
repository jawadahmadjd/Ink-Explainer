# 📐 Antigravity Workspace Rule: Infographic Animation Laws & Quality Gates

This rule is automatically enforced across all 2D motion graphics and infographic explainer development in this workspace.

---

## 🛑 Never Repeat These 7 Mistakes (Permanent Invariants)

1. **NEVER Draw Limbs with Freehand Polygons or Arbitrary Beziers:**
   - Always use rigid Forward Kinematics (`character_library.js`).
   - Elbow angle $\theta_e \in [0^\circ, 140^\circ]$. Elbows **MUST ONLY** bend inward/upward. Zero backward hyperextension.
   - Shoulders $\theta_s \in [-45^\circ, +170^\circ]$. No 360° spin.
   - Props (banknotes, tools, coins) must be anchored to wrist joints $(W_x, W_y)$ and sandwiched between palm and fingers. Never allow mid-air floating props.

2. **NEVER Emit Subtitles from Scene Animators:**
   - Only `orchestrator_engine.js:renderChunkedCaptions(t)` may emit captions.
   - Max 3–4 words per chunk.
   - Subtitle & badge pills must have $\ge 40\text{px}$ inner clearance ($W_{\text{pill}} \ge W_{\text{text}} + 40\text{px}$).

3. **NEVER Switch Base Scenes Before 50% Midpoint:**
   - In all transitions, Base Scene $A$ remains active for $p \in [0, 0.50)$.
   - Exactly at $p = 0.50$, the transition element (whip pan, wipe, burst) must achieve 100% full screen mask.
   - Base Scene $B$ activates at $p \ge 0.50$. Never let Scene $B$ appear prematurely.

4. **NEVER Fly Objects Statically Along Curves:**
   - Any object traveling on a curve must compute its tangent angle from the first derivative:
     $\theta(t) = \text{atan2}(y'(t), x'(t)) \times 180 / \pi$.

5. **NEVER Use Semantic Nonsense for Creatures or Props:**
   - A creature that bites must have an authentic SVG angular mouth wedge (`M 0 0 L ux uy A R R 0 1 1 lx ly Z`) with interlocking teeth along the jawline that meet when closed, not floating triangles on a solid sphere.

6. **NEVER Rely Exclusively on HTML5 Audio Clocks:**
   - Always implement dual clocks: primary audio time + fallback `requestAnimationFrame` delta clock (`fallbackTime += dt`) so that play/pause, scrubbing, and frame stepping never freeze or fail.

7. **NEVER Output Bare Pass/Fail in Auditors:**
   - The diagnostic auditor (`diagnostic_auditor.py`) must provide a structured 5W1H diagnosis:
     - **What** went wrong.
     - **Where** it happened (DOM selector / coordinates).
     - **When** it happened (timestamp $t$).
     - **Why** it happened (technical root cause).
     - **How to fix** (step-by-step code solution).

---

## 🚀 Pre-Flight Quality Gate

Before declaring any animation complete:
1. Run `python "zz- Infographic Experiment/diagnostic_auditor.py"` $\rightarrow$ Must score **100/100** with 0 issues.
2. Inspect `character_model_sheet.html` for human verification of skeletal joint limits.
3. Compile standalone `full_player.html` via `build_player.py`.
4. Export broadcast MP4 via `export_to_mp4.py`.
