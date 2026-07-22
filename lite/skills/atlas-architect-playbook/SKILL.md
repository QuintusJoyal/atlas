<!-- GENERATED FILE. Do not edit directly.
     Source: skills/atlas-architect-playbook/SKILL.md (the <!-- lite:start --> block).
     Regenerate with: python3 scripts/build-lite.py -->

# atlas-architect (Lite Playbook)

## Route
- system design → atlas-architect
- API design → atlas-architect
- architecture decision → atlas-architect
- tech debt assessment → atlas-architect

## Rules
1. Prefer the simplest solution that meets the requirement.
2. Document decisions with ADRs. Include rejected alternatives.
3. Design for failure. Assume components will fail.

## Knowledge (inlined, no external files)
- ADR: Title, Status, Context, Decision, Consequences (pros and cons). One per significant decision. Never delete an ADR — mark it superseded instead.
- C4 model: four zoom levels — Context (system + users + external systems) → Container (deployable units: web app, API, DB, queue) → Component (controllers, services, repositories) → Code. Start at Context, go deeper only when needed.
- Trade-off analysis: every decision sacrifices something. When comparing options, list criteria, weight by importance, score each option, and write the trade-off into the ADR.
