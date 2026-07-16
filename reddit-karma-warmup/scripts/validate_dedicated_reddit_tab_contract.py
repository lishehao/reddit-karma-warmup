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
        "First creation uses one call for tab creation and a second awaited `tab.goto(...)`",
        "never use page-side script navigation or another task's tab",
        "close its tab",
    ],
    ROOT / "references" / "orchestration-core.md": [
        "Every execution task owns one persistent dedicated Reddit primary tab",
        "two-call creation transaction",
        "Never combine `tabs.new()` and the first `goto` in one browser call",
        "`60 sec`",
        "post-timeout page-state check",
        "Never call `finalize({keep: []})` for a nonterminal navigation failure",
        'tab.goto("https://www.reddit.com/")',
        "Never claim an arbitrary user tab",
        'status: "handoff"',
        "own_tab.close()",
        "never persist more than one primary tab",
    ],
    ROOT / "references" / "chrome-network-recovery.md": [
        "Never use `Meta+L` address-bar simulation as recovery",
        "two-call creation transaction",
        "Never combine `tabs.new()` and the first `goto` in one browser call",
        "`60 sec`",
        "navigation acknowledgement uncertain",
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
        "两次浏览器调用完成创建",
        "禁止把创建和首次导航放在同一次调用里",
        "最多 60 秒",
        "超时只代表导航确认不确定",
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
