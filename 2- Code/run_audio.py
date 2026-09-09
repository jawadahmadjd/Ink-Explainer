import subprocess, json

cmd = ['ffmpeg', '-i', 'video_low.mp4', '-af', 'loudnorm=print_format=json', '-f', 'null', '-']
proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
err = proc.stderr
idx = err.find('{')
if idx != -1:
    end_idx = err.rfind('}')
    json_str = err[idx:end_idx+1]
    print(json_str)
