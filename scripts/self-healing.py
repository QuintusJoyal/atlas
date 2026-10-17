#!/usr/bin/env python3
"""Autonomous self-healing and recovery runtime for Atlas agents.

Usage:
    python3 scripts/self-healing.py --self-test          # run the built-in checks
    python3 scripts/self-healing.py --self-test --verbose

Implements the programmatic half of knowledge/process/self-healing-protocol.md:

- classify_error(): map a failure message to an errorCategory (transient,
  rate-limit, quota, timeout, validation, permission, not-found, business)
  following the structured error contract in knowledge/process/aci-enforcement.md.
- RetryPolicy / run_with_retry(): exponential backoff for transient, rate-limit,
  and timeout failures with a configurable max retry count.
- TierCascade(): premium -> standard -> fast downgrade on quota/rate failures,
  with a per-tier cooldown so ambiguous quota errors cannot thrash the cascade.
- should_compact(): context compaction trigger at 75% of the model window
  (configurable), ahead of the ~80% hard limit in rules/atlas-core.md.
- StuckDetector(): kill-and-respawn signal when an agent produces no state
  transition in N consecutive turns (configurable).
- CheckpointStore(): atomic, versioned JSON checkpoint serialization to
  $ATLAS_DATA_DIR/checkpoints/, one save per phase completion.
- degradation_report(): preserve partial results when a role fails so
  atlas-lead can re-delegate only the remaining work scope.

Library use (import from a host integration):

    from self_healing import (
        RetryPolicy, TierCascade, StuckDetector, CheckpointStore,
        classify_error, run_with_retry, should_compact, degradation_report,
    )

Every knob has an ATLAS_SELF_HEALING_* environment override so behaviors can be
feature-flagged per rollout (the protocol's rollout rule).

Exit code: 0 = self-test passed, 1 = self-test failed or bad usage
"""

import argparse
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "atlas-recovery/1.0"

DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0
DEFAULT_MAX_DELAY = 30.0
DEFAULT_STUCK_TURNS = 5
DEFAULT_COMPACTION_THRESHOLD = 0.75
DEFAULT_COOLDOWN_SECONDS = 600.0

TIER_CASCADE = ("premium", "standard", "fast")

# Failure words that mean "same call may succeed later" (retry / short retry).
_TRANSIENT_WORDS = (
    "timeout", "timed out", "temporarily", "econnreset", "connection reset",
    "connection refused", "econnrefused", "unavailable", "overloaded",
    "internal error", "502", "503", "504",
)
_RATE_WORDS = ("rate limit", "rate_limit", "too many requests", "429", "throttl")
_QUOTA_WORDS = (
    "quota", "usage limit", "exceeded", "credit", "billing",
    "out of tokens", "context length", "maximum context",
)
_VALIDATION_WORDS = ("invalid", "malformed", "unsupported", "schema")
_PERMISSION_WORDS = ("permission", "forbidden", "403", "unauthorized", "not allowed", "denied")
_NOT_FOUND_WORDS = ("not found", "no such file", "does not exist", "404")


def env_float(name, default):
    raw = os.environ.get(name)
    try:
        return float(raw) if raw is not None else default
    except ValueError:
        return default


def env_int(name, default):
    raw = os.environ.get(name)
    try:
        return int(raw) if raw is not None else default
    except ValueError:
        return default


