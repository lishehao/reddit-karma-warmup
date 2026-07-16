#!/usr/bin/env python3
"""Validate state-scoped continue semantics and truthful dispatch receipts."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"


def require(path: Path, needles: list[str], errors: list[str]) -> None:
    body = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{path.name}:{needle}")


def forbid(path: Path, needles: list[str], errors: list[str]) -> None:
    body = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle in body:
            errors.append(f"forbidden:{path.name}:{needle}")


errors: list[str] = []

require(ROOT / "SKILL.md", [
    "BOOTSTRAP_AWAITING_OPERATION",
    "bare `继续` means saved/default direction plus `3h`",
    "Full dispatch requires exact message acceptance",
], errors)

require(ROOT / "references" / "runtime-and-setup.md", [
    "In this state, `继续` rechecks only the missing items and never dispatches",
    "persist `bootstrap_state=BOOTSTRAP_AWAITING_OPERATION`",
    "immediately dispatches the first comments + posts + follow-up missions",
    "later bare `继续` in pinned idle must not duplicate the previous mission",
], errors)

require(ROOT / "references" / "launcher-playbook.md", [
    "A first default dispatch is complete only after comments, posts, and follow-up all accept",
    "Never say `已分发` merely because tasks were resolved or messages were prepared",
    "第一轮已分发：Reddit 评论台、Reddit 发帖台、Reddit 跟进台已收到任务。",
    "后续所有 Reddit 运营任务都可以继续在这个 Reddit 分发台下达",
    "本轮部分分发",
], errors)

require(ROOT / "references" / "thread-supervision-runtime.md", [
    "Successful message acceptance by the exact selected task is delivery proof",
    "Call a requested first dispatch complete only when comments, posts, and follow-up each accepted",
    "never claim that all first-round missions were sent",
], errors)

require(ROOT / "references" / "default-operations-sop.md", [
    "A bare `继续` starts default dispatch only from `BOOTSTRAP_AWAITING_OPERATION`",
    "does not silently repeat the prior mission",
], errors)

if README.exists():
    require(README, [
        "BOOTSTRAP_REPAIR_REQUIRED",
        "健康 Bootstrap 提问后，用户回复“继续”",
        "只有三条精确任务消息都被对应执行台接受后",
        "后续所有 Reddit 运营任务都可以继续在这个 Reddit 分发台下达",
        "本轮部分分发",
    ], errors)

forbid(ROOT / "SKILL.md", ["后续请直接到对应任务操作："], errors)
forbid(ROOT / "references" / "launcher-playbook.md", ["后续请直接到对应任务操作："], errors)
if README.exists():
    forbid(README, ["后续请直接到对应任务操作："], errors)

transitions = {
    ("BOOTSTRAP_REPAIR_REQUIRED", "继续"): "RECHECK_MISSING_ONLY",
    ("BOOTSTRAP_AWAITING_OPERATION", "继续"): "DISPATCH_DEFAULT_3H_THREE_LANES_NOW",
    ("DISTRIBUTOR_IDLE", "继续"): "NO_DUPLICATE_WITHOUT_PENDING_REQUEST",
}

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "transitions": {f"{state}+{command}": result for (state, command), result in transitions.items()},
    "full_dispatch_proof": "ALL_REQUESTED_EXACT_TASKS_ACCEPTED_MESSAGES",
    "partial_dispatch": "NAME_ACCEPTED_AND_UNCONFIRMED_LANES",
    "future_distribution": "SAME_PINNED_REDDIT_DISTRIBUTOR",
}, ensure_ascii=False, sort_keys=True))
