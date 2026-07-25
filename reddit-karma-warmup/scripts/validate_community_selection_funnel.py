#!/usr/bin/env python3
"""Validate broad reference filtering and deep post destination selection."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"
defaults = json.loads((ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8"))


required = {
    ROOT / "SKILL.md": [
        "community-selection-funnel.md",
        "action authority",
        "Load only filtered rows",
    ],
    ROOT / "references" / "community-selection-funnel.md": [
        "mission_identity_focus",
        "reference_rows_assessed",
        "comment_shortlist",
        "post_reference_shortlist",
        "posts.narrowing_timebox_minutes",
        "posts.<intensity>.reference_sweep_target",
        "community_selection.post_live_preflight_community_range",
        "verified post is completion",
        "Do not report the mission complete because a configured timebox",
    ],
    ROOT / "references" / "launcher-playbook.md": [
        "selected lane's configured reference sweep",
        "lane shortlist",
        "traffic-probe row is not an action target",
    ],
    ROOT / "references" / "comments-playbook.md": [
        "eligible communities",
        "qualified-read target",
    ],
    ROOT / "references" / "posts-playbook.md": [
        "broad-to-deep funnel",
        "live deep reads",
        "resolved post-mode candidate gate",
        "verified publication normally completes a one-post action target",
    ],
    ROOT / "references" / "account-direction.md": [
        "--lane comments --reference-sweep-limit 100 --limit 20",
        "--lane posts --reference-sweep-limit 150 --limit 30",
    ],
}
if README.exists():
    required[README] = [
        "标准发帖任务评估最多 150 个匹配社区",
        "下发最多 30 个低摩擦候选",
        "Chrome 深查排名前 12–20 个社区",
    ]

errors: list[str] = []
selection = defaults["community_selection"]
if selection["comment_reference_sweep_limit"] != 100:
    errors.append("comment_reference_sweep_limit")
if selection["shortlist_limit"] != 20:
    errors.append("shortlist_limit")
if selection["post_shortlist_limit"] != 30:
    errors.append("post_shortlist_limit")
if selection["traffic_floor_weekly_visitors"] != 5000:
    errors.append("traffic_floor_weekly_visitors")
if selection["post_live_preflight_community_range"] != [12, 20]:
    errors.append("post_live_preflight_community_range")
if selection["post_initial_candidate_range"] != [20, 30]:
    errors.append("post_initial_candidate_range")
for path, needles in required.items():
    body = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{path.name}:{needle}")

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "reference_sweep_cap": "CANONICAL_CONFIG",
    "shortlist_cap": "CANONICAL_CONFIG",
    "post_live_deep_preflight": "CANONICAL_CONFIG",
    "permission": "LIVE_ACTION_GATES_REQUIRED",
}, ensure_ascii=False, sort_keys=True))
