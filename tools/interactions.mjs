// Interaction coverage: pause/resume, restart, touches, settings, keyboard,
// fullscreen/help toggles, record persistence and the results flow.
import fs from 'node:fs';
import { JSDOM, VirtualConsole } from 'jsdom';

const file = process.argv[2];
const html = fs.readFileSync(file, 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

const errors = [];
const seen = new Set();
const recordError = (e) => { const k = String(e).split('\n')[0]; if (!seen.has(k)) { seen.add(k); errors.push(String(e)); } };
const vc = new VirtualConsole();
vc.on('jsdomError', (e) => recordError('jsdomError: ' + (e.stack || e.message)));
vc.on('error', (...a) => recordError('console.error: ' + a.map(String).join(' ')));
vc.on('warn', (...a) => recordError('console.warn: ' + a.map(String).join(' ')));

const dom = new JSDOM(html, { runScripts: 'outside-only', pretendToBeVisual: true, virtualConsole: vc, url: 'https://example.test/' });
const { window } = dom;
const doc = window.document;

let vnow = 0;
const timers = [];
let tid = 1;
window.setTimeout = (cb, ms = 0, ...a) => { const id = tid++; timers.push({ id, cb, time: vnow + (ms || 0), interval: null, args: a }); return id; };
window.setInterval = (cb, ms = 0, ...a) => { const id = tid++; const p = ms > 0 ? ms : 1; timers.push({ id, cb, time: vnow + p, interval: p, args: a }); return id; };
window.clearTimeout = (id) => { const i = timers.findIndex((t) => t.id === id); if (i >= 0) timers.splice(i, 1); };
window.clearInterval = window.clearTimeout;
const runTimers = () => {
  for (const t of [...timers]) {
    if (t.time > vnow) continue;
    if (t.interval) t.time = vnow + t.interval; else timers.splice(timers.indexOf(t), 1);
    try { t.cb(...t.args); } catch (e) { recordError('TIMER ' + (e.stack || e)); }
  }
};
const RealDate = Date;
window.Date = class extends RealDate { constructor(...a) { if (!a.length) super(vnow); else super(...a); } static now() { return vnow; } };
window.performance.now = () => vnow;

const grad = () => ({ addColorStop() {} });
const STYLE = new Set(['fillStyle', 'strokeStyle', 'lineWidth', 'lineCap', 'lineJoin', 'miterLimit', 'font', 'textAlign', 'textBaseline', 'shadowBlur', 'shadowColor', 'shadowOffsetX', 'shadowOffsetY', 'globalAlpha', 'globalCompositeOperation', 'imageSmoothingEnabled', 'lineDashOffset', 'filter', 'direction']);
window.HTMLCanvasElement.prototype.getContext = () => new Proxy({}, {
  get(t, p) {
    if (p === 'canvas') return { width: 1280, height: 720 };
    if (typeof p === 'symbol') return undefined;
    if (STYLE.has(p)) return t[p] ?? '';
    if (p === 'createLinearGradient' || p === 'createRadialGradient' || p === 'createPattern') return grad;
    if (p === 'measureText') return () => ({ width: 10 });
    if (p in t) return t[p];
    return () => {};
  },
  set(t, p, v) { t[p] = v; return true; }
});
const dim = (v) => ({ get() { return v; }, configurable: true });
Object.defineProperty(window.HTMLElement.prototype, 'clientWidth', dim(1280));
Object.defineProperty(window.HTMLElement.prototype, 'clientHeight', dim(720));
window.HTMLElement.prototype.getBoundingClientRect = () => ({ x: 0, y: 0, top: 0, left: 0, right: 1280, bottom: 720, width: 1280, height: 720 });
class P { constructor(v = 0) { this.value = v; } setValueAtTime(v) { this.value = v; return this; } linearRampToValueAtTime(v) { this.value = v; return this; } exponentialRampToValueAtTime(v) { this.value = v; return this; } setTargetAtTime(v) { this.value = v; return this; } cancelScheduledValues() { return this; } }
class N { constructor() { this.frequency = new P(440); this.gain = new P(1); this.Q = new P(1); this.playbackRate = new P(1); this.detune = new P(0); this.pan = new P(0); } connect() { return arguments[0]; } disconnect() {} start() {} stop() {} }
window.AudioContext = class { constructor() { this.currentTime = 0; this.sampleRate = 48000; this.destination = new N(); this.state = 'running'; } createOscillator() { return new N(); } createGain() { return new N(); } createBiquadFilter() { return new N(); } createBufferSource() { return new N(); } createBuffer(c, l, r) { return { length: l, sampleRate: r, getChannelData: () => new Float32Array(l) }; } createStereoPanner() { return new N(); } createDynamicsCompressor() { return new N(); } createAnalyser() { const n = new N(); n.getByteFrequencyData = () => {}; return n; } resume() { return Promise.resolve(); } suspend() { return Promise.resolve(); } };
window.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {} });
window.navigator.getGamepads = () => [];
window.navigator.vibrate = () => true;
doc.exitFullscreen = () => Promise.resolve();
window.HTMLElement.prototype.requestFullscreen = () => Promise.resolve();
Object.defineProperty(doc, 'hidden', { value: false, configurable: true });

