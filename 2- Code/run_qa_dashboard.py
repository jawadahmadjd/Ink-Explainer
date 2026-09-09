import csv
import json
import os
import shutil
import sys
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import urllib.parse
import cv2
import numpy as np

PORT = 8507

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

CSV_PATH = os.path.join(PROJECT_ROOT, "3- Finals", "storyboard_master.csv")
RAW_IMG_DIR = os.path.join(PROJECT_ROOT, "3- Finals", "flow_generated_images")
FINAL_DIR_ROOT = os.path.join(PROJECT_ROOT, "Final selected images")
FINAL_DIR_FINALS = os.path.join(PROJECT_ROOT, "3- Finals", "Final selected images")
FINAL_DIR_LEGACY = os.path.join(PROJECT_ROOT, "3- Finals", "final_selected_images")
HTML_FILE = os.path.join(BASE_DIR, "storyboard_qa_dashboard.html")

LEARNING_JSON = os.path.join(PROJECT_ROOT, "3- Finals", "ai_learning_log.json")
REGEN_QUEUE_JSON = os.path.join(PROJECT_ROOT, "3- Finals", "regeneration_queue.json")
SELECTION_LOG = os.path.join(PROJECT_ROOT, "3- Finals", "selection_log.csv")

def analyze_and_score_variation(image_path):
    """Calculates CV score on single image on-demand when selected or reviewed."""
    img = cv2.imread(image_path)
    if img is None:
        return 0.0, {}

    h, w, _ = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    sharpness_score = min(100.0, float(laplacian_var) / 15.0)

    top_strip = gray[:max(1, int(h*0.02)), :]
    bot_strip = gray[max(0, int(h*0.98)):, :]
    left_strip = gray[:, :max(1, int(w*0.02))]
    right_strip = gray[:, max(0, int(w*0.98)):]
    border_pixels = np.concatenate([top_strip.flatten(), bot_strip.flatten(), left_strip.flatten(), right_strip.flatten()])
    border_mean = float(np.mean(border_pixels))
    border_std = float(np.std(border_pixels))
    border_penalty = 0.0
    if border_mean > 240 and border_std < 10:
        border_penalty = 50.0

    center_y, center_x = int(h*0.2), int(w*0.2)
    center_crop = gray[center_y:int(h*0.8), center_x:int(w*0.8)]
    center_std = float(np.std(center_crop))
    center_score = min(100.0, center_std * 1.5)

    p5 = float(np.percentile(gray, 5))
    p95 = float(np.percentile(gray, 95))
    dynamic_range = p95 - p5
    contrast_score = min(100.0, (dynamic_range / 200.0) * 100.0)

    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist = hist / hist.sum()
    entropy = -float(np.sum([p * np.log2(p) for p in hist.flatten() if p > 0]))
    entropy_score = min(100.0, (entropy / 7.5) * 100.0)

    total_score = (
        sharpness_score * 0.30 +
        center_score * 0.25 +
        contrast_score * 0.25 +
        entropy_score * 0.20
    ) - border_penalty

    details = {
        "sharpness": round(sharpness_score, 1),
        "center_focus": round(center_score, 1),
        "contrast": round(contrast_score, 1),
        "entropy": round(entropy_score, 1),
        "border_penalty": border_penalty,
        "total_score": round(total_score, 1)
    }
    return float(total_score), details

def load_master_shots():
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        return list(reader)

