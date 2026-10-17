---
name: escalation-tiers
category: process
load-when: Stuck on a problem, error repeated, blocker encountered
skip-when: Smooth progress, known solution
description: 4-tier escalation protocol. Escalate with structure, not just "I'm stuck."
audience: [all]
tags: [escalation, blocking, help, crisis]
---

# Escalation tiers

When you hit a wall, escalate with structure, not just "I'm stuck."

## Quick Reference
- **T1:** Retry with different approach (same role, different strategy)
- **T2:** Escalate to lead with context (what failed, what tried, what needed)
- **T3:** Lead escalates to user with options (A: X, B: Y, recommendation)
- **T4 (crisis):** Production down, data loss risk. Stop all other work. Notify user immediately.

## Tiers

### T1: Retry (same role)
Try a different approach. Same role, different strategy. You have context; use it.

### T2: Escalate to lead
When T1 fails or you need information you don't have. Minimum payload:
- What was attempted
- What failed
- What information is missing
- What help is needed

### T3: Lead to user
When the lead can't resolve it. Lead presents options:
- Option A: X (pros/cons)
- Option B: Y (pros/cons)
- Recommendation with reasoning

### T4: Crisis
Production down, data loss risk, security breach. Stop all other work. Notify user immediately. No options presentation — action required now.

## Minimum escalation payload
Every escalation must include:
1. What was attempted
2. What failed
3. What information is missing
4. What help is needed

"I'm stuck" without this context wastes everyone's time.

## Relationship to autonomy levels

Escalation tiers describe how a stuck agent asks for help. They compose with the risk-tiered autonomy levels (L0-L3) in `knowledge/context/adaptive-autonomy.md`: a T1/T2 retry stays at the current autonomy level, while T3/T4 forces at least L2/L3 and a human. A confidence drop below threshold escalates autonomy by one level even before an escalation tier is reached.
