/**
 * ORCHESTRATOR AGENT: TECHNICAL CONTRACTS, SPATIAL ZONES & DATA BUS
 * 
 * Enforces:
 * 1. Screen Real Estate Zoning (Header 0-240, Action 240-850, Caption 860-1080)
 * 2. Calculus Tangent Engine for curve-following motion (Rocket along S&P 500 curve)
 * 3. 18 Non-overlapping Chunked Subtitles (zero double-rendering, zero bounds overflow)
 * 4. 50% Midpoint Scene Switching Protocol for seamless transitions
 */

// 1. SPATIAL ZONING CONTRACTS
export const SPATIAL_ZONES = {
  HEADER:  { yMin: 0,   yMax: 240, label: "Hero Badges & Counters" },
  ACTION:  { yMin: 240, yMax: 850, label: "Character & Kinetic Props" },
  CAPTION: { yMin: 860, yMax: 1080, label: "Chunked Subtitles" }
};

// 2. CALCULUS TANGENT ENGINE FOR BEZIER CURVES
// Quadratic Bezier: B(p) = (1-p)^2 * P0 + 2(1-p)p * P1 + p^2 * P2
export function getQuadraticBezierPointAndTangent(p0, p1, p2, p) {
  const t = Math.min(Math.max(p, 0), 1);
  
  // Position B(t)
  const x = Math.pow(1 - t, 2) * p0.x + 2 * (1 - t) * t * p1.x + Math.pow(t, 2) * p2.x;
  const y = Math.pow(1 - t, 2) * p0.y + 2 * (1 - t) * t * p1.y + Math.pow(t, 2) * p2.y;

  // First Derivative B'(t) = 2(1-t)(P1 - P0) + 2t(P2 - P1)
  const dx = 2 * (1 - t) * (p1.x - p0.x) + 2 * t * (p2.x - p1.x);
  const dy = 2 * (1 - t) * (p1.y - p0.y) + 2 * t * (p2.y - p1.y);

  // Tangent angle in degrees. Adding 90 deg because default rocket points UP (negative Y)
  const angleDeg = (Math.atan2(dy, dx) * 180 / Math.PI) + 90;

  return { x, y, dx, dy, angleDeg };
}

