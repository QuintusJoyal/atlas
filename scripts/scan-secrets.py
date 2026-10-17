#!/usr/bin/env python3
"""Scan Atlas bundle files and run artifacts for leaked secrets.

Usage:
    python3 scripts/scan-secrets.py                     # bundle files + $ATLAS_DATA_DIR/runs/
    python3 scripts/scan-secrets.py --staged            # pre-commit: only staged changes
    python3 scripts/scan-secrets.py --dir DIR [DIR...]  # extra directories to scan
    python3 scripts/scan-secrets.py --skip-runs         # bundle files only
    python3 scripts/scan-secrets.py --update-baseline   # allowlist current findings

Scans tracked bundle files (agents, rules, skills, workflows, knowledge,
examples, scripts, CI configs) with provider-specific patterns (AWS, GCP,
GitHub, OpenAI, Anthropic, Slack, private keys, generic credential
assignments) plus a Shannon-entropy check for high-entropy strings.

Findings are classified and redacted: the matched secret is never echoed,
only a masked preview and a SHA-256 fingerprint. Known-safe placeholders
are allowlisted in .secrets.baseline, keyed by file plus secret hash.

Exit code: 0 = clean, 1 = secrets found
"""

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / ".secrets.baseline"
MAX_FILE_BYTES = 2 * 1024 * 1024

# (rule_id, description, pattern, priority). Lower priority wins overlaps;
# provider-specific rules come before the generic assignment rule.
RULES = [
    ("aws-access-key-id", "AWS access key ID",
     re.compile(r"\b(?:AKIA|ASIA|AIDA|AROA)[0-9A-Z]{16}\b"), 0),
    ("aws-secret-access-key", "AWS secret access key",
     re.compile(r"(?i)\baws.{0,25}[=:,'\"][0-9a-zA-Z/+]{40}\b"), 0),
    ("gcp-api-key", "Google Cloud API key",
     re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), 0),
    ("github-token", "GitHub token",
     re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{22,})\b"), 0),
    ("openai-api-key", "OpenAI API key",
     re.compile(r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_-]{20,}\b"), 0),
    ("anthropic-api-key", "Anthropic API key",
     re.compile(r"\bsk-ant-[A-Za-z0-9_-]{18,}\b"), 0),
    ("slack-token", "Slack token",
     re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), 0),
    ("private-key", "Private key block",
     re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"), 0),
    ("generic-credential", "Credential assignment",
     re.compile(
         r"(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|"
         r"password|passwd|client[_-]?secret|credential)s?\b\s*(?:=|:|=>)\s*"
         r"[\"']?([A-Za-z0-9+/_\-.~%]{12,})[\"']?"
     ), 1),
]

# High-entropy candidate tokens, checked only when no rule matched them.
ENTROPY_RE = re.compile(r"[A-Za-z0-9+/=_-]{32,}")
ENTROPY_THRESHOLD = 4.5

# Values that are documented placeholders rather than live credentials.
PLACEHOLDER_RE = re.compile(
    r"(?i)(example|sample|placeholder|dummy|fake|redacted|changeme|not-a-real|"
    r"your[_-]|<[a-z]|^\{|\}$|x{6,}|\.{3}|test[-_]?key|mock[-_]?key|xxx)"
)

BUNDLE_DIRS = ["agents", "rules", "skills", "knowledge", "workflows", "lite",
               "examples", "scripts", ".github"]


def shannon_entropy(text):
    counts = Counter(text)
    n = len(text)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def is_placeholder(value):
    return bool(PLACEHOLDER_RE.search(value))


def redact(value):
    """Mask a matched secret: keep a short prefix and suffix only."""
    if len(value) <= 8:
        return "*" * 8
    return f"{value[:4]}{'*' * (len(value) - 6)}{value[-2:]}"


