---
name: document-sharding
category: process
load-when: Working with large documents (500+ lines), designing document structure
skip-when: Short documents, single-section work
description: Structure large documents for selective loading by agents.
audience: [all]
tags: [documents, structure, loading, sections]
---

# Document sharding

Large documents should be structured for selective loading.

## Quick Reference
- Design with clear H2/H3 sections that agents load independently
- Each section self-contained (understandable alone)
- Use `See <document>.md#<section>` for cross-references, not duplication
- When >500 lines, split into on-demand sections

## Principles

- **Self-contained sections:** each section should be understandable without loading other sections. Use descriptive header names.
- **References over duplication:** when a section references another section, use `See <document>.md#<section-name>` rather than duplicating content.
- **Progressive loading:** when a document exceeds 500 lines, split into on-demand sections. The lead agent can reference sections by name rather than passing the full document in delegation.
- **Naming:** use descriptive H2/H3 names that tell an agent what's inside without loading. "Rate Limiting" is better than "Configuration".
