---
name: stride-threat-modeling
load-when: Designing security architecture, threat assessment, security review
skip-when: Quick vulnerability list (see owasp-top-10), detailed controls (see owasp-asvs)
---

# STRIDE Threat Modeling

## Quick Reference
- Spoofing: pretending to be someone else
- Tampering: modifying data or code
- Repudiation: denying actions without proof
- Information Disclosure: exposing data to unauthorized parties
- Denial of Service: making system unavailable
- Elevation of Privilege: gaining unauthorized access
- Apply STRIDE per element: each system component gets checked against all 6 categories

## Deep Dive

### STRIDE Per Element
| Threat | Element | Question |
|--------|---------|----------|
| Spoofing | Entry points | Can someone impersonate a legitimate user? |
| Tampering | Data flows | Can data be modified in transit? |
| Repudiation | Trust boundaries | Can someone deny performing an action? |
| Information Disclosure | Data stores | Can data be exposed to unauthorized parties? |
| Denial of Service | Processing | Can the service be made unavailable? |
| Elevation of Privilege | Privilege boundaries | Can someone gain higher access? |

### Process
1. **Decompose the system**: identify components, data flows, trust boundaries
2. **Apply STRIDE per element**: for each component, ask all 6 questions
3. **Rate threats**: use DREAD or risk matrix (probability × impact)
4. **Determine mitigations**: design controls for high-rated threats
5. **Document**: record threats, ratings, and mitigations in a threat model

### DREAD Rating
| Factor | Description |
|--------|-------------|
| Damage | How bad if exploited? |
| Reproducibility | How easy to reproduce? |
| Exploitability | How easy to exploit? |
| Affected users | How many impacted? |
| Discoverability | How easy to find? |

### Threat Model Artifacts
- Data flow diagrams (DFDs) showing components and data flows
- Threat list with STRIDE categories and DREAD ratings
- Mitigation plan with assigned owners
- Residual risk acceptance decisions

### When to Threat Model
- Before implementing new features with security implications
- When integrating external services or APIs
- After major architecture changes
- During security reviews and audits

### Agentic Threat Patterns
For multi-agent or LLM-driven systems, layer these onto STRIDE (see `knowledge/security/owasp-agentic-top-10.md`):
| STRIDE | Agentic Pattern |
|--------|-----------------|
| Spoofing | Identity Spoofing (AG03) — role claims in free text, forged agent/user identity |
| Tampering | Tool Poisoning (AG02), Memory Poisoning (AG04), Goal Manipulation (AG01) |
| Repudiation | Escalation bypass (AG07) — model-forged approvals without out-of-band audit |
| Information Disclosure | Action Confidentiality Breach (AG10) — secrets in tool args, traces, artifacts |
| Denial of Service | Unintended Execution (AG06) — untrusted input triggers runaway tool calls |
| Elevation of Privilege | Dynamic Agent Chaining (AG08), Agentic Supply Chain (AG05) |

## See Also
- **owasp-top-10** — Quick vulnerability list mapped to STRIDE categories
- **owasp-agentic-top-10** — Threats specific to multi-agent and autonomous AI systems
- **owasp-asvs** — Detailed security controls for mitigations
- **nist-800-53-controls** — Security control families
- **architecture-decision-records** — Documenting security design decisions
