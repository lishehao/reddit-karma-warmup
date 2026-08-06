#!/usr/bin/env python3
"""Normalize Reddit startup answers or an explicit target assignment locally."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit


LANE_ORDER = ("browsing", "comments", "posts", "follow-up", "presence")
AUTHORITY = {
    "simulate_browsing": {
        "aliases": {"simulate_browsing", "simulate browsing", "模拟浏览", "research_first", "research first", "研究优先"},
        "business_goal": "community_discovery",
        "requested_work_types": ["browsing"],
        "unit_authority": {"browsing": "READ_ONLY"},
        "profile": {"coverage_budget": "standard", "action_threshold": "high", "action_budget": "standard"},
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
        "profile": {"coverage_budget": "standard", "action_threshold": "standard", "action_budget": "standard"},
    },
}
FREQUENCY_ALIASES = {
    "low": {"low", "minimal", "低", "低频", "慢"},
    "standard": {"standard", "normal", "默认", "标准", "中", "中频"},
    "high": {"high", "active", "高", "高频", "快"},
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

TEXT_FALLBACK = (
    "请先回答以下四个问题（可直接按 `1) … 2) … 3) … 4) …` 回复）：\n"
    "1) 运行多久？可选：2 小时 / 4 小时 / 8 小时。\n"
    "2) 这轮想围绕什么方向或哪些社区运营？"
    "可选：社交与社区 / 个人创作与独立项目 / 3D/游戏/共创。\n"
    "3) 这轮希望做到哪一步？可选：模拟浏览 / 参与讨论 / 全面推进。\n"
    "4) 互动节奏希望怎样？可选：低 / 标准 / 高。"
)

DIRECT_TARGET_FALLBACK = (
    "直接目标模式还缺少必要信息：目标帖子链接、要做的动作（浏览/评论/跟进）和运行时长。"
    "补齐后会在当前任务中直接开始第一轮，不再重复启动问卷。"
)
DIRECT_ACTION_ALIASES = {
    "browse": "browsing", "browsing": "browsing", "浏览": "browsing",
    "comment": "comments", "comments": "comments", "评论": "comments", "回复": "comments",
    "followup": "follow-up", "follow-up": "follow-up", "跟进": "follow-up", "回复跟进": "follow-up",
    "post": "posts", "posts": "posts", "发帖": "posts",
    "presence": "presence", "主页": "presence", "profile": "presence",
}
DIRECT_AUTHORITY = {
    "browsing": "READ_ONLY",
    "comments": "COMMENT_AUTHORIZED",
    "posts": "POST_AUTHORIZED",
    "follow-up": "FOLLOWUP_AUTHORIZED",
    "presence": "PRESENCE_AUTHORIZED",
}
EXCLUDED_COMMUNITIES = {"r/saas"}


def fail(message):
    raise ValueError(message)


def normalize_frequency(value, default=None):
    if value in (None, ""):
        if default is None:
            fail("frequency is required")
        return default
    if not isinstance(value, str):
        fail("invalid frequency")
    answer = value.strip().lower()
    for canonical, aliases in FREQUENCY_ALIASES.items():
        if answer in aliases:
            return canonical
    fail("frequency must be low, standard, or high")


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


def target_post_urls(raw):
    value = raw.get("target_posts")
    if value is None:
        value = raw.get("target_post_urls", raw.get("target_refs"))
    if not isinstance(value, list) or not 1 <= len(value) <= 32:
        fail("direct target mode requires 1 to 32 target_posts")
    result = []
    for item in value:
        url = text(item, "target_posts", 1, 1000)
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower()
        if parsed.scheme != "https" or host not in {"reddit.com", "www.reddit.com", "old.reddit.com", "redd.it", "www.redd.it"}:
            fail("target_posts must be HTTPS Reddit post URLs")
        path = parsed.path.rstrip("/")
        if "/comments/" not in path and not (host.endswith("redd.it") and path.count("/") == 1):
            fail("target_posts must point to Reddit posts")
        canonical = url.split("#", 1)[0]
        if canonical not in result:
            result.append(canonical)
    if len(result) != len(value):
        fail("duplicate target_posts")
    return result


def target_communities(urls):
    result = []
    for url in urls:
        match = re.search(r"/(?:r|u)/([^/]+)(?:/|$)", urlsplit(url).path, re.IGNORECASE)
        if match and urlsplit(url).path.lower().split("/")[1:2] == ["r"]:
            name = "r/" + match.group(1)
            if name.lower() in EXCLUDED_COMMUNITIES:
                fail("excluded community: " + name.lower())
            if name not in result:
                result.append(name)
    return result


def direct_units(raw):
    supplied = raw.get("requested_work_types", raw.get("direct_units", raw.get("allowed_actions")))
    if supplied is None:
        fail("direct target mode requires requested_work_types")
    if not isinstance(supplied, list) or not supplied:
        fail("invalid direct requested_work_types")
    mapped = []
    for item in supplied:
        if not isinstance(item, str):
            fail("invalid direct requested_work_types")
        key = item.strip().lower()
        unit = DIRECT_ACTION_ALIASES.get(key, DIRECT_ACTION_ALIASES.get(item.strip()))
        if unit is None:
            fail("invalid direct requested_work_types")
        if unit not in mapped:
            mapped.append(unit)
    canonical = [unit for unit in LANE_ORDER if unit in mapped]
    if mapped != canonical:
        fail("direct requested_work_types must use canonical unit order")
    return canonical


def direct_waiting(missing):
    return {
        "schema": "reddit_startup_intake/v1",
        "status": "WAITING_FOR_DIRECT_TARGET_INPUT",
        "missing": missing,
        "text_fallback": {
            "channel": "DIRECT_TEXT",
            "request_user_input_repeat": False,
            "message": DIRECT_TARGET_FALLBACK,
        },
    }


def normalize_direct_target(raw):
    if raw.get("direct_target_mode") not in (None, True):
        fail("direct_target_mode must be boolean")
    missing = []
    try:
        urls = target_post_urls(raw)
    except ValueError:
        if not any(raw.get(key) for key in ("target_posts", "target_post_urls", "target_refs")):
            missing.append("target_posts")
        else:
            raise
    if raw.get("duration_hours", raw.get("duration")) in (None, ""):
        missing.append("duration_hours")
    if not any(raw.get(key) for key in ("requested_work_types", "direct_units", "allowed_actions")):
        missing.append("requested_work_types")
    if missing:
        return direct_waiting(missing)
    urls = target_post_urls(raw)
    duration = duration_hours(raw.get("duration_hours", raw.get("duration")))
    units = direct_units(raw)
    direction = raw.get("direction", raw.get("account_direction", "targeted Reddit post discussions"))
    direction = text(direction, "direction", 3, 2000)
    frequency = normalize_frequency(raw.get("frequency", raw.get("interaction_frequency")), "standard")
    named = target_communities(urls)
    supplied_community_scope = raw.get("community_scope")
    if supplied_community_scope not in (None, "closed"):
        fail("direct target mode uses closed community_scope")
    authority = dict(DIRECT_AUTHORITY)
    supplied_authority = raw.get("unit_authority")
    if supplied_authority is not None:
        if not isinstance(supplied_authority, dict) or set(supplied_authority) - set(units) or set(supplied_authority) != set(units):
            fail("direct unit_authority must cover exactly requested units")
        for unit in units:
            choice = text(supplied_authority[unit], "unit_authority", 3, 64)
            expected = DIRECT_AUTHORITY[unit]
            if choice != expected:
                fail("invalid direct authority for " + unit)
            authority[unit] = choice
    material_refs = normalized_list(raw.get("material_refs"), "material_refs", 32)
    tags = normalized_list(raw.get("direction_tags"), "direction_tags", 32)
    overrides = {
        "account_direction": text(raw.get("account_direction", direction), "account_direction", 3, 512),
        "target_posts": urls,
    }
    if tags:
        overrides["direction_tags"] = tags
    if named:
        overrides["target_communities"] = named
    business_goal = "project_distribution" if "posts" in units else "conversation_entry" if "comments" in units else "community_discovery"
    strategy = {
        "business_goal": business_goal,
        "community_scope": "closed",
        "coverage_budget": {"low": "standard", "standard": "standard", "high": "broad"}[frequency],
        "action_threshold": {"low": "high", "standard": "standard", "high": "standard"}[frequency],
        "action_budget": {"low": "minimal", "standard": "standard", "high": "active"}[frequency],
        "frequency": frequency,
        "material_refs": material_refs,
        "planning_targets": {},
    }
    normalized = {
        "duration_hours": duration,
        "direction": direction,
        "authority_profile": "direct_target",
        "frequency": frequency,
        "requested_work_types": units,
        "unit_authority": {unit: authority[unit] for unit in units},
        "authorization_receipt": text(raw.get("authorization_receipt", "explicit target assignment"), "authorization_receipt", 1, 10000),
        "mission_strategy": strategy,
        "explicit_user_overrides": overrides,
        "direct_target_mode": True,
        "target_posts": urls,
    }
    return {
        "schema": "reddit_startup_intake/v1",
        "status": "DIRECT_TARGET_ASSIGNMENT_COMPLETE",
        "answer_sha256": canonical_hash(raw),
        "normalized": normalized,
    }


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


def waiting_response(missing):
    return {
        "schema": "reddit_startup_intake/v1",
        "status": "WAITING_FOR_STARTUP_INPUT",
        "missing": missing,
        "text_fallback": {
            "channel": "DIRECT_TEXT",
            "request_user_input_repeat": False,
            "message": TEXT_FALLBACK,
        },
    }


def normalize(raw):
    if not isinstance(raw, dict):
        fail("input must be object")
    if raw.get("cancelled") is True:
        return {"schema": "reddit_startup_intake/v1", "status": "STARTUP_CANCELLED_BY_USER"}
    if raw.get("cancelled") not in (None, False):
        fail("cancelled must be boolean")
    if raw.get("direct_target_mode") is True or any(raw.get(key) is not None for key in ("target_posts", "target_post_urls", "target_refs")):
        return normalize_direct_target(raw)
    direction_value = raw.get("direction")
    if direction_value in (None, ""):
        direction_value = raw.get("account_direction")
    missing = []
    if raw.get("duration_hours", raw.get("duration")) in (None, ""):
        missing.append("duration_hours")
    if direction_value in (None, ""):
        missing.append("direction")
    if raw.get("authority_profile") in (None, ""):
        missing.append("authority_profile")
    if raw.get("frequency", raw.get("interaction_frequency")) in (None, ""):
        missing.append("frequency")
    if missing:
        return waiting_response(missing)

    duration = duration_hours(raw.get("duration_hours", raw.get("duration")))
    direction = text(direction_value, "direction", 3, 2000)
    profile_name, profile = resolve_profile(raw["authority_profile"], raw.get("custom_authority"))
    frequency = normalize_frequency(raw.get("frequency", raw.get("interaction_frequency")))
    named_communities = normalized_list(raw.get("named_communities"), "named_communities", 64, "r/")
    if any(item.lower() in EXCLUDED_COMMUNITIES for item in named_communities):
        fail("excluded community: r/saas")
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
        "frequency": frequency,
        "coverage_budget": {"low": "standard", "standard": "standard", "high": "broad"}[frequency],
        "action_threshold": {"low": "high", "standard": "standard", "high": "standard"}[frequency],
        "action_budget": {"low": "minimal", "standard": "standard", "high": "active"}[frequency],
        "material_refs": material_refs,
        "planning_targets": {},
    }
    normalized = {
        "duration_hours": duration,
        "direction": direction,
        "authority_profile": profile_name,
        "frequency": frequency,
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
    waiting = normalize({"duration_hours": 2})
    assert waiting["schema"] == "reddit_startup_intake/v1"
    assert waiting["status"] == "WAITING_FOR_STARTUP_INPUT"
    assert waiting["missing"] == ["direction", "authority_profile", "frequency"]
    assert waiting["text_fallback"] == {
        "channel": "DIRECT_TEXT",
        "request_user_input_repeat": False,
        "message": TEXT_FALLBACK,
    }
    assert normalize({"cancelled": True})["status"] == "STARTUP_CANCELLED_BY_USER"
    result = normalize({
        "duration": "2 小时",
        "direction": "个人创作与独立项目",
        "authority_profile": "全面推进",
        "frequency": "高",
    })
    assert result["status"] == "STARTUP_ANSWERS_COMPLETE"
    assert result["normalized"]["mission_strategy"]["community_scope"] == "discover"
    assert result["normalized"]["authority_profile"] == "full_progression"
    assert result["normalized"]["requested_work_types"] == list(LANE_ORDER)
    assert result["normalized"]["mission_strategy"]["material_refs"] == []
    assert result["normalized"]["frequency"] == "high"
    assert result["normalized"]["mission_strategy"]["action_budget"] == "active"
    seeded = normalize({
        "duration_hours": 4,
        "direction": "custom direction",
        "authority_profile": "参与讨论",
        "frequency": "standard",
        "named_communities": ["r/SideProject"],
    })
    assert seeded["normalized"]["authority_profile"] == "discussion_participation"
    assert seeded["normalized"]["mission_strategy"]["community_scope"] == "seeded_expandable"
    browse_only = normalize({
        "duration_hours": 4,
        "direction": "社交与社区",
        "authority_profile": "模拟浏览",
        "frequency": "low",
    })
    assert browse_only["normalized"]["authority_profile"] == "simulate_browsing"
    assert browse_only["normalized"]["requested_work_types"] == ["browsing"]
    assert browse_only["normalized"]["mission_strategy"]["action_budget"] == "minimal"
    account_direction_only = normalize({
        "duration_hours": 4,
        "account_direction": "a practical builder around personal creative tools",
        "authority_profile": "模拟浏览",
        "frequency": "low",
    })
    assert account_direction_only["normalized"]["direction"] == "a practical builder around personal creative tools"
    custom = normalize({
        "duration_hours": 2,
        "direction": "custom direction",
        "authority_profile": "comments only, standard",
        "frequency": "标准",
        "custom_authority": {
            "business_goal": "conversation_entry",
            "requested_work_types": ["browsing", "comments"],
            "unit_authority": {"browsing": "READ_ONLY", "comments": "COMMENT_AUTHORIZED"},
        },
    })
    assert custom["normalized"]["authority_profile"] == "custom"
    direct = normalize({
        "direct_target_mode": True,
        "target_posts": ["https://old.reddit.com/r/SideProject/comments/abc123/demo/"],
        "requested_work_types": ["browsing", "comments", "follow-up"],
        "duration_hours": 2,
    })
    assert direct["status"] == "DIRECT_TARGET_ASSIGNMENT_COMPLETE"
    assert direct["normalized"]["mission_strategy"]["community_scope"] == "closed"
    assert direct["normalized"]["frequency"] == "standard"
    assert direct["normalized"]["requested_work_types"] == ["browsing", "comments", "follow-up"]
    assert direct["normalized"]["explicit_user_overrides"]["target_posts"] == ["https://old.reddit.com/r/SideProject/comments/abc123/demo/"]
    incomplete_direct = normalize({"direct_target_mode": True, "target_posts": ["https://old.reddit.com/r/SideProject/comments/abc123/demo/"]})
    assert incomplete_direct["status"] == "WAITING_FOR_DIRECT_TARGET_INPUT"
    assert incomplete_direct["missing"] == ["duration_hours", "requested_work_types"]
    try:
        normalize({
            "duration_hours": 2,
            "direction": "custom direction",
            "authority_profile": "模拟浏览",
            "frequency": "标准",
            "named_communities": ["r/saas"],
        })
    except ValueError as exc:
        assert str(exc) == "excluded community: r/saas"
    else:
        raise AssertionError("excluded community was accepted")
    try:
        normalize({
            "direct_target_mode": True,
            "target_posts": ["https://old.reddit.com/r/saas/comments/abc123/demo/"],
            "requested_work_types": ["browsing"],
            "duration_hours": 2,
        })
    except ValueError as exc:
        assert str(exc) == "excluded community: r/saas"
    else:
        raise AssertionError("excluded direct target was accepted")
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
