#!/usr/bin/env python3
"""Validate exact targets, score gates, scan expansion, and lane-local voting."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


required = {
    "SKILL.md": [
        "exact target/cap/read floor",
        "incidental voting on already-read candidates",
        "explicit pure-browse missions",
        "自然浏览/投票：随以上执行台读取内容时完成",
    ],
    "references/default-operations-sop.md": [
        "Target-Driven Scan Loop",
        "action_target",
        "action_cap",
        "qualified_read_floor",
        "Fewer actions are not an acceptable convenience outcome",
        "slot_target_remaining",
        "primary completion condition",
        "Reaching the read floor with too few actions means expand, not finish",
        "Natural Incidental Voting",
        "broad `开始/运营`: comments + posts + follow-up",
        "browsing: only when the user explicitly requests",
        "incidental_voting=already_read_content_only",
        "post_default_angle=beginner-common-mistake",
    ],
    "references/proactive-playbook.md": [
        "Comment Candidate Gate",
        "post_candidate_score >=82",
        "The comment target is the slot's primary completion condition",
        "The post target is an execution objective",
        "no vote target",
        "already qualified-read post",
        "Default Conservative Post Tendency",
        "community-memory prompt",
        "never pretend to have used a tool",
        "search the subreddit for the exact topic and close variants",
        "assess up to `100` reference rows",
        "deep-preflight the best `8-15` communities",
        "For a one-post mission, verified publication is normal completion",
    ],
    "references/community-selection-funnel.md": [
        "Stage A: Distributor Reference Sweep",
        "Stage C: Post Lane Deep Search",
        "post_selection_timebox=20-30m",
        "reference_rows_assessed_target=up_to_100",
        "live_deep_preflight_target=8-15",
        "Prefer the highest passing candidate",
        "Do not report the mission complete because 20-30 minutes elapsed",
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
        "incidental vote",
        "incidental_vote_count",
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
    "references/browse-vote-playbook.md": [
        "Continue until the target is reached or the read/time budget is exhausted",
    ],
    "SKILL.md": [
        "vote_owner",
    ],
    "references/default-operations-sop.md": [
        "read budget is exhausted",
        "vote_owner",
        "comments + posts + follow-up + browsing",
    ],
    "references/proactive-playbook.md": [
        "vote_owner",
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
        "votes": "LANE_LOCAL_INCIDENTAL_PLUS_EXPLICIT_BROWSE",
    },
}, ensure_ascii=False, sort_keys=True))
