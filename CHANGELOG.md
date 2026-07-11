# Changelog

All notable changes to Atlas are recorded here. This project follows semantic versioning.

## [Unreleased]

## [0.12.0] - 2026-07-11

### Added

- **9 extracted knowledge files** — moved tactical sections from atlas-core.md into load-on-demand knowledge files: context-engineering, structured-reasoning, clarification-strategy, document-sharding, pre-action-gates, problem-domain-classification (Cynefin), observe-before-act (Gemba), pre-handoff-quality-check, escalation-tiers. atlas-core.md slimmed from ~2,600 to ~800 tokens for optimal prefix caching.
- **Tool registry** — new `knowledge/tool-registry.md`: structured catalog of tool patterns (file ops, search, shell, delegation, web), Atlas-specific batch/read-before-edit/workdir patterns. Agents load on-demand when unsure which tool to use.
- **Trajectory logging** — new `knowledge/trajectory-logging.md`: JSONL decision trail schema (who, what, why, outcome) for post-hoc analysis, debugging, and feeding lessons.md. IDE-agnostic: each IDE implements appending via tool hooks or post-action callbacks.
- **Prompt cache strategy** — new `knowledge/prompt-cache-strategy.md`: cache-optimized ordering (static rules first, dynamic context last), `cache_control` breakpoint concept, anti-patterns for progressive loading defeating caching.
- **Memory hierarchy** — new `knowledge/memory-hierarchy.md`: L1 (personal lessons) > L2 (project knowledge) > L3 (shared patterns). Conflict resolution rules, lesson writing format, cross-project leakage prevention.

### Changed

- **atlas-core.md slimmed** — extracted 9 tactical sections into knowledge files. Now ~800 tokens (down from ~2,600). Non-negotiables + bootstrap + knowledge loading + load-on-demand table (16 entries). Cache-optimized: stable prefix across turns.
- **collaboration.md expanded** — added trajectory logging section and memory hierarchy section with pointers to new knowledge files.
- **lite/rules/atlas-core.md expanded** — added deep guidance section with pointers to 10 extracted knowledge files for complex tasks that overflow lite mode.
- **manifest.json** — added 13 new knowledge files, bumped to 0.12.0.

### Version

- **Version** — bumped to 0.12.0

## [0.11.0] - 2026-07-11

### Added

- **9 new rule files** — created all missing rules referenced by agents: security, data-governance, responsible-ai, networking, cost-governance, architectural-governance, compliance, delivery-governance, client-engagement. 50% of agents now have valid rule references.
- **Cynefin domain classification** — added problem domain classification (clear/complicated/complex/chaotic) to atlas-core as Step 0 before choosing strategy. Agents now diagnose the nature of a problem before deciding how to approach it.
- **Gemba observe-before-act** — added to atlas-core: read files, run tests, check git log before making changes. Prevents acting on assumptions.
- **Pre-handoff quality check** — added to atlas-core: 5-point verification before declaring completion. Includes 3-strike rule for repeated errors.
- **Escalation protocol** — added to atlas-core: 4-tier escalation (T1: retry, T2: escalate to lead, T3: lead to user, T4: crisis). Minimum payload: what was tried, what failed, what's needed.
- **Tool-first enforcement** — added to atlas-core: every response must be a tool call, user question, or formal completion. No plain-text filler.
- **INVEST criteria for task decomposition** — added to atlas-lead orchestration: tasks must be Independent, Negotiable, Valuable, Estimable, Small, Testable before delegation.
- **6 new knowledge files** — kubernetes-patterns, api-design, event-driven-architecture, developer-experience, incident-response, observability-tooling.
- **4 new workflows** — database-migration, performance-optimization, observability-setup, disaster-recovery. Each with small/full variants.
- **4 new lite specialist agents** — atlas-dev, atlas-qa, atlas-architect, atlas-security. Stripped-down definitions for 3B-8B models.
- **4 new lite specialist playbooks** — atlas-dev, atlas-qa, atlas-architect, atlas-security playbooks for lite mode.
- **Lite engineering-standards rule** — condensed coding standards for lite mode.
- **Lite infra-change workflow** — infrastructure change workflow for lite mode.
- **State file format** — formalized state file template in model-resilience.md for workflow resume-from-failure.
- **TOGAF knowledge file** — created togaf-framework.md with ADM phases, Enterprise Continuum, and Architecture Content Framework.

