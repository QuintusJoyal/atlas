---
name: tool-registry
category: process
load-when: Unsure which tool to use, complex tool selection, designing new tools, debugging tool failures
skip-when: Clear tool choice, simple operations
description: Tool usage patterns, decision guide, and ACI standards. Maps needs to tool categories with enforced behavior rules.
audience: [all]
tags: [tools, ide, file-operations, search, delegation, aci]
---

# Tool registry

A structured catalog of tool patterns and ACI standards. Use this when you're unsure which tool to use, or when designing or debugging tools.

## Quick Reference

| Need | Pattern | Atlas tool names | ACI notes |
|------|---------|-----------------|-----------|
| Read file | read/glob | Read, Glob | Windowed: 200-line default, offset/limit for larger |
| Search code | grep | Grep | Return file list with counts, not matched lines |
| Write file | write/edit | Write, Edit | **Must Read first.** Edit requires exact string match. |
| Run command | bash/shell | Bash | Use `workdir` param. Truncate output > 500 lines. |
| Delegate | spawn-subagent | Task, @agent | Include tool provenance in handoff brief. |
| Web research | webfetch/websearch | WebFetch, WebSearch | Cache results. Don't re-fetch same URL. |

## Tool categories

### File operations
- **Read**: read file contents. Default: 200 lines. For large files (>200 lines), use offset/limit. On error, return structured error with file path and line count.
- **Glob**: find files by pattern. Use `**/*.ts` for recursive matching. Returns file list only.
- **Write**: create or overwrite a file. **ALWAYS Read first if file exists.** On permission error, return `errorCategory: "permission"`, `recoverable: false`.
- **Edit**: targeted string replacement. **ALWAYS Read first.** Returns linter/validator feedback on syntax errors. On mismatch, return the closest matching region.

### Search
- **Grep**: content search using regex. Return file list with match counts. For > 10 matches, paginate. Never return full matched lines in default mode.

### Execution
- **Bash**: shell commands. Use `workdir` parameter. Truncate stdout to last 200 lines + exit code. On non-zero exit, return exit code + stderr excerpt + suggested fix.

### Delegation
- **Task**: spawn subagent. Brief MUST include tool provenance from prior steps. See handoff protocol.

### Web
- **WebFetch**: fetch and analyze web content. Returns summarized content, not raw HTML.
- **WebSearch**: real-time web search. Returns structured results with URLs and snippets.

## ACI behavior rules

Error format, output compression thresholds, and semantic-output rules are defined once in `knowledge/process/aci-enforcement.md` — this file only maps needs to tool names; it doesn't restate those rules.

## Atlas-specific patterns

### Batch parallel calls
When multiple independent operations are needed, run them in a single message:
```
Read(file1) + Read(file2) + Grep(pattern)  ->  all in one call
```

### Read-before-edit (enforced)
Always `Read` a file before `Edit`. The Edit tool requires the exact string to match. Reading first gives you the exact content. This is a poka-yoke constraint, not a suggestion.

### Workdir over cd
Use the `workdir` parameter instead of `cd <dir> && command`. Cleaner, more reliable.

### Grep over find+read
When searching for content, use `Grep` first to locate, then `Read` the specific section. Don't read entire files hoping to find something.

### Tool clearing
When switching phases or roles, release unused tool handles. Don't hold stale file locks or MCP connections across unrelated steps.

### Tool provenance on handoff
When delegating to another role or handing off work, include:
1. What tools were called (tool name + key args)
2. What files were read, written, or edited
3. What errors occurred and how they were resolved
4. What tool actions are pending

### Poka-yoke principle
When you make the same tool error twice, the fix is a constraint, not a reminder. Add an input validation rule, improve the error message, or change the tool's default behavior. One constraint change eliminates the entire error class.
