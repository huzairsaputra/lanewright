# Runs with the pack, and how each one ended

Readers asked how many failed runs the pack has, and whether the extra roles pay for themselves. The
only controlled comparison with a no-pack arm is [`fair-2026-11-06`](fair-2026-11-06/README.md): without the
pack 3 of 6 runs failed the Definition-of-Done check (every miss was a report or the sprint summary left
uncommitted), with the pack 0 of 6. That test could not show a difference in broken work, because in all 12
of its runs every item merged through a PR after CI went green on its head commit.

This page adds what the other tests say about the pack **alone**. It is a tally of records already
published, nothing new was run for it. It is not a comparison: the tests used different tasks, different
pack versions, different set-ups, and there is no no-pack arm outside the fair benchmark.

## How a run is counted

Only runs that were asked to deliver a whole job count here: a full sprint, or the hotfix and release
pair. The dry runs and the planning runs are listed separately below.

- **Finished:** every item it was asked to deliver was merged (into the integration branch, or into the
  base branch when no approval was pending), and the merge waited for green CI on its head commit, or
  for the local gate where the repository had no remote. No human fixed anything for it. For the runs
  in local mode this tally relies on each run's own report, not on a separate check.
- **Stopped by design:** it stopped where the pack tells a human to decide (a back-merge conflict, a
  release that would undo a fix, a CI that could not start), and the job was not finished.
- **Interrupted from outside:** stopped by something that is not the pack, then resumed.

## The tally

| Test | Pack runs asked for a whole job | Finished | Stopped by design | Interrupted from outside |
|---|---|---|---|---|
| [First benchmark](2026-11-05-trial.md), pack 1.0.0 | 3 | 2 | 1 (CI could not start, every merge held back) | 0 |
| [Check run](2026-11-05-check.md) | 1 | 1 | 0 | 0 |
| [Fair benchmark](fair-2026-11-06/README.md), pack arms | 9 (3 Claude, 3 Codex, 3 with cheaper settings) | 9 | 0 | 0 |
| [Hotfix and release](2026-11-06-hotfix-release.md) | 3 | 2 | 1 (back-merge conflict, then the release readiness check) | 0 |
| [Second test](gate-2026-11-07/README.md), full sprints | 2 | 2 | 0 | 0 |
| [Third test](verifikasi-2026-11-08/README.md), full sprints, both parts | 4 | 4 (two held back from the base branch on purpose while an approval was pending) | 0 | 1 (a five-hour usage limit, resumed) |
| **Total** | **22** | **20** | **2** | **1** |

The one interrupted run is counted as finished, because it finished after the resume.

Not in the tally:

- **18 dry runs** that stop before any role starts (10 gate scenarios in the second test, 6 in the third,
  2 in the planning test): every one stopped or continued where it should. Three Lanewright dry runs in
  the third test stopped on a real NOT READY verdict, because an old test of the test project called a
  function without an author.
- **The planning runs** (intake, SRS, sprint plan, Backlog Check): all exited with code 0.

## What the tally does not say

- **Finished is not the same as no friction.** Every test surfaced points where the agent had to guess
  or stop and wrote it down: 20 in the first benchmark, 9 in the check run, about 12 in the first hotfix
  run, 11 in the first planning test, 6 in the second test and 6 in the third. Each was fixed in a later
  version, so the early runs, on older versions, are the ones with the most stops.
- **The author tested what the author fixed.** The same person wrote the pack, picked the tasks, fixed
  each finding and ran the next test. Fixes were checked by unit tests, but only the next test could
  prove them.
- **Some things were done by hand on purpose.** In the first tests CI was started by hand under a
  product-owner decision written in the prompt, and in the third test the approval was a script.
- **Small, invented tasks.** One small project per test, a handful of items, mostly one run per cell. None
  of these tasks is hard enough to make a model's unaided work fail, so a zero here is a statement about
  the tasks, not a rate for real projects.
- **Where the pack can help or hurt is not shown.** A task with a real chance of broken work, with many
  runs per condition and a definition of a failed run fixed before the results, is the test that would
  answer the question. It has not been run.
- **Not independent evidence of quality.** Review quality and whether tests came from another session
  were read from transcripts in the fair benchmark and not scored.
