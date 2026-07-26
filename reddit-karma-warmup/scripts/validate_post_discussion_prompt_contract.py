#!/usr/bin/env python3
"""Validate truthful beginner-readable, high-discussion post prompting."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"


def require(path: Path, needles: list[str], errors: list[str]) -> None:
    body = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{path.name}:{needle}")


errors: list[str] = []
defaults = json.loads((ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8"))
if defaults["posts"]["selection_priority"] != "COMPLIANCE_FIRST":
    errors.append("selection_priority")
if defaults["posts"]["content_quality_role"] != "SECONDARY_MINIMUM_AND_TIEBREAK":
    errors.append("content_quality_role")
if defaults["posts"]["discussion_score_min"] != 50:
    errors.append("discussion_score_min")
if defaults["posts"]["discussion_survivor_sample_target"] != 15:
    errors.append("discussion_survivor_sample_target")
if defaults["posts"]["discussion_rewrite_score_min"] != 40:
    errors.append("discussion_rewrite_score_min")

require(ROOT / "SKILL.md", [
    "posts-playbook.md",
], errors)
require(ROOT / "references" / "posts-playbook.md", [
    "Discussion-First Default",
    "truthful beginner-readable community-memory question",
    "must not impersonate a novice",
    "posts.discussion_survivor_sample_target",
    "Recognition density",
    "Answer plurality",
    "Story affordance",
    "Low reply cost",
    "Current native evidence",
    "Novelty vs FAQ/recent posts",
    "After hard compliance passes, draft at `posts.discussion_score_min`",
    "minimum anti-spam/fit floor",
], errors)
require(ROOT / "references" / "launcher-playbook.md", [
    "Every default question-post handoff carries the resolved compliance-first content floor",
], errors)
require(ROOT / "references" / "outbound-copy-gate.md", [
    "`post_copy_score` evaluates writing quality but cannot rescue a weak or generic discussion premise",
], errors)
if README.exists():
    require(README, [
        "默认发帖是 `native_discussion`",
    "discussion_potential_score >=50",
    "只在版规合规后使用",
        "不能伪装新手",
    ], errors)

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "default_angle": "TRUTHFUL_BEGINNER_READABLE_COMMUNITY_MEMORY",
    "discussion_score_min": 50,
    "selection_priority": "COMPLIANCE_FIRST",
    "identity": "NO_NOVICE_IMPERSONATION",
}, ensure_ascii=False, sort_keys=True))
