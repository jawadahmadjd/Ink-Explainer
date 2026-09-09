import wave, struct, numpy as np

for name in ['clip_alarm_intro.wav', 'clip_50k_transition.wav', 'clip_mid_music.wav', 'clip_firelight.wav']:
    with wave.open(name, 'rb') as w:
        frames = w.readframes(w.getnframes())
        samples = np.frombuffer(frames, dtype=np.int16)
        rate = w.getframerate()
        rms = np.sqrt(np.mean(samples.astype(float)**2))
        peak = np.max(np.abs(samples))
        print(f"{name}: RMS={rms:.1f}, Peak={peak}, Duration={len(samples)/rate:.2f}s")
