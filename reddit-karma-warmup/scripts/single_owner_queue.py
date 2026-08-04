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
import re
import sys
import tempfile
import time


CODEX_HOME = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
DEFAULT_ROOT = CODEX_HOME / "reddit-karma-warmup" / "single-owner" / "missions"
UNIT_ORDER = ("browsing", "comments", "posts", "follow-up", "presence")
PROTOCOL_VERSION = "2026.08.04.6"
LEGACY_PROTOCOL_VERSIONS = {"2026.08.04.5", "2026.08.04.4", "2026.08.04.3", "2026.07.28.8"}
SCHEMA = "reddit_single_owner_queue/v10"
HEARTBEAT_INTERVAL_MINUTES = 15
HEARTBEAT_GRID_SECONDS = HEARTBEAT_INTERVAL_MINUTES * 60
ORDINARY_TRIGGER_TOLERANCE_SECONDS = 600
CLEANUP_GRACE_MINUTES = 25
WAKE_LEASE_SECONDS = HEARTBEAT_GRID_SECONDS
PACKET_LEASE_SECONDS = HEARTBEAT_GRID_SECONDS
DECISIONS = ("RUN", "WATCH", "SKIP", "DEFER")
OUTCOMES = ("COMPLETED", "SKIPPED", "BLOCKED", "YIELDED")
MISSION_STATES = {"ACTIVE", "FINALIZING", "RETIRED"}
HEARTBEAT_STATES = {"PENDING", "VERIFIED", "NEEDS_READBACK", "DELETED"}
PRESENTATION_STATES = {"STARTUP", "OPERATING"}
OBJECTIVE_STATES = (
    "RESEARCH_ONLY",
    "PENDING",
    "CANDIDATES_READY",
    "ACTION_ELIGIBLE",
    "ACTION_VERIFIED",
    "LIVE_GATE_UNVERIFIED",
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

RUNTIME_FAILURE_PATTERN = re.compile(
    r"(timeout|timed out|about:blank|content[-_ ]channel|navigation|goto|dom|"
    r"screenshot|evaluate|not expose|not exposed|incomplete|unverified|unknown|"
    r"no verified fresh page|page recovery)",
    re.IGNORECASE,
)
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
BUSINESS_GOALS = {
    "community_discovery",
    "conversation_entry",
    "feedback_validation",
    "project_distribution",
    "relationship_maintenance",
    "profile_readiness",
}
COMMUNITY_SCOPE_MODES = {"closed", "seeded_expandable", "discover"}
COVERAGE_BUDGETS = {"narrow", "standard", "broad"}
ACTION_THRESHOLDS = {"high", "standard", "low"}
ACTION_BUDGETS = {"minimal", "standard", "active"}
GOAL_UNIT_PRIORITY = {
    "community_discovery": ("browsing", "comments", "posts", "follow-up", "presence"),
    "conversation_entry": ("browsing", "comments", "posts", "follow-up", "presence"),
    "feedback_validation": ("browsing", "comments", "posts", "follow-up", "presence"),
    "project_distribution": ("browsing", "posts", "comments", "follow-up", "presence"),
    "relationship_maintenance": ("follow-up", "browsing", "comments", "posts", "presence"),
    "profile_readiness": ("presence", "browsing", "comments", "posts", "follow-up"),
}
ACTION_ORIENTED_GOALS = {
    "conversation_entry",
    "feedback_validation",
    "project_distribution",
    "relationship_maintenance",
    "profile_readiness",
}
ACTION_WINDOW_UNITS = {"comments", "posts"}
UPSTREAM_HANDOFFS = {
    "browsing": {"comments", "posts"},
}
REFILL_UNITS = {"comments", "posts"}


def outward_authority(unit, authority):
    return authority != DEFAULT_AUTHORITY[unit]


def validate_strategy(value):
    if not isinstance(value, dict):
        raise ValueError("invalid mission_strategy")
    if value.get("business_goal") not in BUSINESS_GOALS:
        raise ValueError("invalid business_goal")
    if value.get("community_scope") not in COMMUNITY_SCOPE_MODES:
        raise ValueError("invalid community_scope")
    if value.get("coverage_budget") not in COVERAGE_BUDGETS:
        raise ValueError("invalid coverage_budget")
    if value.get("action_threshold") not in ACTION_THRESHOLDS:
        raise ValueError("invalid action_threshold")
    if value.get("action_budget") not in ACTION_BUDGETS:
        raise ValueError("invalid action_budget")
    if value.get("frequency_alias") not in (None, "low", "standard", "high"):
        raise ValueError("invalid frequency_alias")
    if not isinstance(value.get("material_refs"), list) or not isinstance(value.get("planning_targets"), dict):
        raise ValueError("invalid mission_strategy evidence")
    return value


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


def runtime_failure_reason(reason):
    return isinstance(reason, str) and bool(RUNTIME_FAILURE_PATTERN.search(reason))


def next_grid_epoch(now):
    """Pre-receipt fallback only; live missions use the verified Heartbeat phase."""
    return int(now // HEARTBEAT_GRID_SECONDS + 1) * HEARTBEAT_GRID_SECONDS


def heartbeat_epoch_at_or_after(state, target):
    """Return the first verified mission Heartbeat occurrence at/after target."""
    next_run = state.get("heartbeat", {}).get("next_run_at_utc")
    if isinstance(next_run, str):
        candidate = parse_utc("heartbeat_next_run_at_utc", next_run)
        if candidate < target:
            intervals = int((target - candidate + HEARTBEAT_GRID_SECONDS - 1) // HEARTBEAT_GRID_SECONDS)
            candidate += intervals * HEARTBEAT_GRID_SECONDS
    else:
        candidate = next_grid_epoch(target)
    return candidate if candidate < state["operation_stop_epoch"] else None


def unit_requires_recovery_first(state, unit):
    value = state["units"][unit]
    if value["plan"] != "ACTIVE" or not due_objective(value["objective"]["state"]):
        return False
    return (
        state.get("resume_unit") == unit
        or value["objective"]["state"] == "LIVE_GATE_UNVERIFIED"
        or runtime_failure_reason(value.get("last_reason"))
        or runtime_failure_reason(value["objective"].get("reason"))
    )


def rejected_candidate(state, unit, candidate_ref):
    if candidate_ref is None:
        return False
    return any(
        item["unit"] == unit and item["candidate_ref"] == candidate_ref
        for item in state.get("candidate_rejections", [])
    )


def action_window_guard(state, unit, decision):
    """True when deferring this authorized action would strand it after cutoff."""
    value = state["units"][unit]
    return (
        decision != "RUN"
        and unit in ACTION_WINDOW_UNITS
        and state["mission_strategy"]["business_goal"] in ACTION_ORIENTED_GOALS
        and outward_authority(unit, value["authority"])
        and value["objective"]["state"] in {"PENDING", "CANDIDATES_READY"}
    )


def utc(epoch):
    return dt.datetime.fromtimestamp(epoch, tz=dt.timezone.utc).isoformat().replace("+00:00", "Z")


def require_text(name, value, maximum=512):
    if not isinstance(value, str) or not value or len(value) > maximum or "\x00" in value:
        raise ValueError("invalid " + name)
    return value


def sha256_value(name, value):
    """Read a lightweight opaque runtime token.

    The queue keeps legacy ``*_sha256`` field names for compatibility, but
    normal receipts are identifiers, not manually supplied digests. Package
    and mission-envelope integrity still use ``canonical_hash`` at their
    explicit install/compile boundary.
    """
    return require_text(name, value, 256)


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


def heartbeat_rrule(value):
    value = require_text("heartbeat_rrule", value, 512)
    normalized = value.upper().replace(" ", "")
    required = ("FREQ=MINUTELY", "INTERVAL=15", "UNTIL=")
    if any(part not in normalized for part in required) or "COUNT=" in normalized:
        raise ValueError("invalid heartbeat_rrule")
    return value


def rrule_until_epoch(value):
    match = re.search(r"(?:^|;)UNTIL=(\d{8}T\d{6}Z)(?:;|$)", value.upper().replace(" ", ""))
    if match is None:
        raise ValueError("invalid heartbeat_rrule until")
    return dt.datetime.strptime(match.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=dt.timezone.utc).timestamp()


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
    strict_integrity = os.environ.get("REDDIT_STRICT_INTEGRITY") == "1"
    if strict_integrity and canonical_hash(unsigned) != stored_hash:
        raise ValueError("mission envelope integrity mismatch")
    if raw.get("execution_topology") != "single_owner_v1":
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
    strategy = validate_strategy(raw.get("mission_strategy"))
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
        "mission_strategy": strategy,
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
        "runtime_protocol_version": PROTOCOL_VERSION,
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
        "cleanup_deadline_epoch": envelope["operation_stop_epoch"] + CLEANUP_GRACE_MINUTES * 60,
        "cleanup_deadline_at_utc": utc(envelope["operation_stop_epoch"] + CLEANUP_GRACE_MINUTES * 60),
        "vote_policy": envelope["vote_policy"],
        "mission_strategy": envelope["mission_strategy"],
        "units": units,
        "presentation": {
            "state": "STARTUP",
            "title": None,
            "proof_sha256": None,
            "verified_at_utc": None,
        },
        "canary": {"state": "PENDING", "proof_sha256": None},
        "chrome_release": {"state": "PENDING", "proof_sha256": None},
        "heartbeat": {
            "state": "PENDING",
            "automation_id": None,
            "target_task_id": owner_task_id,
            "rrule": None,
            "until_at_utc": None,
            "next_run_at_utc": None,
            "readback_at_utc": None,
            "proof_sha256": None,
            "last_expected_at_utc": None,
            "last_observed_at_utc": None,
            "scheduler_gap_count": 0,
            "deleted_at_utc": None,
            "delete_proof_sha256": None,
        },
        "cleanup": {"state": "PENDING", "opened_at_utc": None, "reason": None},
        "wake": None,
        "active_packet": None,
        "resume_unit": None,
        "frozen_action_keys": [],
        "candidate_rejections": [],
        "history": [],
        "revision_history": [],
        "updated_at_utc": utc(now),
    }


def validate_state(state, scope, owner_task_id):
    if state.get("schema") != SCHEMA or state.get("state") not in MISSION_STATES:
        raise ValueError("unknown mission state")
    if state.get("runtime_protocol_version") not in ({PROTOCOL_VERSION} | LEGACY_PROTOCOL_VERSIONS):
        raise ValueError("runtime protocol version mismatch")
    require_text("scope_sha256", state.get("scope_sha256"), 256)
    if state.get("owner_task_id") != owner_task_id:
        raise ValueError("single owner mismatch")
    presentation = state.get("presentation")
    if not isinstance(presentation, dict) or presentation.get("state") not in PRESENTATION_STATES:
        raise ValueError("invalid presentation state")
    if presentation["state"] == "OPERATING":
        if presentation.get("title") != "Reddit 运营台":
            raise ValueError("invalid operating title")
        sha256_value("presentation_proof_sha256", presentation.get("proof_sha256"))
        parse_utc("presentation_verified_at_utc", presentation.get("verified_at_utc"))
    if set(state.get("units", {})) != set(UNIT_ORDER):
        raise ValueError("invalid units")
    validate_strategy(state.get("mission_strategy"))
    if not isinstance(state.get("cleanup_deadline_epoch"), (int, float)) or state["cleanup_deadline_epoch"] != state["operation_stop_epoch"] + CLEANUP_GRACE_MINUTES * 60:
        raise ValueError("invalid cleanup deadline")
    if parse_utc("cleanup_deadline_at_utc", state.get("cleanup_deadline_at_utc")) != state["cleanup_deadline_epoch"]:
        raise ValueError("invalid cleanup deadline")
    heartbeat = state.get("heartbeat")
    if not isinstance(heartbeat, dict) or heartbeat.get("state") not in HEARTBEAT_STATES:
        raise ValueError("invalid heartbeat state")
    if heartbeat.get("target_task_id") != owner_task_id:
        raise ValueError("heartbeat target mismatch")
    if not isinstance(heartbeat.get("scheduler_gap_count"), int) or heartbeat["scheduler_gap_count"] < 0:
        raise ValueError("invalid heartbeat scheduler gap count")
    for key in ("last_expected_at_utc", "last_observed_at_utc"):
        value = heartbeat.get(key)
        if value is not None:
            parse_utc("heartbeat_" + key, value)
    if heartbeat["state"] in {"VERIFIED", "NEEDS_READBACK"}:
        if not all(isinstance(heartbeat.get(key), str) and heartbeat[key] for key in ("automation_id", "rrule", "until_at_utc", "next_run_at_utc", "readback_at_utc", "proof_sha256")):
            raise ValueError("incomplete heartbeat receipt")
        heartbeat_rrule(heartbeat["rrule"])
        if parse_utc("heartbeat_until_at_utc", heartbeat["until_at_utc"]) != state["cleanup_deadline_epoch"]:
            raise ValueError("heartbeat until mismatch")
        if heartbeat["state"] == "VERIFIED" and parse_utc("heartbeat_next_run_at_utc", heartbeat["next_run_at_utc"]) > state["cleanup_deadline_epoch"]:
            raise ValueError("heartbeat next run after cleanup deadline")
        sha256_value("heartbeat_proof_sha256", heartbeat["proof_sha256"])
    if heartbeat["state"] == "DELETED":
        if not isinstance(heartbeat.get("delete_proof_sha256"), str) or not isinstance(heartbeat.get("deleted_at_utc"), str):
            raise ValueError("heartbeat deletion proof required")
        sha256_value("heartbeat_delete_proof_sha256", heartbeat["delete_proof_sha256"])
        parse_utc("heartbeat_deleted_at_utc", heartbeat["deleted_at_utc"])
    cleanup = state.get("cleanup")
    if not isinstance(cleanup, dict) or cleanup.get("state") not in {"PENDING", "OPEN"}:
        raise ValueError("invalid cleanup state")
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
        for key in ("candidate_ref", "source_ref"):
            reference = objective.get(key)
            if reference is not None:
                objective_reference("objective_" + key, reference)
        evidence = objective.get("evidence_sha256")
        if evidence is not None:
            sha256_value("objective_evidence_sha256", evidence)
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
        if not isinstance(active.get("lease_expires_at_utc"), str):
            raise ValueError("missing packet lease")
        parse_utc("packet_lease_expires_at_utc", active["lease_expires_at_utc"])
        boundary = active.get("boundary")
        if boundary is not None and boundary.get("state") != "OPEN":
            raise ValueError("invalid Chrome boundary")
    wake = state.get("wake")
    if wake is not None:
        if wake.get("state") != "OPEN" or not isinstance(wake.get("due_units"), list) or not isinstance(wake.get("lease_expires_at_utc"), str):
            raise ValueError("invalid wake")
        parse_utc("wake_lease_expires_at_utc", wake["lease_expires_at_utc"])
    if state.get("resume_unit") is not None and state["resume_unit"] not in UNIT_ORDER:
        raise ValueError("invalid resume unit")
    for key in state.get("frozen_action_keys", []):
        sha256_value("frozen action key", key)
    rejections = state.get("candidate_rejections")
    if not isinstance(rejections, list):
        raise ValueError("invalid candidate rejections")
    seen_rejections = set()
    for item in rejections:
        if not isinstance(item, dict) or item.get("unit") not in REFILL_UNITS:
            raise ValueError("invalid candidate rejection")
        candidate = objective_reference("candidate_rejection_ref", item.get("candidate_ref"))
        rejection_key = (item["unit"], candidate)
        if rejection_key in seen_rejections:
            raise ValueError("duplicate candidate rejection")
        seen_rejections.add(rejection_key)
        require_text("candidate_rejection_reason", item.get("reason"), 512)
        sha256_value("candidate_rejection_evidence", item.get("evidence_sha256"))
        objective_reference("candidate_rejection_source_ref", item.get("source_ref"))
        parse_utc("candidate_rejection_at", item.get("rejected_at_utc"))


def due_units(state, now):
    if now >= state["operation_stop_epoch"]:
        return []
    resumed = state.get("resume_unit")
    if resumed:
        return [resumed]
    candidates = [
        unit for unit in UNIT_ORDER
        if state["units"][unit]["plan"] == "ACTIVE"
        and due_objective(state["units"][unit]["objective"]["state"])
        and state["units"][unit]["next_due_epoch"] is not None
        and state["units"][unit]["next_due_epoch"] <= now
    ]
    goal_priority = GOAL_UNIT_PRIORITY[state["mission_strategy"]["business_goal"]]
    order = {unit: index for index, unit in enumerate(goal_priority)}
    action_goal = state["mission_strategy"]["business_goal"] in ACTION_ORIENTED_GOALS
    return sorted(
        candidates,
        key=lambda unit: (
            0 if action_goal and state["units"][unit]["objective"]["state"] == "ACTION_ELIGIBLE" else 1,
            order[unit],
        ),
    )


def public(state, status, now, detail=None):
    result = {
        "schema": SCHEMA,
        "runtime_protocol_version": state["runtime_protocol_version"],
        "status": status,
        "state": state["state"],
        "owner_task_id": state["owner_task_id"],
        "mission_id": state["mission_id"],
        "mission_revision": state["mission_revision"],
        "mission_strategy": state["mission_strategy"],
        "presentation": {
            "state": state["presentation"]["state"],
            "title": state["presentation"]["title"],
        },
        "canary_state": state["canary"]["state"],
        "chrome_release_state": state["chrome_release"]["state"],
        "heartbeat": {
            "state": state["heartbeat"]["state"],
            "automation_id": state["heartbeat"]["automation_id"],
            "until_at_utc": state["heartbeat"]["until_at_utc"],
            "next_run_at_utc": state["heartbeat"]["next_run_at_utc"],
            "readback_at_utc": state["heartbeat"]["readback_at_utc"],
            "last_expected_at_utc": state["heartbeat"]["last_expected_at_utc"],
            "last_observed_at_utc": state["heartbeat"]["last_observed_at_utc"],
            "scheduler_gap_count": state["heartbeat"]["scheduler_gap_count"],
        },
        "scheduler_health": (
            "HEALTHY" if state["heartbeat"]["state"] in {"VERIFIED", "NEEDS_READBACK"}
            else "DELETED" if state["heartbeat"]["state"] == "DELETED"
            else "ADVISORY_UNVERIFIED_CONTINUING"
        ),
        "cleanup_state": state["cleanup"]["state"],
        "cleanup_deadline_at_utc": state["cleanup_deadline_at_utc"],
        "active_unit": (state.get("active_packet") or {}).get("unit"),
        "resume_unit": state.get("resume_unit"),
        "due_units": due_units(state, now),
        "frozen_action_key_count": len(state["frozen_action_keys"]),
        "candidate_rejection_count": len(state["candidate_rejections"]),
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
        # A normal wake closes work; it does not invalidate an already verified
        # recurring timer. Older queues may still contain NEEDS_READBACK, and
        # heartbeat-observe promotes that legacy state on the next delivery.


def append_idle_wake(state, outcome, now, expected_at_utc, trigger_state, trigger_delta_seconds):
    state["history"].append({
        "kind": "WAKE",
        "state": "CLOSED",
        "outcome": outcome,
        "expected_at_utc": expected_at_utc,
        "actual_at_utc": utc(now),
        "trigger_state": trigger_state,
        "trigger_delta_seconds": trigger_delta_seconds,
        "due_units": [],
        "decisions": {},
        "closed_at_utc": utc(now),
    })
    # Keep the verified receipt across ordinary no-work wakes. Requiring a
    # second timer readback after every wake created a self-blocking loop:
    # close wake -> NEEDS_READBACK -> next observe -> scheduler advisory.


def objectives_terminal(state):
    return all(
        value["plan"] != "ACTIVE" or value["objective"]["state"] in PARKED_OBJECTIVE_STATES
        for value in state["units"].values()
    )


def cleanup_allowed(state, now):
    return now >= state["operation_stop_epoch"] or objectives_terminal(state)


def clear_all_schedules(state):
    for unit in UNIT_ORDER:
        clear_schedule(state, unit)
    state["resume_unit"] = None


def heartbeat_receipt(state, args, now):
    heartbeat = state["heartbeat"]
    automation_id = require_text("automation_id", args.automation_id, 256)
    target_task_id = require_text("heartbeat_target_task_id", args.heartbeat_target_task_id, 256)
    if target_task_id != state["owner_task_id"]:
        raise ValueError("heartbeat target mismatch")
    rrule = heartbeat_rrule(args.heartbeat_rrule)
    until_epoch = parse_utc("heartbeat_until_at_utc", args.heartbeat_until_at_utc)
    next_run_epoch = parse_utc("heartbeat_next_run_at_utc", args.heartbeat_next_run_at_utc)
    if until_epoch != state["cleanup_deadline_epoch"]:
        raise ValueError("heartbeat until mismatch")
    if rrule_until_epoch(rrule) != until_epoch:
        raise ValueError("heartbeat rrule until mismatch")
    if next_run_epoch <= now or next_run_epoch > until_epoch or next_run_epoch - now > HEARTBEAT_GRID_SECONDS + ORDINARY_TRIGGER_TOLERANCE_SECONDS:
        raise ValueError("heartbeat next run invalid")
    if heartbeat["state"] in {"VERIFIED", "NEEDS_READBACK"} and heartbeat["automation_id"] != automation_id:
        raise ValueError("heartbeat automation identity cannot change")
    heartbeat.update({
        "state": "VERIFIED",
        "automation_id": automation_id,
        "target_task_id": target_task_id,
        "rrule": rrule,
        "until_at_utc": args.heartbeat_until_at_utc,
        "next_run_at_utc": args.heartbeat_next_run_at_utc,
        "readback_at_utc": utc(now),
        "proof_sha256": sha256_value("heartbeat_proof_sha256", args.proof_sha256),
        "last_expected_at_utc": None,
        "last_observed_at_utc": None,
    })


def observe_heartbeat(state, now):
    """Record one delivered scheduler event without inventing future delivery."""
    heartbeat = state["heartbeat"]
    if heartbeat["state"] not in {"VERIFIED", "NEEDS_READBACK"}:
        return "MISSION_SCHEDULER_UNVERIFIED_CONTINUING"
    # NEEDS_READBACK is a legacy state from pre-2026.07.30.7 queues. If the
    # receipt still contains the same automation identity and a future
    # occurrence, the delivered heartbeat itself is the required readback.
    if heartbeat["state"] == "NEEDS_READBACK":
        heartbeat["state"] = "VERIFIED"
        heartbeat["readback_at_utc"] = utc(now)
    expected = parse_utc("heartbeat_next_run_at_utc", heartbeat["next_run_at_utc"])
    signed_delta = now - expected
    heartbeat["last_expected_at_utc"] = heartbeat["next_run_at_utc"]
    heartbeat["last_observed_at_utc"] = utc(now)
    if signed_delta < -ORDINARY_TRIGGER_TOLERANCE_SECONDS:
        return "HEARTBEAT_EARLY_OBSERVED"
    # A later event proves this delivery only. More than one elapsed interval is
    # a scheduling gap suspicion, not proof of a lost platform execution.
    elapsed_intervals = max(1, int(max(0, signed_delta) // HEARTBEAT_GRID_SECONDS) + 1)
    heartbeat["next_run_at_utc"] = utc(expected + elapsed_intervals * HEARTBEAT_GRID_SECONDS)
    if elapsed_intervals > 1:
        heartbeat["scheduler_gap_count"] += elapsed_intervals - 1
        return "SCHEDULER_GAP_SUSPECTED"
    if signed_delta > ORDINARY_TRIGGER_TOLERANCE_SECONDS:
        return "HEARTBEAT_LATE_OBSERVED"
    return "HEARTBEAT_OBSERVED"


def recover_stale_work(state, now, reason, action_key=None):
    active = state.get("active_packet")
    wake = state.get("wake")
    if active is None and wake is None:
        return "NO_RECOVERY_NEEDED"
    lease = active.get("lease_expires_at_utc") if active is not None else wake.get("lease_expires_at_utc")
    if now < parse_utc("recovery_lease_expires_at_utc", lease) and now < state["operation_stop_epoch"]:
        return "RECOVERY_NOT_STALE"
    if action_key is not None:
        key = sha256_value("recovery_action_key", action_key)
        if key not in state["frozen_action_keys"]:
            state["frozen_action_keys"].append(key)
        if active is not None and key not in active["frozen_action_keys"]:
            active["frozen_action_keys"].append(key)
    if active is not None:
        if active.get("boundary") is not None:
            active["boundary"]["state"] = "SETTLED"
            active["boundary"]["outcome"] = "RECOVERY_ABORTED"
            active["boundary"]["settled_at_utc"] = utc(now)
            active["boundary"] = None
        active["outcome"] = "YIELDED"
        active["finished_at_utc"] = utc(now)
        active["recovery_reason"] = reason
        state["history"].append({"kind": "PACKET", **active})
        unit = active["unit"]
        state["active_packet"] = None
        state["units"][unit]["last_reason"] = "RECOVERY_FIRST: " + reason
        if runtime_failure_reason(reason) and due_objective(state["units"][unit]["objective"]["state"]):
            state["units"][unit]["objective"].update({
                "state": "LIVE_GATE_UNVERIFIED",
                "reason": reason,
                "updated_at_utc": utc(now),
            })
        state["resume_unit"] = unit if now < state["operation_stop_epoch"] and due_objective(state["units"][unit]["objective"]["state"]) else None
    settle_wake(state, "RECOVERED_YIELDED", now)
    return "RECOVERED_YIELDED"


def reschedule(state, unit, now, minutes):
    if not isinstance(minutes, int) or isinstance(minutes, bool) or not 15 <= minutes <= 10080:
        raise ValueError("invalid next_due_minutes")
    target = now + minutes * 60
    aligned = heartbeat_epoch_at_or_after(state, target)
    if aligned is None:
        state["units"][unit]["next_due_epoch"] = None
        state["units"][unit]["next_due_at_utc"] = None
        return
    state["units"][unit]["next_due_epoch"] = aligned
    state["units"][unit]["next_due_at_utc"] = utc(aligned)


def schedule_next_grid(state, unit, now):
    aligned = heartbeat_epoch_at_or_after(state, now + 0.001)
    if aligned is None:
        return False
    state["units"][unit]["next_due_epoch"] = aligned
    state["units"][unit]["next_due_at_utc"] = utc(aligned)
    return True


def schedule_next_heartbeat(state, unit, now):
    """Schedule the next concrete mission turn, never an unrelated wall-clock grid."""
    scheduled = heartbeat_epoch_at_or_after(state, now + 0.001)
    if scheduled is None:
        return False
    state["units"][unit]["next_due_epoch"] = scheduled
    state["units"][unit]["next_due_at_utc"] = utc(scheduled)
    return True


def clear_schedule(state, unit):
    state["units"][unit]["next_due_epoch"] = None
    state["units"][unit]["next_due_at_utc"] = None


def objective_reference(name, value):
    if value is None:
        return None
    return require_text(name, value, 512)


def update_objective(
    state,
    unit,
    objective_state,
    reason,
    now,
    evidence_sha256=None,
    candidate_ref=None,
    source_ref=None,
    block_scope=None,
):
    if objective_state not in OBJECTIVE_STATES:
        raise ValueError("invalid objective_state")
    value = state["units"][unit]
    if objective_state in {"RULE_BLOCKED", "MATERIAL_REQUIRED", "NOT_APPLICABLE"} and runtime_failure_reason(reason):
        raise ValueError("recoverable_runtime_failure_requires_live_gate_unverified")
    previous_state = value["objective"]["state"]
    if objective_state in ("CANDIDATES_READY", "ACTION_ELIGIBLE"):
        candidate = objective_reference("candidate_ref", candidate_ref) or value["objective"].get("candidate_ref")
        source = objective_reference("source_ref", source_ref) or value["objective"].get("source_ref")
        if not (candidate or source):
            raise ValueError("candidate_or_source_reference_required")
        if unit in REFILL_UNITS:
            if candidate is None:
                raise ValueError("exact_candidate_reference_required")
            if rejected_candidate(state, unit, candidate):
                raise ValueError("candidate_previously_rejected")
    if objective_state == "ACTION_ELIGIBLE" and unit != "browsing" and not outward_authority(unit, value["authority"]):
        raise ValueError("action_authority_required")
    if objective_state == "ACTION_VERIFIED":
        if unit == "browsing" or not outward_authority(unit, value["authority"]):
            raise ValueError("action_authority_required")
        if evidence_sha256 is None:
            raise ValueError("verified_action_evidence_required")
        if not (objective_reference("source_ref", source_ref) or value["objective"].get("source_ref")):
            raise ValueError("verified_permalink_required")
    if objective_state == "LIVE_GATE_UNVERIFIED" and not runtime_failure_reason(reason):
        raise ValueError("live_gate_unverified_requires_runtime_failure")
    if objective_state == "RULE_BLOCKED":
        if block_scope != "MISSION":
            raise ValueError("candidate_or_community_block_requires_candidate_reject")
        if evidence_sha256 is None:
            raise ValueError("mission_rule_block_evidence_required")
    if objective_state == "MATERIAL_REQUIRED":
        if block_scope != "MISSION":
            raise ValueError("candidate_or_format_gap_requires_more_research")
        if evidence_sha256 is None:
            raise ValueError("mission_material_gap_evidence_required")
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
        if not schedule_next_heartbeat(state, unit, now):
            clear_schedule(state, unit)
    elif (
        unit == "browsing"
        and state["mission_strategy"]["action_budget"] == "active"
    ):
        if not schedule_next_heartbeat(state, unit, now):
            clear_schedule(state, unit)
    else:
        reschedule(state, unit, now, normal_minutes)


def apply_envelope_revision(state, envelope, now):
    if state["state"] != "ACTIVE":
        raise ValueError("revision requires active mission")
    if (
        envelope["mission_id"] != state["mission_id"]
        or envelope["account"] != state["account"]
        or envelope["operation_start_epoch"] != state["operation_start_epoch"]
        or envelope["operation_stop_epoch"] != state["operation_stop_epoch"]
    ):
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
    state["mission_strategy"] = envelope["mission_strategy"]
    state["mission_revision"] = envelope["mission_revision"]
    state["mission_envelope_sha256"] = envelope["mission_envelope_sha256"]
    state["revision_history"].append({"applied_at_utc": utc(now), "from": state["mission_revision"] - 1, "to": state["mission_revision"]})


def envelope_matches_state(state, envelope):
    return (
        envelope["mission_id"] == state["mission_id"]
        and envelope["account"] == state["account"]
        and envelope["mission_revision"] == state["mission_revision"]
        and envelope["mission_envelope_sha256"] == state["mission_envelope_sha256"]
        and envelope["operation_start_epoch"] == state["operation_start_epoch"]
        and envelope["operation_stop_epoch"] == state["operation_stop_epoch"]
    )


def rebind_idle_owner(state, owner_task_id, now):
    """Repair a stale parent-task binding without searching other tasks.

    A queue is addressed by the current task's explicit mission scope. If an
    older bootstrap copied the delegation source ID into an otherwise idle
    queue, the current task may adopt that queue once. Active packets, open
    wakes, or unsettled browser/mutation state remain hard stops.
    """
    if state.get("owner_task_id") == owner_task_id:
        return None
    if (
        state.get("state") not in {"ACTIVE", "FINALIZING"}
        or state.get("active_packet") is not None
        or state.get("wake") is not None
    ):
        return None
    previous = state.get("owner_task_id")
    state["owner_task_id"] = owner_task_id
    if isinstance(state.get("heartbeat"), dict):
        state["heartbeat"]["target_task_id"] = owner_task_id
    state.setdefault("history", []).append({
        "kind": "OWNER_REBOUND",
        "from_owner_task_id": previous,
        "to_owner_task_id": owner_task_id,
        "at_utc": utc(now),
        "reason": "current_task_scope_repaired_idle_delegation_binding",
    })
    state["updated_at_utc"] = utc(now)
    return previous


def command(args):
    now = now_epoch(args.now_utc)
    envelope = load_envelope(args.mission_envelope)
    if args.scope != envelope["mission_id"]:
        return {"schema": SCHEMA, "status": "MISSION_SCOPE_MISMATCH"}
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
                rebound_from = rebind_idle_owner(state, args.owner_task_id, now)
                if rebound_from is not None:
                    atomic_write(state_path, state)
                validate_state(state, args.scope, args.owner_task_id)
                return public(state, "ALREADY_BOOTSTRAPPED", now)
            state = state_from_envelope(args.scope, args.owner_task_id, envelope, now)
            return write_and_return(state_path, state, "BOOTSTRAPPED", now)
        if state is None:
            return {"schema": SCHEMA, "status": "NOT_BOOTSTRAPPED"}
        rebound_from = rebind_idle_owner(state, args.owner_task_id, now)
        if rebound_from is not None:
            atomic_write(state_path, state)
        validate_state(state, args.scope, args.owner_task_id)
        if args.command == "apply-revision":
            apply_envelope_revision(state, envelope, now)
            return write_and_return(state_path, state, "REVISION_APPLIED", now)
        if not envelope_matches_state(state, envelope):
            return public(state, "ENVELOPE_MISMATCH", now)
        if args.command == "inspect":
            return public(state, "INSPECT", now)
        if args.command == "presentation-promote":
            if state["state"] != "ACTIVE" or state.get("active_packet") or state.get("wake"):
                return public(state, "PRESENTATION_UNAVAILABLE", now)
            title = require_text("presentation_title", args.presentation_title, 128)
            if title != "Reddit 运营台":
                return public(state, "PRESENTATION_TITLE_INVALID", now)
            state["presentation"] = {
                "state": "OPERATING",
                "title": title,
                "proof_sha256": sha256_value("presentation_proof_sha256", args.proof_sha256),
                "verified_at_utc": utc(now),
            }
            return write_and_return(state_path, state, "PRESENTATION_PROMOTED", now)
        if state["state"] == "FINALIZING" and args.command not in {"recover", "cleanup-open", "release-tabs", "heartbeat-delete", "retire"}:
            return public(state, "FINALIZING", now)
        if args.command == "canary-pass":
            if state["presentation"]["state"] != "OPERATING":
                # Presentation metadata is useful but must not block the
                # current task's first real work. Promote it opportunistically.
                state["presentation"] = {
                    "state": "OPERATING",
                    "title": "Reddit 运营台",
                    "proof_sha256": sha256_value("presentation_proof_sha256", args.proof_sha256),
                    "verified_at_utc": utc(now),
                }
            if state["canary"]["state"] == "PASSED":
                return public(state, "CANARY_ALREADY_PASSED", now)
            state["canary"] = {"state": "PASSED", "proof_sha256": sha256_value("proof_sha256", args.proof_sha256)}
            return write_and_return(state_path, state, "CANARY_PASSED", now)
        if args.command == "heartbeat-record":
            if state["state"] != "ACTIVE" or state.get("active_packet") or state.get("wake"):
                return public(state, "HEARTBEAT_RECORD_UNAVAILABLE", now)
            heartbeat_receipt(state, args, now)
            return write_and_return(state_path, state, "HEARTBEAT_VERIFIED", now)
        if args.command == "heartbeat-observe":
            if state["state"] != "ACTIVE" or state.get("active_packet") or state.get("wake"):
                return public(state, "HEARTBEAT_OBSERVE_UNAVAILABLE", now)
            status = observe_heartbeat(state, now)
            return write_and_return(state_path, state, status, now)
        if args.command == "wake-open":
            if state["state"] != "ACTIVE" or state.get("active_packet") or state.get("wake"):
                return public(state, "WAKE_UNAVAILABLE", now)
            if now >= state["operation_stop_epoch"]:
                return public(state, "MISSION_STOPPED", now)
            if state["canary"]["state"] != "PASSED":
                return public(state, "CANARY_REQUIRED", now)
            scheduler_advisory = state["heartbeat"]["state"] != "VERIFIED"
            wake_source = args.wake_source or "HEARTBEAT"
            if wake_source not in {"INITIAL", "HEARTBEAT"}:
                raise ValueError("invalid wake_source")
            # A verified receipt is useful telemetry, not a second gate.  The
            # scheduler may deliver late or omit an observation; the current
            # task still runs once its ordinary time window is valid.
            expected = parse_utc("expected_at_utc", args.expected_at_utc)
            signed_delta = now - expected
            delta = abs(signed_delta)
            if delta <= ORDINARY_TRIGGER_TOLERANCE_SECONDS:
                trigger = "WITHIN_TOLERANCE"
                effective_now = max(now, expected)
            elif signed_delta < 0:
                trigger = "EARLY_WAKE"
                append_idle_wake(state, "EARLY_WAKE_NOOP", now, args.expected_at_utc, trigger, signed_delta)
                return write_and_return(state_path, state, "EARLY_WAKE_NOOP", now)
            else:
                trigger = "LATE_WAKE"
                effective_now = now
            due = due_units(state, effective_now)
            if not due:
                append_idle_wake(state, "NOOP", now, args.expected_at_utc, trigger, signed_delta)
                return write_and_return(state_path, state, "NOOP", now)
            state["wake"] = {
                "state": "OPEN",
                "wake_id": hashlib.sha256((state["mission_id"] + ":" + str(now)).encode("utf-8")).hexdigest(),
                "expected_at_utc": args.expected_at_utc,
                "actual_at_utc": utc(now),
                "trigger_delta_seconds": signed_delta,
                "trigger_state": trigger,
                "due_units": due,
                "decisions": {},
                "scheduler_status": "ADVISORY_UNVERIFIED_CONTINUING" if scheduler_advisory else "VERIFIED",
                "lease_expires_at_utc": utc(now + WAKE_LEASE_SECONDS),
            }
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
            if args.decision != "RUN" and unit_requires_recovery_first(state, unit):
                return public(state, "RECOVERABLE_RUNTIME_FAILURE_REQUIRES_RUN", now, {"unit": unit})
            minutes = args.next_due_minutes if args.next_due_minutes is not None else DEFAULT_RECHECK_MINUTES[unit]
            if not isinstance(minutes, int) or isinstance(minutes, bool) or not 15 <= minutes <= 10080:
                raise ValueError("invalid next_due_minutes")
            adjustment = None
            if action_window_guard(state, unit, args.decision):
                proposed = heartbeat_epoch_at_or_after(state, now + minutes * 60)
                if proposed is None:
                    if not schedule_next_grid(state, unit, now):
                        minutes = None
                        adjustment = "ACTION_WINDOW_EXPIRED"
                        clear_schedule(state, unit)
                    else:
                        minutes = HEARTBEAT_INTERVAL_MINUTES
                        adjustment = "ACTION_WINDOW_CLAMPED_TO_NEXT_HEARTBEAT"
            decision_record = {"decision": args.decision, "reason": require_text("reason", args.reason, 512), "next_due_minutes": minutes, "decided_at_utc": utc(now)}
            if adjustment is not None:
                decision_record["scheduler_adjustment"] = adjustment
            wake["decisions"][unit] = decision_record
            state["units"][unit]["last_decision"] = args.decision
            state["units"][unit]["last_reason"] = args.reason
            if args.decision != "RUN":
                if adjustment is None:
                    if (
                        unit == "browsing"
                        and state["mission_strategy"]["action_budget"] == "active"
                    ):
                        schedule_next_heartbeat(state, unit, now)
                    else:
                        reschedule(state, unit, now, minutes)
            return write_and_return(state_path, state, "DECISION_RECORDED", now, {"unit": unit, "scheduler_adjustment": adjustment})
        if args.command == "start":
            wake = state.get("wake")
            if wake is None or set(wake["decisions"]) != set(wake["due_units"]):
                return public(state, "DECISIONS_INCOMPLETE", now)
            selected = [unit for unit, item in wake["decisions"].items() if item["decision"] == "RUN"]
            if not selected:
                settle_wake(state, "NO_RUN", now)
                return write_and_return(state_path, state, "NO_PACKET", now)
            unit = selected[0]
            state["active_packet"] = {
                "packet_id": hashlib.sha256((wake["wake_id"] + ":" + unit).encode("utf-8")).hexdigest(),
                "unit": unit,
                "state": "RUNNING",
                "started_at_utc": utc(now),
                "lease_expires_at_utc": utc(now + PACKET_LEASE_SECONDS),
                "next_due_minutes": wake["decisions"][unit]["next_due_minutes"],
                "boundary": None,
                "frozen_action_keys": [],
            }
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
        if args.command == "handoff":
            active = state.get("active_packet")
            if active is None or active.get("boundary") is not None:
                return public(state, "HANDOFF_UNAVAILABLE", now)
            source_unit = active["unit"]
            target_unit = require_text("target_unit", args.target_unit, 32)
            if target_unit not in UPSTREAM_HANDOFFS.get(source_unit, set()):
                return public(state, "HANDOFF_ROUTE_INVALID", now)
            if state["units"][target_unit]["plan"] != "ACTIVE":
                return public(state, "HANDOFF_TARGET_UNAVAILABLE", now)
            if not outward_authority(target_unit, state["units"][target_unit]["authority"]):
                return public(state, "HANDOFF_TARGET_UNAUTHORIZED", now)
            objective_state = require_text("objective_state", args.objective_state, 64)
            if objective_state != "ACTION_ELIGIBLE":
                return public(state, "HANDOFF_OBJECTIVE_INVALID", now)
            source_ref = objective_reference("source_ref", args.source_ref)
            if source_ref is None:
                return public(state, "HANDOFF_SOURCE_REFERENCE_REQUIRED", now)
            candidate_ref = objective_reference("candidate_ref", args.candidate_ref)
            if candidate_ref is None:
                return public(state, "HANDOFF_CANDIDATE_REFERENCE_REQUIRED", now)
            if rejected_candidate(state, target_unit, candidate_ref):
                return public(state, "HANDOFF_CANDIDATE_PREVIOUSLY_REJECTED", now)
            update_objective(
                state,
                target_unit,
                objective_state,
                args.objective_reason,
                now,
                args.objective_evidence_sha256,
                candidate_ref,
                source_ref,
                args.block_scope,
            )
            schedule_objective(state, target_unit, now, DEFAULT_RECHECK_MINUTES[target_unit])
            active.setdefault("handoffs", []).append({
                "source_unit": source_unit,
                "target_unit": target_unit,
                "objective_state": objective_state,
                "source_ref": source_ref,
                "recorded_at_utc": utc(now),
            })
            return write_and_return(state_path, state, "HANDOFF_RECORDED", now, {"source_unit": source_unit, "target_unit": target_unit})
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
                args.block_scope,
            )
            schedule_objective(state, unit, now, DEFAULT_RECHECK_MINUTES[unit])
            return write_and_return(state_path, state, "OBJECTIVE_RECORDED", now, {"unit": unit})
        if args.command == "candidate-reject":
            active = state.get("active_packet")
            if active is None or active.get("boundary") is not None:
                return public(state, "CANDIDATE_REJECT_UNAVAILABLE", now)
            unit = active["unit"]
            if unit not in REFILL_UNITS:
                return public(state, "CANDIDATE_REJECT_ROUTE_INVALID", now)
            browsing = state["units"]["browsing"]
            if browsing["plan"] != "ACTIVE":
                return public(state, "CANDIDATE_REFILL_UNAVAILABLE", now)
            candidate_ref = objective_reference(
                "candidate_ref",
                args.candidate_ref or state["units"][unit]["objective"].get("candidate_ref"),
            )
            if candidate_ref is None:
                return public(state, "CANDIDATE_REFERENCE_REQUIRED", now)
            if rejected_candidate(state, unit, candidate_ref):
                return public(state, "CANDIDATE_ALREADY_REJECTED", now)
            reason = require_text("objective_reason", args.objective_reason, 512)
            evidence = sha256_value("objective_evidence_sha256", args.objective_evidence_sha256)
            source_ref = objective_reference(
                "source_ref",
                args.source_ref or state["units"][unit]["objective"].get("source_ref"),
            )
            if source_ref is None:
                return public(state, "CANDIDATE_SOURCE_REFERENCE_REQUIRED", now)
            rejection = {
                "unit": unit,
                "candidate_ref": candidate_ref,
                "source_ref": source_ref,
                "reason": reason,
                "evidence_sha256": evidence,
                "rejected_at_utc": utc(now),
            }
            state["candidate_rejections"].append(rejection)
            active["candidate_rejection"] = rejection
            current_objective = state["units"][unit]["objective"]
            current_objective.update({
                "state": "NOT_APPLICABLE",
                "reason": "EXACT_CANDIDATE_REJECTED: " + reason,
                "evidence_sha256": evidence,
                "candidate_ref": candidate_ref,
                "source_ref": source_ref,
                "updated_at_utc": utc(now),
            })
            clear_schedule(state, unit)
            browsing["objective"].update({
                "state": "PENDING",
                "reason": "FRESH_CANDIDATE_REQUIRED_AFTER_REJECTION",
                "evidence_sha256": evidence,
                "candidate_ref": None,
                "source_ref": candidate_ref,
                "updated_at_utc": utc(now),
            })
            if not schedule_next_heartbeat(state, "browsing", now):
                clear_schedule(state, "browsing")
            return write_and_return(
                state_path,
                state,
                "CANDIDATE_REJECTED_REFILL_SCHEDULED",
                now,
                {"unit": unit, "refill_unit": "browsing"},
            )
        if args.command == "finish":
            active = state.get("active_packet")
            if active is None or active.get("boundary") is not None:
                return public(state, "PACKET_UNSETTLED", now)
            outcome = require_text("outcome", args.outcome, 16).upper()
            if outcome not in OUTCOMES:
                return public(state, "OUTCOME_INVALID", now)
            unit = active["unit"]
            if (
                outward_authority(unit, state["units"][unit]["authority"])
                and args.objective_state is None
                and active.get("candidate_rejection") is None
            ):
                return public(state, "OBJECTIVE_STATE_REQUIRED", now, {"unit": unit})
            if args.objective_state == "LIVE_GATE_UNVERIFIED" and outcome != "YIELDED":
                return public(state, "LIVE_GATE_UNVERIFIED_REQUIRES_YIELD", now, {"unit": unit})
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
                    args.block_scope,
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
        if args.command == "recover":
            status = recover_stale_work(
                state,
                now,
                require_text("recovery_reason", args.recovery_reason, 512),
                args.recovery_action_key,
            )
            return write_and_return(state_path, state, status, now)
        if args.command == "cleanup-open":
            if state["state"] == "RETIRED":
                return public(state, "CLEANUP_UNAVAILABLE", now)
            if state.get("active_packet") or state.get("wake"):
                return public(state, "CLEANUP_BLOCKED", now)
            if state["state"] == "FINALIZING":
                return public(state, "CLEANUP_ALREADY_OPEN", now)
            if not cleanup_allowed(state, now):
                return public(state, "CLEANUP_NOT_DUE", now)
            clear_all_schedules(state)
            state["state"] = "FINALIZING"
            state["cleanup"] = {
                "state": "OPEN",
                "opened_at_utc": utc(now),
                "reason": require_text("cleanup_reason", args.cleanup_reason, 512),
            }
            state["history"].append({"kind": "CLEANUP", **state["cleanup"]})
            status = "CLEANUP_LATE" if now > state["cleanup_deadline_epoch"] else "CLEANUP_OPEN"
            return write_and_return(state_path, state, status, now)
        if args.command == "release-tabs":
            if state["state"] != "FINALIZING" or state.get("active_packet") or state.get("wake"):
                return public(state, "WORK_REMAINS", now)
            state["chrome_release"] = {"state": "RELEASED", "proof_sha256": sha256_value("proof_sha256", args.proof_sha256), "released_at_utc": utc(now)}
            return write_and_return(state_path, state, "TABS_RELEASED", now)
        if args.command == "heartbeat-delete":
            if state["state"] != "FINALIZING" or state["chrome_release"]["state"] != "RELEASED":
                return public(state, "HEARTBEAT_DELETE_BLOCKED", now)
            if state["heartbeat"]["state"] == "DELETED":
                return public(state, "HEARTBEAT_ALREADY_DELETED", now)
            state["heartbeat"]["state"] = "DELETED"
            state["heartbeat"]["deleted_at_utc"] = utc(now)
            state["heartbeat"]["delete_proof_sha256"] = sha256_value("heartbeat_delete_proof_sha256", args.proof_sha256)
            return write_and_return(state_path, state, "HEARTBEAT_DELETED", now)
        if args.command == "retire":
            if (
                state["state"] != "FINALIZING"
                or state.get("active_packet")
                or state.get("wake")
                or state["chrome_release"]["state"] != "RELEASED"
                or state["heartbeat"]["state"] != "DELETED"
            ):
                return public(state, "RETIRE_BLOCKED", now)
            state["state"] = "RETIRED"
            return write_and_return(state_path, state, "RETIRED", now)
        raise ValueError("unknown command")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("bootstrap", "inspect", "apply-revision", "presentation-promote", "canary-pass", "heartbeat-record", "heartbeat-observe", "wake-open", "decide", "start", "boundary-open", "boundary-settle", "freeze-action", "handoff", "objective-set", "candidate-reject", "finish", "recover", "cleanup-open", "release-tabs", "heartbeat-delete", "retire"))
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--owner-task-id", required=True)
    parser.add_argument("--mission-envelope", required=True, type=Path)
    parser.add_argument("--proof-sha256", "--proof-token", dest="proof_sha256")
    parser.add_argument("--presentation-title")
    parser.add_argument("--automation-id")
    parser.add_argument("--heartbeat-target-task-id")
    parser.add_argument("--heartbeat-rrule")
    parser.add_argument("--heartbeat-until-at-utc")
    parser.add_argument("--heartbeat-next-run-at-utc")
    parser.add_argument("--expected-at-utc")
    parser.add_argument("--wake-source")
    parser.add_argument("--unit")
    parser.add_argument("--target-unit")
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
    parser.add_argument("--objective-evidence-sha256", "--objective-evidence-token", dest="objective_evidence_sha256")
    parser.add_argument("--candidate-ref")
    parser.add_argument("--source-ref")
    parser.add_argument("--block-scope")
    parser.add_argument("--recovery-reason")
    parser.add_argument("--recovery-action-key")
    parser.add_argument("--cleanup-reason")
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
