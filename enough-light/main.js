// Enough Light — a Watercolor Brush film. Everything is a pure function of t (engine.js holds the brush).
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
window.DUR = 30;
const BPM = 72, BEAT = 60 / BPM, BAR = 4 * BEAT;          // 0.833 s · 3.333 s · 9 bars
const bar = (b, beat = 1) => (b - 1) * BAR + (beat - 1) * BEAT;

// ---------- timeline (one place for every cue) ----------
const T = {
  write1: [0.4, 2.2],                    // "Too heavy today."
  paint: { sky: [5.6, 6.9], bld: [6.2, 7.7], gnd: [6.8, 8.0], step: [7.5, 8.3], lamp: [7.9, 8.7], base: [8.3, 10.0], arms: [9.8, 10.6] },
  fold: [11.3, 12.4],                    // arms resting → hands folded
  goldIn: bar(4, 3) + 0.25,              // 11.92: the first point of gold
  bloom: bar(5, 2),                      // 14.17: gold blooms between her hands
  spread: [bar(6), 22.6],                // 16.67 → 22.6: the warm wash crosses the sheet
  burst: bar(7),                         // 20.0: raindrops become blossoms
  stand: [bar(8) - 0.3, bar(8) + 1.2],   // 23.0 → 24.5: she stands
  sun: [22.4, 24.2],
  erase1: [26.3, 27.0],
  write2: [bar(9), bar(9) + 1.5],        // 26.67 → 28.17: "Lighter now."
  lift: [28.3, 29.3],                    // the last stroke, left unfinished
};
const VO = [
  { id: 'v1', t: 1.0, d: 3.005, text: 'Some days, the weight is too heavy to carry alone.' },
  { id: 'v2', t: 6.4, d: 2.824, text: 'So she stopped, closed her eyes, and prayed.' },
  { id: 'v3', t: 11.8, d: 3.274, text: 'Not for everything. Just enough light for the next step.' },
  { id: 'v4', t: 17.2, d: 2.347, text: 'And slowly, something in her softened.' },
  { id: 'v5', t: 23.6, d: 3.435, text: 'The rain was still falling. But she was smiling in the light.' },
];
const SUBS = VO.map(v => ({ t0: v.t, t1: v.t + Math.max(1.8, v.d + 0.6), text: v.text }));

// ---------- palettes: cold opening, warm ending; one accent ----------
const COLD = { sky: '#a9b6bf', sky2: '#bfc8cd', bld: '#a3adb4', bld2: '#8d99a2', gnd: '#7d8a93', gnd2: '#6b7781', step: '#959da2', stepD: '#6f777d',
  coat: '#5d6f80', coatD: '#46566a', skin: '#dcc6b3', skinD: '#b89d8a', hair: '#3e3934', trou: '#56616b', lamp: '#4b5056', glow: '#c8ccc0' };
const WARM = { sky: '#f3d9b0', sky2: '#f7e6c6', bld: '#e6c49d', bld2: '#d3ab84', gnd: '#c9a27e', gnd2: '#b58d6a', step: '#dcb995', stepD: '#b48d6c',
  coat: '#b0705e', coatD: '#8a5548', skin: '#f0caa8', skinD: '#d19f80', hair: '#5a3d2e', trou: '#7c5b4d', lamp: '#6a5040', glow: '#efc27a' };
const GOLD = '#e0a53a', PINK = '#e89a8c', RAIN = '#7f97a8', NOTE1 = '#4f6475', NOTE2 = '#6b4a32';

// ---------- world layout (world = the wide shot, 1920×1080) ----------
const STEP_Y = 772, FIG = { x: 1040, y: STEP_Y, s: 1.35 }, STAND = { x: 1020, y: STEP_Y, s: 1.35 };
const HANDS = [FIG.x - 58 * FIG.s, FIG.y - 112 * FIG.s];   // where the light begins
const NOTE = { x: 1250, y: 300, size: 64 }, SUN = [800, 215];

