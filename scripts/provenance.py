#!/usr/bin/env python3
"""Transitive context provenance: sign, verify, and trace context fragments.

A context fragment is a signed record of content handed between Atlas roles.
Each fragment carries its source agent, a SHA-256 content hash, and the
`parent_hash` of the fragment it derives from, forming a hash chain back to
the fragment's origin. Agents sign fragments with a per-agent HMAC-SHA256 key
stored in `$ATLAS_DATA_DIR/keys/`. Every operation appends an audit record to
the append-only log at `$ATLAS_DATA_DIR/provenance.jsonl`.

Signatures attest *which agent emitted a fragment*, not that its content is
true — a compromised agent can re-sign distorted content. Treat the chain as
an attribution and debugging aid, not a truth proof.

Usage:
    python3 scripts/provenance.py init-key --agent atlas-dev
    python3 scripts/provenance.py sign --agent atlas-dev --file handoff.md \
        [--parent <content_hash>] [--run <run-id>] [--out fragment.json]
    python3 scripts/provenance.py verify --fragment fragment.json [--content handoff.md]
    python3 scripts/provenance.py trace --fragment <content_hash> | --run <run-id>
    python3 scripts/provenance.py check-distortion --original orig.md --compacted sum.md

Exit code: 0 on success (verify: valid chain), 1 on failure (invalid
signature, hash mismatch, or broken chain — fragment is quarantined).
"""

import argparse
import difflib
import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "atlas-provenance/1"
DATA_DIR = Path(os.environ.get("ATLAS_DATA_DIR", Path.home() / ".atlas"))
KEYS_DIR = DATA_DIR / "keys"
AUDIT_LOG = DATA_DIR / "provenance.jsonl"
QUARANTINE_DIR = DATA_DIR / "quarantine"


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def key_path(agent: str) -> Path:
    if not agent.replace("-", "").replace("_", "").isalnum():
        raise SystemExit(f"invalid agent name: {agent!r}")
    return KEYS_DIR / f"{agent}.key"


def signing_payload(fragment: dict) -> bytes:
    lines = [
        fragment["source_agent"],
        fragment.get("run_id", ""),
        fragment["timestamp"],
        fragment["content_hash"],
        fragment.get("parent_hash") or "",
    ]
    return "\n".join(lines).encode("utf-8")


def append_audit(record: dict):
    record.setdefault("ts", utc_now())
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


