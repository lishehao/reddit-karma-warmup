#!/usr/bin/env python3
"""Validate reusable stateless launcher and autonomous lane ownership."""

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
            "Reddit 分发台",
            "reusable stateless launcher",
            "There is no persistent main coordinator",
            "heartbeat_owner=self",
            "launcher_callback=none",
            "The user speaks directly to the relevant lane task after dispatch",
            "No coordinator task, coordinator registry, coordinator supervisor Heartbeat",
            "never search or reuse old tasks",
            "Every distribution command creates another fresh run",
            "自然浏览/投票：随以上执行台读取内容时完成",
            "L1_DIRECTION",
            "L2_READY",
            "pinned=true",
            "never list/search by title to find the task to pin",
        ],
        ROOT / "references" / "launcher-playbook.md": [
            "returns to pinned idle",
            "It is not a coordinator",
            "The launcher never creates timers for workers",
            "Do not list/search/read/reuse/unarchive/revive historical tasks",
            "For every direct command it creates fresh requested lane tasks",
            "next command repeats fresh creation with a new run ID",
            "Post-Dispatch Instruction",
            "Broad `开始/运营` enables comments, posts, and follow-up",
            "Create browsing only for an explicit pure-browse/vote request",
            "Load in the pinned `Reddit 分发台` after temporary `Reddit 启动台` setup passes preflight",
            "Never unpin the distribution task",
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
            "Never send this to `Reddit 分发台`",
        ],
    }

    if README.exists():
        checks[README] = [
            "临时启动台 -> 可重复使用的无状态分发台 + 相互独立的执行台",
            "也不晋升为 `Reddit 主控台`",
            "heartbeat_owner=self",
            "然后回到 pinned idle",
            "不读取、不 callback、不暂停、不修改其他执行台",
            "必须忽略",
            "不得退回旧任务",
            "执行任务始终不会返回分发台",
            "每次用户回复“开始”",
            "已启动：<本次创建的任务>",
            "自然浏览/投票：随以上执行台读取内容时完成",
            "当前任务已切换为 Reddit 分发台",
            "分发台已置顶；后续新一轮运营都从这里分配",
            "执行台保持不置顶",
            "首次安装时只回复 `开始` 不等于确认方向",
            "确认并开始",
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
            "# One-Time Launcher Playbook",
            "Future user instructions belong in the relevant lane task",
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
        "setup_health_passed": "RENAME_DISTRIBUTOR",
        "first_account_direction": "CONFIRM_ONCE_THEN_PERSIST",
        "known_account_direction": "REUSE_WITHOUT_REPROMPT",
        "setup_health_pin": "PIN_EXACT_DISTRIBUTOR_ID",
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
        "same_launcher_second_command": "NEW_RUN_FRESH_EXECUTORS",
        "launcher_idle_reuse": "USER_TRIGGER_ONLY",
        "launcher_idle_presentation": "PINNED",
        "worker_return_to_launcher": "FORBIDDEN",
    }
    print("AUTONOMOUS_LANE_CONTRACT=PASS")
    for scenario, result in scenarios.items():
        print(f"{scenario}={result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