// camera: world centre (x, y) and zoom z, monotone keyframes
const CAM_KEYS = [
  [0, 1440, 300, 2.4], [4.8, 1440, 300, 2.5], [8.6, 1010, 560, 1.12], [10.8, 1000, 590, 1.3],
  [12.6, 975, 640, 2.7], [16.6, 970, 635, 2.9], [22.4, 960, 540, 1.0], [23.4, 960, 540, 1.0],
  [25.6, 1150, 430, 1.75], [30, 1150, 425, 1.8],
];
const camX = monotone(CAM_KEYS.map(k => [k[0], k[1]])), camY = monotone(CAM_KEYS.map(k => [k[0], k[2]]));
const camZ = monotone(CAM_KEYS.map(k => [k[0], k[3]]));
const cam = t => ({ x: camX(t), y: camY(t), z: camZ(t) });
const toScreen = (c, x, y) => [W / 2 + (x - c.x) * c.z, H / 2 + (y - c.y) * c.z];

// ---------- builders (all geometry under fixed seeds; warm and cold share it) ----------
function buildBG(P) {
  const G = { sky: [], bld: [], gnd: [], step: [], lamp: [] };
  withSeed(101, () => {
    for (let i = 0; i < 18; i++) {
      const y = 30 + i * 38 + rnd(-10, 10);
      G.sky.push(mk(qcurve(-140, y, 2060, y + rnd(-20, 20), rnd(-30, 30), 24), rnd(60, 90), i % 3 ? P.sky : P.sky2, { prof: 'even', nb: 4, a: rnd(.32, .48), rough: .3 }));
    }
  });
  withSeed(102, () => {
    let x = -60;
    while (x < 2000) {
      const bw = rnd(110, 210), top = rnd(400, 560), col = rnd() < .5 ? P.bld : P.bld2;
      for (let xx = x; xx < x + bw; xx += 20) G.bld.push(mk(qcurve(xx, 745, xx + rnd(-3, 3), top + rnd(-6, 6), rnd(-4, 4), 10), 28, col, { prof: 'even', nb: 3, a: rnd(.26, .36), rough: .25 }));
      for (let k = 0; k < 5; k++) {
        const wx = x + rnd(18, bw - 18), wy = rnd(top + 30, 700);
        G.bld.push(mk(qcurve(wx, wy, wx, wy + 18, 0, 4), 9, P.bld2, { prof: 'even', nb: 0, a: .35 }));
      }
      x += bw + rnd(10, 60);
    }
    G.bld.push(mk(qcurve(-120, 712, 2040, 708, 6, 30), 70, PAPER, { prof: 'even', nb: 5, a: .55, rough: .35 }));   // mist band
  });
  withSeed(103, () => {
    for (let i = 0; i < 14; i++) {
      const y = 742 + i * 26 + rnd(-6, 6);
      G.gnd.push(mk(qcurve(-140, y, 2060, y + rnd(-8, 8), rnd(-14, 14), 24), rnd(46, 70), i % 4 ? P.gnd : P.gnd2, { prof: 'even', nb: 5, a: rnd(.36, .5), rough: .28 }));
    }
    for (let k = 0; k < 9; k++) {
      const px = rnd(80, 1840), py = rnd(880, 1040);
      G.gnd.push(mk(qcurve(px - rnd(60, 120), py, px + rnd(60, 120), py + rnd(-3, 3), 2, 8), rnd(8, 14), P.gnd2, { prof: 'even', nb: 2, a: .4 }));
    }
  });
  withSeed(104, () => {
    for (let i = 0; i < 4; i++) G.step.push(mk(qcurve(850, STEP_Y + 4 + i * 6, 1250, STEP_Y + 3 + i * 6, rnd(-3, 3), 14), 16, P.step, { prof: 'even', nb: 4, a: .55 }));
    for (let i = 0; i < 5; i++) G.step.push(mk(qcurve(852, STEP_Y + 32 + i * 12, 1248, STEP_Y + 30 + i * 12, rnd(-2, 2), 14), 18, P.stepD, { prof: 'even', nb: 4, a: .5 }));
    G.step.push(mk(qcurve(846, STEP_Y + 22, 1254, STEP_Y + 20, -2, 20), 3.2, INK2, { prof: 'even', nb: 0, a: .7, rough: .4 }));
    G.step.push(mk(qcurve(846, STEP_Y - 2, 1252, STEP_Y - 3, 1, 20), 2.4, INK2, { prof: 'even', nb: 0, a: .55, rough: .4 }));
  });
  withSeed(105, () => {
    const post = mk(qcurve(580, 860, 586, 330, 4, 20), 11, P.lamp, { prof: 'even', nb: 3, a: .85 });
    G.lamp.push(post, edgeOf(post, -1, 2, INK2, .7));
    G.lamp.push(mk(qctrl(586, 334, 600, 300, 640, 308, 10), 7, P.lamp, { prof: 'even', nb: 0, a: .85 }));
    G.lamp.push(mk(qcurve(624, 312, 660, 312, -10, 8), 18, P.lamp, { prof: 'even', nb: 3, a: .8 }));
    clump(G.lamp, 642, 340, 26, 18, [P.glow], { l0: 8, l1: 18, w0: 10, w1: 18, a0: .3, a1: .5 });
  });
  return G;
}