### Fixed

- **atlas-db typo** — fixed handoff-protocol.md contract table: `atlas-db` → `atlas-dba`.
- **TOGAF knowledge mapping** — fixed atlas-ent-arch playbook: TOGAF now correctly maps to `k/togaf-framework` instead of `k/pmbok-framework`.
- **atlas-maintenance rules** — added `engineering-standards` to atlas-maintenance frontmatter (was empty).

### Changed

- **atlas-core expanded** — added 6 new sections: problem domain classification, observe before act, pre-handoff quality check, escalation tiers, tool-first enforcement, state file format.
- **atlas-lead orchestration expanded** — added INVEST criteria to delegation reasoning loop, added domain classification to delegation reasoning.
- **Lite atlas-core expanded** — added 3 new rules: read-before-edit, classify-first, every-response-is-action. Added escalation tiers.
- **Agent examples** — added concrete examples to principles in atlas-docs, atlas-maintenance, atlas-ent-arch.
- **Model resilience** — added state file format template for workflow persistence.
- **Manifest** — updated with all new rules, knowledge files, and workflows.

### Version

- **Version** — bumped to 0.11.0

## [0.10.0] - 2026-07-11

### Added

- **Lite mode** — parallel set of stripped-down rule/agent/workflow/skill files for 3B-8B models with 8K context windows. ~1,100 token system prompt vs ~6,300 in full mode.
  - `lite/rules/atlas-core.md` — 5 imperative rules (~200 tokens)
  - `lite/rules/handoff-protocol.md` — 4-section format only (~80 tokens)
  - `lite/rules/atlas-lead-orchestration.md` — step-by-step delegation procedure (~200 tokens)
  - `lite/rules/team-charter.md` — 3 rules + 1 gate checklist (~100 tokens)
  - `lite/agents/atlas-lead.md` — routing + delegation only (~400 tokens)
  - `lite/workflows/feature.md`, `bugfix.md`, `discovery.md` — max 4 phases, inline conditions
  - `lite/skills/atlas-dev-playbook/SKILL.md`, `atlas-lead-playbook/SKILL.md` — ~120 tokens each
- **Compaction state block template** — formal ~100 token template for context compaction in model-resilience.md
- **Fresh session brief template** — formal ~150 token template for escalation when compaction fails
- **Quick Reference sections** — added to model-resilience.md, collaboration.md, lead-routing.md
- **Concrete examples** — added one example per principle to top 10 agents (dev, qa, architect, security, pm, ba, devops, lead, ux, reviewer)
- **"Works with" protocol** — defined in collaboration.md: bidirectional information exchange, initiate when needed
- **Scope-change handoff format** — 3-section assessment template in handoff-protocol.md

### Fixed

- **Broken knowledge references** — fixed 6 broken file references: quality-bars→quality-gates (9 files), decision-frameworks→mece-framework (2 files), testing-anti-patterns→anti-patterns, solid-practices→solid-principles, craftsmanship→clean-code-practices, anthropic-context-engineering→inline (atlas-docs-playbook)
- **Variant naming** — unified bugfix.md from "simplified" to "small" to match all other workflows
- **Gate schema mismatch** — renamed quality-gates.md gates to match workflow files (Code Gate→implementation, Test Gate→testing, Release Gate→deploy)
- **DoD implicit/explicit contradiction** — clarified that small variant DoD is implicit (role completed = gate passed), no phantom checklist
- **Duplicate atlas-ux** — removed duplicate row in handoff-protocol.md contract table
- **Self-reference** — removed swebok.md self-reference in See Also
- **Frontmatter** — added load-when/skip-when to model-resilience.md, collaboration.md, lead-routing.md
- **Acronym expansions** — expanded DSAR, DPIA, ISMS, AUC-ROC, RMSE, MAE at first use in agent files
- **atlas-lead rules** — added model-resilience to atlas-lead.md frontmatter rules list
- **team.json mandate** — added per-turn state.md read requirement to atlas-lead.md

