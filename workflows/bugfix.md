# Workflow: bugfix (and hotfix)

Fast lane for defects. One final gate. Keep it cheap.

## Phases and roles
1. Reproduce and triage: atlas-maintenance (or atlas-dev)
2. Fix: atlas-dev
3. Test: atlas-qa (regression test for the defect)
4. Review: atlas-reviewer
5. Security or compliance: only if the change touches their domain
6. Gate: final delivery (user)
7. Deploy: atlas-devops (hotfix: expedited, with rollback ready)

## Default tiers
Fast: atlas-dev, atlas-maintenance. Standard: atlas-qa, atlas-devops. Premium: atlas-reviewer only if risk is high.

## Definition of Done
- Root cause identified with evidence (no guessing).
- Regression test added and passing.
- Review clear; rollback ready for hotfix.
