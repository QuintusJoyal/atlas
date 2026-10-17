#!/usr/bin/env python3
"""Deterministic security guardrails engine for Atlas.

Runtime enforcement for the security controls Atlas documents. Permissions,
injection detection, credential scoping, the audit trail, and compliance
reports are evaluated as code, not by the agent being restricted.

Usage:
    python3 scripts/guardrails.py check --role R --phase P --tool T [--args JSON]
    python3 scripts/guardrails.py check --role R --phase P --tool mcp__srv__write --approved
    python3 scripts/guardrails.py scan --text "..." [--file PATH]
    python3 scripts/guardrails.py vault add --id NAME --role R --phase P [--tool T]  # secret on stdin
    python3 scripts/guardrails.py vault get --id NAME --role R --phase P [--tool T]
    python3 scripts/guardrails.py vault revoke-phase --phase P
    python3 scripts/guardrails.py vault list
    python3 scripts/guardrails.py audit verify [--audit PATH]
    python3 scripts/guardrails.py report [--audit PATH] [--format md|json] [--out PATH]

Global options:
    --policy PATH   policy file (default guardrails/policy.yaml, .json supported)
    --audit PATH    audit log (default $ATLAS_DATA_DIR/runs/<run-id>/guardrails.jsonl)
    --run-id ID     run identifier (default $ATLAS_RUN_ID or "local")
    --vault PATH    credential vault (default $ATLAS_DATA_DIR/guardrails/vault.json)

Exit codes:
    0 = allowed / clean / verified
    1 = denied / flagged / verification failed
    2 = usage error
"""

import argparse
import fnmatch
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_POLICY = ROOT / "guardrails" / "policy.yaml"
GENESIS_HASH = "0" * 64
TOOL_ALIASES = {"readfile": "read", "read_file": "read", "writefile": "write",
                "editfile": "edit", "shell": "bash", "run": "bash"}


# --------------------------------------------------------------------------
# Minimal YAML subset parser (stdlib only; JSON is loaded natively).
# Supports nested maps by indentation, block/flow lists, flow maps, quoted and
# plain scalars, booleans, null, numbers, and # comments outside quotes.
# --------------------------------------------------------------------------

def _strip_comment(line):
    out = []
    quote = None
    prev = ""
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            out.append(ch)
        elif ch == "#" and (prev == "" or prev.isspace()):
            break
        else:
            out.append(ch)
        prev = ch
    return "".join(out).rstrip()


def _unquote(s):
    if len(s) >= 2 and s[0] == s[-1] == "'":
        return s[1:-1].replace("''", "'")
    if len(s) >= 2 and s[0] == s[-1] == '"':
        body = s[1:-1]
        parts = []
        i = 0
        while i < len(body):
            if body[i] == "\\" and i + 1 < len(body):
                nxt = body[i + 1]
                parts.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(nxt, "\\" + nxt))
                i += 2
            else:
                parts.append(body[i])
                i += 1
        return "".join(parts)
    return s


def _split_top(s, sep=","):
    parts = []
    depth = 0
    quote = None
    cur = []
    for ch in s:
        if quote:
            cur.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            cur.append(ch)
        elif ch in "[{":
            depth += 1
            cur.append(ch)
        elif ch in "]}":
            depth -= 1
            cur.append(ch)
        elif ch == sep and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if "".join(cur).strip():
        parts.append("".join(cur).strip())
    return parts


def _parse_scalar(s):
    s = s.strip()
    if not s:
        return None
    if s[0] == "{" and s[-1:] == "}":
        return _parse_flow_map(s[1:-1])
    if s[0] == "[" and s[-1:] == "]":
        return [_parse_scalar(p) for p in _split_top(s[1:-1])]
    if (s[0] == s[-1] == "'") or (s[0] == s[-1] == '"'):
        return _unquote(s)
    low = s.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "~"):
        return None
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def _parse_flow_map(body):
    result = {}
    for part in _split_top(body):
        if ":" not in part:
            continue
        key, _, val = part.partition(":")
        key = _unquote(key.strip()) if key.strip()[:1] in ("'", '"') else key.strip()
        result[key] = _parse_scalar(val)
    return result


