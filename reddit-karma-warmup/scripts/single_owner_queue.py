#!/usr/bin/env python3
"""Persist one Reddit task's five internal units without controlling Chrome.

This is a local state helper, not a scheduler, daemon, browser client, lock
service, or cross-task dispatcher. The visible Reddit operating task owns the
mission heartbeat and calls this helper before/after one bounded Chrome packet.
"""

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


CODEX_HOME = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
DEFAULT_ROOT = CODEX_HOME / "reddit-karma-warmup" / "single-owner" / "missions"
UNIT_ORDER = ("browsing", "comments", "posts", "follow-up", "presence")
SCHEMA = "reddit_single_owner_queue/v4"
HEARTBEAT_INTERVAL_MINUTES = 15
HEARTBEAT_GRID_SECONDS = HEARTBEAT_INTERVAL_MINUTES * 60
DECISIONS = ("RUN", "WATCH", "SKIP", "DEFER")
OUTCOMES = ("COMPLETED", "SKIPPED", "BLOCKED", "YIELDED")
OBJECTIVE_STATES = (
    "RESEARCH_ONLY",
    "PENDING",
    "CANDIDATES_READY",
    "ACTION_ELIGIBLE",
    "ACTION_VERIFIED",
    "MATERIAL_REQUIRED",
    "RULE_BLOCKED",
    "SUBMISSION_UNCERTAIN",
    "NOT_APPLICABLE",
)
PARKED_OBJECTIVE_STATES = {
    "ACTION_VERIFIED",
    "MATERIAL_REQUIRED",
    "RULE_BLOCKED",
    "SUBMISSION_UNCERTAIN",
    "NOT_APPLICABLE",
}
DEFAULT_RECHECK_MINUTES = {
    "browsing": 30,
    "comments": 45,
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


def outward_authority(unit, authority):
    return authority != DEFAULT_AUTHORITY[unit]


def initial_objective(unit, plan, authority):
    if plan != "ACTIVE":
        return "NOT_APPLICABLE"
    if unit == "browsing":
        return "PENDING"
    if not outward_authority(unit, authority):
        return "RESEARCH_ONLY"
    if unit in ("follow-up", "presence"):
        return "NOT_APPLICABLE"
    return "PENDING"


def due_objective(value):
    return value not in PARKED_OBJECTIVE_STATES


def utc(epoch):
    return dt.datetime.fromtimestamp(epoch, tz=dt.timezone.utc).isoformat().replace("+00:00", "Z")


def require_text(name, value, maximum=512):
    if not isinstance(value, str) or not value or len(value) > maximum or "\x00" in value:
        raise ValueError("invalid " + name)
    return value


def sha256_value(name, value):
    value = require_text(name, value, 64)
    if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise ValueError("invalid " + name)
    return value


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def parse_utc(name, value):
    value = require_text(name, value, 64)
    if not value.endswith("Z"):
        raise ValueError("invalid " + name)
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid " + name) from exc
    if parsed.tzinfo != dt.timezone.utc:
        raise ValueError("invalid " + name)
    return parsed.timestamp()


def now_epoch(value):
    return parse_utc("now_utc", value) if value else time.time()


def canonical_units(raw, name, allow_empty=False):
    if not isinstance(raw, list) or (not raw and not allow_empty):
        raise ValueError("invalid " + name)
    if any(unit not in UNIT_ORDER for unit in raw) or len(raw) != len(set(raw)):
        raise ValueError("invalid " + name)
    if raw != [unit for unit in UNIT_ORDER if unit in raw]:
        raise ValueError(name + " must use canonical unit order")
    return tuple(raw)


def load_envelope(path):
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("invalid mission envelope") from exc
    if not isinstance(raw, dict) or raw.get("schema") != "reddit_single_owner_mission/v1":
        raise ValueError("invalid mission envelope")
    unsigned = dict(raw)
    stored_hash = sha256_value("mission_envelope_sha256", unsigned.pop("mission_envelope_sha256", None))
    if canonical_hash(unsigned) != stored_hash or raw.get("execution_topology") != "single_owner_v1":
        raise ValueError("mission envelope integrity mismatch")
    selected = canonical_units(raw.get("selected_units"), "selected_units")
    paused = canonical_units(raw.get("paused_units", []), "paused_units", allow_empty=True)
    if any(unit not in selected for unit in paused):
        raise ValueError("paused unit not selected")
    authority = raw.get("unit_authority")
    if not isinstance(authority, dict) or set(authority) != set(selected):
        raise ValueError("invalid unit_authority")
    for unit in selected:
        if authority[unit] not in ALLOWED_AUTHORITY[unit]:
            raise ValueError("invalid authority")
    vote_policy = raw.get("vote_policy")
    if vote_policy not in ("DISABLED", "BROWSING_ONLY"):
        raise ValueError("invalid vote policy")
    if (vote_policy == "BROWSING_ONLY") != (authority.get("browsing") == "VOTE_AUTHORIZED"):
        raise ValueError("vote policy mismatch")
    start = parse_utc("operation_start_at", raw.get("operation_start_at"))
    stop = parse_utc("operation_stop_at", raw.get("operation_stop_at"))
    if stop <= start:
        raise ValueError("invalid operation range")
    revision = raw.get("mission_revision")
    if not isinstance(revision, int) or revision < 1:
        raise ValueError("invalid revision")
    return {
        "mission_id": require_text("mission_id", raw.get("mission_id")),
        "account": require_text("account", raw.get("account")),
        "mission_revision": revision,
        "mission_envelope_sha256": stored_hash,
        "operation_start_at": raw["operation_start_at"],
        "operation_stop_at": raw["operation_stop_at"],
        "operation_start_epoch": start,
        "operation_stop_epoch": stop,
        "selected_units": selected,
        "paused_units": paused,
        "unit_authority": authority,
        "vote_policy": vote_policy,
    }


def paths(root, scope):
    digest = hashlib.sha256(require_text("scope", scope).encode("utf-8")).hexdigest()
    state_path = Path(root) / (digest + ".json")
    return state_path, state_path.with_suffix(".lock")


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


def read_state(path):
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("malformed mission state") from exc
    if not isinstance(value, dict):
        raise ValueError("malformed mission state")
    return value


def state_from_envelope(scope, owner_task_id, envelope, now):
    units = {}
    for unit in UNIT_ORDER:
        plan = "REMOVED"
        if unit in envelope["selected_units"]:
            plan = "PAUSED" if unit in envelope["paused_units"] else "ACTIVE"
        authority = envelope["unit_authority"].get(unit, DEFAULT_AUTHORITY[unit])
        objective_state = initial_objective(unit, plan, authority)
        scheduled = plan == "ACTIVE" and due_objective(objective_state)
        units[unit] = {
            "plan": plan,
            "authority": authority,
            "objective": {
                "state": objective_state,
                "reason": "INITIALIZED",
                "evidence_sha256": None,
                "candidate_ref": None,
                "source_ref": None,
                "updated_at_utc": utc(now),
            },
            "next_due_epoch": envelope["operation_start_epoch"] if scheduled else None,
            "next_due_at_utc": utc(envelope["operation_start_epoch"]) if scheduled else None,
            "last_decision": None,
            "last_reason": None,
        }
    return {
        "schema": SCHEMA,
        "state": "ACTIVE",
        "scope_sha256": hashlib.sha256(scope.encode("utf-8")).hexdigest(),
        "owner_task_id": owner_task_id,
        "mission_id": envelope["mission_id"],
        "account": envelope["account"],
        "mission_revision": envelope["mission_revision"],
        "mission_envelope_sha256": envelope["mission_envelope_sha256"],
        "operation_start_at": envelope["operation_start_at"],
        "operation_stop_at": envelope["operation_stop_at"],
        "operation_start_epoch": envelope["operation_start_epoch"],
        "operation_stop_epoch": envelope["operation_stop_epoch"],
        "vote_policy": envelope["vote_policy"],
        "units": units,
        "canary": {"state": "PENDING", "proof_sha256": None},
        "chrome_release": {"state": "PENDING", "proof_sha256": None},
        "wake": None,
        "active_packet": None,
        "resume_unit": None,
        "frozen_action_keys": [],
        "history": [],
        "revision_history": [],
        "updated_at_utc": utc(now),
    }


def validate_state(state, scope, owner_task_id):
    if state.get("schema") != SCHEMA or state.get("state") not in ("ACTIVE", "RETIRED"):
        raise ValueError("unknown mission state")
    if state.get("scope_sha256") != hashlib.sha256(scope.encode("utf-8")).hexdigest():
        raise ValueError("scope mismatch")
    if state.get("owner_task_id") != owner_task_id:
        raise ValueError("single owner mismatch")
    if set(state.get("units", {})) != set(UNIT_ORDER):
        raise ValueError("invalid units")
    for unit, value in state["units"].items():
        if value.get("plan") not in ("ACTIVE", "PAUSED", "REMOVED"):
            raise ValueError("invalid unit plan")
        if value.get("authority") not in ALLOWED_AUTHORITY[unit]:
            raise ValueError("invalid authority")
        objective = value.get("objective")
        if not isinstance(objective, dict) or objective.get("state") not in OBJECTIVE_STATES:
            raise ValueError("invalid objective")
        if not isinstance(objective.get("reason"), str):
            raise ValueError("invalid objective reason")
        schedule = value.get("next_due_epoch")
        should_schedule = value.get("plan") == "ACTIVE" and due_objective(objective["state"])
        if schedule is not None and not isinstance(schedule, (int, float)):
            raise ValueError("invalid unit schedule")
        if not should_schedule and schedule is not None:
            raise ValueError("parked unit scheduled")
    active = state.get("active_packet")
    if active is not None:
        if active.get("unit") not in UNIT_ORDER or active.get("state") != "RUNNING":
            raise ValueError("invalid active packet")
        boundary = active.get("boundary")
        if boundary is not None and boundary.get("state") != "OPEN":
            raise ValueError("invalid Chrome boundary")
    wake = state.get("wake")
    if wake is not None:
        if wake.get("state") != "OPEN" or not isinstance(wake.get("due_units"), list):
            raise ValueError("invalid wake")
    if state.get("resume_unit") is not None and state["resume_unit"] not in UNIT_ORDER:
        raise ValueError("invalid resume unit")
    for key in state.get("frozen_action_keys", []):
        sha256_value("frozen action key", key)


def due_units(state, now):
    if now >= state["operation_stop_epoch"]:
        return []
    resumed = state.get("resume_unit")
    if resumed:
        return [resumed]
    return [
        unit for unit in UNIT_ORDER
        if state["units"][unit]["plan"] == "ACTIVE"
        and due_objective(state["units"][unit]["objective"]["state"])
        and state["units"][unit]["next_due_epoch"] is not None
        and state["units"][unit]["next_due_epoch"] <= now
    ]


def public(state, status, now, detail=None):
    result = {
        "schema": SCHEMA,
        "status": status,
        "state": state["state"],
        "owner_task_id": state["owner_task_id"],
        "mission_id": state["mission_id"],
        "mission_revision": state["mission_revision"],
        "canary_state": state["canary"]["state"],
        "chrome_release_state": state["chrome_release"]["state"],
        "active_unit": (state.get("active_packet") or {}).get("unit"),
        "due_units": due_units(state, now),
        "frozen_action_key_count": len(state["frozen_action_keys"]),
        "heartbeat_interval_minutes": HEARTBEAT_INTERVAL_MINUTES,
        "timer_policy": "CONTINUE_STABLE_RECURRENCE",
        "next_due_at_utc": {unit: state["units"][unit]["next_due_at_utc"] for unit in UNIT_ORDER},
        "objective_state": {unit: state["units"][unit]["objective"]["state"] for unit in UNIT_ORDER},
        "updated_at_utc": utc(now),
    }
    if detail:
        result.update(detail)
    return result


def write_and_return(path, state, status, now, detail=None):
    state["updated_at_utc"] = utc(now)
    atomic_write(path, state)
    return public(state, status, now, detail)


def settle_wake(state, outcome, now):
    wake = state.get("wake")
    if wake is not None:
        wake["outcome"] = outcome
        wake["closed_at_utc"] = utc(now)
        state["history"].append({"kind": "WAKE", **wake})
        state["wake"] = None


def reschedule(state, unit, now, minutes):
    if not isinstance(minutes, int) or isinstance(minutes, bool) or not 15 <= minutes <= 10080:
        raise ValueError("invalid next_due_minutes")
    target = now + minutes * 60
    aligned = int((target + HEARTBEAT_GRID_SECONDS - 1) // HEARTBEAT_GRID_SECONDS) * HEARTBEAT_GRID_SECONDS
    if aligned >= state["operation_stop_epoch"]:
        state["units"][unit]["next_due_epoch"] = None
        state["units"][unit]["next_due_at_utc"] = None
        return
    state["units"][unit]["next_due_epoch"] = aligned
    state["units"][unit]["next_due_at_utc"] = utc(aligned)


def clear_schedule(state, unit):
    state["units"][unit]["next_due_epoch"] = None
    state["units"][unit]["next_due_at_utc"] = None


def objective_reference(name, value):
    if value is None:
        return None
    return require_text(name, value, 512)


def update_objective(state, unit, objective_state, reason, now, evidence_sha256=None, candidate_ref=None, source_ref=None):
    if objective_state not in OBJECTIVE_STATES:
        raise ValueError("invalid objective_state")
    value = state["units"][unit]
    previous_state = value["objective"]["state"]
    if objective_state in ("CANDIDATES_READY", "ACTION_ELIGIBLE"):
        candidate = objective_reference("candidate_ref", candidate_ref) or value["objective"].get("candidate_ref")
        source = objective_reference("source_ref", source_ref) or value["objective"].get("source_ref")
        if not (candidate or source):
            raise ValueError("candidate_or_source_reference_required")
    if objective_state == "ACTION_ELIGIBLE" and unit != "browsing" and not outward_authority(unit, value["authority"]):
        raise ValueError("action_authority_required")
    if objective_state == "ACTION_VERIFIED":
        if unit == "browsing" or not outward_authority(unit, value["authority"]):
            raise ValueError("action_authority_required")
        if evidence_sha256 is None:
            raise ValueError("verified_action_evidence_required")
        if not (objective_reference("source_ref", source_ref) or value["objective"].get("source_ref")):
            raise ValueError("verified_permalink_required")
    if previous_state in PARKED_OBJECTIVE_STATES and due_objective(objective_state) and source_ref is None:
        raise ValueError("recorded_rearm_evidence_required")
    objective = value["objective"]
    objective["state"] = objective_state
    objective["reason"] = require_text("objective_reason", reason, 512)
    if evidence_sha256 is not None:
        objective["evidence_sha256"] = sha256_value("objective_evidence_sha256", evidence_sha256)
    if candidate_ref is not None:
        objective["candidate_ref"] = objective_reference("candidate_ref", candidate_ref)
    if source_ref is not None:
        objective["source_ref"] = objective_reference("source_ref", source_ref)
    objective["updated_at_utc"] = utc(now)


def schedule_objective(state, unit, now, normal_minutes):
    value = state["units"][unit]
    if value["plan"] != "ACTIVE" or not due_objective(value["objective"]["state"]):
        clear_schedule(state, unit)
    elif value["objective"]["state"] == "ACTION_ELIGIBLE":
        aligned = int(now // HEARTBEAT_GRID_SECONDS + 1) * HEARTBEAT_GRID_SECONDS
        if aligned >= state["operation_stop_epoch"]:
            clear_schedule(state, unit)
        else:
            value["next_due_epoch"] = aligned
            value["next_due_at_utc"] = utc(aligned)
    else:
        reschedule(state, unit, now, normal_minutes)


def apply_envelope_revision(state, envelope, now):
    if envelope["mission_id"] != state["mission_id"] or envelope["account"] != state["account"]:
        raise ValueError("mission identity cannot change")
    if envelope["mission_revision"] <= state["mission_revision"]:
        raise ValueError("revision must advance")
    if state.get("active_packet") or state.get("wake"):
        raise ValueError("safe boundary required")
    before = {unit: dict(value) for unit, value in state["units"].items()}
    for unit in UNIT_ORDER:
        plan = "REMOVED"
        if unit in envelope["selected_units"]:
            plan = "PAUSED" if unit in envelope["paused_units"] else "ACTIVE"
        state["units"][unit]["plan"] = plan
        state["units"][unit]["authority"] = envelope["unit_authority"].get(unit, DEFAULT_AUTHORITY[unit])
        value = state["units"][unit]
        if plan != "ACTIVE":
            clear_schedule(state, unit)
            if plan == "REMOVED":
                update_objective(state, unit, "NOT_APPLICABLE", "UNIT_REMOVED", now)
            continue
        previous_authority = before[unit]["authority"]
        if before[unit]["plan"] != "ACTIVE":
            initial = initial_objective(unit, plan, value["authority"])
            update_objective(state, unit, initial, "UNIT_REACTIVATED", now)
        elif not outward_authority(unit, previous_authority) and outward_authority(unit, value["authority"]) and value["objective"]["state"] == "RESEARCH_ONLY":
            update_objective(state, unit, "PENDING", "NEW_DIRECT_AUTHORITY", now)
        if due_objective(value["objective"]["state"]) and value["next_due_epoch"] is None:
            value["next_due_epoch"] = now
            value["next_due_at_utc"] = utc(now)
    state["vote_policy"] = envelope["vote_policy"]
    state["mission_revision"] = envelope["mission_revision"]
    state["mission_envelope_sha256"] = envelope["mission_envelope_sha256"]
    state["revision_history"].append({"applied_at_utc": utc(now), "from": state["mission_revision"] - 1, "to": state["mission_revision"]})


def command(args):
    now = now_epoch(args.now_utc)
    envelope = load_envelope(args.mission_envelope)
    state_path, lock_path = paths(args.root, args.scope)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return {"schema": SCHEMA, "status": "STATE_BUSY"}
        state = read_state(state_path)
        if args.command == "bootstrap":
            if state is not None:
                validate_state(state, args.scope, args.owner_task_id)
                return public(state, "ALREADY_BOOTSTRAPPED", now)
            state = state_from_envelope(args.scope, args.owner_task_id, envelope, now)
            return write_and_return(state_path, state, "BOOTSTRAPPED", now)
        if state is None:
            return {"schema": SCHEMA, "status": "NOT_BOOTSTRAPPED"}
        validate_state(state, args.scope, args.owner_task_id)
        if args.command == "inspect":
            return public(state, "INSPECT", now)
        if args.command == "apply-revision":
            apply_envelope_revision(state, envelope, now)
            return write_and_return(state_path, state, "REVISION_APPLIED", now)
        if args.command == "canary-pass":
            if state["canary"]["state"] == "PASSED":
                return public(state, "CANARY_ALREADY_PASSED", now)
            state["canary"] = {"state": "PASSED", "proof_sha256": sha256_value("proof_sha256", args.proof_sha256)}
            return write_and_return(state_path, state, "CANARY_PASSED", now)
        if args.command == "wake-open":
            if state["state"] != "ACTIVE" or state.get("active_packet") or state.get("wake"):
                return public(state, "WAKE_UNAVAILABLE", now)
            if now >= state["operation_stop_epoch"]:
                return public(state, "MISSION_STOPPED", now)
            if state["canary"]["state"] != "PASSED":
                return public(state, "CANARY_REQUIRED", now)
            expected = parse_utc("expected_at_utc", args.expected_at_utc)
            delta = abs(now - expected)
            trigger = "WITHIN_TOLERANCE" if delta <= 300 else "RECOMPUTED_FROM_ACTUAL"
            state["wake"] = {"state": "OPEN", "wake_id": hashlib.sha256((state["mission_id"] + ":" + str(now)).encode("utf-8")).hexdigest(), "expected_at_utc": args.expected_at_utc, "actual_at_utc": utc(now), "trigger_delta_seconds": delta, "trigger_state": trigger, "due_units": due_units(state, now), "decisions": {}}
            return write_and_return(state_path, state, "WAKE_OPEN", now)
        if args.command == "decide":
            wake = state.get("wake")
            unit = require_text("unit", args.unit, 32)
            if wake is None or unit not in wake["due_units"]:
                return public(state, "UNIT_NOT_DUE", now)
            if unit in wake["decisions"] or args.decision not in DECISIONS:
                return public(state, "DECISION_INVALID", now)
            if args.decision == "RUN" and any(item["decision"] == "RUN" for item in wake["decisions"].values()):
                return public(state, "RUN_ALREADY_SELECTED", now)
            minutes = args.next_due_minutes if args.next_due_minutes is not None else DEFAULT_RECHECK_MINUTES[unit]
            if not isinstance(minutes, int) or isinstance(minutes, bool) or not 15 <= minutes <= 10080:
                raise ValueError("invalid next_due_minutes")
            wake["decisions"][unit] = {"decision": args.decision, "reason": require_text("reason", args.reason, 512), "next_due_minutes": minutes, "decided_at_utc": utc(now)}
            state["units"][unit]["last_decision"] = args.decision
            state["units"][unit]["last_reason"] = args.reason
            if args.decision != "RUN":
                reschedule(state, unit, now, minutes)
            return write_and_return(state_path, state, "DECISION_RECORDED", now)
        if args.command == "start":
            wake = state.get("wake")
            if wake is None or set(wake["decisions"]) != set(wake["due_units"]):
                return public(state, "DECISIONS_INCOMPLETE", now)
            selected = [unit for unit, item in wake["decisions"].items() if item["decision"] == "RUN"]
            if not selected:
                settle_wake(state, "NO_RUN", now)
                return write_and_return(state_path, state, "NO_PACKET", now)
            unit = selected[0]
            state["active_packet"] = {"packet_id": hashlib.sha256((wake["wake_id"] + ":" + unit).encode("utf-8")).hexdigest(), "unit": unit, "state": "RUNNING", "started_at_utc": utc(now), "next_due_minutes": wake["decisions"][unit]["next_due_minutes"], "boundary": None, "frozen_action_keys": []}
            return write_and_return(state_path, state, "PACKET_STARTED", now, {"unit": unit})
        if args.command == "boundary-open":
            active = state.get("active_packet")
            if active is None or active.get("boundary") is not None:
                return public(state, "BOUNDARY_UNAVAILABLE", now)
            active["boundary"] = {"state": "OPEN", "boundary_id": require_text("boundary_id", args.boundary_id, 128), "kind": require_text("boundary_kind", args.boundary_kind, 64), "opened_at_utc": utc(now)}
            return write_and_return(state_path, state, "BOUNDARY_OPEN", now)
        if args.command == "boundary-settle":
            active = state.get("active_packet")
            boundary = active.get("boundary") if active else None
            if boundary is None or boundary.get("boundary_id") != args.boundary_id:
                return public(state, "BOUNDARY_MISMATCH", now)
            boundary["state"] = "SETTLED"
            boundary["outcome"] = require_text("boundary_outcome", args.boundary_outcome, 128)
            boundary["settled_at_utc"] = utc(now)
            active["boundary"] = None
            return write_and_return(state_path, state, "BOUNDARY_SETTLED", now)
        if args.command == "freeze-action":
            active = state.get("active_packet")
            if active is None:
                return public(state, "NO_ACTIVE_PACKET", now)
            key = sha256_value("action_key", args.action_key)
            if key in state["frozen_action_keys"]:
                return public(state, "ACTION_KEY_ALREADY_FROZEN", now)
            state["frozen_action_keys"].append(key)
            active["frozen_action_keys"].append(key)
            return write_and_return(state_path, state, "ACTION_KEY_FROZEN", now)
        if args.command == "objective-set":
            unit = require_text("unit", args.unit, 32)
            if unit not in UNIT_ORDER or state["units"][unit]["plan"] != "ACTIVE":
                return public(state, "OBJECTIVE_UNAVAILABLE", now)
            active = state.get("active_packet")
            if active is not None and active["unit"] != unit:
                return public(state, "OBJECTIVE_BUSY", now)
            update_objective(
                state,
                unit,
                require_text("objective_state", args.objective_state, 64),
                args.objective_reason,
                now,
                args.objective_evidence_sha256,
                args.candidate_ref,
                args.source_ref,
            )
            schedule_objective(state, unit, now, DEFAULT_RECHECK_MINUTES[unit])
            return write_and_return(state_path, state, "OBJECTIVE_RECORDED", now, {"unit": unit})
        if args.command == "finish":
            active = state.get("active_packet")
            if active is None or active.get("boundary") is not None:
                return public(state, "PACKET_UNSETTLED", now)
            outcome = require_text("outcome", args.outcome, 16).upper()
            if outcome not in OUTCOMES:
                return public(state, "OUTCOME_INVALID", now)
            unit = active["unit"]
            if outward_authority(unit, state["units"][unit]["authority"]) and args.objective_state is None:
                return public(state, "OBJECTIVE_STATE_REQUIRED", now, {"unit": unit})
            if args.objective_state is not None:
                update_objective(
                    state,
                    unit,
                    require_text("objective_state", args.objective_state, 64),
                    args.objective_reason,
                    now,
                    args.objective_evidence_sha256,
                    args.candidate_ref,
                    args.source_ref,
                )
            active["outcome"] = outcome
            active["finished_at_utc"] = utc(now)
            state["history"].append({"kind": "PACKET", **active})
            state["active_packet"] = None
            if outcome == "YIELDED":
                if due_objective(state["units"][unit]["objective"]["state"]):
                    state["resume_unit"] = unit
                    settle_wake(state, "YIELDED", now)
                else:
                    state["resume_unit"] = None
                    settle_wake(state, "PARKED", now)
            else:
                state["resume_unit"] = None
                schedule_objective(state, unit, now, active["next_due_minutes"])
                settle_wake(state, outcome, now)
            return write_and_return(state_path, state, outcome, now, {"unit": unit})
        if args.command == "release-tabs":
            if state.get("active_packet") or state.get("wake"):
                return public(state, "WORK_REMAINS", now)
            state["chrome_release"] = {"state": "RELEASED", "proof_sha256": sha256_value("proof_sha256", args.proof_sha256), "released_at_utc": utc(now)}
            return write_and_return(state_path, state, "TABS_RELEASED", now)
        if args.command == "retire":
            if state.get("active_packet") or state.get("wake") or state["chrome_release"]["state"] != "RELEASED":
                return public(state, "RETIRE_BLOCKED", now)
            state["state"] = "RETIRED"
            return write_and_return(state_path, state, "RETIRED", now)
        raise ValueError("unknown command")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("bootstrap", "inspect", "apply-revision", "canary-pass", "wake-open", "decide", "start", "boundary-open", "boundary-settle", "freeze-action", "objective-set", "finish", "release-tabs", "retire"))
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--owner-task-id", required=True)
    parser.add_argument("--mission-envelope", required=True, type=Path)
    parser.add_argument("--proof-sha256")
    parser.add_argument("--expected-at-utc")
    parser.add_argument("--unit")
    parser.add_argument("--decision")
    parser.add_argument("--reason")
    parser.add_argument("--next-due-minutes", type=int)
    parser.add_argument("--boundary-id")
    parser.add_argument("--boundary-kind")
    parser.add_argument("--boundary-outcome")
    parser.add_argument("--action-key")
    parser.add_argument("--outcome")
    parser.add_argument("--objective-state")
    parser.add_argument("--objective-reason")
    parser.add_argument("--objective-evidence-sha256")
    parser.add_argument("--candidate-ref")
    parser.add_argument("--source-ref")
    parser.add_argument("--now-utc")
    args = parser.parse_args()
    try:
        print(json.dumps(command(args), ensure_ascii=False, sort_keys=True))
    except (OSError, ValueError) as exc:
        print(json.dumps({"schema": SCHEMA, "status": "INVALID", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
