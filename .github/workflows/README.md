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
issue + `action:develop` label
        │
        ▼
auto-developer.yml ──opens PR──▶ auto-reviewer.yml ──approves──▶ auto-merge.yml
   (implements, retargets PR to dev)   (review)                      (squash-merges into dev)
        │                                                                    │
        └──────────────── Validate Bundle must pass ─────────────────────────┘
                                                                             │
                                                                             ▼
                                                              promote.yml (weekly, dev → main)
```

| Workflow | Trigger | Does |
| --- | --- | --- |
| `validate.yml` | PR, push to `dev`/`main` | Runs `scripts/validate-refs.py`, `build-lite.py --check`, `validate-workflows.py`. |
| `auto-developer.yml` | issue labeled `action:develop` | Runs opencode, which commits a branch and opens a PR, then retargets that PR from `main` to `dev` and sets its title from the issue, so the squash-commit subject on `dev`/`main` is deterministic rather than whatever the model happened to say. |
| `auto-reviewer.yml` | PR `opened` | Runs opencode to pick a verdict, then submits the `gh pr review` itself. The agent only writes its verdict to `.atlas/review-verdict.txt` (gitignored) and a workflow step always submits it, so neither a model that narrates a command instead of running it nor a sandbox that blocks writes outside the workspace can silently skip the review. |
| `auto-merge.yml` | `Auto Reviewer` run completes (plus manual `workflow_dispatch`) | When a same-repo PR into `dev` has a current approval: waits for checks, then `gh pr merge --squash --delete-branch`, and closes the issue the PR names (`Closes #N`, or `issue<N>` in the branch). Triggered by `workflow_run`, not `pull_request_review`, because the bot's own approval is made with `GITHUB_TOKEN` and so raises no workflow run — and `workflow_run` also guarantees main's copy of the file runs. |
| `promote.yml` | weekly schedule, `/promote` comment, manual dispatch | Re-runs the bundle validators on the merged tree, then merges `dev` into `main` and pushes. The only path into `main`. |
| `promote-dispatch.yml` | `/promote` comment | Validates the command and dispatches `promote.yml`. |
| `feature-reviewer.yml` | issue `opened`/labeled | Posts a feasibility evaluation comment. |
| `trend-investigator.yml` | weekly schedule | Opens `type:feature` issues from research. |

The human entry points are deliberately few: label an issue `action:develop`
to start work, comment `/promote` to ship early, and step in only if a run
fails (a failed check leaves the PR open rather than merging it).

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
