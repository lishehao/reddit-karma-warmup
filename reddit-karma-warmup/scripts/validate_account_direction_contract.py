#!/usr/bin/env python3
"""Validate broad truthful account direction and per-run style separation."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

required = {
    "SKILL.md": ["account-direction.md", "Resolve the account direction"],
    "references/account-direction.md": [
        "3-5",
        "direction_source=default_loci_broad",
        "It is not a fictional persona",
        "disclose affiliation when material",
        "Do not disguise Loci promotion",
        "account-directions/<normalized-reddit-username>.json",
        "确认并开始",
        "A bare `开始` during first-time setup is not direction confirmation",
        "Never reuse another account's file",
        "mission_identity_focus",
        "comment_shortlist",
        "post_reference_shortlist",
    ],
    "references/runtime-and-setup.md": [
        "account-directions/",
        "remain `Reddit 启动台`",
        "Persist atomically outside the managed Skill tree",
        "确认并开始",
    ],
    "references/launcher-playbook.md": [
        "account_direction",
        "direction_source",
        "mission_identity_focus",
        "comment_shortlist",
        "post_reference_shortlist",
    ],
    "references/default-operations-sop.md": ["account_direction + direction_source"],
    "references/operation-style-profiles.md": [
        "per-run focus inside the broader durable `account_direction`",
    ],
    "references/community-presence-playbook.md": ["Resolve `account-direction.md`"],
}

errors: list[str] = []
for relative, needles in required.items():
    body = (ROOT / relative).read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{relative}:{needle}")

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "direction": "BROAD_TRUTHFUL_3_TO_5_PILLARS",
    "confirmation": "ONCE_PER_VISIBLE_ACCOUNT",
    "storage": "USER_OWNED_OUTSIDE_MANAGED_SKILL",
    "style": "NARROW_PER_RUN_SUBSET",
    "promotion": "TRANSPARENT_RULE_GATED",
}, ensure_ascii=False, sort_keys=True))
