#!/usr/bin/env python3
"""Validate exact targets, simple score gates, scan expansion, and vote ownership."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


required = {
    "SKILL.md": [
        "vote_owner=true",
        "exact target/cap/read floor",
    ],
    "references/default-operations-sop.md": [
        "Target-Driven Scan Loop",
        "action_target",
        "action_cap",
        "qualified_read_floor",
        "Fewer actions are not an acceptable convenience outcome",
        "Exactly one lane in a run owns vote mutations",
    ],
    "references/proactive-playbook.md": [
        "Comment Candidate Gate",
        "post_candidate_score >=82",
        "The comment target is an execution objective",
        "The post target is an execution objective",
        "vote_owner=true",
    ],
    "references/browse-vote-playbook.md": [
        "Initial qualified-read floor",
        "combined-vote target as an active completion objective",
        "Choose `upvote` only at `>=82`",
        "Choose `downvote` only at `>=92`",
    ],
    "references/followup-playbook.md": [
        "Act >=75",
        "no artificial reply quota",
        "every passing `Act`",
    ],
    "references/outbound-copy-gate.md": [
        "comment_fun_score",
        "post_copy_score >=80",
    ],
}

errors = []
for relative, needles in required.items():
    body = read(relative)
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{relative}:{needle}")

forbidden = {
    "references/default-operations-sop.md": [
        "read budget is exhausted",
    ],
    "references/browse-vote-playbook.md": [
        "Continue until the target is reached or the read/time budget is exhausted",
    ],
}
for relative, needles in forbidden.items():
    body = read(relative)
    for needle in needles:
        if needle in body:
            errors.append(f"forbidden:{relative}:{needle}")

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "contract": {
        "counts": "EXACT_TARGET_AND_CAP",
        "discovery": "EXPAND_UNTIL_TARGET_OR_DEADLINE",
        "quality": "NEVER_LOWER_THRESHOLD",
        "votes": "ONE_MISSION_OWNER_INDEPENDENT_SCORE",
    },
}, ensure_ascii=False, sort_keys=True))