// figure strokes in local coordinates (y up = negative), mapped into the world
function figTools(A) {
  const q = (x0, y0, x1, y1, bend = 0, n = 10) => qcurve(A.x + x0 * A.s, A.y + y0 * A.s, A.x + x1 * A.s, A.y + y1 * A.s, bend * A.s, n);
  const m = (pts, w, col, o) => mk(pts, w * A.s, col, o);
  return { q, m };
}
function buildSeated(P) {
  const { q, m } = figTools(FIG), base = [], armsSit = [], armsPray = [];
  withSeed(201, () => {
    base.push(m(q(-2, -6, -72, -34, -6), 30, P.trou, { prof: 'even', nb: 4, a: .8 }));
    base.push(m(q(-72, -34, -92, 52, 4), 24, P.trou, { prof: 'even', nb: 4, a: .8 }));
    base.push(m(q(-104, 56, -80, 58, 0, 6), 12, P.hair, { prof: 'even', nb: 2, a: .85 }));
    const torso = m(q(8, -6, -14, -118, -22, 14), 62, P.coat, { prof: 'leaf', nb: 6, a: .82 });
    base.push(torso, m(q(14, -14, 0, -110, -26, 12), 26, P.coatD, { prof: 'leaf', nb: 3, a: .55 }), edgeOf(torso, 1, 2.4, INK2, .7));
    base.push(m(q(12, -4, -42, -22, -8), 34, P.coat, { prof: 'brush', nb: 4, a: .7 }));
  });
  withSeed(202, () => {
    base.push(m(q(-46, -140, -42, -122, 3, 6), 18, P.skin, { prof: 'leaf', nb: 0, a: .85 }));
    base.push(m(q(-14, -152, -52, -150, -16), 22, P.hair, { prof: 'even', nb: 4, a: .85 }));
    base.push(m(q(-12, -150, -18, -120, 8), 18, P.hair, { prof: 'tip', nb: 3, a: .85 }));
    base.push(m(q(-22, -160, -56, -136, -10), 14, P.hair, { prof: 'tip', nb: 3, a: .8 }));
  });
  withSeed(203, () => {
    armsSit.push(m(q(-8, -110, -44, -74, 6), 18, P.coat, { prof: 'even', nb: 3, a: .85 }));
    armsSit.push(m(q(-44, -74, -74, -44, -4), 16, P.coat, { prof: 'even', nb: 3, a: .85 }));
    armsSit.push(m(q(-74, -44, -84, -38, 0, 5), 11, P.skin, { prof: 'leaf', nb: 0, a: .9 }));
  });
  withSeed(204, () => {
    armsPray.push(m(q(-8, -110, -34, -76, 8), 18, P.coat, { prof: 'even', nb: 3, a: .85 }));
    armsPray.push(m(q(-34, -76, -54, -102, 6), 16, P.coat, { prof: 'even', nb: 3, a: .85 }));
    armsPray.push(m(q(-54, -100, -60, -127, -3, 6), 13, P.skin, { prof: 'leaf', nb: 0, a: .9 }));
    armsPray.push(m(q(-57, -100, -63, -124, 3, 6), 11, P.skinD, { prof: 'leaf', nb: 0, a: .8 }));
  });
  return { base, armsSit, armsPray };
}
function buildStanding(P) {
  const { q, m } = figTools(STAND), S = [];
  withSeed(301, () => {
    S.push(m(q(-6, 0, -4, -190, 2), 28, P.trou, { prof: 'even', nb: 4, a: .8 }));
    S.push(m(q(9, 0, 7, -188, -2), 26, P.trou, { prof: 'even', nb: 4, a: .72 }));
    S.push(m(q(-22, 4, 0, 4, 0, 5), 12, P.hair, { prof: 'even', nb: 2, a: .85 }), m(q(-6, 4, 16, 4, 0, 5), 12, P.hair, { prof: 'even', nb: 2, a: .8 }));
    const coat = m(q(2, -130, -6, -332, -6, 14), 72, P.coat, { prof: 'leaf', nb: 7, a: .82 });
    S.push(coat, m(q(-10, -120, -2, -250, 4, 10), 64, P.coat, { prof: 'leaf', nb: 5, a: .6 }), m(q(14, -140, 8, -318, -6, 12), 24, P.coatD, { prof: 'leaf', nb: 3, a: .5 }));
    S.push(edgeOf(coat, 1, 2.4, INK2, .65));
  });
  withSeed(302, () => {
    S.push(m(q(-12, -332, -16, -352, 0, 5), 14, P.skin, { prof: 'even', nb: 0, a: .85 }));
    S.push(m(q(-28, -394, -34, -354, -7, 8), 36, P.skin, { prof: 'leaf', nb: 0, a: .88 }));
    S.push(m(q(-6, -398, 8, -340, 10), 30, P.hair, { prof: 'tip', nb: 4, a: .85 }));
    S.push(m(q(-40, -398, -4, -402, -10), 18, P.hair, { prof: 'even', nb: 3, a: .85 }));
    S.push(m(q(4, -384, 16, -330, 4), 16, P.hair, { prof: 'tip', nb: 3, a: .8 }));
    S.push(m(q(-40, -381, -29, -382, -3, 6), 2.6, INK, { prof: 'even', nb: 0, a: .85, rough: .15 }));      // closed eye
    S.push(m(q(-44, -365, -32, -362, 4.5, 6), 2.8, INK, { prof: 'even', nb: 0, a: .85, rough: .15 }));     // smile
    S.push(m(q(-33, -372, -27, -371, 0, 4), 9, PINK, { prof: 'leaf', nb: 0, a: .4 }));                       // blush
  });
  withSeed(303, () => {
    S.push(m(q(-2, -318, -26, -250, 6), 18, P.coat, { prof: 'even', nb: 3, a: .85 }));
    S.push(m(q(-26, -250, -40, -200, -4), 16, P.coat, { prof: 'even', nb: 3, a: .85 }));
    S.push(m(q(-40, -200, -46, -186, 0, 5), 11, P.skin, { prof: 'leaf', nb: 0, a: .9 }));
  });
  return S;
}