def _parse_block(lines, idx, indent):
    if idx >= len(lines):
        return None, idx
    if lines[idx][1].startswith("- "):
        items = []
        while idx < len(lines):
            ind, content = lines[idx]
            if ind < indent or not content.startswith("- "):
                break
            items.append(_parse_scalar(content[2:]))
            idx += 1
        return items, idx
    mapping = {}
    while idx < len(lines):
        ind, content = lines[idx]
        if ind < indent or ":" not in content:
            break
        key, _, rest = content.partition(":")
        key = _unquote(key.strip()) if key.strip()[:1] in ("'", '"') else key.strip()
        rest = rest.strip()
        idx += 1
        if rest:
            mapping[key] = _parse_scalar(rest)
        elif idx < len(lines) and lines[idx][0] > indent:
            mapping[key], idx = _parse_block(lines, idx, lines[idx][0])
        elif idx < len(lines) and lines[idx][0] == indent and lines[idx][1].startswith("- "):
            mapping[key], idx = _parse_block(lines, idx, indent)
        else:
            mapping[key] = None
    return mapping, idx


def parse_yaml(text):
    lines = []
    for raw in text.splitlines():
        cleaned = _strip_comment(raw)
        if not cleaned.strip():
            continue
        lines.append((len(cleaned) - len(cleaned.lstrip(" ")), cleaned.strip()))
    value, _ = _parse_block(lines, 0, lines[0][0] if lines else 0)
    return value if value is not None else {}


def load_policy(path):
    text = Path(path).read_text(encoding="utf-8")
    if str(path).endswith(".json"):
        return json.loads(text)
    return parse_yaml(text)


# --------------------------------------------------------------------------
# Audit trail: append-only JSONL with a SHA-256 hash chain.
# --------------------------------------------------------------------------

def _canonical(event):
    return json.dumps(event, sort_keys=True, separators=(",", ":"))


def _chain_hash(event):
    return hashlib.sha256((event.get("prevHash", GENESIS_HASH) + _canonical(event)).encode("utf-8")).hexdigest()


def _last_hash(path):
    if not path.is_file():
        return GENESIS_HASH
    last = GENESIS_HASH
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                last = json.loads(line).get("hash", last)
            except json.JSONDecodeError:
                pass
    return last


def append_audit(path, event):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    event["seq"] = existing.count("\n") + 1
    event["ts"] = datetime.now(timezone.utc).isoformat()
    event["prevHash"] = _last_hash(path)
    event["hash"] = _chain_hash(event)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")
    os.chmod(path, 0o600)
    return event["hash"]


def verify_chain(path):
    path = Path(path)
    issues = []
    prev = GENESIS_HASH
    count = 0
    if not path.is_file():
        return count, issues
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        count += 1
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            issues.append(f"line {lineno}: not valid JSON")
            continue
        stored = event.pop("hash", None)
        if event.get("prevHash") != prev:
            issues.append(f"line {lineno}: broken chain link")
        if stored != _chain_hash(event):
            issues.append(f"line {lineno}: tampered event (hash mismatch)")
        prev = stored or prev
    return count, issues


# --------------------------------------------------------------------------
# Paths and defaults
# --------------------------------------------------------------------------

def data_dir():
    return Path(os.environ.get("ATLAS_DATA_DIR", str(Path.home() / ".atlas")))


def audit_path(args):
    if args.audit:
        return Path(args.audit)
    run_id = args.run_id or os.environ.get("ATLAS_RUN_ID") or "local"
    return data_dir() / "runs" / run_id / "guardrails.jsonl"


def vault_path(args):
    return Path(args.vault) if args.vault else data_dir() / "guardrails" / "vault.json"


def run_id(args):
    return args.run_id or os.environ.get("ATLAS_RUN_ID") or "local"


# --------------------------------------------------------------------------
# Permission policy engine
# --------------------------------------------------------------------------

def normalize_tool(name):
    base = name.strip().lower()
    if base.startswith("functions."):
        base = base.split(".", 1)[1]
    return TOOL_ALIASES.get(base, base)


def is_mcp(policy, tool):
    return any(tool.startswith(p) for p in policy.get("mcp", {}).get("prefixes", ["mcp__"]))


