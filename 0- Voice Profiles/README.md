# 🎙️ Voice Profiles for Qwen3-TTS Voice Cloning

Place the voice sample you want to clone in this folder:

1. **`sample.wav`** (or `sample.mp3`):
   - A clean **3 to 10 second** audio clip of the person speaking.
   - For best results: NO background music, NO heavy echo/reverb, crisp clear microphone.

2. **`transcript.txt`**:
   - The exact words spoken in `sample.wav`.
   - Providing this transcript ensures that Qwen captures accent, prosody, pacing, and tone with 10x higher fidelity.

---

### How to use:
Whenever you want to change the voice being cloned, simply replace `sample.wav` and update `transcript.txt` here!

---

### 📜 Script Chunking Standard (< 2000 Characters):
For long-form narration with Qwen 1.7B:
- **Maximum Chunk Limit**: `< 2000 characters` per request.
- **Natural Chapter Rule**: Always split at **major thematic act/paragraph boundaries** ending in full stops (`.`, `!`, `?`), never mid-sentence. This prevents pitch spikes and unnatural prosody shifts.
- **Project Files**: Look for `qwen_voiceover_chunks.txt` and `Voiceovers/qwen_voiceover_chunks.json` inside each project's folder in `3- Finals/<niche>/<Project Name>/`.
- **Governing SOP**: See [`SOP 04: Section 5`](file:///d:/Tools%20of%20Jawad/25-%20Ink%20Explainers/5-%20SOPs/04_ELEVENLABS_AUDIO_MASTERING_SOP.md#L71-L100).