// a stroke list rasterised at a given scale, drawn back in world units
function spriteAt(L, scale) {
  const [x0, y0, x1, y1] = bbox(L), c2 = document.createElement('canvas');
  c2.width = Math.max(1, Math.ceil((x1 - x0) * scale)); c2.height = Math.max(1, Math.ceil((y1 - y0) * scale));
  const c = c2.getContext('2d'); c.scale(scale, scale); c.translate(-x0, -y0); for (const s of L) drawS(c, s, 1);
  return { cv: c2, x0, y0, w: x1 - x0, h: y1 - y0 };
}
const drawSpr = (sp, a = 1) => { if (a <= 0) return; ctx.globalAlpha = a; ctx.drawImage(sp.cv, sp.x0, sp.y0, sp.w, sp.h); ctx.globalAlpha = 1; };
const flat = G => Object.values(G).flat();

// ---------- rain, drops that land on the page, blossoms ----------
let RAIN_S = [], SPOTS = [];
function buildRainAndSpots() {
  RAIN_S = withSeed(401, () => Array.from({ length: 10 }, () => mk(qcurve(0, 0, -7, 30, rnd(-1, 1), 4), 2.4, RAIN, { prof: 'tip', nb: 0, a: rnd(.35, .55), rough: .2 })));
  const noteBox = [NOTE.x - 30, NOTE.y - 70, NOTE.x + 480, NOTE.y + 30], figBox = [860, 500, 1260, 880];
  const inBox = (x, y, b) => x > b[0] && x < b[2] && y > b[1] && y < b[3];
  withSeed(402, () => {
    for (let i = 0; i < 40; i++) {
      let x, y, tries = 0;
      do {
        if (i < 12) { x = rnd(1080, 1780); y = rnd(110, 500); } else { x = rnd(60, 1860); y = rnd(80, 1040); }
      } while ((inBox(x, y, noteBox) || inBox(x, y, figBox) || inBox(x, y, [520, 240, 700, 880])) && ++tries < 60);
      const tl = i < 12 ? 1.0 + i * 0.36 + rnd(-.1, .1) : rnd(5.6, 16);
      const blot = [], bloom = [];
      for (let k = 0; k < 4; k++) blot.push(mk(qcurve(x + rnd(-6, 6), y + rnd(-6, 6), x + rnd(-6, 6), y + rnd(-6, 6), rnd(-4, 4), 5), rnd(10, 16), RAIN, { prof: 'leaf', nb: 0, a: rnd(.3, .45) }));
      const r = rnd(9, 14), rot = rnd(0, Math.PI);
      for (let k = 0; k < 5; k++) { const a = rot + k / 5 * Math.PI * 2; bloom.push(mk(polar(x, y, a, r * 1.5, rnd(-2, 2), 5), r * 1.15, PINK, { prof: 'leaf', nb: 2, a: rnd(.55, .75) })); }
      bloom.push(mk(qcurve(x - 2, y, x + 2, y + 1, 0, 3), 6, GOLD, { prof: 'leaf', nb: 0, a: .9 }));
      SPOTS.push({ x, y, tl, tb: T.burst + (i < 12 ? i * 0.02 : 0.24 + hash(i * 3.7) * 0.7), blot: spriteAt(blot, 3), bloom: spriteAt(bloom, 3) });
    }
  });
}
function drawRain(t) {
  const amt = 1 - ss(seg(t, T.spread[0] + 1, 25.5));
  if (amt <= 0) return;
  for (let i = 0; i < 170; i++) {
    if (hash(i * 1.31) > amt) continue;
    const sp = 760 + hash(i * 5.3) * 260;
    const y = ((hash(i * 7.7) * 1260 + t * sp) % 1260) - 80, x = ((hash(i * 3.1) * 2120 - y * 0.23) % 2120 + 2120) % 2120 - 100;
    ctx.save(); ctx.translate(x, y); drawS(ctx, RAIN_S[i % 10], 1, null, .9); ctx.restore();
  }
}
function drawSpots(t) {
  for (const s of SPOTS) {
    if (t < s.tl) continue;
    const g = eo(seg(t, s.tl, s.tl + .18)), b = eo(seg(t, s.tb, s.tb + .5));
    if (b < 1) { ctx.save(); ctx.translate(s.x, s.y); ctx.scale(g, g); ctx.translate(-s.x, -s.y); drawSpr(s.blot, 1 - b); ctx.restore(); }
    if (b > 0) { ctx.save(); ctx.translate(s.x, s.y); ctx.scale(b, b); ctx.translate(-s.x, -s.y); drawSpr(s.bloom, 1); ctx.restore(); }
  }
}

