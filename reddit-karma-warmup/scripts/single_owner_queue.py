#!/usr/bin/env python3
"""Persist the one-task, five-unit Reddit runtime without controlling Chrome.

The queue is intentionally not a daemon, cross-task lock, scheduler, or browser
client. It provides a crash-safe, single-owner ledger for mission revisions and
safe-boundary hot-plug decisions. The owning `Reddit 运营台` records browser
boundaries before/after it uses Chrome; an unclosed boundary fails closed.
"""

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time


CODEX_HOME = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
DEFAULT_ROOT = CODEX_HOME / "reddit-karma-warmup" / "single-owner" / "queues"
LANE_ORDER = ("browsing", "comments", "posts", "follow-up", "presence")
SCHEMA = "reddit_single_owner_queue/v2"
HEX_256 = re.compile(r"^[0-9a-f]{64}$")
DECISIONS = ("RUN", "WATCH", "SKIP", "DEFER")
DEFAULT_RECHECK_MINUTES = {
    "browsing": 40,
    "comments": 60,
    "posts": 180,
    "follow-up": 90,
    "presence": 1440,
}
DEFAULT_AUTHORITY = {
    "browsing": "READ_ONLY",
    "comments": "RESEARCH_ONLY",
    "posts": "RESEARCH_ONLY",
    "follow-up": "RESEARCH_ONLY",
    "presence": "RESEARCH_ONLY",
}
ALLOWED_AUTHORITY = {
    "browsing": ("READ_ONLY", "VOTE_AUTHORIZED"),
    "comments": ("RESEARCH_ONLY", "COMMENT_AUTHORIZED"),
    "posts": ("RESEARCH_ONLY", "POST_AUTHORIZED"),
    "follow-up": ("RESEARCH_ONLY", "FOLLOWUP_AUTHORIZED"),
    "presence": ("RESEARCH_ONLY", "PRESENCE_AUTHORIZED"),
}