def mcp_is_write(policy, tool, tool_args):
    indicators = policy.get("mcp", {}).get("writeIndicators", [])
    haystack = (tool + " " + json.dumps(tool_args)).lower()
    return any(ind in haystack for ind in indicators)


def first_path_arg(tool, tool_args):
    for key in ("file_path", "path", "filePath", "file", "directory", "dir"):
        if isinstance(tool_args.get(key), str):
            return tool_args[key]
    return None


def check_path(policy, path_value):
    """Return None if allowed, else a reason string."""
    rules = policy.get("pathPolicy", {})
    cwd = Path.cwd()
    candidate = Path(path_value)
    resolved = (cwd / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    try:
        rel = str(resolved.relative_to(cwd))
    except ValueError:
        rel = str(resolved)
    forms = [rel.replace(os.sep, "/"), path_value.replace(os.sep, "/")]
    for pattern in rules.get("deny", []):
        if any(fnmatch.fnmatch(f, pattern) for f in forms):
            return f"path '{path_value}' matches denied scope '{pattern}'"
    if not any(str(resolved).startswith(str((cwd / root).resolve())) for root in rules.get("allow", ["."])):
        return f"path '{path_value}' is outside the allowed scopes"
    return None


def evaluate(policy, role, phase, tool, tool_args, approved):
    """Return (decision, reason, suggested_action, context)."""
    mcp = is_mcp(policy, tool)
    if mcp and policy.get("mcp", {}).get("writeRequiresApproval", True) and mcp_is_write(policy, tool, tool_args):
        if not approved:
            return ("deny",
                    f"MCP write action '{tool}' requires explicit approval",
                    "Obtain human approval (T2/T3), then re-run with --approved.",
                    {"tool": tool, "mcp": True})
        return "allow", f"MCP write '{tool}' approved", "Proceed; action is audit-logged.", {"tool": tool, "mcp": True}

    role_cfg = policy.get("roles", {}).get(role, {})
    deny_list = [normalize_tool(t) for t in role_cfg.get("deny", [])]
    only_list = [normalize_tool(t) for t in role_cfg.get("only", [])] if role_cfg.get("only") else None
    allow_list = [normalize_tool(t) for t in role_cfg.get("allow", [])]

    if role_cfg and only_list is not None and tool not in only_list:
        return ("deny",
                f"role '{role}' is restricted to {only_list}",
                f"Delegate this action to a role scoped for '{tool}'.",
                {"role": role, "tool": tool})
    if tool in deny_list:
        return ("deny",
                f"role '{role}' may never use '{tool}'",
                f"Delegate to a role permitted to use '{tool}' (escalate T2 if needed).",
                {"role": role, "tool": tool})

    if tool not in allow_list:
        phases = policy.get("phases", {})
        if phase not in phases:
            return ("deny",
                    f"unknown phase '{phase}'",
                    "Use a declared phase: " + ", ".join(sorted(phases)) + ".",
                    {"phase": phase})
        state = phases[phase].get(tool)
        if state is None:
            return ("deny",
                    f"tool '{tool}' is not declared for phase '{phase}'",
                    "Escalate to atlas-lead to expand the phase scope or delegate.",
                    {"phase": phase, "tool": tool})
        if state == "deny":
            return ("deny",
                    f"tool '{tool}' is forbidden in phase '{phase}'",
                    "Escalate to atlas-lead (T2) with justification, or wait for a permitting phase.",
                    {"phase": phase, "tool": tool})
        if state == "readonly" and tool == "bash":
            command = str(tool_args.get("command", ""))
            patterns = policy.get("shellReadonly", [])
            if not any(re.search(p, command) for p in patterns):
                return ("deny",
                        f"bash in phase '{phase}' is read-only; command '{command[:80]}' is not on the allowlist",
                        "Request full bash scope via escalation, or run a read-only command.",
                        {"phase": phase, "command": command})

    if policy.get("tools", {}).get(tool, {}).get("path"):
        target = first_path_arg(tool, tool_args)
        if target:
            reason = check_path(policy, target)
            if reason:
                return ("deny", reason,
                        "Choose a path inside the allowed scope; never touch secrets or VCS metadata.",
                        {"tool": tool, "path": target})

    return "allow", f"'{tool}' permitted for role '{role}' in phase '{phase}'", "Proceed.", \
        {"role": role, "phase": phase, "tool": tool}


def structured_error(message, suggested, context):
    return {
        "error": True,
        "errorCategory": "permission",
        "recoverable": False,
        "message": message,
        "suggestedAction": suggested,
        "context": context,
    }


def cmd_check(args):
    policy = load_policy(args.policy)
    tool = normalize_tool(args.tool)
    try:
        tool_args = json.loads(args.args) if args.args else {}
    except json.JSONDecodeError as exc:
        print(f"ERROR: --args is not valid JSON: {exc}", file=sys.stderr)
        return 2
    decision, reason, suggested, context = evaluate(policy, args.role, args.phase, tool, tool_args, args.approved)
    path = audit_path(args)
    event = {
        "action": "tool.check",
        "runId": run_id(args),
        "role": args.role,
        "phase": args.phase,
        "tool": tool,
        "decision": decision,
        "reason": reason,
        "toolInput": tool_args if tool_args else None,
    }
    event_hash = append_audit(path, event)
    if decision == "allow":
        print(json.dumps({"decision": "allow", "tool": tool, "role": args.role,
                          "phase": args.phase, "reason": reason,
                          "auditEventHash": event_hash}, indent=2))
        return 0
    error = structured_error(reason, suggested, context)
    error["auditEventHash"] = event_hash
    print(json.dumps(error, indent=2))
    return 1


# --------------------------------------------------------------------------
# Prompt injection scanner
# --------------------------------------------------------------------------

def shannon_entropy(value):
    if not value:
        return 0.0
    counts = Counter(value)
    length = len(value)
    return -sum((n / length) * math.log2(n / length) for n in counts.values())


def scan_text(policy, text):
    findings = []
    for name, pattern in policy.get("injection", {}).get("patterns", {}).items():
        for match in re.finditer(pattern, text):
            findings.append({"type": "pattern", "name": name, "match": match.group(0)[:120]})
    min_len = policy.get("injection", {}).get("minTokenLength", 20)
    min_entropy = policy.get("injection", {}).get("minEntropy", 4.5)
    for token in re.findall(r"[A-Za-z0-9+/=_-]{%d,}" % min_len, text):
        entropy = shannon_entropy(token)
        if entropy >= min_entropy:
            findings.append({"type": "entropy", "name": "high-entropy-blob",
                             "entropy": round(entropy, 2), "match": token[:60] + "..."})
    return findings


def cmd_scan(args):
    policy = load_policy(args.policy)
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.text is not None:
        text = args.text
    else:
        text = sys.stdin.read()
    findings = scan_text(policy, text)
    verdict = "flagged" if findings else "clean"
    path = audit_path(args)
    event = {"action": "injection.scan", "runId": run_id(args), "role": args.role,
             "verdict": verdict, "findingCount": len(findings), "findings": findings}
    event_hash = append_audit(path, event)
    print(json.dumps({"verdict": verdict, "findings": findings, "auditEventHash": event_hash}, indent=2))
    return 1 if findings else 0


# --------------------------------------------------------------------------
# MCP credential vault
# --------------------------------------------------------------------------

def load_vault(path):
    if Path(path).is_file():
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return {"version": 1, "credentials": {}}


def save_vault(path, vault):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(vault, indent=2) + "\n", encoding="utf-8")
    os.chmod(path, 0o600)


