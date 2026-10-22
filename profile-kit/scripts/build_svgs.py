#!/usr/bin/env python3
"""
Builds all custom Dark Neon SVG assets for:
  1) profile-kit/assets/ (GitHub Profile README hero + 4 clickable project cards)
  2) assets/road-rush-banner.svg (Road Rush repository banner)
Validates every generated file with xml.etree.ElementTree to guarantee 100% valid XML.
"""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILE_ASSETS = REPO_ROOT / "profile-kit" / "assets"
GAME_ASSETS = REPO_ROOT / "assets"


def build_hero_banner() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="330" viewBox="0 0 1200 330" fill="none" role="img" aria-label="Althaf - Software Engineer and Builder">
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="1200" y2="330" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#060911"/>
      <stop offset="52%" stop-color="#0b1120"/>
      <stop offset="100%" stop-color="#070a12"/>
    </linearGradient>
    <linearGradient id="frameGrad" x1="0" y1="0" x2="1200" y2="330" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#00f0ff" stop-opacity="0.65"/>
      <stop offset="50%" stop-color="#dcff58" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#ff2a85" stop-opacity="0.65"/>
    </linearGradient>
    <linearGradient id="scanBeam" x1="0" y1="0" x2="360" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#00f0ff" stop-opacity="0"/>
      <stop offset="50%" stop-color="#00f0ff" stop-opacity="0.95"/>
      <stop offset="85%" stop-color="#dcff58" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#ff2a85" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="cyanGlow" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(210 95) rotate(25) scale(360 210)">
      <stop offset="0%" stop-color="#00f0ff" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="#00f0ff" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="limeGlow" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(960 250) rotate(-15) scale(340 190)">
      <stop offset="0%" stop-color="#dcff58" stop-opacity="0.10"/>
      <stop offset="100%" stop-color="#dcff58" stop-opacity="0"/>
    </radialGradient>
    <pattern id="cyberGrid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M 32 0 L 0 0 0 32" fill="none" stroke="#1b2640" stroke-width="0.7" stroke-opacity="0.45"/>
    </pattern>
    <clipPath id="bannerClip">
      <rect x="0" y="0" width="1200" height="330" rx="18"/>
    </clipPath>
  </defs>

  <g clip-path="url(#bannerClip)">
    <rect width="1200" height="330" fill="url(#bgGrad)"/>
    <rect width="1200" height="330" fill="url(#cyberGrid)"/>
    <rect width="1200" height="330" fill="url(#cyanGlow)"/>
    <rect width="1200" height="330" fill="url(#limeGlow)"/>

    <!-- Top Chrome Bar -->
    <rect x="0" y="0" width="1200" height="56" fill="#080c17" fill-opacity="0.90"/>
    <line x1="0" y1="56" x2="1200" y2="56" stroke="#1b263f" stroke-width="1"/>

    <!-- Animated Top Laser Beam -->
    <rect x="-360" y="0" width="360" height="3" fill="url(#scanBeam)">
      <animateTransform attributeName="transform" type="translate" from="0 0" to="1560 0" dur="5.5s" repeatCount="indefinite"/>
    </rect>

    <!-- Terminal Window Controls -->
    <circle cx="34" cy="28" r="5.5" fill="#ff2a85"/>
    <circle cx="54" cy="28" r="5.5" fill="#ffb800"/>
    <circle cx="74" cy="28" r="5.5" fill="#00f59b"/>
    <text x="98" y="32" fill="#8b95a8" font-size="12.5" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">~/github/althaf786313 — developer-dashboard.zsh</text>

    <!-- Status Pill -->
    <rect x="910" y="14" width="256" height="28" rx="14" fill="#071f1b" stroke="#00f59b" stroke-opacity="0.45"/>
    <circle cx="929" cy="28" r="4.5" fill="#00f59b">
      <animate attributeName="opacity" values="1;0.25;1" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text x="943" y="32" fill="#00f59b" font-size="11" font-weight="700" letter-spacing="0.8" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">OPEN TO COLLABORATE &amp; BUILD</text>

    <!-- Left Column: Identity & Engineering Headline -->
    <text x="48" y="94" fill="#00f0ff" font-size="13" font-weight="700" letter-spacing="1.2" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">&gt; $ whoami --profile</text>

    <text x="48" y="152" fill="#f8fafc" font-size="56" font-weight="800" letter-spacing="1.5" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">ALTHAF <tspan fill="#dcff58" font-weight="800">//</tspan></text>

    <text x="48" y="188" fill="#00f0ff" font-size="22" font-weight="700" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">Software Engineer &amp; Builder</text>

    <text x="48" y="222" fill="#cbd5e1" font-size="14.5" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">Turning solid software fundamentals into interactive web platforms,</text>
    <text x="48" y="245" fill="#cbd5e1" font-size="14.5" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">Python media automation engines, and zero-dependency browser games.</text>

    <!-- Left Bottom Capability Chips -->
    <g transform="translate(48, 268)">
      <rect x="0" y="0" width="164" height="32" rx="8" fill="#0e1629" stroke="#00f0ff" stroke-opacity="0.4"/>
      <circle cx="17" cy="16" r="4" fill="#00f0ff"/>
      <text x="29" y="20" fill="#e2e8f0" font-size="12" font-weight="600" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">Python &amp; Web</text>

      <rect x="176" y="0" width="184" height="32" rx="8" fill="#0e1629" stroke="#dcff58" stroke-opacity="0.4"/>
      <circle cx="193" cy="16" r="4" fill="#dcff58"/>
      <text x="205" y="20" fill="#e2e8f0" font-size="12" font-weight="600" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">Media Pipelines</text>

      <rect x="372" y="0" width="184" height="32" rx="8" fill="#0e1629" stroke="#ff2a85" stroke-opacity="0.4"/>
      <circle cx="389" cy="16" r="4" fill="#ff2a85"/>
      <text x="401" y="20" fill="#e2e8f0" font-size="12" font-weight="600" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">Canvas Engines</text>
    </g>

    <!-- Right Column: HUD Engineering Architecture Panel -->
    <rect x="708" y="76" width="458" height="226" rx="14" fill="#0c1222" fill-opacity="0.94" stroke="#22304f" stroke-width="1.2"/>
    <text x="732" y="104" fill="#dcff58" font-size="11.5" font-weight="700" letter-spacing="1.2" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">ARCHITECTURE // ACTIVE DOMAINS</text>
    <line x1="732" y1="116" x2="1142" y2="116" stroke="#1b2640" stroke-width="1"/>

    <!-- Row 1 -->
    <rect x="732" y="130" width="36" height="32" rx="8" fill="#09222d" stroke="#00f0ff" stroke-opacity="0.45"/>
    <text x="750" y="150" text-anchor="middle" fill="#00f0ff" font-size="12" font-weight="700" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">01</text>
    <text x="782" y="145" fill="#f8fafc" font-size="14" font-weight="700" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">Interactive Browser Platforms</text>
    <text x="782" y="163" fill="#8b95a8" font-size="11.5" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">Pyodide WASM • HTML5 Canvas • Web Audio</text>

    <!-- Row 2 -->
    <rect x="732" y="182" width="36" height="32" rx="8" fill="#1e2510" stroke="#dcff58" stroke-opacity="0.45"/>
    <text x="750" y="202" text-anchor="middle" fill="#dcff58" font-size="12" font-weight="700" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">02</text>
    <text x="782" y="197" fill="#f8fafc" font-size="14" font-weight="700" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">Python &amp; Automated Video Tooling</text>
    <text x="782" y="215" fill="#8b95a8" font-size="11.5" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">Flask REST • Manim • Piper TTS • FFmpeg</text>

    <!-- Row 3 -->
    <rect x="732" y="234" width="36" height="32" rx="8" fill="#290d1f" stroke="#ff2a85" stroke-opacity="0.45"/>
    <text x="750" y="254" text-anchor="middle" fill="#ff2a85" font-size="12" font-weight="700" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">03</text>
    <text x="782" y="249" fill="#f8fafc" font-size="14" font-weight="700" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">Continuous Learning &amp; Shipping</text>
    <text x="782" y="267" fill="#8b95a8" font-size="11.5" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">Clean Code • Self-Contained Builds • OSS</text>
  </g>

  <rect x="0.75" y="0.75" width="1198.5" height="328.5" rx="17.25" stroke="url(#frameGrad)" stroke-width="1.5"/>
