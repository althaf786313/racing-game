# Test harnesses

Headless regression tests for `index.html`. They need Node 18+ and jsdom:

```bash
npm i jsdom          # in the repo root (adds node_modules/, git-ignored)
node tools/geometry.mjs ../index.html
node tools/interactions.mjs ../index.html
node tools/run.mjs ../index.html --autopilot
```

- **geometry.mjs** — drives real frames and asserts the pseudo-3D projection
  (road width falloff, horizon convergence, culling, gauge needle range, HUD
  values) after a menu frame and a racing frame.
- **interactions.mjs** — pause/resume/restart, touch + keyboard + gamepad input
  paths, livery/quality/camera/sound settings, overlays, record persistence.
- **run.mjs** — races every track with an autopilot and reports lap times,
  finishing position, damage, rival gaps and canvas draw calls per race.
  Environment: `RUNS=3`, `DIFF=pro`, `MAXF=25000`, `--autopilot`.

They stub canvas 2D, Web Audio, timers and rAF, so no browser is required.