def _scope_matches(entry, role, phase, tool):
    if entry.get("revoked"):
        return False, "revoked at phase boundary"
    if entry.get("roles") and role not in entry["roles"]:
        return False, f"not scoped to role '{role}'"
    if entry.get("phases") and phase not in entry["phases"]:
        return False, f"not scoped to phase '{phase}'"
    if entry.get("tools") and tool not in entry["tools"]:
        return False, f"not scoped to tool '{tool}'"
    return True, "in scope"


def cmd_vault(args):
    path = vault_path(args)
    vault = load_vault(path)
    scope = {"roles": args.role or [], "phases": args.phase or [], "tools": args.tool or []}

    if args.vault_action == "add":
        if not any(scope.values()):
            print("ERROR: at least one --role, --phase, or --tool scope is required", file=sys.stderr)
            return 2
        secret = sys.stdin.read().strip()
        if not secret:
            print("ERROR: no secret provided on stdin", file=sys.stderr)
            return 2
        entry = dict(scope)
        entry["value"] = secret
        entry["created"] = datetime.now(timezone.utc).isoformat()
        entry["revoked"] = None
        vault["credentials"][args.id] = entry
        save_vault(path, vault)
        append_audit(audit_path(args), {"action": "vault.add", "runId": run_id(args), "role": args.role,
                                        "credentialId": args.id, "scopes": scope, "decision": "allow"})
        print(f"stored credential '{args.id}' scoped to {scope}")
        return 0

    if args.vault_action == "get":
        if not args.role or not args.phase:
            print("ERROR: vault get requires --role and --phase for scope enforcement", file=sys.stderr)
            return 2
        role, phase = args.role[-1], args.phase[-1]
        tool = args.tool[-1] if args.tool else None
        entry = vault["credentials"].get(args.id)
        if entry is None:
            print(json.dumps(structured_error(f"unknown credential '{args.id}'",
                                              "Add it with 'vault add' before use.",
                                              {"credentialId": args.id}), indent=2))
            return 1
        ok, why = _scope_matches(entry, role, phase, tool)
        append_audit(audit_path(args), {"action": "vault.get", "runId": run_id(args), "role": role,
                                        "phase": phase, "credentialId": args.id,
                                        "decision": "allow" if ok else "deny", "reason": why})
        if not ok:
            print(json.dumps(structured_error(f"credential '{args.id}' denied: {why}",
                                              "Request a credential scoped to your role and phase.",
                                              {"credentialId": args.id, "role": role, "phase": phase}), indent=2))
            return 1
        sys.stdout.write(entry["value"] + "\n")
        return 0

    if args.vault_action == "revoke-phase":
        if not args.phase:
            print("ERROR: revoke-phase requires --phase", file=sys.stderr)
            return 2
        boundary = args.phase[-1]
        revoked = 0
        for cid, entry in vault["credentials"].items():
            if not entry.get("revoked") and (not entry.get("phases") or boundary in entry["phases"]):
                entry["revoked"] = datetime.now(timezone.utc).isoformat()
                entry["revokedReason"] = f"phase boundary: {boundary}"
                revoked += 1
                append_audit(audit_path(args), {"action": "vault.revoke", "runId": run_id(args),
                                                "credentialId": cid, "phase": boundary,
                                                "decision": "revoke"})
        save_vault(path, vault)
        print(f"revoked {revoked} credential(s) at boundary of phase '{boundary}'")
        return 0

    if args.vault_action == "list":
        for cid, entry in sorted(vault["credentials"].items()):
            status = "revoked" if entry.get("revoked") else "active"
            print(f"{cid}\t{status}\troles={entry.get('roles')}\tphases={entry.get('phases')}\ttools={entry.get('tools')}")
        return 0
    return 2


