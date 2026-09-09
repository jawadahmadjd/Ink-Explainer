import wave, numpy as np

def get_f0(filename):
    with wave.open(filename, 'rb') as w:
        rate = w.getframerate()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float)
    # Autocorrelation over 50ms windows
    win_size = int(rate * 0.05)
    pitches = []
    for i in range(0, len(data) - win_size, int(rate * 0.025)):
        window = data[i:i+win_size]
        if np.std(window) < 500: # silent or quiet
            continue
        corr = np.correlate(window, window, mode='full')[win_size-1:]
        # Look for pitch peak between 80Hz and 250Hz
        min_lag = int(rate / 250)
        max_lag = int(rate / 80)
        peak_lag = min_lag + np.argmax(corr[min_lag:max_lag])
        if corr[peak_lag] > 0.4 * corr[0]:
            pitches.append(rate / peak_lag)
    if pitches:
        return np.mean(pitches), np.median(pitches), np.min(pitches), np.max(pitches)
    return 0, 0, 0, 0

print("Voice pitch estimates (Hz):")
for name in ['clip_alarm_intro.wav', 'clip_50k_transition.wav', 'clip_mid_music.wav', 'clip_firelight.wav']:
    mean_p, med_p, min_p, max_p = get_f0(name)
    print(f"  {name}: Mean={mean_p:.1f}Hz, Median={med_p:.1f}Hz (Range: {min_p:.1f} - {max_p:.1f}Hz)")
