# Security Policy

## Supported versions

Atlas is an AI IDE agent bundle (agents, skills, rules, knowledge). Security fixes apply to the latest release on the default branch. See [VERSION](VERSION) and [CHANGELOG](CHANGELOG.md) for the current version.

| Version | Supported |
| ------- | --------- |
| 0.5.x   | Yes       |
| < 0.5   | No        |

## Reporting a vulnerability

If you find a security issue in this repository, please report it privately. Do **not** open a public GitHub issue for vulnerabilities.

**Preferred:** [GitHub private vulnerability reporting](https://github.com/QuintusJoyal/atlas/security/advisories/new) (Security → Advisories → Report a vulnerability).

**Alternative:** Open a minimal public issue asking for a private contact channel only. Do not include exploit details, credentials, or customer data in the issue body.

We aim to acknowledge reports within 5 business days and will coordinate disclosure with you.

## Public issues and discussions

- Do **not** paste API keys, tokens, passwords, `.env` contents, or personal data into issues, PRs, or discussions.
- Redact hostnames, internal ticket IDs, and customer identifiers when describing a bug.
- Atlas run artifacts under `$ATLAS_DATA_DIR` may contain project-specific content. Treat them as local operator data, not something to attach to public reports.

## Secrets and environment variables

This bundle does **not** ship credentials. Operators supply secrets locally via their IDE's environment configuration.

## Operator hygiene

- Keep `.env`, `.env.*`, and `.atlas/` out of commits.
- If you fork Atlas, rotate any tokens that may have appeared in local chat or run artifacts before publishing your fork.

## Scope

This policy covers the **atlas** bundle repository. Your target application codebases are out of scope; report issues in those repos to their respective maintainers.
