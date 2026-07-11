---
name: aci-enforcement
category: process
load-when: Writing tool descriptions, designing tool interfaces, debugging tool failures, reviewing tool call patterns
skip-when: Using tools as-is, simple tool operations
description: ACI design rules for Atlas. Structured errors, semantic output, input validation, output compression. Based on SWE-agent, Anthropic, Composio, and OPENDEV research.
audience: [all]
tags: [aci, tool-design, error-handling, output-formatting, poka-yoke, tool-enforcement]
---

# ACI enforcement

Atlas tools follow Agent-Computer Interface (ACI) design principles. These rules govern how tools behave, not how agents use them. They apply to any custom tools, MCP servers, or tool wrappers built for Atlas.

## Quick Reference
- Structured errors: every tool error includes category, recoverability, and suggested action
- Semantic output: return human-readable identifiers, not UUIDs or raw database fields
- Output compression: per-type summarization for large tool outputs
- Input validation: poka-yoke constraints that prevent entire error classes
- Tool descriptions: written as onboarding docs, not API references

## 1. Structured Error Protocol

Every tool that can fail MUST return errors in this format:

```json
{
  "error": true,
  "errorCategory": "transient|validation|business|permission|not_found",
  "recoverable": true,
  "message": "Specific description of what went wrong",
  "suggestedAction": "Concrete next step the agent should take",
  "context": {"file": "src/api.ts", "line": 42}
}
```

### Error categories

| Category | `recoverable` | Example | Agent behavior |
|----------|---------------|---------|----------------|
| `transient` | true | Rate limit, network timeout | Retry with backoff |
| `validation` | true | Invalid path, missing required field | Fix parameters and retry |
| `business` | false | Permission denied, quota exceeded | Escalate to user (T2/T3) |
| `not_found` | varies | File not found, resource missing | Try alternative path or escalate |
| `permission` | false | Access denied, auth expired | Escalate with context |

### Recovery rates (from production data)
- Transient errors: 92% auto-recovered with structured retry guidance
- Validation errors: 78% auto-corrected with field-level hints
- Business errors: 95% correctly escalated with category + customer message
- Generic errors ("Operation failed"): 15% recovery

### Anti-patterns (forbidden)
- **Silent swallow:** returning success when the tool failed
- **Generic message:** "Operation failed" with no category or suggested action
- **Error-as-data:** returning error text without the `error: true` flag
- **Exception propagation:** letting tool exceptions crash the agent loop instead of returning structured errors

## 2. Semantic Output Rules

### Return human-readable identifiers
- Return `name`, `file_type`, `author` instead of `uuid`, `mime_type`, `user_id`
- When technical IDs are needed for downstream tool calls, include them as secondary fields
- Use 0-indexed numbering for lists: "item 1" not "item a3f4b2c1"
- UUIDs cost ~23 tokens; word-based IDs cost ~14 tokens with equivalent collision resistance
- Agents hallucinate UUIDs more frequently than semantic names

### Return only decision-relevant fields
- Default response: only fields the agent needs for its next step
- Expose `response_format` parameter when full records are sometimes needed:
  - `"concise"` (default): name, status, key fields only
  - `"detailed"`: full record with all fields including technical IDs

### Output compression thresholds
- File reads > 200 lines: return summary ("Read file, 142 lines, 4,831 chars") + offer re-read by range
- Search results > 10 matches: return file list with match counts, not matched lines
- Bash output > 500 lines: truncate to last 200 lines + exit code + summary
- Any empty output: explicit "Operation succeeded, no output produced"

## 3. Input Validation (Poka-Yoke)

### Constraint design principle
One constraint change can eliminate an entire failure class. Prefer constraints over prompts. When an agent makes the same tool error twice, fix the tool interface rather than adding more instructions.

### Atlas-specific poka-yoke rules
- **Absolute paths required** for file operations. No relative paths. Eliminates an entire class of "file not found" errors.
- **Line ranges required** for reads of files > 200 lines. Agent must specify offset/limit or accept default window.
- **Read-before-edit enforced.** Edit tool requires exact string match. Agent must Read first to get exact content. (Extends lite-mode rule to full mode.)
- **Tool clearing on phase switch.** Before starting a new phase, confirm only relevant tools are active. No stale file locks or MCP connections across unrelated delegations.

## 4. Tool Description Standards

### Written as onboarding docs
Tool descriptions should be written for a new hire who will never ask a clarifying question:
- What the tool does (one sentence)
- When to use it (specific trigger conditions)
- When NOT to use it (contrasting alternatives)
- What the output looks like (sample structure)
- Common failure modes and recovery

### Parameter naming
- Use unambiguous names: `file_path` not `path`, `search_pattern` not `query`
- Include format constraints in the description: "Must be an absolute path starting with /"
- Include short examples directly in parameter descriptions

### Anti-patterns
- Descriptions that merely say what the tool wraps: "Calls the GitHub API"
- Parameter names that assume domain knowledge: `repo`, `ref`, `sha`
- Missing error documentation: not telling the agent what happens when the tool fails

## 5. Cross-Agent Tool Provenance

When handing off work between Atlas roles, the handoff MUST include tool provenance:

```markdown
## Tool Provenance
- **Files read:** src/api.ts (lines 1-100), src/db.ts (full)
- **Files edited:** src/api.ts (line 42, fixed N+1 query)
- **Commands run:** npm test (passed, 47/47)
- **Tool errors encountered:** Edit failed on src/types.ts (validation: string mismatch at line 15, recovered by re-reading)
- **Pending tool actions:** Need to run integration tests
```

This prevents the receiving role from re-doing work or making decisions based on stale assumptions about file state.

## 6. Telemetry-Driven Tool Optimization

Atlas trajectory logs (`trajectory.jsonl`) contain tool call sequences. Periodically analyze:

1. **Transition frequency:** Which tool pairs fire together most often? (Read->Edit, Grep->Read, Bash->Grep)
2. **Error patterns:** Which tools fail most, and with what error categories?
3. **Token cost per tool:** Which tools consume the most context per call?
4. **Role-specific patterns:** Which roles use which tools most? Are there role-tool mismatches?

Use these insights to:
- Update tool descriptions based on actual failure modes
- Consolidate frequently-paired tools where appropriate (Tool Transition Fusion)
- Adjust output compression thresholds based on actual context consumption
- Identify tools that should be role-scoped vs. shared

### Tool Transition Fusion
When two tools fire together >80% of the time (e.g., Read->Edit), consider fusing them into a composite tool. Mine trajectory data for transition probabilities. Fuse above threshold; keep separate below.
