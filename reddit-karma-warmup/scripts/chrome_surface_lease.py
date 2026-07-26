#!/usr/bin/env python3
"""Atomically lease one local Chrome control slot or task-owned tab surface."""

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time


DEFAULT_ROOT = Path.home() / ".codex" / "chrome-surface-leases"
VALID_KINDS = ("control", "tab")


def utc(epoch):
    return dt.datetime.fromtimestamp(epoch, tz=dt.timezone.utc).isoformat().replace("+00:00", "Z")


def safe_value(name, value):
    if not value or len(value) > 512 or "\x00" in value:
        raise ValueError("invalid " + name)
    return value


def record_path(root, kind, scope):
    digest = hashlib.sha256(scope.encode("utf-8")).hexdigest()
    return root / kind / (digest + ".json")


def read_record(path):
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def write_record(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="." + path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def emit(value, code=0):
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))
    return code


def active(record, now):
    try:
        expires_at = float(record.get("expires_at_epoch", 0)) if record else 0
    except (TypeError, ValueError):
        return False
    return bool(record and record.get("state") == "ACTIVE" and expires_at > now)


def command(args):
    root = Path(args.root).expanduser()
    scope = safe_value("scope", args.scope)
    path = record_path(root, args.kind, scope)
    lock_path = path.with_suffix(".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    owner = safe_value("owner_task_id", args.owner_task_id) if args.command != "inspect" else None
    lease_id = safe_value("lease_id", args.lease_id) if args.command != "inspect" else None
    deadline = time.monotonic() + args.wait_ms / 1000.0
    while True:
        busy_result = None
        with lock_path.open("a+") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            now = time.time()
            prior = read_record(path)
            base = {
                "kind": args.kind,
                "scope_sha256": hashlib.sha256(scope.encode("utf-8")).hexdigest(),
                "checked_at_utc": utc(now),
            }
            if args.command == "inspect":
                base["status"] = "ACTIVE" if active(prior, now) else "ABSENT_OR_EXPIRED"
                base["record"] = prior
                return emit(base)

            if args.command == "acquire":
                if active(prior, now) and (prior.get("owner_task_id") != owner or prior.get("lease_id") != lease_id):
                    base.update({
                        "status": "BUSY",
                        "owner_task_id": prior.get("owner_task_id"),
                        "expires_at_utc": utc(prior["expires_at_epoch"]),
                    })
                    busy_result = base
                else:
                    expires_at = now + args.ttl_seconds
                    record = {
                        "schema": "chrome_surface_lease/v1",
                        "state": "ACTIVE",
                        "kind": args.kind,
                        "scope_sha256": base["scope_sha256"],
                        "owner_task_id": owner,
                        "lease_id": lease_id,
                        "acquired_at_utc": utc(now),
                        "expires_at_epoch": expires_at,
                        "expires_at_utc": utc(expires_at),
                    }
                    write_record(path, record)
                    base.update({
                        "status": "RENEWED" if active(prior, now) else "ACQUIRED",
                        "owner_task_id": owner,
                        "lease_id": lease_id,
                        "expires_at_utc": record["expires_at_utc"],
                    })
                    return emit(base)
            elif not prior:
                base.update({"status": "ABSENT"})
                return emit(base)
            elif prior.get("owner_task_id") != owner or prior.get("lease_id") != lease_id:
                base.update({"status": "OWNER_MISMATCH", "owner_task_id": prior.get("owner_task_id")})
                return emit(base, code=4)
            else:
                prior["state"] = "RELEASED"
                prior["released_at_utc"] = utc(now)
                prior["expires_at_epoch"] = now
                prior["expires_at_utc"] = utc(now)
                write_record(path, prior)
                base.update({"status": "RELEASED", "owner_task_id": owner, "lease_id": lease_id})
                return emit(base)
        if busy_result is None or time.monotonic() >= deadline:
            return emit(busy_result, code=3)
        time.sleep(min(0.25, max(0.0, deadline - time.monotonic())))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("acquire", "release", "inspect"))
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--kind", choices=VALID_KINDS, required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--owner-task-id")
    parser.add_argument("--lease-id")
    parser.add_argument("--ttl-seconds", type=int, default=150)
    parser.add_argument("--wait-ms", type=int, default=0)
    args = parser.parse_args()
    if args.command != "inspect":
        if not args.owner_task_id or not args.lease_id:
            parser.error("--owner-task-id and --lease-id are required")
        if args.ttl_seconds < 1 or args.ttl_seconds > 86400:
            parser.error("--ttl-seconds must be in 1..86400")
        if args.wait_ms < 0 or args.wait_ms > 60000:
            parser.error("--wait-ms must be in 0..60000")
    try:
        return command(args)
    except ValueError as exc:
        return emit({"status": "INVALID", "error": str(exc)}, code=2)


if __name__ == "__main__":
    sys.exit(main())