### Changed

- **Version** — bumped to 0.10.0

## [0.9.1] - 2026-07-11

### Added

- **Auto-approve gates (small variant)** — small variant final gate auto-approved when all DoD items pass. No user interaction needed. User can override: "I want to review before deploy."
- **Skip tracking (small variant)** — small variants skip team.json and budget.md. Phase states tracked in memory only. No audit trail. Saves ~200 tokens per small run.
- **Compressed handoff (small variant)** — small variant handoffs use 4 sections instead of 8: Summary, Outputs, Issues, Next. Saves ~200 tokens per handoff.
- **Auto-detect conditions** — lead auto-detects conditions from task description (auth/payment → security-sensitive, GDPR/SOC2 → regulated, etc.). User can override at kickoff.
- **Batch delegation** — parallel phases delegated in a single turn. Lead sends multiple delegation calls in one message. Phases run concurrently.
- **Auto-resume** — when user says "continue" or "resume", lead auto-resumes from last completed phase. No confirmation needed.
- **Skip validation (small variant)** — small variant DoD is implicit. Role completed = gate passed. No explicit DoD checklist validation.

### Changed

- **All 6 workflow files** — compressed kickoff sections, added auto-approve/tracking metadata.
- **workflows/README.md** — documented all optimizations, universal kickoff.
- **manifest.json** — added optimizations section (auto-approve, skip-tracking, compressed-handoff, auto-detect, batch-delegation, auto-resume), autoDetect keyword mapping.
- **atlas-lead.md** — added auto-gate, auto-detect, skip-tracking, auto-resume rules.
- **atlas-lead-orchestration.md** — added batch delegation, skip validation rules.
- **handoff-protocol.md** — added compressed template for small variants (4 sections).
- **team-charter.md** — added auto-approve rule for small variant gates.
- **quality-gates.md** — added auto-approve criteria, updated gate table with auto-approve column.

## [0.9.0] - 2026-07-11

### Added

- **Workflow variants** — every workflow preset now has two variants: small (lightweight, skip unnecessary gates, no estimation huddle) and full (standard, all gates, estimation huddle). Variants reduce token usage by ~40% for simple tasks.
- **Workflow conditions** — conditional phase injection via boolean flags (regulated, data-changes, security-sensitive, etc.). Conditions evaluated at kickoff; matched conditions inject additional phases or roles.
- **Formal state machine** — every workflow follows a state machine: pending → active → gated → completed (+ failed, paused, aborted). States tracked in team.json with explicit transitions.
- **Scope-change handling** — when requirements change mid-workflow, pause current phase, re-evaluate via PM/BA, present options to user (resume, restart from phase X, abort, switch variant).
- **Abort and resume** — user or lead can abort at any time; resume from last completed phase. One workflow per run; must resume or abort before starting a new one.
- **Phase composition** — phases can be added via conditions. Injected phases follow the same state machine as native phases. Parallel phases run concurrently.
- **Workflow metadata in manifest.json** — new `workflowMeta` section with state machine, variants, conditions, gates, and transitions.

### Changed

- **All 6 workflow files rewritten** — structured format with named phase blocks (gate, parallel, roles, skip-if, input/output), variants, conditions, and state machine.
- **atlas-lead.md** — added variant selection, condition evaluation, state management, scope-change handling, abort/resume rules.
- **atlas-lead-orchestration.md** — added scope-change handling, abort/cancel/resume, composition rules.
- **handoff-protocol.md** — added variant and phase state to handoff template, state transition rules.
- **team-charter.md** — variant-aware gate enforcement, state machine enforcement rules.
- **quality-gates.md** — variant-aware gate criteria (small skips requirements/design gates).

