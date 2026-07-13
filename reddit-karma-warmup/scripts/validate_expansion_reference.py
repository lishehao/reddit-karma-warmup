#!/usr/bin/env python3
"""Validate the bundled offline community expansion reference and permission fence."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "references" / "community-expansion-pending-review-2026-07-13.md"


def main() -> int:
    body = REFERENCE.read_text(encoding="utf-8")
    errors = []

    shortlist = re.search(
        r"## Suspension 前证据支持的参与优先 shortlist(?P<body>.*?)## 需要继续降级",
        body,
        flags=re.DOTALL,
    )
    shortlist_rows = [] if not shortlist else re.findall(r"^\| `r/[^`]+` \|", shortlist.group("body"), flags=re.MULTILINE)
    if len(shortlist_rows) != 18:
        errors.append(f"shortlist_rows:{len(shortlist_rows)}")

    pending = re.search(
        r"## 本轮新增候选：只做人工复审，不自动升级(?P<body>.*?)## 条件参与、只读研究、不访问",
        body,
        flags=re.DOTALL,
    )
    pending_rows = [] if not pending else re.findall(r"^\| `r/[^`]+` \|", pending.group("body"), flags=re.MULTILINE)
    if len(pending_rows) != 29:
        errors.append(f"pending_rows:{len(pending_rows)}")

    for needle in (
        "本轮新增 live Chrome 核验为 0",
        "全部状态为 `pending_manual_review`",
        "不产生评论、主帖或投票许可",
        "永久排除：`r/gamedev`、`r/CozyGamers`",
    ):
        if needle not in body:
            errors.append(f"missing_fence:{needle}")

    links = {
        ROOT / "SKILL.md": "Discovery only; never grants execution permission",
        ROOT / "references" / "proactive-playbook.md": "is a discovery backlog, not an eligible pool",
        ROOT / "references" / "publish-consistency.md": "closed_pending_live_review",
    }
    for path, needle in links.items():
        if needle not in path.read_text(encoding="utf-8"):
            errors.append(f"missing_link:{path.name}:{needle}")

    if errors:
        print("EXPANSION_REFERENCE=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("EXPANSION_REFERENCE=PASS")
    print("shortlist=18_REPREFLIGHT_ONLY")
    print("new_candidates=29_PENDING_MANUAL_REVIEW")
    print("new_live_chrome=0")
    print("permission=NONE_FROM_REFERENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