</svg>
"""


def build_project_card(
    *,
    card_id: str,
    badge: str,
    accent: str,
    accent_bg: str,
    icon_svg: str,
    title: str,
    line1: str,
    line2: str,
    tags: list[str],
    cta: str,
) -> str:
    tag_els = []
    cur_x = 28
    for tag in tags:
        esc_tag = html.escape(tag)
        w = max(68, len(tag) * 7 + 22)
        tag_els.append(
            f'<rect x="{cur_x}" y="164" width="{w}" height="26" rx="6" fill="#10182b" stroke="#22304d"/>'
            f'<text x="{cur_x + w / 2:.1f}" y="181" text-anchor="middle" fill="#cbd5e1" font-size="11" font-weight="600" font-family="\'JetBrains Mono\', \'SFMono-Regular\', Consolas, monospace">{esc_tag}</text>'
        )
        cur_x += w + 8

    badge_w = len(badge) * 7 + 26
    badge_x = 560 - badge_w

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="588" height="216" viewBox="0 0 588 216" fill="none" role="img" aria-label="{html.escape(title)}">
  <defs>
    <linearGradient id="bg_{card_id}" x1="0" y1="0" x2="588" y2="216" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#090d17"/>
      <stop offset="100%" stop-color="#0d1424"/>
    </linearGradient>
    <radialGradient id="glow_{card_id}" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(520 36) scale(220 140)">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect x="0.75" y="0.75" width="586.5" height="214.5" rx="15" fill="url(#bg_{card_id})" stroke="#1e2a45" stroke-width="1.5"/>
  <rect x="1.5" y="1.5" width="585" height="213" rx="14" fill="url(#glow_{card_id})"/>
  <line x1="28" y1="1.5" x2="188" y2="1.5" stroke="{accent}" stroke-width="2.5"/>

  <!-- Icon Box -->
  <rect x="28" y="26" width="42" height="42" rx="10" fill="{accent_bg}" stroke="{accent}" stroke-opacity="0.5"/>
  <g transform="translate(37, 35)">
    {icon_svg}
  </g>

  <!-- Status Badge -->
  <rect x="{badge_x}" y="28" width="{badge_w}" height="26" rx="13" fill="{accent_bg}" stroke="{accent}" stroke-opacity="0.55"/>
  <text x="{badge_x + badge_w / 2:.1f}" y="45" text-anchor="middle" fill="{accent}" font-size="10.5" font-weight="700" letter-spacing="0.6" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">{html.escape(badge)}</text>

  <!-- Title & Description -->
  <text x="28" y="96" fill="#f8fafc" font-size="20" font-weight="800" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">{html.escape(title)}</text>
  <text x="28" y="122" fill="#94a3b8" font-size="13" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">{html.escape(line1)}</text>
  <text x="28" y="142" fill="#94a3b8" font-size="13" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">{html.escape(line2)}</text>

  <!-- Tech Chips -->
  {''.join(tag_els)}

  <!-- Right Action Label -->
  <text x="560" y="181" text-anchor="end" fill="{accent}" font-size="11.5" font-weight="700" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">{html.escape(cta)} -&gt;</text>
</svg>
"""


