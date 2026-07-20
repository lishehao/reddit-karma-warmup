#!/usr/bin/env python3
"""Validate one persistent Reddit primary tab per execution task."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


required = {
    ROOT / "SKILL.md": [
        "one persistent dedicated Reddit primary tab",
        "First creation is three atomic calls",
        "120-second outer command contract",
        "page-side script navigation and another task's tab are forbidden",
        "close its tab",
    ],
    ROOT / "references" / "orchestration-core.md": [
        "Every execution task owns one persistent dedicated Reddit primary tab",
        "three-call creation transaction",
        "Never combine `tabs.new()`, `goto`, and page-state reading",
        "`120 sec`",
        "post-timeout page-state read",
        "Never call `finalize({keep: []})` for a nonterminal navigation failure",
        'tab.goto("https://www.reddit.com/")',
        "Never claim an arbitrary user tab",
        'status: "handoff"',
        "own_tab.close()",
        "never persist more than one primary tab",
    ],
    ROOT / "references" / "chrome-network-recovery.md": [
        "Never use `Meta+L` address-bar simulation as recovery",
        "three-call creation transaction",
        "Never combine `tabs.new()`, `goto`, and page-state reading",
        "`120 sec`",
        "acknowledgement uncertain",
        "post-timeout page-state check",
        "Never call `finalize({keep: []})` for this nonterminal condition",
        "proves only tab metadata visibility",
        "still show `about:blank`",
    ],
    ROOT / "references" / "launcher-playbook.md": [
        "dedicated_reddit_tab=required",
        "tab_persistence=handoff_until_mission_terminal",
    ],
}

if README.exists():
    required[README] = [
        "一个专属、持久化的 Reddit 主标签",
        "三次浏览器调用完成首次创建",
        "第二次只执行 `tab.goto(...)`",
        "外层超时统一为 120 秒",
        "20–60 秒后成功返回属于慢成功",
        "非终态以 `handoff` 保留",
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
    "persistent_primary_tabs_per_execution_task": 1,
    "nonterminal_disposition": "HANDOFF",
    "terminal_disposition": "CLOSE_OR_RELEASE",
    "shared_user_tab_fallback": "FORBIDDEN",
}, ensure_ascii=False, sort_keys=True))
