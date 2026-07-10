---
name: raid-log-management
load-when: Tracking risks, managing issues, logging assumptions and dependencies
skip-when: Project planning (see pmbok-framework), risk-based testing (see risk-based-testing)
---

# RAID Log Management

## Quick Reference
- **R**isks: what could go wrong
- **A**ssumptions: what we believe to be true
- **I**ssues: what's currently wrong
- **D**ependencies: what we need from others
- Update regularly, review in team meetings
- Assign owners and deadlines to every item

## Deep Dive

### RAID Log Format
```markdown
## Risks
| ID | Description | Probability | Impact | Mitigation | Owner | Status |
|----|-------------|-------------|--------|------------|-------|--------|
| R1 | Key developer leaves | Low | High | Cross-training, documentation | PM | Open |

## Assumptions
| ID | Description | Validated | Impact if Wrong | Owner |
|----|-------------|-----------|-----------------|-------|
| A1 | API will be ready by Sprint 3 | No | 2-week delay | BA |

## Issues
| ID | Description | Impact | Resolution | Owner | Deadline |
|----|-------------|--------|------------|-------|----------|
| I1 | Database performance degradation | High | Index optimization | Dev | 2024-02-15 |

## Dependencies
| ID | Description | Dependent On | Status | Owner |
|----|-------------|--------------|--------|-------|
| D1 | Third-party API credentials | Vendor | Pending | DevOps |
```

### Risk Response Strategies
- **Avoid**: eliminate the risk
- **Mitigate**: reduce probability or impact
- **Transfer**: shift to another party (insurance, outsource)
- **Accept**: acknowledge and prepare contingency

### Assumption Validation
1. List all assumptions
2. Identify which are unvalidated
3. Plan validation activities
4. Update assumptions based on findings

### Issue vs Risk
- **Issue**: happening now, needs resolution
- **Risk**: might happen, needs mitigation plan

## See Also
- **pmbok-framework** — Project management context
- **risk-based-testing** — Testing based on risk assessment
- **raci-matrix** — Role assignment for RAID items
- **quality-gates** — Gate criteria include RAID review
