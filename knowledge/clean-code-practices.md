---
name: clean-code-practices
load-when: Writing or reviewing code, improving readability, code quality assessments
skip-when: Specific principles (see solid-practices), refactoring (see refactoring-patterns)
---

# Clean Code Practices

## Quick Reference
- Meaningful names: reveal intent, avoid encodings, use pronounceable names
- Small functions: do one thing, one level of abstraction
- Comments: explain why, not what; avoid dead code comments
- Error handling: use exceptions, don't return null
- Format: consistent indentation, short lines, vertical density

## Deep Dive

### Meaningful Names
- **Reveal intent**: ` elapsedTime ` not ` d `
- **Avoid encodings**: no Hungarian notation, no prefixes
- **Make meaningful distinctions**: `source` vs `origin` matters
- **Use pronounceable names**: `customerName` not `custNm`
- **Use searchable names**: `MAX_CLASSES_PER_STUDENT` not `7`

### Functions
- **Do one thing**: if you can extract another function, it's doing too much
- **One level of abstraction**: each function should operate at one level
- **Short**: ideally <20 lines
- **Few arguments**: 0-3 ideal, use objects for more
- **No side effects**: function should do one thing, not modify state

### Comments
- **Good**: explains why, clarifies intent, warns of consequences
- **Bad**: explains what (code should be self-explanatory)
- **Avoid**: commented-out code, redundant comments, noise comments

### Error Handling
- Use exceptions instead of return codes
- Write try-catch-finally blocks first
- Don't return null
- Don't pass null as arguments
- Use checked exceptions sparingly

### Formatting
- **Vertical density**: related concepts close together
- **Horizontal density**: related operations on same line
- **Indentation**: consistent, reflects structure
- **Line length**: aim for <80 characters

### Code Smells
- Long functions
- Large classes
- Long parameter lists
- Divergent change (one class modified for many reasons)
- Shotgun surgery (one change requires many small edits)

## See Also
- **solid-principles** — Design principles for clean architecture
- **refactoring-patterns** — How to fix code smells
- **test-driven-development** — TDD produces clean code naturally
- **conventional-commits** — Clean commit messages
