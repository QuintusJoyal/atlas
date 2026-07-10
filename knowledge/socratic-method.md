---
name: socratic-method
load-when: Questioning assumptions, facilitating discovery, deep investigation
skip-when: Requirements gathering (see babok-techniques), root cause analysis (see 5-whys-root-cause)
---

# Socratic Method

## Quick Reference
- Structured questioning to stimulate critical thinking
- Ask questions rather than provide answers
- Challenge assumptions, explore definitions, examine evidence
- Guide others to discover insights through reasoning
- Use in code reviews, architecture discussions, requirements discovery

## Deep Dive

### Types of Socratic Questions
1. **Clarifying**: "What do you mean by...?", "Can you give an example?"
2. **Probing assumptions**: "What are you assuming?", "Why do you assume that?"
3. **Probing reasons and evidence**: "What evidence supports this?", "How do you know?"
4. **Exploring viewpoints**: "What's an alternative?", "How would someone who disagrees see this?"
5. **Probing implications**: "What would happen if...?", "What are the consequences?"
6. **Questions about the question**: "Why is this question important?", "What's the real issue?"

### When to Use
- Requirements discovery: "Why do you need this feature?"
- Architecture review: "What trade-offs did you consider?"
- Code review: "Why did you choose this approach?"
- Problem-solving: "What's the root cause?"
- Mentoring: guide thinking, don't provide answers

### When NOT to Use
- Urgent situations requiring immediate action
- When the answer is well-established and documented
- When emotions are high (use empathy first)

### Socratic Questioning in Code Review
- "What happens if the input is null?"
- "How does this handle concurrent access?"
- "What's the failure mode here?"
- "How would we test this?"

## See Also
- **5-whys-root-cause** — Structured root cause questioning
- **mece-framework** — Structured problem decomposition
- **minto-pyramid** — Structured communication
- **spin-selling** — Structured questioning for discovery
