#!/usr/bin/env python3
"""Validate mandatory built-in Web Search preflight for Reddit text lanes."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "references"


def read(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"missing {path}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    defaults = json.loads(read(REF / "operation-defaults.json"))
    web = defaults["web_search"]
    assert web["tool_requirement"] == "BUILT_IN_WEB_SEARCH"
    assert web["required_pipeline"] == [
        "research_brief",
        "query_plan",
        "evidence_synthesis",
        "chrome_live_gate",
    ]
    assert {"decision_question", "unknowns_to_resolve", "publish_risk_hypothesis"} <= set(
        web["research_brief"]["required_fields"]
    )
    assert web["query_plan"]["require_family_labels"] is True
    assert web["query_plan"]["require_distinct_question_per_query"] is True
    assert web["query_plan"]["duplicate_wording_policy"] == "DO_NOT_COUNT"
    assert {"counter_evidence_or_objections", "unsupported_or_forbidden_claims", "draft_constraints"} <= set(
        web["evidence_synthesis"]["required_fields"]
    )
    assert web["evidence_synthesis"]["must_have_counterevidence"] is True
    assert web["evidence_synthesis"]["must_have_draft_constraints"] is True
    assert web["evidence_synthesis"]["publish_without_synthesis_policy"] == "BLOCK_DRAFT"
    assert web["comments"]["cluster_discovery_query_min"] >= 4
    assert web["comments"]["cluster_discovery_query_cap"] >= web["comments"]["cluster_discovery_query_min"]
    assert web["comments"]["per_comment_exact_query_min"] >= 1
    assert web["posts"]["query_pack_min"] >= 12
    assert web["posts"]["query_pack_target"] >= web["posts"]["query_pack_min"]
    assert web["posts"]["query_pack_cap"] >= web["posts"]["query_pack_target"]
    assert len(web["posts"]["required_query_families"]) >= 4

    required = {
        "SKILL.md": ["research_brief -> query_plan -> evidence_synthesis", "Chrome remains the final live authority"],
        "comments-playbook.md": ["comment-window built-in Web Search pipeline", "evidence_synthesis_id"],
        "posts-playbook.md": ["research_brief", "evidence_synthesis", "query count alone does not unlock drafting"],
        "community-selection-funnel.md": ["Web Search post query pack", "query_pack_min", "Web Search results do not replace"],
        "publish-consistency.md": ["web_search_item_id", "decision-ready `evidence_synthesis`"],
        "web-search-preflight.md": ["Mandatory pipeline", "Before **every individual comment**", "default 12", "Query count alone never satisfies preflight"],
        "chrome-recovery-edge-cases.md": ["as a Chrome recovery substitute", "Normal pre-action Web Search research remains separate"],
        "chrome-network-recovery.md": ["separate mandatory built-in Web Search research stage"],
    }
    for name, phrases in required.items():
        body = " ".join(read(ROOT / name if name == "SKILL.md" else REF / name).split())
        for phrase in phrases:
            assert " ".join(phrase.split()) in body, f"{name}: missing {phrase!r}"

    scenarios = {
        "query_count_satisfied_without_research_brief": "BLOCK_DRAFT",
        "wording_duplicates_inflated_query_count": "DO_NOT_COUNT",
        "no_counterevidence_or_objection": "BLOCK_DRAFT",
        "synthesis_missing_draft_constraints": "BLOCK_DRAFT",
        "web_result_claims_reddit_permission": "CHROME_LIVE_GATE_REQUIRED",
    }

    print(json.dumps({
        "status": "PASS",
        "comment_window_query_range": [
            web["comments"]["cluster_discovery_query_min"],
            web["comments"]["cluster_discovery_query_cap"],
        ],
        "post_query_range": [web["posts"]["query_pack_min"], web["posts"]["query_pack_cap"]],
        "per_comment_exact_query_min": web["comments"]["per_comment_exact_query_min"],
        "scenarios": scenarios,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
