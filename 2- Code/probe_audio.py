import subprocess

# Let us check audio stream properties
cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', 'video_low.mp4']
proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
import json
data = json.loads(proc.stdout)
for s in data.get('streams', []):
    if s.get('codec_type') == 'audio':
        print('Audio Codec:', s.get('codec_name'), 'Sample Rate:', s.get('sample_rate'), 'Channels:', s.get('channels'), 'Bitrate:', s.get('bit_rate'))