// ---------- the light: gold point, warm wash spreading, the sun ----------
let GOLD_SPR, SUN_SPR, MIST_SPR;
function buildLight() {
  const L = [], S = [], M = [];
  withSeed(501, () => clump(L, 0, 0, 30, 26, [GOLD, GOLD, '#efc27a'], { sx: 1, sy: 1, l0: 10, l1: 24, w0: 10, w1: 20, a0: .35, a1: .6 }));
  withSeed(502, () => clump(S, SUN[0], SUN[1], 64, 60, [GOLD, '#efc27a', '#f0b860'], { sx: 1, sy: 1, l0: 18, l1: 40, w0: 16, w1: 30, a0: .3, a1: .55 }));
  withSeed(503, () => clump(M, 0, 0, 120, 40, [PAPER], { sx: 1.1, sy: 1.4, l0: 40, l1: 90, w0: 40, w1: 70, a0: .35, a1: .55 }));
  GOLD_SPR = spriteAt(L, 4); SUN_SPR = spriteAt(S, 2); MIST_SPR = spriteAt(M, 1);
}
const spreadR = t => t < T.spread[0] ? 0 : 60 + 2500 * ei(seg(t, T.spread[0], T.spread[1]));
function blobPath(c, x, y, r, t) {
  c.beginPath();
  for (let i = 0; i <= 120; i++) {
    const a = i / 120 * Math.PI * 2, rr = r * (1 + .05 * Math.sin(5 * a + 1.3 + t * .4) + .03 * Math.sin(11 * a + 2.1) + .018 * Math.sin(23 * a + .7));
    const px = x + Math.cos(a) * rr, py = y + Math.sin(a) * rr; i ? c.lineTo(px, py) : c.moveTo(px, py);
  }
  c.closePath();
}
function drawGold(t) {
  if (t < T.goldIn) return;
  const g = .25 * eo(seg(t, T.goldIn, T.goldIn + .7)) + .35 * eio(seg(t, T.bloom - .4, T.bloom + .6)) + .25 * ss(seg(t, T.bloom + .6, T.spread[0] + 1.5));
  const a = 1 - .7 * ss(seg(t, T.spread[0] + 1, T.spread[0] + 4));
  ctx.save(); ctx.translate(HANDS[0], HANDS[1]); ctx.scale(g, g); drawSpr(GOLD_SPR, a); ctx.restore();
}
function drawSun(t) {
  const p = seg(t, T.sun[0], T.sun[1]);
  if (p <= 0) return;
  ctx.save(); ctx.translate(SUN[0], SUN[1]); const k = .55 + .45 * eo(p); ctx.scale(k, k); ctx.translate(-SUN[0], -SUN[1]);
  drawSpr(SUN_SPR, ss(p) * .95); ctx.restore();
}

