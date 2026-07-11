---
name: toc of contents for developer experience
description: Internal developer platforms, service catalogs, golden paths, developer productivity. Load when building or improving developer tooling.
load-when: task mentions developer experience, IDP, service catalog, golden path, Backstage, or developer productivity
skip-when: task is about application code, infrastructure, or non-developer-tooling work
---

# Developer experience

Developer experience (DX) is how fast and safely developers can deliver value. Good DX compounds. Bad DX compounds faster.

## Quick Reference

Internal Developer Platform (IDP): self-service infrastructure that abstracts away operational complexity. Provides golden paths (opinionated workflows) and paved roads (supported alternatives).

Service catalog: centralized registry of all services, their owners, docs, and status. Backstage is the leading open-source platform.

Golden paths: opinionated, pre-configured workflows for common tasks (create service, deploy, test). Not mandatory, but using them is easier than alternatives.

Developer productivity metrics: DORA metrics (deployment frequency, lead time, change failure rate, time to restore) plus developer satisfaction and cognitive load.

## Deep Dive

### Internal Developer Platform
- **Self-service provisioning:** developers create infrastructure without tickets. Namespace, database, CI/CD pipeline via API or UI.
- **Golden paths:** pre-built templates for new services, libraries, and pipelines. Reduces decision fatigue.
- **Paved roads:** supported alternatives to golden paths. Documented, maintained, but less convenient.
- **Abstraction layers:** hide infrastructure complexity (Kubernetes, networking, storage) behind simple interfaces.

### Service catalog (Backstage)
- **Service overview:** name, description, owner, repository, CI/CD, dependencies.
- **TechDocs:** auto-generated documentation from code (MkDocs, Docusaurus).
- **API documentation:** auto-discovered from code (OpenAPI, protobuf).
- **Scorecards:** compliance checks (security, documentation, testing coverage).
- **Plugins:** extend with cost analysis, K8s visualization, PagerDuty integration.

### Golden path examples
- **New service:** scaffold with CI/CD, monitoring, and documentation pre-configured.
- **New feature:** branch strategy, testing checklist, deployment pipeline.
- **Incident response:** runbook template, escalation contacts, postmortem template.

### Measuring DX
- **DORA metrics:** deployment frequency, lead time for changes, change failure rate, time to restore service.
- **Developer satisfaction:** surveys, NPS scores, qualitative feedback.
- **Cognitive load:** how much mental effort is required to complete common tasks.
- **Time to first commit:** how long until a new developer is productive.

### Common DX problems
- **Too many choices:** no clear recommended path. Developers waste time deciding.
- **Documentation drift:** docs out of date. Developers stop trusting them.
- **Environment inconsistency:** dev/staging/prod behave differently. "Works on my machine."
- **Tool fragmentation:** different tools for different teams. No shared platform.

## See Also
- `k/google-sre-practices.md` for reliability practices
- `k/dora-metrics.md` for DORA metrics details
- `k/gitops-principles.md` for deployment practices
- `k/clean-code-practices.md` for code quality
