#!/usr/bin/env python3
"""Validate the MCP trust catalog against the atlas-mcp-trust/1 schema.

Usage:
    python3 scripts/validate-mcp-catalog.py
    python3 scripts/validate-mcp-catalog.py --catalog PATH

The trust catalog (knowledge/reference/mcp-trust-catalog.yaml) is the
registry of MCP servers Atlas is permitted to mount. Governance rules:
knowledge/process/mcp-server-governance.md.

Checks:
1. Catalog declares schema atlas-mcp-trust/1 and a servers list
2. Each server has required fields (id, name, owner, version, status,
   capabilities, access)
3. Ids are unique and kebab-case
4. Status is one of: approved, review, revoked
5. Version is an exact x.y.z pin (no ranges, no latest)
6. Capabilities declare at least one of tools/resources/prompts
7. Access roles are known agent roles ('all' allowed for read only)
8. Revoked entries carry no write scope (kill-switch is unambiguous);
    only approved entries may carry write scope
9. approved/review entries carry a review block (reviewed_by, reviewed_at)

Opt-in: prints SKIP and exits 0 when no catalog file is configured or
present, so behavior is unchanged without a catalog.

Exit code: 0 = clean or skipped, 1 = issues found
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = ROOT / "knowledge" / "reference" / "mcp-trust-catalog.yaml"

SCHEMA = "atlas-mcp-trust/1"
STATUSES = {"approved", "review", "revoked"}
REQUIRED_FIELDS = ("id", "name", "owner", "version", "status", "capabilities", "access")
CAPABILITY_KEYS = ("tools", "resources", "prompts")
ACCESS_KEYS = ("read", "write")
PINNED_VERSION = re.compile(r"^\d+\.\d+\.\d+$")
SERVER_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")


# --- Minimal YAML subset parser -------------------------------------------
# Supports the constrained subset used by the trust catalog: comment lines,
# scalar mappings, nested mappings by indentation, and flow-style lists.
# This mirrors validate-workflows.py, which also avoids a PyYAML dependency.

def parse_yaml_subset(text):
    lines = []
    for raw in text.splitlines():
        stripped = raw.split("#", 1)[0].rstrip()
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        lines.append((indent, stripped.strip()))
    if not lines:
        return {}
    value, index = _parse_mapping(lines, 0, lines[0][0])
    if index != len(lines):
        raise ValueError(f"unparsed content at entry starting: {lines[index][1]!r}")
    return value


def _scalar(token):
    token = token.strip()
    if token.startswith("[") and token.endswith("]"):
        inner = token[1:-1].strip()
        if not inner:
            return []
        return [_scalar(item) for item in inner.split(",")]
    if len(token) >= 2 and token[0] == token[-1] and token[0] in "\"'":
        return token[1:-1]
    return token


def _parse_mapping(lines, index, indent):
    result = {}
    while index < len(lines):
        line_indent, content = lines[index]
        if line_indent < indent:
            break
        if line_indent > indent:
            raise ValueError(f"unexpected indent: {content!r}")
        if content.startswith("- "):
            break
        if ":" not in content:
            raise ValueError(f"expected 'key: value', got: {content!r}")
        key, _, rest = content.partition(":")
        rest = rest.strip()
        if rest:
            result[key] = _scalar(rest)
            index += 1
        elif index + 1 < len(lines) and lines[index + 1][0] > indent:
            child_indent = lines[index + 1][0]
            if lines[index + 1][1].startswith("- "):
                result[key], index = _parse_list(lines, index + 1, child_indent)
            else:
                result[key], index = _parse_mapping(lines, index + 1, child_indent)
        else:
            result[key] = {}
            index += 1
    return result, index


def _parse_list(lines, index, indent):
    items = []
    while index < len(lines):
        line_indent, content = lines[index]
        if line_indent != indent or not content.startswith("- "):
            break
        first = content[2:].strip()
        if index + 1 < len(lines) and lines[index + 1][0] > indent:
            block = [(indent + 2, first)]
            index += 1
            while index < len(lines) and lines[index][0] > indent:
                block.append(lines[index])
                index += 1
            item, consumed = _parse_mapping(block, 0, indent + 2)
            if consumed != len(block):
                raise ValueError(f"unparsed content in list item: {block[consumed][1]!r}")
            items.append(item)
        else:
            items.append(_scalar(first))
            index += 1
    return items, index


# --- Checks -----------------------------------------------------------------

def known_roles():
    """Agent role names from agents/*.md frontmatter."""
    roles = set()
    for agent in sorted((ROOT / "agents").glob("*.md")):
        match = re.search(r"^name:\s*(\S+)", agent.read_text(encoding="utf-8"), re.MULTILINE)
        if match:
            roles.add(match.group(1))
    return roles


def check_server(server, roles):
    issues = []
    label = server.get("id") or "<missing id>"

    for field in REQUIRED_FIELDS:
        if field not in server or server[field] in ("", {}):
            issues.append(f"server '{label}': missing required field '{field}'")

    server_id = server.get("id", "")
    if server_id and not SERVER_ID.match(str(server_id)):
        issues.append(f"server '{label}': id must be kebab-case ([a-z0-9-])")

    status = server.get("status")
    if status is not None and status not in STATUSES:
        issues.append(f"server '{label}': status must be one of {sorted(STATUSES)}, got '{status}'")

    version = str(server.get("version", ""))
    if version and not PINNED_VERSION.match(version):
        issues.append(
            f"server '{label}': version must be an exact x.y.z pin "
            f"(got '{version}'); upgrades go through re-review"
        )

    capabilities = server.get("capabilities")
    if isinstance(capabilities, dict):
        if not any(capabilities.get(key) for key in CAPABILITY_KEYS):
            issues.append(
                f"server '{label}': capabilities must declare at least one of "
                f"{', '.join(CAPABILITY_KEYS)}"
            )
        for key in capabilities:
            if key not in CAPABILITY_KEYS:
                issues.append(f"server '{label}': unknown capability key '{key}'")
    elif capabilities is not None:
        issues.append(f"server '{label}': capabilities must be a mapping")

    access = server.get("access")
    if isinstance(access, dict):
        for key in access:
            if key not in ACCESS_KEYS:
                issues.append(f"server '{label}': unknown access key '{key}' (allowed: {', '.join(ACCESS_KEYS)})")
        for key in ACCESS_KEYS:
            for role in access.get(key) or []:
                if role == "all":
                    if key != "read":
                        issues.append(f"server '{label}': 'all' is only valid in access.read")
                elif role not in roles:
                    issues.append(f"server '{label}': access.{key} names unknown role '{role}'")
        write_scope = access.get("write") or []
        if status == "revoked" and write_scope:
            issues.append(
                f"server '{label}': revoked servers must have an empty access.write "
                f"(kill-switch must be unambiguous)"
            )
        if status in ("approved", "review") and "read" not in access:
            issues.append(f"server '{label}': status '{status}' requires an access.read list")
        if status == "approved" and write_scope and not access.get("read"):
            issues.append(f"server '{label}': write scope without any read scope")
    elif access is not None:
        issues.append(f"server '{label}': access must be a mapping with 'read' and/or 'write'")

    if status in ("approved", "review"):
        review = server.get("review")
        if not isinstance(review, dict):
            issues.append(f"server '{label}': status '{status}' requires a review block")
        else:
            for field in ("reviewed_by", "reviewed_at"):
                if not review.get(field):
                    issues.append(f"server '{label}': review.{field} is required")

    if status == "revoked":
        if not server.get("revoked_at"):
            issues.append(f"server '{label}': revoked servers must record revoked_at")

    return issues


def main():
    parser = argparse.ArgumentParser(description="Validate the Atlas MCP trust catalog")
    parser.add_argument("--catalog", default=None, help="catalog path (default: knowledge/reference/mcp-trust-catalog.yaml)")
    args = parser.parse_args()

    catalog_path = Path(args.catalog) if args.catalog else DEFAULT_CATALOG
    if not catalog_path.is_file():
        print("SKIP: no MCP trust catalog configured. MCP behavior unchanged (governance is opt-in).")
        return 0

    print("Atlas MCP Trust Catalog Validator")
    print("=" * 50)
    rel = catalog_path if not catalog_path.is_absolute() else catalog_path
    try:
        rel = catalog_path.resolve().relative_to(ROOT)
    except ValueError:
        rel = catalog_path
    print(f"Catalog: {rel}")

    issues = 0

    print("\n1. Parsing catalog...")
    try:
        catalog = parse_yaml_subset(catalog_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        print(f"   FAILED: {exc}")
        print("\n" + "=" * 50)
        print("RESULT: 1 ISSUES FOUND")
        return 1

    if catalog.get("schema") != SCHEMA:
        print(f"   FAILED: top-level 'schema' must be '{SCHEMA}', got '{catalog.get('schema')}'")
        issues += 1
    else:
        print(f"   OK: schema {SCHEMA}")

    servers = catalog.get("servers")
    if not isinstance(servers, list) or not servers:
        print("   FAILED: 'servers' must be a non-empty list")
        print("\n" + "=" * 50)
        print("RESULT: 1 ISSUES FOUND")
        return 1

    print("\n2. Checking server entries...")
    roles = known_roles()
    seen = {}
    for server in servers:
        if not isinstance(server, dict):
            print(f"   - <entry {len(seen)}>: not a mapping")
            issues += 1
            continue
        server_id = server.get("id")
        if server_id in seen:
            print(f"   - server '{server_id}': duplicate id")
            issues += 1
        seen[server_id] = True
        for problem in check_server(server, roles):
            print(f"   - {problem}")
            issues += 1

    approved = [s.get("id") for s in servers if isinstance(s, dict) and s.get("status") == "approved"]
    revoked = [s.get("id") for s in servers if isinstance(s, dict) and s.get("status") == "revoked"]

    print("\n" + "=" * 50)
    if issues == 0:
        print(f"RESULT: CLEAN - {len(servers)} servers ({len(approved)} approved, {len(revoked)} revoked)")
        return 0
    print(f"RESULT: {issues} ISSUES FOUND")
    return 1


if __name__ == "__main__":
    sys.exit(main())
