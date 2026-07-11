---
name: tool-registry
category: process
load-when: Unsure which tool to use, complex tool selection, IDE migration
skip-when: Clear tool choice, simple operations
description: Tool usage patterns and decision guide. Maps needs to tool categories.
audience: [all]
tags: [tools, ide, file-operations, search, delegation]
---

# Tool registry

A structured catalog of tool patterns. Use this when you're unsure which tool to use for a task.

## Quick Reference

| Need | Pattern | Atlas tool names |
|------|---------|-----------------|
| Read file | read/glob | Read, Glob |
| Search code | grep | Grep |
| Write file | write/edit | Write, Edit |
| Run command | bash/shell | Bash |
| Delegate | spawn-subagent | Task, @agent |
| Web research | webfetch/websearch | WebFetch, WebSearch |

## Tool categories

### File operations
- **Read**: `Read` — read file contents. Use for small/medium files. For large files (>500 lines), use offset/limit.
- **Glob**: `Glob` — find files by pattern. Use `**/*.ts` for recursive matching.
- **Write**: `Write` — create or overwrite a file. Always read first if the file exists.
- **Edit**: `Edit` — targeted string replacement. Use `replaceAll` for renames across a file.

### Search
- **Grep**: `Grep` — content search using regex. Faster than reading entire files. Use `include` to filter by file type.

### Execution
- **Bash**: `Bash` — shell commands. Use `workdir` parameter instead of `cd`. Run independent commands in parallel.

### Delegation
- **Task**: `Task` — spawn a subagent for complex, multi-step tasks. Specify `subagent_type` (explore, general). Use `task_id` to resume.

### Web
- **WebFetch**: `WebFetch` — fetch and analyze web content. Use for documentation lookup.
- **WebSearch**: `WebSearch` — real-time web search. Use for current events, library docs.

## Atlas-specific patterns

### Batch parallel calls
When multiple independent operations are needed, run them in a single message:
```
Read(file1) + Read(file2) + Grep(pattern)  →  all in one call
```

### Read-before-edit
Always `Read` a file before `Edit`. The Edit tool requires the exact string to match. Reading first gives you the exact content.

### Workdir over cd
Use the `workdir` parameter instead of `cd <dir> && command`. Cleaner, more reliable.

### Grep over find+read
When searching for content, use `Grep` first to locate, then `Read` the specific section. Don't read entire files hoping to find something.

### Tool clearing
When switching phases or roles, release unused tool handles. Don't hold stale file locks or MCP connections across unrelated steps.
