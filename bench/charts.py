"""Draw the fair-benchmark images in bench/img/ from bench/fair-2026-11-06/results.json. Stdlib only.

Run: py -I bench/charts.py
Each SVG follows the reader's light or dark theme through an inner prefers-color-scheme rule.
(The 2026-11-05 images in bench/img/ without the `fair-` prefix are static records of that run.)
"""
import json
import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "img")
ARMS = [("claude", "skill", "Claude Code + Lanewright"), ("claude", "levers", "Claude Code + Lanewright, cost settings"),
        ("claude", "plain", "Claude Code, no pack"), ("codex", "skill", "Codex CLI + Lanewright"),
        ("codex", "plain", "Codex CLI, no pack")]

STYLE = """<style>
  .bg{fill:#FFFFFF} .fg{fill:#111111} .mu{fill:#6B6B6B} .ln{stroke:#E3E3E3}
  .on{fill:#111111} .mk{stroke:#111111} .off{fill:#C9C9C9} .tile{fill:#F5F5F5}
  text{font-family:Inter,'Helvetica Neue',Arial,sans-serif}
  @media (prefers-color-scheme: dark){
    .bg{fill:#111111} .fg{fill:#F2F2F2} .mu{fill:#9A9A9A} .ln{stroke:#2C2C2C}
    .on{fill:#F2F2F2} .mk{stroke:#F2F2F2} .off{fill:#4A4A4A} .tile{fill:#1C1C1C}
  }
</style>"""


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{escape(label)}">\n{STYLE}\n<rect class="bg" width="{w}" height="{h}" rx="12"/>\n'
            + body + "\n</svg>\n")


def text(x, y, s, cls="fg", size=14, weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{escape(str(s))}</text>')


def mark(x, y, s=0.5):
    """The Lanewright lane-L (brand/LOGO.md): stem + base, and two thin lanes above the base."""
    lines = ((19, 13, 19, 49, 9), (19, 49, 47, 49, 9), (33, 13, 33, 37, 3), (47, 13, 47, 37, 3))
    return "".join(f'<line class="mk" x1="{x + a * s:g}" y1="{y + b * s:g}" x2="{x + c * s:g}" y2="{y + d * s:g}" '
                   f'stroke-width="{w * s:g}" stroke-linecap="round"/>' for a, b, c, d, w in lines)


def wrap(s, n):
    lines, cur = [], ""
    for w in s.split():
        if len(cur) + len(w) + 1 > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur]


def group(runs, agent, arm):
    return [r for r in runs if r["agent"] == agent and r["arm"] == arm]


def mean(xs):
    return sum(xs) / len(xs)


def hero(runs):
    skill = [r for r in runs if r["arm"] == "skill"]
    plain = [r for r in runs if r["arm"] == "plain"]
    full = lambda rs: sum(r["score"]["full_dod_checked"] for r in rs)
    cs, cl, cp = group(runs, "claude", "skill"), group(runs, "claude", "levers"), group(runs, "claude", "plain")
    c_skill, c_lev, c_plain = (mean([r["cost_usd"] for r in g]) for g in (cs, cl, cp))
    fair = [r for r in runs if r["arm"] != "levers"]
    gated = sum(r["score"]["merged_after_green_ci_on_head"] for r in fair)
    merged = sum(r["score"]["items_merged_via_pr"] for r in fair)
    tiles = [
        (f"{full(skill)}/{len(skill)} vs {full(plain)}/{len(plain)}",
         "runs that met every checked Definition-of-Done item, with vs without the pack"),
        (f"{gated}/{merged}", "merges after a green CI run on the PR head, in all 12 runs (both arms)"),
        (f"${c_skill:.2f} vs ${c_plain:.2f}", "mean Claude cost per sprint, with vs without the pack"),
        (f"${c_lev:.2f}", f"with the pack's cost settings (orchestrator on Sonnet 5.5), {full(cl)}/{len(cl)} complete"),
    ]
    body = [mark(28, 22), text(76, 52, "Lanewright 1.0: fair benchmark", size=24, weight=700),
            text(76, 76, "One Definition of Done for both arms. 3 runs per arm, Claude Code (Opus 5.5) and Codex CLI.", "mu", 14)]
    for i, (big, cap) in enumerate(tiles):
        x = 28 + i * 210
        body.append(f'<rect class="tile" x="{x}" y="104" width="196" height="170" rx="10"/>')
        body.append(text(x + 16, 150, big, size=34 if len(big) <= 6 else 24 if len(big) <= 11 else 20, weight=700))
        for j, line in enumerate(wrap(cap, 26)):
            body.append(text(x + 16, 184 + j * 19, line, "mu", 13))
    return svg(880, 300, "\n".join(body), "Lanewright fair benchmark: " + "; ".join(f"{a} {b}" for a, b in tiles))


