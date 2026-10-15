// Headless smoke-test harness for the Road Rush single-file game.
// Usage: node run.mjs /path/to/index.html [--autopilot]
import fs from 'node:fs';
import { JSDOM, VirtualConsole } from 'jsdom';

const file = process.argv[2] || '/home/user/racing-game/index.html';
const AUTOPILOT = process.argv.includes('--autopilot');
const html = fs.readFileSync(file, 'utf8');
const scripts = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map((m) => m[1]).filter((s) => s.trim());
if (!scripts.length) throw new Error('no inline script found');

const errors = [];
const counts = {};
const seen = new Set();
const recordError = (e) => {
  const k = String(e).split('\n').slice(0, 2).join('|');
  counts[k] = (counts[k] || 0) + 1;
  if (seen.has(k)) return;
  seen.add(k);
  errors.push(String(e));
};

const vc = new VirtualConsole();
vc.on('jsdomError', (e) => recordError('jsdomError: ' + (e.stack || e.message)));
vc.on('error', (...a) => recordError('console.error: ' + a.map(String).join(' ')));
vc.on('warn', (...a) => recordError('console.warn: ' + a.map(String).join(' ')));

const dom = new JSDOM(html, { runScripts: 'outside-only', pretendToBeVisual: true, virtualConsole: vc, url: 'https://example.test/' });
const { window } = dom;
const doc = window.document;

/* ---------------- virtual clock + timers ---------------- */
let vnow = 0;
const timers = [];
let timerId = 1;
window.setTimeout = (cb, ms = 0, ...args) => { const id = timerId++; timers.push({ id, cb, time: vnow + (ms || 0), interval: null, args }); return id; };
window.setInterval = (cb, ms = 0, ...args) => { const id = timerId++; const p = ms > 0 ? ms : 1; timers.push({ id, cb, time: vnow + p, interval: p, args }); return id; };
window.clearTimeout = (id) => { const i = timers.findIndex((t) => t.id === id); if (i >= 0) timers.splice(i, 1); };
window.clearInterval = window.clearTimeout;
window.requestIdleCallback = (cb) => window.setTimeout(() => cb({ didTimeout: false, timeRemaining: () => 5 }), 1);
const runTimers = () => {
  for (const t of [...timers]) {
    if (t.time > vnow) continue;
    if (!timers.includes(t)) continue;
    if (t.interval) t.time = vnow + t.interval; else timers.splice(timers.indexOf(t), 1);
    try { t.cb(...t.args); } catch (e) { recordError('TIMER ' + (e.stack || e)); }
  }
};
const RealDate = Date;
window.Date = class FakeDate extends RealDate {
  constructor(...a) { if (a.length === 0) super(vnow); else super(...a); }
  static now() { return vnow; }
};
window.performance.now = () => vnow;

/* ---------------- canvas stub ---------------- */
const STYLE_PROPS = new Set(['fillStyle', 'strokeStyle', 'lineWidth', 'lineCap', 'lineJoin', 'miterLimit', 'font',
  'textAlign', 'textBaseline', 'shadowBlur', 'shadowColor', 'shadowOffsetX', 'shadowOffsetY', 'globalAlpha',
  'globalCompositeOperation', 'imageSmoothingEnabled', 'imageSmoothingQuality', 'lineDashOffset', 'filter', 'direction']);
const grad = () => ({ addColorStop() {} });
let ctxCalls = 0, drawImages = 0, fills = 0;
const makeCtx = () => {
  const noop = () => { ctxCalls++; };
  return new Proxy({}, {
    get(t, prop) {
      if (prop === 'canvas') return { width: 1280, height: 720 };
      if (typeof prop === 'symbol') return undefined;
      if (STYLE_PROPS.has(prop)) return t[prop] ?? '';
      if (prop === 'createLinearGradient' || prop === 'createRadialGradient' || prop === 'createPattern') return grad;
      if (prop === 'measureText') return () => ({ width: 10 });
      if (prop === 'getImageData') return (x, y, w, h) => ({ data: new Uint8ClampedArray(Math.max(1, w * h * 4)), width: w, height: h });
      if (prop === 'drawImage') return () => { ctxCalls++; drawImages++; };
      if (prop === 'fill') return () => { ctxCalls++; fills++; };
      if (prop in t) return t[prop];
      return noop;
    },
    set(t, prop, v) { t[prop] = v; return true; }
  });
};
window.HTMLCanvasElement.prototype.getContext = () => makeCtx();
const dim = (v) => ({ get() { return v; }, configurable: true });
Object.defineProperty(window.HTMLElement.prototype, 'clientWidth', dim(1280));
Object.defineProperty(window.HTMLElement.prototype, 'clientHeight', dim(720));
Object.defineProperty(window.HTMLElement.prototype, 'offsetWidth', dim(1280));
Object.defineProperty(window.HTMLElement.prototype, 'offsetHeight', dim(720));
window.HTMLElement.prototype.getBoundingClientRect = function () { return { x: 0, y: 0, top: 0, left: 0, right: 1280, bottom: 720, width: 1280, height: 720 }; };

