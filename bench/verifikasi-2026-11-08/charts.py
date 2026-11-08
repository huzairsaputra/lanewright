"""Draw runs.svg from results.json (py -I charts.py; stdlib only). Cost shown = all processes of a run.
The SVG follows the reader's light or dark theme through an inner prefers-color-scheme rule."""
import json
import os
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = sys.argv[1] if len(sys.argv) > 1 else "results"  # "results" or "results-approved"
TITLE = ("Run time of the 14 runs of the third test" if NAME == "results"
         else "Run time of the two sprints on the approved path")
runs = json.load(open(os.path.join(HERE, NAME + ".json"), encoding="utf-8"))["runs"]
W, ROW, TOP, LEFT, RIGHT = 860, 40, 92, 310, 300
H = TOP + ROW * len(runs) + 56
scale = (W - LEFT - RIGHT) / max(r["wall_seconds"] for r in runs)
STYLE = """<style>
  .bg{fill:#FFFFFF} .fg{fill:#111111} .mu{fill:#6B6B6B} .ln{stroke:#E3E3E3}
  .lw{fill:#0072B2} .sk{fill:#E69F00} .pl{fill:#009E73}
  text{font-family:Inter,'Helvetica Neue',Arial,sans-serif}
  @media (prefers-color-scheme: dark){
    .bg{fill:#111111} .fg{fill:#F2F2F2} .mu{fill:#9A9A9A} .ln{stroke:#2C2C2C}
    .lw{fill:#56B4E9} .sk{fill:#F0B323} .pl{fill:#2BC59A}
  }
</style>"""
KIND = {"Lanewright": "lw", "scrum-kit": "sk", "Lanewright Planning": "pl"}


def t(x, y, s, cls="fg", size=13, weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{escape(str(s))}</text>')


body = [t(24, 38, TITLE, size=20, weight=600),
        t(24, 60, "Wall seconds per run; cost of every process a run started (US dollars). claude-opus-5-5, 7-8 Nov 2026. Sprints on the subscription: notional list price.", "mu", 12)]
for i, r in enumerate(runs):
    y = TOP + i * ROW
    w = r["wall_seconds"] * scale
    body.append(f'<line x1="24" x2="{W - 24}" y1="{y - 8}" y2="{y - 8}" class="ln"/>')
    body.append(t(24, y + 14, r["id"], size=13, weight=600))
    body.append(t(24, y + 30, r["product"] + " / " + r["step"], "mu", 11))
    body.append(f'<rect x="{LEFT}" y="{y}" width="{w:.1f}" height="22" rx="3" class="{KIND[r["product"]]}"/>')
    body.append(t(LEFT + w + 8, y + 16, f'{r["wall_seconds"]} s', size=13, weight=600))
    body.append(t(W - 24, y + 16, f"${r['cost_usd_all_processes']:.2f}{' notional' if r['billing'] != 'API key' else ''} · {r['num_turns']} turns", "mu", 12, anchor="end"))
y = TOP + ROW * len(runs) + 10
for j, (label, cls) in enumerate((("Lanewright", "lw"), ("scrum-kit", "sk"))):
    x = 24 + j * 150
    body.append(f'<rect x="{x}" y="{y + 7}" width="14" height="14" rx="2" class="{cls}"/>')
    body.append(t(x + 22, y + 19, label, "mu", 11))
body.append(t(24, y + 36, "Full data (API time, tokens, thinking tokens): " + NAME + ".json", "mu", 11))
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="Wall time and cost of {len(runs)} end-to-end runs">\n{STYLE}\n<rect class="bg" width="{W}" height="{H}" rx="12"/>\n'
       + "\n".join(body) + "\n</svg>\n")
with open(os.path.join(HERE, "runs.svg" if NAME == "results" else NAME + ".svg"), "w", encoding="utf-8", newline="\n") as f:
    f.write(svg)
print(NAME, W, H)
