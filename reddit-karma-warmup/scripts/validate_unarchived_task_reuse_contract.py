#!/usr/bin/env python3
"""Validate exact Reddit lane reuse without duplicate creation on uncertainty."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"


def require(path, needles):
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"{path}: missing {missing}")
    return text


defaults = json.loads(
    (ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8")
)
expected = {
    "require_present_unarchived": True,
    "archived_task_policy": "REPLACE_NEVER_AUTO_UNARCHIVE",
    "readable_archived_is_liveness": False,
    "registry_update_after_acceptance_only": True,
    "transient_liveness_policy": "ROUTING_UNVERIFIED_NO_REPLACEMENT",
    "unknown_archive_capability_policy": "ROUTING_UNVERIFIED_NO_REPLACEMENT",
    "explicit_missing_task_policy": "REPLACE",
    "permanent_delivery_rejection_policy": "REPLACE",
    "delivery_uncertain_policy": "DELIVERY_UNCERTAIN_NO_REPLACEMENT",
}
if defaults.get("thread_reuse") != expected:
    raise SystemExit("operation-defaults.json: invalid thread_reuse contract")

require(
    ROOT / "SKILL.md",
    [
        "An archived task is never healthy/reusable",
        "Replace\n   only after exact archived, missing, or permanent-delivery-rejection proof",
        "`notLoaded`, empty, timeout, or unknown liveness blocks that lane",
        "[thread runtime](references/thread-supervision-runtime.md) only for task create/reuse semantics",
    ],
)
require(
    ROOT / "references" / "launcher-playbook.md",
    [
        "exact archived, missing, or permanently delivery-rejected task gets",
        "transient/unknown liveness withholds only that lane",
        "routing_unverified`/`delivery_uncertain`",
        "Never search archives or unarchive a task during ordinary dispatch",
    ],
)
require(
    ROOT / "references" / "runtime-and-setup.md",
    [
        "archive-state read support or a current unarchived task inventory",
        "Unarchive capability is not an ordinary operation preflight requirement",
        "only when the user explicitly asks to restore that exact archived task",
    ],
)
runtime = require(
    ROOT / "references" / "thread-supervision-runtime.md",
    [
        "ARCHIVED_EXACT", "MISSING_EXACT", "PERMANENT_DELIVERY_REJECTION",
        "LIVENESS_UNVERIFIED", "ROUTING_CAPABILITY_BLOCKED",
        "routing_unverified", "DELIVERY_UNCERTAIN",
        "exact send yields a `DELIVERY_ACCEPTED`", "Never auto-unarchive it",
        "Mistaken Unarchive Recovery",
        "only when the user explicitly asks to resume that exact task",
    ],
)
if "archive state is unknown and the task is not reusable; create a fresh replacement" in runtime:
    raise SystemExit("thread-supervision-runtime.md: stale unknown-to-replacement rule remains")

if README.exists():
    require(
        README,
        [
            "当前仍存在、未归档、账号与 lane 匹配且能接收任务",
            "普通分发不得自动反归档",
            "只有用户明确要求恢复某一个精确归档任务时",
        ],
    )


def route(present, archived, account_lane_match, delivery, explicit_exact_restore=False):
    if explicit_exact_restore:
        return "USER_EXPLICIT_EXACT_RESTORE_PATH"
    if present is None or archived is None:
        return "ROUTING_UNVERIFIED_NO_REPLACEMENT"
    if delivery == "uncertain":
        return "DELIVERY_UNCERTAIN_NO_REPLACEMENT"
    if archived is True or present is False or delivery == "rejected_permanent":
        return "CREATE_FRESH_REPLACEMENT"
    if present and archived is False and account_lane_match and delivery == "accepted":
        return "REUSE"
    if present and archived is False and not account_lane_match:
        return "CREATE_FRESH_REPLACEMENT"
    return "ROUTING_UNVERIFIED_NO_REPLACEMENT"


scenarios = {
    "present_unarchived_match": route(True, False, True, "accepted"),
    "archived_but_readable": route(True, True, True, "accepted"),
    "explicit_missing": route(False, False, True, "not_sent"),
    "archive_state_unknown": route(True, None, True, "accepted"),
    "transient_not_loaded": route(None, None, True, "not_sent"),
    "present_wrong_account": route(True, False, False, "not_sent"),
    "delivery_uncertain": route(True, False, True, "uncertain"),
    "present_delivery_rejected_permanent": route(True, False, True, "rejected_permanent"),
    "explicit_exact_restore": route(True, True, True, "accepted", True),
}
expected_scenarios = {
    "present_unarchived_match": "REUSE",
    "archived_but_readable": "CREATE_FRESH_REPLACEMENT",
    "explicit_missing": "CREATE_FRESH_REPLACEMENT",
    "archive_state_unknown": "ROUTING_UNVERIFIED_NO_REPLACEMENT",
    "transient_not_loaded": "ROUTING_UNVERIFIED_NO_REPLACEMENT",
    "present_wrong_account": "CREATE_FRESH_REPLACEMENT",
    "delivery_uncertain": "DELIVERY_UNCERTAIN_NO_REPLACEMENT",
    "present_delivery_rejected_permanent": "CREATE_FRESH_REPLACEMENT",
    "explicit_exact_restore": "USER_EXPLICIT_EXACT_RESTORE_PATH",
}
if scenarios != expected_scenarios:
    raise SystemExit(f"scenario mismatch: {scenarios}")

print(json.dumps({"status": "PASS", "scenarios": scenarios}, sort_keys=True))
