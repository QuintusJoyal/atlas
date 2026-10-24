---
name: schemas
description: JSON Schemas for handoffs and validation contracts.
---

# Schemas

This directory contains JSON Schema definitions for structured, typed handoffs across all Atlas roles.

## Structure

- `handoffs/` - Schema definitions for each role's handoff artifacts
  - `base-handoff.schema.json` - Base schema for all handoffs
  - `{role}.schema.json` - Role-specific schemas extending the base schema
- `lite/` - Lite mode schema definitions
  - `handoff-lite.schema.json` - Subset schema for small variant (4-section format)

## Schema Versioning

All schemas include `schemaVersion` for forward compatibility. Schema versioning follows semantic versioning principles.

## Validation

Schema validation is deterministic and runs before LLM-based quality evaluation at gate checks. Both JSON and legacy markdown handoffs are accepted during the transition period for backward compatibility.

## Usage

Schemas are referenced by `rules/handoff-protocol.md` and validated by gate checking logic.
