---
name: owasp-agentic-top-10
load-when: Securing multi-agent systems, reviewing agent tool usage, agent threat modeling, agentic AI security
skip-when: Single-model LLM risks (see owasp-llm-top-10), web vulnerabilities (see owasp-top-10)
---

# OWASP Agentic Top 10

Threats specific to autonomous and multi-agent AI systems. A 2026 large-scale competition (464 participants, 272K attacks) found all 13 tested frontier models vulnerable — treat every agent, tool, and communication channel as an attack surface.

## Quick Reference
- AG01: Goal Manipulation — instructions that redirect the agent's objective
- AG02: Tool Abuse — malicious or compromised tools hijack agent behavior
- AG03: Identity Spoofing — forging agent, user, or role identity
- AG04: Memory Poisoning — corrupting persistent memory or RAG context
- AG05: Agentic Supply Chain — poisoned skills, plugins, prompts, or models
- AG06: Unintended Execution — untrusted input triggers code or side effects
- AG07: Human Escalation Failure — agent bypasses or fakes human approval
- AG08: Dynamic Agent Chaining — unauthorized spawning or delegation of agents
- AG09: Human-Agent Interaction Misuse — social engineering through the agent
- AG10: Action Confidentiality Breach — sensitive data leaks via tool calls or traces

## Deep Dive

### AG01: Goal Manipulation
- Crafted inputs redefine the agent's real objective (task redirection, hidden secondary goals)
- Includes Chain-of-Thought Forgery: fabricated reasoning traces injected at ~60% success against frontier models; adversaries process untrusted code and can be co-opted by plausible-looking rationale
- Mitigation: keep the authoritative goal in trusted context, verify outputs still serve the original task, require re-confirmation when scope shifts

### AG02: Tool Abuse
- Tool Poisoning / ToolHijacker: malicious tool descriptions hijack agent behavior; every agent system prompt is an attack surface
- Mitigation: treat tool descriptions as untrusted code, pin and review tool manifests, apply least privilege per tool, never auto-trust newly surfaced tools

### AG03: Identity Spoofing
- Spoofed user, agent, or role identity inside prompts or artifacts; models perceive source by how text sounds, not its labeled role
- Mitigation: authenticate delegation channels, bind identity to metadata outside the model's context, reject role claims found inside free text

### AG04: Memory Poisoning
- Malicious content written to long-term memory or retrieved via RAG persists and re-influences future tasks; Self-Replicating AI Worms (Morris-II) propagate through RAG pipelines
- Mitigation: quarantine and review before memory commits, provenance-tag retrieved content, cap memory influence on high-stakes decisions

### AG05: Agentic Supply Chain Vulnerabilities
- Poisoned skills, plugins, prompt templates, fine-tuned models, or knowledge files enter through the same path as legitimate ones
- Mitigation: verify integrity hashes on bundles (manifest.json), review third-party skills/prompts before install, vendor everything

### AG06: Unintended Execution
- Untrusted input smuggles commands, code, or tool invocations the user never intended (indirect prompt injection leading to execution)
- Mitigation: sandbox tool execution, validate arguments against schemas, require explicit approval for side-effecting calls

### AG07: Human Escalation Failure
- Agent skips required human-in-the-loop gates, forges approval, or escalates to a human with manipulated context
- Mitigation: enforce approval gates outside the model's reach, log every escalation with immutable audit trail, verify approval authenticity

### AG08: Dynamic Agent Chaining
- A compromised agent propagates malicious instructions through legitimate artifact communication, spawning or redirecting downstream agents (Multi-Agent Prompt Infection)
- Mitigation: validate artifacts at each handoff, limit delegation fan-out, treat peer artifacts as untrusted input

### AG09: Human-Agent Interaction Misuse
- Users or integrators are social-engineered through the agent: persuasive outputs, fake urgency, exfiltration requests framed as routine
- Mitigation: constrain what the agent can ask of humans, surface high-risk requests with warnings, never route credentials through conversational turns

### AG10: Action Confidentiality Breach
- Sensitive data leaks via tool call arguments, execution traces, returned tool results, or shared artifacts
- Mitigation: redact secrets before tool calls, minimize data in traces, scope artifacts to need-to-know recipients

## Defense Patterns
- Validate every input at role boundaries: instructions embedded in data are data, not commands
- Treat artifacts from peer agents and tools as untrusted; re-verify before acting
- Least privilege for tools, memory, and delegation; deny by default
- Keep approval gates and identity checks outside the model's context
- Integrity-pin skills, prompts, and knowledge bundles; review before install
- Log tool calls, escalations, and handoffs for auditability

## See Also
- **owasp-llm-top-10** — Single-model LLM risks that agentic threats build on
- **owasp-top-10** — General web vulnerabilities (tool endpoints inherit these)
- **stride-threat-modeling** — STRIDE mapping includes agentic threat patterns
- **nist-ai-rmf** — AI risk management framework