def utc(epoch):
    return dt.datetime.fromtimestamp(epoch, tz=dt.timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(name, value):
    value = required(name, value, 64)
    if not value.endswith("Z"):
        raise ValueError("invalid " + name)
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid " + name) from exc
    if parsed.tzinfo != dt.timezone.utc:
        raise ValueError("invalid " + name)
    return parsed.timestamp()


def configured_now(raw):
    return parse_utc("now_utc", raw) if raw is not None else time.time()


def recheck_minutes(raw, lane):
    if raw is None:
        return DEFAULT_RECHECK_MINUTES[lane]
    if not isinstance(raw, int) or isinstance(raw, bool) or not 20 <= raw <= 10080:
        raise ValueError("invalid next_due_minutes")
    return raw


def required(name, value, maximum=512):
    if not value or not isinstance(value, str) or len(value) > maximum or "\x00" in value:
        raise ValueError("invalid " + name)
    return value


def sha256_value(name, value):
    value = required(name, value, 64)
    if not HEX_256.fullmatch(value):
        raise ValueError("invalid " + name)
    return value


def canonical_hash(value):
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def canonical_units(raw, name, allow_empty=False):
    if not isinstance(raw, list) or (not raw and not allow_empty):
        raise ValueError("invalid " + name)
    if any(unit not in LANE_ORDER for unit in raw) or len(set(raw)) != len(raw):
        raise ValueError("invalid " + name)
    expected = [unit for unit in LANE_ORDER if unit in raw]
    if raw != expected:
        raise ValueError(name + " must use canonical unit order")
    return tuple(raw)


def load_envelope(path):
    try:
        envelope = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("invalid mission envelope") from exc
    if not isinstance(envelope, dict):
        raise ValueError("invalid mission envelope")
    stored_hash = sha256_value("mission_envelope_sha256", envelope.get("mission_envelope_sha256"))
    unsigned = dict(envelope)
    unsigned.pop("mission_envelope_sha256", None)
    if canonical_hash(unsigned) != stored_hash:
        raise ValueError("mission envelope hash mismatch")
    if envelope.get("schema") != "reddit_single_owner_mission/v1":
        raise ValueError("unknown mission envelope schema")
    if envelope.get("execution_topology") != "single_owner_v1":
        raise ValueError("not a single-owner envelope")
    mission_id = required("mission_id", envelope.get("mission_id"))
    account = required("account", envelope.get("account"))
    operation_start_at = required("operation_start_at", envelope.get("operation_start_at"), 64)
    operation_stop_at = required("operation_stop_at", envelope.get("operation_stop_at"), 64)
    start_epoch = parse_utc("operation_start_at", operation_start_at)
    stop_epoch = parse_utc("operation_stop_at", operation_stop_at)
    if stop_epoch <= start_epoch:
        raise ValueError("invalid mission time range")
    revision = envelope.get("mission_revision")
    if not isinstance(revision, int) or revision < 1:
        raise ValueError("invalid mission_revision")
    selected = canonical_units(envelope.get("selected_units"), "selected_units")
    paused = canonical_units(envelope.get("paused_units", []), "paused_units", allow_empty=True)
    if any(unit not in selected for unit in paused):
        raise ValueError("paused unit not selected")
    authority = envelope.get("unit_authority")
    if not isinstance(authority, dict) or set(authority) != set(selected):
        raise ValueError("invalid unit_authority")
    for unit, value in authority.items():
        if value not in ALLOWED_AUTHORITY[unit]:
            raise ValueError("invalid authority for " + unit)
    vote_policy = envelope.get("vote_policy")
    if vote_policy not in ("DISABLED", "BROWSING_ONLY"):
        raise ValueError("invalid vote policy")
    if vote_policy == "BROWSING_ONLY":
        if authority.get("browsing") != "VOTE_AUTHORIZED":
            raise ValueError("vote authority mismatch")
    elif authority.get("browsing") == "VOTE_AUTHORIZED":
        raise ValueError("vote policy mismatch")
    parent_hash = envelope.get("parent_envelope_sha256")
    if revision == 1:
        if parent_hash is not None:
            raise ValueError("initial envelope has parent")
    else:
        sha256_value("parent_envelope_sha256", parent_hash)
    changes = envelope.get("unit_changes")
    if not isinstance(changes, dict) or any(unit not in LANE_ORDER or action not in ("ADD", "PAUSE", "REMOVE", "RESUME") for unit, action in changes.items()):
        raise ValueError("invalid unit_changes")
    authority_changes = envelope.get("authority_changes")
    if not isinstance(authority_changes, dict):
        raise ValueError("invalid authority_changes")
    for unit, change in authority_changes.items():
        if unit not in LANE_ORDER or not isinstance(change, dict) or set(change) != {"from", "to"}:
            raise ValueError("invalid authority_changes")
        for value in (change["from"], change["to"]):
            if value is not None and value not in ALLOWED_AUTHORITY[unit]:
                raise ValueError("invalid authority change value")
    vote_policy_change = envelope.get("vote_policy_change")
    if vote_policy_change is not None:
        if not isinstance(vote_policy_change, dict) or set(vote_policy_change) != {"from", "to"}:
            raise ValueError("invalid vote_policy_change")
        if vote_policy_change["from"] not in ("DISABLED", "BROWSING_ONLY") or vote_policy_change["to"] not in ("DISABLED", "BROWSING_ONLY"):
            raise ValueError("invalid vote_policy_change")
    return {
        "mission_id": mission_id,
        "account": account,
        "operation_start_at": operation_start_at,
        "operation_stop_at": operation_stop_at,
        "operation_start_epoch": start_epoch,
        "operation_stop_epoch": stop_epoch,
        "mission_revision": revision,
        "mission_envelope_sha256": stored_hash,
        "parent_envelope_sha256": parent_hash,
        "selected_units": selected,
        "paused_units": paused,
        "unit_authority": authority,
        "vote_policy": vote_policy,
        "unit_changes": changes,
        "authority_changes": authority_changes,
        "vote_policy_change": vote_policy_change,
    }


def plan(selected, paused):
    return {unit: ("PAUSED" if unit in paused else "ACTIVE") if unit in selected else "REMOVED" for unit in LANE_ORDER}


def paths(root, scope):
    digest = hashlib.sha256(scope.encode("utf-8")).hexdigest()
    record = root / (digest + ".json")
    return record, record.with_suffix(".lock")


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


def read_record(path):
    if not path.exists():
        return None
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("malformed queue record") from exc
    if not isinstance(result, dict):
        raise ValueError("malformed queue record")
    return result


def unit_id(mission_id, lane, generation):
    return mission_id + ":" + lane + ":g" + str(generation)


def make_unit(record, lane, now, origin):
    record["unit_generations"][lane] += 1
    record["next_sequence"] += 1
    generation = record["unit_generations"][lane]
    return {
        "unit_id": unit_id(record["mission_id"], lane, generation),
        "lane": lane,
        "generation": generation,
        "sequence": record["next_sequence"],
        "status": "QUEUED",
        "owner_task_id": record["owner_task_id"],
        "origin": origin,
        "mission_revision": record["mission_revision"],
        "enqueued_at_utc": utc(now),
    }


def initial(scope, owner_task_id, envelope, now):
    record = {
        "schema": SCHEMA,
        "state": "READY",
        "scope_sha256": hashlib.sha256(scope.encode("utf-8")).hexdigest(),
        "owner_task_id": owner_task_id,
        "executor_task_id": owner_task_id,
        "mission_id": envelope["mission_id"],
        "account": envelope["account"],
        "operation_start_at": envelope["operation_start_at"],
        "operation_stop_at": envelope["operation_stop_at"],
        "operation_start_epoch": envelope["operation_start_epoch"],
        "operation_stop_epoch": envelope["operation_stop_epoch"],
        "mission_revision": envelope["mission_revision"],
        "mission_envelope_sha256": envelope["mission_envelope_sha256"],
        "lane_order": list(LANE_ORDER),
        "unit_plan": plan(envelope["selected_units"], envelope["paused_units"]),
        "unit_authority": envelope["unit_authority"],
        "vote_policy": envelope["vote_policy"],
        "unit_generations": {unit: 0 for unit in LANE_ORDER},
        "canary": {"state": "PENDING", "proof_sha256": None},
        "chrome_release": {"state": "PENDING", "proof_sha256": None},
        "browser_boundary": None,
        "active_read_batch": None,
        "read_batch_history": [],
        "frozen_action_keys": [],
        "next_sequence": 0,
        "queue": [],
        "active": None,
        "history": [],
        "unit_schedule": {
            lane: {
                "next_due_at_utc": utc(envelope["operation_start_epoch"]),
                "next_due_epoch": envelope["operation_start_epoch"],
                "last_decision": None,
                "last_decision_reason": None,
            }
            for lane in LANE_ORDER
        },
        "wake": None,
        "wake_history": [],
        "revision_history": [],
        "updated_at_utc": utc(now),
    }
    return record


def all_units(record):
    return record["queue"] + record["history"] + ([record["active"]] if record["active"] else [])


def due_units(record, now):
    return [
        lane for lane in LANE_ORDER
        if record["unit_plan"][lane] == "ACTIVE"
        and record["unit_schedule"][lane]["next_due_epoch"] <= now
    ]


def next_due(record, lane, now, minutes=None):
    delay = recheck_minutes(minutes, lane)
    record["unit_schedule"][lane]["next_due_epoch"] = now + delay * 60
    record["unit_schedule"][lane]["next_due_at_utc"] = utc(now + delay * 60)
    return delay


def archive_wake(record, outcome, now):
    wake = record.get("wake")
    if wake is None:
        return
    wake["outcome"] = outcome
    wake["closed_at_utc"] = utc(now)
    record["wake_history"].append(wake)
    record["wake"] = None


def active_yielded_item(record):
    yielded = [item for item in record["queue"] if item.get("status") == "YIELDED"]
    return min(yielded, key=lambda item: (LANE_ORDER.index(item["lane"]), item["sequence"])) if yielded else None


def decisions_complete(wake):
    return set(wake["decisions"]) == set(wake["due_units"])


def record_decision(record, wake, lane, decision, reason, now, minutes):
    value = {
        "decision": decision,
        "reason": reason,
        "decided_at_utc": utc(now),
        "next_due_minutes": minutes,
    }
    wake["decisions"][lane] = value
    schedule = record["unit_schedule"][lane]
    schedule["last_decision"] = decision
    schedule["last_decision_reason"] = reason
    if decision != "RUN":
        next_due(record, lane, now, minutes)
    return value


def validate_record(record, scope, owner_task_id):
    if record.get("schema") != SCHEMA or record.get("state") not in ("READY", "RETIRED"):
        raise ValueError("unknown queue record")
    if record.get("scope_sha256") != hashlib.sha256(scope.encode("utf-8")).hexdigest():
        raise ValueError("scope mismatch")
    if record.get("owner_task_id") != owner_task_id or record.get("executor_task_id") != owner_task_id:
        raise ValueError("single owner mismatch")
    if record.get("lane_order") != list(LANE_ORDER):
        raise ValueError("lane order mismatch")
    if not isinstance(record.get("operation_start_epoch"), (int, float)) or not isinstance(record.get("operation_stop_epoch"), (int, float)) or record["operation_stop_epoch"] <= record["operation_start_epoch"]:
        raise ValueError("invalid mission time")
    if set(record.get("unit_plan", {})) != set(LANE_ORDER) or any(state not in ("ACTIVE", "PAUSED", "REMOVED") for state in record["unit_plan"].values()):
        raise ValueError("invalid unit plan")
    if not isinstance(record.get("queue"), list) or not isinstance(record.get("history"), list):
        raise ValueError("invalid queue lists")
    schedule = record.get("unit_schedule")
    if not isinstance(schedule, dict) or set(schedule) != set(LANE_ORDER):
        raise ValueError("invalid unit schedule")
    for lane, state in schedule.items():
        if not isinstance(state, dict) or not isinstance(state.get("next_due_epoch"), (int, float)) or not isinstance(state.get("next_due_at_utc"), str):
            raise ValueError("invalid unit schedule")
    wake = record.get("wake")
    if wake is not None:
        if not isinstance(wake, dict) or wake.get("state") not in ("OPEN", "READY_TO_RUN", "RECOVERY_PENDING"):
            raise ValueError("invalid wake")
        if not isinstance(wake.get("wake_id"), str) or not isinstance(wake.get("due_units"), list) or any(lane not in LANE_ORDER for lane in wake["due_units"]):
            raise ValueError("invalid wake")
        if not isinstance(wake.get("expected_at_utc"), str) or not isinstance(wake.get("actual_at_utc"), str):
            raise ValueError("invalid wake timing")
        if not isinstance(wake.get("trigger_delta_seconds"), (int, float)) or wake.get("trigger_state") not in ("WITHIN_TOLERANCE", "RECOMPUTED_FROM_ACTUAL"):
            raise ValueError("invalid wake trigger state")
        if not isinstance(wake.get("decisions"), dict) or any(lane not in wake["due_units"] for lane in wake["decisions"]):
            raise ValueError("invalid wake decisions")
        for lane, value in wake["decisions"].items():
            if not isinstance(value, dict) or value.get("decision") not in DECISIONS:
                raise ValueError("invalid wake decision")
            if not isinstance(value.get("reason"), str):
                raise ValueError("invalid wake decision reason")
        if wake.get("run_unit_id") is not None and not isinstance(wake["run_unit_id"], str):
            raise ValueError("invalid wake run unit")
    if not isinstance(record.get("wake_history"), list):
        raise ValueError("invalid wake history")
    if record.get("canary", {}).get("state") not in ("PENDING", "PASSED"):
        raise ValueError("invalid canary")
    if record.get("chrome_release", {}).get("state") not in ("PENDING", "RELEASED"):
        raise ValueError("invalid chrome release")
    if record.get("active") is not None and record["active"].get("status") != "RUNNING":
        raise ValueError("invalid active unit")
    batch = record.get("active_read_batch")
    if batch is not None:
        if record.get("active") is None or batch.get("unit_id") != record["active"].get("unit_id"):
            raise ValueError("orphan read batch")
        if batch.get("read_tab_count") not in (1, 2):
            raise ValueError("invalid read batch size")
    boundary = record.get("browser_boundary")
    if boundary is not None:
        if record.get("active") is None or boundary.get("unit_id") != record["active"].get("unit_id"):
            raise ValueError("orphan browser boundary")
    ids = []
    for unit in all_units(record):
        if not isinstance(unit, dict) or unit.get("lane") not in LANE_ORDER or not unit.get("unit_id"):
            raise ValueError("invalid queue unit")
        ids.append(unit["unit_id"])
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate unit id")
    for key in record.get("frozen_action_keys", []):
        sha256_value("frozen action key", key)


def same_envelope(record, envelope):
    return record["mission_id"] == envelope["mission_id"] and record["mission_revision"] == envelope["mission_revision"] and record["mission_envelope_sha256"] == envelope["mission_envelope_sha256"]


def public(record, status, now, detail=None):
    output = {
        "schema": SCHEMA,
        "status": status,
        "state": record["state"],
        "scope_sha256": record["scope_sha256"],
        "owner_task_id": record["owner_task_id"],
        "mission_id": record["mission_id"],
        "mission_revision": record["mission_revision"],
        "mission_envelope_sha256": record["mission_envelope_sha256"],
        "unit_plan": record["unit_plan"],
        "canary_state": record["canary"]["state"],
        "chrome_release_state": record["chrome_release"]["state"],
        "active_unit_id": (record.get("active") or {}).get("unit_id"),
        "active_read_batch_unit_id": (record.get("active_read_batch") or {}).get("unit_id"),
        "browser_boundary_in_flight": record.get("browser_boundary") is not None,
        "queued_count": len(record["queue"]),
        "history_count": len(record["history"]),
        "wake_id": (record.get("wake") or {}).get("wake_id"),
        "wake_state": (record.get("wake") or {}).get("state"),
        "due_units": due_units(record, now),
        "unit_next_due_at_utc": {
            lane: record["unit_schedule"][lane]["next_due_at_utc"]
            for lane in LANE_ORDER
        },
        "frozen_action_key_count": len(record["frozen_action_keys"]),
        "updated_at_utc": utc(now),
    }
    if detail:
        output.update(detail)
    return output


def select_next(queue):
    yielded = [item for item in queue if item.get("status") == "YIELDED"]
    if yielded:
        return min(yielded, key=lambda item: (LANE_ORDER.index(item["lane"]), item["sequence"]))
    queued = [item for item in queue if item.get("status") == "QUEUED"]
    return min(queued, key=lambda item: (LANE_ORDER.index(item["lane"]), item["sequence"])) if queued else None


def archive_open_units(record, lane, status, now, revision):
    changed = []
    for unit in list(record["queue"]):
        if unit["lane"] == lane and unit["status"] in ("QUEUED", "YIELDED"):
            record["queue"].remove(unit)
            unit["status"] = status
            unit["closed_at_utc"] = utc(now)
            unit["closed_by_revision"] = revision
            record["history"].append(unit)
            changed.append(unit["unit_id"])
    return changed


def expected_change(before, after):
    if before == after:
        return None
    if before == "REMOVED" and after == "ACTIVE":
        return "ADD"
    if before == "ACTIVE" and after == "PAUSED":
        return "PAUSE"
    if before == "PAUSED" and after == "ACTIVE":
        return "RESUME"
    if after == "REMOVED":
        return "REMOVE"
    raise ValueError("unsupported unit transition")


def safe_boundary(record):
    if record["state"] == "RETIRED":
        return False, "MISSION_RETIRED"
    if record.get("active") is not None:
        return False, "ACTIVE_UNIT"
    if record.get("active_read_batch") is not None:
        return False, "READ_BATCH_ACTIVE"
    if record.get("browser_boundary") is not None:
        return False, "BROWSER_BOUNDARY_IN_FLIGHT"
    if record.get("wake") is not None:
        return False, "WAKE_DECISION_OPEN"
    return True, None


def apply_revision(record, envelope, now):
    if envelope["mission_id"] != record["mission_id"] or envelope["account"] != record["account"]:
        return "MISSION_MISMATCH", {}
    if envelope["mission_revision"] != record["mission_revision"] + 1:
        return "REVISION_SEQUENCE_INVALID", {}
    if envelope["parent_envelope_sha256"] != record["mission_envelope_sha256"]:
        return "PARENT_HASH_MISMATCH", {}
    boundary_ok, reason = safe_boundary(record)
    if not boundary_ok:
        return "HOTPLUG_DEFERRED_UNSAFE_BOUNDARY", {"unsafe_reason": reason}
    desired = plan(envelope["selected_units"], envelope["paused_units"])
    expected = {}
    for lane in LANE_ORDER:
        change = expected_change(record["unit_plan"][lane], desired[lane])
        if change:
            expected[lane] = change
    if envelope["unit_changes"] != expected:
        return "UNIT_CHANGE_MISMATCH", {"expected_unit_changes": expected}
    expected_authority_changes = {}
    for lane in LANE_ORDER:
        before = record["unit_authority"].get(lane)
        after = envelope["unit_authority"].get(lane) if lane in envelope["selected_units"] else None
        if before != after:
            expected_authority_changes[lane] = {"from": before, "to": after}
    if envelope["authority_changes"] != expected_authority_changes:
        return "AUTHORITY_CHANGE_MISMATCH", {"expected_authority_changes": expected_authority_changes}
    expected_vote_policy_change = None
    if record["vote_policy"] != envelope["vote_policy"]:
        expected_vote_policy_change = {"from": record["vote_policy"], "to": envelope["vote_policy"]}
    if envelope["vote_policy_change"] != expected_vote_policy_change:
        return "VOTE_POLICY_CHANGE_MISMATCH", {"expected_vote_policy_change": expected_vote_policy_change}
    history_ids = []
    scheduled_due_units = []
    for lane in LANE_ORDER:
        before, after = record["unit_plan"][lane], desired[lane]
        if before == after:
            continue
        if after == "ACTIVE":
            record["unit_plan"][lane] = "ACTIVE"
            record["unit_schedule"][lane] = {
                "next_due_at_utc": utc(now),
                "next_due_epoch": now,
                "last_decision": "RESUME" if before == "PAUSED" else "ADD",
                "last_decision_reason": "REVISION_" + expected_change(before, after),
            }
            scheduled_due_units.append(lane)
        elif after == "PAUSED":
            history_ids.extend(archive_open_units(record, lane, "PAUSED_BY_REVISION", now, envelope["mission_revision"]))
            record["unit_plan"][lane] = "PAUSED"
        elif after == "REMOVED":
            history_ids.extend(archive_open_units(record, lane, "REMOVED_BY_REVISION", now, envelope["mission_revision"]))
            record["unit_plan"][lane] = "REMOVED"
    record["revision_history"].append({
        "from_revision": record["mission_revision"],
        "to_revision": envelope["mission_revision"],
        "from_envelope_sha256": record["mission_envelope_sha256"],
        "to_envelope_sha256": envelope["mission_envelope_sha256"],
        "unit_changes": expected,
        "authority_changes": expected_authority_changes,
        "vote_policy_change": expected_vote_policy_change,
        "archived_unit_ids": history_ids,
        "scheduled_due_units": scheduled_due_units,
        "applied_at_utc": utc(now),
    })
    record["mission_revision"] = envelope["mission_revision"]
    record["mission_envelope_sha256"] = envelope["mission_envelope_sha256"]
    record["unit_authority"] = envelope["unit_authority"]
    record["vote_policy"] = envelope["vote_policy"]
    record["updated_at_utc"] = utc(now)
    return "REVISION_APPLIED", {
        "unit_changes": expected,
        "authority_changes": expected_authority_changes,
        "vote_policy_change": expected_vote_policy_change,
        "scheduled_due_units": scheduled_due_units,
        "archived_unit_ids": history_ids,
    }


def command(args):
    root = Path(args.root).expanduser()
    scope = required("scope", args.scope)
    owner_task_id = required("owner_task_id", args.owner_task_id)
    envelope = load_envelope(args.mission_envelope)
    record_path, lock_path = paths(root, scope)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        now = configured_now(args.now_utc)
        record = read_record(record_path)
        if record is None:
            if args.command != "bootstrap":
                return {"schema": SCHEMA, "status": "BOOTSTRAP_REQUIRED", "updated_at_utc": utc(now)}
            if envelope["mission_revision"] != 1:
                return {"schema": SCHEMA, "status": "INITIAL_REVISION_REQUIRED", "updated_at_utc": utc(now)}
            record = initial(scope, owner_task_id, envelope, now)
            atomic_write(record_path, record)
            return public(record, "BOOTSTRAPPED", now)
        validate_record(record, scope, owner_task_id)
        if args.command == "apply-revision":
            status, detail = apply_revision(record, envelope, now)
            if status == "REVISION_APPLIED":
                atomic_write(record_path, record)
            return public(record, status, now, detail)
        if not same_envelope(record, envelope):
            return public(record, "MISSION_REVISION_MISMATCH", now)
        if args.command == "bootstrap":
            return public(record, "BOOTSTRAP_EXISTS", now)
        if args.command == "inspect":
            return public(record, "INSPECT", now, {"queue_lanes": [item["lane"] for item in record["queue"]]})
        if record["state"] == "RETIRED":
            return public(record, "RETIRED", now)
        if args.command == "canary-pass":
            if record["canary"]["state"] == "PASSED":
                return public(record, "CANARY_ALREADY_PASSED", now)
            record["canary"] = {"state": "PASSED", "proof_sha256": sha256_value("proof_sha256", args.proof_sha256), "passed_at_utc": utc(now)}
            record["updated_at_utc"] = utc(now)
            atomic_write(record_path, record)
            return public(record, "CANARY_PASSED", now)
        if args.command == "wake-open":
            if record["canary"]["state"] != "PASSED":
                return public(record, "CANARY_REQUIRED", now)
            if now >= record["operation_stop_epoch"]:
                return public(record, "DEADLINE_REACHED", now)
            if record.get("active") is not None:
                return public(record, "ACTIVE_UNIT_EXISTS", now)
            if record.get("wake") is not None:
                return public(record, "WAKE_ALREADY_OPEN", now)
            wake_id = required("wake_id", args.wake_id, 256)
            expected_at = parse_utc("expected_at_utc", args.expected_at_utc)
            trigger_delta_seconds = now - expected_at
            trigger_state = "WITHIN_TOLERANCE" if abs(trigger_delta_seconds) <= 300 else "RECOMPUTED_FROM_ACTUAL"
            timing = {
                "expected_at_utc": utc(expected_at),
                "actual_at_utc": utc(now),
                "trigger_delta_seconds": trigger_delta_seconds,
                "trigger_state": trigger_state,
            }
            yielded = active_yielded_item(record)
            if yielded is not None:
                record["wake"] = {
                    "wake_id": wake_id,
                    "state": "RECOVERY_PENDING",
                    "opened_at_utc": utc(now),
                    **timing,
                    "due_units": [yielded["lane"]],
                    "decisions": {
                        yielded["lane"]: {
                            "decision": "RUN",
                            "reason": "YIELDED_RECOVERY_FIRST",
                            "decided_at_utc": utc(now),
                            "next_due_minutes": yielded.get("next_due_minutes", DEFAULT_RECHECK_MINUTES[yielded["lane"]]),
                        }
                    },
                    "run_unit_id": yielded["unit_id"],
                }
                record["updated_at_utc"] = utc(now)
                atomic_write(record_path, record)
                return public(record, "WAKE_RECOVERY_REQUIRED", now, {"unit_id": yielded["unit_id"], "lane": yielded["lane"], "trigger_state": trigger_state, "trigger_delta_seconds": trigger_delta_seconds})
            due = due_units(record, now)
            if not due:
                return public(record, "WAKE_NOT_DUE", now)
            record["wake"] = {
                "wake_id": wake_id,
                "state": "OPEN",
                "opened_at_utc": utc(now),
                **timing,
                "due_units": due,
                "decisions": {},
                "run_unit_id": None,
            }
            record["updated_at_utc"] = utc(now)
            atomic_write(record_path, record)
            return public(record, "WAKE_OPENED", now, {"wake_id": wake_id, "due_units": due, "trigger_state": trigger_state, "trigger_delta_seconds": trigger_delta_seconds})
        if args.command == "decide":
            wake = record.get("wake")
            if wake is None:
                return public(record, "WAKE_REQUIRED", now)
            if wake.get("state") != "OPEN":
                return public(record, "WAKE_NOT_DECIDABLE", now)
            if required("wake_id", args.wake_id, 256) != wake["wake_id"]:
                return public(record, "WAKE_ID_MISMATCH", now)
            lane = required("unit", args.unit, 64)
            if lane not in wake["due_units"]:
                return public(record, "UNIT_NOT_DUE", now, {"unit": lane})
            if lane in wake["decisions"]:
                return public(record, "UNIT_ALREADY_DECIDED", now, {"unit": lane})
            decision = required("decision", args.decision, 16)
            if decision not in DECISIONS:
                raise ValueError("invalid decision")
            if decision == "RUN" and wake.get("run_unit_id") is not None:
                return public(record, "WAKE_RUN_ALREADY_SELECTED", now)
            reason = required("reason", args.reason, 1024)
            minutes = recheck_minutes(args.next_due_minutes, lane)
            result = record_decision(record, wake, lane, decision, reason, now, minutes)
            if decision == "RUN":
                item = make_unit(record, lane, now, "DECISION:" + wake["wake_id"])
                item["next_due_minutes"] = minutes
                record["queue"].append(item)
                wake["run_unit_id"] = item["unit_id"]
                result["unit_id"] = item["unit_id"]
            wake_closed = False
            if decisions_complete(wake):
                if wake.get("run_unit_id") is not None:
                    wake["state"] = "READY_TO_RUN"
                else:
                    archive_wake(record, "NO_RUN", now)
                    wake_closed = True
            record["updated_at_utc"] = utc(now)
            atomic_write(record_path, record)
            return public(record, "DECISION_RECORDED", now, {
                "unit": lane,
                "decision": decision,
                "wake_closed": wake_closed,
                "unit_id": result.get("unit_id"),
            })
        if args.command == "start":
            if record["canary"]["state"] != "PASSED":
                return public(record, "CANARY_REQUIRED", now)
            if record["active"] is not None:
                return public(record, "ACTIVE_UNIT_EXISTS", now)
            wake = record.get("wake")
            if wake is None:
                return public(record, "WAKE_REQUIRED", now)
            if wake.get("state") not in ("READY_TO_RUN", "RECOVERY_PENDING"):
                return public(record, "WAKE_DECISIONS_INCOMPLETE", now)
            item = next((candidate for candidate in record["queue"] if candidate["unit_id"] == wake.get("run_unit_id")), None)
            if item is None:
                return public(record, "WAKE_RUN_UNIT_MISSING", now)
            record["queue"].remove(item)
            was_yielded = item["status"] == "YIELDED"
            item["status"] = "RUNNING"
            item["resumed_at_utc" if was_yielded else "started_at_utc"] = utc(now)
            record["active"] = item
            record["updated_at_utc"] = utc(now)
            atomic_write(record_path, record)
            return public(record, "RESUMED" if was_yielded else "STARTED", now, {"unit_id": item["unit_id"], "lane": item["lane"]})
        if args.command == "boundary-open":
            active = record.get("active")
            if active is None or active.get("unit_id") != required("unit_id", args.unit_id):
                return public(record, "ACTIVE_UNIT_MISMATCH", now)
            if record.get("browser_boundary") is not None:
                return public(record, "BROWSER_BOUNDARY_ACTIVE", now)
            if record.get("active_read_batch") is not None:
                return public(record, "READ_BATCH_ACTIVE", now)
            kind = required("boundary_kind", args.boundary_kind, 64)
            if kind not in ("metadata", "tab_create", "navigate", "content_read", "locator", "input", "click", "submit", "verify", "finalize"):
                raise ValueError("invalid boundary_kind")
            boundary_id = required("boundary_id", args.boundary_id, 256)
            record["browser_boundary"] = {"boundary_id": boundary_id, "unit_id": active["unit_id"], "kind": kind, "opened_at_utc": utc(now)}
            record["updated_at_utc"] = utc(now)
            atomic_write(record_path, record)
            return public(record, "BROWSER_BOUNDARY_OPEN", now, {"boundary_id": boundary_id, "boundary_kind": kind})
        if args.command == "boundary-settle":
            boundary = record.get("browser_boundary")
            if boundary is None or boundary.get("boundary_id") != required("boundary_id", args.boundary_id, 256):
                return public(record, "BROWSER_BOUNDARY_NOT_FOUND", now)
            outcome = required("boundary_outcome", args.boundary_outcome, 32)
            if outcome not in ("ACKNOWLEDGED", "UNKNOWN", "FAILED"):
                raise ValueError("invalid boundary_outcome")
            record["browser_boundary"] = None
            if outcome != "ACKNOWLEDGED":
                record["active"]["last_boundary_outcome"] = outcome
            record["updated_at_utc"] = utc(now)
            atomic_write(record_path, record)
            return public(record, "BROWSER_BOUNDARY_SETTLED", now, {"boundary_outcome": outcome})
        if args.command == "read-batch-open":
            active = record.get("active")
            if active is None or active.get("unit_id") != required("unit_id", args.unit_id):
                return public(record, "ACTIVE_UNIT_MISMATCH", now)
            if record["canary"]["state"] != "PASSED":
                return public(record, "CANARY_REQUIRED", now)
            if record.get("browser_boundary") is not None or record.get("active_read_batch") is not None:
                return public(record, "READ_BATCH_UNSAFE", now)
            if args.read_tab_count not in (1, 2):
                raise ValueError("read_tab_count must be 1 or 2")
            record["active_read_batch"] = {"unit_id": active["unit_id"], "read_tab_count": args.read_tab_count, "opened_at_utc": utc(now)}
            record["updated_at_utc"] = utc(now)
            atomic_write(record_path, record)
            return public(record, "READ_BATCH_OPEN", now)
        if args.command == "read-batch-settle":
            batch = record.get("active_read_batch")
            if batch is None or batch.get("unit_id") != required("unit_id", args.unit_id):
                return public(record, "READ_BATCH_NOT_FOUND", now)
            outcome = required("read_batch_outcome", args.read_batch_outcome, 16)
            if outcome not in ("VERIFIED", "UNKNOWN"):
                raise ValueError("invalid read_batch_outcome")
            batch["outcome"] = outcome
            batch["proof_sha256"] = sha256_value("proof_sha256", args.proof_sha256)
            batch["settled_at_utc"] = utc(now)
            record["read_batch_history"].append(batch)
            record["active_read_batch"] = None
            record["updated_at_utc"] = utc(now)
            atomic_write(record_path, record)
            return public(record, "READ_BATCH_SETTLED", now, {"read_batch_outcome": outcome})
        if args.command == "freeze-action":
            active = record.get("active")
            if active is None or active.get("unit_id") != required("unit_id", args.unit_id):
                return public(record, "ACTIVE_UNIT_MISMATCH", now)
            key = sha256_value("action_key", args.action_key)
            if key in record["frozen_action_keys"]:
                return public(record, "ACTION_KEY_ALREADY_FROZEN", now, {"action_key": key})
            record["frozen_action_keys"].append(key)
            active.setdefault("frozen_action_keys", []).append(key)
            record["updated_at_utc"] = utc(now)
            atomic_write(record_path, record)
            return public(record, "ACTION_KEY_FROZEN", now, {"action_key": key})
        if args.command in ("complete", "skip", "block", "yield"):
            active = record.get("active")
            if active is None or active.get("unit_id") != required("unit_id", args.unit_id):
                return public(record, "ACTIVE_UNIT_MISMATCH", now)
            if record.get("browser_boundary") is not None or record.get("active_read_batch") is not None:
                return public(record, "UNIT_BOUNDARY_UNSETTLED", now)
            terminal = {"complete": "COMPLETED", "skip": "SKIPPED", "block": "BLOCKED", "yield": "YIELDED"}[args.command]
            record["active"] = None
            active["status"] = terminal
            active["closed_at_utc"] = utc(now)
            if terminal == "YIELDED":
                record["queue"].append(active)
                archive_wake(record, "YIELDED", now)
            else:
                record["history"].append(active)
                next_due(record, active["lane"], now, active.get("next_due_minutes"))
                archive_wake(record, terminal, now)
            record["updated_at_utc"] = utc(now)
            atomic_write(record_path, record)
            return public(record, terminal, now, {"unit_id": active["unit_id"]})
        if args.command == "release-tabs":
            if record.get("active") is not None or record.get("queue") or record.get("wake") is not None or record.get("active_read_batch") is not None or record.get("browser_boundary") is not None:
                return public(record, "WORK_REMAINS", now)
            if record["chrome_release"]["state"] == "RELEASED":
                return public(record, "TABS_ALREADY_RELEASED", now)
            record["chrome_release"] = {"state": "RELEASED", "proof_sha256": sha256_value("proof_sha256", args.proof_sha256), "released_at_utc": utc(now)}
            record["updated_at_utc"] = utc(now)
            atomic_write(record_path, record)
            return public(record, "TABS_RELEASED", now)
        if args.command == "retire":
            if record.get("active") is not None or record.get("queue") or record.get("wake") is not None or record.get("active_read_batch") is not None or record.get("browser_boundary") is not None:
                return public(record, "WORK_REMAINS", now)
            if record["chrome_release"]["state"] != "RELEASED":
                return public(record, "CHROME_RELEASE_REQUIRED", now)
            record["state"] = "RETIRED"
            record["updated_at_utc"] = utc(now)
            atomic_write(record_path, record)
            return public(record, "RETIRED", now)
        raise ValueError("unknown command")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=(
        "bootstrap", "inspect", "apply-revision", "canary-pass", "wake-open", "decide", "start",
        "boundary-open", "boundary-settle", "read-batch-open", "read-batch-settle",
        "freeze-action", "complete", "skip", "block", "yield", "release-tabs", "retire",
    ))
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--owner-task-id", required=True)
    parser.add_argument("--mission-envelope", required=True, type=Path)
    parser.add_argument("--unit-id")
    parser.add_argument("--proof-sha256")
    parser.add_argument("--read-tab-count", type=int)
    parser.add_argument("--read-batch-outcome")
    parser.add_argument("--boundary-id")
    parser.add_argument("--boundary-kind")
    parser.add_argument("--boundary-outcome")
    parser.add_argument("--action-key")
    parser.add_argument("--wake-id")
    parser.add_argument("--unit")
    parser.add_argument("--decision")
    parser.add_argument("--reason")
    parser.add_argument("--next-due-minutes", type=int)
    parser.add_argument("--now-utc")
    parser.add_argument("--expected-at-utc")
    args = parser.parse_args()
    try:
        result = command(args)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    except (OSError, ValueError) as exc:
        print(json.dumps({"schema": SCHEMA, "status": "INVALID", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
