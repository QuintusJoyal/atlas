# Atlas Setup Guide

Atlas is a universal AI agent team framework. It gives you 24 specialist roles (PM, architect, dev, QA, security, and more) plus an orchestrator (`atlas-lead`) that can run a feature from requirements through review and deploy-ready handoff.

This guide helps any AI agent install Atlas for the IDE it is running in.

## Bundle structure

```
atlas/
  agents/          24 agent definitions (YAML frontmatter + markdown body)
  lite/            Lite mode for 3B-8B models (5 agents, 5 rules, simplified workflows)
  skills/          24 playbooks (one per role, methodology and workflow)
  rules/           15 governance rules (always-on core, orchestration, charter, standards, handoff, writing, security, etc.)
  knowledge/       114 shared knowledge files in 18 subdirectories
  workflows/       14 pipeline presets (feature, bugfix, data-project, infra, security-audit, discovery, etc.)
  manifest.json    Bundle metadata, tier definitions, delegation protocol
  SETUP.md         This file
  README.md        Human-readable overview
  VERSION          Bundle version
```

## Quick setup

### Step 1: Set environment variables

Atlas stores run artifacts and knowledge in a central location. Set these before installing:

```bash
export ATLAS_DATA_DIR="$HOME/.atlas/data"
export ATLAS_KNOWLEDGE_DIR="$HOME/.atlas/knowledge"
```

Create the directories:

```bash
mkdir -p "$ATLAS_DATA_DIR/runs"
mkdir -p "$ATLAS_KNOWLEDGE_DIR"
```

Copy the knowledge base:

```bash
cp -r knowledge/* "$ATLAS_KNOWLEDGE_DIR/"
```

### Step 2: Detect your IDE

Read the environment to determine which IDE you are running in:

| Signal | IDE |
|--------|-----|
| `.cursor/` directory exists, or `cursor` in `$PATH` | Cursor |
| `.claude/` directory exists, or `claude` in `$PATH` | Claude Code |
| `.opencode/` directory exists, or `opencode` in `$PATH` | OpenCode |
| `.vscode/` directory exists, or `VSCODE_GIT_IPC_HANDLE` env var | VS Code |
| `.windsurf/` directory exists, or `windsurf` in `$PATH` | Windsurf |
| `.agents/AGENTS.md` exists | Antigravity |
| `GEMINI.md` exists at project root | Gemini |

If detection is ambiguous, ask the user which IDE they are using.

### Step 3: Install for your IDE

---

#### Claude Code

Claude Code uses `.claude/agents/` for subagents and `CLAUDE.md` for always-on instructions.

**Agent files** (24 files):

```bash
mkdir -p .claude/agents
cp agents/atlas-*.md .claude/agents/
```

**Skills** (24 directories):

```bash
mkdir -p .claude/skills
cp -r skills/atlas-*-playbook .claude/skills/
```

**Rules** append atlas-core.md to CLAUDE.md:

```bash
cat rules/atlas-core.md >> CLAUDE.md
```

**Model mapping:**

| Tier | Claude Code model |
|------|------------------|
| premium | `opus` |
| standard | `sonnet` |
| fast | `haiku` |

> Claude Code uses aliases that auto-resolve to the latest models. No manual updates needed.

During setup, add `modelHints` to each agent's frontmatter:

```yaml
modelHints:
  claude-code: opus  # or sonnet, haiku based on tier
```

**Multi-agent configuration:**

Atlas-lead must be the main session agent. Claude Code limits subagent nesting to 1 level by default (or 5 with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`).

- `atlas-lead` goes in `CLAUDE.md` (main session orchestrator)
- Specialist roles go in `.claude/agents/` (first-level subagents)
- Specialists do NOT spawn further subagents
- Delegation uses the Agent tool: `Agent(name="atlas-dev", prompt="...")`

**Verify:**

1. Start a new Claude Code session in the project
2. Type `@atlas-dev` and confirm it appears in typeahead
3. Ask "Who are you?" and confirm it responds as atlas-dev

---

#### OpenCode

OpenCode uses `.opencode/agents/` for agent definitions and `opencode.json` for configuration.

**Agent files** (24 files):

```bash
mkdir -p .opencode/agents
cp agents/atlas-*.md .opencode/agents/
```

**Skills** (24 directories):

```bash
mkdir -p .opencode/skills
cp -r skills/atlas-*-playbook .opencode/skills/
```

**Rules** append to AGENTS.md:

```bash
cat rules/atlas-core.md >> AGENTS.md
```

**Configuration** register agents in `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "default_agent": "atlas-lead",
  "agent": {
    "atlas-lead": {
      "mode": "primary",
      "model": "anthropic/claude-sonnet-5",
      "description": "Orchestrator. Delegates to specialist roles."
    }
  }
}
```

**Model mapping:**

| Tier | OpenCode model |
|------|---------------|
| premium | `anthropic/claude-opus-4-8` |
| standard | `anthropic/claude-sonnet-5` |
| fast | `anthropic/claude-haiku-4-5` |

**Multi-agent configuration:**

- `atlas-lead` as primary agent (`mode: primary` in frontmatter)
- Specialist roles as subagents (`mode: subagent` in each agent's frontmatter)
- Delegation uses the task tool: `task(agent="atlas-dev", prompt="...")`

**Verify:**

1. Start OpenCode
2. Select `atlas-lead` from the agent picker
3. Ask "What is Atlas?" and confirm it responds with framework overview

---

#### VS Code (Copilot)

VS Code uses `.github/agents/` for custom agents and `.github/copilot-instructions.md` for always-on rules.

**Agent files** (24 files, note the `.agent.md` extension):

```bash
mkdir -p .github/agents
for f in agents/atlas-*.md; do
  name=$(basename "$f" .md)
  cp "$f" ".github/agents/${name}.agent.md"