// 3. 18 RHYTHMIC CHUNKED SUBTITLES (3 to 5 words each - ZERO OVERFLOW)
export const CHUNKED_SUBTITLES = [
  // Scene 1: The Hook (0.00s - 4.75s)
  {
    chunkId: 1, start: 0.00, end: 1.05,
    words: [
      { word: "What", start: 0.00, end: 0.25 },
      { word: "happens", start: 0.25, end: 0.65 },
      { word: "if", start: 0.65, end: 0.85 },
      { word: "you", start: 0.85, end: 1.05 }
    ]
  },
  {
    chunkId: 2, start: 1.05, end: 2.15,
    words: [
      { word: "take", start: 1.05, end: 1.35 },
      { word: "five", start: 1.35, end: 1.70 },
      { word: "dollars", start: 1.70, end: 2.15 }
    ]
  },
  {
    chunkId: 3, start: 2.15, end: 3.45,
    words: [
      { word: "every", start: 2.15, end: 2.55 },
      { word: "single", start: 2.55, end: 2.95 },
      { word: "day", start: 2.95, end: 3.45 }
    ]
  },
  {
    chunkId: 4, start: 3.45, end: 4.75,
    words: [
      { word: "and", start: 3.45, end: 3.70 },
      { word: "simply", start: 3.70, end: 4.05 },
      { word: "never", start: 4.05, end: 4.35 },
      { word: "spend", start: 4.35, end: 4.60 },
      { word: "it?", start: 4.60, end: 4.75 }
    ]
  },

  // Scene 2: The Mattress Stash (4.75s - 9.70s)
  {
    chunkId: 5, start: 5.30, end: 6.95,
    words: [
      { word: "Tuck", start: 5.30, end: 5.60 },
      { word: "it", start: 5.60, end: 5.80 },
      { word: "under", start: 5.80, end: 6.10 },
      { word: "your", start: 6.10, end: 6.35 },
      { word: "mattress,", start: 6.35, end: 6.95 }
    ]
  },
  {
    chunkId: 6, start: 6.95, end: 8.35,
    words: [
      { word: "and", start: 6.95, end: 7.20 },
      { word: "in", start: 7.20, end: 7.45 },
      { word: "thirty", start: 7.45, end: 7.85 },
      { word: "years,", start: 7.85, end: 8.35 }
    ]
  },
  {
    chunkId: 7, start: 8.35, end: 9.70,
    words: [
      { word: "you'll", start: 8.35, end: 8.65 },
      { word: "have", start: 8.65, end: 8.90 },
      { word: "fifty-four", start: 8.90, end: 9.35 },
      { word: "thousand", start: 9.35, end: 9.70 }
    ]
  },

  // Scene 3: The Inflation Threat (9.70s - 16.10s)
  {
    chunkId: 8, start: 9.70, end: 11.45,
    words: [
      { word: "dollars.", start: 9.70, end: 10.05 },
      { word: "Sounds", start: 10.05, end: 10.45 },
      { word: "decent,", start: 10.45, end: 11.00 },
      { word: "right?", start: 11.00, end: 11.45 }
    ]
  },
  {
    chunkId: 9, start: 12.04, end: 13.00,
    words: [
      { word: "Wrong.", start: 12.04, end: 13.00 }
    ]
  },
  {
    chunkId: 10, start: 13.10, end: 14.45,
    words: [
      { word: "Inflation", start: 13.10, end: 13.65 },
      { word: "quietly", start: 13.65, end: 14.10 },
      { word: "eats", start: 14.10, end: 14.45 }
    ]
  },
  {
    chunkId: 11, start: 14.45, end: 16.10,
    words: [
      { word: "half", start: 14.45, end: 14.75 },
      { word: "of", start: 14.75, end: 14.95 },
      { word: "that", start: 14.95, end: 15.20 },
      { word: "buying", start: 15.20, end: 15.65 },
      { word: "power.", start: 15.65, end: 16.10 }
    ]
  },

  // Scene 4: S&P 500 Rocket Engine (16.10s - 25.07s)
  {
    chunkId: 12, start: 16.50, end: 18.05,
    words: [
      { word: "But", start: 16.50, end: 16.75 },
      { word: "put", start: 16.75, end: 17.00 },
      { word: "that", start: 17.00, end: 17.25 },
      { word: "exact", start: 17.25, end: 17.65 },
      { word: "same", start: 17.65, end: 18.05 }
    ]
  },
  {
    chunkId: 13, start: 18.05, end: 19.30,
    words: [
      { word: "five", start: 18.05, end: 18.40 },
      { word: "dollars", start: 18.40, end: 18.80 },
      { word: "a", start: 18.80, end: 18.95 },
      { word: "day", start: 18.95, end: 19.30 }
    ]
  },
  {
    chunkId: 14, start: 19.30, end: 20.65,
    words: [
      { word: "into", start: 19.30, end: 19.60 },
      { word: "the", start: 19.60, end: 19.80 },
      { word: "S&P", start: 19.80, end: 20.15 },
      { word: "500,", start: 20.15, end: 20.65 }
    ]
  },
  {
    chunkId: 15, start: 20.95, end: 22.65,
    words: [
      { word: "and", start: 20.95, end: 21.20 },
      { word: "compound", start: 21.20, end: 21.75 },
      { word: "interest", start: 21.75, end: 22.25 },
      { word: "turns", start: 22.25, end: 22.65 }
    ]
  },
  {
    chunkId: 16, start: 22.65, end: 23.75,
    words: [
      { word: "it", start: 22.65, end: 22.85 },
      { word: "into", start: 22.85, end: 23.15 },
      { word: "over", start: 23.15, end: 23.45 },
      { word: "three", start: 23.45, end: 23.75 }
    ]
  },
  {
    chunkId: 17, start: 23.75, end: 25.07,
    words: [
      { word: "hundred", start: 23.75, end: 24.15 },
      { word: "thirty", start: 24.15, end: 24.65 },
      { word: "thousand", start: 24.65, end: 24.85 },
      { word: "dollars.", start: 24.85, end: 25.07 }
    ]
  },

  // Scene 5: Climax CTA (25.07s - 26.85s)
  {
    chunkId: 18, start: 25.40, end: 26.85,
    words: [
      { word: "Start", start: 25.65, end: 26.15 },
      { word: "today.", start: 26.15, end: 26.85 }
    ]
  }
];

export function renderChunkedCaptions(currentTime) {
  const t = currentTime;
  const currentChunk = CHUNKED_SUBTITLES.find(c => t >= c.start && t <= c.end);
  if (!currentChunk) return '';

  const words = currentChunk.words;
  const activeWordIdx = words.findIndex(w => t >= w.start && t <= w.end);

  return `
    <g id="master_chunked_captions" transform="translate(960, 960)">
      <!-- Auto-fitting pill (Max width 820px, fits comfortably in 1920x1080) -->
      <rect x="-410" y="-45" width="820" height="90" rx="45" fill="#020617" opacity="0.88" stroke="#1e293b" stroke-width="2.5"/>
      <text x="0" y="14" font-family="'Montserrat', 'Arial Black', sans-serif" font-size="34" font-weight="900" text-anchor="middle" letter-spacing="1">
        ${words.map((w, idx) => {
          const isCurrent = idx === activeWordIdx;
          const isPassed = t > w.end;
          const fill = isCurrent ? "#facc15" : (isPassed ? "#ffffff" : "#64748b");
          const size = isCurrent ? "40" : "34";
          return `<tspan fill="${fill}" font-size="${size}" ${isCurrent ? 'font-weight="900"' : ''}>${w.word} </tspan>`;
        }).join('')}
      </text>
    </g>
  `;
}
