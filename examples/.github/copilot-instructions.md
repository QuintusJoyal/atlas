# GitHub Copilot Custom Instructions for Atlas

## Atlas Framework

This project uses Atlas, a multi-agent team framework for software delivery.

### When Writing Code

1. Follow `atlas/rules/atlas-core.md` non-negotiables
2. Read files before editing (observe-before-act)
3. Return structured errors, not bare strings
4. Keep responses under 4,000 tokens

### When Reviewing Code

1. Check against `atlas/knowledge/testing/anti-patterns.md`
2. Verify test coverage for new logic
3. Look for oracle leakage (tests that pass but verify wrong behavior)

### When Debugging

1. Classify the problem domain first (clear/complicated/complex/chaotic)
2. Read relevant files before hypothesizing
3. Escalate with structure: what was tried, what failed, what's needed

### Key Knowledge Files

- `atlas/knowledge/reference/lessons.md` - Approved lessons
- `atlas/knowledge/context/escalation-tiers.md` - When and how to escalate
- `atlas/knowledge/context/pre-handoff-quality-check.md` - Quality checklist
- `atlas/knowledge/craftsmanship/solid-principles.md` - Design principles
