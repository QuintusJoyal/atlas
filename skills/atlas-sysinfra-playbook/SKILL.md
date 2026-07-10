---
name: atlas-sysinfra-playbook
description: Systems methodology for atlas-sysinfra: hardening, virtualization, and operations. Use when atlas-sysinfra runs.
disable-model-invocation: true
---

# Systems and infrastructure playbook

Standards: CIS Benchmarks, OS and server hardening, virtualization best practices.

## Hardening
Apply CIS Benchmarks for the OS. Minimal install, patched, least privilege, disabled unused services, audited access.

## Virtualization and capacity
Right-size resources. Isolate workloads. Plan capacity and failure domains.

## Operations
Backups, monitoring, log shipping, and a recovery procedure. Document the runbook with atlas-docs.

## Systems artifact
Configuration, hardening steps, operational notes. Persist to `$ATLAS_DATA_DIR/runs/<run-id>/sysinfra.md`.

## References
- https://www.cisecurity.org/cis-benchmarks
