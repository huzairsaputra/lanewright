# Trial, 2026-11-06: emergency hotfix and scheduled release

The first real run of the hotfix and release skills. One Claude Code run (Opus 5.5, API key,
isolated as in the fair benchmark), pack `a4164cf`. Prompt:
[`fair-2026-11-06/hotfix-release-prompt.md`](fair-2026-11-06/hotfix-release-prompt.md).

## Setup

- **Production state:** `main` is production, tagged `v1.0.0`. `staging` is one merged feature
  ahead: BE-1 added `admin.Greet` right after `Hello`.
- **Job 1, emergency hotfix HF-1:** `admin.Hello()` must return `"hello"`, not `"hi"`.
- **Job 2, release:** release `staging` to `main` as `v1.1.0`, with the schedule set to now.
- **Product-owner approvals:** given in advance for the HF-1 merge, the back-merge and the release.

## Result

Cost $3.02 (4 sessions, 38,714 output tokens), 10 minutes.

| Step | What happened |
|---|---|
| HF-1 implementer, QA, reviewer | Separate headless processes in worktrees from `origin/main` |
| Regression test | Red before the fix (`Hello() = "hi", want "hello"`), green after |
| Review | CLEAN (2 MINOR, 3 INFO) |
| PR to `main` | #1 merged with a merge commit after a green CI run on its head SHA |
| Patch tag | `v1.0.1`, annotated, pushed |
| Back-merge to `staging` | **Stopped**: `admin/admin.go` conflicted, because `Greet` sits on the line after `Hello`. The skill says a human resolves conflicts, so the agent stopped and named the resolution (keep both). |
| Release `v1.1.0` | **Stopped at the readiness check**: `git log --no-merges S..origin/main` listed the hotfix commits that were not back-merged. Releasing `staging` then would have undone the fix in production. |

Both stops are what the skills require. The run did not finish both jobs. On a real project, that
conflict would also stall the next release until a human resolves it.

## Re-run after the fixes (pack `5ad2917`)

Problems 1–12 below were fixed in `5ad2917` through one Batch API request. The trial then ran
again, Opus 5.5 with the API key and the same isolation, in a fresh repository. There, BE-1's
`Greet` lives in its own file, so the back-merge does not conflict, and the handover records the
last staging deploy and a release checklist. Cost $4.88 (5 sessions, 62,988 output tokens),
17.3 minutes.

| Step | Result |
|---|---|
| HF-1 | Regression test red at the QA commit on the unfixed base, green after the fix merged in. Review CLEAN. PR #1 merged into `main` after green CI on its head. Tag `v1.0.1`. |
| Back-merge | PR #2 `claude/backmerge-HF-1` → `staging`, merged after green CI. Its review verdict is in the PR description. |
| Release `v1.1.0` | PR #3 `claude/release-v1.1.0` → `main`, merged after green CI on its head, tagged `v1.1.0`. `main` now has the hotfix and BE-1. |
| Handover after release | PR #4 → `staging`, left open: no rule lets the agent merge it. |

Every merge waited for a green CI run on the exact head SHA (7 runs). Both jobs finished.

### Third run (pack `8fbe0b6`, the 7 problems below fixed)

Same setup in a fresh repository; Opus 5.5, API key, isolated. Cost $3.45 (4 sessions), 15 minutes.

- **Everything merged:** HF-1 (PR #1, `v1.0.1`), the back-merge (PR #2), the release (PR #3,
  `v1.1.0`), and the release handover update (PR #4). The last one merged under the release
  approval, after green CI.
- **CI:** all 7 runs green, each on the exact head SHA.
- **End state:** `main` and `staging` both return `"hello"`, and the handover records the release.

Remaining problems (known, not fixed; none blocked the run):

- Role reports for a hotfix still land on `main`.
- The orchestrator's documents commit on the back-merge branch is not reviewed separately.
- Cleanup rules do not mention `hotfix/<ID>` and `claude/backmerge-<ID>`.
- The hotfix spec should be written against the hotfix target, not the base.
- The forge merge-settings check covers GitLab only. A GitHub repository that allows squash or
  rebase merges is not detected, so `--merge --match-head-commit` is what keeps merges correct.
- The release skill reads the version only from the first argument.
- The fallback for a missing pipeline on `S` is vague.
- `Last deployed to staging` is never updated by the release skill.
- The release checklist is not tied to a SHA.
- Matching merge commits to MRs through the forge search can return the same MR twice.
- A read-only reviewer can still read report files through a search before its verdict (deny
  rules block writes, not reads).

### Problems from the second run (fixed in `8fbe0b6`)

- The handover can't be committed when an item starts, because `hotfix/<ID>` only exists from step
  6.
- Updating the handover on the hotfix branch guarantees a back-merge conflict.
- There's no place to save the back-merge review verdict without changing the reviewed head.
- The release step 8 handover PR has no merge rule.
- "`S` already deployed to staging" can never hold right after a back-merge. The skill covers a
  missing line, not one that names an older deploy.
- The release MR search by date also picks up MRs already in production.
- A module-dev `test` gate stays red when the old test asserts the bug. The brief doesn't cover
  that case, and QA owns the test.

## Problems found in the first run (1–12 fixed in `5ad2917`)

Hotfix skill:

1. No path when the back-merge conflicts, although a hotfix and the base often touch nearby lines.
2. The spec is written to a temp file outside the repository, which headless roles in their
   worktrees are not allowed to read.
3. "Red before the fix, green after" clashes with step 4, where QA starts from a worktree that
   already contains the fix. The agent had QA commit the test on the unfixed base first.
4. No home for documents written after the merge (post-incident review, handover line). The agent
   used the back-merge branch.
5. No naming rule for the hotfix integration branch. The agent used `hotfix/HF-1`.
6. The sprint number for the item branch is not defined for out-of-sprint work.

Shared:

7. The dispatch example unsets `ANTHROPIC_API_KEY`, which conflicts with an operator who bills
   roles to the API on purpose.
8. A read-only reviewer cannot re-run "red before the fix" (no stash or worktree).
9. Role reports on the reviewed branch still reach the reviewer through `merge-tree` previews.
10. No MR template in the trial repo; the fallback structure was used.

Release skill:

11. Release notes find PRs only from `Merge pull request #N` messages, and miss merges with
    other wording.
12. Readiness needs a "last deployed" line and a production checklist that the generated handover
    does not have.
13. CI did not start on push in the trial repository, as in every run; this is the repository, not
    the skill.
