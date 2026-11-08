# Third end-to-end test: approving "not applicable" Definition-of-Done items (7-8 Nov 2026)

The second test ([gate-2026-11-07](../gate-2026-11-07/README.md)) ended with an open question: when a
role marks a Definition-of-Done (DoD) item "not applicable" (for example a negative authorization test in
an app with no login), who may approve that? Agents had either guessed or stopped. The fix, released as
[Lanewright Planning v1.0.2](https://github.com/huzairsaputra/lanewright-planning/releases/tag/v1.0.2) and
[scrum-kit v1.4.1](https://github.com/huzairsaputra/scrum-kit/releases/tag/v1.4.1) (and folded into
Lanewright 1.0.1), is a contract:

- the Sprint Planner **proposes** DoD items that may not apply, each with a reason from the SRS;
- the Backlog Check report lists the proposals; its sign-off block has a field `DoD not applicable
  (approved):` that only a human fills;
- the sprint workflow treats an item as approved only if that field names it **and** the report's SHA-256
  fingerprint still matches the backlog; otherwise the line reads "pending product-owner approval", is not
  counted as met, and the integration branch is **never merged into the base branch** while one is pending.

This test checks that the contract works with the released versions.

![Wall time and cost of the 14 runs](runs.svg)

(PNG: [runs.png](runs.png). Raw numbers and tokens per run: [results.json](results.json).)

## Method

- **Input:** the same invented one-line notes-app brief as the earlier tests; one fresh throwaway
  repository without a remote per workflow tool, local mode. Both tools plan from the same SRS.
- **12 headless runs on an API key** (`claude -p --bare`, `claude-opus-5-5`): setup, the planning chain,
  Backlog Check, and per tool three gate dry runs. The dry runs follow the sprint preparation up to the
  readiness gate and stop before dispatching any role.
- **Three states of the sign-off**, each in its own copy of the same repository (the human is simulated by a
  script that fills the sign-off block):

  | State | DoD field of the sign-off | Expected reading |
  |---|---|---|
  | naok | names the "negative authorization test" item | approved; a later "not applicable" mark on it is accepted without asking |
  | nanone | says none | no item approved; a later mark means "pending product-owner approval" |
  | naold | report in the old format, no such field | same as none |

- **Two full sprints on the Claude Code subscription**, one per tool, in the repositories left by the
  dry-run chain (field says none, nobody can answer). They ran isolated from the researcher's own settings:
  no user `CLAUDE.md`, skills, plugins or MCP servers, no API key (`apiKeySource` of the init message was
  `none`). Cost on the subscription is not billed; the figures here are the notional list price.
- Costs of the sprints come from the transcripts of every process, because the report of the main
  process covers only that process.

## Results

### The contract: read correctly in all 6 dry runs, and held in both sprints

| State | Lanewright | scrum-kit |
|---|---|---|
| naok | approved set read correctly | approved set read correctly |
| nanone | empty set, "pending" rule quoted | empty set, "pending" rule quoted |
| naold | read as "none approved" | read as "none approved" |

A proposal from the planner was read as a proposal only, never as an approval.

In the two full sprints the roles marked the "no login" DoD items not applicable (scrum-kit: one item
class on all six items; Lanewright: two classes, six entries in all). Nobody could approve, so in both
sprints:

- each such line was recorded as "pending product-owner approval", unticked, in the merge notes and the
  handover;
- every item still merged into the integration branch because all its other DoD items were met;
- the sprint stopped after the close-out commit and listed every pending approval;
- **the integration branch was not merged into the base branch** (the base branch stayed on the commit of
  the sprint documents).

| | Lanewright | scrum-kit |
|---|---|---|
| Items merged into integration | 6 of 6 (17 SP) | 6 of 6 (17 SP) |
| Tests at the end | 115 (3 skipped on Windows) | 55 |
| Reviews | CLEAN on all merges (one item needed four rounds) | CLEAN on all three merges |
| Merged into the base branch | no, 6 approvals pending | no, 1 approval pending |
| Processes | 26 | 11 |
| Wall time | 4143 s (one pause, see below) | 2035 s |
| Notional cost, all processes | $17.88 | $6.06 |
| Turns | 387 | 130 |

### One finding about the test, not the contract

In the Lanewright dry runs the new Backlog Check returned NOT READY, because an old test called `add()`
without an author, so the first backend item could not merge with green tests. The three Lanewright dry
runs therefore stopped at the gate. For the full sprint the standing answers continued with a written
reason (the finding is resolved inside the sprint); the sprint then fixed it. The approval script of the
harness signs any report whatever its verdict. That is a weakness of the simulation, not of the tools.

### Pause

The Lanewright sprint stopped once at the account's five-hour usage limit after 3701 s. It was resumed in
the same session from the handover and the git state and finished in 442 s without redoing finished items.
The scrum-kit sprint ran uninterrupted.

The limit is a usage quota of the subscription account, counted on the provider's side in model tokens
and shared by every session of that account. It is not a fault of the tools and not a lack of local
resources. Both sprints ran at the same time on the same account, next to the researcher's own
interactive session, which together used up the five-hour allowance; the error was a 429
`usage_limit_reached`. The 4143 s is the 3701 s before the stop plus the 442 s after the resume; the waiting time in between
is not counted.

## Addendum: the approved path (8 Nov 2026, later the same day)

The two sprints above never had an approval, so they only showed the *held back* half of the contract.
This addendum runs the other half: when the sign-off does approve the items a role marks "not
applicable", the integration branch must merge into the base branch without anyone being asked.

- **Setup.** One copy per tool of the repository left by the gate dry run (before any role ran), with the
  readiness report's DoD field filled by a script with the names exactly as the report proposed them. For
  scrum-kit that is one item whose name itself contains a semicolon; for Lanewright three names.
- **Same standing answers and isolation as before**, one sprint at a time (not in parallel), on the
  subscription, no API key.

![Wall time and cost of the two sprints](results-approved.png)

(Raw numbers: [results-approved.json](results-approved.json).)

| | Lanewright | scrum-kit |
|---|---|---|
| Items merged into integration | 6 of 6 (17 SP) | 6 of 6 (17 SP) |
| Roles' "not applicable" marks | 3 classes, all named in the sign-off | 1 class, named in the sign-off |
| Approvals pending at the end | none | none |
| Integration branch merged into the base branch | **yes**, one local merge commit | **yes**, one local merge commit |
| Reviews | CLEAN on the first round, three of three | one NOT CLEAN round (2 major, 3 minor), then CLEAN; the other two CLEAN at once |
| Tests at the end | 58 | 56 (4 Linux-only tests skipped on Windows; all 56 pass under WSL) |
| Processes / wall time | 10 / 992 s | 14 / 2058 s |
| Notional cost, all processes / turns | $6.04 / 152 | $9.81 / 209 |

Both sprints read the approval correctly, recorded each "not applicable" line as approved in the sprint
handover, and merged. The contract works on the approved path as well as on the held-back one.

The Lanewright sprint cost about a third of the earlier one ($6.04 against $17.88), the scrum-kit sprint
about 60 percent more ($9.81 against $6.06, with one extra review round). Do not read that as a
comparison: one run per cell, and neither run here started the security auditor (see below), which is
where the earlier Lanewright sprint spent four rounds.

### What the runs reported as unclear

These come from each sprint's own closing report and are listed so they can be fixed, not because they
broke the contract:

1. **A name with a semicolon.** The DoD field separates names with `;`, and the item proposed by the
   report contains one. The scrum-kit run guessed that both halves belong to one item. The field needs a
   different separator, or the proposals need names without `;`.
2. **A misleading gate line (Lanewright).** The report's verdict was NOT READY while its sign-off was
   filled. The handover template then says "continued without sign-off", which is wrong for that case.
   The run also noted the rules apply the approved set whatever the verdict, and it did.
3. **A reused integration branch (scrum-kit).** The integration branch already existed from preparation
   and was not brought up to date with the base branch, so role worktrees saw an older sign-off line until
   the final merge.
4. **Child processes inherit the user's plugins.** The first dispatch of a role by plugin name failed
   until the plugin directory was passed explicitly. This is the same isolation limit listed above.
5. **No security audit in either sprint.** Both orchestrators decided against it, on the reasoning that
   the author nickname is visible to the whole team by design, while the SRS of the test project calls it
   personal data. The workflow leaves that call to the orchestrator. It probably explains why the
   Lanewright sprint was far cheaper than the earlier one.
6. **A harness detail.** The scripted sign-off was an uncommitted edit of the report; the scrum-kit run
   assumed the product owner made it. In real use the signed report should be committed first.

**What was done with them (8 Nov 2026).** Items 1, 2, 3 and 5 are fixed in
[scrum-kit 1.4.2](https://github.com/huzairsaputra/scrum-kit/releases/tag/v1.4.2),
[Lanewright Planning 1.0.3](https://github.com/huzairsaputra/lanewright-planning/releases/tag/v1.0.3)
(item 1 only) and Lanewright 1.0.1, which has not been uploaded anywhere yet. Item 1 is fixed twice:
the planning skills no longer write a semicolon inside a proposed name, and the workflow tools match a
whole proposal before splitting, so reports written earlier still read correctly. Item 4 needed no
change: scrum-kit already tells the orchestrator to retry with the plugin directory. Item 6 is a harness
detail. The fixes were checked by the unit tests and the build of each product, **not** by another full
sprint, so they are unproven in a run.

## Limits

- One small invented repository, one run per cell: a direction, not a rate.
- The two sprints shared one laptop and one account while they ran in parallel, so their wall times may
  be inflated by competing for CPU and for the account's usage quota. This was not measured; compare the
  two sprints with each other only as a direction. A study that compares conditions should run them one at
  a time.
- The role processes started by either sprint inherited the researcher's settings; only the orchestrating
  process was isolated. The Lanewright sprint ran four security-audit rounds on its first item, which is
  probably why it cost about three times as much as the scrum-kit sprint; this test does not isolate that.
- The "approval" is either always absent (the first two sprints) or always present and scripted (the
  addendum). Whether a real product owner decides well is a question for the later study, not for this
  harness.

## Run time and cost of this test

| | Runs | Wall seconds | Cost |
|---|---|---|---|
| 12 runs on an API key | 12 | 3082 | $8.79 |
| 2 full sprints on the subscription | 2 | 6178 | not billed ($23.94 notional) |
| 2 approved-path sprints on the subscription (addendum) | 2 | 3050 | not billed ($15.85 notional) |

All figures recorded per run in [results.json](results.json); redraw the chart with `py -I charts.py`.
