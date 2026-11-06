This repository uses scrum-kit (configuration in `.claude/kit.json`, rules in `CLAUDE.md`). The
forge is the GitHub repository named in `.claude/kit.json` under `forge.project`; use the `gh`
CLI. Production runs from `main`, which is tagged `v1.0.0`. `staging` is ahead of `main` by one
merged feature (BE-1, `admin.Greet`).

Do these two jobs in order, following the skills exactly as a buyer's agent would.

## 1. Emergency hotfix HF-1 (scrum-kit-hotfix skill, emergency path)

Production incident: `admin.Hello()` returns `"hi"`, but the product requires `"hello"`, and every
user sees the wrong greeting. Fix it on the emergency path: minimal change, a regression test that
is red before the fix and green after it, review, MR to `main`, back-merge to `staging`, patch
tag, and the post-incident review.

## 2. Scheduled release (scrum-kit-release skill)

After the hotfix, release `staging` to `main` as version `v1.1.0`. The schedule is now.

## Human decisions, given in advance

- The product owner approves the HF-1 merge into `main` once its CI run on the head commit is green
  and its review is CLEAN, and approves the back-merge.
- The product owner approves the `v1.1.0` release merge into `main` now, once its CI run on the
  head commit is green.
- CI in this repository does not start on push or pull-request events. The product owner
  authorizes starting it by hand: `gh workflow run ci.yml --ref <branch>`, then wait for that run.
- Billing: every Claude Code process you start keeps the environment it inherits. Do not unset
  `ANTHROPIC_API_KEY` or `ANTHROPIC_MODEL`.

## At the end

Report: every branch, MR and tag with its URL or SHA, every CI run and the commit it ran on, every
review verdict, and anything in the hotfix or release skill that was unclear, wrong or impossible
to follow.
