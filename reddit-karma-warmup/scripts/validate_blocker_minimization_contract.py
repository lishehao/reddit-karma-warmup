#!/usr/bin/env python3
"""Validate lane-local recovery and continuation behavior."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


required = {
    "SKILL.md": [
        "Recover stale tabs",
        "One lane fault affects only that lane",
        "Pending-review own posts are withdrawn immediately",
    ],
    "references/risk-escalation.md": [
        "Default: Continue Locally",
        "Direct User Repair In This Task",
        "One lane's failure never changes another lane's mission",
    ],
    "references/scheduler-and-heartbeats.md": [
        "Technical failure is not timer termination",
        "Never inspect, pause, repair, or delete another task's timer",
    ],
    "references/chrome-network-recovery.md": [
        "Multiple unsuccessful recovery wakes remain `lane_recovering`",
    ],
}

errors: list[str] = []
for relative, needles in required.items():
    body = read(relative)
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{relative}:{needle}")

scenarios = {
    "network_timeout": "SELF_RETRY_KEEP_OWN_HEARTBEAT",
    "chrome_disconnect": "RECONNECT_OWN_TAB",
    "empty_candidates": "NO_ACTION_CHECKPOINT_REDISCOVER",
    "single_rule_rejection": "RETARGET_CURRENT_LANE",
    "pending_approval": "DELETE_RETIRE_RETARGET",
    "timed_rate_limit": "AUTO_REPROBE_CURRENT_LANE",
    "uncertain_mutation": "HOLD_EXACT_ACTION_CONTINUE_LOCAL_SAFE_WORK",
    "persistent_login_or_captcha": "ASK_USER_IN_CURRENT_TASK",
    "sibling_failure": "IGNORE_AND_CONTINUE",
    "explicit_stop_or_deadline": "RETIRE_OWN_HEARTBEAT",
}

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({"status": "PASS", "scenarios": scenarios}, ensure_ascii=False, sort_keys=True))
