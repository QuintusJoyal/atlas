# Public release checklist

Use this checklist before making the Atlas repository public on GitHub. Scan date: 2026-07-10.

## Safe to publish

The tracked bundle is documentation and Cursor configuration, not a deployed service. No live credentials were found in the working tree.

| Area | Contents | Notes |
| ---- | -------- | ----- |
| **Agents** | `agents/atlas-*.md` (24 roles + lead) | Frontmatter, delegation examples, MCP guidance |
| **Skills** | `skills/atlas-*-playbook/SKILL.md` | Role methodologies; cite public standards (OWASP, ISTQB, etc.) |
| **Rules** | `rules/*.mdc` | Always-on and on-demand Cursor rules |
| **Knowledge** | `knowledge/*.md` | Framework docs, lessons, templates; operator-editable after install |
| **Workflows** | `workflows/*.md` | Preset pipeline definitions |
| **Install** | `install.ps1`, `install.sh`, `manifest.json` | Copies bundle into `~/.cursor/` |
| **Validate** | `validate.ps1`, `validate.sh` | Frontmatter, model IDs, playbook refs, writing-style lint |
| **Scripts** | `scripts/merge-knowledge.ps1`, `scripts/migrate-to-atlas-data.*` | KB merge and data-dir migration helpers |
| **Docs** | `README.md`, `ROLES.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `LICENSE` | Public-facing project docs |
| **Archive** | `docs/archive/CONTROL-CENTER-PLAN.md` | Historical product plan (see flagged items) |

**Not in this bundle:** Cursor SDK orchestrator and runner (`sdk/`) live in sibling repo [`atlas-control-center`](https://github.com/QuintusJoyal/atlas-control-center). See that repo's `sdk/README.md` and release checklist there.

**Env var names only (not values):** `CURSOR_API_KEY`, `ATLAS_CC_URL`, `ATLAS_CC_TOKEN`, `ATLAS_DATA_DIR`, `ATLAS_HOME` appear in docs and Control Center SDK code as expected configuration surface.

**Placeholder paths only:** Examples use `C:/Users/you`, `~/.cursor/`, `$ATLAS_DATA_DIR`. No `qujolk` or machine-specific paths in tracked text.

**`.gitignore` covers:** `.env`, `.env.*`, `.atlas/`, `**/node_modules/`, `.cursor/`, `docker-compose.override.yml`, logs, OS noise.

---

## Flagged / review before publish

Decisions for the repository owner before `git push` and flipping visibility to public.

| Item | Location | Risk | Recommendation |
| ---- | -------- | ---- | -------------- |
| **Control Center archive** | `docs/archive/CONTROL-CENTER-PLAN.md` | Internal run IDs (`2026-06-14-control-center-sdk`), product history, GitHub org link | **Keep** as archived context (already prefixed with historical notice) **or** trim run-specific IDs. Do not delete without deciding whether public users need CC history. |
| **Proposed lessons (run detail)** | `knowledge/proposed.md` | Multiple lines reference internal run `2026-06-14-control-center-sdk` and CC integration debugging | Safe for a transparent OSS project; **trim or redact run IDs** if you prefer a cleaner public KB. |
| **GitHub username / org** | `README.md`, archive plan | Links to `QuintusJoyal/atlas-control-center` | Intentional if that is your public org; change links if publishing under a different account. |
| **Untracked release files** | `git status` shows many `??` paths (`docs/`, new `knowledge/*`, `rules/atlas-lead-orchestration.mdc`) | Incomplete release if only partial commit | Stage and review all files intended for the public drop. |
| **Deleted tracked files** | `knowledge/control-center-brief.md`, `scripts/patch-playbooks.ps1`, former `sdk/` tree | Changelog drift if deletion not documented | Confirm deletions are intentional; update `CHANGELOG.md` (SDK now in `atlas-control-center`). |
| **Sibling repos** | `atlas-control-center` (includes `sdk/`) | Separate visibility and secrets surface | Publish order: decide whether CC repo is public first; this bundle links to it for operator UI and SDK. |
| **Git history** | `.git/` | Prior private commits may predate sanitization | Run secret scan on **full history** before first public push (commands below). Consider `git filter-repo` only if history contained real credentials. |

---

## Must not commit

Never add these to the repository or to `knowledge/` / run artifacts:

| Category | Examples | Mitigation |
| -------- | -------- | ---------- |
| **Environment files** | `.env`, `.env.local`, `.env.production` | Listed in `.gitignore`; use `.env.example` in sibling CC repo only |
| **API keys and tokens** | `CURSOR_API_KEY`, `ATLAS_CC_TOKEN`, `ghp_*`, `glpat-*`, `sk-*`, `AKIA*` | Host env or secret manager only |
| **Override compose** | `docker-compose.override.yml` | Often contains host bind paths; gitignored |
| **Operator run data** | `.atlas/`, `$ATLAS_DATA_DIR/runs/`, `team.json`, `budget.md`, gate sidecars | Local pipeline state; never in project repos |
| **IDE-local config** | `.cursor/` (project-specific) | Gitignored |
| **Dependencies** | `node_modules/` | Gitignored; rebuild from lockfile in each repo |
| **PII** | Real names, emails, customer IDs in lessons or proposed items | Redact before commit |
| **Internal ticket IDs** | `PLAT-*`, `JIRA-*`, customer ticket prefixes | Use generic "user feedback" in KB (see fixes below) |

---

## Pre-push commands

Run from the repository root. Fix any hits before publishing.

### 1. Bundle validation (required)

```powershell
# Windows
./validate.ps1
```

```bash
# macOS / Linux
./validate.sh
```

### 2. Secret and PII grep (working tree)

Exclude dependencies and git metadata.

**PowerShell:**

```powershell
$exclude = @('node_modules','.git')
$files = Get-ChildItem -Recurse -File | Where-Object {
  $p = $_.FullName
  -not ($exclude | Where-Object { $p -like "*$_*" })
}
$patterns = @(
  'PLAT-\d+',
  'qujolk',
  'ghp_[a-zA-Z0-9]+',
  'glpat-[a-zA-Z0-9]+',
  'sk-[a-zA-Z0-9]{20,}',
  'AKIA[0-9A-Z]{16}',
  'BEGIN (RSA |OPENSSH )?PRIVATE KEY',
  '@[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
)
foreach ($pat in $patterns) {
  $hits = $files | Select-String -Pattern $pat -List
  if ($hits) { Write-Host "MATCH $pat"; $hits | ForEach-Object { $_.Path } }
}
```

**Bash (ripgrep):**

```bash
rg -n 'PLAT-[0-9]+|qujolk|ghp_[a-zA-Z0-9]+|glpat-[a-zA-Z0-9]+|sk-[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN (RSA |OPENSSH )?PRIVATE KEY' \
  --glob '!**/node_modules/**' --glob '!**/.git/**'
```

### 3. Sensitive paths and env files

```powershell
git status --short
git ls-files | Select-String -Pattern '\.env$|node_modules|\.atlas'
```

```bash
git status --short
git ls-files | rg '\.env$|node_modules|\.atlas'
```

Expect **no** `.env` or `node_modules` in `git ls-files` output.

### 4. Optional: scan git history (first public push)

```bash
git log -p --all -S 'CURSOR_API_KEY=' -- '*.env' '*.md' '*.ts'
git log -p --all -S 'ghp_' -S 'glpat-' -S 'AKIA'
```

If anything real appears, rotate the credential and rewrite history before going public.

### 5. Final smoke check

```powershell
./install.ps1 -Mode update   # or ./install.sh update; dry-run on a test machine
./validate.ps1
```

---

## Scan summary (2026-07-10)

| Check | Result |
| ----- | ------ |
| Hardcoded API keys (`ghp_`, `glpat-`, `sk-`, `AKIA`) | **None** |
| Email addresses | **None** |
| Username path `qujolk` | **None** |
| `PLAT-*` ticket IDs | **Fixed** in `knowledge/proposed.md` (was `PLAT-33724`) |
| Internal example `PSO` | **Fixed** in `agents/atlas-lead.md`, `rules/atlas-lead-orchestration.mdc` |
| `.env` files in tree | **None** |
| `node_modules` tracked | **No** (gitignored) |

---

## Fixes applied in this pass

1. `knowledge/proposed.md`: `PLAT-33724` → generic user feedback wording.
2. `agents/atlas-lead.md`, `rules/atlas-lead-orchestration.mdc`: `PSO` example → `example shell scripts`.

---

## Related

- [SECURITY.md](../SECURITY.md) - vulnerability reporting and env var policy
- [CONTRIBUTING.md](../CONTRIBUTING.md) - no secrets in KB
- [README.md](../README.md) - what ships vs optional Control Center
