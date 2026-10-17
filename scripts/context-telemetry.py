#!/usr/bin/env python3
"""Post-hoc context telemetry over an Atlas trajectory.jsonl log.

Computes per-role/per-phase token accounting, prompt-cache hit rate,
compaction events, context-quality flags (poisoning / distraction /
confusion / clash), and an OTel-shaped export of the 8 Atlas metrics.

Usage:
    python3 scripts/context-telemetry.py RUN_DIR_OR_FILE
    python3 scripts/context-telemetry.py trajectory.jsonl --format flags --fail-on high
    python3 scripts/context-telemetry.py trajectory.jsonl --format otel --phase-budget 30000

Schema and metric definitions: knowledge/context/context-telemetry.md.
Metrics not computable from the log are reported as null, never fabricated.

Exit code: 0 = report produced (below --fail-on, if set), 1 = --fail-on threshold met
"""

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_PHASE_BUDGET = 40000
SEVERITY_RANK = {"low": 0, "medium": 1, "high": 2}
TOKEN_FIELDS = ("tokens", "tokensEstimate")
READ_ACTIONS = {"read", "grep", "glob"}
DELEGATE_ACTIONS = {"delegate"}
ESCALATE_ACTIONS = {"escalate"}
GATE_ACTIONS = {"gate-check"}

_TIKTOKEN = None
_TIKTOKEN_TRIED = False


def token_method():
    global _TIKTOKEN, _TIKTOKEN_TRIED
    if not _TIKTOKEN_TRIED:
        _TIKTOKEN_TRIED = True
        try:
            import tiktoken  # type: ignore

            _TIKTOKEN = tiktoken.get_encoding("cl100k_base")
        except Exception:
            _TIKTOKEN = None
    return _TIKTOKEN


