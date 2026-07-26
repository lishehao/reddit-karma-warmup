#!/usr/bin/env python3
"""Validate that post rules are hard gates and quality ranks only passing candidates."""

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

if posts["selection_priority"] != "COMPLIANCE_FIRST":
    errors.append("selection_priority")
if posts["content_quality_role"] != "SECONDARY_MINIMUM_AND_TIEBREAK":
    errors.append("content_quality_role")
if posts["rules_eligibility_score_min"] != 20:
    errors.append("rules_eligibility_score_min")
if (posts["native_discussion_content_score_floor"], posts["artifact_content_score_floor"]) != (50, 50):
    errors.append("content_score_floors")
if "native_discussion_candidate_score_min" in posts or "artifact_post_candidate_score_min" in posts:
    errors.append("obsolete_high_score_gate")

require(ROOT / "SKILL.md", [
    "evaluate hard compliance before content quality",
    "secondary tiebreaker",
], errors)
require(ROOT / "references" / "post-coverage-and-kpi.md", [
    "Hard compliance",
    "Minimum content floor",
    "Secondary ranking",
    "immediate `retarget`",
    "not rejected merely for missing an arbitrary high aggregate score",
], errors)
require(ROOT / "references" / "community-selection-funnel.md", [
    "Compliance Gate Before Ranking",
    "A failure is `retarget`, not a lower score",
    "No 100-point aggregate candidate score is a publication gate",
], errors)
require(ROOT / "references" / "posts-playbook.md", [
    "Resolve hard compliance first",
    "minimum anti-spam/fit floor",
], errors)
require(ROOT / "references" / "launcher-playbook.md", [
    "post_selection_priority=COMPLIANCE_FIRST",
    "post_content_quality_role=SECONDARY_MINIMUM_AND_TIEBREAK",
], errors)
require(ROOT / "references" / "lane-state-checkpoint.md", [
    "candidate_hard_compliance + candidate_content_floor + candidate_secondary_rank_score",
], errors)
if README.exists():
    require(README, [
        "候选先过当天版规",
        "内容质量只用于该底线及合规候选间的排序",
        "它只在版规合规后使用",
    ], errors)

scenarios = {
    "excellent_copy_rule_failure": "RETARGET_BEFORE_RANKING",
    "compliant_native_post_without_high_hype_score": "ELIGIBLE_AFTER_CONTENT_FLOOR",
    "compliant_duplicate_or_spam": "REWRITE_OR_RETARGET",
    "artifact_without_direct_evidence": "BLOCKED_NO_FABRICATION",
}

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "selection_priority": posts["selection_priority"],
    "quality_role": posts["content_quality_role"],
    "scenarios": scenarios,
}, ensure_ascii=False, sort_keys=True))
