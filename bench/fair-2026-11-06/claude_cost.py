"""Sum token usage and wall time from Claude Code transcripts whose project dir matches a prefix.

py -I metrics.py <project-dir-name-prefix>   ->  JSON per session and totals
"""
import glob
import json
import os
import sys
from datetime import datetime

ROOT = os.path.expanduser("~/.claude/projects")


# List prices, $ per token (claude-api skill; Opus checked against a CLI-reported cost). Cache writes
# are 1.25x (5 min) and 2x (1 h) the input price.
PRICES = {
    "claude-opus-5-5": {"input": 4e-6, "output": 20e-6, "cache_read": 0.2e-6, "cache_write_5m": 5e-6, "cache_write_1h": 8e-6},
    "claude-sonnet-5-5": {"input": 2e-6, "output": 10e-6, "cache_read": 0.2e-6, "cache_write_5m": 2.5e-6, "cache_write_1h": 4e-6},
}


def session(path):
    usage = {"input": 0, "output": 0, "cache_read": 0, "cache_write_5m": 0, "cache_write_1h": 0}
    times, turns, seen, cost, models = [], 0, set(), 0.0, set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("timestamp"):
                times.append(datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00")))
            m = d.get("message") or {}
            u = m.get("usage") if d.get("type") == "assistant" else None
            if u and m.get("id") not in seen:  # one API response can span several transcript lines
                seen.add(m.get("id"))
                turns += 1
                cc = u.get("cache_creation") or {}
                w1h = cc.get("ephemeral_1h_input_tokens", 0)
                msg = {"input": u.get("input_tokens", 0), "output": u.get("output_tokens", 0),
                       "cache_read": u.get("cache_read_input_tokens", 0), "cache_write_1h": w1h,
                       "cache_write_5m": u.get("cache_creation_input_tokens", 0) - w1h}
                for k, v in msg.items():
                    usage[k] += v
                model = m.get("model") or "?"
                models.add(model)
                price = PRICES.get(model)
                if price is None and any(msg.values()):
                    sys.exit(f"no price for model {model} in {path}")
                cost += sum(msg[k] * price[k] for k in price) if price else 0
    span = (max(times) - min(times)).total_seconds() if times else 0
    return {"file": path, "turns": turns, "seconds": round(span), **usage, "cost": round(cost, 4),
            "models": sorted(models),
            "start": min(times).isoformat() if times else None, "end": max(times).isoformat() if times else None}


prefix = sys.argv[1]
rows = []
for d in sorted(glob.glob(os.path.join(ROOT, prefix + "*"))):
    for p in sorted(glob.glob(os.path.join(d, "**", "*.jsonl"), recursive=True)):  # includes subagent transcripts
        r = session(p)
        r["dir"] = os.path.basename(d)[len(prefix):] or "(root)"
        rows.append(r)
starts = [r["start"] for r in rows if r["start"]]
ends = [r["end"] for r in rows if r["end"]]
tot = {k: sum(r[k] for r in rows) for k in ("turns", "input", "output", "cache_read", "cache_write_5m", "cache_write_1h", "cost")}
tot["cost"] = round(tot["cost"], 4)
tot["sessions"] = len(rows)
if starts:
    tot["wall_seconds"] = round((datetime.fromisoformat(max(ends)) - datetime.fromisoformat(min(starts))).total_seconds())
print(json.dumps({"sessions": [{k: v for k, v in r.items() if k != "file"} for r in rows], "total": tot}, indent=1))
