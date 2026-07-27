#!/usr/bin/env python3
"""Normalize the three Reddit startup answers without browser or network work."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile


LANE_ORDER = ("browsing", "comments", "posts", "follow-up", "presence")
AUTHORITY = {
    "simulate_browsing": {
        "aliases": {"simulate_browsing", "simulate browsing", "模拟浏览", "research_first", "research first", "研究优先"},
        "business_goal": "community_discovery",
        "requested_work_types": ["browsing"],
        "unit_authority": {"browsing": "READ_ONLY"},
        "profile": {"coverage_budget": "standard", "action_threshold": "high", "action_budget": "minimal"},
    },
    "discussion_participation": {
        "aliases": {"discussion_participation", "discussion participation", "参与讨论", "discussion_first", "discussion first", "评论优先"},
        "business_goal": "conversation_entry",
        "requested_work_types": ["browsing", "comments"],
        "unit_authority": {"browsing": "READ_ONLY", "comments": "COMMENT_AUTHORIZED"},
        "profile": {"coverage_budget": "standard", "action_threshold": "standard", "action_budget": "standard"},
    },
    "full_progression": {
        "aliases": {"full_progression", "full progression", "全面推进", "project_operation", "project operation", "项目运营"},
        "business_goal": "project_distribution",
        "requested_work_types": list(LANE_ORDER),
        "unit_authority": {
            "browsing": "READ_ONLY",
            "comments": "COMMENT_AUTHORIZED",
            "posts": "POST_AUTHORIZED",
            "follow-up": "FOLLOWUP_AUTHORIZED",
            "presence": "PRESENCE_AUTHORIZED",
        },
        "profile": {"coverage_budget": "broad", "action_threshold": "standard", "action_budget": "active"},
    },
}
PRESET_TAGS = {
    "社交与社区": ["social", "community", "community-ux"],
    "个人创作与独立项目": ["personal-creation", "indie-projects", "solo-building"],
    "3D/游戏/共创": ["spatial", "games", "co-creation"],
}
VALID_SCOPES = {"closed", "seeded_expandable", "discover"}
BUSINESS_GOALS = {
    "community_discovery", "conversation_entry", "feedback_validation",
    "project_distribution", "relationship_maintenance", "profile_readiness",
}
VALID_COVERAGE = {"narrow", "standard", "broad"}
VALID_THRESHOLD = {"high", "standard", "low"}
VALID_BUDGET = {"minimal", "standard", "active"}
CUSTOM_UNIT_AUTHORITY = {
    "browsing": {"READ_ONLY"},
    "comments": {"RESEARCH_ONLY", "COMMENT_AUTHORIZED"},
    "posts": {"RESEARCH_ONLY", "POST_AUTHORIZED"},
    "follow-up": {"RESEARCH_ONLY", "FOLLOWUP_AUTHORIZED"},
    "presence": {"RESEARCH_ONLY", "PRESENCE_AUTHORIZED"},
}


def fail(message):
    raise ValueError(message)


def text(value, name, minimum=1, maximum=2000):
    if not isinstance(value, str):
        fail(name + " must be text")
    value = value.strip()
    if not minimum <= len(value) <= maximum or "\x00" in value:
        fail("invalid " + name)
    return value


def canonical_hash(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def duration_hours(value):
    if isinstance(value, bool):
        fail("invalid duration_hours")
    if isinstance(value, (int, float)):
        result = value
    elif isinstance(value, str):
        normalized = value.strip().lower().replace("小时", " hours")
        match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(?:hours?|h)?", normalized)
        if not match:
            fail("invalid duration_hours")
        result = float(match.group(1))
    else:
        fail("invalid duration_hours")
    if not 0 < result <= 168:
        fail("duration_hours must be between 0 and 168")
    return int(result) if float(result).is_integer() else float(result)


def normalized_list(value, name, maximum, prefix=None):
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > maximum:
        fail("invalid " + name)
    result = [text(item, name, 1, 256) for item in value]
    if len(result) != len(set(result)):
        fail("duplicate " + name)
    if prefix and any(not item.startswith(prefix) for item in result):
        fail("invalid " + name)
    return result


def canonical_units(value):
    if not isinstance(value, list) or not value or len(value) != len(set(value)):
        fail("invalid custom_authority.requested_work_types")
    if any(unit not in LANE_ORDER for unit in value):
        fail("invalid custom_authority.requested_work_types")
    normalized = [unit for unit in LANE_ORDER if unit in value]
    if value != normalized:
        fail("custom_authority.requested_work_types must use canonical unit order")
    return normalized


def custom_profile(raw):
    if not isinstance(raw, dict):
        fail("custom authority requires structured custom_authority")
    allowed = {"business_goal", "requested_work_types", "unit_authority", "coverage_budget", "action_threshold", "action_budget"}
    if set(raw) - allowed or {"business_goal", "requested_work_types", "unit_authority"} - set(raw):
        fail("invalid custom_authority")
    business_goal = text(raw["business_goal"], "custom_authority.business_goal", 3, 128)
    if business_goal not in BUSINESS_GOALS:
        fail("invalid custom_authority.business_goal")
    units = canonical_units(raw["requested_work_types"])
    authority = raw["unit_authority"]
    if not isinstance(authority, dict) or set(authority) != set(units):
        fail("custom_authority.unit_authority must cover exactly requested units")
    normalized_authority = {}
    for unit in units:
        choice = text(authority[unit], "custom_authority.unit_authority", 3, 64)
        if choice not in CUSTOM_UNIT_AUTHORITY[unit]:
            fail("invalid custom authority for " + unit)
        normalized_authority[unit] = choice
    profile = {
        "coverage_budget": raw.get("coverage_budget", "standard"),
        "action_threshold": raw.get("action_threshold", "standard"),
        "action_budget": raw.get("action_budget", "standard"),
    }
    if profile["coverage_budget"] not in VALID_COVERAGE:
        fail("invalid custom_authority.coverage_budget")
    if profile["action_threshold"] not in VALID_THRESHOLD:
        fail("invalid custom_authority.action_threshold")
    if profile["action_budget"] not in VALID_BUDGET:
        fail("invalid custom_authority.action_budget")
    return {
        "business_goal": business_goal,
        "requested_work_types": units,
        "unit_authority": normalized_authority,
        "profile": profile,
    }


def resolve_profile(value, custom):
    answer = text(value, "authority_profile", 1, 256)
    for name, profile in AUTHORITY.items():
        if answer in profile["aliases"]:
            return name, profile
    return "custom", custom_profile(custom)


def normalize(raw):
    if not isinstance(raw, dict):
        fail("input must be object")
    if raw.get("cancelled") is True:
        return {"schema": "reddit_startup_intake/v1", "status": "STARTUP_CANCELLED_BY_USER"}
    if raw.get("cancelled") not in (None, False):
        fail("cancelled must be boolean")
    missing = []
    if raw.get("duration_hours", raw.get("duration")) in (None, ""):
        missing.append("duration_hours")
    if raw.get("direction") in (None, ""):
        missing.append("direction")
    if raw.get("authority_profile") in (None, ""):
        missing.append("authority_profile")
    if missing:
        return {"schema": "reddit_startup_intake/v1", "status": "WAITING_FOR_STARTUP_INPUT", "missing": missing}

    duration = duration_hours(raw.get("duration_hours", raw.get("duration")))
    direction = text(raw["direction"], "direction", 3, 2000)
    profile_name, profile = resolve_profile(raw["authority_profile"], raw.get("custom_authority"))
    named_communities = normalized_list(raw.get("named_communities"), "named_communities", 64, "r/")
    supplied_scope = raw.get("community_scope")
    if supplied_scope is None:
        scope = "seeded_expandable" if named_communities else "discover"
    else:
        scope = text(supplied_scope, "community_scope", 3, 64)
        if scope not in VALID_SCOPES:
            fail("invalid community_scope")
        if scope == "closed" and not named_communities:
            fail("closed community_scope requires named_communities")
    material_refs = normalized_list(raw.get("material_refs"), "material_refs", 32)
    tags = normalized_list(raw.get("direction_tags"), "direction_tags", 32)
    if not tags:
        tags = PRESET_TAGS.get(direction, [])
    overrides = {"account_direction": text(raw.get("account_direction", direction), "account_direction", 3, 512)}
    if tags:
        overrides["direction_tags"] = tags
    if named_communities:
        overrides["target_communities"] = named_communities
    strategy = {
        "business_goal": profile["business_goal"],
        "community_scope": scope,
        **profile["profile"],
        "material_refs": material_refs,
        "planning_targets": {},
    }
    normalized = {
        "duration_hours": duration,
        "direction": direction,
        "authority_profile": profile_name,
        "requested_work_types": profile["requested_work_types"],
        "unit_authority": profile["unit_authority"],
        "authorization_receipt": text(raw.get("authorization_receipt", raw["authority_profile"]), "authorization_receipt", 1, 10000),
        "mission_strategy": strategy,
        "explicit_user_overrides": overrides,
    }
    return {
        "schema": "reddit_startup_intake/v1",
        "status": "STARTUP_ANSWERS_COMPLETE",
        "answer_sha256": canonical_hash(raw),
        "normalized": normalized,
    }


def atomic_write(path, value):
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


def self_test():
    assert normalize({"duration_hours": 2}) == {
        "schema": "reddit_startup_intake/v1",
        "status": "WAITING_FOR_STARTUP_INPUT",
        "missing": ["direction", "authority_profile"],
    }
    assert normalize({"cancelled": True})["status"] == "STARTUP_CANCELLED_BY_USER"
    result = normalize({
        "duration": "2 小时",
        "direction": "个人创作与独立项目",
        "authority_profile": "全面推进",
    })
    assert result["status"] == "STARTUP_ANSWERS_COMPLETE"
    assert result["normalized"]["mission_strategy"]["community_scope"] == "discover"
    assert result["normalized"]["authority_profile"] == "full_progression"
    assert result["normalized"]["requested_work_types"] == list(LANE_ORDER)
    assert result["normalized"]["mission_strategy"]["material_refs"] == []
    seeded = normalize({
        "duration_hours": 4,
        "direction": "custom direction",
        "authority_profile": "参与讨论",
        "named_communities": ["r/SideProject"],
    })
    assert seeded["normalized"]["authority_profile"] == "discussion_participation"
    assert seeded["normalized"]["mission_strategy"]["community_scope"] == "seeded_expandable"
    browse_only = normalize({
        "duration_hours": 4,
        "direction": "社交与社区",
        "authority_profile": "模拟浏览",
    })
    assert browse_only["normalized"]["authority_profile"] == "simulate_browsing"
    assert browse_only["normalized"]["requested_work_types"] == ["browsing"]
    custom = normalize({
        "duration_hours": 2,
        "direction": "custom direction",
        "authority_profile": "comments only, standard",
        "custom_authority": {
            "business_goal": "conversation_entry",
            "requested_work_types": ["browsing", "comments"],
            "unit_authority": {"browsing": "READ_ONLY", "comments": "COMMENT_AUTHORIZED"},
        },
    })
    assert custom["normalized"]["authority_profile"] == "custom"
    return {"status": "PASS", "schema": "reddit_startup_intake/v1"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        if args.input or args.output:
            parser.error("--self-test cannot be combined with input/output")
        print(json.dumps(self_test(), sort_keys=True))
        return
    if not args.input:
        parser.error("--input is required")
    try:
        raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = normalize(raw)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        result = {"schema": "reddit_startup_intake/v1", "status": "INVALID_STARTUP_INPUT", "error": str(exc)}
    if args.output:
        atomic_write(args.output, result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
