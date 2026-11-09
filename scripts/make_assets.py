"""Generate the EU flag emblem SVG (12 gold stars on blue, official geometry).

Official proportions: flag is 3:2; the star circle radius is 1/3 of flag
height; each star's circumscribed circle radius is 1/18 of flag height;
stars sit at clock positions (every 30 degrees) with one point vertical.
"""

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "src" / "assets" / "eu-flag.svg"
OUT_PUBLIC = ROOT / "site" / "public" / "eu-cofunded.svg"

H = 120  # flag height in svg units
W = round(H * 1.5)
R_CIRCLE = H / 3
R_STAR = H / 18


def star_points(cx: float, cy: float, r_outer: float) -> str:
    """Five-pointed star, one point up."""
    r_inner = r_outer * math.sin(math.radians(18)) / math.sin(math.radians(54))
    pts = []
    for k in range(5):
        ao = math.radians(-90 + 72 * k)
        ai = math.radians(-90 + 36 + 72 * k)
        pts.append((cx + r_outer * math.cos(ao), cy + r_outer * math.sin(ao)))
        pts.append((cx + r_inner * math.cos(ai), cy + r_inner * math.sin(ai)))
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def build() -> str:
    cx, cy = W / 2, H / 2
    stars = []
    for k in range(12):
        a = math.radians(-90 + 30 * k)
        sx = cx + R_CIRCLE * math.cos(a)
        sy = cy + R_CIRCLE * math.sin(a)
        stars.append(f'  <polygon points="{star_points(sx, sy, R_STAR)}" fill="#FFCC00"/>')
    stars_svg = "\n".join(stars)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Flag of the European Union">
  <rect width="{W}" height="{H}" fill="#003399"/>
{stars_svg}
</svg>
'''


if __name__ == "__main__":
    svg = build()
    for out in (OUT, OUT_PUBLIC):
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(svg, encoding="utf-8")
        print(f"wrote {out}")
