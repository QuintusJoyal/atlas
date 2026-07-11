# Lead Orchestration (Lite)

## Delegation procedure

Do this for every delegation:

1. Read `state.md` to know current phase and completed phases
2. Pick the role: match the task to a role name from the list in atlas-core
3. Write a brief:
   - **Goal:** one sentence — what this role should produce
   - **Context:** 2-3 sentences — what happened before, what they need to know
   - **Files:** paths to read (handoff from previous role, relevant code)
4. Delegate in the same turn you decide. Don't announce then wait.

## After delegation returns

1. Read the handoff fully
2. If handoff has "Issues" that need user input → tell the user, wait for answer
3. If handoff has "Next" → delegate to that role
4. Update `state.md`: mark current phase done, next phase active

## If delegation fails

Try the same role once more. If it fails again, tell the user what failed and what they can do.

## Scope change

When the user says something changes scope:
1. Stop the current phase
2. Tell the user: "Scope changed. Options: continue with adjusted scope, restart from [phase], or stop. What do you prefer?"
3. Wait for user answer before proceeding
