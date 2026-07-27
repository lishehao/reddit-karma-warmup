#!/usr/bin/env python3
"""Validate policy carried forward into the production single-owner topology."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = ROOT / "references" / "operation-defaults.json"
SKILL = ROOT / "SKILL.md"
ATOMIC = ROOT / "references" / "chrome-atomic-command-runtime.md"
RECOVERY = ROOT / "references" / "chrome-network-recovery.md"
AUDIT = ROOT / "references" / "community-audit-pool.md"
OWNERSHIP = ROOT / "references" / "lane-action-ownership.md"
README = ROOT.parent / "README.md"


def normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def main():
    defaults = json.loads(DEFAULTS.read_text(encoding="utf-8"))
    topology = defaults["execution_topology"]
    runtime = defaults["single_owner_runtime"]
    decision_round = defaults["decision_round"]
    liveness = defaults["single_owner_task_liveness"]
    web = defaults["web_search"]
    posts = defaults["posts"]
    votes = defaults["votes"]
    chrome = defaults["chrome_command_runtime"]
    scheduler = defaults["scheduler"]
    assert topology["default"] == "single_owner_v1"
    assert topology["cross_task_chrome_owner_count"] == 1
    assert topology["public_read_tab_cap_after_canary"] == 2
    assert topology["chrome_boundary_parallelism"] == 1
    assert runtime["schema"] == "reddit_single_owner_queue/v2"
    assert runtime["heartbeat_interval_minutes"] == 20
    assert runtime["yielded_unit_blocks_later_units"] is True
    assert runtime["unknown_mutation_policy"] == "FREEZE_EXACT_ACTION_KEY_NO_RETRY"
    assert runtime["hotplug_actions"] == ["ADD", "PAUSE", "REMOVE", "RESUME", "AUTHORITY_CHANGE", "VOTE_POLICY_CHANGE"]
    assert liveness["require_present_unarchived"] is True
    assert liveness["automatic_replacement_creation_cap_per_mission"] == 0
    assert liveness["not_loaded_policy"] == "REQUIRE_USER_REFRESH_NO_REPLACEMENT"
    assert defaults["model_runtime"]["fallback_chain"][0] == {"model": "gpt-5.6-luna", "reasoning_effort": "high"}
    assert web["tool_requirement"] == "BUILT_IN_WEB_SEARCH"
    assert web["comments"]["cluster_discovery_query_min"] >= 4
    assert web["posts"]["query_pack_min"] >= 12
    assert posts["selection_priority"] == "COMPLIANCE_FIRST"
    assert posts["content_quality_role"] == "SECONDARY_MINIMUM_AND_TIEBREAK"
    assert posts["publication_kpi"] == "CONDITIONAL_ONE_VERIFIED_POST"
    assert votes["allowed_lanes"] == ["browsing"]
    assert votes["non_browsing_policy"] == "DISABLED_BY_LANE"
    assert chrome["outer_timeout_ms"] >= 120000
    assert chrome["blocking_page_commands_per_cell"] == 1
    assert scheduler["heartbeat_trigger_tolerance_seconds"] == 300
    assert decision_round["heartbeat_interval_minutes"] == 20
    assert decision_round["heartbeat_trigger_tolerance_seconds"] == 300
    assert decision_round["max_chrome_units_per_wake"] == 1
    assert decision_round["max_outward_actions_per_wake"] == 1
    assert decision_round["outcomes"] == ["RUN", "WATCH", "SKIP", "DEFER"]
    assert decision_round["default_recheck_minutes"] == {
        "browsing": 40, "comments": 60, "posts": 180,
        "follow-up": 90, "presence": 1440,
    }

    skill = normalized(SKILL)
    atomic = normalized(ATOMIC)
    recovery = normalized(RECOVERY)
    audit = normalized(AUDIT)
    ownership = normalized(OWNERSHIP)
    readme = normalized(README) if README.is_file() else ""
    for phrase in (
        "hard compliance -> truthful minimum content floor -> secondary ranking",
        "do not duplicate an uncertain Reddit mutation",
        "research_brief -> query_plan -> evidence_synthesis -> Chrome live gate",
        "community-action-routing-overrides.md",
        "organization-community-denylist.md",
        "subreddit-profile-index.csv",
        "Timing within the configured ±5-minute tolerance is ordinary",
        "One decision round is not a mandatory five-unit sweep",
        "RUN`, `WATCH`, `SKIP`, or `DEFER`",
    ):
        assert phrase in skill, phrase
    for phrase in (
        "One Owner, One Primary Tab", "browser_boundary=OPEN", "one primary agent-owned Reddit tab",
        "Never implement timeout with `Promise.race()`", "120000", "metadata-only cell",
    ):
        assert phrase in atomic, phrase
    for phrase in (
        "single `Reddit 运营台`", "chrome_content_channel_timeout", "never starts a second Chrome owner",
        "same mission, Heartbeat, queue cursor", "`429_ROUND_PAUSE` applies to the active unit",
    ):
        assert phrase in recovery, phrase
    for phrase in (
        "one `Reddit 运营台`", "GET-only", "never publishes", "never replaces live Chrome checks",
    ):
        assert phrase in audit, phrase
    for phrase in (
        "table defines unit authority; it does not create five separate tasks",
        "vote_policy=DISABLED_BY_LANE", "Only a browsing unit with both `VOTE_AUTHORIZED`",
    ):
        assert phrase in ownership, phrase
    if README.is_file():
        for phrase in (
            "one persistent, user-visible `Reddit 运营台`", "direct GitHub `main` publication",
            "All five units can be added, paused, removed, resumed", "±5 minutes",
        ):
            assert phrase in readme, phrase
    print(json.dumps({
        "status": "PASS", "chrome_calls": 0,
        "web_research_policy": "BUILT_IN_WEB_SEARCH",
        "post_policy": "COMPLIANCE_FIRST",
        "vote_policy": "BROWSING_ONLY",
        "heartbeat_tolerance_seconds": 300,
        "decision_round": "ONE_PACKET_PER_WAKE",
        "single_owner_chrome_boundaries": True,
        "root_readme": "PRESENT" if README.is_file() else "OPTIONAL_ABSENT",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
