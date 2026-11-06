Run sprint 1 of this repository. The backlog is `docs/sprints/sprint-01-backlog.md`; the project
configuration (branches, modules, write regions, gate commands, document paths, forge) is
`.claude/kit.json`; project rules are in `CLAUDE.md`. The forge is the GitHub repository named in
`.claude/kit.json` under `forge.project`; use the `gh` CLI.

## Definition of Done (every item must meet all of it)

1. The item is implemented by an implementer.
2. Its tests are written by a different session from the one that wrote the implementation.
3. A session that wrote neither the code nor the tests reviews the change and writes a verdict,
   CLEAN or NOT CLEAN, with findings. A NOT CLEAN item goes back for fixes and is reviewed again.
4. Write regions in `.claude/kit.json` are respected: implementation commits touch only the
   implementer's region, and test commits only the tests region. Nothing is committed outside the
   region of the session that commits it.
5. Each item reaches the integration branch (`integration-1`, created from `staging`) through its
   own pull request. The PR is merged with a merge commit (no squash, no rebase), and only after
   (a) a successful run of the `ci` workflow on the PR's exact head commit, and (b) a CLEAN review
   of that head commit.
6. Every session that worked on an item writes a short report in `docs/sprints/reports/sprint-01/`
   with the commands it ran and their real output. At the end there is a sprint summary in the
   same folder.
7. At the end, a pull request from `integration-1` into `staging` is open as a **draft**. Do not
   merge it. Do not touch `main`.

## Human decisions, given in advance

- CI in this repository does not start on push or pull-request events. The product owner
  authorizes starting it by hand: `gh workflow run ci.yml --ref <branch>`, then wait for that run.
- BE-2: if it cannot be done without writing outside the admin region, keep `mobile/` unchanged and
  record the gap as code debt in `docs/sprints/code-debt.md`. That is enough for BE-2 to be
  reviewed and merged.
- Billing: every Claude Code process you start, including any helper or role process, keeps the
  environment it inherits. Do not unset `ANTHROPIC_API_KEY` or `ANTHROPIC_MODEL`.

## At the end

Report: every branch and PR with its URL and state, every CI run and the commit it ran on, every
review verdict, and any part of the Definition of Done you could not meet, with the reason.
