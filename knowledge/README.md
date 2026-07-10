# Atlas knowledge base

The shared memory of the Atlas team. It ships with the bundle and installs to `~/.cursor/atlas-knowledge/`. Anyone (human or role) can open and read it directly.

## Shipped vs installed

| Location | Purpose |
| --- | --- |
| Repo `knowledge/` | Source files in version control. Install copies them to `~/.cursor/atlas-knowledge/`. |
| `~/.cursor/atlas-knowledge/` | Live KB on your machine. Roles read and write here during work. |

On **update**, install preserves your local edits to `lessons.md`, `proposed.md`, `ways-of-working.md`, and `usage-insights.md`. New bundle files can be merged with `./scripts/merge-knowledge.ps1`.

Canonical Framework docs (`core-values-charter.md`, `enterprise-org-model.md`, `atlas-framework.md`, `retro-template.md`, and others) ship in both places after install.

## Files

- `lessons.md`: canonical, approved lessons. Every role reads this before acting.
- `proposed.md`: a queue of new lessons drafted by roles. The user approves in batches; approved items move to `lessons.md`. **The repo copy includes example entries** that show the format. They are not private data; replace or clear them after install if you prefer a clean queue.
- `ways-of-working.md`: approved process and idea changes, plus a proposed section.
- `usage-insights.md`: atlas-ai-eng logs usage patterns and efficiency recommendations here.
- `branding-values.md`: Atlas name, tagline, core values, visual identity, and voice.

## How it works

1. Before acting, a role reads `lessons.md` (topic-indexed; read only the relevant part).
2. After work, a role appends any new, non-obvious lesson to `proposed.md` with a one-line rationale and source.
3. The user reviews `proposed.md` and `ways-of-working.md` in batches and promotes approved items.

## Hygiene

- Never store secrets, credentials, or PII here.
- Keep `lessons.md` lean and topic-indexed. Curate and merge as it grows.
- atlas-ai-eng periodically proposes pruning stale or superseded lessons.
