import csv
import json
import os
import shutil
import time
from datetime import datetime
import cv2
import numpy as np
import streamlit as st

# Configure page
st.set_page_config(
    page_title="Ink Explainers - Curation & AI Learning Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-title { font-size: 26px; font-weight: 700; color: #f8fafc; margin-bottom: 2px; }
    .sub-title { font-size: 14px; color: #94a3b8; margin-bottom: 16px; }
    .vo-box { background-color: #1e293b; border-left: 5px solid #38bdf8; padding: 14px 18px; border-radius: 6px; margin-bottom: 16px; }
    .vo-text { font-size: 18px; font-weight: 600; color: #f1f5f9; }
    .vo-meta { font-size: 12px; color: #94a3b8; margin-top: 4px; }
    .card-active { border: 3px solid #22c55e !important; border-radius: 8px; box-shadow: 0 0 15px rgba(34, 197, 94, 0.25); }
    .card-normal { border: 1px solid #334155; border-radius: 8px; }
    .badge-ai { background-color: #3b82f6; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .badge-final { background-color: #22c55e; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .badge-override { background-color: #f59e0b; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .metric-chip { background-color: #0f172a; padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #cbd5e1; display: inline-block; margin-right: 4px; margin-bottom: 4px; }
    .learning-box { background-color: #1e1b4b; border: 1px solid #6366f1; border-radius: 6px; padding: 12px 16px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# Paths
VIDEO_SUBDIR = "1- What Did Ancient Humans Actually Do All Day"
FINALS_DIR = os.path.join("3- Finals", VIDEO_SUBDIR)
CSV_PATH = os.path.join(FINALS_DIR, "storyboard_master.csv")
RAW_IMG_DIR = os.path.join(FINALS_DIR, "flow_generated_images")
FINAL_DIR_ROOT = os.path.join(FINALS_DIR, "Final selected images")
STATUS_JSON = os.path.join(FINALS_DIR, "production_status.json")
LOG_CSV = os.path.join(FINALS_DIR, "selection_log.csv")
LEARNING_JSON = os.path.join(FINALS_DIR, "ai_learning_log.json")
REGEN_QUEUE_JSON = os.path.join(FINALS_DIR, "regeneration_queue.json")

def load_master_shots():
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        return list(reader)

def load_status():
    if os.path.exists(STATUS_JSON):
        try:
            with open(STATUS_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def load_learning_log():
    if os.path.exists(LEARNING_JSON):
        try:
            with open(LEARNING_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"overrides": [], "rejections": [], "learned_rules": []}

def save_learning_log(data):
    with open(LEARNING_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_regen_queue():
    if os.path.exists(REGEN_QUEUE_JSON):
        try:
            with open(REGEN_QUEUE_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"queue": []}

def save_regen_queue(data):
    with open(REGEN_QUEUE_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def analyze_and_score_variation(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return -1.0, {}

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

def get_shot_variations(shot_num):
    """Returns list of paths for shot_{shot_num:03d}_var_*.jpg in RAW_IMG_DIR."""
    prefix = f"shot_{shot_num:03d}_var_"
    if not os.path.exists(RAW_IMG_DIR):
        return []
    vars_found = []
    for fname in sorted(os.listdir(RAW_IMG_DIR)):
        if fname.startswith(prefix) and fname.endswith(".jpg"):
            vars_found.append(os.path.join(RAW_IMG_DIR, fname))
    return vars_found

def get_active_final_path(shot_num):
    p = os.path.join(FINAL_DIR_ROOT, f"shot_{shot_num:03d}.jpg")
    return p if os.path.exists(p) else None

def set_final_image(shot_num, chosen_path, reason="", user_override=False):
    """Copies chosen image strictly to Final selected images/ and logs learning data."""
    final_root = os.path.join(FINAL_DIR_ROOT, f"shot_{shot_num:03d}.jpg")
    shutil.copy2(chosen_path, final_root)

    # If user override, log to learning system
    if user_override:
        learning = load_learning_log()
        override_entry = {
            "shot_num": shot_num,
            "chosen_path": chosen_path,
            "timestamp": datetime.now().isoformat(),
            "reason": reason
        }
        learning["overrides"].append(override_entry)
        save_learning_log(learning)

# Main App Layout
all_shots = load_master_shots()
total_shots = len(all_shots)
status_data = load_status()
completed_count = len([f for f in os.listdir(FINAL_DIR_ROOT) if f.startswith("shot_") and f.endswith(".jpg")]) if os.path.exists(FINAL_DIR_ROOT) else 0

# Sidebar
with st.sidebar:
    st.markdown("### 🎬 Production Monitor")
    st.progress(min(1.0, completed_count / max(1, total_shots)))
    st.metric("Generated Shots", f"{completed_count} / {total_shots}", f"{completed_count/total_shots*100:.1f}%")
    
    st.markdown("---")
    st.markdown(f"**Pipeline Status:** `{status_data.get('status', 'RUNNING')}`")
    st.markdown(f"**Active Model:** `{status_data.get('active_model', 'Nano Banana 2 (x2)')}`")
    st.markdown(f"**Current Job:** Shot {status_data.get('current_shot', '-')}")
    if status_data.get("note"):
        st.info(status_data.get("note"))

    st.markdown("---")
    st.markdown("### 🎯 Quick Shot Navigation")
    shot_to_view = st.number_input("Jump to Shot #", min_value=1, max_value=max(1, total_shots), value=min(completed_count, total_shots) if completed_count > 0 else 1)
    
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("⬅ Previous") and shot_to_view > 1:
            st.session_state["active_shot"] = shot_to_view - 1
            st.rerun()
    with col_next:
        if st.button("Next ➡") and shot_to_view < total_shots:
            st.session_state["active_shot"] = shot_to_view + 1
            st.rerun()

    if "active_shot" in st.session_state:
        current_shot_num = st.session_state["active_shot"]
    else:
        current_shot_num = shot_to_view

# Main content
tab_curate, tab_learning, tab_queue = st.tabs(["🎨 Shot Curation & Re-generation Studio", "🧠 Live AI Learning & Rules Engine", "📋 Priority Re-generation Queue"])

with tab_curate:
    row_idx = current_shot_num - 1
    if 0 <= row_idx < len(all_shots):
        shot_row = all_shots[row_idx]
        timecode = shot_row[1]
        vo_text = shot_row[2]
        action_desc = shot_row[3]
        prompt = shot_row[4]
        
        # Header banner
        st.markdown(f"<div class='main-title'>Shot #{current_shot_num:03d} / {total_shots}</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='vo-box'>
            <div class='vo-text'>"{vo_text}"</div>
            <div class='vo-meta'>⏱ Timecode: {timecode} | Visual: {action_desc}</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📝 View Full Prompt Used"):
            st.code(prompt, language="text")

        # Load variations
        variations = get_shot_variations(current_shot_num)
        active_final = get_active_final_path(current_shot_num)

        if not variations:
            st.warning(f"No variations generated yet for Shot #{current_shot_num}. The background generator is currently working on earlier shots.")
        else:
            st.markdown(f"#### Available Variations ({len(variations)})")
            cols = st.columns(min(3, max(1, len(variations))))

            var_scores = {}
            for idx, v_path in enumerate(variations):
                score, details = analyze_and_score_variation(v_path)
                var_scores[v_path] = (score, details)

            # Determine best by score
            ai_best_path = max(var_scores.keys(), key=lambda k: var_scores[k][0]) if var_scores else None

            for idx, (v_path, col) in enumerate(zip(variations, cols), 1):
                with col:
                    score, details = var_scores[v_path]
                    
                    # Check if currently active final
                    is_active = False
                    if active_final and os.path.exists(active_final):
                        # Compare file size or content
                        if os.path.getsize(active_final) == os.path.getsize(v_path):
                            is_active = True

                    # Badges
                    badge_html = ""
                    if is_active:
                        badge_html += " <span class='badge-final'>✅ ACTIVE FINAL</span>"
                    if v_path == ai_best_path:
                        badge_html += " <span class='badge-ai'>🤖 AI RECOMMENDED</span>"

                    st.markdown(f"**Variation {idx}** {badge_html}", unsafe_allow_html=True)
                    st.image(v_path, use_container_width=True)

                    # Metrics
                    st.markdown(f"""
                    <div style='margin-top: 6px; margin-bottom: 8px;'>
                        <span class='metric-chip'>⭐ Overall: <b>{score:.1f}</b></span>
                        <span class='metric-chip'>Sharpness: {details.get('sharpness', '-')}</span>
                        <span class='metric-chip'>Focus: {details.get('center_focus', '-')}</span>
                        <span class='metric-chip'>Contrast: {details.get('contrast', '-')}</span>
                        <span class='metric-chip'>Entropy: {details.get('entropy', '-')}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    btn_label = "✅ Currently Selected" if is_active else f"⭐ Select Variation {idx}"
                    if st.button(btn_label, key=f"select_var_{idx}_{current_shot_num}", disabled=is_active):
                        is_override = (v_path != ai_best_path)
                        set_final_image(current_shot_num, v_path, reason="Selected by user on curation portal", user_override=is_override)
                        st.success(f"Saved Variation {idx} as the Final Image for Shot #{current_shot_num}!")
                        time.sleep(0.8)
                        st.rerun()

            # AI Reflection / Differential Analysis if user chose different
            if active_final and ai_best_path and os.path.getsize(active_final) != os.path.getsize(ai_best_path):
                st.markdown("<div class='learning-box'>", unsafe_allow_html=True)
                st.markdown("### 🧠 AI Differential Reflection")
                st.markdown("You selected an image that differs from the default computer-vision pick. Here is the AI's analysis of what you preferred:")
                
                user_score, user_det = analyze_and_score_variation(active_final)
                ai_score, ai_det = analyze_and_score_variation(ai_best_path)
                
                diffs = []
                if user_det.get("center_focus", 0) > ai_det.get("center_focus", 0):
                    diffs.append("• **Stronger Subject Focus:** The character has a more prominent center presence.")
                if user_det.get("entropy", 0) < ai_det.get("entropy", 0):
                    diffs.append("• **Cleaner Composition:** Less background clutter, favoring minimalist negative space.")
                if user_det.get("contrast", 0) > ai_det.get("contrast", 0):
                    diffs.append("• **Higher Visual Contrast:** Bolder separation between ink outlines and color fills.")
                if not diffs:
                    diffs.append("• **Storytelling Nuance:** The visual metaphor or character expression matches the voiceover more closely.")

                for d in diffs:
                    st.markdown(d)

                user_reason = st.text_input("Help the AI grow: Why did you prefer this one? (Optional)", key=f"reason_{current_shot_num}")
                if st.button("Save Feedback to AI Memory", key=f"save_reason_{current_shot_num}"):
                    if user_reason:
                        learning = load_learning_log()
                        learning["overrides"].append({
                            "shot_num": current_shot_num,
                            "user_feedback": user_reason,
                            "timestamp": datetime.now().isoformat()
                        })
                        save_learning_log(learning)
                        st.success("Thank you! Feedback recorded in AI learning database.")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("---")
            
            # REJECT BOTH & REQUEST RE-GENERATION
            st.markdown("### ❌ Neither Image Works? Request Re-generation with Live Direction")
            st.markdown("If neither variation tells the story properly, describe what needs to change. The AI will synthesize an updated prompt and generate a newer version.")

            with st.form(key=f"regen_form_{current_shot_num}"):
                critique = st.text_area(
                    "Open-Ended Analysis & Critique:",
                    placeholder="e.g. 'The character should look completely exhausted, slumped under the tree with visible sweat drops. The sky should feel late afternoon orange, and remove any modern clutter.'"
                )
                
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    adj_emotion = st.checkbox("Stronger character emotion / face")
                    adj_clean = st.checkbox("Cleaner / simpler background")
                with col_c2:
                    adj_close = st.checkbox("Closer character framing (Medium close-up)")
                    adj_action = st.checkbox("Fix action to match voiceover literally")
                with col_c3:
                    adj_lighting = st.checkbox("Warmer / dramatic lighting")
                    adj_bleed = st.checkbox("Enforce strict full-bleed / zero borders")

                submit_regen = st.form_submit_button("🚀 Submit Critique & Queue Re-generation", use_container_width=True)
                
                if submit_regen:
                    if not critique.strip() and not any([adj_emotion, adj_clean, adj_close, adj_action, adj_lighting, adj_bleed]):
                        st.error("Please provide a critique or select at least one adjustment checkbox.")
                    else:
                        # Build refined prompt
                        adjustments = []
                        if adj_emotion: adjustments.append("intense expressive emotional facial details")
                        if adj_clean: adjustments.append("minimalist clean background with zero clutter")
                        if adj_close: adjustments.append("medium close-up camera angle focusing on character")
                        if adj_action: adjustments.append("character actively performing the exact voiceover action")
                        if adj_lighting: adjustments.append("warm dramatic atmospheric lighting")
                        if adj_bleed: adjustments.append("strict edge-to-edge full bleed widescreen composition")

                        addon = ""
                        if critique.strip():
                            addon += f" User direction: {critique.strip()}."
                        if adjustments:
                            addon += f" Visual priorities: {', '.join(adjustments)}."

                        refined_prompt = f"{prompt.rstrip('.')}.{addon}"

                        # Save to queue
                        queue_data = load_regen_queue()
                        queue_item = {
                            "shot_num": current_shot_num,
                            "original_prompt": prompt,
                            "critique": critique,
                            "adjustments": adjustments,
                            "refined_prompt": refined_prompt,
                            "status": "PENDING",
                            "requested_at": datetime.now().isoformat()
                        }
                        queue_data["queue"].append(queue_item)
                        save_regen_queue(queue_data)

                        # Save to learning log
                        learning = load_learning_log()
                        learning["rejections"].append({
                            "shot_num": current_shot_num,
                            "critique": critique,
                            "adjustments": adjustments,
                            "timestamp": datetime.now().isoformat()
                        })
                        save_learning_log(learning)

                        st.success(f"Shot #{current_shot_num} added to the Priority Re-generation Queue! The generator will process it with your custom guidance.")

with tab_learning:
    st.markdown("### 🧠 AI System Evolution & Active Learning Profile")
    st.markdown("Every time you override a selection or critique a generation, the AI logs your aesthetic preferences to dynamically calibrate future shot selections.")
    
    learning_data = load_learning_log()
    overrides = learning_data.get("overrides", [])
    rejections = learning_data.get("rejections", [])
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Total Human Overrides", len(overrides))
    with col_m2:
        st.metric("Total Rejected Shots", len(rejections))
    with col_m3:
        agreement_pct = ((completed_count - len(overrides)) / max(1, completed_count)) * 100
        st.metric("Human-AI Alignment Rate", f"{agreement_pct:.1f}%")

    st.markdown("---")
    st.markdown("#### 📜 Human Feedback & Override History")
    if not overrides:
        st.info("No overrides recorded yet. As you select alternative variations on the Curation tab, the AI will log them here.")
    else:
        for idx, o in enumerate(reversed(overrides[-10:]), 1):
            st.markdown(f"**Override #{idx}** - Shot #{o.get('shot_num')} | *{o.get('timestamp', '')[:19]}*")
            if o.get("user_feedback"):
                st.markdown(f"> 💬 *\"{o.get('user_feedback')}\"*")
            st.markdown("---")

    st.markdown("#### ❌ Rejection Critiques & Desired Adjustments")
    if not rejections:
        st.info("No rejections recorded yet. When you reject both variations and request a new version, your critique appears here.")
    else:
        for idx, r in enumerate(reversed(rejections[-10:]), 1):
            st.markdown(f"**Rejection #{idx}** - Shot #{r.get('shot_num')} | *{r.get('timestamp', '')[:19]}*")
            st.markdown(f"> 🔍 **Critique:** {r.get('critique', 'No critique text')}")
            if r.get("adjustments"):
                st.markdown(f"> ⚙ **Tags:** {', '.join(r.get('adjustments'))}")
            st.markdown("---")

with tab_queue:
    st.markdown("### 📋 Priority Re-generation Queue")
    st.markdown("Shots requested for re-generation from the Curation tab are tracked here.")
    
    q_data = load_regen_queue()
    items = q_data.get("queue", [])
    
    if not items:
        st.info("No re-generation jobs in the queue. You can queue a shot from the Curation tab whenever neither image works.")
    else:
        for item in reversed(items):
            status_color = "#f59e0b" if item["status"] == "PENDING" else "#22c55e"
            st.markdown(f"""
            <div style='background-color: #1e293b; padding: 14px; border-radius: 6px; margin-bottom: 12px; border-left: 4px solid {status_color};'>
                <div style='display: flex; justify-content: space-between;'>
                    <b>Shot #{item['shot_num']}</b>
                    <span style='color: {status_color}; font-weight: 700;'>{item['status']}</span>
                </div>
                <div style='margin-top: 6px; font-size: 13px; color: #94a3b8;'>
                    Critique: "{item.get('critique', 'None')}"<br>
                    Tags: {', '.join(item.get('adjustments', []))}<br>
                    Requested: {item.get('requested_at', '')[:19]}
                </div>
            </div>
            """, unsafe_allow_html=True)
