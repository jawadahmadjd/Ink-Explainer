# 🤖 Autonomous Agent Operating Instructions & Studio Invariants

Welcome to the **Autonomous Ink & Infographics Studio**.

All AI agents working within this workspace must adhere to the formal Standard Operating Procedures (SOPs) located in [**`5- SOPs/`**](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/README.md) and the permanent animation rules in [**`.agents/rules/infographics_animation_laws.md`**](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/.agents/rules/infographics_animation_laws.md).

---

## 🏛️ Two Distinct Production Pipelines

This workspace supports two distinct visual mediums:

### 1. Minimalist Ink Explainers (*MinutePhysics* Style)
- **Documented in:** [`SOP 01`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/01_END_TO_END_PIPELINE_SOP.md) through [`SOP 06`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/06_FINANCE_CREATIVE_INTELLIGENCE_SOP.md)
- **Visuals:** Pure white paper (`#FFFFFF`), black ink outlines (`#000000`), white-filled stick figures.
- **Pacing:** Elastic action steps (~20–65 characters / 1.0s–2.2s) with Never-Orphan grammar shield.
- **Voiceover:** Continuous audio streams (ElevenLabs combined / Qwen 1.7B with <2000-character natural chapter pauses), 300ms silence normalization, Apple XML timeline generation.

### 2. 2D Infographic Motion Graphics (*The Infographics Show* Style)
- **Documented in:** [`SOP 07`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/07_INFOGRAPHIC_VECTOR_ANIMATION_PIPELINE_SOP.md) and [`zz- Infographic Experiment/README.md`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/zz-%20Infographic%20Experiment/README.md)
- **Visuals:** 1920x1080 60fps/30fps vector animation, rich gradients, dynamic lighting, kinetic HUD odometers.
- **Character Mandate:** Rigid Forward Kinematics (FK) only. Elbow flexion $\theta_e \in [0^\circ, 140^\circ]$, zero backward bending, hands physically grip props.
- **Transition Mandate:** 50% Midpoint Screen Mask Handover Law (zero popping).
- **Subtitles:** Orchestrator single-source-of-truth chunking (max 3–4 words, $\ge 40\text{px}$ padding).
- **Auditor Mandate:** 5W1H actionable diagnostics (What, Where, When, Why, Step-by-Step Fix).
- **Export:** Deterministic Playwright parallel frame capture + FFmpeg H.264 broadcast MP4.

---

## 🚫 The 7 Forbidden Mistakes in Vector Animation

1. **NEVER** use bezier curves or freehand polygon approximations for human limbs (FK math only).
2. **NEVER** emit subtitles from scene animators (Orchestrator only).
3. **NEVER** switch base scenes before the 50% midpoint of a transition.
4. **NEVER** fly objects on curves without tangent orientation ($\theta = \text{atan2}(y', x')$).
5. **NEVER** draw semantic nonsense (e.g. Pac-Man mouth must be an authentic moving arc wedge).
6. **NEVER** rely solely on HTML5 audio without a fallback `requestAnimationFrame` delta clock.
7. **NEVER** provide bare pass/fail audit results (must follow the 5W1H format).