// ---------- handwriting ----------
function hand(txt, x, y, p, col, size, dotGold = false) {
  if (p <= 0) return;
  ctx.font = `600 ${size}px Caveat`; const w = ctx.measureText(txt).width;
  ctx.save(); ctx.beginPath(); ctx.rect(x - 20, y - size * 1.2, (w + 40) * clamp(p), size * 1.8); ctx.clip();
  ctx.lineJoin = 'round'; ctx.strokeStyle = rgba(PAPER, .7); ctx.lineWidth = size * .14; ctx.strokeText(txt, x, y);
  const body = dotGold ? txt.slice(0, -1) : txt;
  ctx.fillStyle = rgba(col, .62); ctx.fillText(body, x, y); ctx.fillStyle = rgba(col, .45); ctx.fillText(body, x + .8, y + .5);
  if (dotGold) { const bw = ctx.measureText(body).width; ctx.fillStyle = rgba(GOLD, .95); ctx.beginPath(); ctx.arc(x + bw + size * .12, y - size * .06, size * .085, 0, Math.PI * 2); ctx.fill(); }
  ctx.restore();
  return w;
}
let LIFT_S;
function drawNotes(t) {
  const e = seg(t, T.erase1[0], T.erase1[1]);
  if (e < 1) {
    ctx.save(); ctx.globalAlpha = 1 - ss(e); hand('Too heavy today.', NOTE.x, NOTE.y, seg(t, ...T.write1), NOTE1, NOTE.size); ctx.restore();
    if (e > 0) { ctx.save(); ctx.translate(NOTE.x + 220, NOTE.y - 20); ctx.scale(2.2, .7); drawSpr(MIST_SPR, Math.sin(Math.PI * e) * .9); ctx.restore(); }
  }
  hand('Lighter now.', NOTE.x, NOTE.y, seg(t, ...T.write2), NOTE2, NOTE.size, true);
  const lp = .86 * ss(seg(t, ...T.lift));                   // the brush lifts before the stroke ends
  if (lp > 0) drawS(ctx, LIFT_S, lp);
}

