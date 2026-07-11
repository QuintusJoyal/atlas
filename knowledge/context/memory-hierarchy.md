---
name: memory-hierarchy
category: process
load-when: Resolving conflicting guidance, deciding which source to trust, onboarding to a new project
skip-when: Clear single-source guidance
description: Three-tier memory hierarchy. Personal > Project > Shared. Conflict resolution rules.
audience: [all]
tags: [memory, hierarchy, lessons, knowledge, priority]
---

# Memory hierarchy

Atlas has three tiers of memory. When sources conflict, higher tiers win.

## Quick Reference
- **L1 Personal:** `lessons.md` per-role entries. Highest priority. This agent, this project.
- **L2 Project:** project-specific knowledge. Medium priority. All roles, this project.
- **L3 Shared:** universal patterns. Lowest priority. Any project.

## Tiers

### L1: Personal (highest priority)
**Source:** `knowledge/reference/lessons.md` (per-role entries)
**Scope:** This agent, this project
**Examples:**
- "atlas-dev: avoid nested Promise.all in Express middleware — causes memory spikes"
- "atlas-qa: always test with empty database, not mock, for migration validation"
**When to read:** Bootstrap (before every task)
**When to write:** After a failed attempt that succeeded with a different approach

### L2: Project (medium priority)
**Source:** `knowledge/` project-specific files
**Scope:** All roles, this project
**Examples:**
- "Our API uses REST, not GraphQL"
- "We deploy to AWS ECS, not Kubernetes"
- "Database is PostgreSQL 15, no MySQL"
**When to read:** When onboarding to a new area of the codebase
**When to write:** When discovering project-specific patterns

### L3: Shared (lowest priority)
**Source:** `knowledge/` universal pattern files
**Scope:** Any project
**Examples:**
- "OWASP Top 10: injection is #1"
- "SOLID principles: dependency inversion"
- "TDD: red-green-refactor"
**When to read:** When applying universal best practices
**When to write:** When adding new domain knowledge

## Conflict resolution

When sources conflict:

1. **L1 > L2 > L3.** Personal lessons override project knowledge, which overrides shared knowledge.
2. **Project context > universal rules.** "We don't use TDD for hotfixes" overrides "always use TDD."
3. **Explicit > implicit.** A documented decision (ADR) overrides a pattern from shared knowledge.

## Writing lessons

Lessons must be:
- **Specific:** "avoid X in Y context" not "be careful"
- **Actionable:** "use Z approach instead" not "X is tricky"
- **Attributed:** include role name so the right agent reads it

Format in `lessons.md`:
```markdown
## atlas-dev
- **avoid:** nested Promise.all in Express middleware — causes memory spikes under load
- **prefer:** sequential awaits with early termination for independent calls
```

## Cross-project leakage prevention

Personal lessons (L1) are project-scoped by default. They live in the project's `knowledge/reference/lessons.md`, not a global file. When working on a new project, start with L3 shared knowledge; L1 lessons accumulate as you work.
