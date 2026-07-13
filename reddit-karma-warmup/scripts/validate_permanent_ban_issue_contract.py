#!/usr/bin/env python3
"""Validate permanent subreddit ban issue reporting behavior."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


required = {
    "SKILL.md": [
        "permanent-ban-issue-reporting.md",
        "without asking for a second confirmation",
        "Issue reporting never blocks other eligible work",
    ],
    "references/risk-escalation.md": [
        "An explicit permanent subreddit ban is a separate event",
        "never pause other eligible work",
    ],
    "references/permanent-ban-issue-reporting.md": [
        "PERMANENT_SUBREDDIT_BAN:",
        "search open and closed Issues",
        "GitHub authentication is not a setup dependency",
        "ban_issue_status=pending_retry",
        "Do not trigger for a removed post/comment",
        "Do not repeatedly reopen or verify the Issue",
    ],
    "../README.md": [
        "自动提交一个去重、脱敏的公开 Issue",
        "普通删帖、审核中、临时封禁、限流或推断不会触发",
    ],
}

errors: list[str] = []
for relative, needles in required.items():
    body = (ROOT / relative).resolve().read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{relative}:{needle}")

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "trigger": "CONFIRMED_PERMANENT_SUBREDDIT_BAN_ONLY",
    "issue": "DEDUPED_SANITIZED_AUTO_CREATE",
    "failure": "PENDING_RETRY_CONTINUE_LANE",
}, ensure_ascii=False, sort_keys=True))