// ---------- layers ----------
let BG_C, BG_W, SEAT_C, SEAT_W, STAND_W, SPR = {};
function bgSprite(G) {                                     // the whole background at 2× world resolution
  const c2 = document.createElement('canvas'); c2.width = W * 2; c2.height = H * 2;
  const c = c2.getContext('2d'); c.scale(2, 2); for (const s of flat(G)) drawS(c, s, 1);
  return { cv: c2, x0: 0, y0: 0, w: W, h: H };
}
function figAlpha(t) {
  return {
    base: 1 - ss(seg(t, T.stand[0], T.stand[0] + .7)),
    sit: 1 - ss(seg(t, T.fold[0], T.fold[0] + .6)),
    pray: ss(seg(t, T.fold[0] + .3, T.fold[1])),
  };
}
function drawCold(t) {
  if (t < T.paint.sky[0]) return;
  if (t < T.paint.lamp[1]) { for (const k of ['sky', 'bld', 'gnd', 'step', 'lamp']) drawList(ctx, BG_C[k], seg(t, ...T.paint[k])); }
  else drawSpr(SPR.bgC);
  if (t < T.paint.base[0]) return;
  const fa = figAlpha(t);
  if (t < T.paint.base[1]) drawList(ctx, SEAT_C.base, seg(t, ...T.paint.base)); else drawSpr(SPR.baseC, fa.base);
  if (t < T.paint.arms[1]) drawList(ctx, SEAT_C.armsSit, seg(t, ...T.paint.arms)); else drawSpr(SPR.sitC, fa.sit * fa.base);
  if (t > T.fold[0]) { if (t < T.fold[1]) drawList(ctx, SEAT_C.armsPray, seg(t, T.fold[0] + .2, T.fold[1])); else drawSpr(SPR.prayC, fa.base); }
}
function drawWarm(t) {
  const fa = figAlpha(t);
  drawSpr(SPR.bgW); drawSpr(SPR.baseW, fa.base); drawSpr(SPR.prayW, fa.base * fa.pray);
  if (t > T.stand[0]) {
    const p = seg(t, T.stand[0] + .3, T.stand[1]);
    if (p < 1) drawList(ctx, STAND_W, p); else drawSpr(SPR.standW);
    const m = seg(t, T.stand[0], T.stand[0] + 1.1);
    if (m > 0 && m < 1) { ctx.save(); ctx.translate(FIG.x - 30, FIG.y - 150); drawSpr(MIST_SPR, Math.sin(Math.PI * m) * .8); ctx.restore(); }
  }
}
const BANDS = [.2, .25, 1 / 3, .5, 1];                       // outer → inner: 5 quantised bands of warm
function drawSheet(t) {
  const R = spreadR(t);
  if (R >= 2560) { drawWarm(t); return; }
  drawCold(t);
  if (R <= 0) return;
  const bw = 40 + R * .06;
  for (let k = 4; k >= 0; k--) {
    ctx.save(); blobPath(ctx, HANDS[0], HANDS[1], R + k * bw, t); ctx.clip();
    ctx.globalAlpha = BANDS[4 - k]; drawWarm(t); ctx.globalAlpha = 1; ctx.restore();
  }
  ctx.save(); blobPath(ctx, HANDS[0], HANDS[1], R, t);       // the pooled edge where the wash stops
  ctx.strokeStyle = rgba(GOLD, .09); ctx.lineWidth = 22; ctx.stroke(); ctx.strokeStyle = rgba(GOLD, .1); ctx.lineWidth = 9; ctx.stroke(); ctx.strokeStyle = rgba('#c98a2a', .1); ctx.lineWidth = 3; ctx.stroke(); ctx.restore();
}

// ---------- subtitles (on the paper, no box) ----------
function wrap(txt, maxW) {
  const words = txt.split(' '), lines = []; let cur = '';
  for (const w of words) { const n = cur ? cur + ' ' + w : w; if (ctx.measureText(n).width > maxW && cur) { lines.push(cur); cur = w; } else cur = n; }
  if (cur) lines.push(cur);
  if (lines.length === 2) return lines;
  return lines.length > 2 ? [lines.slice(0, Math.ceil(lines.length / 2)).join(' '), lines.slice(Math.ceil(lines.length / 2)).join(' ')] : lines;
}
function drawSubs(t) {
  const s = SUBS.find(s => t >= s.t0 && t < s.t1);
  if (!s) return;
  const a = ss(seg(t, s.t0, s.t0 + .25)) * (1 - ss(seg(t, s.t1 - .25, s.t1)));
  ctx.font = 'italic 400 38px "Cormorant Garamond"'; ctx.textAlign = 'center'; ctx.lineJoin = 'round';
  const L = wrap(s.text, 1100);
  L.forEach((ln, i) => {
    const y = H - 62 - (L.length - 1 - i) * 46;
    ctx.strokeStyle = rgba(PAPER, .8 * a); ctx.lineWidth = 9; ctx.strokeText(ln, W / 2, y);
    ctx.fillStyle = rgba(INK, .78 * a); ctx.fillText(ln, W / 2, y);
  });
  ctx.textAlign = 'left';
}

// ---------- the frame ----------
let PAPER_IMG;
function render(t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.drawImage(PAPER_IMG, 0, 0);
  const c = cam(t);
  ctx.setTransform(c.z, 0, 0, c.z, W / 2 - c.x * c.z, H / 2 - c.y * c.z);
  drawSheet(t);
  drawGold(t); drawSun(t); drawSpots(t); drawRain(t); drawNotes(t);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  drawSubs(t);
}
window.render = render;

