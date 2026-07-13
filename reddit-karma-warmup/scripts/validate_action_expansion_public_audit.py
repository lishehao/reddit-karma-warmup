#!/usr/bin/env python3
"""Validate the bundled public action-expansion audit and its permission fence."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "references" / "community-action-expansion-public-audit-2026-07-13.md"


def main() -> int:
    body = REFERENCE.read_text(encoding="utf-8")
    errors: list[str] = []

    matrix = re.search(
        r"## 逐候选动作矩阵：未确认项和自然话题(?P<body>.*?)## 账号门槛与审核机制汇总",
        body,
        flags=re.DOTALL,
    )
    rows = [] if not matrix else re.findall(r"^\| `r/[^`]+` \|", matrix.group("body"), flags=re.MULTILINE)
    if len(rows) != 30:
        errors.append(f"candidate_rows:{len(rows)}")

    for needle in (
        "`public-rule-confirmed` | 14",
        "`public-rule-signal` | 3",
        "仅名称级 pending | 13",
        "本轮真实 Chrome 页面核验 | 0",
        "没有任何候选因为本轮公开 Web 核验而获得当前账号执行许可",
        "r/gamedev",
        "r/CozyGamers",
    ):
        if needle not in body:
            errors.append(f"missing:{needle}")

    links = {
        ROOT / "SKILL.md": "grants no current action permission",
        ROOT / "references" / "proactive-playbook.md": "every row is still `closed_pending_live_review`",
        ROOT / "references" / "publish-consistency.md": "no comment, post, vote, Join, or product permission is created",
    }
    for path, needle in links.items():
        if needle not in path.read_text(encoding="utf-8"):
            errors.append(f"missing_link:{path.name}:{needle}")

    if errors:
        print("ACTION_EXPANSION_PUBLIC_AUDIT=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("ACTION_EXPANSION_PUBLIC_AUDIT=PASS")
    print("candidates=30")
    print("public_rule_confirmed=14")
    print("public_rule_signal=3")
    print("name_only=13")
    print("permission=NONE_UNTIL_LIVE_PREFLIGHT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
