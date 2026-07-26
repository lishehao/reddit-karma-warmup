#!/usr/bin/env python3
"""Validate the built-in Web Search evidence protocol for Reddit text lanes."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "references"


def read(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"missing {path}")
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return " ".join(read(path).split())


def require_fields(actual: list[str], expected: tuple[str, ...], label: str) -> None:
    missing = [field for field in expected if field not in actual]
    assert not missing, f"{label}: missing {missing}"


def research_gate(
    *,
    lane: str,
    brief: bool,
    plan: bool,
    synthesis: bool,
    exact_item_query: bool = True,
    substantive: bool = False,
    objection_query: bool = True,
    search_result_claimed_as_permission: bool = False,
    no_result: bool = False,
) -> str:
    """Executable model of the documented pre-Chrome research gates."""
    if search_result_claimed_as_permission:
        return "INVALID_REDDIT_PERMISSION_EVIDENCE"
    if not (brief and plan):
        return "BLOCK_BEFORE_QUERIES"
    if lane == "comments" and not synthesis:
        return "BLOCK_BEFORE_CHROME"
    if lane == "posts" and not synthesis:
        return "BLOCK_BEFORE_CHROME_FINALISTS"
    if lane == "comments" and not exact_item_query:
        return "BLOCK_BEFORE_DRAFT"
    if lane == "comments" and substantive and not objection_query:
        return "BLOCK_BEFORE_DRAFT"
    if no_result:
        return "VALID_DISCOVERY_EFFORT_NOT_ACTION_BLOCKER"
    return "PROCEED_TO_CHROME_LIVE_GATE"


def main() -> None:
    defaults = json.loads(read(REF / "operation-defaults.json"))
    web = defaults["web_search"]
    brief = web["research_brief"]
    plan = web["query_plan"]
    synthesis = web["evidence_synthesis"]
    comments = web["comments"]
    posts = web["posts"]

    assert web["tool_requirement"] == "BUILT_IN_WEB_SEARCH"
    assert web["batch_independent_queries_when_supported"] is True
    assert web["results_are_discovery_and_fact_evidence_not_reddit_permission"] is True
    assert web["required_pipeline"] == [
        "research_brief",
        "query_plan",
        "evidence_synthesis",
        "chrome_live_gate",
    ]

    require_fields(
        brief["required_fields"],
        (
            "research_brief_id",
            "lane",
            "decision_question",
            "target_surface",
            "audience_or_context",
            "candidate_angle",
            "intended_claims_or_questions",
            "unknowns_to_resolve",
            "research_questions",
            "publish_risk_hypothesis",
            "stop_condition",
        ),
        "research_brief.required_fields",
    )
    assert brief["max_bullets"] <= 6
    require_fields(
        plan["required_fields"],
        (
            "research_brief_id",
            "query_plan_id",
            "query_family",
            "research_question_id",
            "candidate_or_claim_use",
        ),
        "query_plan.required_fields",
    )
    assert plan["require_family_labels"] is True
    assert plan["require_distinct_question_per_query"] is True
    assert plan["duplicate_wording_policy"] == "DO_NOT_COUNT"
    assert plan["comments_min_distinct_families"] >= 4
    assert plan["posts_min_distinct_families"] == 3
    require_fields(
        synthesis["required_fields"],
        (
            "research_brief_id",
            "evidence_synthesis_id",
            "linked_web_search_item_ids",
            "usable_findings",
            "counter_evidence_or_objections",
            "saturation_or_duplicate_risk",
            "unsupported_or_forbidden_claims",
            "candidate_decision",
            "draft_constraints",
            "chrome_live_gate_targets",
        ),
        "evidence_synthesis.required_fields",
    )
    assert synthesis["must_have_counterevidence"] is True
    assert synthesis["must_have_draft_constraints"] is True
    assert synthesis["publish_without_synthesis_policy"] == "BLOCK_DRAFT"

    assert comments["brief_scope"] == "cluster_window"
    assert comments["per_comment_exact_query_updates_synthesis"] is True
    assert comments["cluster_discovery_query_min"] >= 4
    assert comments["cluster_discovery_query_min"] <= comments["cluster_discovery_query_target"]
    assert comments["cluster_discovery_query_target"] <= comments["cluster_discovery_query_cap"]
    assert comments["per_comment_exact_query_min"] >= 1
    assert comments["substantive_item_objection_query_min"] >= 1
    assert set(comments["required_window_query_families"]) == {
        "community_topic",
        "recent_discussion",
        "contradiction_or_objection",
        "language_or_event_signal",
    }
    assert comments["time_sensitive_claim_source_min"] >= 2

    assert posts["brief_scope"] == "candidate_packet"
    assert posts["query_plan_required_before_pack"] is True
    assert posts["synthesis_required_before_chrome_finalists"] is True
    assert posts["query_pack_min"] >= 12
    assert posts["query_pack_min"] <= posts["query_pack_target"] <= posts["query_pack_cap"]
    assert posts["finalist_delta_query_min"] >= 1
    base_minimums = posts["base_query_family_minimums"]
    assert set(base_minimums) == {
        "community_topic_and_recent_discussion",
        "premise_and_close_variants",
        "duplicate_and_faq_risk",
    }
    assert all(value >= 3 for value in base_minimums.values())
    assert sum(base_minimums.values()) <= posts["query_pack_min"]
    assert posts["external_fact_query_min_when_claimed"] >= 2
    assert posts["external_fact_family_policy"] == "REQUIRED_ONLY_WHEN_EXTERNAL_FACT_CLAIMED"
    assert posts["time_sensitive_claim_source_min"] >= 2

    required = {
        "SKILL.md": [
            "WEB RESEARCH: brief -> plan -> synthesis",
            "research_brief -> query_plan -> evidence_synthesis",
            "Chrome remains the final live authority",
        ],
        "web-search-preflight.md": [
            "Mandatory Pipeline",
            "research_brief -> query_plan -> purpose-labelled Web Search -> evidence_synthesis -> Chrome live gate",
            "Do not draft from snippets",
            "Before **every individual comment**",
            "substantive_item_objection_query_min",
            "synthesis_required_before_chrome_finalists",
            "Write the post evidence synthesis before Chrome narrowing",
            "never proves live Reddit permission",
            "Do not use Web Search as a workaround for a broken Chrome control path",
        ],
        "comments-playbook.md": [
            "comment-window built-in Web Search pipeline",
            "research_brief_id",
            "query_plan_id",
            "evidence_synthesis_id",
            "unsupported_or_forbidden_claims",
            "objection/duplicate-risk query",
        ],
        "posts-playbook.md": [
            "`evidence_synthesis` before Chrome finalist narrowing",
            "finalist-delta Web Search query",
            "draft_constraints",
            "unsupported factual claim",
            "query count alone does not unlock drafting",
        ],
        "community-selection-funnel.md": [
            "Create the post `research_brief` and `query_plan`",
            "built-in Web Search post research pipeline",
            "write `evidence_synthesis` before selecting Chrome finalists",
            "`research_brief_id`, `query_plan_id`, `evidence_synthesis_id`",
            "targeted finalist delta query",
            "Web Search results do not replace",
        ],
        "publish-consistency.md": [
            "research_brief_id",
            "query_plan_id",
            "evidence_synthesis_id",
            "unsupported claim",
            "targeted delta query",
        ],
        "chrome-recovery-edge-cases.md": [
            "as a Chrome recovery substitute",
            "Normal pre-action Web Search research remains separate",
        ],
        "chrome-network-recovery.md": [
            "separate mandatory built-in Web Search research stage",
        ],
    }
    for name, phrases in required.items():
        path = ROOT / name if name == "SKILL.md" else REF / name
        body = normalized(path)
        for phrase in phrases:
            assert " ".join(phrase.split()) in body, f"{name}: missing {phrase!r}"

    search_reference = read(REF / "web-search-preflight.md")
    assert not re.search(r"\b(?:default|target|cap)\s+\d", search_reference, re.IGNORECASE)

    scenarios = {
        "comment_without_research_brief": research_gate(
            lane="comments", brief=False, plan=True, synthesis=True
        ),
        "post_query_count_without_synthesis": research_gate(
            lane="posts", brief=True, plan=True, synthesis=False
        ),
        "substantive_comment_without_objection": research_gate(
            lane="comments", brief=True, plan=True, synthesis=True,
            substantive=True, objection_query=False,
        ),
        "unsupported_claim_after_synthesis": "REMOVE_OR_REFRAME",
        "search_result_as_permission": research_gate(
            lane="posts", brief=True, plan=True, synthesis=True,
            search_result_claimed_as_permission=True,
        ),
        "no_result_query": research_gate(
            lane="comments", brief=True, plan=True, synthesis=True, no_result=True
        ),
        "material_live_finalist_change": "RUN_DELTA_QUERY_AND_UPDATE_SYNTHESIS",
    }
    assert scenarios == {
        "comment_without_research_brief": "BLOCK_BEFORE_QUERIES",
        "post_query_count_without_synthesis": "BLOCK_BEFORE_CHROME_FINALISTS",
        "substantive_comment_without_objection": "BLOCK_BEFORE_DRAFT",
        "unsupported_claim_after_synthesis": "REMOVE_OR_REFRAME",
        "search_result_as_permission": "INVALID_REDDIT_PERMISSION_EVIDENCE",
        "no_result_query": "VALID_DISCOVERY_EFFORT_NOT_ACTION_BLOCKER",
        "material_live_finalist_change": "RUN_DELTA_QUERY_AND_UPDATE_SYNTHESIS",
    }

    print(json.dumps({
        "status": "PASS",
        "protocol": "research_brief_to_query_plan_to_evidence_synthesis_to_chrome_live_gate",
        "comment_window_query_range": [
            comments["cluster_discovery_query_min"],
            comments["cluster_discovery_query_cap"],
        ],
        "post_query_range": [posts["query_pack_min"], posts["query_pack_cap"]],
        "scenarios": scenarios,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
