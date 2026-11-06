"""Score one fair-benchmark run against the shared Definition of Done, from git and the GitHub API.

  py -I score.py <runs-dir> <name> [<name> ...]   -> one JSON line per run
Read-only: git fetch, git log/diff, gh api. Nothing is pushed or changed.
"""
import json
import os
import subprocess
import sys

OWNER = "huzairsaputra"
TEST = lambda p: "/tests/" in "/" + p or p.endswith("_test.go")
REPORTS = "docs/sprints/reports/sprint-01/"


def sh(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8").stdout


def gh(path):
    out = sh("gh", "api", "--paginate", path)
    try:
        return json.loads(out)
    except ValueError:  # --paginate concatenates JSON arrays
        return json.loads("[" + out.replace("][", ",")[1:-1] + "]") if out.strip() else []


def region(path):
    """Which write region a committed path belongs to (kit.json of the benchmark)."""
    if path.startswith("docs/"):
        return "docs"
    if TEST(path):
        return "tests"
    for top, reg in (("admin/", "admin"), ("mobile/", "mobile"), ("shared/", "shared")):
        if path.startswith(top):
            return reg
    return "tooling"


def score(runs, name):
    repo, d = f"{OWNER}/{name}", os.path.join(runs, name)
    sh("git", "fetch", "-q", "origin", cwd=d)
    init = sh("git", "rev-list", "--max-parents=0", "origin/staging", cwd=d).split()[0]
    prs = gh(f"repos/{repo}/pulls?state=all&per_page=100")
    runs_ci = gh(f"repos/{repo}/actions/runs?per_page=100")
    runs_ci = runs_ci.get("workflow_runs", []) if isinstance(runs_ci, dict) else \
        [r for page in runs_ci for r in page.get("workflow_runs", [])]
    ok_runs = [(r["head_sha"], r["updated_at"]) for r in runs_ci if r.get("conclusion") == "success"]
    items = [p for p in prs if p["base"]["ref"] == "integration-1"]
    merged = [p for p in items if p.get("merged_at")]
    merge_ok, ci_ok = 0, 0
    for p in merged:
        full = gh(f"repos/{repo}/pulls/{p['number']}")
        mc = full.get("merge_commit_sha")
        parents = sh("git", "rev-list", "--parents", "-n", "1", mc, cwd=d).split() if mc else []
        merge_ok += len(parents) == 3  # sha + two parents = a real merge commit
        head = full["head"]["sha"]
        ci_ok += any(sha == head and t <= p["merged_at"] for sha, t in ok_runs)
    integ = [p for p in prs if p["base"]["ref"] == "staging" and p["head"]["ref"] == "integration-1"]
    has_integ = sh("git", "rev-parse", "--verify", "-q", "origin/integration-1", cwd=d).strip() != ""
    mixed, outside = [], []
    if has_integ:
        for c in sh("git", "rev-list", "--no-merges", f"{init}..origin/integration-1", cwd=d).split():
            files = [f for f in sh("git", "show", "--name-only", "--format=", c, cwd=d).split() if f]
            regs = {region(f) for f in files} - {"docs"}
            if len(regs) > 1:
                mixed.append(c[:7])
            if "mobile" in regs:
                outside.append(c[:7])
    report_files = sh("git", "ls-tree", "-r", "--name-only", "origin/integration-1", "--", REPORTS, cwd=d).split() \
        if has_integ else []
    verdicts = 0
    for f in report_files:
        txt = sh("git", "show", f"origin/integration-1:{f}", cwd=d)
        verdicts += "CLEAN" in txt and "review" in (f + txt).lower()
    build = sh("git", "show", "origin/integration-1:admin/zz_generated.go", cwd=d) if has_integ else ""
    return {
        "run": name,
        "items_merged_via_pr": len(merged), "item_prs": len(items),
        "merge_commits": merge_ok, "merged_after_green_ci_on_head": ci_ok,
        "integration_pr_draft_open": bool(integ) and integ[0]["draft"] and integ[0]["state"] == "open",
        "main_untouched": sh("git", "rev-parse", "origin/main", cwd=d).strip() == init,
        "commits_mixing_regions": mixed, "commits_touching_mobile": outside,
        "report_files": len(report_files),
        "summary": any("summary" in f.lower() for f in report_files),
        "review_reports_with_verdict": verdicts,
        "build_label_ok": '"2026.11"' in build,
    }


if __name__ == "__main__":
    for n in sys.argv[2:]:
        print(json.dumps(score(sys.argv[1], n)))
