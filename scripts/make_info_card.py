"""Hand-authored neofetch-style info card.

    python scripts/make_info_card.py     # writes info-card.svg

Edit HOST and LINES below, then re-run. STATIC=1 emits a frozen frame.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"

HOST = "rohit@github"

# (key, value). A None key continues the previous value; ("", "") is a blank line.
LINES = [
    ("Name", "Rohit Patil"),
    ("Now", "B.Tech Cloud Computing @ MIT ADT University"),
    ("Based", "Pune, India"),
    ("Focus", "AWS & DevOps - building real-world cloud projects"),
    ("", ""),
    ("Cloud", "AWS Lambda, API Gateway, DynamoDB, S3"),
    ("Stack", "Python, JavaScript, TypeScript"),
    (None, "WebGL / GLSL, Astro, HTML & CSS"),
    ("AI/ML", "Python + scikit-learn, OpenAI Whisper, LangChain"),
    (None, "LLM apps on Groq and the Claude API"),
    ("", ""),
    ("Builds", "From-scratch WebGL 3D engine (no libraries)"),
    (None, "neon-rush / orbital / rewind-heist browser games"),
    (None, "AI meeting summarizer, LeetCode hint coach"),
    (None, "Phishing & fake-news classifiers (~98% accuracy)"),
    (None, "Serverless URL shortener on AWS"),
]

W, H = 490, 412  # 412 matches the portrait's height at README scale
PAD_X = 22
KEY_W = 62
LINE_H = 18.5
BAR_H = 30
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

BG = "#0d1117"
BAR = "#161b22"
BORDER = "#30363d"
KEY = "#39d353"
VALUE = "#c9d1d9"
MUTED = "#8b949e"
SWATCHES = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

STAGGER = 0.09


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(static):
    rows = []  # svg fragments, one per animated line
    y = BAR_H + 30
    user, host = HOST.split("@")
    rows.append(
        f'<text x="{PAD_X}" y="{y}" font-weight="700"><tspan fill="{KEY}">{esc(user)}</tspan>'
        f'<tspan fill="{VALUE}">@</tspan><tspan fill="{KEY}">{esc(host)}</tspan></text>'
    )
    y += LINE_H
    rows.append(f'<text x="{PAD_X}" y="{y}" fill="{MUTED}">{"-" * len(HOST)}</text>')
    for key, value in LINES:
        y += LINE_H
        if not key and not value:
            continue
        parts = ""
        if key:
            parts += f'<tspan x="{PAD_X}" fill="{KEY}" font-weight="700">{esc(key)}</tspan>'
        parts += f'<tspan x="{PAD_X + KEY_W}" fill="{VALUE}">{esc(value)}</tspan>'
        rows.append(f'<text y="{y}">{parts}</text>')
    y += LINE_H + 4
    blocks = "".join(
        f'<rect x="{PAD_X + i * 22}" y="{y - 11}" width="18" height="12" rx="2" fill="{c}" '
        f'stroke="{BORDER}" stroke-width="0.5"/>'
        for i, c in enumerate(SWATCHES)
    )
    rows.append(f"<g>{blocks}</g>")
    if y + 14 > H:
        raise SystemExit(f"card content overflows: needs {y + 14}px, card is {H}px")

    style = ""
    if not static:
        style = (
            "<style>"
            ".l{opacity:0;animation:in .5s ease-out forwards}"
            "@keyframes in{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}"
            "@media (prefers-reduced-motion:reduce){.l{animation:none;opacity:1}}"
            "</style>"
        )
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="About {esc(HOST)}">',
        style,
        f'<clipPath id="card"><rect width="{W}" height="{H}" rx="10"/></clipPath>',
        f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{BG}"/>'
        f'<rect width="{W}" height="{BAR_H}" fill="{BAR}"/></g>',
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="none" stroke="{BORDER}"/>',
        f'<line x1="0" y1="{BAR_H}" x2="{W}" y2="{BAR_H}" stroke="{BORDER}"/>',
        '<circle cx="18" cy="15" r="5" fill="#ff5f56"/><circle cx="36" cy="15" r="5" fill="#ffbd2e"/>'
        '<circle cx="54" cy="15" r="5" fill="#27c93f"/>',
        f'<g font-family="{FONT}" font-size="12.5">',
        f'<text x="{W / 2}" y="19" text-anchor="middle" fill="{MUTED}">{esc(HOST)}: ~ - neofetch</text>',
    ]
    for i, frag in enumerate(rows):
        if static:
            out.append(frag)
        else:
            out.append(f'<g class="l" style="animation-delay:{0.2 + i * STAGGER:.2f}s">{frag}</g>')
    out.append("</g></svg>")
    return "\n".join(p for p in out if p) + "\n"


def main():
    OUT.write_text(build(os.environ.get("STATIC") == "1"), encoding="utf-8")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
