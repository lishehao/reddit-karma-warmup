#!/usr/bin/env python3
"""Validate that archived Reddit lane tasks are replaced, never auto-restored."""

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
}
if defaults.get("thread_reuse") != expected:
    raise SystemExit("operation-defaults.json: invalid thread_reuse contract")

require(
    ROOT / "SKILL.md",
    [
        "exact present, unarchived, healthy account+lane tasks",
        "An archived task is never healthy or reusable",
        "Ordinary distributor dispatch never auto-unarchives a task",
        "explicit user request to resume that exact archived task",
    ],
)
require(
    ROOT / "references" / "launcher-playbook.md",
    [
        "currently present, unarchived, healthy registered task",
        "ordinary dispatch never auto-unarchives it",
        "Never search archives or unarchive a task during ordinary dispatch",
        "Archived registry entries are replacement signals",
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
        "last_known_archive_state=unarchived",
        "current unarchived task inventory",
        "`read_thread` history alone is observation, not liveness",
        "archive state is unknown and the task is not reusable",
        "current product state proves that it is present and unarchived",
        "A readable archived task, exact archived ID",
        "Never auto-unarchive it",
        "including when the registered task is archived",
        "Mistaken Unarchive Recovery",
        "only when the user explicitly asks to resume that exact task",
    ],
)
if "Unarchive that exact registered task when needed" in runtime:
    raise SystemExit("thread-supervision-runtime.md: stale auto-unarchive rule remains")

if README.exists():
    require(
        README,
        [
            "当前仍存在、未归档、账号与 lane 匹配且能接收任务",
            "普通分发不得自动反归档",
            "只有用户明确要求恢复某一个精确归档任务时",
        ],
    )


def route(present, archived, account_lane_match, accepts, explicit_exact_restore=False):
    if explicit_exact_restore:
        return "USER_EXPLICIT_EXACT_RESTORE_PATH"
    if present and archived is False and account_lane_match and accepts:
        return "REUSE"
    return "CREATE_FRESH_REPLACEMENT"


scenarios = {
    "present_unarchived_match": route(True, False, True, True),
    "archived_but_readable": route(True, True, True, True),
    "archived_exact_id": route(True, True, True, True),
    "archive_state_unknown": route(True, None, True, True),
    "present_wrong_account": route(True, False, False, True),
    "present_delivery_rejected": route(True, False, True, False),
    "explicit_exact_restore": route(True, True, True, True, True),
}
expected_scenarios = {
    "present_unarchived_match": "REUSE",
    "archived_but_readable": "CREATE_FRESH_REPLACEMENT",
    "archived_exact_id": "CREATE_FRESH_REPLACEMENT",
    "archive_state_unknown": "CREATE_FRESH_REPLACEMENT",
    "present_wrong_account": "CREATE_FRESH_REPLACEMENT",
    "present_delivery_rejected": "CREATE_FRESH_REPLACEMENT",
    "explicit_exact_restore": "USER_EXPLICIT_EXACT_RESTORE_PATH",
}
if scenarios != expected_scenarios:
    raise SystemExit(f"scenario mismatch: {scenarios}")

print(json.dumps({"status": "PASS", "scenarios": scenarios}, sort_keys=True))
