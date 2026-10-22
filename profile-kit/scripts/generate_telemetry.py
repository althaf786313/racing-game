#!/usr/bin/env python3
"""
Generates assets/telemetry-card.svg from live GitHub REST API data for @althaf786313.
Runs standalone with Python 3 standard library only (zero pip dependencies) — ready for GitHub Actions!
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

USERNAME = os.environ.get("GITHUB_USERNAME", "althaf786313")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "assets" / "telemetry-card.svg"


def gh_get(path: str):
    url = f"https://api.github.com/{path.lstrip('/')}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-profile-telemetry",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_metrics() -> dict:
    user = gh_get(f"users/{USERNAME}")
    repos = gh_get(f"users/{USERNAME}/repos?per_page=100&sort=updated")
    own_repos = [r for r in repos if not r.get("fork")]

    lang_bytes: dict[str, int] = {}
    total_stars = 0
    for repo in own_repos:
        total_stars += int(repo.get("stargazers_count", 0))
        name = repo["name"]
        try:
            langs = gh_get(f"repos/{USERNAME}/{name}/languages")
            for lang, count in langs.items():
                lang_bytes[lang] = lang_bytes.get(lang, 0) + int(count)
        except Exception:
            continue

    total_bytes = sum(lang_bytes.values()) or 1
    sorted_langs = sorted(lang_bytes.items(), key=lambda kv: kv[1], reverse=True)[:4]

    palette = {
        "HTML": ("#00f0ff", "HTML5 / Interactive UI"),
        "Python": ("#dcff58", "Python"),
        "JavaScript": ("#ff2a85", "JavaScript (ES6+)"),
        "CSS": ("#00f59b", "CSS3 / Motion UI"),
        "Shell": ("#ffb800", "Shell Automation"),
        "TypeScript": ("#38bdf8", "TypeScript"),
    }

    bars = []
    for lang, count in sorted_langs:
        pct = round((count / total_bytes) * 100, 1)
        color, label = palette.get(lang, ("#00f0ff", lang))
        bars.append({"label": label, "pct": pct, "color": color, "kb": round(count / 1024, 1)})

    return {
        "public_repos": int(user.get("public_repos", len(own_repos))),
        "total_stars": total_stars,
        "total_kb": round(total_bytes / 1024, 1),
        "active_repos": sum(1 for r in own_repos if int(r.get("size", 0)) > 0),
        "bars": bars,
        "updated": dt.datetime.now(dt.timezone.utc).strftime("%b %d, %Y"),
    }


def render_svg(data: dict) -> str:
    bar_rows = []
    start_y = 84
    row_gap = 31
    max_bar_w = 320

    for idx, bar in enumerate(data["bars"]):
        y = start_y + idx * row_gap
        fill_w = max(10, round((bar["pct"] / 100.0) * max_bar_w, 1))
        label = html.escape(bar["label"])
        pct_str = f"{bar['pct']:.1f}%"
        bar_rows.append(
            f"""
    <g transform="translate(440, {y})">
      <text x="0" y="0" fill="#e2e8f0" font-size="12" font-weight="600" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">{label}</text>
      <text x="{max_bar_w}" y="0" text-anchor="end" fill="{bar['color']}" font-size="11.5" font-weight="700" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">{pct_str}</text>
      <rect x="0" y="7" width="{max_bar_w}" height="7" rx="3.5" fill="#172036"/>
      <rect x="0" y="7" width="{fill_w}" height="7" rx="3.5" fill="{bar['color']}"/>
    </g>"""
        )

    bars_markup = "\n".join(bar_rows)
    updated = html.escape(data["updated"])

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="224" viewBox="0 0 1200 224" fill="none" role="img" aria-label="GitHub Engineering Telemetry for {USERNAME}">
  <defs>
    <linearGradient id="panelBg" x1="0" y1="0" x2="1200" y2="224" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#090d16"/>
      <stop offset="50%" stop-color="#0d1322"/>
      <stop offset="100%" stop-color="#080b13"/>
    </linearGradient>
    <linearGradient id="panelStroke" x1="0" y1="0" x2="1200" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#00f0ff" stop-opacity="0.45"/>
      <stop offset="50%" stop-color="#dcff58" stop-opacity="0.30"/>
      <stop offset="100%" stop-color="#ff2a85" stop-opacity="0.45"/>
    </linearGradient>
  </defs>

  <rect x="0.75" y="0.75" width="1198.5" height="222.5" rx="16" fill="url(#panelBg)" stroke="url(#panelStroke)" stroke-width="1.5"/>

  <!-- Column Dividers -->
  <line x1="404" y1="24" x2="404" y2="200" stroke="#1d2740" stroke-width="1"/>
  <line x1="796" y1="24" x2="796" y2="200" stroke="#1d2740" stroke-width="1"/>

  <!-- COLUMN 1: REPOSITORY TELEMETRY -->
  <g>
    <circle cx="42" cy="40" r="4.5" fill="#00f0ff">
      <animate attributeName="opacity" values="1;0.35;1" dur="2.4s" repeatCount="indefinite"/>
    </circle>
    <text x="55" y="44" fill="#00f0ff" font-size="11.5" font-weight="700" letter-spacing="1.2" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">01 // REPOSITORY TELEMETRY</text>

    <rect x="36" y="64" width="164" height="62" rx="10" fill="#11182b" stroke="#1e2942"/>
    <text x="52" y="86" fill="#8b95a8" font-size="11" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">PUBLIC REPOS</text>
    <text x="52" y="113" fill="#f8fafc" font-size="24" font-weight="800" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">{data['public_repos']}</text>

    <rect x="212" y="64" width="164" height="62" rx="10" fill="#11182b" stroke="#1e2942"/>
    <text x="228" y="86" fill="#8b95a8" font-size="11" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">CODEBASE VOLUME</text>
    <text x="228" y="113" fill="#dcff58" font-size="24" font-weight="800" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">{data['total_kb']} KB</text>

    <rect x="36" y="138" width="164" height="62" rx="10" fill="#11182b" stroke="#1e2942"/>
    <text x="52" y="160" fill="#8b95a8" font-size="11" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">SHIPPED BUILDS</text>
    <text x="52" y="187" fill="#00f0ff" font-size="24" font-weight="800" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">{data['active_repos']} Apps</text>

    <rect x="212" y="138" width="164" height="62" rx="10" fill="#11182b" stroke="#1e2942"/>
    <text x="228" y="160" fill="#8b95a8" font-size="11" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">CORE STACKS</text>
    <text x="228" y="187" fill="#ff2a85" font-size="20" font-weight="800" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">Py + Web</text>
  </g>

  <!-- COLUMN 2: MEASURED CODE DISTRIBUTION -->
  <g>
    <text x="440" y="44" fill="#dcff58" font-size="11.5" font-weight="700" letter-spacing="1.2" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">02 // CODEBASE DISTRIBUTION</text>
    {bars_markup}
  </g>

  <!-- COLUMN 3: BUILDER DNA & LIVE STATUS -->
  <g>
    <text x="830" y="44" fill="#ff2a85" font-size="11.5" font-weight="700" letter-spacing="1.2" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">03 // CURRENT SPRINT FOCUS</text>

    <rect x="822" y="64" width="348" height="104" rx="10" fill="#11182b" stroke="#1e2942"/>
    <text x="840" y="88" fill="#f8fafc" font-size="12.5" font-weight="700" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">Full-Stack &amp; Browser-Native Engineering</text>
    <text x="840" y="110" fill="#94a3b8" font-size="12" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">• Interactive Python IDE &amp; 100+ Project Hub</text>
    <text x="840" y="130" fill="#94a3b8" font-size="12" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">• Automated Manim + Piper TTS Video Studio</text>
    <text x="840" y="150" fill="#94a3b8" font-size="12" font-family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">• Zero-Dependency Canvas &amp; Web Audio Games</text>

    <rect x="822" y="178" width="348" height="24" rx="6" fill="#0b101d" stroke="#1b263d"/>
    <text x="838" y="194" fill="#00f59b" font-size="10.5" font-weight="600" font-family="'JetBrains Mono', 'SFMono-Regular', Consolas, monospace">SYNCED: {updated} • @{USERNAME}</text>
  </g>
</svg>
"""
    ET.fromstring(svg.encode("utf-8"))
    return svg


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    metrics = fetch_metrics()
    svg = render_svg(metrics)
    OUT_FILE.write_text(svg, encoding="utf-8")
    print(f"Generated {OUT_FILE} ({len(svg)} bytes) -> {json.dumps(metrics)}")


if __name__ == "__main__":
    main()
