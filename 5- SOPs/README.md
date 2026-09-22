# 📚 Standard Operating Procedures (SOPs) — Autonomous Studio Library

Welcome to the central operations repository for **Ink Explainers**, an autonomous multi-niche animation studio powered by Google Antigravity, Google Flow CDP automation, ElevenLabs voiceover mastering, and Apple NLE timeline synthesis.

This library provides production-grade operational manuals for every phase of content creation, from competitor forensic ingestion to multi-channel YouTube distribution.

---

## 🗂️ SOP Master Navigation

| Document | Scope & Focus | Primary Technologies | Key Operational Targets |
| :--- | :--- | :--- | :--- |
| [**01. End-to-End Pipeline SOP**](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/01_END_TO_END_PIPELINE_SOP.md) | Complete 7-stage production lifecycle from URL ingestion to final NLE sequence | `pipeline_orchestrator.py`, `config.py`, Web UI | Zero manual intervention, automated error recovery, multi-niche directory routing |
| [**02. Google Flow Image Generation SOP**](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/02_GOOGLE_FLOW_IMAGE_GENERATION_SOP.md) | Autonomous browser automation via Chrome CDP, prompt injection, and vision curation | Chrome CDP (Port 9222), Playwright, OpenCV | Nano Banana model cascade, 1-image acceptance rule, 10–30s pacing, CV scoring |
| [**03. Multi-Niche Scriptwriting SOP**](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/03_MULTI_NICHE_SCRIPTWRITING_SOP.md) | High-retention script formulation, dynamic niche taxonomy, and stick-figure prompts | Antigravity AI Engine, Dynamic Niche Taxonomy | 20–50 char micro-beats, mandatory punctuation dividers, 7-act retention arcs |
| [**04. ElevenLabs Audio Mastering SOP**](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/04_ELEVENLABS_AUDIO_MASTERING_SOP.md) | Unified voiceover generation, millisecond alignment, silence normalization, and XML assembly | ElevenLabs API (`eleven_multilingual_v2`), FFmpeg, Apple `xmeml` | Always-combined mode, >300ms silence trimmed to 150ms tail + 150ms head, -12.28 LUFS |
| [**05. YouTube Publishing & Packaging SOP**](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/05_YOUTUBE_PUBLISHING_PACKAGING_SOP.md) | Channel launch kits, CTR-optimized thumbnails, high-velocity metadata, and QA workflows | YouTube Studio, Ink Explainer Design System | 1280x720 white-bg thumbnails, algorithmic keyword tags, unlisted QA protocol |
| [**06. Finance Creative Intelligence SOP**](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/06_FINANCE_CREATIVE_INTELLIGENCE_SOP.md) | Money behavior, 8 story engines, 10-point title test, Shariah wealth principles | Antigravity AI Engine, Behavioral Story Models | Zero interest/riba, 5-15s story hook, stick-figure visual thinking, 9-point self-audit |
| [**07. Infographic Vector Animation SOP**](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/07_INFOGRAPHIC_VECTOR_ANIMATION_PIPELINE_SOP.md) | 2D motion graphics (*The Infographics Show* style), FK rigging, 50% midpoint mask, 5W1H diagnostics, MP4 export | Playwright, FFmpeg, Forward Kinematics, SVG Engine | Zero twisted limbs, 50% mask handover, single-source captions, 100/100 audit score |

---

## 🏛️ Studio Aesthetic & Core Principles

1. **The Visual Signature**:
   - Pure white paper backgrounds (`#FFFFFF`).
   - Pitch-black ink outlines (`#000000`) with expressive, white-filled stick figures in the spirit of *MinutePhysics* and *Casually Explained*.
   - Flat, selective muted accent colors for clarity.
   - **Zero realistic human anatomy, zero flesh skin tones, zero floating card borders**.

2. **Ultra-Fast Visual Pacing**:
   - Visual cuts occur every **20 to 50 characters** (approx. 1 to 2.5 seconds).
   - Every punctuation mark (`,`, `.`, `;`, `?`, `!`, `:`, `—`) acts as an immutable divider that spawns an immediate image change.

3. **Combined Audio Continuity**:
   - Voiceovers are synthesized as a single unbroken paragraph stream to preserve natural human prosody, inflection, and cadence.
   - Silence gaps exceeding 300ms are automatically compressed to exactly 300ms (150ms tail cushion + 150ms head cushion).

4. **100% Local Autonomous Execution**:
   - Zero external LLM subscription dependencies.
   - Fully driven by Antigravity paired with local tools, Chrome CDP, and local Python pipelines.

---

## 📁 Repository Directory Structure

```text
25- Ink Explainers/
├── 1- Postmartum/                 <- Competitor forensic analysis & transcripts by niche
│   ├── history/
│   ├── finance/
│   ├── medical/
│   ├── horror/
│   └── engineering/
├── 2- Code/                       <- Production automation engine & Web UI
│   ├── pipeline_orchestrator.py   <- Master 7-stage orchestrator
│   ├── web_ui.py                  <- Web-based production control dashboard
│   ├── config.py                  <- Path resolver & multi-niche discovery engine
│   └── ...
├── 3- Finals/                     <- Master production assets & timelines by niche
│   ├── history/
│   ├── finance/
│   ├── medical/
│   ├── horror/
│   └── engineering/
├── 4- YouTube Setup/              <- Multi-channel network branding & channel kits
│   ├── history/Forefathers Explained/
│   ├── finance/Capital Explained/
│   └── ...
├── 5- SOPs/                       <- Standard operating procedures (this library)
├── SOP.md                         <- Root executive overview and quick-reference
└── README.md                      <- Project introduction
```

