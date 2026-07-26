#!/usr/bin/env python3
"""Validate broad post discovery, conditional publication, and mode-specific trust gates."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"
DEFAULTS = json.loads((ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8"))


def require(path: Path, needles: list[str], errors: list[str]) -> None:
    body = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{path.name}:{needle}")


errors: list[str] = []
posts = DEFAULTS["posts"]
selection = DEFAULTS["community_selection"]

expected_posts = {
    "low": (80, 8),
    "standard": (150, 14),
    "high": (220, 18),
}
for intensity, expected in expected_posts.items():
    row = posts[intensity]
    actual = (row["reference_sweep_target"], row["live_deep_read_target"])
    if actual != expected:
        errors.append(f"post_coverage_{intensity}:{actual}")

if posts["default_post_mode"] != "native_discussion":
    errors.append("default_post_mode")
if posts["default_target_pool_policy"] != "preferred_expandable":
    errors.append("default_target_pool_policy")
if posts["exact_closed_pool_user_only"] is not True:
    errors.append("exact_closed_pool_user_only")
if posts["publication_kpi"] != "CONDITIONAL_ONE_VERIFIED_POST":
    errors.append("publication_kpi")
if (posts["candidate_packet_target"], posts["candidate_packet_min_before_blocked"]) != (3, 3):
    errors.append("candidate_packet_target")
if posts["selection_priority"] != "COMPLIANCE_FIRST":
    errors.append("selection_priority")
if posts["content_quality_role"] != "SECONDARY_MINIMUM_AND_TIEBREAK":
    errors.append("content_quality_role")
if (posts["native_discussion_content_score_floor"], posts["artifact_content_score_floor"]) != (50, 50):
    errors.append("mode_content_floors")
if "native_discussion_candidate_score_min" in posts or "artifact_post_candidate_score_min" in posts:
    errors.append("obsolete_mode_candidate_scores")
if "post_candidate_score_min" in posts:
    errors.append("obsolete_generic_post_candidate_score")
if (posts["discussion_survivor_sample_target"], posts["discussion_score_min"], posts["discussion_rewrite_score_min"]) != (15, 50, 40):
    errors.append("discussion_coverage_scores")
if selection["post_shortlist_limit"] != 30:
    errors.append("post_shortlist_limit")
if selection["post_live_preflight_community_range"] != [12, 20]:
    errors.append("post_live_preflight_range")
if selection["post_initial_candidate_range"] != [20, 30]:
    errors.append("post_initial_candidate_range")

required = {
    ROOT / "SKILL.md": ["post-coverage-and-kpi.md"],
    ROOT / "references" / "post-coverage-and-kpi.md": [
        "CONDITIONAL_ONE_VERIFIED_POST",
        "preferred_expandable",
        "target_pool_exact_and_closed=true",
        "closed_pool_exhausted",
        "native_discussion",
        "artifact",
        "candidate_packet_target",
        "0/1",
        "Hard compliance",
        "Minimum content floor",
        "Secondary ranking",
        "not rejected merely for missing an arbitrary high aggregate score",
    ],
    ROOT / "references" / "posts-playbook.md": [
        "target_pool_policy=preferred_expandable",
        "Resolve hard compliance first",
        "minimum content floor",
        "ordinary discussion post does not require an artifact",
        "conditional publication KPI",
    ],
    ROOT / "references" / "outbound-copy-gate.md": [
        "`post_copy_score` is a revision cue, not an eligibility gate",
        "does not reach an arbitrary writing-score threshold",
    ],
    ROOT / "references" / "community-selection-funnel.md": [
        "candidate_packet_target",
        "target_pool_policy=preferred_expandable",
        "target_pool_exact_and_closed=true",
        "Compliance Gate Before Ranking",
        "No 100-point aggregate candidate score is a publication gate",
    ],
    ROOT / "references" / "launcher-playbook.md": [
        "post-coverage-and-kpi.md",
        "target_pool_policy",
        "candidate_packet_target",
        "publication_target=1",
        "post_selection_priority=COMPLIANCE_FIRST",
    ],
    ROOT / "references" / "default-operations-sop.md": [
        "post_mode=native_discussion",
        "target_pool_policy=preferred_expandable",
        "candidate packets",
        "publication_target",
    ],
    ROOT / "references" / "lane-state-checkpoint.md": [
        "publication_target + publication_cap + publication_status",
        "candidate_packet_target + candidate_packet_verified + candidate_packet_rejections",
        "candidate_hard_compliance + candidate_content_floor + candidate_secondary_rank_score",
    ],
}
for path, needles in required.items():
    require(path, needles, errors)

if README.exists():
    require(README, [
        "标准发帖任务评估最多 150 个匹配社区",
        "preferred_expandable",
        "条件性 1 篇",
        "3 个候选包",
        "候选先过当天版规",
        "内容质量只用于该底线及合规候选间的排序",
        "discussion_potential_score >=50",
    ], errors)

if "Publish only at `post_copy_score >=80`" in (ROOT / "references" / "outbound-copy-gate.md").read_text(encoding="utf-8"):
    errors.append("post_copy_score_hard_gate")

scenarios = {
    "ordinary_discussion": {
        "post_mode": "native_discussion",
        "artifact_required": False,
        "selection_priority": posts["selection_priority"],
        "content_floor": posts["native_discussion_content_score_floor"],
        "pool_policy": posts["default_target_pool_policy"],
        "publication_target": 1,
    },
    "artifact_without_evidence": {
        "post_mode": "artifact",
        "artifact_required": True,
        "publication": "BLOCKED_NO_FABRICATION",
    },
    "high_rank_but_noncompliant": {
        "hard_compliance": "FAIL",
        "publication": "REJECT_BEFORE_RANKING",
    },
    "compliant_but_not_hype_optimized": {
        "hard_compliance": "PASS",
        "content_floor": "PASS",
        "publication": "ELIGIBLE_NO_HIGH_AGGREGATE_GATE",
    },
    "coverage_without_eligible_post": {
        "candidate_packets": posts["candidate_packet_min_before_blocked"],
        "action_remaining": 1,
        "publication_status": "blocked_after_coverage",
    },
    "explicit_closed_pool": {
        "expand": False,
        "result": "closed_pool_exhausted_0_OF_1",
    },
}

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "scenarios": scenarios,
    "publication": "CONDITIONAL_ONE_VERIFIED_POST",
    "pool": "PREFERRED_EXPANDABLE_UNLESS_USER_EXPLICITLY_CLOSES",
}, ensure_ascii=False, sort_keys=True))
