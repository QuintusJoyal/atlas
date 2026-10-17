#!/usr/bin/env python3
"""Validate least-privilege attenuation in Atlas delegation.

Usage:
    # Check one spawn: delegatee scope must be a strict subset of the delegator's
    python3 scripts/validate-delegation.py --delegator "Read,Grep,Glob,Write" \
                                           --delegatee "Read,Grep,Glob"

    # Check a full chain record: field completeness, parent links, unique ids,
    # and strict attenuation on every spawn/grant edge; prints the reconstructed
    # authorization paths (who authorized what, upon whose authority)
    python3 scripts/validate-delegation.py --chain $ATLAS_DATA_DIR/runs/<run-id>/delegation-chain.jsonl

Attenuation rule (knowledge/process/delegation-authority.md):
    scope(delegatee) subset-of scope(delegator), and never equal or greater.
    A `Tool:read-only` entry is attenuated relative to full `Tool`; the reverse
    is an escalation, not attenuation.

Chain record: append-only JSONL, one edge per spawn/escalate/grant/revoke.
spawn and grant edges carry a scope and must be strictly attenuated from their
parent edge; escalate and revoke edges carry no scope. Root edges (parent null)
originate with the principal and are not attenuated against anything.

Exit code: 0 = clean, 1 = violations or malformed record
"""

import argparse
import json
import sys
from pathlib import Path

ACTIONS = {"spawn", "escalate", "grant", "revoke"}
SCOPE_BEARING = {"spawn", "grant"}
REQUIRED_FIELDS = ("ts", "id", "action", "principal", "delegator", "delegate", "parent", "scope", "authorizedBy")

# Higher number = more permissive.
MODE_PERMISSIVENESS = {"read-only": 0, "full": 1}


def parse_scope(text_or_list):
    """Normalize a scope into a set of (base_tool, mode) tuples.

    Accepts a comma/space-separated string or a list of entries.
    Bare tool names mean full mode; `Tool:read-only` (or `Tool:ro`) means read-only.
    """
    if isinstance(text_or_list, str):
        raw = [part for chunk in text_or_list.split(",") for part in chunk.split()]
    else:
        raw = list(text_or_list)
    scope = set()
    for entry in raw:
        entry = str(entry).strip()
        if not entry:
            continue
        if ":" in entry:
            base, _, mode = entry.partition(":")
            mode = "read-only" if mode.lower() in ("read-only", "ro") else "full"
        else:
            base, mode = entry, "full"
        scope.add((base.lower(), mode))
    return scope


def contains(delegator, delegatee_entry):
    """True when the delegator's scope covers delegatee_entry (equal or fuller mode)."""
    base, mode = delegatee_entry
    for d_base, d_mode in delegator:
        if d_base == base and MODE_PERMISSIVENESS[d_mode] >= MODE_PERMISSIVENESS[mode]:
            return True
    return False


def check_attenuation(delegator_scope, delegatee_scope, label=""):
    """Return a list of violation messages for one delegation edge."""
    violations = []
    for entry in sorted(delegatee_scope):
        if not contains(delegator_scope, entry):
            violations.append(f"{label}delegatee tool '{entry[0]}:{entry[1]}' is not in the delegator's scope")
    if not violations:
        # Strictness: fail when the delegatee covers every delegator entry at equal
        # permissiveness (equal or greater), even though containment held.
        if all(contains(delegatee_scope, entry) for entry in delegator_scope):
            violations.append(
                f"{label}delegated scope is not attenuated (equal to or broader than the delegator's scope)"
            )
    return violations


def load_chain(path):
    """Parse the JSONL chain record; returns (edges, parse_errors)."""
    edges, errors = [], []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            edges.append((lineno, json.loads(line)))
        except json.JSONDecodeError as exc:
            errors.append(f"line {lineno}: invalid JSON ({exc})")
    return edges, errors


