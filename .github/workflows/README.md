# Repository automation

The GitHub Actions in this directory run Atlas on itself: an issue is picked
up, implemented, reviewed, and merged without a human in the loop, and `dev`
is promoted to `main` on a schedule. This file is the map; each workflow's
header comment explains its own design choices.

For the *bundle* workflows that ship to users (the `workflows/` presets and
their gates), see [`workflows/README.md`](../../workflows/README.md) — that is
a different thing that merely shares the word "workflow".

## The chain

```
issue (`type:feature`)
        │
        ▼
feature-reviewer.yml ──evaluates + labels `action:develop`──▶ queue.yml
   (posts evaluation)                                            (drains one issue at a time,
                                                                  once the lane is free)
                                                                        │
                                                                        ▼
                                                          auto-developer.yml  (WIP = 1)
                                                             (implements, retargets PR to dev)
                                                                        │
                                                                        ▼
                                              auto-reviewer.yml ──approves──▶ auto-merge.yml
                                                 (review, ≤20 files)            (squash-merges into dev
                                                                                + closes the issue)
                                                                                       │
                                   Validate Bundle must pass ─────────────────────────┘
                                                                                       │
                                                                                       ▼
                                                                    promote.yml (weekly, dev → main)
```

| Workflow | Trigger | Does |
| --- | --- | --- |
| `validate.yml` | PR, push to `dev`/`main` | Runs `scripts/validate-refs.py`, `build-lite.py --check`, `validate-workflows.py`. |
| `auto-developer.yml` | issue labeled `action:develop` | Runs opencode, which commits a branch and opens a PR, then retargets that PR from `main` to `dev` and sets its title from the issue, so the PR listing is deterministic rather than whatever the model happened to say. Runs at **WIP = 1**: a gate job yields the lane while another implementation PR is in flight, because every feature rewrites the same shared files, so concurrent branches cannot all merge. Makes `.github/workflows/` read-only (the token cannot push there), regenerates the derived files (`manifest.json` integrity hashes and `lite/`) and runs the validators, requires the reply to end in one short line (that line is the PR title, and a longer one is rejected by the API), and reports a failed run on the issue. |
| `queue.yml` | every 15 minutes, manual dispatch | Drains the WIP-1 lane: once no implementation PR is in flight, re-adds `action:develop` to the oldest waiting issue. A concurrency group can serialise *runs* but cannot express "wait until that PR has merged", so this is what makes the lane actually advance. It also retries an issue whose run yielded the lane or whose PR was closed — but never one the reviewer has rejected. |
| `auto-reviewer.yml` | PR `opened`/`reopened` | A size gate first rejects anything over 20 files or 1000 changed lines — that is the size that cannot be reviewed in time and collides with every other branch — then runs opencode to pick a verdict, then submits the `gh pr review` itself. The agent only writes its verdict to `.atlas/review-verdict.txt` (gitignored) and a workflow step submits it, so neither a model that narrates a command instead of running it nor a sandbox that blocks writes outside the workspace can silently skip the review. It works from the diff under a hard tool-call budget, because an exhaustive review is what runs out of time. Close/reopen a PR to re-queue a review. |
| `auto-merge.yml` | `Auto Reviewer` run completes (plus manual `workflow_dispatch`) | When a same-repo PR into `dev` has a current approval: waits for checks, then `gh pr merge --squash --delete-branch`, passing `--subject` from the PR title so the squash commit is deterministic (the repo's `COMMIT_OR_PR_TITLE` setting would otherwise take the subject from the model's branch commit), and closes the issue the PR names (`Closes #N`, or `issue<N>` in the branch). Triggered by `workflow_run`, not `pull_request_review`, because the bot's own approval is made with `GITHUB_TOKEN` and so raises no workflow run — and `workflow_run` also guarantees main's copy of the file runs. Runs even when the reviewer did not conclude `success`, so a review that never completed is reported on the PR; the merge itself still requires a live approval. |
| `promote.yml` | weekly schedule, `/promote` comment, manual dispatch | Re-runs the bundle validators on the merged tree, then merges `dev` into `main` and pushes. The only path into `main`. |
| `promote-dispatch.yml` | `/promote` comment | Validates the command and dispatches `promote.yml`. |
| `feature-reviewer.yml` | issue `opened` with `type:feature`, or labeled `type:feature`/`action:evaluate` | Posts an evaluation (the action comments the agent's reply itself) and then labels the issue `action:develop` with `PROMOTE_PAT`, which starts development. `action:evaluate` is the manual retry/sweep label. |
| `trend-investigator.yml` | weekly schedule | Opens `type:feature` issues from research. Files them with `PROMOTE_PAT` so the issues raise a real `opened` event and `feature-reviewer` actually evaluates them. |

The human entry points are deliberately few: file an issue (or let
`trend-investigator` file one), which is evaluated and then developed
automatically; label an issue `action:develop` to skip the evaluation and start
work immediately; comment `/promote` to ship early; and step in only if a run
fails.

## Limits

Every limit below exists because the unbounded version of it broke something
concrete. They are structural caps, not tuning knobs:

| Limit | Value | Why |
| --- | --- | --- |
| Implementations in flight | 1 (`auto-developer.yml` gate + `queue.yml`) | 45 branches cut from the same `dev` all rewrote `manifest.json`'s integrity map, `CHANGELOG.md` and `rules/atlas-core.md`, so 28 PRs became unmergeable — 13 of them already approved. |
| PR size | 20 files / 1000 changed lines | A 30-file PR took 40 minutes and 113 shell calls to review and was cancelled with nothing to show. Over budget gets rejected rather than reviewed badly. |
| Reviewer effort | ~15 tool calls, 40-minute ceiling | The model is slow here; an unbounded review loses the race with the job timeout. |
| Developer effort | 30-minute ceiling | Issue #1's implementation used 16 of its original 20. |
| Evaluation effort | 10-minute ceiling | Read-only; it should never need more. |
| `.github/workflows/` | read-only, at the filesystem | `PROMOTE_PAT` has no `workflows` permission, so a workflow edit is rejected at push time and kills the run. |
| PR title | 200 characters | The action derives the PR title from the model's reply, and GitHub rejects anything longer with a 422 — which failed two runs outright. |
| Derived files | regenerated, never hand-written | `manifest.json`'s `integrity` map and `lite/` are outputs of the tree. Hand-maintaining them produced both the conflicts and the silent drift on `dev`. |

On the platform limits themselves: the API rate limit (5000/hour, ~4980 free at
rest) is nowhere near a constraint here. GitHub's *concurrent job* limit is — a
burst of 45 runs simply queues — which is why the pipeline serialises itself
rather than relying on queue position.

## When a run fails

Every step here talks to a remote model, so the usual failures are time, not
logic: the agent runs out of its job timeout, or the provider errors on a slow
stream. The design rule is that a failure must be **visible and cheap to
retry**, never a silent stall.

Retries, by stage:

| Stalled at | Retry with |
| --- | --- |
| Evaluation | Add the `action:evaluate` label. |
| Development | Remove and re-add the `action:develop` label. |
| Review | Close and reopen the PR (that is what the `reopened` trigger is for). |
| Merge on infrastructure | `gh workflow run auto-merge.yml -f pr=<n>`. |

What makes each stage survivable:

- **Bounded work.** Both agents are told to stop early and are given a hard
  budget (reviewer: ~15 tool calls; developer: one small change). Exhaustive
  work is what loses the race with the timeout — a 40-minute, 113-shell-call
  review of a 30-file PR was cancelled with nothing to show for it.
- **Generous timeouts.** `auto-reviewer` 40 min, `auto-developer` 30 min. A
  cancelled run produces nothing, so headroom is worth more than a shorter
  worst case.
- **Nothing merges unreviewed.** `auto-merge` re-reads the PR's live review
  state and requires a current `APPROVED` with no `CHANGES_REQUESTED`, so a
  failed or cancelled review can never be mistaken for an approval, and a red
  check leaves the PR open.
- **Failures speak.** A failed developer run comments on its issue; a review
  that never completed is reported on the PR by `auto-merge` (which is why it
  deliberately runs even when `Auto Reviewer` did not conclude `success`);
  a reviewer that produced no verdict file comments that too.
- **One thing that cannot be automated.** `PROMOTE_PAT` has no `workflows`
  permission, so an issue that requires editing `.github/workflows/` cannot be
  implemented by the agent. `auto-developer` makes that directory read-only and
  tells the agent to describe the change in the PR body instead. This is the
  intended human boundary, not a bug.

## Required repository configuration

Automation breaks silently if these drift. Check with:

```sh
gh api repos/OWNER/REPO/actions/permissions/workflow
gh secret list
```

- **Workflow permissions → "Allow GitHub Actions to create and approve pull
  requests"** must be **on** (`can_approve_pull_request_reviews: true`). With
  it off, `auto-reviewer` can only leave a `COMMENTED` review, GitHub blocks
  `auto-developer`'s PR creation, and the chain stalls after step one.
- **`PROMOTE_PAT`** — a personal access token for a repository admin. Classic
  `repo` scope, or a fine-grained token with Contents, Pull requests, and
  Issues (all read/write). Used because GitHub suppresses workflow runs for
  `push`/`pull_request` events raised by the built-in `GITHUB_TOKEN`; a PR it
  opened would never wake `auto-reviewer` or `Validate Bundle`. It is also the
  admin identity that `promote.yml` pushes `main` with, which is what gets
  past `main`'s lock-branch protection.
  It deliberately does **not** carry the `workflows` permission, so its push
  is refused for any file under `.github/workflows/`. That is a feature: the
  agent cannot rewrite the CI that grades it, and an issue that asks for a
  change there has to be done by hand.
- **`main` branch protection** — one approving review, lock branch. Promotions
  arrive as a direct admin push, so `enforce_admins` must stay **off**.
- **`dev`** is intentionally unprotected: PRs into it merge on a green
  review + checks, with no per-PR approval queue.

## Local checks

`validate.yml` runs these on every PR and on push to `dev`/`main`; run the
same three before pushing, since a red check leaves a PR open rather than
merging it:

```sh
python3 scripts/validate-refs.py
python3 scripts/build-lite.py --check
python3 scripts/validate-workflows.py
```

`actionlint` against `.github/workflows/*.yml` is worth running too if you
touched the workflows in this directory.

## Two-identity rule

A pull request cannot be approved by its own author, so creation and approval
must be different actors. This repo uses `PROMOTE_PAT` (a human admin) to open
PRs and the Actions `github-actions[bot]` (`GITHUB_TOKEN`) to approve them.
Do not collapse both onto one token, or every approval will fail as
self-approval.

The split has a second consequence worth knowing before you wire anything else
off a review: **an event raised by `GITHUB_TOKEN` does not trigger workflows.**
That is why nothing listens on `pull_request_review` here — the bot's approval
would not wake it. `auto-merge.yml` reacts to the *Auto Reviewer run
completing* (`workflow_run`) instead, which is a system event and survives the
guard. The same rule stops a `GITHUB_TOKEN`-opened PR from firing
`pull_request` at all, which is why PR creation uses `PROMOTE_PAT` too.

It also means the squash merge `auto-merge` performs raises no `push` run on
`dev`, so you will not see a `Validate Bundle` run for the merge commit itself —
only for the PR that produced it. That is fine because `promote.yml` re-runs
the validators on the merged tree before it touches `main`.