def env_flag(name, default=True):
    """ATLAS_SELF_HEALING=0/1-style kill switch; anything else keeps the default."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in ("0", "false", "off", "no")


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def classify_error(message):
    """Map a failure message to an errorCategory string.

    Order matters: rate-limit is checked before quota because a "rate limit
    exceeded" message also contains the generic quota word "exceeded", and
    permission beats validation. Returns 'business' when nothing matches,
    matching the four-category contract in aci-enforcement.md plus the
    rate-limit/quota split the cascade needs.
    """
    text = str(message).lower()
    if any(w in text for w in _RATE_WORDS):
        return "rate-limit"
    if any(w in text for w in _QUOTA_WORDS):
        return "quota"
    if any(w in text for w in _PERMISSION_WORDS):
        return "permission"
    if any(w in text for w in _NOT_FOUND_WORDS):
        return "not-found"
    if any(w in text for w in _VALIDATION_WORDS):
        return "validation"
    if any(w in text for w in _TRANSIENT_WORDS):
        return "transient"
    return "business"


class RetryPolicy:
    """Exponential backoff: base * 2^attempt, capped at max_delay."""

    def __init__(self, max_retries=None, base_delay=None, max_delay=None):
        self.max_retries = (
            max_retries if max_retries is not None
            else env_int("ATLAS_SELF_HEALING_MAX_RETRIES", DEFAULT_MAX_RETRIES)
        )
        self.base_delay = (
            base_delay if base_delay is not None
            else env_float("ATLAS_SELF_HEALING_BASE_DELAY", DEFAULT_BASE_DELAY)
        )
        self.max_delay = (
            max_delay if max_delay is not None
            else env_float("ATLAS_SELF_HEALING_MAX_DELAY", DEFAULT_MAX_DELAY)
        )

    def delay(self, attempt):
        """Delay in seconds before retry number `attempt` (1-based)."""
        if attempt < 1:
            attempt = 1
        return min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)

    def is_retryable(self, category):
        return category in ("transient", "rate-limit", "timeout")


def run_with_retry(fn, policy=None, sleep=time.sleep, on_error=None):
    """Call fn() with exponential backoff on retryable failures.

    fn takes no arguments and either returns a value or raises. Non-retryable
    error categories (validation, permission, business, ...) are raised
    immediately. Returns (result, attempts_used).
    """
    policy = policy or RetryPolicy()
    attempt = 0
    while True:
        attempt += 1
        try:
            return fn(), attempt
        except Exception as exc:  # noqa: BLE001 - boundary for arbitrary callables
            category = classify_error(exc)
            if on_error:
                on_error(exc, category, attempt)
            if not policy.is_retryable(category) or attempt > policy.max_retries:
                raise
            sleep(policy.delay(attempt))


class TierCascade:
    """premium -> standard -> fast with cooldown so downgrades cannot thrash.

    A cooldown entry records when a tier was abandoned; within the cooldown
    window the same tier is never re-offered, so an ambiguous quota error
    cannot bounce the agent back up and down repeatedly.
    """

    def __init__(self, tiers=None, start=None, cooldown=None):
        self.tiers = tuple(tiers or TIER_CASCADE)
        self.current = start or self.tiers[0]
        self.cooldown_seconds = (
            cooldown if cooldown is not None
            else env_float("ATLAS_SELF_HEALING_COOLDOWN", DEFAULT_COOLDOWN_SECONDS)
        )
        self._cooldown_until = {}
        self._sleep = time.sleep
        self._now = time.time

    def on_failure(self, category, message=""):
        """Record a quota/rate failure at the current tier and move down one step.

        Returns the new tier, or None when the cascade is exhausted (all tiers
        tried: address the user, per model-resilience.md).
        """
        if category not in ("quota", "rate-limit", "transient"):
            return self.current
        self._cooldown_until[self.current] = self._now() + self.cooldown_seconds
        idx = self.tiers.index(self.current)
        for tier in self.tiers[idx + 1:]:
            until = self._cooldown_until.get(tier, 0)
            if self._now() >= until:
                self.current = tier
                return tier
        self.current = None  # exhausted: every remaining tier is cooling down
        return None

    def exhausted(self):
        return self.current is None

    def log_line(self, role, reason):
        return (
            f"downgrade: {role} to {self.current}, reason {reason}, "
            f"date {utc_now()}"
        )


def should_compact(context_tokens, window_size, threshold=None):
    """True when context usage has reached the compaction trigger point.

    Default trigger is 75% of the window (the self-healing protocol's early
    trigger), ahead of the ~80% hard limit in rules/atlas-core.md.
    """
    if window_size <= 0:
        return False
    if threshold is None:
        threshold = env_float("ATLAS_SELF_HEALING_COMPACT_AT", DEFAULT_COMPACTION_THRESHOLD)
    return (context_tokens / window_size) >= threshold


class StuckDetector:
    """Kill-and-respawn signal after N turns with no state transition.

    Call record(state) once per turn with a fingerprint of observable state
    (phase, artifact paths, team.json status, trajectory tail). is_stuck()
    returns True once the same fingerprint has been seen `max_stuck_turns`
    times in a row; the caller then respawns the role from its last checkpoint.
    """

    def __init__(self, max_stuck_turns=None):
        self.max_stuck_turns = (
            max_stuck_turns if max_stuck_turns is not None
            else env_int("ATLAS_SELF_HEALING_STUCK_TURNS", DEFAULT_STUCK_TURNS)
        )
        self._last = None
        self._streak = 0

    def record(self, state):
        fingerprint = json.dumps(state, sort_keys=True, default=str)
        if fingerprint == self._last:
            self._streak += 1
        else:
            self._last = fingerprint
            self._streak = 1
        return self._streak

    def is_stuck(self):
        return self._streak >= self.max_stuck_turns

    def streak(self):
        return self._streak

    def reset(self):
        self._last = None
        self._streak = 0


class CheckpointStore:
    """Atomic, versioned JSON checkpoints under <data_dir>/checkpoints/.

    data_dir defaults to $ATLAS_DATA_DIR (fallback ~/.atlas/data), matching
    knowledge/process/checkpoint-protocol.md. Each save writes a new sequence-
    numbered file via temp-file + os.replace so a crash mid-write can never
    corrupt the previous good checkpoint. latest() returns the most recent
    checkpoint for a role, which is what kill-and-respawn restores from.
    """

    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.environ.get("ATLAS_DATA_DIR") or os.path.join(
                os.path.expanduser("~"), ".atlas", "data"
            )
        self.data_dir = Path(data_dir)
        self.checkpoint_dir = self.data_dir / "checkpoints"

    def save(self, role, phase, state, level="standard"):
        """Serialize agent state for role at phase completion.

        `state` is any JSON-serializable mapping (the checkpoint's context,
        artifacts, trajectory tail per checkpoint-protocol.md). Returns the
        written checkpoint path.
        """
        seq = len(list(self.checkpoint_dir.glob(f"cp-{role}-*.json"))) + 1 if self.checkpoint_dir.is_dir() else 1
        checkpoint_id = f"cp-{role}-{phase}-{seq:04d}"
        payload = {
            "schema": SCHEMA,
            "checkpointId": checkpoint_id,
            "created": utc_now(),
            "role": role,
            "phase": phase,
            "level": level,
            "state": state,
        }
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        target = self.checkpoint_dir / f"{checkpoint_id}.json"
        fd, tmp = tempfile.mkstemp(dir=str(self.checkpoint_dir), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, sort_keys=True)
                f.write("\n")
            os.replace(tmp, target)  # atomic on POSIX and Windows
        except BaseException:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
        latest = self.checkpoint_dir / f"latest-{role}.json"
        latest.write_text(json.dumps({"checkpointId": checkpoint_id}) + "\n", encoding="utf-8")
        return target

    def load(self, checkpoint_id):
        path = self.checkpoint_dir / f"{checkpoint_id}.json"
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        if payload.get("schema") != SCHEMA:
            raise ValueError(f"unknown checkpoint schema: {payload.get('schema')!r}")
        for field in ("checkpointId", "role", "phase", "state"):
            if field not in payload:
                raise ValueError(f"checkpoint missing required field: {field}")
        return payload

    def latest(self, role):
        """Most recent checkpoint for role, or None if none was ever saved."""
        if not self.checkpoint_dir.is_dir():
            return None
        candidates = sorted(self.checkpoint_dir.glob(f"cp-{role}-*.json"))
        if not candidates:
            return None
        return self.load(candidates[-1].stem)


def degradation_report(role, error, checkpoint=None, completed=None, remaining=None):
    """Bundle what a failed role did finish so atlas-lead can re-degrade gracefully.

    Returns a JSON-serializable partial-results report: the preserved artifacts,
    the failed scope, the checkpoint to respawn from, and a re-delegation brief
    for the remaining work only (never redo completed scope).
    """
    completed = list(completed or [])
    remaining = list(remaining or [])
    report = {
        "schema": SCHEMA,
        "kind": "degradation-report",
        "created": utc_now(),
        "role": role,
        "error": {
            "message": str(error),
            "errorCategory": classify_error(error),
            "recoverable": classify_error(error) in ("transient", "rate-limit", "quota", "timeout"),
        },
        "partialResults": {
            "preservedArtifacts": completed,
            "remainingScope": remaining,
        },
        "checkpointId": (checkpoint or {}).get("checkpointId"),
        "redelegate": {
            "scope": "remaining only",
            "briefHint": (
                f"Re-delegate the remaining scope to {role} (or the next tier down). "
                "Preserved artifacts are already on disk; do not redo them."
            ),
        },
    }
    return report


def _demo():
    """End-to-end walk-through used by --self-test and by integrators as an example."""
    log = []
    policy = RetryPolicy(max_retries=2, base_delay=0.01)
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise TimeoutError("request timed out")
        return "ok"

    result, attempts = run_with_retry(flaky, policy, sleep=lambda s: None,
                                      on_error=lambda e, c, a: log.append((c, a)))
    assert result == "ok" and attempts == 3

    cascade = TierCascade(start="premium", cooldown=0)
    assert cascade.on_failure("quota") == "standard"
    assert cascade.on_failure("rate-limit") == "fast"
    assert cascade.on_failure("quota") is None and cascade.exhausted()

    assert should_compact(750, 1000) and not should_compact(749, 1000)

    stuck = StuckDetector(max_stuck_turns=3)
    for _ in range(3):
        stuck.record({"phase": "impl", "artifacts": ["a.py"]})
    assert stuck.is_stuck()

    return log


def main():
    parser = argparse.ArgumentParser(
        description="Atlas self-healing runtime (retry, cascade, stuck detection, checkpoints)"
    )
    parser.add_argument("--self-test", action="store_true", help="run built-in checks and exit")
    parser.add_argument("--verbose", action="store_true", help="print per-check detail")
    args = parser.parse_args()

    if not (args.self_test or args.verbose):
        parser.print_help()
        print("\nThis script is a library. Import it, or run --self-test.")
        return 1

    checks = []

    def check(name, fn):
        try:
            fn()
            checks.append((name, True, ""))
        except AssertionError as exc:
            checks.append((name, False, f"assertion failed: {exc}"))
        except Exception as exc:  # noqa: BLE001
            checks.append((name, False, f"{type(exc).__name__}: {exc}"))

    def classify_check():
        cases = [
            ("HTTP 429 too many requests", "rate-limit"),
            ("usage limit exceeded for model", "quota"),
            ("request timed out", "transient"),
            ("temporarily unavailable", "transient"),
            ("invalid argument foo", "validation"),
            ("permission denied", "permission"),
            ("file not found", "not-found"),
            ("insufficient funds for export", "business"),
        ]
        for message, expected in cases:
            actual = classify_error(message)
            assert actual == expected, f"{message!r}: expected {expected}, got {actual}"

    check("classify_error", classify_check)

    def retry_check():
        policy = RetryPolicy(max_retries=3, base_delay=1.0)
        assert policy.delay(1) == 1.0
        assert policy.delay(2) == 2.0
        assert policy.delay(3) == 4.0
        assert policy.delay(10) == DEFAULT_MAX_DELAY  # capped
        slept = []
        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            if calls["n"] < 3:
                raise ConnectionError("connection reset by peer")
            return "ok"

        result, attempts = run_with_retry(flaky, policy, sleep=slept.append)
        assert result == "ok" and attempts == 3
        assert slept == [1.0, 2.0]

        def fatal():
            raise PermissionError("permission denied")

        try:
            run_with_retry(fatal, policy, sleep=slept.append)
            raise AssertionError("non-retryable error was retried")
        except PermissionError:
            pass

        def exhausted():
            raise TimeoutError("timed out")

        try:
            run_with_retry(exhausted, RetryPolicy(max_retries=1, base_delay=0.01), sleep=slept.append)
            raise AssertionError("retryable error should exhaust and raise")
        except TimeoutError:
            pass

    check("retry_exponential_backoff", retry_check)

    def cascade_check():
        c = TierCascade(start="premium", cooldown=0)
        assert c.on_failure("quota") == "standard"
        assert c.on_failure("rate-limit") == "fast"
        assert c.on_failure("quota") is None and c.exhausted()
        d = TierCascade(start="premium", cooldown=3600)
        assert d.on_failure("quota") == "standard"
        # Within cooldown, "fast" is still the only valid next step even if a
        # later attempt claims standard recovered; exhausted -> None.
        assert d.on_failure("quota") == "fast"
        assert d.on_failure("quota") is None
        e = TierCascade(start="premium", cooldown=0)
        assert e.on_failure("validation") == "premium"  # no downgrade on validation
        assert "downgrade:" in e.log_line("atlas-dev", "quota")

    check("tier_cascade_with_cooldown", cascade_check)

    def compaction_check():
        assert should_compact(750, 1000), "75% of window should trigger compaction"
        assert not should_compact(749, 1000), "74.9% should not trigger"
        assert should_compact(8000, 10000, threshold=0.8), "custom threshold respected"
        assert not should_compact(1, 0), "zero window never compacts"

    check("compaction_trigger", compaction_check)

    def stuck_check():
        d = StuckDetector(max_stuck_turns=3)
        for _ in range(2):
            d.record({"phase": "impl"})
            assert not d.is_stuck()
        d.record({"phase": "impl"})
        assert d.is_stuck()
        d.record({"phase": "review"})  # a transition resets the detector
        assert not d.is_stuck()

    check("stuck_detector", stuck_check)

    def checkpoint_check():
        with tempfile.TemporaryDirectory() as tmp:
            store = CheckpointStore(data_dir=tmp)
            p1 = store.save("atlas-dev", "implementation", {"currentTask": "write parser"})
            p2 = store.save("atlas-dev", "testing", {"currentTask": "run tests"})
            assert p1 != p2 and p1.is_file() and p2.is_file()
            assert not list(Path(tmp).glob("*.tmp"))
            latest = store.latest("atlas-dev")
            assert latest["phase"] == "testing"
            reloaded = store.load(latest["checkpointId"])
            assert reloaded["state"]["currentTask"] == "run tests"
            assert store.latest("atlas-qa") is None

    check("checkpoint_serialization", checkpoint_check)

    def degradation_check():
        report = degradation_report(
            "atlas-dev",
            "rate limit exceeded",
            checkpoint={"checkpointId": "cp-atlas-dev-implementation-0001"},
            completed=["src/parser.py"],
            remaining=["tests/test_parser.py"],
        )
        assert report["error"]["errorCategory"] == "rate-limit"
        assert report["partialResults"]["preservedArtifacts"] == ["src/parser.py"]
        assert report["partialResults"]["remainingScope"] == ["tests/test_parser.py"]
        assert report["checkpointId"] == "cp-atlas-dev-implementation-0001"
        json.dumps(report)  # must be serializable for team.json / trajectory

    check("graceful_degradation", degradation_check)

    check("demo_walkthrough", lambda: _demo())

    print("Atlas Self-Healing Runtime")
    print("=" * 50)
    failed = 0
    for name, ok, detail in checks:
        if ok:
            if args.verbose:
                print(f"  PASS {name}")
        else:
            failed += 1
            print(f"  FAIL {name}: {detail}")
    print("=" * 50)
    if failed:
        print(f"RESULT: {failed} of {len(checks)} checks FAILED")
        return 1
    print(f"RESULT: all {len(checks)} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