def load_audit_log():
    if not AUDIT_LOG.exists():
        return []
    entries = []
    with open(AUDIT_LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def signed_fragments():
    return {
        e["fragment"]["content_hash"]: e["fragment"]
        for e in load_audit_log()
        if e.get("event") == "sign" and "fragment" in e
    }


def cmd_init_key(args) -> int:
    path = key_path(args.agent)
    if path.exists() and not args.force:
        print(f"key exists: {path}", file=sys.stderr)
        return 1
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    secret = os.urandom(32).hex()
    path.write_text(secret + "\n", encoding="utf-8")
    os.chmod(path, 0o600)
    print(f"key created: {path}")
    return 0


def cmd_sign(args) -> int:
    path = key_path(args.agent)
    if not path.exists():
        print(f"no key for {args.agent}; run init-key first", file=sys.stderr)
        return 1
    secret = path.read_text(encoding="utf-8").strip()
    if args.file:
        content = Path(args.file).read_bytes()
    else:
        content = sys.stdin.buffer.read()
    fragment = {
        "schema": SCHEMA,
        "source_agent": args.agent,
        "run_id": args.run or "",
        "timestamp": utc_now(),
        "content_hash": sha256_hex(content),
        "parent_hash": args.parent or None,
    }
    fragment["signature"] = hmac.new(
        secret.encode("utf-8"), signing_payload(fragment), hashlib.sha256
    ).hexdigest()
    fragment["key_id"] = args.agent
    append_audit(
        {
            "event": "sign",
            "fragment_hash": fragment["content_hash"],
            "source_agent": args.agent,
            "run_id": fragment["run_id"],
            "parent_hash": fragment["parent_hash"],
            "fragment": fragment,
        }
    )
    text = json.dumps(fragment, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


def verify_fragment(fragment: dict, content: bytes | None):
    """Return (checks dict, problems list)."""
    checks = {"hash_valid": None, "signature_valid": False, "chain_valid": None}
    problems = []

    if content is not None:
        checks["hash_valid"] = sha256_hex(content) == fragment.get("content_hash")
        if not checks["hash_valid"]:
            problems.append("content hash mismatch")

    key = key_path(fragment.get("source_agent", ""))
    if key.exists():
        secret = key.read_text(encoding="utf-8").strip()
        expected = hmac.new(
            secret.encode("utf-8"), signing_payload(fragment), hashlib.sha256
        ).hexdigest()
        checks["signature_valid"] = hmac.compare_digest(
            expected, fragment.get("signature", "")
        )
        if not checks["signature_valid"]:
            problems.append("signature invalid")
    else:
        problems.append(f"no key for agent {fragment.get('source_agent')!r}")

    parent = fragment.get("parent_hash")
    if parent is None:
        checks["chain_valid"] = True
    else:
        checks["chain_valid"] = parent in signed_fragments()
        if not checks["chain_valid"]:
            problems.append(f"parent fragment {parent[:12]}… not found in audit log")

    return checks, problems


def quarantine(fragment: dict, problems):
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    out = QUARANTINE_DIR / f"{fragment.get('content_hash', 'unknown')}.json"
    out.write_text(
        json.dumps({"quarantined_at": utc_now(), "problems": problems,
                    "fragment": fragment}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out


def cmd_verify(args) -> int:
    fragment = json.loads(Path(args.fragment).read_text(encoding="utf-8"))
    content = Path(args.content).read_bytes() if args.content else None
    checks, problems = verify_fragment(fragment, content)
    ok = not problems
    append_audit(
        {
            "event": "verify",
            "fragment_hash": fragment.get("content_hash"),
            "source_agent": fragment.get("source_agent"),
            "run_id": fragment.get("run_id"),
            "parent_hash": fragment.get("parent_hash"),
            "status": "verified" if ok else "quarantined",
            **checks,
        }
    )
    if ok:
        print(json.dumps({"status": "verified", **checks}, sort_keys=True))
        return 0
    out = quarantine(fragment, problems)
    print(f"QUARANTINED: {'; '.join(problems)} -> {out}", file=sys.stderr)
    return 1


def cmd_trace(args) -> int:
    frags = signed_fragments()
    if args.run:
        chain = [f for f in frags.values() if f.get("run_id") == args.run]
        chain.sort(key=lambda f: f["timestamp"])
    elif args.fragment:
        target = args.fragment
        if target not in frags:
            prefix = [h for h in frags if h.startswith(target)]
            if len(prefix) != 1:
                print(f"fragment {target!r} not found in audit log", file=sys.stderr)
                return 1
            target = prefix[0]
        chain = []
        seen = set()
        while target and target in frags and target not in seen:
            seen.add(target)
            frag = frags[target]
            chain.append(frag)
            target = frag.get("parent_hash")
        chain.reverse()
    else:
        print("provide --fragment or --run", file=sys.stderr)
        return 1

    if not chain:
        print("no fragments found", file=sys.stderr)
        return 1

    verifies = {
        e["fragment_hash"]: e["status"]
        for e in load_audit_log()
        if e.get("event") == "verify"
    }
    print(f"{'FRAGMENT':14} {'SOURCE_AGENT':18} {'TIMESTAMP':21} PARENT        STATUS")
    for frag in chain:
        parent = frag.get("parent_hash") or "-"
        print(
            f"{frag['content_hash'][:12]} {frag['source_agent']:18} "
            f"{frag['timestamp']:21} {parent[:12]:13} "
            f"{verifies.get(frag['content_hash'], 'unverified')}"
        )
    return 0


def cmd_check_distortion(args) -> int:
    original = Path(args.original).read_text(encoding="utf-8")
    compacted = Path(args.compacted).read_text(encoding="utf-8")
    original_hash = sha256_hex(original.encode("utf-8"))
    compacted_hash = sha256_hex(compacted.encode("utf-8"))
    if original_hash == compacted_hash:
        severity, ratio = "none", 1.0
    else:
        ratio = difflib.SequenceMatcher(None, original, compacted).ratio()
        severity = "low" if ratio >= 0.9 else "medium" if ratio >= 0.5 else "high"
    record = {
        "event": "distortion",
        "original_hash": original_hash,
        "compacted_hash": compacted_hash,
        "severity": severity,
        "similarity": round(ratio, 4),
        "status": "mismatch" if severity != "none" else "match",
    }
    append_audit(record)
    print(json.dumps(record, sort_keys=True))
    return 0 if severity in ("none", "low") else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init-key", help="create a per-agent signing key")
    p.add_argument("--agent", required=True)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init_key)

    p = sub.add_parser("sign", help="sign a context fragment")
    p.add_argument("--agent", required=True)
    p.add_argument("--file", help="content file (default: stdin)")
    p.add_argument("--parent", help="content_hash of the parent fragment")
    p.add_argument("--run", help="run-id the fragment belongs to")
    p.add_argument("--out", help="write fragment JSON here (default: stdout)")
    p.set_defaults(func=cmd_sign)

    p = sub.add_parser("verify", help="verify a fragment's hash, signature, and chain")
    p.add_argument("--fragment", required=True)
    p.add_argument("--content", help="original content to re-hash")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("trace", help="trace a fragment chain back to its source")
    p.add_argument("--fragment", help="content_hash (or unique prefix)")
    p.add_argument("--run", help="list all fragments for a run-id")
    p.set_defaults(func=cmd_trace)

    p = sub.add_parser("check-distortion", help="compare original vs compacted content")
    p.add_argument("--original", required=True)
    p.add_argument("--compacted", required=True)
    p.set_defaults(func=cmd_check_distortion)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
