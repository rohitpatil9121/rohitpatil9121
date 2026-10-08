"""Convert source-prepped.png into a monochrome ASCII SVG that types itself in.

    python scripts/make_ascii_svg.py [image]     # writes ascii-portrait.svg

STATIC=1 emits a frozen frame (no animation) for local previews.
"""
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ascii-portrait.svg"

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense)
COLS = 100
CHAR_W = 6.0    # advance of one glyph at FONT_SIZE in a monospace font
LINE_H = 11.0
FONT_SIZE = 10
PAD = 14
GAMMA = 1.15    # >1 pushes midtones toward the sparse end

FG = "#c9d1d9"
BG = "#0d1117"
BORDER = "#30363d"
CURSOR = "#39d353"

ROW_DUR = 0.45
ROW_STAGGER = 0.06


def to_rows(path):
    img = Image.open(path).convert("L")
    rows = max(1, round(COLS * img.height / img.width * CHAR_W / LINE_H))
    small = img.resize((COLS, rows), Image.LANCZOS)
    lum = (np.asarray(small, dtype=np.float32) / 255.0) ** GAMMA
    idx = np.rint((1.0 - lum) * (len(RAMP) - 1)).astype(int)
    return ["".join(RAMP[i] for i in row) for row in idx]


def esc(s):
    # NBSP instead of spaces: SVG collapses plain whitespace, which would let
    # textLength stretch a short row across the full width.
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return s.replace(" ", "&#160;")


def build(rows, static):
    text_w = COLS * CHAR_W
    width = text_w + 2 * PAD
    height = len(rows) * LINE_H + 2 * PAD
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {height:g}" '
        f'width="{width:g}" height="{height:g}" role="img" aria-label="ASCII portrait">',
        f'<rect x="0.5" y="0.5" width="{width - 1:g}" height="{height - 1:g}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'Liberation Mono\',monospace" '
        f'font-size="{FONT_SIZE}" fill="{FG}">',
    ]
    for i, row in enumerate(rows):
        if not row.strip():
            continue
        top = PAD + i * LINE_H
        base = top + LINE_H - 2.5
        attrs = f'x="{PAD}" y="{base:g}" textLength="{text_w:g}" lengthAdjust="spacing"'
        if static:
            out.append(f'<text {attrs}>{esc(row)}</text>')
            continue
        begin = f"{i * ROW_STAGGER:.2f}s"
        out.append(
            f'<clipPath id="r{i}"><rect x="{PAD}" y="{top:g}" width="0" height="{LINE_H:g}">'
            f'<animate attributeName="width" from="0" to="{text_w:g}" begin="{begin}" '
            f'dur="{ROW_DUR}s" fill="freeze"/></rect></clipPath>'
        )
        out.append(f'<text {attrs} clip-path="url(#r{i})">{esc(row)}</text>')
        # block cursor riding the wipe edge, visible only while its row prints
        out.append(
            f'<rect x="{PAD}" y="{top + 1:g}" width="{CHAR_W:g}" height="{LINE_H - 2:g}" '
            f'fill="{CURSOR}" opacity="0">'
            f'<set attributeName="opacity" to="0.9" begin="{begin}" dur="{ROW_DUR}s"/>'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + text_w - CHAR_W:g}" '
            f'begin="{begin}" dur="{ROW_DUR}s"/></rect>'
        )
    out.append("</g></svg>")
    return "\n".join(out) + "\n"


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "source-prepped.png"
    if not src.exists():
        sys.exit(f"{src} not found - run scripts/prep_photo.py <photo> first")
    rows = to_rows(src)
    OUT.write_text(build(rows, os.environ.get("STATIC") == "1"), encoding="utf-8")
    print(f"wrote {OUT.name} ({COLS}x{len(rows)} chars)")


if __name__ == "__main__":
    main()
