import os
import re

exp_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(exp_dir, 'character_library.js'), 'r', encoding='utf-8') as f:
    c_lib = f.read()
    c_lib = re.sub(r"export\s+const\s+", "const ", c_lib)
    c_lib = re.sub(r"export\s+function\s+", "function ", c_lib)

c1 = f"""// --- MASTER CHARACTER SKELETAL RIG & FORWARD KINEMATICS ---
{c_lib}
function renderCharacter(options = {{}}) {{
  return renderMasterCharacter(options);
}}
"""

with open(os.path.join(exp_dir, 'agent2_scene.js'), 'r', encoding='utf-8') as f:
    c2 = f.read().replace('export function renderSceneEnvironment', 'function renderSceneEnvironment')

with open(os.path.join(exp_dir, 'orchestrator_engine.js'), 'r', encoding='utf-8') as f:
    c_orch = f.read()
    c_orch = re.sub(r"import\s+.*?;\n?", "", c_orch)
    c_orch = c_orch.replace('export const SPATIAL_ZONES', 'const SPATIAL_ZONES')
    c_orch = c_orch.replace('export function getQuadraticBezierPointAndTangent', 'function getQuadraticBezierPointAndTangent')
    c_orch = c_orch.replace('export const CHUNKED_SUBTITLES', 'const CHUNKED_SUBTITLES')
    c_orch = c_orch.replace('export function renderChunkedCaptions', 'function renderChunkedCaptions')

with open(os.path.join(exp_dir, 'agent5_continuity.js'), 'r', encoding='utf-8') as f:
    c5 = f.read()
    for exp in ['export function easeInOutCubic', 'export function easeOutBack', 'export function clamp', 'export function lerp', 'export function getContinuityState']:
        c5 = c5.replace(exp, exp.replace('export ', ''))

with open(os.path.join(exp_dir, 'scene2_scene5_assets.js'), 'r', encoding='utf-8') as f:
    c_scenes = f.read()
    c_scenes = re.sub(r"import\s+.*?;\n?", "", c_scenes)
    for exp in ['export function formatCurrency', 'export function renderScene2', 'export function renderScene3', 'export function renderScene4', 'export function renderScene5']:
        c_scenes = c_scenes.replace(exp, exp.replace('export ', ''))

with open(os.path.join(exp_dir, 'scene1_animator.js'), 'r', encoding='utf-8') as f:
    c_anim1 = f.read()
    c_anim1 = re.sub(r"import\s+.*?;\n?", "", c_anim1)
    c_anim1 = c_anim1.replace('export function computeScene1Frame', 'function computeScene1Frame')

with open(os.path.join(exp_dir, 'master_timeline_engine.js'), 'r', encoding='utf-8') as f:
    c_master = f.read()
    c_master = re.sub(r"import\s+.*?;\n?", "", c_master)
    c_master = c_master.replace('export function computeMasterFrame', 'function computeMasterFrame')

html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The $5 Daily Habit - Full 5-Scene Infographics Explainer</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800;900&family=Poppins:wght@600;700;800&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
    }}

    body {{
      background-color: #070a12;
      color: #f8fafc;
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 16px;
      overflow-x: hidden;
    }}

    header {{
      width: 100%;
      max-width: 1240px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }}

    .badge-title {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .pill-tag {{
      background: linear-gradient(135deg, #10b981, #047857);
      color: #ffffff;
      padding: 4px 14px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.8px;
      text-transform: uppercase;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }}

    .pill-scene {{
      background: #1e293b;
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.3);
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
    }}

    h1 {{
      font-size: 19px;
      font-weight: 800;
      color: #f1f5f9;
      letter-spacing: -0.3px;
    }}

    .status-text {{
      font-size: 13px;
      color: #94a3b8;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    /* 16:9 Cinema Viewport */
    #viewport-container {{
      position: relative;
      width: 100%;
      max-width: 1240px;
      aspect-ratio: 16 / 9;
      background: #020617;
      border-radius: 14px;
      overflow: hidden;
      box-shadow: 0 30px 80px -15px rgba(0, 0, 0, 0.85), 0 0 0 1px rgba(255, 255, 255, 0.08);
    }}

    #stage {{
      width: 100%;
      height: 100%;
      display: block;
    }}

    /* Controls Bar */
    #controls-container {{
      width: 100%;
      max-width: 1240px;
      margin-top: 12px;
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(14px);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      padding: 12px 20px;
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .btn {{
      background: linear-gradient(135deg, #2563eb, #1d4ed8);
      color: white;
      border: none;
      padding: 10px 22px;
      border-radius: 8px;
      font-weight: 800;
      font-size: 14px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.15s ease;
      box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
    }}

    .btn:hover {{
      background: linear-gradient(135deg, #1d4ed8, #1e40af);
      transform: translateY(-1px);
    }}

    .btn-secondary {{
      background: rgba(255, 255, 255, 0.08);
      color: #e2e8f0;
      box-shadow: none;
    }}

    .btn-secondary:hover {{
      background: rgba(255, 255, 255, 0.14);
    }}

    /* Timeline Slider */
    #timeline-slider {{
      flex: 1;
      accent-color: #10b981;
      height: 6px;
      border-radius: 3px;
      cursor: pointer;
    }}

    .time-indicator {{
      font-family: monospace;
      font-size: 14px;
      font-weight: 700;
      color: #38bdf8;
      min-width: 130px;
      text-align: right;
    }}

    .scene-badge {{
      background: rgba(16, 185, 129, 0.12);
      padding: 4px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-family: monospace;
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.25);
      font-weight: bold;
    }}
  </style>
