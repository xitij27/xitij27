"""Draws the "Tools I use" picture on the profile README.

GitHub READMEs can't lay icons out in columns, so the icon groups are drawn
into one picture instead: tools-light.svg and tools-dark.svg, next to this
script. To change the icons, edit GROUPS below and run:

    python3 assets/make_tools_svg.py

Icon names come from https://skillicons.dev (for example "py" or "docker").
"""
import base64
import html
import re
import urllib.request
from pathlib import Path

GROUPS = [  # (label, skillicons names, column, row)
    ("Languages", "py,ts,js,java,cpp,c,latex", 0, 0),
    ("AI and data", "pytorch,tensorflow,sklearn,opencv,anaconda", 1, 0),
    ("Web and apps", "react,nextjs,threejs,tailwind,nodejs,express,fastapi,flask", 0, 1),
    ("Databases and cloud", "postgres,mongodb,mysql,supabase,docker,aws,gcp,azure,vercel,firebase", 1, 1),
]
WIDTH = 840  # about the width of a GitHub profile README
COLUMN_X = (0, 420)
ICON_H = 30
LABEL_SIZE = 14
ICONS_Y = 26  # icons start this far below the top of their row
ROW_H = 72
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
LABEL_COLOURS = {"light": "#1f2328", "dark": "#f0f6fc"}  # GitHub's text colours


def fetch_icons(names: str) -> bytes:
    request = urllib.request.Request(
        f"https://skillicons.dev/icons?i={names}", headers={"User-Agent": "xitij27-profile-readme"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def build(icons: dict, colour: str) -> str:
    parts = []
    for label, _, col, row in GROUPS:
        raw = icons[label]
        vb_w, vb_h = map(float, re.search(rb'viewBox="0 0 ([\d.]+) ([\d.]+)"', raw).groups())
        width = ICON_H * vb_w / vb_h
        if COLUMN_X[col] + width > (COLUMN_X[col + 1] if col + 1 < len(COLUMN_X) else WIDTH):
            raise SystemExit(f'"{label}" has too many icons to fit its column. Move some to another group.')
        x, y = COLUMN_X[col], row * ROW_H
        # Embedded as a data URI: GitHub blocks outside files inside an SVG picture.
        data = base64.b64encode(raw).decode()
        parts.append(
            f'<text x="{x}" y="{y + LABEL_SIZE + 2}" font-family="{FONT}" font-size="{LABEL_SIZE}" '
            f'font-weight="600" fill="{colour}">{html.escape(label)}</text>'
            f'<image x="{x}" y="{y + ICONS_Y}" width="{width:.1f}" height="{ICON_H}" '
            f'href="data:image/svg+xml;base64,{data}"/>'
        )
    rows = max(row for *_, row in GROUPS) + 1
    height = (rows - 1) * ROW_H + ICONS_Y + ICON_H + 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}">' + "".join(parts) + "</svg>"
    )


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    icons = {label: fetch_icons(names) for label, names, _, _ in GROUPS}
    for mode, colour in LABEL_COLOURS.items():
        out = out_dir / f"tools-{mode}.svg"
        out.write_text(build(icons, colour), encoding="utf-8")
        print(f"wrote {out.name} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
