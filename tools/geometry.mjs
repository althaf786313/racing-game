// Projection sanity: run real frames, then assert the road geometry the
// renderer produced (screen y ordering, road width falloff, horizon, bike).
import fs from 'node:fs';
import { JSDOM, VirtualConsole } from 'jsdom';
const file = process.argv[2];
const html = fs.readFileSync(file, 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const vc = new VirtualConsole();
const errors = [];
vc.on('jsdomError', (e) => errors.push(String(e.message).slice(0, 120)));
const dom = new JSDOM(html, { runScripts: 'outside-only', pretendToBeVisual: true, virtualConsole: vc, url: 'https://example.test/' });
const { window } = dom, doc = window.document;
let vnow = 0; const timers = []; let tid = 1;
window.setTimeout = (cb, ms = 0, ...a) => { const id = tid++; timers.push({ id, cb, time: vnow + (ms || 0) }); return id; };
window.setInterval = (cb, ms = 0) => { const id = tid++; timers.push({ id, cb, time: vnow + (ms || 1), every: ms || 1 }); return id; };
window.clearTimeout = window.clearInterval = (id) => { const i = timers.findIndex((t) => t.id === id); if (i >= 0) timers.splice(i, 1); };
const runTimers = () => { for (const t of [...timers]) { if (t.time > vnow) continue; if (t.every) t.time = vnow + t.every; else timers.splice(timers.indexOf(t), 1); try { t.cb(); } catch (e) {} } };
window.performance.now = () => vnow;
window.Date.now = () => vnow;
const grad = () => ({ addColorStop() {} });
window.HTMLCanvasElement.prototype.getContext = () => new Proxy({}, { get(t, p) {
  if (p === 'canvas') return { width: 1280, height: 720 };
  if (typeof p === 'symbol') return undefined;
  if (typeof p === 'string' && /Style|lineWidth|font|Alpha|Composite|Shadow|align|Baseline|Cap|Join|Limit|direction|filter|dash/i.test(p)) return t[p] ?? '';
  if (/Gradient|Pattern/.test(String(p))) return grad;
  if (p === 'measureText') return () => ({ width: 10 });
  if (p in t) return t[p];
  return () => {};
}, set(t, p, v) { t[p] = v; return true; } });
const dim = (v) => ({ get: () => v, configurable: true });
Object.defineProperty(window.HTMLElement.prototype, 'clientWidth', dim(1280));
Object.defineProperty(window.HTMLElement.prototype, 'clientHeight', dim(720));
window.HTMLElement.prototype.getBoundingClientRect = () => ({ width: 1280, height: 720, top: 0, left: 0, right: 1280, bottom: 720, x: 0, y: 0 });
class P { constructor(v = 0) { this.value = v; } setValueAtTime(v) { this.value = v; return this; } linearRampToValueAtTime(v) { this.value = v; return this; } exponentialRampToValueAtTime(v) { this.value = v; return this; } setTargetAtTime(v) { this.value = v; return this; } cancelScheduledValues() { return this; } }
class N { constructor() { this.frequency = new P(); this.gain = new P(); this.Q = new P(); this.pan = new P(); this.playbackRate = new P(); } connect() { return arguments[0]; } disconnect() {} start() {} stop() {} }
window.AudioContext = class { constructor() { this.currentTime = 0; this.sampleRate = 48000; this.destination = new N(); this.state = 'running'; } createOscillator() { return new N(); } createGain() { return new N(); } createBiquadFilter() { return new N(); } createBufferSource() { return new N(); } createBuffer(c, l, r) { return { length: l, sampleRate: r, getChannelData: () => new Float32Array(l) }; } createStereoPanner() { return new N(); } createDynamicsCompressor() { return new N(); } resume() { return Promise.resolve(); } suspend() { return Promise.resolve(); } };
window.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {} });
doc.exitFullscreen = () => Promise.resolve();
const raf = [];
window.requestAnimationFrame = (cb) => { raf.push(cb); return raf.length; };
const frames = (n) => { for (let i = 0; i < n; i++) { vnow += 16.7; runTimers(); raf.splice(0, raf.length).forEach((cb) => { try { cb(vnow); } catch (e) { errors.push(String(e.message).slice(0, 140)); } }); } };
window.eval(script);
doc.dispatchEvent(new window.Event('DOMContentLoaded', { bubbles: true }));
window.dispatchEvent(new window.Event('load'));
const g = window.roadrush;
const checks = [];
const check = (name, ok, detail) => checks.push({ name, ok: !!ok, detail: ok ? '' : String(detail) });
const W = 1280, H = 720;