# --------------------------------------------------------------------------
# Audit verification and compliance report
# --------------------------------------------------------------------------

def cmd_audit(args):
    path = Path(args.audit) if args.audit else audit_path(args)
    count, issues = verify_chain(path)
    print("Atlas Guardrails Audit Chain")
    print("=" * 50)
    print(f"log: {path}")
    print(f"events: {count}")
    if issues:
        print(f"FAILED: {len(issues)} integrity issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    print("OK: hash chain intact; no tampering detected")
    return 0


def build_report(path):
    events = []
    if Path(path).is_file():
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    _, issues = verify_chain(path)
    decisions = Counter(e.get("decision", "n/a") for e in events if "decision" in e)
    by_role = Counter(e.get("role", "unknown") for e in events if e.get("action") == "tool.check")
    by_tool = Counter(e.get("tool", "unknown") for e in events if e.get("action") == "tool.check")
    violations = [e for e in events if e.get("decision") in ("deny", "revoke")]
    flags = [e for e in events if e.get("verdict") == "flagged"]
    report = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "log": str(path),
        "chainIntact": not issues,
        "chainIssues": issues,
        "eventCount": len(events),
        "toolChecks": sum(by_role.values()),
        "decisions": dict(decisions),
        "byRole": dict(by_role),
        "byTool": dict(by_tool),
        "violations": violations,
        "injectionFlags": flags,
        "controls": {
            "access-control": "A01 / AC-* — tool permission decisions",
            "logging": "A09 / AU-* — append-only hash-chained audit trail",
            "injection": "A03 / LLM01 — prompt injection and encoded-payload scans",
            "secrets": "A02 — scoped MCP credential injection and phase revocation",
        },
    }
    return report