done
```

**Rules** append to copilot-instructions.md:

```bash
cat rules/atlas-core.md >> .github/copilot-instructions.md
```

**Skills** copy to workspace:

```bash
mkdir -p .github/skills
cp -r skills/atlas-*-playbook .github/skills/
```

**Model mapping:**

| Tier | VS Code Copilot model |
|------|----------------------|
| premium | `gpt-5.5` |
| standard | `gpt-5.4` |
| fast | `gpt-5 mini` |

**Multi-agent configuration:**

- VS Code supports subagents via the `runSubagent` tool
- Enable nested subagents: `chat.subagents.allowInvocationsFromSubagents: true`
- Set `disable-model-invocation: false` on agents that should be auto-delegated
- Set `user-invocable: true` on agents users can select from the dropdown

**Verify:**

1. Open VS Code in the project
2. Open Chat view
3. Select `atlas-dev` from the Agents dropdown
4. Ask "What do you do?" and confirm it responds with role description

---

#### Cursor

Cursor uses `~/.cursor/agents/` for agents and `~/.cursor/rules/` for rules.

**Agent files** (24 files):

```bash
mkdir -p ~/.cursor/agents
cp agents/atlas-*.md ~/.cursor/agents/
```

**Skills** (24 directories):

```bash
mkdir -p ~/.cursor/skills
cp -r skills/atlas-*-playbook ~/.cursor/skills/
```

**Rules** convert to .mdc format:

```bash
mkdir -p ~/.cursor/rules
for f in rules/atlas-core.md rules/atlas-lead-orchestration.md rules/team-charter.md rules/engineering-standards.md rules/handoff-protocol.md rules/writing-style.md; do
  basename=$(basename "$f" .md)
  if [[ "$basename" == "atlas-core" || "$basename" == "atlas-lead-orchestration" ]]; then
    echo -e "---\nalwaysApply: true\n---\n" > ~/.cursor/rules/${basename}.mdc
  else
    echo -e "---\nalwaysApply: false\n---\n" > ~/.cursor/rules/${basename}.mdc
  fi
  cat "$f" >> ~/.cursor/rules/${basename}.mdc
done
```

**Model mapping:**

| Tier | Cursor model |
|------|-------------|
| premium | `claude-opus-4-8-thinking-high` |
| standard | `composer-2.5` |
| fast | `composer-2.5` (with `fast: true` parameter) |

Update each agent's `model:` field in frontmatter to the Cursor-specific slug.

**Multi-agent configuration:**

Cursor uses the Task tool for subagent delegation:

```
Task(subagent_type="atlas-dev", description="atlas-dev: implement feature", prompt="...")
```

- Set `model:` in each agent's frontmatter to the Cursor model slug
- The Task tool accepts a `model` parameter for tier override

**Verify:**

1. Start a new Cursor chat
2. Type `/atlas-dev` and confirm it appears as an available agent
3. Ask "Who are you?" and confirm it responds as atlas-dev

---

#### Antigravity

Antigravity uses `.agents/AGENTS.md` for always-on instructions and `.agents/skills/` for skills.

**Instructions** copy atlas-core.md to AGENTS.md:

```bash
mkdir -p .agents/skills
cp rules/atlas-core.md .agents/AGENTS.md
```

**Skills** (24 directories):

```bash
cp -r skills/atlas-*-playbook .agents/skills/
```

**Agent files** Antigravity does not support nested subagents. Copy agent files as reference documents:

```bash
mkdir -p .agents/roles
cp agents/atlas-*.md .agents/roles/
```

**Model mapping:**

| Tier | Antigravity model |
|------|------------------|
| premium | `gemini-3.1-pro` |
| standard | `gemini-3.5-flash` |
| fast | `gemini-3.1-flash-lite` |

**Multi-agent configuration:**

Antigravity has no subagent nesting. The orchestrator must be the main agent.

- atlas-lead goes in `.agents/AGENTS.md` (main session)
- Specialist roles are invoked sequentially, not in parallel
- When atlas-lead needs a specialist, it reads the role file from `.agents/roles/atlas-*.md` and acts as that role itself
- This is a significant limitation; Atlas works but without true parallel delegation

**Verify:**

1. Open Antigravity in the project
2. Ask "What is Atlas?" and confirm it responds with framework overview loaded from AGENTS.md

---

#### Windsurf

Windsurf uses `.windsurf/rules/` for rules and reads AGENTS.md.

**Rules** convert to Windsurf format with trigger frontmatter:

```bash
mkdir -p .windsurf/rules