/* ---------------- Web Audio stub ---------------- */
class FakeParam { constructor(v = 0) { this.value = v; } setValueAtTime(v) { this.value = v; return this; } linearRampToValueAtTime(v) { this.value = v; return this; } exponentialRampToValueAtTime(v) { this.value = v; return this; } setTargetAtTime(v) { this.value = v; return this; } cancelScheduledValues() { return this; } }
class FakeNode {
  constructor(ctx, type) { this.context = ctx; this.type = type; this.frequency = new FakeParam(440); this.gain = new FakeParam(1); this.Q = new FakeParam(1); this.detune = new FakeParam(0); this.playbackRate = new FakeParam(1); this.delayTime = new FakeParam(0); this.pan = new FakeParam(0); this.curve = null; this.oversample = 'none'; this.buffer = null; this.loop = false; }
  connect() { return arguments[0]; } disconnect() {} start() {} stop() {} setPeriodicWave() {}
}
class FakeAudioContext {
  constructor() { this.currentTime = 0; this.sampleRate = 48000; this.destination = new FakeNode(this, 'destination'); this.state = 'running'; }
  createOscillator() { return new FakeNode(this, 'oscillator'); }
  createGain() { return new FakeNode(this, 'gain'); }
  createBiquadFilter() { return new FakeNode(this, 'biquad'); }
  createBufferSource() { return new FakeNode(this, 'bufferSource'); }
  createBuffer(ch, len, rate) { return { length: len, sampleRate: rate, numberOfChannels: ch, duration: len / rate, getChannelData: () => new Float32Array(len) }; }
  createStereoPanner() { return new FakeNode(this, 'panner'); }
  createDynamicsCompressor() { return new FakeNode(this, 'compressor'); }
  createConvolver() { return new FakeNode(this, 'convolver'); }
  createDelay() { return new FakeNode(this, 'delay'); }
  createWaveShaper() { return new FakeNode(this, 'waveshaper'); }
  createAnalyser() { const n = new FakeNode(this, 'analyser'); n.fftSize = 2048; n.frequencyBinCount = 1024; n.getByteFrequencyData = (a) => a && a.fill(0); return n; }
  createPeriodicWave() { return {}; }
  resume() { this.state = 'running'; return Promise.resolve(); }
  suspend() { this.state = 'suspended'; return Promise.resolve(); }
  close() { return Promise.resolve(); }
}
window.AudioContext = FakeAudioContext;
window.webkitAudioContext = FakeAudioContext;

/* ---------------- misc browser stubs ---------------- */
if (!window.PointerEvent) window.PointerEvent = window.MouseEvent;
window.matchMedia = window.matchMedia || (() => ({ matches: false, media: '', addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} }));
window.navigator.vibrate = window.navigator.vibrate || (() => true);
window.navigator.getGamepads = window.navigator.getGamepads || (() => []);
if (!window.screen) window.screen = {};
if (!window.screen.orientation) window.screen.orientation = { type: 'landscape-primary', angle: 0, addEventListener() {}, removeEventListener() {} };
window.HTMLElement.prototype.requestFullscreen = window.HTMLElement.prototype.requestFullscreen || (() => Promise.resolve());
doc.exitFullscreen = doc.exitFullscreen || (() => Promise.resolve());
Object.defineProperty(doc, 'visibilityState', { value: 'visible', configurable: true });
Object.defineProperty(doc, 'hidden', { value: false, configurable: true });

/* ---------------- rAF control ---------------- */
const rafQueue = [];
let lastCb = null, revives = 0;
window.requestAnimationFrame = (cb) => { lastCb = cb; rafQueue.push(cb); return rafQueue.length; };
window.cancelAnimationFrame = () => {};
const stepFrame = (ms = 16.7) => {
  vnow += ms;
  runTimers();
  const q = rafQueue.splice(0, rafQueue.length);
  q.forEach((cb) => { try { cb(vnow); } catch (e) { recordError('FRAME ' + (e.stack || e)); } });
  if (rafQueue.length === 0 && lastCb) { revives++; rafQueue.push(lastCb); }
};

