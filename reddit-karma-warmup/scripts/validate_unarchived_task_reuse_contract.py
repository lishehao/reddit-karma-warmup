#!/usr/bin/env python3
"""Validate Reddit lane reuse and one replacement per unavailable lane+mission."""

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
    "transient_liveness_policy": "CREATE_FRESH_REPLACEMENT_ONCE_PER_LANE_MISSION",
    "unknown_archive_capability_policy": "CREATE_FRESH_REPLACEMENT_ONCE_PER_LANE_MISSION",
    "not_loaded_policy": "CREATE_FRESH_REPLACEMENT_ONCE_PER_LANE_MISSION",
    "replacement_creation_cap_per_lane_mission": 1,
    "old_unavailable_task_policy": "NEVER_AUTO_UNARCHIVE_OR_OPERATE",
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
        "one fresh same-lane replacement",
        "never\n   create a second replacement for the same lane+mission",
        "[thread runtime](references/thread-supervision-runtime.md) only for task create/reuse semantics",
    ],
)
require(
    ROOT / "references" / "launcher-playbook.md",
    [
        "unavailable (`notLoaded`/empty/timeout/unknown) task gets one fresh same-lane",
        "deterministic replacement key per account+lane+mission",
        "replacement_creation_uncertain`/`delivery_uncertain`",
        "Never search archives or unarchive a task during ordinary dispatch",
    ],
)
require(
    ROOT / "references" / "runtime-and-setup.md",
    [
        "Attempt archive-state read support or a current unarchived task inventory",
        "do not block a fresh same-lane replacement",
        "Unarchive capability is not an ordinary operation preflight requirement",
        "only when the user explicitly asks to restore that exact archived task",
    ],
)
runtime = require(
    ROOT / "references" / "thread-supervision-runtime.md",
    [
        "ARCHIVED_EXACT", "MISSING_EXACT", "PERMANENT_DELIVERY_REJECTION",
        "LIVENESS_UNVERIFIED", "UNAVAILABLE_SUPERSEDED_PENDING_ACCEPTANCE",
        "replacement_key=<account>/<lane>/<mission_id>",
        "replacement_creation_uncertain", "DELIVERY_UNCERTAIN",
        "exact send yields a `DELIVERY_ACCEPTED`", "Never auto-unarchive it",
        "Mistaken Unarchive Recovery",
        "only when the user explicitly asks to resume that exact task",
    ],
)
if "routing_unverified`, retry one exact readback" in runtime:
    raise SystemExit("thread-supervision-runtime.md: stale uncertainty-block rule remains")

if README.exists():
    require(
        README,
        [
            "当前仍存在、未归档、账号与 lane 匹配且能接收任务",
            "普通分发不得自动反归档",
            "只有用户明确要求恢复某一个精确归档任务时",
        ],
    )


def route(present, archived, account_lane_match, delivery, replacement_created=False,
          explicit_exact_restore=False):
    if explicit_exact_restore:
        return "USER_EXPLICIT_EXACT_RESTORE_PATH"
    if replacement_created:
        return "NO_SECOND_REPLACEMENT"
    if delivery == "uncertain":
        return "DELIVERY_UNCERTAIN_NO_REPLACEMENT"
    if present is None or archived is None:
        return "CREATE_FRESH_REPLACEMENT"
    if archived is True or present is False or delivery == "rejected_permanent":
        return "CREATE_FRESH_REPLACEMENT"
    if present and archived is False and account_lane_match and delivery == "accepted":
        return "REUSE"
    if present and archived is False and not account_lane_match:
        return "CREATE_FRESH_REPLACEMENT"
    return "CREATE_FRESH_REPLACEMENT"


scenarios = {
    "present_unarchived_match": route(True, False, True, "accepted"),
    "archived_but_readable": route(True, True, True, "accepted"),
    "explicit_missing": route(False, False, True, "not_sent"),
    "archive_state_unknown": route(True, None, True, "accepted"),
    "transient_not_loaded": route(None, None, True, "not_sent"),
    "present_wrong_account": route(True, False, False, "not_sent"),
    "delivery_uncertain": route(True, False, True, "uncertain"),
    "unavailable_after_create_unknown": route(None, None, True, "not_sent", True),
    "present_delivery_rejected_permanent": route(True, False, True, "rejected_permanent"),
    "explicit_exact_restore": route(
        True, True, True, "accepted", explicit_exact_restore=True
    ),
}
expected_scenarios = {
    "present_unarchived_match": "REUSE",
    "archived_but_readable": "CREATE_FRESH_REPLACEMENT",
    "explicit_missing": "CREATE_FRESH_REPLACEMENT",
    "archive_state_unknown": "CREATE_FRESH_REPLACEMENT",
    "transient_not_loaded": "CREATE_FRESH_REPLACEMENT",
    "present_wrong_account": "CREATE_FRESH_REPLACEMENT",
    "delivery_uncertain": "DELIVERY_UNCERTAIN_NO_REPLACEMENT",
    "unavailable_after_create_unknown": "NO_SECOND_REPLACEMENT",
    "present_delivery_rejected_permanent": "CREATE_FRESH_REPLACEMENT",
    "explicit_exact_restore": "USER_EXPLICIT_EXACT_RESTORE_PATH",
}
if scenarios != expected_scenarios:
    raise SystemExit(f"scenario mismatch: {scenarios}")

print(json.dumps({"status": "PASS", "scenarios": scenarios}, sort_keys=True))