def render_markdown(report):
    lines = ["# Atlas Guardrails Compliance Report", ""]
    lines.append(f"- Generated: {report['generatedAt']}")
    lines.append(f"- Audit log: `{report['log']}`")
    lines.append(f"- Audit chain intact: {'yes' if report['chainIntact'] else 'NO'}")
    lines.append(f"- Events: {report['eventCount']} ({report['toolChecks']} tool checks)")
    lines.append("")
    lines.append("## Decisions")
    for key, value in sorted(report["decisions"].items()):
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Tool checks by role")
    for key, value in sorted(report["byRole"].items()):
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Violations")
    if report["violations"]:
        for event in report["violations"]:
            lines.append(f"- [{event.get('ts', '?')}] {event.get('action')} "
                         f"{event.get('tool', event.get('credentialId', ''))}: {event.get('reason', event.get('decision'))}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Injection flags")
    if report["injectionFlags"]:
        for event in report["injectionFlags"]:
            lines.append(f"- [{event.get('ts', '?')}] {event.get('findingCount')} finding(s)")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Control mapping")
    for control, detail in report["controls"].items():
        lines.append(f"- {control}: {detail}")
    lines.append("")
    return "\n".join(lines)


def cmd_report(args):
    path = Path(args.audit) if args.audit else audit_path(args)
    report = build_report(path)
    output = json.dumps(report, indent=2) if args.format == "json" else render_markdown(report)
    if args.out:
        Path(args.out).write_text(output + "\n", encoding="utf-8")
        print(f"wrote {args.format} report to {args.out}")
    else:
        print(output)
    return 0 if report["chainIntact"] else 1


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(description="Atlas deterministic security guardrails engine")
    parser.add_argument("--policy", default=str(DEFAULT_POLICY), help="policy file (.yaml or .json)")
    parser.add_argument("--audit", default=None, help="audit log path")
    parser.add_argument("--run-id", default=None, help="run identifier")
    parser.add_argument("--vault", default=None, help="credential vault path")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="pre-invocation tool permission check")
    check.add_argument("--role", required=True)
    check.add_argument("--phase", required=True)
    check.add_argument("--tool", required=True)
    check.add_argument("--args", default=None, help="tool arguments as a JSON object")
    check.add_argument("--approved", action="store_true", help="human approval for MCP writes")
    check.set_defaults(func=cmd_check)

    scan = sub.add_parser("scan", help="scan text for prompt injection")
    scan.add_argument("--text", default=None)
    scan.add_argument("--file", default=None)
    scan.add_argument("--role", default="unknown")
    scan.set_defaults(func=cmd_scan)

    vault = sub.add_parser("vault", help="scoped MCP credential vault")
    vault.add_argument("vault_action", choices=["add", "get", "revoke-phase", "list"])
    vault.add_argument("--id", default=None)
    vault.add_argument("--role", action="append", default=[])
    vault.add_argument("--phase", action="append", default=[])
    vault.add_argument("--tool", action="append", default=[])
    vault.set_defaults(func=cmd_vault)

    audit = sub.add_parser("audit", help="audit trail operations")
    audit.add_argument("audit_action", choices=["verify"])
    audit.set_defaults(func=cmd_audit)

    report = sub.add_parser("report", help="compliance attestation from the audit trail")
    report.add_argument("--format", choices=["md", "json"], default="md")
    report.add_argument("--out", default=None)
    report.set_defaults(func=cmd_report)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "vault" and args.vault_action in ("add", "get") and not args.id:
        parser.error("--id is required for vault add/get")
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
