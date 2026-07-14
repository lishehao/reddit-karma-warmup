#!/usr/bin/env python3
"""Validate exact self-targeted Heartbeat identity and readback gates."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"


def require(path: Path, needles: list[str], errors: list[str]) -> None:
    body = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{path.name}:{needle}")


errors: list[str] = []

require(ROOT / "SKILL.md", [
    "worker_task_id=<exact destination task ID>",
    "Resolve `self_task_id` only from the host's exact current-task context",
    "targetThreadId=self_task_id",
    "current_task_id == self_task_id == worker_task_id == Heartbeat.targetThreadId",
    "Hidden next-run time is non-blocking; hidden/mismatched target binding is not verified",
    "Unknown automation IDs are never touched",
    "绑定：本任务已核验",
], errors)

require(ROOT / "references" / "scheduler-and-heartbeats.md", [
    "self_task_id == worker_task_id",
    "self_task_id + worker_task_id + lane + mission_id + own_heartbeat_id",
    "Pre-bind",
    "Explicit bind",
    "Post-bind",
    "target_binding_proof=verified",
    "target_binding_unverified",
    "one_active_heartbeat_per_mission=true",
    "current_task_id == self_task_id == worker_task_id == Heartbeat.targetThreadId",
    "delete that known misbound timer first",
    "never inspect further, pause, repair, or delete it",
], errors)

require(ROOT / "references" / "launcher-playbook.md", [
    "worker_task_id=<the exact selected destination task ID>",
    "worker_task_id=<exact selected destination task ID>",
], errors)

require(ROOT / "references" / "thread-supervision-runtime.md", [
    "worker_task_id=<that same exact destination task ID>",
    "accepts the mission only when it equals `worker_task_id`",
], errors)

require(ROOT / "references" / "default-operations-sop.md", [
    "worker_task_id=<exact destination task ID>",
    "heartbeat_target=worker_task_id",
], errors)

require(ROOT / "references" / "runtime-and-setup.md", [
    "exact-automation target readback",
    "an unreadable target binding is not verified",
], errors)

require(ROOT / "references" / "orchestration-core.md", [
    "self_task_id + worker_task_id + lane + title",
    "own_heartbeat_id + target_binding_proof",
    "pre-bind, explicit-bind, and post-bind transaction",
], errors)

if README.exists():
    require(README, [
        "按返回的 automation ID 读回目标任务 ID",
        "目标任务 ID 隐藏或不匹配则不能算绑定成功",
        "worker_task_id=<精确目标任务 ID>",
    ], errors)

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "prebind_mismatch": "NO_REDDIT_ACTION_NO_TIMER_MUTATION",
    "create_or_update": "EXPLICIT_SELF_TARGET",
    "postbind": "READ_EXACT_AUTOMATION_AND_COMPARE",
    "hidden_target": "UNVERIFIED_DELETE_ONLY_OWN_RECORDED_TIMER",
    "hidden_next_run": "NONBLOCKING_CREATED_UNREADABLE",
    "wake_mismatch": "NO_REDDIT_ACTION_REPAIR_ONLY_OWN_TIMER",
    "unknown_automation_id": "NEVER_TOUCH",
    "existing_own_heartbeat": "UPDATE_NOT_DUPLICATE",
    "reused_task_new_mission": "RETIRE_VERIFIED_STALE_OWN_TIMER",
    "terminal": "DELETE_BEFORE_REPORT",
}, ensure_ascii=False, sort_keys=True))
