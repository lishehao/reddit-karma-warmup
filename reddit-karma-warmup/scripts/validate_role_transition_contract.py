#!/usr/bin/env python3
"""Validate the Reddit Bootstrap-to-coordinator role contract."""

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
            "B0_BOOTSTRAP_NAME",
            "REDDIT_BOOTSTRAP",
            "Reddit 启动台",
            "REDDIT_COORDINATOR",
            "ACCOUNT_BOOTSTRAP",
            "Reddit 主控台",
            "same task ID",
            "direct-mission fast path",
            "rename_unavailable",
            "Never create a second task to become the main console",
        ],
        ROOT / "references" / "runtime-and-setup.md": [
            "The first available UI action",
            "before downloading",
            "remain Bootstrap",
            "transition this same task in place",
            "direct-mission fast path",
            "Naming is presentation state, not a dependency or blocker",
            "Do not create a second installer task or a second future coordinator",
        ],
        ROOT / "references" / "orchestration-core.md": [
            "setup command immediately names the current task `Reddit 启动台`",
            "Never create a second main task for the role transition",
        ],
        ROOT / "references" / "coordinator-playbook.md": [
            "completed `B2_PROMOTE`",
            "It never creates or replaces itself",
            "do not create workers or mission Heartbeats",
        ],
        ROOT / "references" / "thread-supervision-runtime.md": [
            "never create a second main/coordinator task",
            "Worker discovery, task creation, and replacement rules below apply only to lane workers",
        ],
        README: [
            "请先将当前任务重命名为“Reddit 启动台”",
            "第一个可用的界面动作",
            "早于下载、依赖检查、预检或方案解释",
            "不得另建 installer 或第二个未来主控台",
            "在同一个任务内切换为 `REDDIT_COORDINATOR`",
            "立即把当前任务命名为 `Reddit 主控台` 并在同一轮开始执行",
        ],
    }

    errors: list[str] = []
    for path, needles in checks.items():
        if not path.exists():
            errors.append(f"missing file: {path}")
            continue
        errors.extend(require(path, needles))

    errors.extend(
        forbid(
            README,
            [
                "任一工作线没有 proof，就不能声称整项任务已启动",
                "用户回复 setup 后先完成预检，再重命名",
            ],
        )
    )

    if errors:
        print("ROLE_TRANSITION_CONTRACT=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    scenarios = {
        "setup_command": "RENAME_BOOTSTRAP_FIRST",
        "hard_repair": "REMAIN_BOOTSTRAP",
        "healthy_handoff": "SAME_TASK_PROMOTE_RENAME_MAIN",
        "direct_mission": "FAST_PATH_MAIN_AND_EXECUTE_NOW",
        "rename_unavailable": "CONTINUE_AND_RETRY_PRESENTATION",
        "duplicate_main": "FORBIDDEN",
    }
    print("ROLE_TRANSITION_CONTRACT=PASS")
    for scenario, result in scenarios.items():
        print(f"{scenario}={result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
