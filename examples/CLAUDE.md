# CLAUDE.md - Atlas Configuration for Claude Code

## Atlas Framework

This project uses Atlas, a multi-agent team framework for software delivery.

### Core Rules

Always load `atlas/rules/atlas-core.md` at session start. It contains:
- Non-negotiable rules for all agents
- Bootstrap steps (grep lessons.md, model-resilience.md)
- Knowledge loading strategy (three-tier: inline → grep → load)

### Key Files

| File | Purpose |
|------|---------|
| `atlas/rules/atlas-core.md` | Core rules (always loaded) |
| `atlas/rules/atlas-lead-orchestration.md` | Delegation rules |
| `atlas/rules/handoff-protocol.md` | Artifact format |
| `atlas/knowledge/reference/lessons.md` | Approved lessons |
| `atlas/knowledge/reference/model-resilience.md` | Model tier cascade |

### Agents

Atlas has 24 specialist roles. Key ones:
- `atlas-lead` - Orchestrator (routes, never implements)
- `atlas-dev` - Implementation
- `atlas-qa` - Testing
- `atlas-architect` - Design
- `atlas-security` - Security review

### Workflows

- `feature.md` - Net-new work (requirements → design → implement → test → review → deploy)
- `bugfix.md` - Defects (triage → fix → test → review → deploy)
- `discovery.md` - Research and exploration

### Model Tiers

- Premium: deep reasoning, gate roles
- Standard: orchestrator, everyday work
- Fast: implementation-heavy roles
