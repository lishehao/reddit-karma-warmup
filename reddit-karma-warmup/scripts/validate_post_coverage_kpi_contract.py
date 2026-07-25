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
if (posts["native_discussion_candidate_score_min"], posts["artifact_post_candidate_score_min"]) != (76, 82):
    errors.append("mode_candidate_scores")
if (posts["discussion_survivor_sample_target"], posts["discussion_score_min"], posts["discussion_rewrite_score_min"]) != (15, 75, 65):
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
    ],
    ROOT / "references" / "posts-playbook.md": [
        "target_pool_policy=preferred_expandable",
        "resolved post-mode candidate gate",
        "ordinary discussion post does not require an artifact",
        "conditional publication KPI",
    ],
    ROOT / "references" / "community-selection-funnel.md": [
        "candidate_packet_target",
        "target_pool_policy=preferred_expandable",
        "target_pool_exact_and_closed=true",
        "native_discussion` pass requires",
    ],
    ROOT / "references" / "launcher-playbook.md": [
        "post-coverage-and-kpi.md",
        "target_pool_policy",
        "candidate_packet_target",
        "publication_target=1",
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
        "discussion_potential_score >=75",
        "artifact` 模式才保留 `>=82`",
    ], errors)

scenarios = {
    "ordinary_discussion": {
        "post_mode": "native_discussion",
        "artifact_required": False,
        "candidate_score_min": posts["native_discussion_candidate_score_min"],
        "pool_policy": posts["default_target_pool_policy"],
        "publication_target": 1,
    },
    "artifact_without_evidence": {
        "post_mode": "artifact",
        "artifact_required": True,
        "publication": "BLOCKED_NO_FABRICATION",
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