def dod(runs):
    rows = [
        ("Every item merged through its own PR", lambda r: r["score"]["items_merged_via_pr"] >= 2),
        ("Merged only after CI on the PR head", lambda r: r["score"]["merged_after_green_ci_on_head"] == r["score"]["items_merged_via_pr"]),
        ("Merge commits, draft integration PR, main untouched", lambda r: r["score"]["merge_commits"] == r["score"]["items_merged_via_pr"]
            and r["score"]["integration_pr_draft_open"] and r["score"]["main_untouched"]),
        ("No commit outside its region", lambda r: not r["score"]["commits_mixing_regions"] and not r["score"]["commits_touching_mobile"]),
        ("Reports and sprint summary committed", lambda r: r["score"]["reports_committed"]),
        ("Every checked item met", lambda r: r["score"]["full_dod_checked"]),
    ]
    colw, left, top = 140, 330, 92
    w = left + colw * len(ARMS) + 20
    body = [text(28, 42, "Definition of Done, per arm", size=20, weight=700),
            text(28, 64, "Runs (of 3) that met each item, read from git and the GitHub API.", "mu", 13)]
    heads = [wrap(label, 16) for _, _, label in ARMS]
    for i, lines in enumerate(heads):
        for j, line in enumerate(lines):
            body.append(text(left + colw * i + colw / 2, top + j * 16, line, "fg", 12, 600, "middle"))
    y0 = top + 16 * max(len(h) for h in heads) + 32  # header height follows the longest wrapped label
    for k, (name, f) in enumerate(rows):
        y = y0 + k * 44
        body.append(f'<line class="ln" x1="28" x2="{w - 20}" y1="{y - 26}" y2="{y - 26}"/>')
        body.append(text(28, y, name, "fg", 14, 700 if k == len(rows) - 1 else 400))
        for i, (agent, arm, _) in enumerate(ARMS):
            rs = group(runs, agent, arm)
            n = sum(bool(f(r)) for r in rs)
            body.append(text(left + colw * i + colw / 2, y, f"{n}/{len(rs)}", "fg" if n == len(rs) else "mu",
                             15, 700 if n == len(rs) else 400, "middle"))
    return svg(w, y0 + len(rows) * 44, "\n".join(body), "Definition of Done per arm: " + "; ".join(
        f"{label}: " + ", ".join(f"{name} {sum(bool(f(r)) for r in group(runs, a, m))}/3" for name, f in rows)
        for a, m, label in ARMS))


def cost(runs):
    metrics = [("Output tokens (mean of 3)", "output_tokens", lambda v: f"{v:,.0f}"),
               ("Wall time (mean of 3)", "seconds", lambda v: f"{v / 60:.1f} min")]
    left, barw, rowh = 300, 450, 26
    cs, cp = group(runs, "claude", "skill"), group(runs, "claude", "plain")
    body = [text(28, 42, "What the pack costs", size=20, weight=700),
            text(28, 64, "Claude cost per sprint (mean, Opus 5.5 list price): with the pack $%.2f, without $%.2f. Codex not priced."
                 % (mean([r["cost_usd"] for r in cs]), mean([r["cost_usd"] for r in cp])), "mu", 13)]
    y = 100
    for title, key, fmt in metrics:
        body.append(text(28, y, title, "fg", 15, 700))
        y += 14
        vals = [(label, arm, mean([r[key] for r in group(runs, agent, arm)])) for agent, arm, label in ARMS]
        top = max(v for _, _, v in vals)
        for label, arm, v in vals:
            wbar = max(2, barw * v / top)
            body.append(text(28, y + 17, label, "mu", 13))
            body.append(f'<rect class="{"on" if arm == "skill" else "off"}" x="{left}" y="{y + 4}" width="{wbar:.1f}" height="16" rx="3"/>')
            body.append(text(left + wbar + 8, y + 17, fmt(v), "fg", 13))
            y += rowh
        y += 22
    return svg(880, y, "\n".join(body), "Mean cost per arm: " + "; ".join(
        f"{label}: {mean([r['output_tokens'] for r in group(runs, a, m)]):.0f} output tokens, "
        f"{mean([r['seconds'] for r in group(runs, a, m)]) / 60:.1f} min" for a, m, label in ARMS))


def main():
    runs = json.load(open(os.path.join(HERE, "fair-2026-11-06", "results.json"), encoding="utf-8"))["runs"]
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("fair-hero", hero), ("fair-dod", dod), ("fair-cost", cost)):
        with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8", newline="\n") as f:
            f.write(fn(runs))
        print("wrote", os.path.join("bench", "img", name + ".svg"))


if __name__ == "__main__":
    main()