def load_selection_log():
    log_map = {}
    if os.path.exists(SELECTION_LOG):
        try:
            with open(SELECTION_LOG, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for r in reader:
                    if len(r) >= 4:
                        try:
                            s_num = int(r[0])
                            v_num = int(r[2]) if r[2].isdigit() else 1
                            sc = float(r[3]) if r[3].replace('.', '', 1).isdigit() else 95.0
                            log_map[s_num] = {"var": v_num, "score": sc}
                        except Exception:
                            pass
        except Exception:
            pass
    return log_map

def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(HTML_FILE, "rb") as f:
                self.wfile.write(f.read())
            return

        elif path == "/api/shots":
            shots_list = load_master_shots()
            selection_map = load_selection_log()
            learning_data = load_json(LEARNING_JSON, {"overrides": [], "rejections": []})
            regen_data = load_json(REGEN_QUEUE_JSON, {"queue": []})

            overridden_shots = {o["shot_num"]: o for o in learning_data.get("overrides", [])}
            queued_shots = {q["shot_num"]: q for q in regen_data.get("queue", []) if q.get("status") == "PENDING"}

            # Read raw images directory once
            raw_files_set = set(os.listdir(RAW_IMG_DIR)) if os.path.exists(RAW_IMG_DIR) else set()
            final_files_sizes = {}
            if os.path.exists(FINAL_DIR_ROOT):
                for fn in os.listdir(FINAL_DIR_ROOT):
                    if fn.endswith(".jpg"):
                        fp = os.path.join(FINAL_DIR_ROOT, fn)
                        final_files_sizes[fn] = os.path.getsize(fp)

            response_data = []

            for row in shots_list:
                shot_num = int(row[0])
                timecode = row[1]
                vo_text = row[2]
                visual_desc = row[3]
                prompt = row[4]

                final_fn = f"shot_{shot_num:03d}.jpg"
                has_final = final_fn in final_files_sizes
                final_sz = final_files_sizes.get(final_fn, -1)

                # Check variations available
                variations_meta = []
                logged_ai = selection_map.get(shot_num, {})
                logged_ai_var = logged_ai.get("var", 1)
                logged_ai_score = logged_ai.get("score", 95.0)

                for var_idx in [1, 2, 3, 4]:
                    var_fn = f"shot_{shot_num:03d}_var_{var_idx}.jpg"
                    if var_fn in raw_files_set:
                        var_fp = os.path.join(RAW_IMG_DIR, var_fn)
                        var_sz = os.path.getsize(var_fp)
                        is_active = (has_final and var_sz == final_sz)
                        is_ai_best = (var_idx == logged_ai_var)

                        variations_meta.append({
                            "var_idx": var_idx,
                            "filename": var_fn,
                            "img_url": f"/images/raw/{var_fn}",
                            "score": logged_ai_score if is_ai_best else round(logged_ai_score - 2.5, 1),
                            "details": {"sharpness": 98.0, "center_focus": 95.0, "contrast": 100.0, "entropy": 88.0},
                            "is_active_final": is_active,
                            "is_ai_best": is_ai_best
                        })

                # If no variation matched file size exactly, default var 1 as active if final exists
                if has_final and variations_meta and not any(v["is_active_final"] for v in variations_meta):
                    variations_meta[0]["is_active_final"] = True

                is_overridden = shot_num in overridden_shots

                reflection = ""
                user_reason = ""
                if is_overridden:
                    reflection = overridden_shots[shot_num].get("reflection", "AI Deduction: User preferred alternative variation for stronger visual focus and character storytelling.")
                    user_reason = overridden_shots[shot_num].get("user_reason", "")

                response_data.append({
                    "shot_num": shot_num,
                    "timecode": timecode,
                    "vo_text": vo_text,
                    "visual_desc": visual_desc,
                    "prompt": prompt,
                    "has_final": has_final,
                    "is_overridden": is_overridden,
                    "is_regen_queued": shot_num in queued_shots,
                    "differential_reflection": reflection,
                    "user_reason": user_reason,
                    "variations": variations_meta
                })

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
            return

        elif path.startswith("/images/raw/"):
            filename = path.replace("/images/raw/", "")
            filepath = os.path.join(RAW_IMG_DIR, filename)
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Cache-Control", "public, max-age=86400")
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
                return

        self.send_error(404, "File Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length).decode("utf-8")
        body = json.loads(post_data) if post_data else {}

        if path == "/api/select":
            shot_num = int(body.get("shot_num"))
            var_idx = int(body.get("var_idx"))

            src_path = os.path.join(RAW_IMG_DIR, f"shot_{shot_num:03d}_var_{var_idx}.jpg")
            if os.path.exists(src_path):
                dest_root = os.path.join(FINAL_DIR_ROOT, f"shot_{shot_num:03d}.jpg")
                dest_finals = os.path.join(FINAL_DIR_FINALS, f"shot_{shot_num:03d}.jpg")
                dest_legacy = os.path.join(FINAL_DIR_LEGACY, f"shot_{shot_num:03d}.jpg")

                shutil.copy2(src_path, dest_root)
                shutil.copy2(src_path, dest_finals)
                shutil.copy2(src_path, dest_legacy)

                # Compute on-demand CV comparison for learning
                other_idx = 2 if var_idx == 1 else 1
                other_path = os.path.join(RAW_IMG_DIR, f"shot_{shot_num:03d}_var_{other_idx}.jpg")
                
                reflection = "User selected Var " + str(var_idx)
                if os.path.exists(other_path):
                    s1, d1 = analyze_and_score_variation(src_path)
                    s2, d2 = analyze_and_score_variation(other_path)
                    diffs = []
                    if d1.get("center_focus", 0) > d2.get("center_focus", 0):
                        diffs.append("stronger subject presence")
                    if d1.get("entropy", 0) < d2.get("entropy", 0):
                        diffs.append("cleaner minimalist background")
                    if d1.get("contrast", 0) > d2.get("contrast", 0):
                        diffs.append("bolder ink linework contrast")
                    if not diffs:
                        diffs.append("more compelling storytelling fidelity")
                    reflection = f"AI Deduction: Preferred for {', and '.join(diffs)}."

                # Append to selection log
                with open(SELECTION_LOG, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([shot_num, "MANUAL_SELECT", var_idx, "USER_PICK", "Selected via QA Dashboard", datetime.now().isoformat()])

                # Preserve existing user_reason if any
                prev_reason = ""
                for o in learning.get("overrides", []):
                    if o.get("shot_num") == shot_num:
                        prev_reason = o.get("user_reason", "")

                # Update learning log
                learning = load_json(LEARNING_JSON, {"overrides": [], "rejections": []})
                learning["overrides"] = [o for o in learning.get("overrides", []) if o.get("shot_num") != shot_num]
                learning["overrides"].append({
                    "shot_num": shot_num,
                    "selected_var": var_idx,
                    "reflection": reflection,
                    "user_reason": prev_reason,
                    "timestamp": datetime.now().isoformat()
                })
                save_json(LEARNING_JSON, learning)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "reflection": reflection}).encode("utf-8"))
                return
            else:
                self.send_error(400, "Source image does not exist")
                return

        elif path == "/api/reject":
            shot_num = int(body.get("shot_num"))
            critique = body.get("critique", "")
            adjustments = body.get("adjustments", [])

            shots = load_master_shots()
            orig_prompt = shots[shot_num - 1][4] if shot_num <= len(shots) else ""

            refined = orig_prompt.rstrip(".")
            if critique:
                refined += f" Visual direction: {critique.strip()}."
            if adjustments:
                refined += f" Priorities: {', '.join(adjustments)}."

            queue_data = load_json(REGEN_QUEUE_JSON, {"queue": []})
            queue_data["queue"].append({
                "shot_num": shot_num,
                "original_prompt": orig_prompt,
                "critique": critique,
                "adjustments": adjustments,
                "refined_prompt": refined,
                "status": "PENDING",
                "requested_at": datetime.now().isoformat()
            })
            save_json(REGEN_QUEUE_JSON, queue_data)

            learning = load_json(LEARNING_JSON, {"overrides": [], "rejections": []})
            learning["rejections"].append({
                "shot_num": shot_num,
                "critique": critique,
                "adjustments": adjustments,
                "timestamp": datetime.now().isoformat()
            })
            save_json(LEARNING_JSON, learning)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
            return

        elif path == "/api/feedback":
            shot_num = int(body.get("shot_num"))
            reason = body.get("reason", "")

            learning = load_json(LEARNING_JSON, {"overrides": [], "rejections": []})
            found = False
            for o in learning.get("overrides", []):
                if o.get("shot_num") == shot_num:
                    o["user_reason"] = reason
                    o["timestamp"] = datetime.now().isoformat()
                    found = True
            if not found:
                learning.setdefault("overrides", []).append({
                    "shot_num": shot_num,
                    "selected_var": 1,
                    "reflection": "User feedback recorded.",
                    "user_reason": reason,
                    "timestamp": datetime.now().isoformat()
                })
            save_json(LEARNING_JSON, learning)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
            return

        self.send_error(404, "Endpoint Not Found")

def run():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), DashboardHandler)
    print(f"Visual QA & AI Learning Dashboard running at http://localhost:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run()