## [0.8.0] - 2026-07-11

### Added

- **Knowledge base: 67 standalone domain reference files** — granular, self-contained docs covering testing, security, architecture, DevOps, data, craftsmanship, delivery, compliance, AI/ML, UX, cloud, decision frameworks, quality, and anti-patterns. Each file has frontmatter (name, load-when, skip-when), Quick Reference, Deep Dive, and See Also sections. Designed for AI agents (search via grep) and humans (read directly).
- **Compact playbooks** — all 24 playbooks rewritten to ~180 tokens each with Route, Knowledge Index, Scope, and Delegation Examples. Playbooks now serve as routing cards with embedded search indexes for knowledge files.
- **Three-tier knowledge loading** — inline (playbook facts) → search (grep for specific term) → load (full file). Reduces token usage by ~73% compared to loading full knowledge files.
- **Bootstrap section in atlas-core.md** — universal bootstrap steps (grep lessons.md, model-resilience.md) moved from individual playbooks to core rules.
- **Knowledge loading budget** — routine task = 2-3 searches (~400-600 tokens), complex task = 3-5 searches + 1 full file (~1,500-2,500 tokens), hard cap = 5,000 tokens per task.
- **Knowledge file index** — comprehensive index in knowledge/README.md with topic, file, and role mappings.

### Changed

- **Playbook format** — all 24 playbooks standardized to compact format: Route (trigger → role), Knowledge Index (search term → file), Scope (DO | NOT), Delegation Examples (2-3 condensed examples).
- **atlas-core.md** — added Bootstrap, Knowledge Loading, and three-tier loading strategy sections.

## [0.7.0] - 2026-07-11

### Added

- **Per-agent principles:** all 24 agents now have 4 role-specific thinking rules (inspired by BMAD agent principles and CrewAI persona system).
- **Phase-transition validation:** Gate 1/2/3 checklists in `team-charter.md` with concrete criteria for requirements→design, design→implementation, and implementation→delivery transitions (inspired by BMAD phase-transition validation).
- **Structured handoff contracts:** input/output contract table for all 24 roles in `handoff-protocol.md`, with required fields for inputs and outputs (inspired by OpenAI Swarm explicit handoffs and MetaGPT structured outputs).
- **Pre-action gates:** verification checklists for security, architecture, and review decisions in `atlas-core.md` and role-specific agents (inspired by SARC pre-action gates and GlassBox decision interception).
- **Context engineering patterns:** progressive disclosure, just-in-time loading, tool-as-context, structured note-taking, and compaction triggers in `atlas-core.md` (from Anthropic context engineering research).
- **Structured reasoning patterns:** plan-then-action, thought-action-observation loop, atomic reasoning, and lookahead simulation in `atlas-core.md` (from ReAct, PTA-GRPO, GoT-R1, NCoTS research).
- **Clarification strategy:** when-to-ask vs. when-to-proceed rubric, information gain principle, and question consolidation in `atlas-core.md` (from ClarifyAgent research).
- **Document sharding:** guidance for breaking long documents into loadable sections in `atlas-core.md` (from BMAD document sharding).
- **Delegation reasoning loop:** atlas-lead now reasons through current state, goal, owning role, and inputs before each delegation (from ReAct loop applied to orchestration).
- **Compaction rubric:** when-to-compact vs. when-not-to-compact table in `model-resilience.md` with proactive compaction guidance (from SelfCompacting research).

## [0.6.0] - 2026-07-10

### Changed

