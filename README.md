# ROAD RUSH — Sunset & Beyond

A single-file, dependency-free pseudo-3D arcade motorbike racer. Open `index.html`
in any modern browser (desktop, tablet or phone) and ride — no build step, no
server, no assets. Everything (art, sound, music, tracks) is generated in code.

```
open index.html          # macOS
xdg-open index.html      # Linux
# or serve it:  python3 -m http.server 8080
```

## What is in the box

**Five tracks, five weather systems** — each with its own road layout, not a
recolour:

| Track | Conditions | Character |
| --- | --- | --- |
| Sunset Highway | Dry, golden hour | Wide sweepers, long sight lines |
| Neon Cyber City | Rain, 4 lanes | Fast, greasy, heavy traffic, blind crests |
| Desert Dust Storm | Sandstorm, low visibility | Narrow canyon switchbacks |
| Alpine Snow Pass | Snow and ice | 2 lanes, steep descent, very low grip |
| Midnight Thunder | Night, lightning | Headlight only, flowing and fast |

**Riding model** — 6-speed gearbox with a live power band, rpm-driven engine
note, nitro with overdrive, engine braking, quadratic drag, hill grade
resistance, low/high-side lateral slip that depends on weather grip, airtime
over crests, steering scrub, slipstream tow behind rivals, barrier grind,
damage model that costs you pace, and a launch meter for the standing start.

**Opponents** — 7-9 AI rivals with individual skill, lane changes, traffic
avoidance, corner braking and light rubber-banding (strictly bounded, so they
never teleport), plus lane-keeping traffic cars and trucks.

**Game feel** — clean-pass combo scoring, near-miss bonuses, lap records,
damage, DNFs, per-track records in `localStorage`, a career ladder
(Rookie → Semi-Pro → Pro → Ace → Legend), race feed toasts, minimap,
analogue tachometer, rev lights, speed trap, three cameras, three difficulties,
three race lengths and optional assists.

**Presentation** — parallax backdrops per track, procedural sprite atlases,
rain with road spray, drifting snow, rolling dust, lightning with thunder,
wet-road sheen, headlight cone, speed streaks, camera shake, damage flash,
device-pixel-ratio aware rendering and automatic quality scaling.

**Procedural audio** — Web Audio only: layered engine (three oscillators,
moving lowpass, intake noise, sub), wind and tyre-skid loops, plus a
16-step synth groove whose tempo tracks how fast you are going, and SFX for
shifts, crashes, barriers, nitro, overtakes, laps, lightning and the finish.

## Controls

| Action | Keys |
| --- | --- |
| Throttle | `W` / `↑` (or gamepad RT) |
| Brake / reverse | `S` / `↓` (gamepad LT) |
| Steer | `A` `D` / `←` `→` (gamepad stick) |
| Nitrous | `Space` (gamepad A) |
| Pause | `P` / `Esc` |
| Restart | `R` |
| Mute / music | `M` / `N` |
| Camera | `C` |
| Fullscreen | `F` |
| Debug HUD | `G` |
| How to play | `H` |

Touch controls appear automatically on coarse-pointer devices.

## Tests

The repo ships the headless harnesses that were used to verify the game. They
need Node and jsdom (`npm i jsdom` in the repo root), and they drive the real
game through a stubbed canvas/Web Audio environment — including an autopilot
that races using the game's own input layer.

```bash
node tools/geometry.mjs index.html                 # projection + HUD maths
node tools/interactions.mjs index.html             # pause, restart, touch, settings
node tools/run.mjs index.html --autopilot          # races every track, prints results
DIFF=legend RUNS=1 node tools/run.mjs index.html --autopilot
```

`run.mjs` prints lap times, finishing position, damage, rival gaps and canvas
draw-call counts per race; it exits non-zero if a race fails to finish or any
check fails.

---

## Upgrade log — what changed from the original export

The original single-file build had a fatal defect and a long list of smaller
ones. Everything below was found with the harnesses above, then fixed.

### Showstoppers

- **The game never ran.** `render()` read `this.segments[NaN].index` on the very
  first frame (the menu state has no track built), which threw every frame and
  killed the `requestAnimationFrame` chain before it could re-arm. The canvas
  stayed blank and nothing responded. The renderer now handles having no track
  and the loop is exception-proof.
