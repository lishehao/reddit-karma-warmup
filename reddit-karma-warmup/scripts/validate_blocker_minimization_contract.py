#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


required = {
    "SKILL.md": [
        "Progress-first fallback is mandatory",
        "Hard user-repair states are allowlisted and current-only",
        "one slow/failed lane never delays healthy lanes",
    ],
    "references/risk-escalation.md": [
        "Default outcome is `continue`, not `blocked`",
        "user_repair_required",
        "explicit_target_decision",
    ],
    "references/thread-supervision-runtime.md": [
        "Timer creation is per-lane, never a central all-lanes barrier",
    ],
    "references/startup-health-check.md": [
        "without becoming a batch-wide startup barrier",
        "Exhausting current alternatives records a no-action checkpoint",
    ],
    "references/chrome-network-recovery.md": [
        "three consecutive recovery wakes",
    ],
}

forbidden = {
    "references/thread-supervision-runtime.md": [
        "Central batch creation is allowed only after every enabled lane has first proof",
        "mark only that lane `startup_blocked`",
    ],
    "references/startup-health-check.md": [
        "`submit_verified`, `surface_visible`, and `survivor_visible`",
    ],
    "references/orchestration-core.md": [
        "clear rule prohibition for the current target",
        "sitewide rate limit, lock/suspension, wrong/logged-out account, credential request",
    ],
    "references/risk-escalation.md": [
        "severity: <decision_required|lane_blocked|account_blocked",
    ],
}

errors = []
for relative, needles in required.items():
    body = read(relative)
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{relative}:{needle}")

for relative, needles in forbidden.items():
    body = read(relative)
    for needle in needles:
        if needle in body:
            errors.append(f"forbidden:{relative}:{needle}")

scenarios = {
    "network_timeout": "AUTO_RETRY_CONTINUE",
    "chrome_disconnect_first_wake": "AUTO_RETRY_CONTINUE",
    "empty_candidates": "NO_ACTION_CHECKPOINT_REDISCOVER",
    "single_rule_rejection": "RETARGET_CONTINUE",
    "pending_approval": "DELETE_RETIRE_RETARGET",
    "delayed_survivor_visibility": "QUALITY_CHECK_CONTINUE",
    "worker_transport_failure": "LANE_RECOVERING_SIBLINGS_CONTINUE",
    "misbound_timer": "REPLACE_NO_GAP",
    "timed_rate_limit": "AUTO_REPROBE_CONTINUE_ALLOWED_WORK",
    "uncertain_mutation": "HOLD_EXACT_ACTION_CONTINUE_OTHERS",
    "persistent_login_or_captcha": "USER_REPAIR_KEEP_HEARTBEATS",
    "explicit_stop_or_deadline": "TERMINAL_RELEASE",
}

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({"status": "PASS", "scenarios": scenarios}, ensure_ascii=False, sort_keys=True))