def validate_chain(edges):
    """Structural + attenuation checks over the ordered edge list."""
    violations = []
    by_id = {}

    for lineno, edge in edges:
        missing = [f for f in REQUIRED_FIELDS if f not in edge]
        if missing:
            violations.append(f"line {lineno}: missing required field(s): {', '.join(missing)}")
            continue
        if edge["action"] not in ACTIONS:
            violations.append(f"line {lineno} ({edge['id']}): unknown action '{edge['action']}'")
        if not isinstance(edge["scope"], list):
            violations.append(f"line {lineno} ({edge['id']}): scope must be a list")
        if edge["id"] in by_id:
            violations.append(f"line {lineno} ({edge['id']}): duplicate edge id")
        by_id[edge["id"]] = edge

    for lineno, edge in edges:
        if any(f not in edge for f in REQUIRED_FIELDS):
            continue
        parent_id = edge["parent"]
        parent = by_id.get(parent_id) if parent_id is not None else None
        if parent_id is not None and parent is None:
            violations.append(f"line {lineno} ({edge['id']}): parent '{parent_id}' not found in record")
            continue
        if parent is not None and parent["id"] == edge["id"]:
            violations.append(f"line {lineno} ({edge['id']}): edge cannot be its own parent")
            continue
        # Principals are inherited from the root of the chain.
        if parent is None:
            if edge["principal"] != edge["delegator"]:
                violations.append(
                    f"line {lineno} ({edge['id']}): root edge must have principal == delegator "
                    f"(got '{edge['principal']}' != '{edge['delegator']}')"
                )
        elif edge["principal"] != parent.get("principal"):
            violations.append(
                f"line {lineno} ({edge['id']}): principal '{edge['principal']}' does not match "
                f"parent's principal '{parent.get('principal')}'"
            )
        # Scope-bearing edges must be strictly attenuated from their parent edge.
        if edge["action"] in SCOPE_BEARING:
            if parent is None:
                continue  # root authority originates with the principal; nothing to attenuate against
            if parent["action"] not in SCOPE_BEARING:
                violations.append(
                    f"line {lineno} ({edge['id']}): {edge['action']} parent '{parent_id}' is a "
                    f"'{parent['action']}' edge and carries no authority to delegate from"
                )
                continue
            parent_scope = parse_scope(parent["scope"])
            edge_scope = parse_scope(edge["scope"])
            violations.extend(
                check_attenuation(parent_scope, edge_scope, label=f"line {lineno} ({edge['id']}): ")
            )
        else:
            if edge["scope"]:
                violations.append(
                    f"line {lineno} ({edge['id']}): '{edge['action']}' edges must carry an empty scope"
                )
    return violations


def reconstruct(edges):
    """Print each delegate's authorization path from the principal down."""
    by_id = {e["id"]: e for _, e in edges if "id" in e}
    print("\nAuthorization paths (who authorized what, upon whose authority):")
    for _, edge in edges:
        if "id" not in edge or edge.get("action") not in SCOPE_BEARING:
            continue
        path, cursor = [], edge
        while cursor is not None:
            scope_txt = ",".join(f"{b}:{m}" if m != "full" else b for b, m in sorted(parse_scope(cursor.get("scope", []))))
            path.append(f"{cursor['delegator']} --[{cursor['id']}]--> {cursor['delegate']} [{scope_txt}]")
            parent_id = cursor.get("parent")
            cursor = by_id.get(parent_id) if parent_id is not None else None
        print(f"  {'  '.join(reversed(path))}")


def main():
    parser = argparse.ArgumentParser(description="Validate Atlas delegation attenuation and chain records")
    parser.add_argument("--delegator", help="delegator's scope, e.g. 'Read,Grep,Write,Bash'")
    parser.add_argument("--delegatee", help="delegated scope, e.g. 'Read,Grep'")
    parser.add_argument("--chain", help="path to a delegation-chain.jsonl record")
    args = parser.parse_args()

    if not args.delegator and not args.chain:
        parser.error("provide --delegator/--delegatee for a single-edge check, or --chain for a chain record")

    issues = 0

    if args.delegator is not None or args.delegatee is not None:
        if args.delegator is None or args.delegatee is None:
            parser.error("--delegator and --delegatee must be provided together")
        print("Atlas Delegation Attenuation Check")
        print("=" * 50)
        violations = check_attenuation(parse_scope(args.delegator), parse_scope(args.delegatee))
        if violations:
            print(f"FAILED: {len(violations)} violation(s):")
            for v in violations:
                print(f"  - {v}")
            issues += len(violations)
        else:
            print("OK: delegated scope is a strict subset of the delegator's scope")

    if args.chain:
        path = Path(args.chain)
        print(f"\nAtlas Delegation Chain Record ({path})")
        print("=" * 50)
        if not path.is_file():
            print(f"FAILED: chain record not found: {path}")
            issues += 1
        else:
            edges, parse_errors = load_chain(path)
            for err in parse_errors:
                print(f"  - {err}")
            issues += len(parse_errors)
            violations = validate_chain(edges)
            if violations:
                print(f"FAILED: {len(violations)} violation(s):")
                for v in violations:
                    print(f"  - {v}")
                issues += len(violations)
            else:
                spawns = sum(1 for _, e in edges if e.get("action") in SCOPE_BEARING)
                print(f"OK: {len(edges)} edge(s), {spawns} scope-bearing, all strictly attenuated")
                reconstruct(edges)

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
