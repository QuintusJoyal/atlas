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

## Structured Typed Handoffs (Lite)
Lite mode uses the small variant schema. See `schemas/handoffs/small.json` for the canonical contract. Backward compatibility with markdown handoffs is maintained.
