#!/usr/bin/env python3
"""Validate that only the browsing lane can own Reddit vote mutations."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


errors: list[str] = []
defaults = json.loads(read("references/operation-defaults.json"))
votes = defaults["votes"]

if votes.get("allowed_lanes") != ["browsing"]:
    errors.append("allowed_lanes_must_be_browsing_only")
if votes.get("non_browsing_policy") != "DISABLED_BY_LANE":
    errors.append("non_browsing_policy")
if votes.get("non_browsing_cap") != 0:
    errors.append("non_browsing_cap")

required = {
    "SKILL.md": [
        "references/lane-action-ownership.md",
        "Only `Reddit 浏览台` may vote",
        "vote_policy=DISABLED_BY_LANE",
    ],
    "references/lane-action-ownership.md": [
        "This is the single authority",
        "| `comments` / `Reddit 评论台`",
        "| `posts` / `Reddit 发帖台`",
        "| `follow-up` / `Reddit 跟进台`",
        "| `browsing` / `Reddit 浏览台`",
        "vote_policy=DISABLED_BY_LANE",
        "vote_policy=BROWSING_ONLY",
        "preserve them as historical evidence only",
    ],
    "references/launcher-playbook.md": [
        "vote_policy=DISABLED_BY_LANE",
        "vote_cap=0",
        "browse_vote_playbook=NOT_LOADED",
        "vote_policy=BROWSING_ONLY",
    ],
    "references/browse-vote-playbook.md": [
        "Load only in `Reddit 浏览台`",
        "must not load this file or use any vote control",
    ],
    "references/comments-playbook.md": [
        "vote_policy=DISABLED_BY_LANE",
        "Vote controls are out of scope even when visible",
        "Do not include Upvote/Downvote counters",
    ],
    "references/posts-playbook.md": [
        "vote_policy=DISABLED_BY_LANE",
        "Vote controls are out of scope even when visible",
        "Do not include Upvote/Downvote counters",
    ],
    "references/followup-playbook.md": [
        "vote_policy=DISABLED_BY_LANE",
        "Vote controls are out of scope even on another user's reply",
        "Do not include Upvote/Downvote counters",
    ],
    "references/lane-state-checkpoint.md": [
        "preserves legacy vote counters only as history",
        "zeros them for the new mission revision",
    ],
}
for relative, needles in required.items():
    body = read(relative)
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{relative}:{needle}")

for relative in (
    "references/comments-playbook.md",
    "references/posts-playbook.md",
    "references/followup-playbook.md",
):
    body = read(relative)
    if "vote assessment" in body.lower():
        errors.append(f"off_lane_vote_assessment:{relative}")

browse = read("references/browse-vote-playbook.md")
if "lane_round" in browse:
    errors.append("legacy_lane_round_vote_mode")

scenarios = {
    "comment_candidate_visible_vote": "IGNORE_CONTROL",
    "post_research_visible_vote": "IGNORE_CONTROL",
    "followup_inbound_visible_vote": "IGNORE_CONTROL",
    "explicit_vote_with_comment_request": "SPLIT_TO_BROWSING",
    "explicit_vote_inside_comment_lane": "NAME_BROWSING_AS_OWNER",
    "broad_start_without_vote_request": "NO_BROWSING_LANE",
    "legacy_non_browsing_checkpoint": "HISTORY_ONLY_CURRENT_ZERO",
    "browsing_vote_candidate": "ALLOW_INDEPENDENT_GATE",
}
expected = {
    "comment_candidate_visible_vote": "IGNORE_CONTROL",
    "post_research_visible_vote": "IGNORE_CONTROL",
    "followup_inbound_visible_vote": "IGNORE_CONTROL",
    "explicit_vote_with_comment_request": "SPLIT_TO_BROWSING",
    "explicit_vote_inside_comment_lane": "NAME_BROWSING_AS_OWNER",
    "broad_start_without_vote_request": "NO_BROWSING_LANE",
    "legacy_non_browsing_checkpoint": "HISTORY_ONLY_CURRENT_ZERO",
    "browsing_vote_candidate": "ALLOW_INDEPENDENT_GATE",
}
if scenarios != expected:
    errors.append("scenario_resolution")

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "vote_owner": "BROWSING_ONLY",
    "non_browsing_vote_policy": "DISABLED_BY_LANE",
    "non_browsing_vote_cap": 0,
    "scenarios": scenarios,
}, ensure_ascii=False, sort_keys=True))
