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
feature-reviewer.yml ──evaluates + labels `action:develop`──▶ auto-developer.yml
   (posts evaluation)                                            (implements, retargets PR to dev)
                                                                        │
                                                                        ▼
                                              auto-reviewer.yml ──approves──▶ auto-merge.yml
                                                 (review)                       (squash-merges into dev
                                                                                 + closes the issue)
                                                                                        │
                                    Validate Bundle must pass ──────────────────────────┘
                                                                                        │
                                                                                        ▼
                                                                     promote.yml (weekly, dev → main)
```

| Workflow | Trigger | Does |
| --- | --- | --- |
| `validate.yml` | PR, push to `dev`/`main` | Runs `scripts/validate-refs.py`, `build-lite.py --check`, `validate-workflows.py`. |
| `auto-developer.yml` | issue labeled `action:develop` | Runs opencode, which commits a branch and opens a PR, then retargets that PR from `main` to `dev` and sets its title from the issue, so the PR listing is deterministic rather than whatever the model happened to say. Makes `.github/workflows/` read-only first (the token cannot push there) and reports a failed run on the issue. |
| `auto-reviewer.yml` | PR `opened`/`reopened` | Runs opencode to pick a verdict, then submits the `gh pr review` itself. The agent only writes its verdict to `.atlas/review-verdict.txt` (gitignored) and a workflow step always submits it, so neither a model that narrates a command instead of running it nor a sandbox that blocks writes outside the workspace can silently skip the review. It works from the diff under a hard tool-call budget, because an exhaustive review is what runs out of time. Close/reopen a PR to re-queue a review. |
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
