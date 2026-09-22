# 📋 Standard Operating Procedures (SOP): Autonomous Ink Explainers Studio

> **Central Operations Hub & Executive Index**  
> For the comprehensive, modular operational manuals, visit the [**`5- SOPs/`**](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/README.md) directory.

---

## 🗂️ Modular SOP Library

| SOP Document | Domain & Focus | Direct Link |
| :--- | :--- | :--- |
| **SOP 01: End-to-End Pipeline** | 7-stage automated lifecycle from URL ingestion to NLE sequence | [`5- SOPs/01_END_TO_END_PIPELINE_SOP.md`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/01_END_TO_END_PIPELINE_SOP.md) |
| **SOP 02: Google Flow Generation** | Chrome CDP (port 9222) automation, model cascade & vision scoring | [`5- SOPs/02_GOOGLE_FLOW_IMAGE_GENERATION_SOP.md`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/02_GOOGLE_FLOW_IMAGE_GENERATION_SOP.md) |
| **SOP 03: Multi-Niche Scriptwriting** | 20–50 char micro-beats, mandatory punctuation dividers, 7-act arcs | [`5- SOPs/03_MULTI_NICHE_SCRIPTWRITING_SOP.md`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/03_MULTI_NICHE_SCRIPTWRITING_SOP.md) |
| **SOP 04: ElevenLabs Audio Mastering** | Always-combined voiceover, 300ms silence normalization, Apple XML | [`5- SOPs/04_ELEVENLABS_AUDIO_MASTERING_SOP.md`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/04_ELEVENLABS_AUDIO_MASTERING_SOP.md) |
| **SOP 05: YouTube Publishing & Packaging** | Channel kits, white-canvas CTR thumbnails, metadata & QA workflow | [`5- SOPs/05_YOUTUBE_PUBLISHING_PACKAGING_SOP.md`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/05_YOUTUBE_PUBLISHING_PACKAGING_SOP.md) |
| **SOP 06: Finance Creative Intelligence** | Money behavior, 8 story engines, 10-point title test, Shariah wealth principles | [`5- SOPs/06_FINANCE_CREATIVE_INTELLIGENCE_SOP.md`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/06_FINANCE_CREATIVE_INTELLIGENCE_SOP.md) |
| **SOP 07: Infographic Vector Animation** | 2D motion graphics (*The Infographics Show* style), FK rigging, 50% midpoint mask, 5W1H diagnostics, MP4 export | [`5- SOPs/07_INFOGRAPHIC_VECTOR_ANIMATION_PIPELINE_SOP.md`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/07_INFOGRAPHIC_VECTOR_ANIMATION_PIPELINE_SOP.md) |
| **SOPs Index & Architecture** | Complete overview of studio conventions and directory topology | [`5- SOPs/README.md`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/README.md) |

---

## ⚡ Executive Quick Reference (Core Rules & Thresholds)

### 1. Visual Style & Character Mandates
* **Art Style**: Minimalist 2D hand-drawn black ink comic line art on pure white paper (`#FFFFFF`).
* **Character Mandate**: All human characters **MUST** be minimalist white-filled black-outlined stick figures (*MinutePhysics* / *Casually Explained* style) with simple circular heads, pure solid white head fill, clean bold black comic outlines, simple black stick limbs, zero realistic human anatomy, and zero flesh skin tones.
* **Framing**: 100% full-bleed edge-to-edge environment grounding. **Zero white borders, zero floating card matting**.
* **Resolution**: Native 16:9 widescreen (`1376 × 768 px`).

### 2. Micro-Beat Pacing & Punctuation Dividers
* **Target Beat Duration**: **20 to 50 characters** of spoken dialogue per shot (~1.0 to 2.2 seconds).
* **Mandatory Punctuation Cuts**: Every comma (`,`), period (`.`), semicolon (`;`), question mark (`?`), exclamation point (`!`), colon (`:`), and em-dash (`—`) forces an immediate shot cut, regardless of word length (e.g. *"Why?"* receives its own dedicated shot and image).
* **Number & Decimal Shielding**: Values such as `99.9%` or `$3.50` are protected from false sentence splitting.

### 3. Google Flow Image Generation & Model Cascade
* **Browser Attachment**: Chrome CDP on port `9222` (`--remote-debugging-port=9222`).
* **Model Priority Cascade**: `🍌 Nano Banana Pro` (Priority 1) $\rightarrow$ `🍌 Nano Banana 2` (Priority 2) $\rightarrow$ `🍌 Nano Banana 2 Lite` (Priority 3).
* **Variations per Prompt**: `x2`.
* **Partial Generation 1-Image Rule**: If generation encounters an error or timeout, but $\ge 1$ variation was rendered and computer vision score $\ge 50.0$, accept it immediately as the final winning image and proceed.
* **Pacing Delay**: Randomized interval between **10 and 30 seconds** between shots.
* **Single Destination Folder**: All winning images are saved exclusively to `Final selected images/shot_NNN.jpg`.

### 4. ElevenLabs Voiceover & Silence Normalization
* **Generation Mode**: **ALWAYS COMBINED**. Never generate voiceover clips sentence-by-sentence.
* **Active Voice**: `Tyler - Clear US YouTube Creator Voice` (`rPMkKgdwgIwqv4fXgR6N`) on `eleven_multilingual_v2`.
* **Silence Normalization Rule**: Any inter-sentence pause $> 300\text{ ms}$ is compressed, leaving exactly **150ms tail cushion** after the spoken phrase and **150ms head cushion** before the next phrase (total 300ms cushion).
* **Loudness Target**: **-12.28 LUFS** ($\pm 0.5$ LUFS), True Peak max -1.0 dBFS.

### 5. Multi-Niche Directory Mapping

```text
d:\Tools of Jawad\25- Ink Explainers\
├── 1- Postmartum/<niche>/<Project Name>/   <- Competitor ingestion, transcripts & cuts
├── 2- Code/                               <- Master pipeline & Web UI (Port 5000)
├── 3- Finals/<niche>/<Project Name>/       <- Storyboards, voiceovers, XML sequences
├── 4- YouTube Setup/<niche>/<Brand>/      <- Channel kits, banners, PFPs, thumbnails
└── 5- SOPs/                               <- Full modular SOP manuals
```
