<!-- GENERATED FILE. Do not edit directly.
     Source: skills/atlas-qa-playbook/SKILL.md (the <!-- lite:start --> block).
     Regenerate with: python3 scripts/build-lite.py -->

# atlas-qa (Lite Playbook)

## Route
- write tests → atlas-qa
- verify fix → atlas-qa
- regression test → atlas-qa
- quality assessment → atlas-qa

## Rules
1. Test against requirements, not against the implementation.
2. Report with evidence: steps, expected, actual.
3. Never approve with failing tests or critical findings.

## Knowledge (inlined, no external files)
- Testing pyramid: ratio unit 70% / integration 20% / e2e 10%. Never skip unit tests to write more e2e. Inverted pyramid = maintenance debt.
- Test design: equivalence partitioning (test one value per input group), boundary analysis (test at edges, not the middle), decision tables (all combinations of conditions), error guessing (target likely defects from experience).
- BDD/Gherkin: Feature → Scenario → Given/When/Then. One scenario = one testable behavior. Feature files are living documentation, not just tests.
