/* ==========================================================================
   ALTHAF // DEVELOPER PORTFOLIO & GITHUB UPGRADE STUDIO
   ========================================================================== */

const ASSET_BASE =
  "https://raw.githubusercontent.com/althaf786313/racing-game/arena/ecf6f967-racing-game/profile-kit/assets";

const TERMINAL_OUTPUTS = {
  whoami: `$ whoami --verbose
  Name      : Althaf (@althaf786313)
  Role      : Software Engineer & Builder
  Focus     : Interactive Web Runtimes, Python Automation & Canvas Engines
  Mindset   : Master core fundamentals -> build clean, playable software.`,

  projects: `$ ls -lh ~/github/althaf786313/
  drwxr-xr-x  python-mastery-hub/   122.7 KB  [LIVE] Pyodide IDE + 75p Ebook + 100+ Projects
  drwxr-xr-x  pip-studio/            65.9 KB  [FULL-STACK] Flask + Manim + Piper TTS + FFmpeg
  drwxr-xr-x  racing-game/           54.5 KB  [PLAYABLE] 5-Biome Canvas Racer + Web Audio Synth`,

  stack: `$ cat stack.json
{
  "languages": ["Python", "JavaScript (ES6+)", "HTML5", "CSS3", "Bash"],
  "engines":   ["Flask REST", "Pyodide WASM", "Manim", "Piper TTS", "FFmpeg", "Canvas 2D"],
  "workflow":  ["Git", "GitHub Actions", "GitHub Pages", "Vercel", "Linux"]
}`,

  pipeline: `$ ./pip-studio --architecture
  [1] Scene JSON / AI Assistant Bridge
         └──> [2] Manim Pro OR Pillow Cartoon Frame Engine
         └──> [3] Offline Piper Neural TTS (+ Edge-TTS Fallback)
                 └──> [4] FFmpeg Muxer -> Downloadable HD MP4 Video`
};

const BIOMES = [
  {
    id: "sunset",
    name: "Sunset Highway",
    difficulty: "Easy",
    grip: "1.00x Grip",
    traffic: "0.8x Traffic",
    weather: "Golden-Hour Clear",
    desc: "Smooth coastal highway with warm golden sunlight, palm silhouettes, and sweeping bends."
  },
  {
    id: "cyber",
    name: "Neon Cyber City",
    difficulty: "Medium",
    grip: "0.90x Grip",
    traffic: "1.2x Traffic",
    weather: "Neon Rain & Boost Grids",
    desc: "Rain-slick cyberpunk grid lined with skyscrapers, speed pads, and holographic lane markers."
  },
  {
    id: "desert",
    name: "Desert Dust Storm",
    difficulty: "Hard",
    grip: "0.82x Grip",
    traffic: "1.0x Traffic",
    weather: "Swirling Sandstorm",
    desc: "Red canyon highway cutting through dense sandstorms with reduced horizon visibility."
  },
  {
    id: "alpine",
    name: "Alpine Snow Pass",
    difficulty: "Extreme",
    grip: "0.68x Grip",
    traffic: "0.7x Traffic",
    weather: "Snowfall & Black Ice",
    desc: "High-altitude mountain pass requiring careful counter-steering across slippery ice patches."
  },
  {
    id: "midnight",
    name: "Midnight Thunder",
    difficulty: "Hard",
    grip: "0.85x Grip",
    traffic: "1.1x Traffic",
    weather: "Headlights & Lightning",
    desc: "Pitch-dark forest highway illuminated by bike headlights and sudden lightning flashes."
  }
];

