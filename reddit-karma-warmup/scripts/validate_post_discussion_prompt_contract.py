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

require(ROOT / "SKILL.md", [
    "truthful beginner-readable community-memory angle",
    "discussion_potential_score >=80",
    "never impersonate a novice or fabricate confusion",
], errors)

require(ROOT / "references" / "proactive-playbook.md", [
    "Default Discussion-First Post Tendency",
    "beginner-readable community-memory question",
    "must not impersonate a novice",
    "low reply cost and high experience recall",
    "Discussion-potential gate",
    "at least `10` recent native question/discussion posts",
    "discussion_potential_score",
    "Recognition density",
    "Answer plurality",
    "Story affordance",
    "Low reply cost",
    "Current native evidence",
    "Novelty vs FAQ/recent posts",
    "`pass_to_draft`: `>=80`",
    "never pretend to have used a tool",
], errors)

require(ROOT / "references" / "default-operations-sop.md", [
    "truthful beginner-readable community-memory question",
    "post_discussion_gate=required_for_question_posts",
    "post_discussion_score_min=80",
], errors)

require(ROOT / "references" / "launcher-playbook.md", [
    "Every default question-post handoff carries `post_discussion_gate=required_for_question_posts`",
    "`post_discussion_score_min=80`",
], errors)

require(ROOT / "references" / "outbound-copy-gate.md", [
    "`post_copy_score` evaluates writing quality but cannot rescue a weak or generic discussion premise",
], errors)

if README.exists():
    require(README, [
        "小白也能理解",
        "discussion_potential_score >=80",
        "不能伪装新手",
    ], errors)

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "default_angle": "BEGINNER_READABLE_COMMUNITY_MEMORY",
    "identity": "NO_NOVICE_IMPERSONATION",
    "discussion_score_min": 80,
    "local_survivor_sample_min": 10,
    "reply_shape": "LOW_COST_MULTI_ANSWER_STORY_FRIENDLY",
}, ensure_ascii=False, sort_keys=True))