def build_road_rush_banner() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="300" viewBox="0 0 1200 300" fill="none" role="img" aria-label="Road Rush - Sunset and Beyond Multi-Biome Arcade Racing Engine">
  <defs>
    <linearGradient id="rrSky" x1="0" y1="0" x2="1200" y2="300" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#090b13"/>
      <stop offset="55%" stop-color="#170f2e"/>
      <stop offset="100%" stop-color="#2a1038"/>
    </linearGradient>
    <linearGradient id="sunDisc" x1="965" y1="45" x2="965" y2="195" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#dcff58"/>
      <stop offset="48%" stop-color="#ff8054"/>
      <stop offset="100%" stop-color="#ff2a85"/>
    </linearGradient>
    <linearGradient id="groundFade" x1="650" y1="0" x2="810" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#0b0d17" stop-opacity="0"/>
      <stop offset="100%" stop-color="#0b0d17" stop-opacity="1"/>
    </linearGradient>
    <linearGradient id="horizonFade" x1="650" y1="0" x2="820" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#00f0ff" stop-opacity="0"/>
      <stop offset="100%" stop-color="#00f0ff" stop-opacity="1"/>
    </linearGradient>
    <linearGradient id="rrBorder" x1="0" y1="0" x2="1200" y2="300" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#dcff58" stop-opacity="0.7"/>
      <stop offset="50%" stop-color="#00f0ff" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#ff2a85" stop-opacity="0.7"/>
    </linearGradient>
    <clipPath id="rrClip">
      <rect width="1200" height="300" rx="18"/>
    </clipPath>
  </defs>

  <g clip-path="url(#rrClip)">
    <rect width="1200" height="300" fill="url(#rrSky)"/>

    <!-- Synthwave Horizon & Perspective Road Artwork on Right Side -->
    <circle cx="965" cy="148" r="78" fill="url(#sunDisc)" opacity="0.92"/>
    <!-- Sun Scan Cutouts -->
    <rect x="875" y="138" width="180" height="5" fill="#1b1031"/>
    <rect x="875" y="151" width="180" height="7" fill="#1b1031"/>
    <rect x="875" y="166" width="180" height="9" fill="#1b1031"/>

    <!-- Seamless Faded Horizon Ground -->
    <rect x="650" y="176" width="550" height="124" fill="url(#groundFade)"/>
    <line x1="650" y1="176" x2="1200" y2="176" stroke="url(#horizonFade)" stroke-width="2"/>

    <!-- Perspective Highway Polygon -->
    <polygon points="925,176 1005,176 1185,300 745,300" fill="#161b2c" stroke="#ff2a85" stroke-width="2"/>
    <line x1="940" y1="176" x2="775" y2="300" stroke="#00f0ff" stroke-width="2" stroke-opacity="0.8"/>
    <line x1="990" y1="176" x2="1155" y2="300" stroke="#00f0ff" stroke-width="2" stroke-opacity="0.8"/>

    <!-- Animated Center Lane Dashes -->
    <line x1="965" y1="178" x2="965" y2="300" stroke="#dcff58" stroke-width="4" stroke-dasharray="16 14">
      <animate attributeName="stroke-dashoffset" from="30" to="0" dur="0.65s" repeatCount="indefinite"/>
    </line>

    <!-- Left Content Column -->
    <rect x="48" y="34" width="234" height="28" rx="14" fill="#192112" stroke="#dcff58" stroke-opacity="0.55"/>
    <circle cx="66" cy="48" r="4.5" fill="#dcff58"/>
    <text x="80" y="52" fill="#dcff58" font-size="11" font-weight="700" letter-spacing="0.8" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">HTML5 CANVAS ARCADE ENGINE</text>

    <text x="48" y="114" fill="#f8fafc" font-size="52" font-weight="900" letter-spacing="1.5" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">ROAD <tspan fill="#dcff58">RUSH</tspan></text>
    <text x="48" y="148" fill="#00f0ff" font-size="20" font-weight="700" letter-spacing="1.8" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">SUNSET &amp; BEYOND // MULTI-MAP RACER</text>

    <text x="48" y="184" fill="#cbd5e1" font-size="14" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">Zero-dependency pseudo-3D bike racing game featuring 5 dynamic weather biomes,</text>
    <text x="48" y="205" fill="#cbd5e1" font-size="14" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">real-time Web Audio API engine synthesis, N2O boost physics &amp; mobile touch controls.</text>

    <!-- 5 Biome Pills -->
    <g transform="translate(48, 234)">
      <rect x="0" y="0" width="114" height="28" rx="7" fill="#1a1523" stroke="#ff8054"/>
      <text x="57" y="18" text-anchor="middle" fill="#ff8054" font-size="11" font-weight="700" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">SUNSET 1.0G</text>

      <rect x="124" y="0" width="112" height="28" rx="7" fill="#0b1d2a" stroke="#00f0ff"/>
      <text x="180" y="18" text-anchor="middle" fill="#00f0ff" font-size="11" font-weight="700" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">CYBER 0.9G</text>

      <rect x="246" y="0" width="118" height="28" rx="7" fill="#23160f" stroke="#ffb800"/>
      <text x="305" y="18" text-anchor="middle" fill="#ffb800" font-size="11" font-weight="700" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">DESERT 0.82G</text>

      <rect x="374" y="0" width="118" height="28" rx="7" fill="#101d30" stroke="#60a5fa"/>
      <text x="433" y="18" text-anchor="middle" fill="#60a5fa" font-size="11" font-weight="700" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">ALPINE 0.68G</text>

      <rect x="502" y="0" width="132" height="28" rx="7" fill="#1d112b" stroke="#c084fc"/>
      <text x="568" y="18" text-anchor="middle" fill="#c084fc" font-size="11" font-weight="700" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">MIDNIGHT 0.85G</text>
    </g>
  </g>

  <rect x="0.75" y="0.75" width="1198.5" height="298.5" rx="17.25" stroke="url(#rrBorder)" stroke-width="1.5"/>