def fingerprint(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_baseline():
    """Return the set of (file, sha256) pairs that are allowlisted."""
    if not BASELINE_PATH.is_file():
        return set()
    try:
        data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        print(f"WARN: could not parse {BASELINE_PATH.name}; ignoring it")
        return set()
    entries = set()
    for entry in data.get("entries", []):
        if "file" in entry and "hash" in entry:
            entries.add((entry["file"], entry["hash"]))
    return entries


def read_text(path):
    """Return file text, or None for binary, oversized, or unreadable files."""
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if len(raw) > MAX_FILE_BYTES or b"\x00" in raw[:8192]:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def git_lines(root, args):
    try:
        out = subprocess.run(["git"] + args, cwd=root, capture_output=True,
                             check=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return [line for line in out.stdout.splitlines() if line]


def bundle_files():
    """Tracked bundle files, with a directory-walk fallback for tarball installs."""
    tracked = git_lines(ROOT, ["ls-files"])
    if tracked is not None and tracked:
        return [ROOT / p for p in tracked if (ROOT / p).is_file()]
    files = []
    for name in BUNDLE_DIRS:
        base = ROOT / name
        if not base.is_dir():
            continue
        for dirpath, _, filenames in os.walk(base):
            for f in filenames:
                files.append(Path(dirpath) / f)
    for entry in ROOT.iterdir():
        if entry.is_file() and entry.suffix in {".md", ".json", ".py", ".yml"}:
            files.append(entry)
    return files


def staged_files():
    """Staged paths paired with their staged content (pre-commit mode)."""
    names = git_lines(ROOT, ["diff", "--cached", "--name-only", "--diff-filter=ACMR"])
    if names is None:
        print("ERROR: --staged requires a git repository with a index")
        return None
    pairs = []
    for name in names:
        if not (ROOT / name).is_file():
            continue  # deleted from the index
        show = subprocess.run(["git", "show", f":{name}"], cwd=ROOT,
                              capture_output=True, text=True)
        if show.returncode != 0:
            continue
        pairs.append((name, show.stdout))
    return pairs


def runs_dir():
    data_dir = os.environ.get("ATLAS_DATA_DIR")
    candidates = []
    if data_dir:
        candidates.append(Path(data_dir).expanduser())
    candidates.append(Path("~/.atlas/data").expanduser())
    for candidate in candidates:
        runs = candidate / "runs"
        if runs.is_dir():
            return runs
    return None


def collect_runs_files(runs):
    files = []
    for dirpath, _, filenames in os.walk(runs):
        for f in filenames:
            files.append(Path(dirpath) / f)
    return files


def scan_text(label, text, baseline):
    """Return (findings, suppressed) for one file."""
    findings = []
    suppressed = 0
    for line_no, line in enumerate(text.splitlines(), 1):
        line_matches = []
        for rule_id, _, pattern, priority in RULES:
            for match in pattern.finditer(line):
                value = match.group(0)
                if priority == 1 and is_placeholder(value):
                    continue
                line_matches.append((priority, match.start(), match.end(),
                                     rule_id, value))
        # Entropy check, skipping anything a provider rule already matched.
        for match in ENTROPY_RE.finditer(line):
            value = match.group(0)
            if is_placeholder(value) or re.fullmatch(r"[0-9a-fA-F]+", value):
                continue
            if shannon_entropy(value) < ENTROPY_THRESHOLD:
                continue
            if any(match.start() < end and match.end() > start
                   for _, start, end, _, _ in line_matches):
                continue
            line_matches.append((2, match.start(), match.end(),
                                 "high-entropy", value))
        # Overlap is resolved per line: provider rules beat the generic and
        # entropy rules that share character offsets.
        kept_spans = []
        for _priority, start, end, rule_id, value in sorted(line_matches):
            if any(start < k_end and end > k_start for k_start, k_end in kept_spans):
                continue
            kept_spans.append((start, end))
            fp = fingerprint(value)
            if (label, fp) in baseline:
                suppressed += 1
                continue
            findings.append((label, line_no, rule_id, value, fp))

    return findings, suppressed


def display_label(path):
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def main():
    parser = argparse.ArgumentParser(description="Scan for leaked secrets in Atlas files")
    parser.add_argument("--staged", action="store_true",
                        help="scan only git-staged changes (pre-commit mode)")
    parser.add_argument("--dir", action="append", default=[], metavar="DIR",
                        help="extra directory to scan (repeatable)")
    parser.add_argument("--skip-runs", action="store_true",
                        help="do not scan $ATLAS_DATA_DIR/runs/")
    parser.add_argument("--update-baseline", action="store_true",
                        help="allowlist the current findings in .secrets.baseline")
    args = parser.parse_args()

    print("Atlas Secret Scanner")
    print("=" * 50)

    baseline = load_baseline()
    state = {"suppressed": 0, "scanned": 0}
    findings = []

    def handle(pairs, heading):
        print(f"\n{heading}")
        if not pairs:
            print("   SKIP: nothing to scan")
            return
        file_findings = []
        for label, text in pairs:
            scanned_findings, suppressed = scan_text(label, text, baseline)
            state["scanned"] += 1
            state["suppressed"] += suppressed
            findings.extend(scanned_findings)
            file_findings.extend(scanned_findings)
        if file_findings:
            print(f"   FOUND {len(file_findings)} potential secrets:")
            for label, line_no, rule_id, _value, fp in file_findings:
                print(f"   - {label}:{line_no} [{rule_id}] redacted sha256:{fp[:12]}")
        else:
            print(f"   OK: {len(pairs)} files scanned, no findings")

    if args.staged:
        staged = staged_files()
        if staged is None:
            return 1
        pairs = []
        for name, text in staged:
            if text is None:
                continue
            pairs.append((name, text))
        handle(pairs, "1. Scanning staged changes...")
        step = 2
    else:
        pairs = []
        for path in bundle_files():
            text = read_text(path)
            if text is not None:
                pairs.append((display_label(path), text))
        handle(pairs, "1. Scanning bundle files...")
        step = 2

        if not args.skip_runs:
            runs = runs_dir()
            if runs is None:
                print("\n2. Scanning run artifacts...")
                print("   SKIP: no runs directory found (set $ATLAS_DATA_DIR)")
            else:
                pairs = []
                for path in collect_runs_files(runs):
                    text = read_text(path)
                    if text is not None:
                        pairs.append((display_label(path), text))
                handle(pairs, f"2. Scanning run artifacts under {runs} ...")
            step = 3

    for extra in args.dir:
        base = Path(extra).expanduser()
        if not base.exists():
            print(f"\n{step}. Scanning {base} ...")
            print("   SKIP: directory not found")
            step += 1
            continue
        pairs = []
        paths = [base] if base.is_file() else [
            Path(dp) / f for dp, _, fns in os.walk(base) for f in fns]
        for path in paths:
            text = read_text(path)
            if text is not None:
                pairs.append((display_label(path), text))
        handle(pairs, f"{step}. Scanning {base} ...")
        step += 1

    print("\n" + "=" * 50)
    if args.update_baseline:
        update_baseline(baseline, findings)
        return 0
    if findings:
        print(f"RESULT: {len(findings)} POTENTIAL SECRETS FOUND")
        print("Never commit credentials. Rotate anything real, then allowlist")
        print("documented placeholders with: python3 scripts/scan-secrets.py --update-baseline")
        return 1
    note = f" ({state['suppressed']} baseline-allowed)" if state["suppressed"] else ""
    print(f"RESULT: CLEAN - no secrets found in {state['scanned']} files{note}")
    return 0


def update_baseline(baseline, findings):
    """Append the current findings to .secrets.baseline as allowlisted entries."""
    entries = sorted({"file": f, "hash": fp} for f, _, _, _, fp in findings)
    merged = sorted(
        list(baseline_set_to_dicts(baseline)) + entries,
        key=lambda e: (e["file"], e["hash"]),
    )
    payload = {
        "comment": ("Known-safe placeholders allowlisted by "
                    "scripts/scan-secrets.py. Each entry is keyed by file path "
                    "and SHA-256 of the matched value. Only document genuinely "
                    "fake values here, never live credentials."),
        "entries": merged,
    }
    BASELINE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(merged)} entries to {BASELINE_PATH.name}")


def baseline_set_to_dicts(baseline):
    return [{"file": f, "hash": h} for f, h in baseline]


if __name__ == "__main__":
    sys.exit(main())
