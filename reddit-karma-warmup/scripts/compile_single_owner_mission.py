#!/usr/bin/env python3
"""Compile immutable, revisioned single-owner Reddit mission envelopes.

This script is deliberately local-only: it does not read Chrome, create a
task, run a scheduler, or infer a user's outward-action authorization. It
turns a caller-supplied structured interpretation of one direct user prompt
into a canonical envelope that the queue can verify later.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile


LANE_ORDER = ("browsing", "comments", "posts", "follow-up", "presence")
DEFAULT_AUTHORITY = {
    "browsing": "READ_ONLY",
    "comments": "RESEARCH_ONLY",
    "posts": "RESEARCH_ONLY",
    "follow-up": "RESEARCH_ONLY",
    "presence": "RESEARCH_ONLY",
}
ALLOWED_AUTHORITY = {
    "browsing": ("READ_ONLY",),
    "comments": ("RESEARCH_ONLY", "COMMENT_AUTHORIZED"),
    "posts": ("RESEARCH_ONLY", "POST_AUTHORIZED"),
    "follow-up": ("RESEARCH_ONLY", "FOLLOWUP_AUTHORIZED"),
    "presence": ("RESEARCH_ONLY", "PRESENCE_AUTHORIZED"),
}
SAFE_OVERRIDE_TEXT_KEYS = {
    "intensity",
    "style",
    "language_style",
    "account_direction",
    "mission_identity_focus",
    "research_focus",
    "target_pool_policy",
    "community_expansion",
    "stop_condition",
}
SAFE_OVERRIDE_TEXT_LIST_KEYS = {"direction_tags", "target_communities", "target_posts"}
BUSINESS_GOALS = (
    "community_discovery",
    "conversation_entry",
    "feedback_validation",
    "project_distribution",
    "relationship_maintenance",
    "profile_readiness",
)
COMMUNITY_SCOPE_MODES = ("closed", "seeded_expandable", "discover")
COVERAGE_BUDGETS = ("narrow", "standard", "broad")
ACTION_THRESHOLDS = ("high", "standard", "low")
ACTION_BUDGETS = ("minimal", "standard", "active")
FREQUENCY_ALIASES = {
    "low": {"coverage_budget": "standard", "action_threshold": "high", "action_budget": "minimal"},
    "standard": {"coverage_budget": "standard", "action_threshold": "standard", "action_budget": "standard"},
    "high": {"coverage_budget": "broad", "action_threshold": "standard", "action_budget": "active"},
}
GOAL_DEFAULT_SCOPE = {
    "community_discovery": "discover",
    "conversation_entry": "seeded_expandable",
    "feedback_validation": "discover",
    "project_distribution": "discover",
    "relationship_maintenance": "closed",
    "profile_readiness": "closed",
}
MODEL_REQUEST = {
    "preferred_model": "gpt-5.6-luna",
    "reasoning_effort": "xhigh",
    "request_mode": "PREFERRED_IF_HOST_SUPPORTED",
    "evidence_state": "REQUESTED_NOT_RUNTIME_PROOF",
}
THROUGHPUT_TARGETS = {
    "minimal": {
        "comments_per_hour": 1,
        "posts_per_two_hours": 0,
        "followups_per_hour": 0,
        "qualified_reads_per_hour": 12,
        "public_actions_per_hour_ceiling": 2,
    },
    "standard": {
        "comments_per_hour": 2,
        "posts_per_two_hours": 1,
        "followups_per_hour": 1,
        "qualified_reads_per_hour": 20,
        "public_actions_per_hour_ceiling": 4,
    },
    "active": {
        "comments_per_hour": 4,
        "posts_per_two_hours": 1,
        "followups_per_hour": 1,
        "qualified_reads_per_hour": 30,
        "public_actions_per_hour_ceiling": 6,
    },
}


def fail(message):
    raise ValueError(message)


def text_field(raw, name, minimum=1, maximum=2000):
    if not isinstance(raw, str):
        fail(name + " must be text")
    value = raw.strip()
    if not minimum <= len(value) <= maximum or "\x00" in value:
        fail("invalid " + name)
    return value


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_hash(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def parse_utc(raw, name):
    value = text_field(raw, name, 20, 64)
    if not value.endswith("Z"):
        fail(name + " must be UTC RFC3339 ending in Z")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid " + name) from exc
    if parsed.tzinfo != dt.timezone.utc:
        fail(name + " must use UTC")
    return parsed.replace(microsecond=0)


def utc_string(value):
    return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_units(raw, name, allow_all=False):
    if raw == ["all"] and allow_all:
        raw = list(LANE_ORDER)
    if not isinstance(raw, list) or not raw:
        fail(name + " must be a non-empty list")
    if any(unit not in LANE_ORDER for unit in raw) or len(set(raw)) != len(raw):
        fail("invalid " + name)
    canonical = [unit for unit in LANE_ORDER if unit in raw]
    if raw != canonical and raw != ["all"]:
        fail(name + " must use canonical unit order")
    return canonical


def normalize_overrides(raw):
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        fail("explicit_user_overrides must be object")
    normalized = {}
    for key, value in raw.items():
        if key in SAFE_OVERRIDE_TEXT_KEYS:
            normalized[key] = text_field(value, "explicit_user_overrides." + key, 1, 512)
        elif key in SAFE_OVERRIDE_TEXT_LIST_KEYS:
            if not isinstance(value, list) or not value or len(value) > 64:
                fail("invalid explicit_user_overrides." + key)
            normalized[key] = [
                text_field(item, "explicit_user_overrides." + key, 1, 256)
                for item in value
            ]
        else:
            fail("unsupported explicit_user_overrides key")
    return normalized


def derived_business_goal(selected):
    if selected == ["presence"]:
        return "profile_readiness"
    if selected == ["follow-up"]:
        return "relationship_maintenance"
    if "posts" in selected:
        return "feedback_validation"
    if "comments" in selected:
        return "conversation_entry"
    return "community_discovery"


def normalize_material_refs(raw):
    if raw is None:
        return []
    if not isinstance(raw, list) or len(raw) > 32:
        fail("material_refs must be a list of at most 32 items")
    return [text_field(item, "material_refs", 1, 512) for item in raw]


def normalize_planning_targets(raw):
    if raw is None:
        return {}
    if not isinstance(raw, dict) or len(raw) > 16:
        fail("planning_targets must be an object with at most 16 keys")
    normalized = {}
    for key, value in raw.items():
        target = text_field(key, "planning_targets key", 1, 64)
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 1000:
            fail("planning_targets values must be integers from 0 to 1000")
        normalized[target] = value
    return dict(sorted(normalized.items()))


def normalize_strategy(raw, selected, parent):
    supplied = raw if raw is not None else {}
    if not isinstance(supplied, dict):
        fail("mission_strategy must be object")
    allowed = {
        "business_goal", "community_scope", "coverage_budget", "action_threshold",
        "action_budget", "frequency", "material_refs", "planning_targets",
    }
    if set(supplied) - allowed:
        fail("unsupported mission_strategy key")
    inherited = parent.get("mission_strategy", {}) if parent else {}
    if inherited and not isinstance(inherited, dict):
        fail("invalid parent mission_strategy")
    frequency_input = supplied.get("frequency")
    frequency = frequency_input if frequency_input is not None else inherited.get("frequency_alias")
    if frequency is not None and frequency not in FREQUENCY_ALIASES:
        fail("mission_strategy.frequency must be low, standard, or high")
    alias = FREQUENCY_ALIASES.get(frequency_input, {})
    business_goal = supplied.get("business_goal", inherited.get("business_goal", derived_business_goal(selected)))
    if business_goal not in BUSINESS_GOALS:
        fail("invalid mission_strategy.business_goal")
    community_scope = supplied.get("community_scope", inherited.get("community_scope", GOAL_DEFAULT_SCOPE[business_goal]))
    if community_scope not in COMMUNITY_SCOPE_MODES:
        fail("invalid mission_strategy.community_scope")
    coverage_budget = supplied.get("coverage_budget", alias.get("coverage_budget", inherited.get("coverage_budget", "standard")))
    if coverage_budget not in COVERAGE_BUDGETS:
        fail("invalid mission_strategy.coverage_budget")
    action_threshold = supplied.get("action_threshold", alias.get("action_threshold", inherited.get("action_threshold", "standard")))
    if action_threshold not in ACTION_THRESHOLDS:
        fail("invalid mission_strategy.action_threshold")
    action_budget = supplied.get("action_budget", alias.get("action_budget", inherited.get("action_budget", "standard")))
    if action_budget not in ACTION_BUDGETS:
        fail("invalid mission_strategy.action_budget")
    material_refs = normalize_material_refs(supplied["material_refs"]) if "material_refs" in supplied else list(inherited.get("material_refs", []))
    planning_targets = dict(THROUGHPUT_TARGETS[action_budget])
    planning_targets.update(dict(inherited.get("planning_targets", {})))
    if "planning_targets" in supplied:
        planning_targets.update(normalize_planning_targets(supplied["planning_targets"]))
    return {
        "business_goal": business_goal,
        "community_scope": community_scope,
        "coverage_budget": coverage_budget,
        "action_threshold": action_threshold,
        "action_budget": action_budget,
        "frequency_alias": frequency,
        "material_refs": material_refs,
        "planning_targets": planning_targets,
    }


def expected_hash(envelope):
    unsigned = dict(envelope)
    stored = unsigned.pop("mission_envelope_sha256", None)
    if not isinstance(stored, str) or len(stored) != 64:
        fail("invalid mission_envelope_sha256")
    if canonical_hash(unsigned) != stored:
        fail("mission envelope hash mismatch")
    return stored


def load_parent(path):
    try:
        envelope = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("invalid parent envelope") from exc
    if not isinstance(envelope, dict):
        fail("invalid parent envelope")
    expected_hash(envelope)
    if envelope.get("schema") != "reddit_single_owner_mission/v1":
        fail("unsupported parent schema")
    if envelope.get("execution_topology") != "single_owner_v1":
        fail("parent is not single-owner")
    if not isinstance(envelope.get("mission_revision"), int) or envelope["mission_revision"] < 1:
        fail("invalid parent revision")
    canonical_units(envelope.get("selected_units"), "parent selected_units")
    canonical_units(envelope.get("paused_units", []), "parent paused_units") if envelope.get("paused_units") else None
    return envelope


def normalize_authority(raw, selected, parent, receipt):
    supplied = raw if raw is not None else {}
    if not isinstance(supplied, dict):
        fail("unit_authority must be object")
    if any(unit not in selected for unit in supplied):
        fail("authority supplied for unselected unit")
    result = {}
    parent_authority = parent.get("unit_authority", {}) if parent else {}
    for unit in selected:
        authority = supplied.get(unit, parent_authority.get(unit, DEFAULT_AUTHORITY[unit]))
        # Missions compiled before voting was removed may carry the legacy
        # authority in their parent envelope.  Migrate that state to the only
        # supported browsing authority instead of carrying a vote capability
        # into a new revision.
        if unit == "browsing" and authority == "VOTE_AUTHORIZED":
            authority = "READ_ONLY"
        if authority not in ALLOWED_AUTHORITY[unit]:
            fail("invalid authority for " + unit)
        result[unit] = authority
        old = parent_authority.get(unit, DEFAULT_AUTHORITY[unit])
        if authority != DEFAULT_AUTHORITY[unit] and (not parent or old != authority):
            if receipt is None:
                fail("outward authority requires authorization_receipt")
    return result


def normalize_vote_policy(raw, selected, authority, parent, receipt):
    policy = raw if raw is not None else (parent.get("vote_policy") if parent else "DISABLED")
    if policy not in (None, "DISABLED", "BROWSING_ONLY"):
        fail("invalid vote_policy")
    # `BROWSING_ONLY` is accepted only as a legacy input so an existing
    # mission can be revised safely.  It is never emitted again.
    return "DISABLED"


def plan_status(selected, paused):
    return {unit: ("PAUSED" if unit in paused else "ACTIVE") if unit in selected else "REMOVED" for unit in LANE_ORDER}


def derive_changes(parent, selected, paused):
    previous = plan_status(parent.get("selected_units", []), parent.get("paused_units", [])) if parent else {unit: "REMOVED" for unit in LANE_ORDER}
    desired = plan_status(selected, paused)
    changes = {}
    for unit in LANE_ORDER:
        before, after = previous[unit], desired[unit]
        if before == after:
            continue
        if before == "REMOVED" and after == "ACTIVE":
            changes[unit] = "ADD"
        elif before == "ACTIVE" and after == "PAUSED":
            changes[unit] = "PAUSE"
        elif before == "PAUSED" and after == "ACTIVE":
            changes[unit] = "RESUME"
        elif after == "REMOVED":
            changes[unit] = "REMOVE"
        else:
            fail("unsupported unit transition")
    return changes


def derive_authority_changes(parent, selected, authority):
    """Return the complete authority delta for an auditable hot-plug revision.

    A revision can safely change authorization without changing its five-unit
    plan (for example, research-only comments -> COMMENT_AUTHORIZED after a
    direct user receipt).  Unit-plan deltas alone must not reject that case.
    """
    if parent is None:
        return {}
    previous = parent.get("unit_authority", {})
    changes = {}
    for unit in LANE_ORDER:
        before = previous.get(unit)
        after = authority.get(unit) if unit in selected else None
        if before != after:
            changes[unit] = {"from": before, "to": after}
    return changes


def derive_vote_policy_change(parent, vote_policy):
    if parent is None:
        return None
    previous = parent.get("vote_policy")
    if previous == vote_policy:
        return None
    return {"from": previous, "to": vote_policy}


def derive_strategy_change(parent, strategy):
    if parent is None:
        return None
    previous = parent.get("mission_strategy", {})
    if previous == strategy:
        return None
    return {"from_sha256": canonical_hash(previous), "to_sha256": canonical_hash(strategy)}


def atomic_write_json(path, value):
    path = Path(path)
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


def compile_envelope(raw, parent=None):
    if not isinstance(raw, dict):
        fail("input must be object")
    source_prompt = text_field(raw.get("source_prompt"), "source_prompt", 1, 10000)
    receipt_raw = raw.get("authorization_receipt")
    receipt = text_field(receipt_raw, "authorization_receipt", 1, 10000) if receipt_raw is not None else None
    if parent is None:
        mission_id = text_field(raw.get("mission_id"), "mission_id", 8, 256)
        account = text_field(raw.get("account"), "account", 3, 128)
        if not account.startswith("u/"):
            fail("account must use u/<name>")
        direction = text_field(raw.get("direction"), "direction", 3, 2000)
        duration = raw.get("duration_hours")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or not 0 < duration <= 168:
            fail("duration_hours must be between 0 and 168")
        start = parse_utc(raw.get("operation_start_at"), "operation_start_at")
        stop = start + dt.timedelta(hours=duration)
        revision = 1
        parent_hash = None
        requested = canonical_units(raw.get("requested_work_types"), "requested_work_types", allow_all=True)
        paused = canonical_units(raw.get("paused_work_types", []), "paused_work_types") if raw.get("paused_work_types") else []
        if any(unit not in requested for unit in paused):
            fail("paused_work_types must be selected")
        if paused:
            fail("initial mission cannot add a paused unit")
    else:
        mission_id = parent["mission_id"]
        account = parent["account"]
        direction = parent["direction"]
        duration = parent["duration_hours"]
        start = parse_utc(parent["operation_start_at"], "parent operation_start_at")
        stop = parse_utc(parent["operation_stop_at"], "parent operation_stop_at")
        revision = parent["mission_revision"] + 1
        parent_hash = parent["mission_envelope_sha256"]
        for key, expected in (("mission_id", mission_id), ("account", account), ("direction", direction)):
            if key in raw and raw[key] != expected:
                fail(key + " cannot change in a hot-plug revision")
        requested = canonical_units(raw.get("requested_work_types", parent["selected_units"]), "requested_work_types", allow_all=True)
        paused = canonical_units(raw.get("paused_work_types", parent.get("paused_units", [])), "paused_work_types") if raw.get("paused_work_types", parent.get("paused_units", [])) else []
        if any(unit not in requested for unit in paused):
            fail("paused_work_types must be selected")
    authority = normalize_authority(raw.get("unit_authority"), requested, parent, receipt)
    vote_policy = normalize_vote_policy(raw.get("vote_policy"), requested, authority, parent, receipt)
    strategy = normalize_strategy(raw.get("mission_strategy"), requested, parent)
    changes = derive_changes(parent, requested, paused)
    authority_changes = derive_authority_changes(parent, requested, authority)
    vote_policy_change = derive_vote_policy_change(parent, vote_policy)
    strategy_change = derive_strategy_change(parent, strategy)
    if parent is None:
        changes = {unit: "ADD" for unit in requested}
    if parent is not None and not (changes or authority_changes or vote_policy_change or strategy_change):
        fail("hot-plug revision has no unit, authority, vote-policy, or strategy change")
    envelope = {
        "schema": "reddit_single_owner_mission/v1",
        "execution_topology": "single_owner_v1",
        "mission_id": mission_id,
        "mission_revision": revision,
        "parent_envelope_sha256": parent_hash,
        "account": account,
        "direction": direction,
        "operation_start_at": utc_string(start),
        "operation_stop_at": utc_string(stop),
        "duration_hours": duration,
        "selected_units": requested,
        "paused_units": paused,
        "unit_authority": authority,
        "vote_policy": vote_policy,
        "mission_strategy": strategy,
        "unit_changes": changes,
        "authority_changes": authority_changes,
        "vote_policy_change": vote_policy_change,
        "strategy_change": strategy_change,
        "model_request": dict(MODEL_REQUEST),
        "authorization_receipt_sha256": sha256_text(receipt) if receipt else None,
        "explicit_user_overrides": normalize_overrides(raw.get("explicit_user_overrides")),
        "source_prompt_sha256": sha256_text(source_prompt),
    }
    envelope["mission_envelope_sha256"] = canonical_hash(envelope)
    return envelope


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--parent-envelope", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        raw = json.loads(args.input.read_text(encoding="utf-8"))
        parent = load_parent(args.parent_envelope) if args.parent_envelope else None
        envelope = compile_envelope(raw, parent)
        if args.output is not None:
            atomic_write_json(args.output, envelope)
        print(json.dumps(envelope, ensure_ascii=False, sort_keys=True))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
