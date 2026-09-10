"""
Autonomous Ink Explainer Master Pipeline Orchestrator
Coordinates end-to-end production across Stages 1 through 6:
  Stage 1: Ingestion & Forensic Postmortem (yt-dlp, ffmpeg scene cuts, audio LUFS profile)
  Stage 2: Script Preparation & Stick-Figure Storyboard Prompts (MinutePhysics style, CSV, audit)
  Stage 3: ElevenLabs Combined Voiceover Production & Silence Normalization (>300ms trimmed)
  Stage 4: Google Flow Autonomous Stick-Figure Generation (Chrome CDP, model cascade, CV scoring)
  Stage 5: Apple xmeml v4 Sequence XML Assembly for Premiere Pro / DaVinci Resolve
  Stage 6: Execution Telemetry, Start/End Timestamps, and Final Work Report
"""

import os
import sys
import argparse
from datetime import datetime

# Ensure modules directory is discoverable
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

import config
from modules.stage1_postmortem import run_stage1_postmortem
from modules.stage2_script_prompts import run_stage2_script_prompts
from modules.stage3_voiceover import run_stage3_voiceover
from modules.stage4_image_gen import run_stage4_image_gen
from modules.stage5_timeline_xml import run_stage5_timeline_xml
from modules.stage6_reporter import PipelineReporter

