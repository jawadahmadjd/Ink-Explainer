"""
Stage 5: Apple xmeml v4 XML Sequence Assembly for Premiere Pro / DaVinci Resolve
Maps master normalized voiceover on Audio Track 1 and all storyboard images on Video Track 1
aligned sample-accurately to voiceover sentence timestamps with zero black frames.
"""

import os
import sys
import json
import csv
import xml.etree.ElementTree as ET
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def sec_to_frames(sec: float, fps: int = 24) -> int:
    return int(round(sec * fps))

def path_to_file_uri(path: str) -> str:
    norm = path.replace("\\", "/")
    if norm[1:3] == ":/":
        return f"file://localhost/{norm[0]}:/{norm[3:]}"
    return f"file://localhost/{norm}"

def run_stage5_timeline_xml(video_title: str, fps: int = 24) -> dict:
    """
    Generate Apple xmeml v4 XML timeline sequence.
    """
    dirs = config.get_project_dirs(video_title)
    finals_dir = dirs["finals_dir"]
    vo_dir = dirs["voiceovers_dir"]
    final_img_dir = dirs["final_images_dir"]
    shots_align_path = os.path.join(vo_dir, "shots_timing_alignment.json")
    master_wav_path = os.path.join(vo_dir, "voiceover_master_normalized.wav")
    master_mp3_path = os.path.join(vo_dir, "voiceover_master_normalized.mp3")
    xml_output_path = dirs["timeline_xml"]

    if not os.path.exists(shots_align_path):
        raise FileNotFoundError(f"Missing shots alignment file: {shots_align_path}. Run Stage 3 first.")

    with open(shots_align_path, "r", encoding="utf-8") as f:
        shot_timings = json.load(f)

    # Determine master audio file and length
    audio_path = master_wav_path if os.path.exists(master_wav_path) else master_mp3_path
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Missing master audio file in: {vo_dir}")

    a_info = sf.info(audio_path)
    audio_duration_sec = a_info.duration
    total_sequence_frames = sec_to_frames(audio_duration_sec, fps)

    print(f"\n[STAGE 5] Assembling NLE Sequence XML for '{video_title}'")
    print(f"Master Audio Duration: {audio_duration_sec:.2f}s ({total_sequence_frames} frames @ {fps} fps)")
    print(f"Total Video Clips to Map: {len(shot_timings)}")

    # Construct frame boundaries for each shot
    # Each shot starts at shot_start and lasts until next shot_start
    clips = []
    for i, st in enumerate(shot_timings):
        shot_num = st["shot_num"]
        start_f = sec_to_frames(st["start_sec"], fps)
        if i + 1 < len(shot_timings):
            end_f = sec_to_frames(shot_timings[i+1]["start_sec"], fps)
        else:
            end_f = total_sequence_frames

        # Ensure non-zero duration
        if end_f <= start_f:
            end_f = start_f + 1

        img_name = f"shot_{shot_num:03d}.jpg"
        img_path = os.path.join(final_img_dir, img_name)

        clips.append({
            "shot_num": shot_num,
            "name": img_name,
            "path": img_path,
            "start_frame": start_f,
            "end_frame": end_f,
            "duration_frames": end_f - start_f
        })

    # Build XML
    root = ET.Element("xmeml", version="4")
    seq = ET.SubElement(root, "sequence", id="sequence-1")
    ET.SubElement(seq, "name").text = f"{video_title} - Storyboard Master Sequence"
    ET.SubElement(seq, "duration").text = str(total_sequence_frames)

    rate = ET.SubElement(seq, "rate")
    ET.SubElement(rate, "timebase").text = str(fps)
    ET.SubElement(rate, "ntsc").text = "FALSE"

    timecode = ET.SubElement(seq, "timecode")
    tc_rate = ET.SubElement(timecode, "rate")
    ET.SubElement(tc_rate, "timebase").text = str(fps)
    ET.SubElement(tc_rate, "ntsc").text = "FALSE"
    ET.SubElement(timecode, "string").text = "00:00:00:00"
    ET.SubElement(timecode, "frame").text = "0"

    media = ET.SubElement(seq, "media")

    # 1. VIDEO TRACK
    video = ET.SubElement(media, "video")
    v_format = ET.SubElement(video, "format")
    v_sample = ET.SubElement(v_format, "samplecharacteristics")
    v_rate = ET.SubElement(v_sample, "rate")
    ET.SubElement(v_rate, "timebase").text = str(fps)
    ET.SubElement(v_rate, "ntsc").text = "FALSE"
    ET.SubElement(v_sample, "width").text = str(config.TARGET_WIDTH)
    ET.SubElement(v_sample, "height").text = str(config.TARGET_HEIGHT)

    v_track = ET.SubElement(video, "track")

    for clip in clips:
        clipitem = ET.SubElement(v_track, "clipitem", id=f"clipitem-v-{clip['shot_num']}")
        ET.SubElement(clipitem, "name").text = clip["name"]
        ET.SubElement(clipitem, "duration").text = str(clip["duration_frames"])

        c_rate = ET.SubElement(clipitem, "rate")
        ET.SubElement(c_rate, "timebase").text = str(fps)
        ET.SubElement(c_rate, "ntsc").text = "FALSE"

        ET.SubElement(clipitem, "start").text = str(clip["start_frame"])
        ET.SubElement(clipitem, "end").text = str(clip["end_frame"])
        ET.SubElement(clipitem, "in").text = "0"
        ET.SubElement(clipitem, "out").text = str(clip["duration_frames"])

        c_file = ET.SubElement(clipitem, "file", id=f"file-v-{clip['shot_num']}")
        ET.SubElement(c_file, "name").text = clip["name"]
        ET.SubElement(c_file, "pathurl").text = path_to_file_uri(clip["path"])
        f_rate = ET.SubElement(c_file, "rate")
        ET.SubElement(f_rate, "timebase").text = str(fps)
        ET.SubElement(f_rate, "ntsc").text = "FALSE"

        f_media = ET.SubElement(c_file, "media")
        f_video = ET.SubElement(f_media, "video")
        f_sample = ET.SubElement(f_video, "samplecharacteristics")
        ET.SubElement(f_sample, "width").text = str(config.TARGET_WIDTH)
        ET.SubElement(f_sample, "height").text = str(config.TARGET_HEIGHT)

    # 2. AUDIO TRACK
    audio = ET.SubElement(media, "audio")
    a_sample = ET.SubElement(audio, "samplecharacteristics")
    ET.SubElement(a_sample, "depth").text = "16"
    ET.SubElement(a_sample, "samplerate").text = "44100"

    a_track = ET.SubElement(audio, "track")
    a_clip = ET.SubElement(a_track, "clipitem", id="clipitem-a-master")
    ET.SubElement(a_clip, "name").text = os.path.basename(audio_path)
    ET.SubElement(a_clip, "duration").text = str(total_sequence_frames)

    ac_rate = ET.SubElement(a_clip, "rate")
    ET.SubElement(ac_rate, "timebase").text = str(fps)
    ET.SubElement(ac_rate, "ntsc").text = "FALSE"

    ET.SubElement(a_clip, "start").text = "0"
    ET.SubElement(a_clip, "end").text = str(total_sequence_frames)
    ET.SubElement(a_clip, "in").text = "0"
    ET.SubElement(a_clip, "out").text = str(total_sequence_frames)

    ac_file = ET.SubElement(a_clip, "file", id="file-a-master")
    ET.SubElement(ac_file, "name").text = os.path.basename(audio_path)
    ET.SubElement(ac_file, "pathurl").text = path_to_file_uri(audio_path)
    af_rate = ET.SubElement(ac_file, "rate")
    ET.SubElement(af_rate, "timebase").text = str(fps)
    ET.SubElement(af_rate, "ntsc").text = "FALSE"

    af_media = ET.SubElement(ac_file, "media")
    af_audio = ET.SubElement(af_media, "audio")
    af_sample = ET.SubElement(af_audio, "samplecharacteristics")
    ET.SubElement(af_sample, "depth").text = "16"
    ET.SubElement(af_sample, "samplerate").text = "44100"

    # Write formatted XML
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(xml_output_path, encoding="utf-8", xml_declaration=True)

    print(f"\n-> [STAGE 5 COMPLETE] Final Timeline XML generated at: {xml_output_path}")
    return {
        "xml_path": xml_output_path,
        "video_clips_count": len(clips),
        "total_frames": total_sequence_frames,
        "duration_sec": audio_duration_sec,
        "fps": fps
    }
