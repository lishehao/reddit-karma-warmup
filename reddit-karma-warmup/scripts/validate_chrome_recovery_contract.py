#!/usr/bin/env python3
"""Validate bounded same-wake and persistent cross-wake Chrome recovery."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = json.loads((ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8"))
RECOVERY = DEFAULTS.get("chrome_recovery", {})
errors: list[str] = []


expected = {
    "same_wake_recovery_cycle_cap": 2,
    "same_url_retry_cap_per_wake": 1,
    "tab_replacement_cap_per_wake": 1,
    "diagnostic_tab_cap_per_wake": 1,
    "neutral_probe_cap_per_wake": 1,
    "short_wait_seconds": [5, 15],
    "recovery_backoff_minutes": [5, 10, 20, 40, 60],
    "backoff_jitter_minutes": [0, 3],
    "quiet_mode_after_consecutive_wakes": 3,
    "control_user_repair_after_consecutive_wakes": 3,
    "healthy_read_proofs_to_reset": 2,
    "user_notice_suppression_minutes": 120,
    "account_identity_recheck_after_reconnect": True,
    "uncertain_mutation_retry_allowed": False,
}
for key, value in expected.items():
    if RECOVERY.get(key) != value:
        errors.append(f"default:{key}:{RECOVERY.get(key)!r}")

backoff = RECOVERY.get("recovery_backoff_minutes", [])
if backoff != sorted(set(backoff)) or not backoff or backoff[-1] > 60:
    errors.append(f"backoff_not_bounded_monotonic:{backoff!r}")

required = {
    "SKILL.md": [
        "Recovery is mission-persistent but wake-bounded",
        "chrome-recovery-edge-cases.md",
        "Never use a later wake to replay an uncertain mutation",
    ],
    "references/chrome-network-recovery.md": [
        "Apply `chrome-atomic-command-runtime.md` first",
        "configured `120 sec` outer timeout",
        "`slow_success`, not `page_control_partial`",
        "record `ambient_network_degraded`",
        "operation-defaults.json.chrome_recovery",
        "invalidate/reconnect the browser binding only after an explicit browser-disconnected result",
        "`openTabs()` returning no tabs is not proof that the browser disconnected",
        "classify `page_control_partial`",
        "do not immediately repeat the same control call in that wake",
        "error_fingerprint = error_class|exact_code|failure_scope|hostname",
        "same_wake_recovery_cycle_cap",
        "recovery_backoff_minutes",
        "quiet_mode_after_consecutive_wakes",
        "healthy_read_proofs_to_reset",
        "Never submit a second time, even on a later wake or after an upgrade",
        "When `operation_stop_at` arrives during recovery",
        "next_recovery_at=min(proposed_recovery_due, operation_stop_at)",
        "diagnostic_tab_cap_per_wake",
    ],
    "references/chrome-recovery-edge-cases.md": [
        "Atomic command returns after 20-60 seconds",
        "`Statsig` or `ab.chatgpt.com` timeout appears but the Chrome command succeeds",
        "Chrome tool is temporarily unavailable",
        "`openTabs()` returns an empty list",
        "Chrome restarted and tab IDs changed",
        "`goto` times out but navigation may have landed",
        "HTTP `429` or `Too Many Requests`",
        "Vote click acknowledgement is unknown",
        "Heartbeat wakes while Chrome/network is still down",
        "Mission deadline passes during outage",
        "Proposed recovery or `Retry-After` falls after the mission deadline",
        "Checkpoint write fails",
        "Existing self-owned Heartbeat update/readback fails",
        "First Heartbeat creation or target binding cannot be verified",
        "Nonterminal tab handoff/finalize acknowledgement is unknown",
        "Tab inventory/creation works but exact-tab page control times out",
        "Classify `page_control_partial`, not disconnected/network/account failure",
        "User switches Reddit accounts in the shared Chrome profile",
        "Same-wake retries are bounded",
    ],
    "references/lane-state-checkpoint.md": [
        "recovery_state_version=1",
        "consecutive_failure_wakes + same_wake_recovery_cycles + backoff_index",
        "quarantined_mutation_url + quarantined_outbound_text_hash",
        "optional when reading a checkpoint written by an older Skill version",
    ],
    "references/scheduler-and-heartbeats.md": [
        "recovery_status=recovering|quiet_recovery",
        "Repeated technical wakes use the same logical timer",
        "do not perform a final Chrome probe or mutation",
        "deadline-clamped wake performs cleanup only",
        "scheduler_repair_required",
    ],
    "references/risk-escalation.md": [
        "cross-wake backoff and quiet-recovery state",
        "A later wake never clears or replays an uncertain mutation",
    ],
}
for relative, needles in required.items():
    body = (ROOT / relative).read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{relative}:{needle}")

scenarios = {
    "empty_tab_inventory_without_disconnect": "RETRY_INVENTORY_KEEP_BROWSER_BINDING",
    "explicit_browser_disconnect": "RECONNECT_SAME_PROFILE_RECHECK_ACCOUNT",
    "missing_owned_tab": "REPLACE_OWN_TAB_ONCE",
    "navigation_timeout_before_mutation": "POST_TIMEOUT_STATE_READ_THEN_ONE_RETRY",
    "partial_page_control_timeout": "KEEP_BROWSER_BINDING_END_PAGE_WORK_THIS_WAKE",
    "submit_acknowledgement_unknown": "QUARANTINE_EXACT_MUTATION_NEVER_REPLAY",
    "http_429": "END_WAKE_KEEP_HEARTBEAT_RESPECT_RETRY_AFTER",
    "repeated_retryable_failure": "BACKOFF_THEN_QUIET_RECOVERY",
    "account_identity_drift": "READ_ONLY_USER_REPAIR_NO_WRITES",
    "deadline_during_outage": "TERMINAL_CLEANUP_NO_FINAL_PROBE",
}

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "same_wake_cycle_cap": RECOVERY["same_wake_recovery_cycle_cap"],
    "cross_wake_backoff_minutes": backoff,
    "quiet_mode_after_wakes": RECOVERY["quiet_mode_after_consecutive_wakes"],
    "scenarios": scenarios,
}, ensure_ascii=False, sort_keys=True))
