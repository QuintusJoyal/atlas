#!/usr/bin/env python3
"""Validate a handoff artifact against schemas.

Usage:
    python3 scripts/validate-handoff.py <handoff.json> [--schema <schema-path>]

If --schema not specified, it will infer based on variant field.
"""

import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("jsonschema package not installed; skipping validation", file=sys.stderr)
    sys.exit(0)


def load_schema(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-handoff.py <handoff.json> [--schema <schema>]", file=sys.stderr)
        sys.exit(1)
    handoff_path = Path(sys.argv[1])
    schema_path = None
    for i, a in enumerate(sys.argv[2:], 2):
        if a == '--schema' and i + 1 < len(sys.argv):
            schema_path = Path(sys.argv[i + 1])

    with open(handoff_path) as f:
        handoff = json.load(f)

    if schema_path is None:
        variant = handoff.get('variant', 'full')
        root = Path(__file__).resolve().parent.parent
        if variant == 'small':
            schema_path = root / 'schemas' / 'handoffs' / 'small.json'
        else:
            role = handoff.get('role')
            if role:
                schema_path = root / 'schemas' / 'handoffs' / f'{role}.json'
            if not schema_path or not schema_path.exists():
                schema_path = root / 'schemas' / 'handoffs' / 'base.json'

    schema = load_schema(schema_path)
    try:
        jsonschema.validate(instance=handoff, schema=schema)
        print(f"OK: {handoff_path} validates against {schema_path.name}")
        sys.exit(0)
    except jsonschema.ValidationError as e:
        print(f"ERROR: {handoff_path} fails validation against {schema_path.name}", file=sys.stderr)
        print(f"  {e.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: validation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
