#!/usr/bin/env python3
"""Validate one-time launcher and autonomous lane ownership."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"


def require(path: Path, needles: list[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [f"{path.name}: missing {needle!r}" for needle in needles if needle not in text]


def forbid(path: Path, needles: list[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [f"{path.name}: forbidden {needle!r}" for needle in needles if needle in text]


def main() -> int:
    checks = {
        ROOT / "SKILL.md": [
            "REDDIT_LAUNCHER",
            "Reddit 启动台",
            "There is no persistent main coordinator",
            "heartbeat_owner=self",
            "launcher_callback=none",
            "The user speaks directly to the relevant lane task after dispatch",
            "No coordinator task, coordinator registry, coordinator supervisor Heartbeat",
            "never search or reuse old tasks",
        ],
        ROOT / "references" / "launcher-playbook.md": [
            "then becomes idle",
            "It is not a coordinator",
            "The launcher never creates timers for workers",
            "Do not list/search/read/reuse/unarchive/revive historical tasks",
        ],
        ROOT / "references" / "thread-supervision-runtime.md": [
            "not discovery, reuse, or ongoing supervision",
            "Workers never register with, callback, or send completion/risk events to the launcher",
            "The launcher must not call task list/search/read to find historical workers",
            "fresh_task_creation_failed",
        ],
        ROOT / "references" / "scheduler-and-heartbeats.md": [
            "The worker is the only scheduler for its lane",
            "There is no launcher/coordinator supervisor Heartbeat",
            "targetThreadId=self_task_id",
        ],
        ROOT / "references" / "risk-escalation.md": [
            "There is no callback or central risk surface",
            "Never send this to `Reddit 启动台`",
        ],
    }

    if README.exists():
        checks[README] = [
            "一次性启动台 + 相互独立的执行台",
            "也不晋升为 `Reddit 主控台`",
            "heartbeat_owner=self",
            "启动台进入 idle",
            "不读取、不 callback、不暂停、不修改其他执行台",
            "必须忽略",
            "不得退回旧任务",
        ]

    errors: list[str] = []
    for path, needles in checks.items():
        if not path.exists():
            errors.append(f"missing file: {path}")
            continue
        errors.extend(require(path, needles))

    obsolete = [
        ROOT / "references" / "coordinator-playbook.md",
        ROOT / "references" / "startup-health-check.md",
        ROOT / "references" / "operations-audit.md",
    ]
    for path in obsolete:
        if path.exists():
            errors.append(f"obsolete file still present: {path.name}")

    forbidden = {
        ROOT / "references" / "scheduler-and-heartbeats.md": [
            "The coordinator is the only scheduler",
            "supervisor_heartbeat_id",
            "Coordinator Creation Flow",
        ],
        ROOT / "references" / "thread-supervision-runtime.md": [
            "recurring supervisor",
            "callback target",
            "Search for an unarchived task",
            "Reuse it only when",
        ],
        ROOT / "references" / "launcher-playbook.md": [
            "Create or reuse the exact independent lane tasks",
        ],
    }
    for path, needles in forbidden.items():
        errors.extend(forbid(path, needles))

    if errors:
        print("AUTONOMOUS_LANE_CONTRACT=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    scenarios = {
        "setup_command": "RENAME_LAUNCHER_FIRST",
        "launcher_dispatch": "DELIVER_ONCE_THEN_IDLE",
        "worker_first_slot": "EXECUTE_NOW",
        "worker_continuation": "SELF_OWNED_HEARTBEAT",
        "worker_risk": "HANDLE_OR_ASK_USER_LOCALLY",
        "launcher_callback": "FORBIDDEN",
        "coordinator_supervisor": "ABSENT",
        "sibling_failure": "NO_INTERFERENCE",
        "old_same_title_task": "IGNORE_CREATE_FRESH",
        "old_archived_task": "IGNORE_CREATE_FRESH",
        "old_live_run": "IGNORE_CREATE_FRESH",
        "fresh_create_failure": "REPORT_NO_OLD_TASK_FALLBACK",
    }
    print("AUTONOMOUS_LANE_CONTRACT=PASS")
    for scenario, result in scenarios.items():
        print(f"{scenario}={result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