</head>
<body>

  <header>
    <div class="badge-title">
      <span class="pill-tag">Infographics Master</span>
      <h1>The $5 Daily Habit (Director & Orchestrator Master Pipeline)</h1>
      <span id="active-scene-pill" class="pill-scene">Scene 1: The Hook</span>
    </div>
    <div class="status-text">
      Director Arc • Orchestrator Zones • 60fps Tangent Rocket
    </div>
  </header>

  <!-- Cinema Viewport -->
  <div id="viewport-container">
    <div id="stage"></div>
  </div>

  <!-- Audio Element -->
  <audio id="voiceover-audio" src="what-happens-if-you-take-five-.wav" preload="auto"></audio>

  <!-- Controls Bar -->
  <div id="controls-container">
    <button id="play-btn" class="btn">▶ Play</button>
    <button id="restart-btn" class="btn btn-secondary">↺ Restart</button>
    
    <input type="range" id="timeline-slider" min="0" max="26.85" step="0.01" value="0">
    
    <div class="time-indicator">
      <span id="current-time">0.00s</span> / <span>26.85s</span>
    </div>

    <div id="scene-indicator" class="scene-badge">
      SCENE 1 / 5
    </div>
  </div>

  <!-- MASTER SCRIPT BUNDLE (Zero-CORS standalone) -->
  <script>
    // --- 1. AGENT 1: CHARACTER POSE RIG ---
    {c1}

    // --- 2. AGENT 2: SCENE 1 ENVIRONMENT ---
    {c2}

    // --- 3. ORCHESTRATOR ENGINE (Zoning, Bezier Tangent, Chunked Captions) ---
    {c_orch}

    // --- 4. AGENT 5: CONTINUITY & 50% MIDPOINT TRANSITIONS ---
    {c5}

    // --- 5. SCENES 2 THROUGH 5 ASSETS (Monster, Badge, Tangent Rocket) ---
    {c_scenes}

    // --- 6. SCENE 1 ANIMATOR ---
    {c_anim1}

    // --- 7. MASTER TIMELINE ENGINE ---
    {c_master}

    // --- 8. MASTER UI CONTROLLER ---
    document.addEventListener('DOMContentLoaded', () => {{
      const stage = document.getElementById('stage');
      const audio = document.getElementById('voiceover-audio');
      const playBtn = document.getElementById('play-btn');
      const restartBtn = document.getElementById('restart-btn');
      const timelineSlider = document.getElementById('timeline-slider');
      const currentTimeDisplay = document.getElementById('current-time');
      const activeScenePill = document.getElementById('active-scene-pill');
      const sceneIndicator = document.getElementById('scene-indicator');

      const TOTAL_DURATION = 26.85;
      let isPlaying = false;
      let animFrameId = null;
      let fallbackTime = 0.0;
      let lastTimestamp = 0;

      function getSceneTitle(t) {{
        if (t < 4.40) return {{ name: 'Scene 1: The Hook', num: '1 / 5' }};
        if (t < 5.10) return {{ name: 'Transition: Studio ➔ Bedroom (50% Midpoint)', num: 'T 1➔2' }};
        if (t < 9.30) return {{ name: 'Scene 2: The Mattress Stash', num: '2 / 5' }};
        if (t < 10.10) return {{ name: 'Transition: Punch-in Freeze', num: 'T 2➔3' }};
        if (t < 15.70) return {{ name: 'Scene 3: The Inflation Threat', num: '3 / 5' }};
        if (t < 16.50) return {{ name: 'Transition: Emerald Wipe (50% Midpoint)', num: 'T 3➔4' }};
        if (t < 24.80) return {{ name: 'Scene 4: S&P 500 Rocket Engine', num: '4 / 5' }};
        if (t < 25.35) return {{ name: 'Transition: Climax Starburst', num: 'T 4➔5' }};
        return {{ name: 'Scene 5: START TODAY', num: '5 / 5' }};
      }}

      // Global hook for Diagnostic Auditor
      window.seekTo = function(seconds) {{
        const t = Math.min(Math.max(seconds, 0), TOTAL_DURATION);
        timelineSlider.value = t;
        currentTimeDisplay.textContent = t.toFixed(2) + 's';
        const sc = getSceneTitle(t);
        activeScenePill.textContent = sc.name;
        sceneIndicator.textContent = 'SCENE ' + sc.num;
        stage.innerHTML = computeMasterFrame(t);
        fallbackTime = t;
      }};

      function update(now) {{
        if (isPlaying) {{
          let t = 0;
          if (!audio.paused && !isNaN(audio.currentTime) && audio.currentTime > 0) {{
            t = audio.currentTime;
          }} else {{
            if (!lastTimestamp) lastTimestamp = now;
            const dt = (now - lastTimestamp) / 1000;
            fallbackTime += dt;
            lastTimestamp = now;
            t = fallbackTime;
          }}

          if (t >= TOTAL_DURATION) {{
            try {{ audio.pause(); }} catch(e) {{}}
            audio.currentTime = 0;
            fallbackTime = 0;
            isPlaying = false;
            playBtn.innerHTML = '▶ Play';
            window.seekTo(0);
            return;
          }}

          timelineSlider.value = t;
          currentTimeDisplay.textContent = t.toFixed(2) + 's';
          const sc = getSceneTitle(t);
          activeScenePill.textContent = sc.name;
          sceneIndicator.textContent = 'SCENE ' + sc.num;
          stage.innerHTML = computeMasterFrame(t);

          animFrameId = requestAnimationFrame(update);
        }}
      }}

      function togglePlay() {{
        if (isPlaying) {{
          try {{ audio.pause(); }} catch(e) {{}}
          isPlaying = false;
          playBtn.innerHTML = '▶ Play';
          cancelAnimationFrame(animFrameId);
        }} else {{
          if (timelineSlider.value >= TOTAL_DURATION) {{
            window.seekTo(0);
          }}
          fallbackTime = parseFloat(timelineSlider.value) || 0;
          lastTimestamp = performance.now();
          audio.currentTime = fallbackTime;

          const playPromise = audio.play();
          if (playPromise !== undefined) {{
            playPromise.then(() => {{
              isPlaying = true;
              playBtn.innerHTML = '❚❚ Pause';
              animFrameId = requestAnimationFrame(update);
            }}).catch(err => {{
              isPlaying = true;
              playBtn.innerHTML = '❚❚ Pause';
              animFrameId = requestAnimationFrame(update);
            }});
          }} else {{
            isPlaying = true;
            playBtn.innerHTML = '❚❚ Pause';
            animFrameId = requestAnimationFrame(update);
          }}
        }}
      }}

      playBtn.addEventListener('click', togglePlay);

      restartBtn.addEventListener('click', () => {{
        try {{ audio.pause(); }} catch(e) {{}}
        audio.currentTime = 0;
        fallbackTime = 0;
        window.seekTo(0);
        if (isPlaying) {{
          lastTimestamp = performance.now();
          audio.play().catch(() => {{}});
        }}
      }});

      timelineSlider.addEventListener('input', (e) => {{
        const val = parseFloat(e.target.value);
        audio.currentTime = val;
        fallbackTime = val;
        window.seekTo(val);
      }});

      window.addEventListener('keydown', (e) => {{
        if (e.code === 'Space') {{
          e.preventDefault();
          togglePlay();
        }}
      }});

      window.seekTo(0);
    }});
  </script>
</body>
</html>'''

out_path = os.path.join(exp_dir, 'full_player.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html_template)
print(f'Successfully compiled {out_path} ({len(html_template)} bytes)')