/* ---------------- boot ---------------- */
let booted = false;
try {
  for (const s of scripts) window.eval(s);
  doc.dispatchEvent(new window.Event('DOMContentLoaded', { bubbles: true }));
  window.dispatchEvent(new window.Event('load'));
  booted = true;
} catch (e) { recordError('BOOT: ' + (e.stack || e)); }

const txt = (sel) => (doc.querySelector(sel)?.textContent || '').trim();
const hidden = (sel) => {
  const el = doc.querySelector(sel);
  if (!el) return true;
  let n = el;
  while (n) { if (n.hasAttribute && n.hasAttribute('hidden')) return true; n = n.parentElement; }
  return false;
};
const click = (sel) => {
  const el = doc.querySelector(sel);
  if (!el) throw new Error('missing element for click: ' + sel);
  el.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  return el;
};
const key = (type, code) => window.dispatchEvent(new window.KeyboardEvent(type, { code, key: code, bubbles: true }));
const report = { file, autopilot: AUTOPILOT, booted, errors, checks: [], notes: {} };
const check = (label, cond, extra = '') => { report.checks.push({ label, ok: !!cond, extra: cond ? '' : String(extra || '') }); };

/* ---------------- autopilot: drives the real input path ---------------- */
function autopilot(g) {
  const kb = g.keyBuffer;
  const seg = g.segmentAt(g.playerZ);
  const top = g.map.topSpeed;
  const ahead = g.cornerBrake(g.playerZ + 9000);
  let target = clamp(-g.segmentAt(g.playerZ + 5000).curve * 0.11, -0.62, 0.62);
  let nearest = null, nearestD = 9e9;
  if (g.activeVehicles) {
    for (let i = 0; i < g.activeVehicles.length; i++) {
      const v = g.activeVehicles[i];
      let d = v.z - g.playerZ;
      if (d < -g.trackLength / 2) d += g.trackLength;
      if (d > g.trackLength / 2) d -= g.trackLength;
      const gap = d - (v.isBike ? 0 : 0);
      if (d > 200 && d < 5200 && Math.abs(v.x - g.playerX) < 0.42 && d < nearestD) { nearest = v; nearestD = d; }
    }
  }
  if (nearest) {
    const away = nearest.x >= g.playerX ? -1 : 1;
    target = clamp(g.playerX + away * 0.62, -0.72, 0.72);
    if (nearestD < 1500 && g.health < 55) target = clamp(nearest.x + away * 0.5, -0.7, 0.7);
  }
  const dx = target - g.playerX;
  kb.ArrowLeft = dx < -0.05;
  kb.ArrowRight = dx > 0.05;
  const straight = ahead > 0.9;
  const want = straight ? top * 1.12 : top * (0.46 + 0.5 * ahead);
  kb.ArrowUp = g.speed < want;
  kb.ArrowDown = g.speed > want * 1.14 && !straight;
  kb.Space = !!straight && g.nitro > 35 && g.health > 45;
  if (Math.abs(g.playerX) > 0.94) { kb.ArrowLeft = g.playerX > 0; kb.ArrowRight = g.playerX < 0; }
}
const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);