frames(30);
checks.push({ name: 'game object exposed', ok: !!g, detail: g ? '' : 'window.roadrush missing' });
if (g) {
  // menu attract mode geometry
  const segs = g.track.segments;
  const base = g.segmentAt(g.camZ);
  g.ren.render(16.7, 1);
  // the first segment the renderer actually draws (everything nearer is culled)
  const camDepth = g.ren.fovDepth;
  let n0 = 1;
  while (segs[(base.index + n0) % segs.length].p1.camera.z <= camDepth && n0 < 40) n0++;
  const near = segs[(base.index + n0) % segs.length], mid = segs[(base.index + 60) % segs.length], far = segs[(base.index + 180) % segs.length];
  check('first drawn segment sits at the bottom of the frame', near.p1.screen.y > H * 0.75, `n0=${n0} y=${near.p1.screen.y.toFixed(0)}`);
  check('road narrows with distance', near.p1.screen.w > mid.p1.screen.w && mid.p1.screen.w > far.p1.screen.w,
    `${near.p1.screen.w.toFixed(0)} / ${mid.p1.screen.w.toFixed(0)} / ${far.p1.screen.w.toFixed(0)}`);
  check('far segments converge toward the horizon', far.p2.screen.y < H * 0.62 && far.p2.screen.y > H * 0.2,
    `y=${far.p2.screen.y.toFixed(0)} of ${H}`);
  check('drawn road centre is near the middle of the frame', Math.abs(near.p1.screen.x - W / 2) < W * 0.3, `x=${near.p1.screen.x.toFixed(0)}`);
  check('camera-space depth grows with distance', mid.p1.camera.z > near.p1.camera.z && far.p1.camera.z > mid.p1.camera.z,
    `${near.p1.camera.z.toFixed(0)} / ${mid.p1.camera.z.toFixed(0)} / ${far.p1.camera.z.toFixed(0)}`);
  check('segments in front of the near plane are never drawn', segs.every((s) => !isFinite(s.p1.screen.scale) || s.p1.screen.y > -1e5));

  // race geometry
  doc.querySelector('#startBtn').dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  frames(260);   // countdown
  g.keyBuffer.ArrowUp = true;
  frames(180);
  const b = g.segmentAt(g.playerZ);
  check('player advances along the track', g.playerZ > 0, `z=${g.playerZ.toFixed(0)}`);
  check('speed is climbing under throttle', g.speed > 40, `speed=${g.speed.toFixed(1)}`);
  check('race clock is running', g.raceTime > 1000, `t=${g.raceTime}`);
  check('player x stays on the road under autopilot-free throttle', Math.abs(g.playerX) < 1.4, `x=${g.playerX.toFixed(2)}`);
  check('hud speed text matches model', Math.abs(Number(doc.querySelector('#hudSpeed').textContent) - Math.abs(g.speed)) < 2,
    `hud=${doc.querySelector('#hudSpeed').textContent} model=${g.speed.toFixed(0)}`);
  check('gauge needle angle is inside the dial', (() => {
    const m = /rotate\(([-\d.]+)/.exec(doc.querySelector('#gaugeNeedle').getAttribute('transform') || '');
    const a = m ? parseFloat(m[1]) : NaN;
    return a >= -121 && a <= 121;
  })(), doc.querySelector('#gaugeNeedle').getAttribute('transform'));
  check('progress bar advances', parseFloat(doc.querySelector('#progressBar').style.width) > 0, doc.querySelector('#progressBar').style.width);
  check('minimap path was built from the layout', (doc.querySelector('#miniTrack').getAttribute('d') || '').split('L').length > 20);
  check('no runtime errors', errors.length === 0, errors[0]);
}
console.log(JSON.stringify({ file, checks, failed: checks.filter((c) => !c.ok), errors: errors.slice(0, 4), trace: g ? { state: g.state, drawn: g.ren.segmentsDrawn, speed: +g.speed.toFixed(1), lap: g.lap, z: Math.round(g.playerZ) } : null }, null, 1));
process.exit(checks.some((c) => !c.ok) ? 1 : 0);