</svg>
"""


def write_and_validate(path: Path, svg_text: str) -> None:
    ET.fromstring(svg_text.encode("utf-8"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg_text, encoding="utf-8")
    print(f"OK [{len(svg_text):5d} B] -> {path.relative_to(REPO_ROOT)}")


def main() -> None:
    write_and_validate(PROFILE_ASSETS / "hero-banner.svg", build_hero_banner())

    write_and_validate(
        PROFILE_ASSETS / "card-python-hub.svg",
        build_project_card(
            card_id="pyhub",
            badge="LIVE ON GITHUB PAGES",
            accent="#00f0ff",
            accent_bg="#08242e",
            icon_svg='<path d="M4 6a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v12a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V6Z" stroke="#00f0ff" stroke-width="1.8"/><path d="M8 9l3 3-3 3M13 15h3" stroke="#00f0ff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
            title="Python Mastery Hub",
            line1="Interactive dark-mode Python learning hub with a 75-page ebook,",
            line2="100+ projects, live Pyodide + Matplotlib runner &amp; resume builder.".replace("&amp;", "&"),
            tags=["Pyodide", "Python", "Matplotlib", "HTML5"],
            cta="LAUNCH LIVE",
        ),
    )

    write_and_validate(
        PROFILE_ASSETS / "card-pip-studio.svg",
        build_project_card(
            card_id="pipstudio",
            badge="PYTHON FULL-STACK",
            accent="#dcff58",
            accent_bg="#1e2610",
            icon_svg='<rect x="2" y="4" width="20" height="16" rx="3" stroke="#dcff58" stroke-width="1.8"/><polygon points="10,8.5 16,12 10,15.5" fill="#dcff58"/>',
            title="Pip Studio",
            line1="All-in-one animated video studio uniting Manim Pro, custom Pillow",
            line2="cartoon scenes, offline Piper TTS voiceover & FFmpeg MP4 muxing.",
            tags=["Python", "Flask", "Manim", "FFmpeg"],
            cta="VIEW STUDIO",
        ),
    )

    write_and_validate(
        PROFILE_ASSETS / "card-road-rush.svg",
        build_project_card(
            card_id="roadrush",
            badge="5-BIOME ARCADE ENGINE",
            accent="#ff2a85",
            accent_bg="#2b0d1d",
            icon_svg='<path d="M3 16l4-7h10l4 7H3Z" stroke="#ff2a85" stroke-width="1.8" stroke-linejoin="round"/><circle cx="7.5" cy="17" r="2.2" fill="#ff2a85"/><circle cx="16.5" cy="17" r="2.2" fill="#ff2a85"/>',
            title="Road Rush — Sunset & Beyond",
            line1="Zero-dependency pseudo-3D bike racer with 5 dynamic weather maps,",
            line2="Web Audio API sound synthesis, nitro boost & mobile controls.",
            tags=["Canvas 2D", "Web Audio", "ES6 JS", "60 FPS"],
            cta="EXPLORE REPO",
        ),
    )

    write_and_validate(
        PROFILE_ASSETS / "card-portfolio.svg",
        build_project_card(
            card_id="portfolio",
            badge="DEVELOPER HUB",
            accent="#00f59b",
            accent_bg="#08261d",
            icon_svg='<circle cx="12" cy="12" r="9" stroke="#00f59b" stroke-width="1.8"/><path d="M3.6 9h16.8M3.6 15h16.8M12 3a13.5 13.5 0 0 1 0 18M12 3a13.5 13.5 0 0 0 0 18" stroke="#00f59b" stroke-width="1.5"/>',
            title="Althaf // Developer Portfolio",
            line1="Interactive Dark Neon engineering showcase featuring embedded",
            line2="playable Road Rush arcade, system architecture & profile studio.",
            tags=["Portfolio", "Interactive", "Vercel", "GH Pages"],
            cta="OPEN HUB",
        ),
    )

    write_and_validate(GAME_ASSETS / "road-rush-banner.svg", build_road_rush_banner())


if __name__ == "__main__":
    main()
