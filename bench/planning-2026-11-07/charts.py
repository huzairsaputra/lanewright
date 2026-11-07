"""Draw runs.svg from results.json (stdlib only). Run: py -I charts.py
The SVG follows the reader's light or dark theme through an inner prefers-color-scheme rule."""
import json
import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
runs = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))["runs"]
W, ROW, TOP, LEFT, RIGHT = 820, 44, 92, 290, 190
H = TOP + ROW * len(runs) + 56
scale = (W - LEFT - RIGHT) / max(r["wall_seconds"] for r in runs)
STYLE = """<style>
  .bg{fill:#FFFFFF} .fg{fill:#111111} .mu{fill:#6B6B6B} .ln{stroke:#E3E3E3}
  .lw{fill:#111111} .sk{fill:#8A8A8A} .pl{fill:#C9C9C9}
  text{font-family:Inter,'Helvetica Neue',Arial,sans-serif}
  @media (prefers-color-scheme: dark){
    .bg{fill:#111111} .fg{fill:#F2F2F2} .mu{fill:#9A9A9A} .ln{stroke:#2C2C2C}
    .lw{fill:#F2F2F2} .sk{fill:#9A9A9A} .pl{fill:#6E6E6E}
  }
</style>"""
KIND = {"Lanewright": "lw", "scrum-kit": "sk", "Lanewright Planning": "pl"}


def t(x, y, s, cls="fg", size=13, weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{escape(str(s))}</text>')


body = [t(24, 38, "Run time of the seven end-to-end runs", size=20, weight=600),
        t(24, 60, "Wall seconds per run, cost in US dollars. One headless process each, claude-opus-5-5, 7 Nov 2026.", "mu", 12)]
for i, r in enumerate(runs):
    y = TOP + i * ROW
    w = r["wall_seconds"] * scale
    body.append(f'<line x1="24" x2="{W - 24}" y1="{y - 8}" y2="{y - 8}" class="ln"/>')
    body.append(t(24, y + 14, r["id"], size=13, weight=600))
    body.append(t(24, y + 30, r["product"] + " / " + r["step"], "mu", 11))
    body.append(f'<rect x="{LEFT}" y="{y}" width="{w:.1f}" height="22" rx="3" class="{KIND[r["product"]]}"/>')
    body.append(t(LEFT + w + 8, y + 16, f'{r["wall_seconds"]} s', size=13, weight=600))
    body.append(t(W - 24, y + 16, f'${r["total_cost_usd"]:.2f} · {r["num_turns"]} turns', "mu", 12, anchor="end"))
y = TOP + ROW * len(runs) + 10
for j, (label, cls) in enumerate((("Lanewright", "lw"), ("scrum-kit", "sk"), ("Lanewright Planning skills", "pl"))):
    x = 24 + j * 150
    body.append(f'<rect x="{x}" y="{y + 7}" width="14" height="14" rx="2" class="{cls}"/>')
    body.append(t(x + 22, y + 19, label, "mu", 11))
body.append(t(24, y + 36, "Full data (API time, tokens, thinking tokens): results.json", "mu", 11))
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="Wall time and cost of seven end-to-end runs">\n{STYLE}\n<rect class="bg" width="{W}" height="{H}" rx="12"/>\n'
       + "\n".join(body) + "\n</svg>\n")
with open(os.path.join(HERE, "runs.svg"), "w", encoding="utf-8", newline="\n") as f:
    f.write(svg)
print("runs.svg", W, H)