const raf = [];
window.requestAnimationFrame = (cb) => { raf.push(cb); return raf.length; };
window.cancelAnimationFrame = () => {};
const step = (ms = 16.7) => { vnow += ms; runTimers(); const q = raf.splice(0, raf.length); q.forEach((cb) => { try { cb(vnow); } catch (e) { recordError('FRAME ' + (e.stack || e)); } }); };
const frames = (n, ms = 16.7) => { for (let i = 0; i < n; i++) step(ms); };

try {
  window.eval(script);
  doc.dispatchEvent(new window.Event('DOMContentLoaded', { bubbles: true }));
  window.dispatchEvent(new window.Event('load'));
} catch (e) { recordError('BOOT: ' + (e.stack || e)); }

const results = [];
const t = (name, fn) => { try { const r = fn(); results.push({ name, ok: r === true, detail: r === true ? '' : String(r) }); } catch (e) { results.push({ name, ok: false, detail: 'threw: ' + e.message }); } };
const el = (s) => doc.querySelector(s);
const hidden = (s) => { const n = el(s); return !n || !!n.closest('[hidden]'); };
const click = (s) => el(s).dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
const keyOf = (code) => window.dispatchEvent(new window.KeyboardEvent('keydown', { code, key: code, bubbles: true }));
const keyUp = (code) => window.dispatchEvent(new window.KeyboardEvent('keyup', { code, key: code, bubbles: true }));
const pointer = (s, type) => { const n = el(s); const E = window.PointerEvent || window.MouseEvent; n.dispatchEvent(new E(type, { bubbles: true, pointerId: 1 })); };
const g = () => window.roadrush;

frames(5);

/* ---- settings / livery ------------------------------------------------ */
t('livery swatch updates accent + prefs', () => {
  click('[data-livery="pink"]');
  const saved = JSON.parse(window.localStorage.getItem('roadrush.v2.save')).prefs.livery;
  const applied = window.roadrush.livery.id;
  return applied === 'pink' && saved === 'pink' ? true : `applied=${applied} saved=${saved}`;
});
t('camera chip switches camera', () => {
  const btn = doc.querySelector('#camSeg [data-cam="cockpit"]');
  btn.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  return g().camera === 'cockpit' ? true : `camera=${g().camera} btn=${!!btn} pressed=${btn && btn.getAttribute('aria-pressed')}`;
});
t('quality chip persists', () => {
  click('#qualitySeg [data-quality="low"]');
  const saved = JSON.parse(window.localStorage.getItem('roadrush.v2.save')).prefs.quality;
  click('#qualitySeg [data-quality="auto"]');
  return saved === 'low' ? true : saved;
});
t('fx toggle hides scanlines', () => {
  click('#fxSeg [data-fx="off"]');
  const off = el('#scanlines').style.display === 'none';
  click('#fxSeg [data-fx="on"]');
  return off || 'scanlines still shown';
});
t('assist chip toggles', () => {
  const before = g().assist;
  click('#assistChips [data-assist]');
  const after = g().assist;
  click('#assistChips [data-assist]');
  return after !== before ? true : 'assist did not change';
});
t('sound + music toggles persist', () => {
  click('#soundBtn'); click('#musicBtn');
  const s = JSON.parse(window.localStorage.getItem('roadrush.v2.save')).prefs;
  click('#soundBtn'); click('#musicBtn');
  return s.sound === false && s.music === false ? true : JSON.stringify(s);
});
t('help overlay opens and closes', () => {
  click('#helpBtn');
  const open = !hidden('#helpScreen');
  click('#helpCloseBtn');
  const closed = hidden('#helpScreen');
  return open && closed ? true : `open=${open} closed=${closed}`;
});
t('map info panel updates on selection', () => {
  const before = el('#infoBlurb').textContent;
  doc.querySelectorAll('.map-card')[2].dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  frames(2);
  const after = el('#infoBlurb').textContent;
  const len = el('#infoLength').textContent;
  return before !== after && /\d/.test(len) ? true : `${before} -> ${after} (${len})`;
});