# atlas-core: always on
echo -e "---\ntrigger: always_on\n---\n" > .windsurf/rules/atlas-core.md
cat rules/atlas-core.md >> .windsurf/rules/atlas-core.md

# atlas-lead-orchestration: model decision
echo -e "---\ntrigger: model_decision\ndescription: Atlas lead orchestration rules\n---\n" > .windsurf/rules/atlas-lead-orchestration.md
cat rules/atlas-lead-orchestration.md >> .windsurf/rules/atlas-lead-orchestration.md

# team-charter: model decision
echo -e "---\ntrigger: model_decision\ndescription: Atlas team charter\n---\n" > .windsurf/rules/team-charter.md
cat rules/team-charter.md >> .windsurf/rules/team-charter.md

# engineering-standards: glob
echo -e "---\ntrigger: glob\nglobs: \"**/*.{ts,tsx,js,jsx,py,go,rs,java,kt,rb,php,cs,cpp,c,h,hpp,scala,swift,sql,sh,ps1,yaml,yml}\"\n---\n" > .windsurf/rules/engineering-standards.md
cat rules/engineering-standards.md >> .windsurf/rules/engineering-standards.md

# handoff-protocol: model decision
echo -e "---\ntrigger: model_decision\ndescription: Handoff protocol\n---\n" > .windsurf/rules/handoff-protocol.md
cat rules/handoff-protocol.md >> .windsurf/rules/handoff-protocol.md