def main():
    parser = argparse.ArgumentParser(
        description="Autonomous Ink Explainer End-to-End Production Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline for a new YouTube video:
  python pipeline_orchestrator.py --url "https://www.youtube.com/watch?v=..." --mode auto

  # Run full pipeline on an existing project title:
  python pipeline_orchestrator.py --title "1- What Did Ancient Humans Actually Do All Day"

  # Run only Voiceover & XML assembly:
  python pipeline_orchestrator.py --title "1- What Did Ancient Humans Actually Do All Day" --stage 3,5

  # Regenerate specific shots in Google Flow:
  python pipeline_orchestrator.py --title "1- What Did Ancient Humans Actually Do All Day" --stage 4 --shots 127,129,131 --model "Nano Banana 2"
        """
    )
    parser.add_argument("--url", type=str, default="", help="Reference YouTube URL for ingestion and postmortem")
    parser.add_argument("--title", type=str, default="1- What Did Ancient Humans Actually Do All Day", help="Project / Video Title")
    parser.add_argument("--stage", type=str, default="all", help="Stage(s) to run: 'all', or comma-separated numbers: '1,2,3,4,5'")
    parser.add_argument("--mode", type=str, choices=["auto", "interactive"], default="auto", help="Execution mode: 'auto' (unattended) or 'interactive' (review gates)")
    parser.add_argument("--model", type=str, default="", help="Google Flow starting model ('Nano Banana Pro', 'Nano Banana 2', etc.)")
    parser.add_argument("--shots", type=str, default="", help="Comma-separated shot numbers for Stage 4 (e.g. '1,2,3')")
    parser.add_argument("--skip-images", action="store_true", help="Skip Google Flow image generation (Stage 4)")
    parser.add_argument("--skip-vo", action="store_true", help="Skip ElevenLabs voiceover generation (Stage 3)")
    parser.add_argument("--force-vo", action="store_true", help="Force regenerate voiceover even if cached")

    args = parser.parse_args()

    # Parse stages
    all_stages = ["1", "2", "3", "4", "5"]
    if args.stage.lower() == "all":
        stages_to_run = all_stages
    else:
        stages_to_run = [s.strip() for s in args.stage.split(",") if s.strip() in all_stages]

    if args.skip_images and "4" in stages_to_run:
        stages_to_run.remove("4")
    if args.skip_vo and "3" in stages_to_run:
        stages_to_run.remove("3")

    # Determine project title
    video_title = args.title
    if args.url and not args.title:
        video_title = "Ink Explainer Video"

    dirs = config.get_project_dirs(video_title)
    finals_dir = dirs["finals_dir"]
    os.makedirs(finals_dir, exist_ok=True)

    # Initialize reporter
    reporter = PipelineReporter(video_title=video_title, mode=args.mode, output_dir=finals_dir)

    print("="*65)
    print("      AUTONOMOUS INK EXPLAINER PRODUCTION PIPELINE")
    print("="*65)
    print(f"Project Title:    {video_title}")
    print(f"Execution Mode:   {args.mode.upper()}")
    print(f"Active Stages:    {', '.join(stages_to_run)}")
    print(f"Destination:      {finals_dir}")
    print(f"Start Timestamp:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*65)

    try:
        # ---------------------------------------------------------------------
        # STAGE 1: INGESTION & FORENSIC POSTMORTEM
        # ---------------------------------------------------------------------
        if "1" in stages_to_run:
            reporter.start_stage(1, "Ingestion & Forensic Postmortem")
            if not args.url:
                print("No --url provided. Checking existing postmortem folder...")
                pm_dir = dirs["postmortem_dir"]
                if os.path.exists(pm_dir) and os.path.exists(os.path.join(pm_dir, "cuts_data.json")):
                    print(f"Existing postmortem data found in: {pm_dir}")
                    reporter.end_stage(1, {"status": "Loaded existing postmortem", "path": pm_dir})
                else:
                    raise ValueError("Stage 1 requested but neither --url provided nor existing postmortem found.")
            else:
                pm_res = run_stage1_postmortem(args.url, custom_title=video_title)
                reporter.record_stat("Postmortem Cuts", pm_res.get("cuts_count", 0))
                reporter.record_stat("Video Duration", f"{pm_res.get('duration', 0):.1f}s")
                reporter.end_stage(1, pm_res)

        # ---------------------------------------------------------------------
        # STAGE 2: SCRIPT PREPARATION & STICK-FIGURE PROMPT COMPILATION
        # ---------------------------------------------------------------------
        if "2" in stages_to_run:
            reporter.start_stage(2, "Script & Stick-Figure Storyboard Prompts")
            s2_res = run_stage2_script_prompts(video_title)
            reporter.record_stat("Total Storyboard Shots", s2_res["total_shots"])
            reporter.record_stat("Script Word Count", s2_res["word_count"])
            reporter.end_stage(2, s2_res)

            # Interactive gate if enabled
            if args.mode == "interactive" and len(stages_to_run) > 1:
                print("\n[INTERACTIVE REVIEW GATE]")
                print(f"Generated {s2_res['total_shots']} shots in {dirs['master_csv']}.")
                confirm = input("Proceed to Voiceover & Image Generation? (y/n): ").strip().lower()
                if confirm not in ("y", "yes", ""):
                    print("Halting pipeline per user request.")
                    reporter.finish()
                    return

        # ---------------------------------------------------------------------
        # STAGE 3: ELEVENLABS COMBINED VO & SILENCE NORMALIZATION
        # ---------------------------------------------------------------------
        if "3" in stages_to_run:
            reporter.start_stage(3, "ElevenLabs Combined VO & Silence Normalization")
            vo_res = run_stage3_voiceover(video_title, force_regenerate=args.force_vo)
            reporter.record_stat("Voiceover Duration", f"{vo_res.get('duration_sec', 0)}s")
            reporter.record_stat("Words Spoken", vo_res.get("total_words", 0))
            reporter.end_stage(3, vo_res)

        # ---------------------------------------------------------------------
        # STAGE 4: GOOGLE FLOW STICK-FIGURE IMAGE GENERATION
        # ---------------------------------------------------------------------
        if "4" in stages_to_run:
            reporter.start_stage(4, "Google Flow Autonomous Stick-Figure Generation")
            target_list = [s.strip() for s in args.shots.split(",") if s.strip()] if args.shots else None
            img_res = run_stage4_image_gen(
                video_title=video_title,
                target_shots=target_list,
                model=args.model
            )
            reporter.end_stage(4, img_res)

        # ---------------------------------------------------------------------
        # STAGE 5: APPLE XMEML V4 XML SEQUENCE ASSEMBLY
        # ---------------------------------------------------------------------
        if "5" in stages_to_run:
            reporter.start_stage(5, "Apple xmeml v4 XML Sequence Assembly")
            xml_res = run_stage5_timeline_xml(video_title)
            reporter.record_stat("Timeline Clips Mapped", xml_res["video_clips_count"])
            reporter.record_stat("Timeline Total Frames", xml_res["total_frames"])
            reporter.end_stage(5, xml_res)

    except Exception as ex:
        print(f"\n[PIPELINE EXCEPTION] {ex}")
        import traceback
        traceback.print_exc()
        reporter.record_error(0, str(ex))

    finally:
        # STAGE 6: FINALIZE & EMIT WORK REPORT
        reporter.finish()

if __name__ == "__main__":
    main()
