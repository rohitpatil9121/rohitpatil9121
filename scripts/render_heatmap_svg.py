"""Render data/contributions.json as an animated 53-week heatmap SVG.

    python scripts/render_heatmap_svg.py     # writes contrib-heatmap.svg

STATIC=1 emits a frozen frame.
"""
import json
import os
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
# none -> brightest (level 5 is a neon top end, reserved for the best day)

W = 860
CELL = 12
PITCH = 15
GRID_X = 46
GRID_Y = 44
H = GRID_Y + 7 * PITCH + 62
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

BG = "#0d1117"
BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#39d353"


def fmt_day(iso):
    d = date.fromisoformat(iso)
    return f"{d.strftime('%b')} {d.day}"


def build(data, static):
    days, s = data["days"], data["stats"]
    first = date.fromisoformat(days[0]["date"])
    origin = first - timedelta(days=(first.weekday() + 1) % 7)  # Sunday of first column
    peak = s["best_day"]["count"]

    cells, months, seen_month = [], [], None
    for d in days:
        day = date.fromisoformat(d["date"])
        col = (day - origin).days // 7
        row = (day.weekday() + 1) % 7
        level = 5 if peak and d["count"] == peak else d["level"]
        x, y = GRID_X + col * PITCH, GRID_Y + row * PITCH
        anim = "" if static else f' class="c" style="animation-delay:{(col + row) * 0.022:.2f}s"'
        cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
                     f'fill="{PALETTE[level]}"{anim}/>')
        if day.month != seen_month and (row == 0 or seen_month is None):
            if not months or x - months[-1][0] >= 2 * PITCH:
                months.append((x, day.strftime("%b")))
            seen_month = day.month

    style = ""
    if not static:
        style = (
            "<style>"
            ".c{opacity:0;animation:drop .45s cubic-bezier(.2,.8,.2,1) forwards}"
            ".f{opacity:0;animation:fade .6s ease-out 1.6s forwards}"
            "@keyframes drop{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:none}}"
            "@keyframes fade{to{opacity:1}}"
            "@media (prefers-reduced-motion:reduce){.c,.f{animation:none;opacity:1}}"
            "</style>"
        )

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="{s["total"]:,} contributions in the last year">',
        style,
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
        f'<g font-family="{FONT}" font-size="11" fill="{MUTED}">',
    ]
    out += [f'<text x="{x}" y="{GRID_Y - 10}">{name}</text>' for x, name in months]
    out += [f'<text x="{GRID_X - 10}" y="{GRID_Y + r * PITCH + 10}" text-anchor="end">{name}</text>'
            for r, name in ((1, "Mon"), (3, "Wed"), (5, "Fri"))]
    out.append("</g>")
    out += cells

    foot_y = GRID_Y + 7 * PITCH + 22
    grid_right = GRID_X + 53 * PITCH - (PITCH - CELL)
    # legend is right-aligned to the grid: Less [swatches] More
    more_w = 32
    legend_x = grid_right - more_w - len(PALETTE) * PITCH
    legend = "".join(
        f'<rect x="{legend_x + i * PITCH}" y="{foot_y - 10}" width="{CELL}" height="{CELL}" '
        f'rx="3" fill="{c}"/>' for i, c in enumerate(PALETTE))
    best = s["best_day"]
    foot_cls = "" if static else ' class="f"'
    out += [
        f'<g{foot_cls} font-family="{FONT}" font-size="12">',
        f'<text x="{GRID_X}" y="{foot_y}" fill="{TEXT}"><tspan fill="{ACCENT}" font-weight="700">'
        f'{s["total"]:,}</tspan> contributions in the last year</text>',
        f'<text x="{legend_x - 8}" y="{foot_y}" fill="{MUTED}" text-anchor="end" font-size="11">Less</text>',
        legend,
        f'<text x="{grid_right}" y="{foot_y}" fill="{MUTED}" text-anchor="end" font-size="11">More</text>',
        f'<text x="{GRID_X}" y="{foot_y + 22}" fill="{MUTED}" font-size="11">'
        f'current streak <tspan fill="{TEXT}">{s["current_streak"]}d</tspan>'
        f'  ·  longest streak <tspan fill="{TEXT}">{s["longest_streak"]}d</tspan>'
        f'  ·  best day <tspan fill="{TEXT}">{best["count"]} on {fmt_day(best["date"])}</tspan>'
        f'  ·  active days <tspan fill="{TEXT}">{s["active_days"]}</tspan></text>',
        "</g></svg>",
    ]
    return "\n".join(p for p in out if p) + "\n"


def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))
    OUT.write_text(build(data, os.environ.get("STATIC") == "1"), encoding="utf-8")
    print(f"wrote {OUT.name} ({len(data['days'])} days)")


if __name__ == "__main__":
    main()
