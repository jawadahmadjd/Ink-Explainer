"""
Stage 6: Execution Telemetry & Final Work Reporter
Tracks pipeline milestones, start/end timestamps, elapsed durations, and generates summary reports.
"""

import os
import json
from datetime import datetime

class PipelineReporter:
    def __init__(self, video_title: str, mode: str = "auto", output_dir: str = None):
        self.video_title = video_title
        self.mode = mode
        self.output_dir = output_dir
        self.start_time = datetime.now()
        self.end_time = None
        self.stages = {}
        self.errors = []
        self.stats = {}

    def start_stage(self, stage_num: int, name: str):
        print(f"\n{'='*60}")
        print(f"[STAGE {stage_num}] STARTING: {name}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        self.stages[stage_num] = {
            "name": name,
            "start": datetime.now(),
            "end": None,
            "duration_sec": 0,
            "status": "RUNNING",
            "details": {}
        }

    def end_stage(self, stage_num: int, details: dict = None):
        if stage_num in self.stages:
            now = datetime.now()
            st = self.stages[stage_num]
            st["end"] = now
            st["duration_sec"] = round((now - st["start"]).total_seconds(), 2)
            st["status"] = "COMPLETED"
            if details:
                st["details"].update(details)
            print(f"\n-> [STAGE {stage_num} COMPLETED] in {st['duration_sec']:.1f}s\n")

    def record_error(self, stage_num: int, error_msg: str):
        self.errors.append({
            "stage": stage_num,
            "timestamp": datetime.now().isoformat(),
            "error": str(error_msg)
        })
        if stage_num in self.stages:
            self.stages[stage_num]["status"] = "FAILED"
            self.stages[stage_num]["error"] = str(error_msg)

    def record_stat(self, key: str, value):
        self.stats[key] = value

    def finish(self) -> dict:
        self.end_time = datetime.now()
        total_duration = round((self.end_time - self.start_time).total_seconds(), 2)

        report = {
            "project_title": self.video_title,
            "mode": self.mode,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "total_duration_seconds": total_duration,
            "total_duration_human": f"{int(total_duration // 60)}m {int(total_duration % 60)}s",
            "stages": {
                k: {
                    "name": v["name"],
                    "start": v["start"].isoformat(),
                    "end": v["end"].isoformat() if v["end"] else None,
                    "duration_seconds": v["duration_sec"],
                    "status": v["status"],
                    "details": v["details"]
                }
                for k, v in self.stages.items()
            },
            "stats": self.stats,
            "errors": self.errors
        }

        # Print console summary
        print("\n" + "="*65)
        print("          END-TO-END PIPELINE EXECUTION REPORT")
        print("="*65)
        print(f"Project Title:    {self.video_title}")
        print(f"Execution Mode:   {self.mode}")
        print(f"Start Time:       {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End Time:         {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Duration:   {report['total_duration_human']} ({total_duration}s)")
        print("-"*65)
        print(f"{'Stage':<8} | {'Stage Name':<35} | {'Status':<10} | {'Duration'}")
        print("-"*65)
        for num, st in self.stages.items():
            dur_str = f"{st['duration_sec']}s"
            print(f"Stage {num:<2} | {st['name']:<35} | {st['status']:<10} | {dur_str}")
        print("="*65)

        # Save markdown report
        if self.output_dir and os.path.exists(self.output_dir):
            report_md_path = os.path.join(self.output_dir, "EXECUTION_REPORT.md")
            self._write_markdown_report(report_md_path, report)
            print(f"Report saved to: {report_md_path}\n")

        return report

    def _write_markdown_report(self, path: str, data: dict):
        lines = [
            f"# Pipeline Execution Report: {data['project_title']}",
            "",
            f"- **Execution Mode**: `{data['mode']}`",
            f"- **Start Time**: `{data['start_time']}`",
            f"- **End Time**: `{data['end_time']}`",
            f"- **Total Duration**: **{data['total_duration_human']}** ({data['total_duration_seconds']}s)",
            "",
            "## Stage Milestones",
            "",
            "| Stage | Name | Status | Duration | Key Metrics |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ]
        for num, st in self.stages.items():
            details_str = ", ".join(f"{k}: {v}" for k, v in st.get("details", {}).items() if not isinstance(v, (dict, list)))
            lines.append(f"| Stage {num} | {st['name']} | `{st['status']}` | {st['duration_sec']}s | {details_str} |")

        if data["stats"]:
            lines.extend(["", "## Project Statistics", ""])
            for k, v in data["stats"].items():
                lines.append(f"- **{k}**: {v}")

        if data["errors"]:
            lines.extend(["", "## Errors & Warnings", ""])
            for err in data["errors"]:
                lines.append(f"- `[Stage {err['stage']}]` {err['error']}")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
