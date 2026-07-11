---
name: codebase-context
category: process
load-when: Discovering relevant files, loading context for a task, debugging large codebases
skip-when: Simple tasks, small codebases
description: Codebase-aware context loading. Strategies for discovering and loading relevant files.
audience: [atlas-lead, atlas-dev, atlas-ai-eng]
tags: [codebase, context, discovery, search, embeddings, AST]
---

# Codebase-aware context

Atlas agents discover and load relevant files from the codebase using multiple strategies. The strategy depends on the IDE's capabilities and the task's complexity.

## Quick Reference
- 4 discovery strategies: manual, search-assisted, embedding-assisted, AST-aware
- 3 loading strategies: on-demand, batch, predictive
- Priority: recently changed > related > structural > all
- Budget: max 5,000 tokens of codebase context per task

## 4 discovery strategies

### 1. Manual (all IDEs)
Agent explicitly reads files it knows about.
```
Agent: "I need to modify src/app.py"
→ read_file("src/app.py")
→ Agent reads and understands the file
```

**When to use:** Small codebases (<50 files), agent knows exactly what to read.

### 2. Search-assisted (all IDEs)
Agent uses grep/glob to find relevant files.
```
Agent: "I need to find all files that import calculate()"
→ search_content("import.*calculate|from.*calculate")
→ Agent gets list of files, reads relevant ones
```

**When to use:** Medium codebases (50-500 files), agent knows what to search for.

### 3. Embedding-assisted (Cursor, Copilot)
IDE provides vector search for file discovery.
```
Agent: "I need to understand how tax calculation works"
→ IDE performs semantic search
→ Agent gets ranked list of relevant files
→ Agent reads top 5 files
```

**When to use:** Large codebases (>500 files), agent doesn't know where to look.

### 4. AST-aware (IDE-dependent)
IDE parses code structure for intelligent loading.
```
Agent: "I need to modify the calculate() function"
→ IDE finds function definition via AST
→ Agent gets function + all callers + all test files
→ Agent reads the complete context
```

**When to use:** Complex refactoring, need to understand call graphs.

## 3 loading strategies

### 1. On-demand
Read files as needed during execution.
```
Step 1: read_file("src/app.py") → understand structure
Step 2: read_file("src/utils.py") → find helper function
Step 3: edit_file("src/app.py") → make change
```

**Pros:** Minimal token usage. **Cons:** May miss context.

### 2. Batch
Read multiple files at once before making changes.
```
Step 1: search_files("**/*.py") → get all Python files
Step 2: read_file("src/app.py") + read_file("src/utils.py") + read_file("tests/test_app.py")
Step 3: Understand full context
Step 4: edit_file("src/app.py") → make change
```

**Pros:** Complete context. **Cons:** Higher token usage.

### 3. Predictive
IDE suggests files based on the task.
```
Agent: "Fix the bug in calculate()"
IDE: "Based on your task, you may need:
  - src/app.py (main function)
  - src/utils.py (helper)
  - tests/test_app.py (existing tests)
  - docs/api.md (API documentation)"
Agent: Reads suggested files
```

**Pros:** IDE-assisted discovery. **Cons:** IDE-dependent.

## Priority ranking

When multiple files are relevant, prioritize:

1. **Recently changed** (git log) — most likely to contain the bug or be affected
2. **Related by import** — directly connected to the target file
3. **Related by test** — test files for the target
4. **Structurally related** — same module, same package
5. **All other** — lower priority

## Context budget

Maximum codebase context per task:
- **Routine task:** 2,000 tokens (~5 files)
- **Complex task:** 5,000 tokens (~15 files)
- **Architecture task:** 10,000 tokens (~30 files)

If budget is exceeded:
1. Prioritize by the ranking above
2. Read only the most relevant sections (offset/limit)
3. Summarize what you read instead of reading everything

## Integration with Atlas workflows

### Feature workflow
- Requirements phase: read existing docs, API specs
- Design phase: read architecture files, ADRs
- Implementation phase: read target files, related modules
- Testing phase: read test files, coverage reports

### Bugfix workflow
- Triage phase: read error logs, recent changes
- Fix phase: read target file, related code
- Test phase: read existing tests, add new test

### Discovery workflow
- Research phase: read documentation, READMEs
- Feasibility phase: read architecture, dependencies

## Anti-patterns

- Reading the entire codebase (wasteful)
- Not reading enough context (misses important information)
- Re-reading files you've already read (track what you've seen)
- Ignoring test files (they show expected behavior)
- Not checking git log for recent changes
