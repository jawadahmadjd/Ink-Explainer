# Let us inspect the intro sound effects
# At 00:00 - 00:05, there is an alarm ringing SFX.
# Let's inspect the high frequencies (alarm bell frequencies typically 2kHz - 4kHz)
import wave, numpy as np

with wave.open('clip_alarm_intro.wav', 'rb') as w:
    data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float)
    rate = w.getframerate()

# Check energy in 2000-4000 Hz band (alarm sound) vs voice band (100-1000 Hz)
fft = np.abs(np.fft.rfft(data[:rate*2]))
freqs = np.fft.rfftfreq(rate*2, 1.0/rate)
alarm_band = np.mean(fft[(freqs >= 2000) & (freqs <= 4000)])
voice_band = np.mean(fft[(freqs >= 100) & (freqs <= 1000)])
print(f"Alarm clip high-mid energy ratio: {alarm_band/voice_band:.3f}")