# writing-style: model decision
echo -e "---\ntrigger: model_decision\ndescription: Writing style guide\n---\n" > .windsurf/rules/writing-style.md
cat rules/writing-style.md >> .windsurf/rules/writing-style.md
```

**Instructions** append to AGENTS.md:

```bash
cat rules/atlas-core.md >> AGENTS.md
```

**Model mapping:**

| Tier | Windsurf model |
|------|---------------|
| premium | `anthropic/claude-opus-4-7` |
| standard | `anthropic/claude-sonnet-4-6` |
| fast | `anthropic/claude-haiku-4-5` |

**Verify:**

1. Open Windsurf in the project
2. Start a Cascade session
3. Atlas rules should be loaded automatically

---

### Step 4: Verify installation

Regardless of IDE, check:

- [ ] Environment variables set: `ATLAS_DATA_DIR`, `ATLAS_KNOWLEDGE_DIR`
- [ ] Knowledge base copied: `$ATLAS_KNOWLEDGE_DIR/reference/lessons.md` exists
- [ ] Run directory created: `$ATLAS_DATA_DIR/runs/` exists
- [ ] Agent files present: all 24 `atlas-*.md` files in the IDE's agent directory
- [ ] Skills present: all 24 `atlas-*-playbook/SKILL.md` files
- [ ] Rules loaded: atlas-core content is active in the IDE
- [ ] Agent responds: invoke `atlas-dev` and confirm it identifies itself correctly
- [ ] Orchestrator works: invoke `atlas-lead` and confirm it can describe workflows

## Model tier mapping

| Tier | Capabilities | Claude Code | OpenCode | VS Code | Cursor | Antigravity | Windsurf |
|------|-------------|-------------|----------|---------|--------|-------------|----------|
| Premium | deep-reasoning, long-context, complex-planning | `opus` | `anthropic/claude-opus-4-8` | `gpt-5.5` | `claude-opus-4-8-thinking-high` | `gemini-3.1-pro` | `anthropic/claude-opus-4-7` |
| Standard | balanced, general-purpose | `sonnet` | `anthropic/claude-sonnet-5` | `gpt-5.4` | `composer-2.5` | `gemini-3.5-flash` | `anthropic/claude-sonnet-4-6` |
| Fast | high-volume, low-latency | `haiku` | `anthropic/claude-haiku-4-5` | `gpt-5 mini` | `composer-2.5` (fast) | `gemini-3.1-flash-lite` | `anthropic/claude-haiku-4-5` |

Adjust these mappings based on your plan and account. The `modelHints` field in each agent's frontmatter stores IDE-specific suggestions.

## Multi-agent configuration

| IDE | Orchestrator location | Subagent location | Delegation mechanism | Max nesting |
|-----|----------------------|-------------------|---------------------|-------------|
| Claude Code | `CLAUDE.md` (main session) | `.claude/agents/*.md` | `Agent(name="atlas-dev", prompt="...")` | 1 (5 with experimental) |
| OpenCode | `opencode.json` (primary agent) | `.opencode/agents/*.md` | `task(agent="atlas-dev", prompt="...")` | Unlimited |
| VS Code | `.github/agents/*.agent.md` | `.github/agents/*.agent.md` | `runSubagent` tool | 5 (with setting) |
| Cursor | `~/.cursor/agents/atlas-lead.md` | `~/.cursor/agents/*.md` | `Task(subagent_type="atlas-dev", ...)` | Unlimited |
| Antigravity | `.agents/AGENTS.md` (main session) | N/A (no nesting) | Sequential role switching | 0 |
| Windsurf | `AGENTS.md` (main session) | `.windsurf/rules/` | Cascade subagent | Varies |

For all IDEs: atlas-lead is the orchestrator. It delegates to specialists. Specialists return structured handoff artifacts. atlas-lead collects artifacts and delegates to the next specialist. This pattern works regardless of nesting depth because the orchestrator always runs as the main session.

## Updating

To update Atlas after a new release:

1. Back up your knowledge base: `cp -r $ATLAS_KNOWLEDGE_DIR ~/atlas-knowledge-backup/`
2. Pull the latest bundle
3. Re-run the install steps for your IDE
4. Knowledge files `reference/lessons.md`, `reference/proposed.md`, `reference/ways-of-working.md`, `reference/usage-insights.md` are preserved (do not overwrite)
5. Start a new session so updated agents and rules load

## Choosing lite vs full mode

| Factor | Lite | Full |
|--------|------|------|
| Context window | 4K-8K tokens | 16K+ tokens |
| Model size | 3B-8B parameters | 70B+ parameters |
| Agents | 5 core roles | 24 specialist roles |
| Workflows | Simplified pipelines | Full pipelines with gates |
| Knowledge | Inlined in each playbook, no `knowledge/` dependency | Complete knowledge base, loaded on demand |
| Best for | Quick tasks, small models | Complex delivery, enterprise |

**Start with lite if:**
- Your model has < 16K context window
- You're using a 3B-8B parameter model
- You want fast, lightweight orchestration
- You only need dev, qa, architect, security, and lead roles

**Use full if:**
- Your model has 16K+ context window
- You're using 70B+ parameter models
- You need all 24 specialist roles
- You want full approval gates and tracking

## Uninstalling Atlas

> **Warning:** This removes all Atlas run data and knowledge. Back up first if you have active runs.

### 1. Back up (optional)

```bash
cp -r "$ATLAS_DATA_DIR" ~/atlas-data-backup/
cp -r "$ATLAS_KNOWLEDGE_DIR" ~/atlas-knowledge-backup/
```

### 2. Remove data directories

```bash
rm -rf "$ATLAS_DATA_DIR"
rm -rf "$ATLAS_KNOWLEDGE_DIR"
```

### 3. Remove from IDE

#### Claude Code
```bash
rm -f .claude/agents/atlas-*.md
rm -rf .claude/skills/atlas-*-playbook
rm -f .claude/rules/atlas-*.md
```

#### OpenCode
```bash
rm -f .opencode/agents/atlas-*.md
rm -rf .opencode/skills/atlas-*-playbook
rm -f .opencode/rules/atlas-*.md
```

#### VS Code / Copilot
```bash
rm -f .github/copilot-instructions.md
rm -f .github/agents/atlas-*.md
```

#### Cursor
```bash
rm -f .cursor/rules/atlas-*.md
rm -f .cursor/agents/atlas-*.md
```

#### Windsurf / Antigravity
```bash
rm -f .windsurf/rules/atlas-*.md
rm -f .windsurf/agents/atlas-*.md
```

### 4. Remove environment variables

Remove from your shell profile (`~/.bashrc`, `~/.zshrc`, `~/.config/fish/config.fish`):

```bash
unset ATLAS_DATA_DIR
unset ATLAS_KNOWLEDGE_DIR
```

### 5. Verify cleanup

```bash
# Should return "No such file" for both
ls "$ATLAS_DATA_DIR" 2>&1
ls "$ATLAS_KNOWLEDGE_DIR" 2>&1
```

> **For AI agents:** When asked to uninstall Atlas, execute steps 2-4 in order. Skip step 1 unless user requests backup. Step 5 confirms removal. If any `rm` fails with "No such file", that component was not installed — continue.