- **Agent restructure:** all 24 agents rewritten with deep expertise definitions, role boundaries (I DO / DO NOT), collaboration tables, and 2 delegation examples each.
- **Model hints deduplicated:** `modelHints` removed from all 24 agent frontmatter; centralized in `manifest.json` tiers section.
- **atlas-lead trimmed:** routing tables, keyword mappings, workflow-phase routing, multi-role rules, artifact ownership, and specialist engagement moved to `knowledge/lead-routing.md`. Agent file reduced from ~398 lines to ~141 lines.
- **Delegation examples moved:** 3 of 5 delegation examples removed from each of 23 specialist agents; moved to corresponding playbook SKILL.md files.
- **"I DO NOT" removed:** role boundary "DO NOT" sections removed from 22 specialist agents (ownership matrix in `knowledge/collaboration.md` is the single reference).
- **Model resilience consolidated:** duplication across atlas-core.md, atlas-lead-orchestration.md, atlas-lead.md, team-charter.md, collaboration.md, and atlas-lead-playbook reduced to pointers to canonical `knowledge/model-resilience.md`.
- **Delegation rules consolidated:** duplication across atlas-core.md, atlas-lead.md, atlas-lead-playbook, and collaboration.md reduced to single source in `atlas-lead-orchestration.md`.
- **atlas-lead-orchestration load changed:** from `always` to `on-demand` (saves ~1,178 tokens per invocation).

### Added

- `knowledge/lead-routing.md`: intent classification, keyword-to-role mapping, workflow-phase routing, multi-role delegation rules, artifact ownership, and specialist engagement triggers.
- Frontier behavior patterns: context compaction, tool clearing, structured output, and output length targets added to atlas-core.md, model-resilience.md, atlas-lead.md, atlas-dev.md, and atlas-qa.md.
- Artifact ownership matrix added to `knowledge/collaboration.md`.

## [0.5.0] - 2026-07-10

### Changed

- **Universal IDE support:** Atlas is no longer Cursor-only. Works on Cursor, Claude Code, OpenCode, VS Code Copilot, Windsurf, Antigravity, and any AI IDE that reads agents, rules, and skills from a project.
- **Model tiers abstracted:** per-role model slugs replaced with `premium`/`standard`/`fast` tiers. Each IDE maps tiers to its available models via `modelHints` in agent frontmatter.
- **Delegation protocol:** abstract protocol-agnostic delegation replaces Cursor Task tool specifics. Each IDE implements delegation natively.
- **Data home universalized:** all `~/.cursor/atlas-data/` and `~/.cursor/atlas-knowledge/` paths replaced with `$ATLAS_DATA_DIR/`.
- **Agent frontmatter:** all 24 agents rewritten with universal schema (name, role, tier, capabilities, permissions, skills, rules, modelHints, memory).
- **Rules renamed:** all `.mdc` files renamed to `.md` with universal frontmatter (name, load, globs).
- **Skills updated:** all 24 SKILL.md files updated with `type` and `appliesTo` fields; `disable-model-invocation` removed.
- **Knowledge updated:** all knowledge files updated with frontmatter (name, category, description, audience, tags) and universal paths.
- **Workflows updated:** all 6 workflow files updated with frontmatter (name, type, triggers, gates).
- **SETUP.md created:** comprehensive AI-readable setup guide for 6 IDEs, model tier mapping, multi-agent config, and verification checklists.
- **Shell scripts removed:** `install.sh`, `install.ps1`, `validate.sh`, `validate.ps1` removed (replaced by SETUP.md).
- **Obsolete docs removed:** `docs/PUBLIC_RELEASE_CHECKLIST.md`, `docs/archive/CONTROL-CENTER-PLAN.md` removed.

### Added

- `SETUP.md`: IDE-specific install instructions, model tier mapping table, multi-agent nesting config, verification checklists.
- `manifest.json`: universal bundle schema (atlas-bundle/1.0), tiers, delegation protocol, dataHome/knowledgeHome.

## [0.4.0] - 2026-06-17

### Changed

