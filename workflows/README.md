# Workflow presets

atlas-lead picks a preset to right-size the pipeline. Each preset lists its phases, roles, approval gates, and a Definition of Done per gate. Unknown task shapes fall back to `feature`. The user can override the preset at any time.

| Preset | When to use |
| --- | --- |
| feature | Net-new work, full pipeline with all three gates |
| bugfix | Defects and hotfixes, fast lane, single final gate |
| data-project | Data or analytics work, pulls the data roles |
| infra-change | Infrastructure, network, or cloud changes |
| security-audit | Read-only security and compliance assessment |
| discovery | Consulting: scope and proposal, no build |

Gates pause for user sign-off. A gate cannot pass until its Definition of Done is met.
