---
name: babok-techniques
load-when: Gathering requirements, analyzing stakeholders, defining business needs
skip-when: Project planning (see pmbok-framework), user experience (see nielsen-heuristics)
---

# BABOK Techniques

## Quick Reference
- BABOK = Business Analysis Body of Knowledge (IIBA)
- 50+ techniques for business analysis
- Key techniques: stakeholder analysis, SWOT, MoSCoW, use cases, user stories
- Requirements types: business, stakeholder, solution, transition
- Bridge between business needs and technical solutions

## Deep Dive

### Stakeholder Analysis
1. Identify all stakeholders
2. Classify by influence and interest
3. Determine communication needs
4. Plan engagement strategy

### Requirements Elicitation Techniques
| Technique | When to Use |
|-----------|-------------|
| Interviews | Deep dive with individual experts |
| Workshops | Group consensus building |
| Observation | Understanding actual workflows |
| Surveys | Large-scale feedback collection |
| Document Analysis | Understanding existing systems |
| Prototyping | Validating requirements visually |

### Prioritization
- **MoSCoW**: Must have, Should have, Could have, Won't have
- **Kano**: Basic, Performance, Delighter
- **Weighted Scoring**: criteria × weights × scores
- **Timeboxing**: fix time, vary scope

### User Stories
```
As a [role]
I want [feature]
So that [benefit]
```
Acceptance criteria: Given/When/Then (BDD format)

### Gap Analysis
1. Current state (as-is)
2. Future state (to-be)
3. Gap (what's missing)
4. Roadmap (how to close the gap)

### Business Case
- Problem statement
- Proposed solution
- Cost-benefit analysis
- Risk assessment
- Timeline
- Decision recommendation

## See Also
- **pmbok-framework** — Project management context
- **scrum-guide** — Agile requirements management
- **minto-pyramid** — Structuring requirements documents
- **spint-selling** — Eliciting stakeholder needs