const REPO_POLISH_DATA = [
  {
    repo: "python-mastery-hub",
    url: "https://github.com/althaf786313/python-mastery-hub",
    homepage: "https://althaf786313.github.io/python-mastery-hub/",
    desc: "Interactive dark-mode Python learning platform: 75-page ebook, 100+ runnable projects, in-browser Pyodide + Matplotlib runner & ATS resume builder.",
    topics: ["python", "pyodide", "webassembly", "interactive-learning", "matplotlib", "edtech", "github-pages"]
  },
  {
    repo: "pip-studio",
    url: "https://github.com/althaf786313/pip-studio",
    homepage: "",
    desc: "All-in-one Python animated video studio uniting Manim Pro, custom Pillow cartoon scenes, offline Piper TTS voiceover & FFmpeg MP4 rendering via Flask API.",
    topics: ["python", "flask", "manim", "ffmpeg", "text-to-speech", "piper-tts", "video-generation", "automation"]
  },
  {
    repo: "racing-game",
    url: "https://github.com/althaf786313/racing-game",
    homepage: "https://althaf786313.github.io/racing-game/",
    desc: "Road Rush: Sunset & Beyond — Zero-dependency pseudo-3D HTML5 Canvas bike racing game with 5 weather biomes & real-time Web Audio API synthesis.",
    topics: ["html5-canvas", "javascript", "gamedev", "web-audio-api", "racing-game", "arcade", "zero-dependencies"]
  },
  {
    repo: "Tilawat-E-Quran",
    url: "https://github.com/althaf786313/Tilawat-E-Quran",
    homepage: "",
    desc: "Clean, distraction-free Quran recitation & reading experience built for clarity and accessibility.",
    topics: ["quran", "audio-player", "web-app", "islamic-tech"]
  }
];

let toastTimer = null;
function showToast(msg) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.add("visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("visible"), 2400);
}

async function copyText(text, label) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      showToast(`Copied ${label}!`);
      return;
    }
  } catch (_) {
    // Fall back to hidden textarea copy for iframe environments
  }
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.style.position = "fixed";
  ta.style.opacity = "0";
  document.body.appendChild(ta);
  ta.focus();
  ta.select();
  try {
    document.execCommand("copy");
    showToast(`Copied ${label}!`);
  } catch (_) {
    showToast("Select text in the Raw README tab to copy");
  }
  document.body.removeChild(ta);
}

/* 1. Terminal Command Switcher */
function initTerminal() {
  const out = document.getElementById("terminalOutput");
  out.textContent = TERMINAL_OUTPUTS.whoami;

  document.querySelectorAll(".cmd-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".cmd-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      out.textContent = TERMINAL_OUTPUTS[btn.dataset.cmd] || "";
    });
  });
}

/* 2. Project Filter Pills */
function initProjectFilters() {
  document.querySelectorAll(".filter-pill").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-pill").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const filter = btn.dataset.filter;
      document.querySelectorAll(".project-card").forEach((card) => {
        const cats = card.dataset.category.split(" ");
        card.hidden = filter !== "all" && !cats.includes(filter);
      });
    });
  });
}

/* 3. Biome Physics Strip & Embedded Road Rush Launcher */
function initArcade() {
  const strip = document.getElementById("biomeStrip");
  const readout = document.getElementById("biomeReadout");

  function selectBiome(biome) {
    strip.querySelectorAll(".biome-chip").forEach((c) => {
      c.classList.toggle("active", c.dataset.id === biome.id);
    });
    readout.innerHTML = `
      <div>
        <strong style="color:var(--ink)">${biome.name}</strong>
        <span style="color:var(--muted);margin-left:8px">${biome.desc}</span>
      </div>
      <div class="biome-stats">
        <span>[${biome.difficulty}]</span>
        <span>${biome.grip}</span>
        <span>${biome.traffic}</span>
        <span>${biome.weather}</span>
      </div>
    `;
  }

  BIOMES.forEach((b) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "biome-chip";
    btn.dataset.id = b.id;
    btn.textContent = b.name;
    btn.addEventListener("click", () => selectBiome(b));
    strip.appendChild(btn);
  });
  selectBiome(BIOMES[0]);

  function launchGame() {
    const cover = document.getElementById("arcadeCover");
    const frame = document.getElementById("arcadeFrame");
    if (!frame.getAttribute("src")) {
      frame.setAttribute("src", "./road-rush/index.html");
    }
    cover.style.display = "none";
    frame.focus();
  }

  document.getElementById("launchArcadeBtn").addEventListener("click", launchGame);
  document.getElementById("coverLaunchBtn").addEventListener("click", launchGame);
  document.getElementById("heroPlayBtn").addEventListener("click", () => {
    setTimeout(launchGame, 250);
  });
  document.getElementById("cardPlayBtn").addEventListener("click", () => {
    setTimeout(launchGame, 250);
  });
}