/* ---- race + pause + restart ------------------------------------------ */
t('start button enters countdown', () => {
  click('#startBtn');
  const state = g().state;
  return (state === 'COUNTDOWN' && !hidden('#countdownBox')) ? true : `state=${state}`;
});
t('pause freezes the clock, resume restarts it', () => {
  frames(300);           // let the countdown finish
  frames(120);           // ~2 s of racing
  const g0 = g();
  const t0 = g0.raceTime;
  keyOf('KeyP');
  const pausedState = g0.state;
  frames(120);
  const tPaused = g0.raceTime;
  keyUp('KeyP');
  keyOf('KeyP');
  const resumeState = g0.state;
  frames(120);
  const tAfter = g0.raceTime;
  return (pausedState === 'PAUSED' && Math.abs(tPaused - t0) < 1 && resumeState === 'RACING' && tAfter > tPaused + 100)
    ? true : `pausedState=${pausedState} frozen=${tPaused - t0} resume=${resumeState} gained=${tAfter - tPaused}`;
});
t('pause overlay buttons work', () => {
  keyOf('KeyP');
  frames(2);
  const showed = !hidden('#pauseScreen');
  click('#resumeBtn');
  frames(2);
  return showed && hidden('#pauseScreen') ? true : `showed=${showed}`;
});
t('restart key resets the race', () => {
  frames(200);
  const before = g().raceTime;
  keyOf('KeyR');
  frames(3);
  const reset = g().raceTime < before;
  frames(280);           // sit through the new countdown
  return reset ? true : `${before} -> ${g().raceTime}`;
});
t('touch steering reaches the input layer', () => {
  const gg = g();
  const pad = el('#touchPad');
  doc.body.classList.add('touch');
  pointer('#btnGas', 'pointerdown');
  pointer('#btnLeft', 'pointerdown');
  frames(3);
  const input = gg.readInput();
  const gasOn = input.throttle > 0.5;
  const leftOn = input.steer < -0.5;
  pointer('#btnGas', 'pointerup');
  pointer('#btnLeft', 'pointerup');
  frames(2);
  const cleared = gg.readInput().throttle === 0;
  return gasOn && leftOn && cleared ? true : `gas=${gasOn} left=${leftOn} cleared=${cleared}`;
});
t('keyboard steering reaches the input layer', () => {
  keyOf('ArrowUp'); keyOf('ArrowRight');
  frames(3);
  const input = g().readInput();
  keyUp('ArrowUp'); keyUp('ArrowRight');
  return input.throttle > 0.5 && input.steer > 0.5 ? true : JSON.stringify(input);
});
t('nitro drains while held', () => {
  const gg = g();
  gg.nitro = 100;
  keyOf('ArrowUp'); keyOf('Space');
  frames(90);
  const drained = gg.nitro < 96;
  const painted = Number(gg.el.nitroFill.style.width.replace('%', '')) < 100;
  keyUp('Space'); keyUp('ArrowUp');
  return drained && painted ? true : `nitro=${gg.nitro.toFixed(1)} bar=${gg.el.nitroFill.style.width}`;
});
t('hud elements update while racing', () => {
  const gg = g();
  keyOf('ArrowUp');
  frames(60);
  keyUp('ArrowUp');
  const speed = el('#hudSpeed').textContent;
  const gear = el('#hudGear').textContent;
  const gaugeD = el('#gaugeFill').getAttribute('d') || '';
  return Number(speed) > 0 && /^[1-6N]$/.test(gear) && gaugeD.length > 10 ? true : `speed=${speed} gear=${gear} d=${gaugeD.slice(0, 24)}`;
});
t('minimap tracks the player', () => {
  const gg = g();
  const before = el('#miniPlayer').getAttribute('cx');
  frames(200);
  const after = el('#miniPlayer').getAttribute('cx');
  return before !== after ? true : `cx stuck at ${before}`;
});
t('quit to garage returns to the menu', () => {
  keyOf('KeyP');
  frames(2);
  click('#quitBtn');
  frames(3);
  return g().state === 'MENU' && !hidden('#menuScreen') ? true : `${g().state}`;
});
t('records survived the session', () => {
  const save = JSON.parse(window.localStorage.getItem('roadrush.v2.save'));
  return save && save.career && save.records ? true : 'no save';
});
t('debug hud toggles', () => {
  keyOf('KeyG');
  frames(8);
  const on = g().debug;
  keyOf('KeyG');
  return on === true ? true : 'debug flag did not set';
});
t('camera cycle walks all three modes', () => {
  const seen = new Set();
  for (let i = 0; i < 4; i++) { keyOf('KeyC'); seen.add(g().camera); }
  return seen.size === 3 ? true : [...seen].join(',');
});
t('no errors were raised during interactions', () => errors.length === 0 ? true : errors[0]);

console.log(JSON.stringify({ file, errors, results, failed: results.filter((r) => !r.ok) }, null, 1));
