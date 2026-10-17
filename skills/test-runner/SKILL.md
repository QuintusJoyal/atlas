---
name: test-runner
description: Run a project's test suite and report structured pass/fail results with failing-test details.
type: skill
version: 1.0.0
appliesTo: [all]
capabilities: [test-execution]
permissions: [read-files, run-commands]
inputs: [scope]
outputs: [result, exit-code]
requires: []
tags: [testing, ci, quality]
---

# test-runner

Cross-agent, cross-project skill that discovers and runs a project's test suite and returns a structured result. Any agent binds it via capability tag `test-execution` (see `knowledge/process/skill-registry.md`).

## Route
- run tests, execute suite → test-runner
- CI test gate, pre-merge check → test-runner
- flaky or failing test triage (first pass) → test-runner

## Inputs
- `scope` (optional) — path or suite name to narrow the run (e.g. `tests/auth`). Default: the project's full suite.

## Outputs
- `result` — pass/fail summary with failing test names and error excerpts.
- `exit-code` — the test command's exit code, verbatim.

## Procedure
1. Detect the runner from project files (e.g. `package.json` → npm test, `pyproject.toml`/`pytest.ini` → pytest, `go.mod` → go test, `Cargo.toml` → cargo test). Never install a runner the project does not declare.
2. Run the suite with `scope` if given, otherwise the full default suite. Capture stdout/stderr and the exit code.
3. On non-zero exit, extract the failing test names and the shortest error excerpt that explains each; do not paste full logs.
4. Report `result` + `exit-code` to the binding agent. Retry once only for errors that are clearly environmental (e.g. missing dev service); never retry a genuine assertion failure.

## Audit
Append one line per invocation to `$ATLAS_DATA_DIR/skill-audit.log` per the registry convention: `timestamp|role|session|test-runner@1.0.0|invoked|exit=<code> <passed>/<total> passed`.

## Scope
Test execution and result summarization | NOT writing or fixing tests (→ dev), test strategy or coverage design (→ qa), CI pipeline authoring (→ devops).

## Delegation Examples
### Quality gate before handoff
"Run the suite and tell me if it's green." → test-runner: detect runner, execute full suite, return pass/fail summary with failing-test excerpts.

### Targeted regression check
"Only the auth tests, did my change break them?" → test-runner: scope to `tests/auth`, report result and exit code.
