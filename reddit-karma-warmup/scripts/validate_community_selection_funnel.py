#!/usr/bin/env python3
"""Validate broad reference filtering and deep post destination selection."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


required = {
    ROOT / "SKILL.md": [
        "community-selection-funnel.md",
        "assess up to 100 reference rows",
        "lane-specific low-friction shortlists",
    ],
    ROOT / "references" / "community-selection-funnel.md": [
        "mission_identity_focus",
        "reference_rows_assessed",
        "comment_shortlist",
        "post_reference_shortlist",
        "post_selection_timebox=20-30m",
        "reference_rows_assessed_target=up_to_100",
        "live_deep_preflight_target=8-15",
        "verified post is completion",
    ],
    ROOT / "references" / "launcher-playbook.md": [
        "assess up to 100 matching reference rows",
        "comment_shortlist` or `post_reference_shortlist",
        "reference_rows_assessed",
    ],
    ROOT / "references" / "proactive-playbook.md": [
        "allow `20-30m` for the initial selection pass",
        "assess up to `100` reference rows",
        "deep-preflight the best `8-15` communities",
        "For a one-post mission, verified publication is normal completion",
    ],
    ROOT / "references" / "account-direction.md": [
        "--lane comments --reference-sweep-limit 100 --limit 20",
        "--lane posts --reference-sweep-limit 100 --limit 20",
    ],
}

if README.exists():
    required[README] = [
        "评估最多 100 个匹配社区",
        "各收到最多 20 个已过基础门槛的候选",
        "Chrome 深查排名前 8–15 个社区",
    ]

errors: list[str] = []
for path, needles in required.items():
    body = read(path)
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{path.name}:{needle}")

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "reference_sweep_cap": 100,
    "comment_routing": "ACCOUNT_FOCUS_PLUS_RULE_FRIENDLINESS",
    "post_selection_timebox": "20-30m_INITIAL",
    "post_live_deep_preflight": "8-15",
    "post_completion": "VERIFIED_PUBLICATION",
}, ensure_ascii=False, sort_keys=True))
