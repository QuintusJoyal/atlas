---
name: runtime-execution
category: process
load-when: Designing execution flows, integrating with new IDEs, debugging tool failures
skip-when: Normal operation
description: Runtime execution protocol for Atlas. Defines how agents make tool calls across IDEs.
audience: [atlas-lead, atlas-ai-eng]
tags: [runtime, execution, tools, protocol, IDE-integration]
---

# Runtime execution protocol

Atlas agents make tool calls through their host IDE. This protocol defines the standard interface that all IDEs must implement.

## Quick Reference
- 3 execution modes: prompt-only, tool-assisted, programmatic
- Tools: whatever the host IDE provides natively (Read, Write, Edit, Bash, Glob, Grep or equivalents) — see `knowledge/process/tool-registry.md` for the need-to-tool mapping
- Error recovery: retry, escalate, checkpoint
- Context passing: structured artifacts between roles
- IDE implements the mechanism, Atlas defines the protocol

## 3 execution modes

### 1. Prompt-only (current)
Agent reasoning + tool calls via IDE's native interface.
- Agent decides what to do
- Agent calls tools through IDE
- IDE executes and returns results
- Agent processes results

**When to use:** Default mode. Works on all IDEs.

### 2. Tool-assisted
Agent uses tools but waits for IDE to execute.
- Agent generates tool call specification
- IDE validates and executes
- Results returned to agent
- Agent continues reasoning

**When to use:** When IDE supports structured tool calls.

### 3. Programmatic
Agent defines execution plan, IDE runs it.
- Agent generates a sequence of tool calls
- IDE executes the sequence
- Intermediate results are available
- Agent can inspect and adjust

**When to use:** When IDE supports batch execution.

## Error recovery

### Tool failure handling
```
Tool call fails
  → Check error category (from aci-enforcement.md)
  → If recoverable: retry with backoff (1s, 2s, 4s)
  → If timeout: escalate to user
  → If resource: checkpoint and pause
  → Log failure in trajectory.jsonl
```

### Checkpoint on failure
When a tool fails mid-execution:
1. Save current state (checkpoint-protocol.md)
2. Record what succeeded and what failed
3. Enable resume from last successful step

## Context passing between roles

### Structured artifacts
Roles communicate through structured artifacts, not raw context:

```json
{
  "artifact_type": "implementation_summary",
  "from_role": "atlas-dev",
  "to_role": "atlas-qa",
  "files_changed": ["src/app.py", "tests/test_app.py"],
  "approach": "Refactored calculate() to handle edge cases",
  "test_results": {"passed": 12, "failed": 0},
  "decisions": ["Used strategy pattern for tax calculation"],
  "next_action": "Run integration tests"
}
```

### Tool provenance
Every handoff includes what tools were called, in plain prose or a short list (see `rules/handoff-protocol.md`):

```markdown
- Read: src/app.py
- Edit: src/app.py (refactor calculate())
- Bash: pytest tests/test_app.py (12 passed)
Files touched: src/app.py, tests/test_app.py. Errors: none.
```

## Anti-patterns

- Assuming a tool exists without checking IDE capabilities
- Not handling tool failures (assume success)
- Passing raw context instead of structured artifacts
- Not recording tool provenance in handoffs
- Retrying indefinitely without backoff
