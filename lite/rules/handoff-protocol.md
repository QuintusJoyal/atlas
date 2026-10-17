# Handoff Format (Lite)

Every handoff has 4 sections:

## Summary
What you did. 2-3 sentences max. Key files changed.

## Outputs
Files created or modified (full paths). Decisions made.

## Issues
Blockers, questions, or risks. Write "None" if there are none.

## Next
Who picks up next and what they do first. Be specific: "atlas-qa should run regression tests on the export endpoint" not "qa should test."

## Attenuation (lite)
When you delegate, give the subagent a tool scope strictly smaller than your own — never equal, never larger. A subagent never widens its own scope; it escalates the need to atlas-lead or the user instead. Lite mode skips the delegation-chain record — attenuation only.