// every on-screen note with its box, for readcheck (subtitles are checked from the .srt)
window.TEXTS = t => {
  const c = cam(t), out = [];
  ctx.font = `600 ${NOTE.size}px Caveat`;
  const box = (id, text) => {
    const w = ctx.measureText(text).width, [x0, y0] = toScreen(c, NOTE.x, NOTE.y - NOTE.size), [x1, y1] = toScreen(c, NOTE.x + w, NOTE.y + NOTE.size * .3);
    out.push({ id, text, x0, y0, x1, y1 });
  };
  if (t >= T.write1[0] && t < T.erase1[0]) box('note1', 'Too heavy today.');
  if (t >= T.write2[0]) box('note2', 'Lighter now.');
  return out;
};

// sound and cue events for the mixer
function buildEvents() {
  const EV = [];
  const pan = x => clamp((x - 960) / 960, -1, 1);
  EV.push({ t: T.write1[0], type: 'pencil', d: T.write1[1] - T.write1[0], pan: .4 });
  for (const s of SPOTS) EV.push({ t: s.tl, type: 'drip', pan: pan(s.x) * .7 });
  for (const [k, [a, b]] of Object.entries(T.paint)) EV.push({ t: a, type: 'brush', d: b - a, pan: k === 'lamp' ? -.4 : k === 'base' || k === 'arms' ? .1 : 0 });
  EV.push({ t: T.fold[0] + .2, type: 'brush', d: 1, pan: 0 });
  EV.push({ t: T.goldIn, type: 'bloom', d: 1.2 }, { t: T.bloom, type: 'bloom', d: 2.4 });
  EV.push({ t: T.spread[0], type: 'sweep', d: T.spread[1] - T.spread[0] });
  EV.push({ t: T.burst, type: 'chime' });
  for (const s of SPOTS) EV.push({ t: s.tb, type: 'petal', pan: pan(s.x) * .7 });
  EV.push({ t: T.stand[0], type: 'mist', d: 1.1 }, { t: T.stand[0] + .3, type: 'brush', d: 1.2, pan: .05 });
  EV.push({ t: T.sun[0], type: 'brush', d: 1.6, pan: -.3 });
  EV.push({ t: T.erase1[0], type: 'mist', d: .7 }, { t: T.write2[0], type: 'pencil', d: T.write2[1] - T.write2[0], pan: .4 });
  EV.push({ t: T.lift[0], type: 'brush', d: 1.0, pan: .3 });
  for (const v of VO) EV.push({ t: v.t, type: 'vo', id: v.id });
  EV.push({ t: 0, type: 'grid', bpm: BPM, bars: 9 });
  return EV.sort((a, b) => a.t - b.t);
}

(async () => {
  PAPER_IMG = new Image(); PAPER_IMG.src = 'paper.jpg'; await PAPER_IMG.decode();
  await Promise.all(['600 64px Caveat', 'italic 400 38px "Cormorant Garamond"'].map(f => document.fonts.load(f)));
  BG_C = buildBG(COLD); BG_W = buildBG(WARM);
  SEAT_C = buildSeated(COLD); SEAT_W = buildSeated(WARM); STAND_W = buildStanding(WARM);
  SPR.bgC = bgSprite(BG_C); SPR.bgW = bgSprite(BG_W);
  SPR.baseC = spriteAt(SEAT_C.base, 3); SPR.sitC = spriteAt(SEAT_C.armsSit, 3); SPR.prayC = spriteAt(SEAT_C.armsPray, 3);
  SPR.baseW = spriteAt(SEAT_W.base, 3); SPR.prayW = spriteAt(SEAT_W.armsPray, 3); SPR.standW = spriteAt(STAND_W, 2.5);
  buildRainAndSpots(); buildLight();
  ctx.font = `600 ${NOTE.size}px Caveat`;
  const lw = ctx.measureText('Lighter now.').width;
  LIFT_S = withSeed(601, () => mk(qcurve(NOTE.x - 6, NOTE.y + 22, NOTE.x + lw + 10, NOTE.y + 18, 5, 20), 7, GOLD, { prof: 'brush', nb: 4, a: .7 }));
  window.EV = buildEvents();
  window.READY = true;
})();