def count_tokens(value):
    """Estimate tokens for a string: tiktoken if available, else chars/4."""
    if value is None:
        return 0
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    enc = token_method()
    if enc is not None:
        return len(enc.encode(text))
    return max(0, len(text) // 4)


def entry_tokens(entry):
    """Tokens for a decision entry, preferring explicit fields over estimation."""
    for field in TOKEN_FIELDS:
        if isinstance(entry.get(field), (int, float)):
            return int(entry[field])
    return count_tokens(entry.get("toolOutput") or entry.get("why") or "")


def load_entries(path):
    entries = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            print(f"WARN: skipping malformed JSON at line {lineno}", file=sys.stderr)
            continue
        if isinstance(obj, dict):
            entries.append(obj)
    return entries


def role_of(entry):
    return entry.get("role") or "unknown"


def phase_of(entry):
    return entry.get("phase") or "unknown"


def is_event(entry, kind):
    return entry.get("event") == kind


def decisions(entries):
    return [e for e in entries if not e.get("event")]


def detect_flags(entries, phase_budget, phase_totals):
    flags = []

    # Distraction: phase volume over budget.
    for phase, total in sorted(phase_totals.items()):
        if phase == "unknown" or total <= phase_budget:
            continue
        ratio = total / phase_budget
        severity = "high" if ratio >= 2 else "medium" if ratio >= 1.5 else "low"
        flags.append({
            "type": "distraction",
            "severity": severity,
            "role": None,
            "target": phase,
            "evidence": f"{total} tokens in phase (budget {phase_budget}, {ratio:.2f}x)",
        })

    # Confusion: same role re-reads same target >= 3x with no edit between.
    streaks, max_streaks = {}, {}
    for entry in decisions(entries):
        action = entry.get("action")
        target = entry.get("target")
        if not target:
            continue
        key = (role_of(entry), target)
        if action in READ_ACTIONS:
            streaks[key] = streaks.get(key, 0) + 1
            max_streaks[key] = max(max_streaks.get(key, 0), streaks[key])
        elif action in {"edit", "write"}:
            streaks[key] = 0
    for (role, target), count in sorted(max_streaks.items(), key=lambda kv: -kv[1]):
        if count < 3:
            continue
        severity = "high" if count >= 7 else "medium" if count >= 5 else "low"
        flags.append({
            "type": "confusion",
            "severity": severity,
            "role": role,
            "target": target,
            "evidence": f"{count} reads of same target without an intervening edit",
        })

    # Clash: conflicting approaches to the same target.
    approaches = {}
    order = {}
    for i, entry in enumerate(decisions(entries)):
        target = entry.get("target")
        approach = entry.get("approach")
        if not target:
            continue
        key = (role_of(entry), target)
        if approach:
            approaches.setdefault(key, set()).add(str(approach))
        order.setdefault(key, []).append((i, entry.get("outcome"), approach))
    for (role, target), seen in sorted(approaches.items(), key=lambda kv: -len(kv[1])):
        history = order.get((role, target), [])
        inverted = any(
            history[j][1] == "failure"
            and any(h[1] == "success" for h in history[:j])
            and history[j][2] != history[j - 1][2]
            for j in range(1, len(history))
        )
        if len(seen) < 2 and not inverted:
            continue
        severity = "high" if len(seen) >= 4 or inverted else "medium" if len(seen) == 3 else "low"
        detail = f"{len(seen)} distinct approaches" if len(seen) >= 2 else "conflicting approaches"
        flags.append({
            "type": "clash",
            "severity": severity,
            "role": role,
            "target": target,
            "evidence": detail + (" + success→failure inversion" if inverted else ""),
        })

    # Poisoning: a failed claim's error text reappears in a later success.
    failures = []
    for i, entry in enumerate(decisions(entries)):
        if entry.get("outcome") == "failure" and entry.get("error"):
            norm = re.sub(r"\s+", " ", str(entry["error"])).strip().lower()
            if len(norm) >= 20:
                failures.append((i, norm, entry))
    reported = set()
    for i, norm, entry in failures:
        for later in decisions(entries)[i + 1:]:
            if later.get("outcome") != "success":
                continue
            haystack = " ".join(
                str(later.get(f) or "") for f in ("why", "approach", "toolOutput")
            ).lower()
            if norm in re.sub(r"\s+", " ", haystack):
                key = (role_of(later), later.get("target"))
                if key in reported:
                    continue
                reported.add(key)
                flags.append({
                    "type": "poisoning",
                    "severity": "high",
                    "role": role_of(later),
                    "target": later.get("target"),
                    "evidence": f"failed claim from {role_of(entry)} reused as fact",
                })
                break
    return flags


def compute_metrics(entries, flags, tier_map):
    dec = decisions(entries)
    metrics = {}

    delegations = [e for e in dec if e.get("action") in DELEGATE_ACTIONS]
    rework = 0
    for i, d in enumerate(dec):
        if d.get("action") not in DELEGATE_ACTIONS:
            continue
        target_role = d.get("delegatedTo") or d.get("target")
        for later in dec[i + 1:]:
            if role_of(later) == target_role:
                if later.get("outcome") in {"failure", "escalated"}:
                    rework += 1
                break
    metrics["iahqs"] = round(1 - rework / len(delegations), 3) if delegations else None
    metrics["das"] = round((len(delegations) - rework) / len(delegations), 3) if delegations else None

    escalations = [e for e in dec if e.get("action") in ESCALATE_ACTIONS]
    structured = [e for e in escalations if e.get("why") and (e.get("toolInput") or e.get("approach"))]
    metrics["ejr"] = round(len(structured) / len(escalations), 3) if escalations else None

    gates = {}
    for e in dec:
        if e.get("action") not in GATE_ACTIONS:
            continue
        gates.setdefault(e.get("target") or "gate", []).append(e.get("outcome"))
    if gates:
        first_pass = sum(1 for outcomes in gates.values() if outcomes and outcomes[0] == "success")
        metrics["gyr"] = round(first_pass / len(gates), 3)
    else:
        metrics["gyr"] = None

    expected = [(e.get("expectedTokens"), entry_tokens(e)) for e in dec if e.get("expectedTokens")]
    if expected:
        exp = sum(x for x, _ in expected)
        act = sum(y for _, y in expected) or 1
        metrics["rei"] = round(exp / act, 3)
    else:
        metrics["rei"] = None

    rederive = sum(1 for f in flags if f["type"] == "confusion")
    metrics["cps"] = round(1 - min(1.0, rederive / len(delegations)), 3) if delegations else None

    timed = [e for e in dec if isinstance(e.get("durationMs"), (int, float))]
    if timed:
        total = sum(e["durationMs"] for e in timed)
        span = len(timed) * max(e["durationMs"] for e in timed)
        metrics["per"] = round(span / total, 3) if total else None
    else:
        metrics["per"] = None

    if tier_map:
        roles = {role_of(e) for e in dec if e.get("tier")}
        mismatches = sum(1 for e in dec if e.get("tier") and
                         tier_map.get(role_of(e)) not in (None, e["tier"]))
        metrics["mtas"] = round(1 - mismatches / len(roles), 3) if roles else None
    else:
        metrics["mtas"] = None
    return metrics


def build_report(entries, phase_budget, tier_map):
    dec = decisions(entries)
    tokens_by_role, tokens_by_phase, tokens_by_category = {}, {}, {}
    for entry in dec:
        tokens = entry_tokens(entry)
        tokens_by_role[role_of(entry)] = tokens_by_role.get(role_of(entry), 0) + tokens
        tokens_by_phase[phase_of(entry)] = tokens_by_phase.get(phase_of(entry), 0) + tokens
        category = entry.get("contextCategory")
        if category:
            tokens_by_category[category] = tokens_by_category.get(category, 0) + tokens
    for entry in entries:
        if is_event(entry, "context") and entry.get("category"):
            cat = entry["category"]
            tokens_by_category[cat] = tokens_by_category.get(cat, 0) + int(entry.get("tokens", 0))

    cache = {"static": {"hit": 0, "miss": 0}, "dynamic": {"hit": 0, "miss": 0}, "other": {"hit": 0, "miss": 0}}
    for entry in entries:
        if is_event(entry, "cache"):
            boundary = entry.get("boundary") if entry.get("boundary") in cache else "other"
            cache[boundary]["hit" if entry.get("hit") else "miss"] += 1

    compactions = []
    for entry in entries:
        if is_event(entry, "compaction"):
            before = int(entry.get("tokensBefore", 0))
            after = int(entry.get("tokensAfter", 0))
            score = entry.get("qualityScore")
            low_quality = (isinstance(score, (int, float)) and score < 0.6) or (
                before and (before - after) / before > 0.8
            )
            compactions.append({
                "trigger": entry.get("trigger", "unknown"),
                "delta": after - before,
                "qualityScore": score,
                "lowQuality": bool(low_quality),
            })

    flags = detect_flags(entries, phase_budget, tokens_by_phase)
    metrics = compute_metrics(entries, flags, tier_map)
    cache_rates = {
        boundary: (v["hit"] / (v["hit"] + v["miss"]) if (v["hit"] + v["miss"]) else None)
        for boundary, v in cache.items()
    }
    return {
        "entries": len(dec),
        "tokens": {
            "total": sum(tokens_by_role.values()),
            "byRole": tokens_by_role,
            "byPhase": tokens_by_phase,
            "byCategory": tokens_by_category,
            "method": "tiktoken" if token_method() else "chars/4",
        },
        "cache": {"counts": cache, "hitRate": cache_rates},
        "compactions": compactions,
        "flags": flags,
        "metrics": metrics,
    }


def render_dashboard(report, run_id):
    out = [f"Atlas Context Telemetry — run {run_id}", "=" * 50]
    t = report["tokens"]
    out.append(f"Decisions: {report['entries']}   Tokens: {t['total']} (est. via {t['method']})")
    out.append("\nTokens by role:")
    for role, total in sorted(t["byRole"].items(), key=lambda kv: -kv[1]):
        out.append(f"  {role:<20} {total:>8}")
    out.append("\nTokens by phase:")
    for phase, total in sorted(t["byPhase"].items(), key=lambda kv: -kv[1]):
        out.append(f"  {phase:<20} {total:>8}")
    out.append("\nContext budget by category (inline/search/load):")
    for cat in ("inline", "search", "load"):
        out.append(f"  {cat:<20} {t['byCategory'].get(cat, 0):>8}")
    for cat, total in sorted(t["byCategory"].items()):
        if cat not in ("inline", "search", "load"):
            out.append(f"  {cat:<20} {total:>8}")
    out.append("\nCache hit rate:")
    for boundary in ("static", "dynamic", "other"):
        rate = report["cache"]["hitRate"][boundary]
        counts = report["cache"]["counts"][boundary]
        shown = "n/a" if rate is None else f"{rate:.2%}"
        out.append(f"  {boundary:<10} {shown:>7}  ({counts['hit']} hit / {counts['miss']} miss)")
    out.append("\nCompactions:")
    if report["compactions"]:
        for c in report["compactions"]:
            score = "n/a" if c["qualityScore"] is None else f"{c['qualityScore']:.2f}"
            warn = "  [LOW QUALITY]" if c["lowQuality"] else ""
            out.append(f"  trigger={c['trigger']:<9} delta={c['delta']:>+7}"
                       f"  quality={score}{warn}")
    else:
        out.append("  none")
    out.append("\nContext quality flags:")
    if report["flags"]:
        for f in sorted(report["flags"], key=lambda x: -SEVERITY_RANK[x["severity"]]):
            who = f"{f['role']} " if f["role"] else ""
            out.append(f"  [{f['severity'].upper():<6}] {f['type']:<10} {who}{f['target'] or ''}")
            out.append(f"            {f['evidence']}")
    else:
        out.append("  none")
    out.append("\nAtlas metrics (null = inputs not logged):")
    for name, value in report["metrics"].items():
        out.append(f"  {name.upper():<6} {value if value is not None else 'null'}")
    return "\n".join(out)


def render_flags(report):
    lines = []
    for f in report["flags"]:
        lines.append(f"{f['severity']}\t{f['type']}\t{f['role'] or '-'}\t{f['target'] or '-'}\t{f['evidence']}")
    return "\n".join(lines) if lines else "(no context quality flags)"


def render_otel(report, run_id):
    metrics = []

    def add(name, unit, value, attributes=None, kind="sum"):
        if value is None:
            return
        entry = {"name": name, "unit": unit, kind: value}
        if attributes:
            entry["attributes"] = attributes
        metrics.append(entry)

    for role, total in report["tokens"]["byRole"].items():
        add("atlas.context.tokens.total", "By", total, {"atlas.role": role})
    for phase, total in report["tokens"]["byPhase"].items():
        add("atlas.context.tokens.total", "By", total, {"atlas.phase": phase})
    for cat, total in report["tokens"]["byCategory"].items():
        add("atlas.context.tokens.total", "By", total, {"atlas.context.category": cat})
    for boundary, rate in report["cache"]["hitRate"].items():
        add("atlas.context.cache.hit_ratio", "1", rate, {"atlas.cache.boundary": boundary}, kind="gauge")
    add("atlas.context.compaction.count", "1", len(report["compactions"]))
    for c in report["compactions"]:
        add("atlas.context.compaction.delta", "By", c["delta"], {"atlas.compaction.trigger": c["trigger"]})
    counts = {}
    for f in report["flags"]:
        counts[(f["type"], f["severity"])] = counts.get((f["type"], f["severity"]), 0) + 1
    for (ftype, sev), count in counts.items():
        add("atlas.context.quality.flags", "1", count,
            {"atlas.quality.type": ftype, "atlas.quality.severity": sev})
    for name, value in report["metrics"].items():
        add(f"atlas.metric.{name}", "1", value, kind="gauge")
    return json.dumps({
        "resource": {"service.name": "atlas", "atlas.run.id": run_id},
        "metrics": metrics,
    }, indent=2)


def parse_tier_map(value):
    if not value:
        return {}
    tier_map = {}
    for pair in value.split(","):
        if "=" in pair:
            role, tier = pair.split("=", 1)
            tier_map[role.strip()] = tier.strip()
    return tier_map


def main():
    parser = argparse.ArgumentParser(description="Atlas context telemetry analyzer")
    parser.add_argument("path", help="trajectory.jsonl file or a run directory containing it")
    parser.add_argument("--format", choices=["dashboard", "flags", "metrics", "otel", "json"],
                        default="dashboard")
    parser.add_argument("--phase-budget", type=int, default=DEFAULT_PHASE_BUDGET,
                        help=f"per-phase token budget (default {DEFAULT_PHASE_BUDGET})")
    parser.add_argument("--tier-map", default=None,
                        help="role=tier pairs, comma-separated, for MTAS")
    parser.add_argument("--fail-on", choices=["low", "medium", "high"], default=None,
                        help="exit 1 if any flag at or above this severity is found")
    args = parser.parse_args()

    path = Path(args.path)
    if path.is_dir():
        path = path / "trajectory.jsonl"
    if not path.is_file():
        print(f"ERROR: no trajectory file at {path}", file=sys.stderr)
        return 1

    entries = load_entries(path)
    run_id = path.parent.name if path.name == "trajectory.jsonl" else path.stem
    report = build_report(entries, args.phase_budget, parse_tier_map(args.tier_map))

    if args.format == "dashboard":
        print(render_dashboard(report, run_id))
    elif args.format == "flags":
        print(render_flags(report))
    elif args.format == "metrics":
        print(json.dumps(report["metrics"], indent=2))
    elif args.format == "otel":
        print(render_otel(report, run_id))
    else:
        print(json.dumps(report, indent=2))

    if args.fail_on:
        threshold = SEVERITY_RANK[args.fail_on]
        if any(SEVERITY_RANK[f["severity"]] >= threshold for f in report["flags"]):
            print(f"\nFAIL: context quality flag at or above '{args.fail_on}'", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
