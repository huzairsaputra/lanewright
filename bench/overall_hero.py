"""Draw bench/img/overall-hero.svg: one card over every benchmark (fair 6 Nov, hard stages 1+2, hard extra phase).

Run: py -I bench/overall_hero.py      (stdlib only; every number is computed from the per-run data files)
Measures: DoD met (frozen grader; D10 as a note), hidden acceptance tests passing, cost per passed item.
PNG: open the SVG in headless Chrome at 960x650 (see the commit that added this script).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from charts import mark, svg, text, wrap  # noqa: E402

HARD = os.path.join(HERE, "hard-2026-11-10")
W, H = 960, 650


def load(*p):
    return json.load(open(os.path.join(HERE, *p), encoding="utf-8"))


def mean(xs):
    return sum(xs) / len(xs)


def fair():
    runs = load("fair-2026-11-06", "results.json")["runs"]
    arm = lambda a, agent=None: [r for r in runs if r["arm"] == a and agent in (None, r["agent"])]
    full = lambda rs: sum(r["score"]["full_dod_checked"] for r in rs)
    return {"n": len(runs), "full": (full(arm("skill")), len(arm("skill")), full(arm("plain")), len(arm("plain"))),
            "cost": (mean([r["cost_usd"] for r in arm("skill", "claude")]), mean([r["cost_usd"] for r in arm("plain", "claude")]))}


def hard():
    runs = load("hard-2026-11-10", "runs.json")
    models = sorted({r["model"] for r in runs})
    g = lambda m, a: [r for r in runs if r["model"] == m and (r["arm"] == "none") == (a == "A")]
    cpi = lambda rs: sum(r["cost_usd_notional"] for r in rs) / sum(r["hidden_items_passing"] for r in rs)
    up = lambda k: sum(mean([r[k] for r in g(m, "C")]) > mean([r[k] for r in g(m, "A")]) + 1e-9 for m in models)
    hid = [round(mean([r["hidden_items_passing"] for r in g(m, "C")]) - mean([r["hidden_items_passing"] for r in g(m, "A")]), 6) for m in models]
    miss = lambda item, a: sum(not r["dod_items"][item] for m in models for r in g(m, a))
    suite = lambda a: sum(r["dod_items"]["7_hidden_suite"] for m in models for r in g(m, a))
    return {"n": len(runs), "models": len(models), "dod_up": up("dod_grader"), "dod10_up": up("dod_d10"),
            "verdicts": (miss("2_review_verdicts", "A"), miss("2_review_verdicts", "C")),
            "reports": (miss("5_reports", "A"), miss("5_reports", "C")), "arm_n": len(runs) // 2,
            "hid": (sum(d > 0 for d in hid), sum(d == 0 for d in hid), sum(d < 0 for d in hid)),
            "suite": (suite("A"), suite("C")),
            "cpi_lower": sum(cpi(g(m, "C")) < cpi(g(m, "A")) for m in models),
            "sol56": (cpi(g("gpt-5.6-sol", "A")), cpi(g("gpt-5.6-sol", "C")))}


def extra():
    runs = load("hard-2026-11-10", "runs-extra.json")
    sets = sorted({r["setting"] for r in runs})
    g = lambda s, p: [r for r in runs if r["setting"] == s and r["pack"].startswith(p)]
    cpi = lambda rs: sum(r["cost_usd_notional"] for r in rs) / sum(r["hidden_items_passing"] for r in rs)
    m = lambda s, p, k: mean([r[k] for r in g(s, p)])
    per = lambda p: [r for r in runs if r["pack"].startswith(p)]
    return {"n": len(runs), "sets": len(sets),
            "dod_lw_higher": sum(m(s, "lane", "dod_grader") > m(s, "scrum", "dod_grader") for s in sets),
            "reports": tuple(sum(not r["dod_items"]["5_reports"] for r in per(p)) for p in ("scrum", "lane")),
            "pack_n": len(per("lane")),
            "hid_same": sum(m(s, "lane", "hidden_items_passing") == m(s, "scrum", "hidden_items_passing") for s in sets),
            "hid_lw_higher": sum(m(s, "lane", "hidden_items_passing") > m(s, "scrum", "hidden_items_passing") for s in sets),
            "suite": tuple(sum(r["dod_items"]["7_hidden_suite"] for r in per(p)) for p in ("scrum", "lane")),
            "sk_cpi": sum(cpi(g(s, "scrum")) < cpi(g(s, "lane")) for s in sets),
            "sk_run": sum(m(s, "scrum", "cost_usd_notional") < m(s, "lane", "cost_usd_notional") for s in sets)}


def card(f, h, x):
    cols = [("Fair benchmark, 6 Nov", "small task, Opus 5.5 and gpt-6.1-sol, %d runs" % f["n"]),
            ("Hard benchmark, 10-12 Nov", "%d models, no pack against Lanewright, %d runs" % (h["models"], h["n"])),
            ("Extra phase, 13-14 Nov", "%d Claude settings, scrum-kit against Lanewright, %d runs" % (x["sets"], x["n"]))]
    rows = [("DoD met", "frozen grader", "consistent", [
                ("%d/%d vs %d/%d" % f["full"], "runs met every checked item, with vs without the pack"),
                ("%d → %d" % h["verdicts"], "runs of %d without review verdicts, no pack → pack; reports %d → %d. "
                 "Mean DoD up in %d of %d models (%d with D10)" % (h["arm_n"], *h["reports"], h["dod_up"], h["models"], h["dod10_up"])),
                ("%d vs %d" % x["reports"], "runs of %d without reports, scrum-kit vs Lanewright. Lanewright DoD higher "
                 "in %d of %d settings" % (x["pack_n"], x["dod_lw_higher"], x["sets"]))]),
            ("Hidden tests", "code correctness", "not consistent", [
                ("n/a", "this small task had no hidden acceptance tests"),
                ("%d vs %d" % h["suite"], "runs of %d passing every hidden test, without vs with. Per model: up %d, "
                 "same %d, down %d" % (h["arm_n"], *h["hid"])),
                ("%d vs %d" % x["suite"], "runs of %d passing every hidden test, scrum-kit vs Lanewright. Same in %d "
                 "settings, higher in %d" % (x["pack_n"], x["hid_same"], x["hid_lw_higher"]))]),
            ("Cost", "per passed item", "not consistent", [
                ("$%.2f vs $%.2f" % f["cost"], "Claude cost per sprint, with vs without (no hidden tests to divide by)"),
                ("$%.2f → $%.2f" % h["sol56"], "gpt-5.6-sol, no pack → pack. Lower with the pack for %d of %d models"
                 % (h["cpi_lower"], h["models"])),
                ("%d of %d" % (x["sk_cpi"], x["sets"]), "settings where scrum-kit was cheaper per passed item; "
                 "cheaper per run in %d of %d" % (x["sk_run"], x["sets"]))])]
    left, cw, top = 190, 242, 160
    b = [mark(28, 22), text(76, 52, "Lanewright benchmarks, as measured", size=24, weight=700),
         text(76, 76, "%d runs, 6-14 Nov 2026. The pack makes the process complete; it does not make the code reliably "
              "more correct or cheaper." % (f["n"] + h["n"] + x["n"]), "mu", 14)]
    for j, (head, sub) in enumerate(cols):
        cx = left + j * (cw + 10)
        b.append(text(cx + 14, 118, head, size=15, weight=700))
        b += [text(cx + 14, 136 + k * 16, line, "mu", 12) for k, line in enumerate(wrap(sub, 36))]
    for i, (label, sub, verdict, cells) in enumerate(rows):
        y = top + 12 + i * 132
        b += [text(28, y + 30, label, size=17, weight=700), text(28, y + 50, sub, "mu", 13),
              text(28, y + 76, verdict, size=13, weight=700)]
        for j, (big, cap) in enumerate(cells):
            cx = left + j * (cw + 10)
            b.append(f'<rect class="tile" x="{cx}" y="{y}" width="{cw}" height="120" rx="10"/>')
            b.append(text(cx + 14, y + 36, big, size=26 if len(big) <= 12 else 20, weight=700))
            b += [text(cx + 14, y + 60 + k * 17, line, "mu", 12) for k, line in enumerate(wrap(cap, 38))]
    foot = ("DoD by the frozen grader; D10 re-scores DoD item 1 (roles separated), which the grader misread after item "
            "branches were deleted. Notional cost at list prices, Claude prices corrected 14 Nov 2026 (D14). "
            "2-3 runs per cell on one task each: a direction, not significance.")
    b += [text(28, H - 52 + k * 17, line, "mu", 12) for k, line in enumerate(wrap(foot, 150))]
    label = "Lanewright benchmarks: " + "; ".join(
        "%s (%s): %s" % (r[0], r[2], ", ".join("%s: %s %s" % (c[0], big, cap) for c, (big, cap) in zip(cols, r[3]))) for r in rows)
    return svg(W, H, "\n".join(b), label)


def main():
    f, h, x = fair(), hard(), extra()
    # numbers the README text states; a data change that moves them should fail here, not drift silently
    assert f["full"] == (6, 6, 3, 6) and (h["n"], x["n"]) == (42, 16), (f, h, x)
    assert h["verdicts"] == (10, 2) and h["reports"] == (10, 1) and h["suite"] == (3, 4) and h["hid"] == (3, 2, 2), h
    assert (h["dod_up"], h["dod10_up"], h["cpi_lower"]) == (3, 6, 4) and [round(v, 2) for v in h["sol56"]] == [0.72, 2.79], h
    assert x["reports"] == (8, 0) and x["suite"] == (4, 6) and (x["sk_cpi"], x["sk_run"], x["dod_lw_higher"]) == (3, 4, 4), x
    out = os.path.join(HERE, "img", "overall-hero.svg")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(card(f, h, x))
    print("wrote", os.path.relpath(out, os.path.dirname(HERE)))


if __name__ == "__main__":
    main()
