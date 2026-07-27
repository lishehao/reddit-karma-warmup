#!/usr/bin/env python3
"""Classify and reconcile stale local Reddit runtime records without Chrome.

The caller obtains task, Heartbeat, and lock facts independently. This helper
never opens a browser, calls Reddit, deletes an automation, or modifies an old
queue. It only writes an immutable reconciliation marker after a proven stale
runtime classification.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile


SCHEMA = "reddit_runtime_fence/v1"
TASK_STATES = {"running", "idle", "notLoaded", "archived", "absent", "unknown"}
HEARTBEAT_STATES = {"future", "absent", "expired", "unknown"}
LOCK_STATES = {"held", "unheld", "unknown"}
QUEUE_STATES = {"ACTIVE", "FINALIZING", "RETIRED", "UNKNOWN"}
INACTIVE_TASK_STATES = {"idle", "notLoaded", "archived", "absent"}
CODEX_HOME = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
DEFAULT_REGISTRY_ROOT = CODEX_HOME / "reddit-karma-warmup" / "single-owner" / "runtime-reconciliations"


def fail(message):
    raise ValueError(message)


def text(value, name, minimum=1, maximum=512):
    if not isinstance(value, str):
        fail(name + " must be text")
    value = value.strip()
    if not minimum <= len(value) <= maximum or "\x00" in value:
        fail("invalid " + name)
    return value


def parse_utc(value, name):
    value = text(value, name, 20, 64)
    if not value.endswith("Z"):
        fail(name + " must be UTC RFC3339 ending in Z")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid " + name) from exc
    if parsed.tzinfo != dt.timezone.utc:
        fail(name + " must use UTC")
    return parsed.timestamp()


def canonical_hash(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_evidence(path):
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("invalid runtime fence evidence") from exc
    if not isinstance(raw, dict):
        fail("runtime fence evidence must be object")
    required = {
        "owner_task_id", "mission_id", "queue_state", "operation_stop_at",
        "task_state", "heartbeat_state", "lock_state",
    }
    if set(raw) - (required | {"chrome_ledger_state", "source_queue_path"}) or required - set(raw):
        fail("runtime fence evidence has unsupported or missing fields")
    evidence = {
        "owner_task_id": text(raw["owner_task_id"], "owner_task_id", 8, 128),
        "mission_id": text(raw["mission_id"], "mission_id", 8, 256),
        "queue_state": text(raw["queue_state"], "queue_state", 4, 16),
        "operation_stop_at": text(raw["operation_stop_at"], "operation_stop_at", 20, 64),
        "task_state": text(raw["task_state"], "task_state", 2, 32),
        "heartbeat_state": text(raw["heartbeat_state"], "heartbeat_state", 2, 32),
        "lock_state": text(raw["lock_state"], "lock_state", 2, 32),
        "chrome_ledger_state": text(raw.get("chrome_ledger_state", "UNKNOWN"), "chrome_ledger_state", 2, 32),
        "source_queue_path": text(raw.get("source_queue_path", "unknown"), "source_queue_path", 1, 2048),
    }
    if evidence["queue_state"] not in QUEUE_STATES:
        fail("invalid queue_state")
    if evidence["task_state"] not in TASK_STATES:
        fail("invalid task_state")
    if evidence["heartbeat_state"] not in HEARTBEAT_STATES:
        fail("invalid heartbeat_state")
    if evidence["lock_state"] not in LOCK_STATES:
        fail("invalid lock_state")
    parse_utc(evidence["operation_stop_at"], "operation_stop_at")
    return evidence


def classify(evidence, now_epoch):
    stop_epoch = parse_utc(evidence["operation_stop_at"], "operation_stop_at")
    expired = now_epoch >= stop_epoch
    reasons = []
    if evidence["task_state"] == "running":
        reasons.append("TASK_RUNNING")
    if evidence["heartbeat_state"] == "future":
        reasons.append("HEARTBEAT_FUTURE")
    if evidence["lock_state"] == "held":
        reasons.append("LOCK_HELD")
    if reasons:
        return "ACTIVE_OWNER", reasons
    unknown = [
        name for name in ("task_state", "heartbeat_state", "lock_state")
        if evidence[name] == "unknown"
    ]
    if unknown:
        return "UNCERTAIN", ["MISSING_" + name.upper() for name in unknown]
    if evidence["queue_state"] == "RETIRED":
        return "NO_FENCE", ["QUEUE_RETIRED"]
    if (
        expired
        and evidence["task_state"] in INACTIVE_TASK_STATES
        and evidence["heartbeat_state"] in {"absent", "expired"}
        and evidence["lock_state"] == "unheld"
    ):
        return "STALE_RUNTIME", [
            "OPERATION_CUTOFF_PASSED",
            "TASK_NOT_RUNNING",
            "HEARTBEAT_ABSENT_OR_EXPIRED",
            "LOCK_UNHELD",
            "CHROME_LEDGER_NOT_LIVE_OWNERSHIP_PROOF",
        ]
    return "UNCERTAIN", ["RUNTIME_STATE_CONFLICT"]


def atomic_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix="." + path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def verify_marker(path, evidence_sha256):
    try:
        marker = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("invalid stale runtime reconciliation marker") from exc
    if not isinstance(marker, dict):
        fail("invalid stale runtime reconciliation marker")
    if (
        marker.get("schema") != SCHEMA
        or marker.get("status") != "STALE_RUNTIME_RECONCILED"
        or marker.get("evidence_sha256") != evidence_sha256
        or marker.get("mutation_scope") != "LOCAL_MARKER_ONLY"
    ):
        fail("stale runtime reconciliation marker mismatch")


def result(evidence, now_epoch):
    status, reasons = classify(evidence, now_epoch)
    return {
        "schema": SCHEMA,
        "status": status,
        "reason_codes": reasons,
        "now_utc": dt.datetime.fromtimestamp(now_epoch, tz=dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "evidence_sha256": canonical_hash(evidence),
        "owner_task_id": evidence["owner_task_id"],
        "mission_id": evidence["mission_id"],
        "chrome_ledger_is_not_occupancy_proof": True,
    }


def reconcile(evidence, now_epoch, registry_root):
    output = result(evidence, now_epoch)
    if output["status"] != "STALE_RUNTIME":
        output["reconciliation"] = "NOT_ALLOWED"
        return output
    path = Path(registry_root) / (output["evidence_sha256"] + ".json")
    if path.is_file():
        verify_marker(path, output["evidence_sha256"])
        output["reconciliation"] = "ALREADY_RECORDED"
        output["marker_path"] = str(path)
        return output
    marker = {
        "schema": SCHEMA,
        "status": "STALE_RUNTIME_RECONCILED",
        "reconciled_at_utc": output["now_utc"],
        "evidence_sha256": output["evidence_sha256"],
        "reason_codes": output["reason_codes"],
        "evidence": evidence,
        "mutation_scope": "LOCAL_MARKER_ONLY",
    }
    atomic_write(path, marker)
    output["reconciliation"] = "RECORDED"
    output["marker_path"] = str(path)
    return output


def self_test():
    base = {
        "owner_task_id": "019fa29e-2cb5-70d0-9519-b6d993fe7e71",
        "mission_id": "reddit-example-20260727",
        "queue_state": "ACTIVE",
        "operation_stop_at": "2026-07-27T10:17:31Z",
        "task_state": "notLoaded",
        "heartbeat_state": "absent",
        "lock_state": "unheld",
        "chrome_ledger_state": "PENDING",
        "source_queue_path": "/example/legacy.json",
    }
    now = parse_utc("2026-07-27T12:00:00Z", "now_utc")
    assert classify(base, now)[0] == "STALE_RUNTIME"
    active = dict(base, heartbeat_state="future")
    assert classify(active, now)[0] == "ACTIVE_OWNER"
    unknown = dict(base, lock_state="unknown")
    assert classify(unknown, now)[0] == "UNCERTAIN"
    terminal = dict(base, queue_state="RETIRED")
    assert classify(terminal, now)[0] == "NO_FENCE"
    with tempfile.TemporaryDirectory() as temporary:
        first = reconcile(base, now, temporary)
        assert first["reconciliation"] == "RECORDED"
        second = reconcile(base, now, temporary)
        assert second["reconciliation"] == "ALREADY_RECORDED"
        assert not list(Path(temporary).glob("*.lock"))
    return {"status": "PASS", "schema": SCHEMA, "stale_runtime": "NON_DESTRUCTIVE_RECONCILIATION"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--now-utc")
    parser.add_argument("--reconcile", action="store_true")
    parser.add_argument("--registry-root", type=Path, default=DEFAULT_REGISTRY_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            if args.input or args.now_utc:
                fail("self-test cannot combine with input")
            print(json.dumps(self_test(), ensure_ascii=False, sort_keys=True))
            return 0
        if args.input is None or args.now_utc is None:
            fail("input and now_utc are required")
        evidence = load_evidence(args.input)
        now_epoch = parse_utc(args.now_utc, "now_utc")
        output = reconcile(evidence, now_epoch, args.registry_root) if args.reconcile else result(evidence, now_epoch)
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"schema": SCHEMA, "status": "INVALID", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