- **The results screen always showed placeholder HTML** (rank `1st`, time
  `01:42.50`, speed `285 KM/H`, score `14,200`) for every track: `finishRace`
  wrote to the DOM with `innerText`, which silently no-ops in some engines.
  All HUD/results writes now use `textContent`, and every value is computed.
- **Top speed reported was the cap, not your speed** — `resSpeed` printed
  `this.maxSpeed`. It now reports the fastest speed actually achieved.

### Gameplay

- Fixed-step `dt = 1/60` ignored real frame time, so the sim ran **twice as fast
  on a 120 Hz display**; timing now uses an accumulator with a capped catch-up
  and lap times are measured in simulation time, not wall-clock.
- The race clock started during the **countdown**, adding ~3.6 s to every time.
- Rank was computed from raw `z` only (rivals never had laps), so the position
  display was meaningless; racers now carry lap + distance and are ranked on
  total progress.
- All five "tracks" shared **one identical layout** — they differed only in
  colour. Each track now has its own segment layout, width, lane count, grip,
  acceleration and top speed.
- Laps were a fixed 2 and races lasted ~20 seconds; tracks are now 1.5-2.1 km
  with 2/3/5-lap options (~50 s to 2.5 min races).
- Added: pause, restart, cameras, difficulties, assists, airtime, slipstream,
  combo scoring, per-track records, career stats, launch meter, DNF handling,
  health regen rules and a damage penalty on acceleration.
- Collisions could fire on consecutive frames and stack damage instantly; they
  now have per-vehicle cooldowns, relative-speed damage, a lateral push and
  particle/sound feedback.

### Engine and rendering

- Added **devicePixelRatio scaling** (the original was blurry on every Retina
  and mobile display) and a live quality controller (draw distance, particle
  density, DPR cap, sprite tier) that reacts to measured frame rate.
- The camera is now smoothed and offset with a look-ahead, the bike is drawn at
  its true lateral position on the road instead of always dead centre, and
  sprites/vehicles are projected in road-width space so props scale correctly
  on narrow and wide tracks.
- Cached sprite atlases (each roadside prop is rasterised once per track),
  cached sky gradients, memoised colour strings, occlusion culling for the far
  field, layered rumbles/edge lines into single paths, and DOM writes that only
  happen when a value actually changes.
- Traffic, rain, snow, dust and lightning are time-based particle systems
  instead of per-frame `Math.random()` (which flickered and was frame-rate
  dependent).

### Audio

- The original had one oscillator, one noise loop and two one-shot effects.
  There is now a full mixer with separate engine/SFX/music buses, a compressor,
  a gear-and-throttle-driven engine voice, tyre skid, wind, a tempo-reactive
  synth soundtrack, countdown beeps, shift blips, a finish fanfare and panning
  pass-by whooshes — all still synthesised, no files.

### UI, input and accessibility

- Rebuilt the page as a three-column cockpit (career/records rail, stage,
  track-setup rail) with a toolbar, a proper map grid previewing each layout
  shape with best laps, and per-track briefings.
- Corrected controls: pointer events (touch, pen, mouse) with capture, stuck-key
  fix on blur/visibility change, gamepad support, `Esc`/`P` pause, and keys
  cleared when the tab loses focus. The old build polled `touchstart` only and
  left keys stuck after a tab switch.
- Accessibility: `aria-pressed` state on every toggle, `aria-label`s on icon
  buttons, a polite live region announcing laps and the finish, visible focus
  rings, `prefers-reduced-motion` support, a `<noscript>` fallback, keyboard
  reachable menu, and no more `user-scalable=no` lockout.

### Save data

- One integer (`roadrush_top_score`) became a versioned save with per-track lap
  and race records, wins, career totals, and preferences (livery, track,
  difficulty, laps, camera, quality, FX, assists, sound, music) that persist
  across sessions. Legacy scores are migrated on first load.

### Also fixed while in there

- `varColor('--acid')` returned `''` in engines without CSS custom-property
  support and the bike fairing went black; colours are now literal, so the
  canvas no longer depends on `getComputedStyle`.
- The Alpine "Cockpit" camera button carried `data-cam="hood"`, so the cockpit
  view was unreachable from the UI (caught by `tools/interactions.mjs`).
- Toasts, the results order chart, min/max clamping on `playerX`, off-road
  speed caps, reverse handling, "engine braking" that pushed the bike backwards
  at a standstill, and a countdown that kept writing to `undefined` elements.
