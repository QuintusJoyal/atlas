---
name: toc of contents for TOGAF framework
description: TOGAF Architecture Development Method (ADM), Enterprise Continuum, and Architecture Content Framework. Load when enterprise architecture tasks reference TOGAF.
load-when: task mentions TOGAF, ADM, enterprise architecture framework, or architecture governance
skip-when: task is purely technical or implementation-focused
---

# TOGAF framework

TOGAF (The Open Group Architecture Framework) is a proven enterprise architecture methodology. Version 10 integrates with other Open Group standards.

## Quick Reference

TOGAF ADM cycle: Preliminary → Vision → Business Architecture → Information Systems Architecture → Technology Architecture → Opportunities & Solutions → Migration Planning → Implementation Governance → Architecture Change Management. Requirements Management runs continuously through all phases.

Enterprise Continuum: Foundation → Common Systems → Industry → Organization-specific. Classifies architecture artifacts from generic to specific.

Architecture Content Framework: defines the deliverables (Artifacts + Building Blocks) produced at each ADM phase. Key artifacts: Baseline/Target Architecture Documents, Gap Analysis, Transition Plan, Architecture Requirements Specification.

Governance: Architecture Board reviews and approves changes. Architecture Contracts govern implementation. Architecture Compliance assessments verify alignment.

## Deep Dive

### ADM Phases (detailed)

**Preliminary Phase**: Establish architecture capability. Define principles, select tools, establish governance.

**Phase A - Architecture Vision**: Define scope, constraints, expectations. Create Architecture Vision document. Obtain approval.

**Phase B - Business Architecture**: Describe baseline and target business architecture. Analyze gaps. Identify candidate roadmap components.

**Phase C - Information Systems Architecture**: Data Architecture + Application Architecture. Define logical and physical data models. Map application components.

**Phase D - Technology Architecture**: Define baseline and target technology platforms. Map applications and data to technology components.

**Phase E - Opportunities & Solutions**: Identify delivery vehicles (projects). Perform cost/benefit analysis. Define rollback approach.

**Phase F - Migration Planning**: Create detailed implementation and migration plan. Confirm benefits, costs, risks. Prioritize work packages.

**Phase G - Implementation Governance**: Architecture contracts for implementation projects. Monitor compliance. Manage architecture-related issues.

**Phase H - Architecture Change Management**: Establish change management process. Monitor technology and business changes. Trigger re-architecture when needed.

### Enterprise Continuum
The Enterprise Continuum provides a taxonomy for architecture artifacts:
- **Foundation Architectures**: generic models, reference architectures
- **Common Systems Architectures**: industry-standard patterns
- **Industry Architectures**: sector-specific reference models
- **Organization-Specific Architectures**: your actual architectures

### Architecture Content Framework
Standard deliverables at each ADM phase:
- Architecture Vision (Phase A)
- Business, Data, Application, Technology Architecture Documents (Phases B-D)
- Architecture Requirements Specification
- Gap Analysis (comparing baseline to target)
- Transition Architecture (intermediate states)
- Implementation Plan (Phase F)
- Architecture Contract (Phase G)

### Governance
- **Architecture Board**: decision-making body for architecture changes
- **Architecture Contracts**: agreements between developers and architects
- **Compliance Assessments**: verify implementations match architecture
- **Architecture Skills Framework**: defines competency levels

## See Also
- `k/architecture-decision-records.md` for capturing individual decisions
- `k/c4-model.md` for architecture visualization
- `k/trade-off-analysis.md` for evaluating alternatives
- `k/solid-principles.md` for design principles