/* ---------------- flow ---------------- */
if (booted) {
  try {
    check('menu visible at boot', !hidden('#menuScreen'));
    const cards = doc.querySelectorAll('.map-card');
    report.notes.mapCards = cards.length;
    check('map cards rendered', cards.length >= 3, `found ${cards.length}`);

    for (let i = 0; i < 12; i++) stepFrame();
    check('no errors while idle in MENU', errors.length === 0, errors[0] || '');

    const diffs = [...doc.querySelectorAll('.diff-btn, [data-diff]')].map((d) => d.dataset.diff || d.textContent.trim());
    report.notes.diffOptions = diffs.length;

    const laps = [...doc.querySelectorAll('[data-laps]')].map((d) => d.dataset.laps);
    report.notes.lapOptions = laps;

    const runs = Number(process.env.RUNS || cards.length);
    for (let m = 0; m < Math.min(runs, cards.length); m++) {
      doc.querySelectorAll('.map-card')[m].dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
      const diffPick = process.env.DIFF || null;
      if (diffPick) {
        const chip = doc.querySelector(`[data-diff="${diffPick}"]`);
        if (chip) chip.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
      }
      const twoLap = doc.querySelector('[data-laps="2"]');
      if (twoLap && m > 0) twoLap.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));  // keep the sweep quick
      click('#startBtn');
      check(`m${m} countdown shown`, !hidden('#countdownBox'));
      let guard = 0;
      while (!hidden('#countdownBox') && guard++ < 400) stepFrame(50);
      check(`m${m} race started`, hidden('#countdownBox'));

      const g = window.roadrush;
      let f = 0;
      const maxFrames = Number(process.env.MAXF ? process.env.MAXF : 20000);
      const callsStart = ctxCalls, framesStart = f;
      while (hidden('#resultsScreen') && f < maxFrames) {
        if (AUTOPILOT && g) autopilot(g);
        else { window.dispatchEvent(new window.KeyboardEvent('keydown', { code: 'ArrowUp' })); }
        stepFrame(16.7); f++;
      }
      ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Space'].forEach((k) => {
        if (g) g.keyBuffer[k] = false;
        window.dispatchEvent(new window.KeyboardEvent('keyup', { code: k }));
      });
      check(`m${m} race finished`, !hidden('#resultsScreen'), `ran ${f} frames, no results`);
      const rivals = g && g.rivals ? g.rivals.map((r) => ({ name: r.name, lap: r.lap, z: Math.round(r.z) })) : [];
      const lapInfo = g ? {
        laps: g.laps, lapTimes: g.lapTimes.map((t) => Math.round(t)),
        bestLap: Math.round(g.bestLap), health: Math.round(g.health),
        damage: Math.round(g.damageTaken), passes: g.passes, nearMisses: g.nearMisses,
        combos: g.combo, state: g.state, rivalsAhead: rivals.filter((r) => (r.lap - 1) * g.trackLength + r.z > (g.lap - 1) * g.trackLength + g.playerZ).length, trackKm: +(g.trackLength / (62 * 3600)).toFixed(2),
        maxSpeed: Math.round(g.topSpeedReached), segments: g.track.segments.length
      } : null;
      let gaps = null;
      if (g && g.rivals) {
        const playerProg = (g.lap - 1) * g.trackLength + g.playerZ;
        const unitsPerSec = g.raceTime > 0 ? playerProg / (g.raceTime / 1000) : 1;
        gaps = g.rivals
          .map((r) => ({ name: r.name, gap: +(((g.lap - 1) * g.trackLength + g.playerZ - ((r.lap - 1) * g.trackLength + r.z)) / unitsPerSec).toFixed(1) }))
          .sort((a, b) => a.gap - b.gap);
      }
      report.notes[`race_m${m}`] = {
        frames: f, rank: txt('#resRank'), title: txt('#resTitle'), time: txt('#resTime'),
        best: txt('#resBest'), speed: txt('#resSpeed'), score: txt('#resScore'),
        passes: txt('#resPasses'), damage: txt('#resDamage'), lapInfo, gaps,
        canvasCallsPerFrame: Math.round((ctxCalls - callsStart) / Math.max(1, f - framesStart)),
        drawImagesPerFrame: drawImages
      };
      click('#menuReturnBtn');
      check(`m${m} back to menu`, !hidden('#menuScreen'));
    }

    report.notes.localStorage = Object.keys(window.localStorage);
    report.notes.save = JSON.parse(window.localStorage.getItem('roadrush.v2.save') || '{}');
    report.notes.extraUI = {
      topPauseButton: !!doc.querySelector('#topPauseBtn'),
      pauseOverlay: !!doc.querySelector('#pauseScreen'),
      minimap: !!doc.querySelector('#miniTrack'),
      gauge: !!doc.querySelector('#gaugeFill'),
      helpOverlay: !!doc.querySelector('#helpScreen'),
      touchPad: !!doc.querySelector('#touchPad'),
      liveRegion: !!doc.querySelector('#liveRegion')
    };
    report.notes.ctxCalls = ctxCalls;
    report.notes.fills = fills;
    report.notes.drawImages = drawImages;
  } catch (e) {
    recordError('FLOW: ' + (e.stack || e));
  }
}

report.errorCounts = counts;
report.rafRevives = revives;
report.failed = report.checks.filter((c) => !c.ok);
console.log(JSON.stringify(report, null, 1));