/* 4. Live GitHub Profile Upgrade Studio */
function buildMarkdown(state) {
  const portfolioUrl = state.portfolio.trim() || "https://althaf786313.github.io/racing-game/portfolio/";
  const linkedinUrl = state.linkedin.trim() || "https://linkedin.com/in/YOUR-LINKEDIN-HANDLE";
  const emailVal = state.email.trim() || "your.email@example.com";
  const xUrl = state.x.trim() || "https://x.com/YOUR-X-HANDLE";
  const nameVal = state.name.trim() || "Althaf";

  return `<div align="center">

<!-- HERO DASHBOARD BANNER -->
<img src="${ASSET_BASE}/hero-banner.svg" alt="${nameVal} — Software Engineer & Builder" width="100%" />

<br />

<!-- QUICK CONNECT & LIVE APP BADGES -->
<p align="center">
  <a href="${portfolioUrl}">
    <img src="https://img.shields.io/badge/PORTFOLIO-ALTHAF.DEV-00f59b?style=for-the-badge&labelColor=0b1120&logo=vercel&logoColor=00f59b" alt="Live Portfolio" />
  </a>
  <a href="https://althaf786313.github.io/python-mastery-hub/">
    <img src="https://img.shields.io/badge/LIVE_APP-PYTHON_MASTERY_HUB-00f0ff?style=for-the-badge&labelColor=0b1120&logo=python&logoColor=00f0ff" alt="Python Mastery Hub" />
  </a>
  <a href="${linkedinUrl}">
    <img src="https://img.shields.io/badge/LINKEDIN-CONNECT-38bdf8?style=for-the-badge&labelColor=0b1120&logo=linkedin&logoColor=38bdf8" alt="LinkedIn" />
  </a>
  <a href="mailto:${emailVal}">
    <img src="https://img.shields.io/badge/EMAIL-CONTACT_ME-dcff58?style=for-the-badge&labelColor=0b1120&logo=gmail&logoColor=dcff58" alt="Email" />
  </a>
  <a href="${xUrl}">
    <img src="https://img.shields.io/badge/X_%2F_TWITTER-FOLLOW-ff2a85?style=for-the-badge&labelColor=0b1120&logo=x&logoColor=ff2a85" alt="X / Twitter" />
  </a>
</p>

</div>

---

### \`>//\` About Me

Hi, I'm **${nameVal}** — a **Software Engineer & Builder** focused on turning core computer science fundamentals into fast, interactive software people can actually run in one click.

- **What I build:** Browser-native learning environments (**Pyodide / WebAssembly**), full-stack **Python media automation pipelines** (**Flask + Manim + TTS + FFmpeg**), and zero-dependency **HTML5 Canvas & Web Audio** engines.
- **How I work:** Learn deeply by shipping end-to-end projects — clean architecture, minimal bloat, responsive UIs, and working live demos.
- **Currently sharpening:** Full-stack web engineering, Python backend automation, interactive data/graphics programming, and system design.
- **Collaboration:** Always excited to collaborate on open-source developer tools, educational tech, creative web apps, and Python automation projects.

---

### \`>//\` Live Engineering Telemetry

<div align="center">
  <img src="${ASSET_BASE}/telemetry-card.svg" alt="GitHub Engineering Telemetry" width="100%" />
</div>

---

### \`>//\` Featured Shipped Projects

<div align="center">
  <a href="https://althaf786313.github.io/python-mastery-hub/">
    <img src="${ASSET_BASE}/card-python-hub.svg" alt="Python Mastery Hub — Live App" width="49%" />
  </a>
  <a href="https://github.com/althaf786313/pip-studio">
    <img src="${ASSET_BASE}/card-pip-studio.svg" alt="Pip Studio — Full-Stack Video Studio" width="49%" />
  </a>
  <br />
  <a href="https://github.com/althaf786313/racing-game">
    <img src="${ASSET_BASE}/card-road-rush.svg" alt="Road Rush — Sunset & Beyond" width="49%" />
  </a>
  <a href="${portfolioUrl}">
    <img src="${ASSET_BASE}/card-portfolio.svg" alt="${nameVal} Developer Portfolio" width="49%" />
  </a>
</div>

| Project | Architecture & Highlights | Stack | Links |
| :--- | :--- | :--- | :---: |
| **Python Mastery Hub** | 75-page interactive Python ebook + **100+ runnable projects**, side-by-side browser code runner powered by **Pyodide + Skulpt**, live **Matplotlib** charts, AI transcriber, certificate generator & ATS resume builder. | \`Python\` \`Pyodide\` \`HTML5\` \`CSS3\` \`JavaScript\` | [Live Demo](https://althaf786313.github.io/python-mastery-hub/) · [Repo](https://github.com/althaf786313/python-mastery-hub) |
| **Pip Studio** | All-in-one animated video studio uniting **Manim Pro** & custom **Pillow cartoon frame animation**, offline **Piper TTS** (+ Edge-TTS), and **FFmpeg** MP4 muxing behind a **Flask REST API** & AI Assistant Bridge. | \`Python\` \`Flask\` \`Manim\` \`Piper TTS\` \`FFmpeg\` | [Repo](https://github.com/althaf786313/pip-studio) |
| **Road Rush: Sunset & Beyond** | Zero-dependency pseudo-3D arcade bike racing game featuring **5 dynamic weather biomes** (Sunset, Cyber Rain, Desert Storm, Alpine Ice, Midnight Thunder), real-time **Web Audio API** sound synthesis & touch controls. | \`HTML5 Canvas\` \`ES6 JS\` \`Web Audio API\` \`CSS3\` | [Play Live](https://althaf786313.github.io/racing-game/) · [Repo](https://github.com/althaf786313/racing-game) |

---

### \`>//\` Tech Stack & Tooling

**Languages & Core**

![Python](https://img.shields.io/badge/Python-dcff58?style=flat-square&logo=python&logoColor=080b12)
![JavaScript](https://img.shields.io/badge/JavaScript_ES6+-00f0ff?style=flat-square&logo=javascript&logoColor=080b12)
![HTML5](https://img.shields.io/badge/HTML5-ff8054?style=flat-square&logo=html5&logoColor=080b12)
![CSS3](https://img.shields.io/badge/CSS3-38bdf8?style=flat-square&logo=css3&logoColor=080b12)
![Bash](https://img.shields.io/badge/Bash_%2F_Shell-00f59b?style=flat-square&logo=gnubash&logoColor=080b12)

**Frameworks, Engines & Media Pipelines**

![Flask](https://img.shields.io/badge/Flask_REST_API-111827?style=flat-square&logo=flask&logoColor=00f0ff)
![Pyodide](https://img.shields.io/badge/Pyodide_WASM-111827?style=flat-square&logo=webassembly&logoColor=dcff58)
![Matplotlib](https://img.shields.io/badge/Matplotlib-111827?style=flat-square&logo=plotly&logoColor=38bdf8)
![Manim](https://img.shields.io/badge/Manim_Animation-111827?style=flat-square&logo=python&logoColor=dcff58)
![FFmpeg](https://img.shields.io/badge/FFmpeg_Video-111827?style=flat-square&logo=ffmpeg&logoColor=00f59b)
![Canvas 2D](https://img.shields.io/badge/HTML5_Canvas_%26_Web_Audio-111827?style=flat-square&logo=html5&logoColor=ff2a85)

**Developer Workflow & Deployment**

![Git](https://img.shields.io/badge/Git-111827?style=flat-square&logo=git&logoColor=ff8054)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-111827?style=flat-square&logo=githubactions&logoColor=00f0ff)
![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-111827?style=flat-square&logo=githubpages&logoColor=dcff58)
![Vercel](https://img.shields.io/badge/Vercel-111827?style=flat-square&logo=vercel&logoColor=ffffff)
![Linux](https://img.shields.io/badge/Linux-111827?style=flat-square&logo=linux&logoColor=ffb800)

---

<div align="center">
  <sub>Crafted by <strong>${nameVal} (@althaf786313)</strong> • Always learning, always shipping.</sub>
</div>
`;
}

