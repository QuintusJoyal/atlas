# Security Policy

## Supported versions

Atlas is a Cursor subagent bundle (agents, skills, rules, knowledge). Security fixes apply to the latest release on the default branch. See [VERSION](VERSION) and [CHANGELOG](CHANGELOG.md) for the current version.

| Version | Supported |
| ------- | --------- |
| 0.3.x   | Yes       |
| < 0.3   | No        |

## Reporting a vulnerability

If you find a security issue in this repository, please report it privately. Do **not** open a public GitHub issue for vulnerabilities.

**Preferred:** [GitHub private vulnerability reporting](https://github.com/QuintusJoyal/atlas/security/advisories/new) (Security → Advisories → Report a vulnerability).

**Alternative:** Open a minimal public issue asking for a private contact channel only. Do not include exploit details, credentials, or customer data in the issue body.

We aim to acknowledge reports within 5 business days and will coordinate disclosure with you.

## Public issues and discussions

- Do **not** paste API keys, tokens, passwords, `.env` contents, or personal data into issues, PRs, or discussions.
- Redact hostnames, internal ticket IDs, and customer identifiers when describing a bug.
- Atlas run artifacts under `$ATLAS_DATA_DIR` (default `~/.cursor/atlas-data/`) may contain project-specific content. Treat them as local operator data, not something to attach to public reports.

## Secrets and environment variables

This bundle does **not** ship credentials. Operators supply secrets locally:

| Variable | Where set | Purpose |
| -------- | --------- | ------- |
| `CURSOR_API_KEY` | Host environment or SDK runner only | Cursor SDK agent execution |
| `ATLAS_CC_URL` | Host or runner environment | Optional Control Center ingest base URL |
| `ATLAS_CC_TOKEN` | Host or runner environment | Optional Control Center write auth |

Control Center (sibling repo [`atlas-control-center`](https://github.com/QuintusJoyal/atlas-control-center)) uses its own `.env` for Docker deploy. None of these values belong in git, `knowledge/`, or run folders under `$ATLAS_DATA_DIR`.

Install and validate scripts never write secrets to disk. The SDK redacts common secret patterns before posting ingest events (`sdk/ingest-client.ts`).

## Operator hygiene

- Keep `.env`, `.env.*`, `docker-compose.override.yml`, and `.atlas/` out of commits (see [.gitignore](.gitignore)).
- Before your first public push, run the pre-push checks in [docs/PUBLIC_RELEASE_CHECKLIST.md](docs/PUBLIC_RELEASE_CHECKLIST.md).
- If you fork Atlas, rotate any tokens that may have appeared in local chat or run artifacts before publishing your fork.

## Scope

This policy covers the **atlas** bundle repository. The optional Control Center UI and your target application codebases are out of scope here; report issues in those repos to their respective maintainers.
