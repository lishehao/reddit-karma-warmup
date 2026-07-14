#!/usr/bin/env python3
"""Validate terminal Heartbeat retirement ordering and failure boundaries."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


required = {
    ROOT / "SKILL.md": [
        "run mandatory terminal cleanup before reporting",
        "clear `own_heartbeat_id` and every `next_due` field",
        "may not retain an idle Heartbeat",
    ],
    ROOT / "references" / "orchestration-core.md": [
        "terminal -> `RETIRE`",
        "mission_target_remaining == 0",
        "unused duration does not justify another wake",
    ],
    ROOT / "references" / "scheduler-and-heartbeats.md": [
        "Completion Cleanup Transaction",
        "Do not report the mission complete while its Heartbeat remains active",
        "heartbeat_retirement_proof",
        "下轮时间：无",
        "does not apply to recoverable browser/network failures",
    ],
}

if README.exists():
    required[README] = [
        "必须先删除自己的 Heartbeat、清空下一次运行时间，再回报任务完成",
        "单个评论簇、每小时配额或阅读下限只是中间进度",
    ]

errors: list[str] = []
for path, needles in required.items():
    body = read(path)
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{path.name}:{needle}")

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "mission_target_met": "DELETE_OWN_HEARTBEAT_BEFORE_TERMINAL_RECEIPT",
    "timer_state_after_completion": "CLEARED",
    "intermediate_slot": "KEEP_HEARTBEAT",
    "recoverable_failure": "KEEP_HEARTBEAT",
}, ensure_ascii=False, sort_keys=True))