- **SDK colocation:** Cursor SDK orchestrator and runner moved to [`atlas-control-center`](https://github.com/QuintusJoyal/atlas-control-center) (`sdk/`). This bundle ships agents, rules, skills, and knowledge only.

## [0.3.0] - 2026-06-12

### Added (Atlas Framework v1)
- **Hybrid runtime:** kickoff validator, gate DoD evaluator, delegation checks via chat and repo artifacts.
- Graduated enforcement via chat prompts and gate sidecars (`warn` | `standard` | `strict`).
- Waiver flow with non-waivable 2nd/3rd line DoD; force-approve audit trail in gate sidecars.
- KB promote/reject inbox actions; auto usage-insights row on final gate.
- Six workflow plans with RACI fields on delegations.
- Knowledge: `core-values-charter.md`, `enterprise-org-model.md`, `atlas-framework.md`, `retro-template.md`.
- `scripts/merge-knowledge.ps1`.

### Changed
- Root README: Framework v1 positioning, install/post-update.
- `atlas-lead`: kickoff and gate checks via chat and repo artifacts.
- Legacy runs (no `frameworkVersion: 1`): warn-only enforcement.

## [0.2.5] - 2026-06-12

### Added
- Mandatory pipeline **kickoff**: workflow announcement, estimation huddle, `budget.md` from `knowledge/budget-template.md`, per-role estimates before first specialist delegation.
- `team.json` fields: `workflowRationale`, `kickoffAt`, `budget` (predicted + roleEstimates).

### Changed
- `workflows/feature.md`, `bugfix.md`, README: Phase 0 kickoff documented.
- `atlas-lead` agent and playbook: kickoff blocking sequence.
- `handoff-protocol`, `atlas-ai-eng-playbook`: required role estimates in handoffs and huddle output format.

## [0.2.4] - 2026-06-12

### Changed
- **atlas-lead default model** moved from premium to standard so orchestration does not burn premium quota; premium stays for gate roles.
- Documented **lead self-limit** failure mode: when the orchestrator session hits quota, lead must still delegate to specialist roles; forbidden to collapse into inline implementation.

## [0.2.3] - 2026-06-12

### Added
- `rules/atlas-lead-orchestration.mdc` (always-on): hard stop when delegation fails or hits quota. Lead's only recovery is re-delegate same role at lower tier.

### Changed
- `agents/atlas-lead.md`: quota interrupt moved to top with allowed/forbidden table.
- `atlas-lead-playbook`, `model-resilience.md`, `atlas-core.mdc`: anti-patterns for lead absorbing work after interrupt.

## [0.2.2] - 2026-06-12

### Changed
- Team continuity on usage limits: atlas-lead must **re-delegate to the same role** at a downgraded tier instead of absorbing work inline.
- `team.json` delegations may record `model` and `downgradedFrom` for manifest visibility when a role was re-delegated after quota interrupt.

## [0.2.1] - 2026-06-11

### Changed
- atlas-lead now delegates every phase to the named role by default and must not impersonate roles by writing their output in its own voice.

## [0.2.0] - 2026-06-11

### Added
- Automatic model downgrade (model resilience): when a model is quota-limited, rate-limited, unavailable, or blocked, roles and atlas-lead retry the affected step one tier down (premium to standard to fast) and continue without interrupting the workflow.
- `knowledge/model-resilience.md`: the canonical tier cascade, triggers, behavior, logging format, and premium-gate quality flag.

### Changed
- `atlas-core.mdc`, `team-charter.mdc`, `handoff-protocol.mdc`, `atlas-lead` (agent and playbook), and `atlas-ai-eng` updated for the no-interruption downgrade policy and downgrade tracking.

## [0.1.0] - 2026-06-11

### Added
- Initial Atlas bundle: a self-contained, shareable team of AI IDE agents.
- 12 core SDLC roles plus the orchestrator atlas-lead.
- 12 enterprise specialists.
- Per-role playbook skills grounded in cited industry standards.
- Lazy-loaded rules: always-on atlas-core plus on-demand team-charter, handoff-protocol, writing-style, and glob-scoped engineering-standards.
- Quota-aware model tiering (premium, standard, fast) and a token-budget protocol.
- Shared knowledge base with a proposal queue, ways-of-working, and usage-insights.
- Workflow presets: feature, bugfix, data-project, infra-change, security-audit, discovery.
- Human-authored voice standard (no em dashes, no AI tells), enforced by atlas-reviewer.
