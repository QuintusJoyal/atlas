---
name: anti-patterns
load-when: Diagnosing failures, reviewing practices, identifying common mistakes
skip-when: Specific patterns (see testing-pyramid, solid-principles, google-sre-practices)
---

# Anti-Patterns

## Quick Reference
- Common solutions that seem right but are wrong
- Each anti-pattern has: name, symptom, problem, solution
- Use to diagnose team and code issues
- Prevention is better than cure
- Document anti-patterns to prevent recurrence

## Deep Dive

### Testing Anti-Patterns
| Anti-Pattern | Symptom | Solution |
|--------------|---------|----------|
| Ice cream cone | All E2E, no unit tests | Build up unit test base |
| Flaky tests | Tests fail intermittently | Fix test isolation |
| Coverage gaming | High coverage, low quality | Focus on mutation testing |
| Testing after implementation | Tests written to pass, not to find bugs | Adopt TDD |
| Testing the wrong thing | Tests verify implementation, not behavior | Test outcomes, not methods |

### Architecture Anti-Patterns
| Anti-Pattern | Symptom | Solution |
|--------------|---------|----------|
| Golden hammer | Using one tool for everything | Evaluate alternatives per use case |
| Big ball of mud | No clear structure | Refactor to modules, define boundaries |
| Vendor lock-in | Can't switch providers | Use abstractions, avoid proprietary APIs |
| Resume-driven development | Choosing tech for résumé, not project | Choose boring technology |
| Over-engineering | Building for scale you don't need | YAGNI (You Ain't Gonna Need It) |

### Deployment Anti-Patterns
| Anti-Pattern | Symptom | Solution |
|--------------|---------|----------|
| No rollback plan | Can't recover from bad deploy | Automated rollback, feature flags |
| Big bang deployment | Large, risky releases | Continuous deployment, small batches |
| Manual deployment | Human error, slow process | Automate with CI/CD |
| No monitoring | Deploy and hope | Observability, alerting, dashboards |
| Skip staging | Test in production | Maintain staging environment |

### Data Anti-Patterns
| Anti-Pattern | Symptom | Solution |
|--------------|---------|----------|
| No schema evolution | Breaking changes to data models | Version schemas, backward compatibility |
| Missing lineage | Can't trace data origins | Data catalog, lineage tracking |
| Silent failures | Data pipelines fail silently | Alerting, validation, monitoring |
| No data quality | Bad data in, bad data out | Great Expectations, validation |
| God table | One massive table | Normalize, partition, shard |

### Communication Anti-Patterns
| Anti-Pattern | Symptom | Solution |
|--------------|---------|----------|
| Bicycle shed | Arguing about trivial details | Timebox decisions, escalate |
| Design by committee | No decisions made | Assign decision owner |
| Not invented here | Rejecting external solutions | Evaluate objectively |
| Information hoarding | Knowledge silos | Document, share, cross-train |

## See Also
- **testing-pyramid** — Correct testing approach
- **solid-principles** — Correct design approach
- **google-sre-practices** — Correct operations approach
- **itil-incident-management** — Correct incident response
