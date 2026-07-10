# Core values and charter runtime checks

Maps Atlas branding values and team charter standards to what operators and roles can verify at runtime. Full charter text lives in `rules/team-charter.mdc`. Values list in `branding-values.md`.

## Values → runtime checks

| Value / standard | What it means in practice | Runtime check |
| --- | --- | --- |
| You're in command | Human approves gates, MCP writes, and budget overruns | Pending gates in chat; `gates/*.json` sidecars in the run folder |
| Evidence over guesswork | Claims cite sources; unknowns escalate | Requirements and design artifacts list assumptions; open questions routed via atlas-pm / atlas-ba |
| Simplicity over complexity | Minimal diff, no premature abstraction | atlas-reviewer and atlas-architect flag over-engineering in `review.md` |
| Frugal by design | Token and cost awareness | Kickoff `budget.md` (see `budget-template.md`); downgrades logged per `model-resilience.md` |
| Craftsmanship | Higher quality only, not more volume | Gate Definition of Done checklists in lead playbook; security and review gates before deploy |
| Collective intelligence | Specialists own artifacts; lead orchestrates | `team.json` delegation rows in the run folder |
| Always learning | Lessons read before work; proposals after | `lessons.md` read; `proposed.md` and retro actions queue for user approval |
| Never reinvent the wheel | MCP and existing tools first | MCP-first rule; charter blocks ad-hoc REST when MCP exists |
| Built to scale | Lazy context, workflow presets | `atlas-core.mdc` stays small; playbooks load on demand; workflow picks phase set |

## Charter standards → runtime checks

| Standard | Runtime signal |
| --- | --- |
| Token efficiency | Estimation huddle before first specialist Task; `Predicted` and role estimates in `budget.md`; pipeline validator warns on kickoff gaps |
| No guesswork | Triage and requirements artifacts name evidence or mark TBD with escalation |
| Human-authored voice | `validate.ps1` / `validate.sh` flags em dashes and AI tells; atlas-reviewer checks prose |
| Model resilience | Downgrade lines in `budget.md` and `usage-insights.md`; `downgradedFrom` on delegation rows |
| Orchestration only (lead) | Specialist artifacts appear after Task delegation; lead edits `team.json`, `budget.md`, gate sequencing only |
| Approval gates | Requirements, design, final (plus token-budget when heavy); user sign-off recorded in gate sidecars |

## Token efficiency as FinOps layer

Treat token usage like a cloud cost envelope, not an afterthought.

**Predict (kickoff)**

1. atlas-lead announces workflow and rationale.
2. Estimation huddle via Task: each role returns light | medium | heavy.
3. atlas-ai-eng aggregates; lead writes `budget.md` from `budget-template.md`.
4. Heavy predicted usage needs token-budget gate approval before build Tasks start.

**Observe (during run)**

- `budget.md`: predicted vs approved envelope and downgrade lines.
- `team.json`: active premium-tier count (lead should cap concurrent premium delegations per playbook).
- Kickoff gaps (missing estimates, workflow rationale) surfaced by atlas-lead before build Tasks.

**Report (post-run)**

- `budget.md` **Actual** section (see v1 note below).
- `usage-insights.md`: patterns, estimation accuracy, downgrade log.
- Retro `token efficiency` section (`retro-template.md`).

**Optimize**

- atlas-ai-eng proposes cuts in `usage-insights.md` and ways-of-working.
- Model tier table in `README.md`: lead on standard; premium reserved for gate roles via Task.

## Actual usage in budget.md (v1)

The **Actual** block in `budget-template.md` is **self-reported** in v1. Roles and lead fill it at final delivery or retro from chat memory, delegation notes, and downgrade lines. There is no automatic token telemetry from Cursor into `budget.md` yet.

v2 (planned): SDK or IDE telemetry feeds Actual by tier and role. Until then, treat Actual as directional, not audit-grade. FinOps decisions should lean on Predicted, gate approval, downgrade frequency, and retro notes.

## Anti-patterns

| Anti-pattern | Why it fails the charter | Correct behavior |
| --- | --- | --- |
| Lead implements after quota hit | Collapses team model; burns lead context | Re-delegate via Task at lower tier (`model-resilience.md`) |
| Skip kickoff budget | No envelope; heavy work starts unapproved | Phase 0 kickoff before requirements or build Tasks |
| Chat-only gate approval without sidecar | Gate state not inspectable on disk | Confirm approval in chat and write or update `gates/<gate>.json` |
| Inline REST to Jira/GitLab when MCP exists | Bypasses approval and audit path | MCP read free; MCP write drafted and approved |
| Mark delegation `completed` without Task success | False progress in `team.json` | Keep `active` or `failed` until subagent returns |
| Regenerate full artifacts each phase | Wastes tokens; drops prior decisions | Handoff paths in brief; edit artifacts on disk |
| Premium tier on every role | Exhausts quota early | Default tiers in workflow presets and `README.md` |
| Ignoring legacy run warnings | Pre-v1 runs lack `frameworkVersion: 1` | Acknowledge warnings or migrate run manifest |
| Fabricating Actual numbers | Breaks evidence standard | Estimate honestly or leave blank with note until v2 telemetry |

## References

- `rules/team-charter.mdc`
- `knowledge/budget-template.md`
- `knowledge/model-resilience.md`
- `knowledge/collaboration.md`
