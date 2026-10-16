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
| `auto-developer.yml` | issue labeled `action:develop` | Runs opencode, which commits a branch and opens a PR, then retargets that PR from `main` to `dev`. |
| `auto-reviewer.yml` | PR `opened` | Runs opencode to submit a real `gh pr review` (approve / request-changes / comment). |
| `auto-merge.yml` | PR review `submitted` | On an approval of a same-repo PR into `dev`: waits for checks, then `gh pr merge --squash --delete-branch`. |
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
- **`main` branch protection** — one approving review, lock branch. Promotions
  arrive as a direct admin push, so `enforce_admins` must stay **off**.
- **`dev`** is intentionally unprotected: PRs into it merge on a green
  review + checks, with no per-PR approval queue.

## Two-identity rule

A pull request cannot be approved by its own author, so creation and approval
must be different actors. This repo uses `PROMOTE_PAT` (a human admin) to open
PRs and the Actions `github-actions[bot]` (`GITHUB_TOKEN`) to approve them.
Do not collapse both onto one token, or every approval will fail as
self-approval.