function initUpgradeStudio() {
  const inputs = {
    name: document.getElementById("inpName"),
    portfolio: document.getElementById("inpPortfolio"),
    linkedin: document.getElementById("inpLinkedin"),
    email: document.getElementById("inpEmail"),
    x: document.getElementById("inpX")
  };

  const bioText =
    "Software Engineer & Builder • Crafting interactive web apps, Python media pipelines & browser games • Always learning & shipping.";

  const bioPreview = document.getElementById("bioPreviewText");
  const bioCounter = document.getElementById("bioCounter");
  bioPreview.textContent = bioText;
  bioCounter.textContent = `${bioText.length} / 160`;

  const readmeTa = document.getElementById("readmeTextarea");
  const liveBadges = document.getElementById("liveBadgesPreview");

  function refresh() {
    const state = {
      name: inputs.name.value,
      portfolio: inputs.portfolio.value,
      linkedin: inputs.linkedin.value,
      email: inputs.email.value,
      x: inputs.x.value
    };
    readmeTa.value = buildMarkdown(state);

    liveBadges.innerHTML = `
      <a class="badge badge-cyan" href="${state.portfolio}" target="_blank" rel="noopener">PORTFOLIO // ALTHAF.DEV ↗</a>
      <a class="badge badge-lime" href="https://althaf786313.github.io/python-mastery-hub/" target="_blank" rel="noopener">LIVE APP // PYTHON MASTERY HUB ↗</a>
      <a class="badge badge-cyan" href="${state.linkedin}" target="_blank" rel="noopener">LINKEDIN // CONNECT ↗</a>
      <a class="badge badge-lime" href="mailto:${state.email}">EMAIL // ${state.email}</a>
      <a class="badge badge-pink" href="${state.x}" target="_blank" rel="noopener">X // FOLLOW ↗</a>
    `;
  }

  Object.values(inputs).forEach((inp) => inp.addEventListener("input", refresh));
  refresh();

  document.getElementById("copyBioBtn").addEventListener("click", () => copyText(bioText, "GitHub Bio"));
  document.getElementById("topCopyReadmeBtn").addEventListener("click", () =>
    copyText(readmeTa.value, "Profile README.md")
  );
  document.getElementById("barCopyReadmeBtn").addEventListener("click", () =>
    copyText(readmeTa.value, "Profile README.md")
  );

  // Studio Tabs
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const target = btn.dataset.tab;
      ["preview", "markdown", "repos"].forEach((id) => {
        document.getElementById(`panel-${id}`).hidden = id !== target;
      });
    });
  });

  // Repo Polish Cheat Sheet
  const repoContainer = document.getElementById("repoPolishList");
  REPO_POLISH_DATA.forEach((item) => {
    const div = document.createElement("div");
    div.className = "repo-polish-item";
    div.innerHTML = `
      <div class="repo-polish-head">
        <a href="${item.url}" target="_blank" rel="noopener"><strong>althaf786313/${item.repo} ↗</strong></a>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <button type="button" class="btn btn-cyan btn-sm" data-copy-desc>Copy Description</button>
          <button type="button" class="btn btn-ghost btn-sm" data-copy-topics>Copy Topics</button>
        </div>
      </div>
      <p class="repo-polish-desc">${item.desc}</p>
      <div class="chip-row" style="margin-bottom:0">
        ${item.topics.map((t) => `<span class="chip">#${t}</span>`).join("")}
      </div>
    `;
    div.querySelector("[data-copy-desc]").addEventListener("click", () =>
      copyText(item.desc, `${item.repo} description`)
    );
    div.querySelector("[data-copy-topics]").addEventListener("click", () =>
      copyText(item.topics.join(", "), `${item.repo} topics`)
    );
    repoContainer.appendChild(div);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initTerminal();
  initProjectFilters();
  initArcade();
  initUpgradeStudio();
});
