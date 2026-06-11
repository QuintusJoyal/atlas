# Atlas SDK orchestrator (optional)

A small, optional script that runs an Atlas-style pipeline headlessly with the Cursor SDK, for CI or automation. It is not required to use Atlas in the IDE.

## Setup
```
cd sdk
npm install
export CURSOR_API_KEY="cursor_..."   # user or service-account key
```

## Run
```
npm run pipeline -- "add CSV export to the reports page"
```

The orchestrator runs phases in sequence (requirements, design, implementation, test, review, security), threading each phase's output into the next, and prints a summary. It runs locally against the current working directory. Approval gates are surfaced as prompts in the console; in unattended mode it stops at the first gate and reports, rather than auto-approving.

## Notes
- The SDK surface evolves. See https://cursor.com/docs/sdk/typescript for the reference.
- This script is a thin starting point. Extend it to stream events into the future Atlas Control Center.
