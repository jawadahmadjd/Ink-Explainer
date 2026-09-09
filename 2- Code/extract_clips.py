import subprocess, os

# Let us extract 5-second audio clips to inspect what sounds/music exist
clips = [(0, 5, 'clip_alarm_intro.wav'), (15, 20, 'clip_50k_transition.wav'), (180, 185, 'clip_mid_music.wav'), (420, 425, 'clip_firelight.wav')]
for start, end, name in clips:
    cmd = ['ffmpeg', '-ss', str(start), '-to', str(end), '-i', 'video_low.mp4', '-ac', '1', '-ar', '22050', name, '-y']
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print('Clips extracted:', [c[2] for c in clips])
