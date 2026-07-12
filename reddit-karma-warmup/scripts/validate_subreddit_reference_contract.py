#!/usr/bin/env python3
"""Validate the bundled Feishu subreddit archive and progressive retrieval contract."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "references" / "loci-subreddit-pool-v1.md"


def main() -> int:
    body = REFERENCE.read_text(encoding="utf-8")
    rows = re.findall(r"^\| (r/[^ |]+) \|", body, flags=re.MULTILINE)
    normalized = [row.casefold() for row in rows]
    required = [
        "revision `763`",
        "主要用户",
        "痛点/反馈",
        "版规/边界",
        "可发内容",
        "账号适配/备注",
        "近期信号/更新",
        "Live Reddit rules, submit controls, and current account state always win.",
    ]
    errors = [f"missing:{needle}" for needle in required if needle not in body]
    if len(rows) != 144:
        errors.append(f"row_count:{len(rows)}")
    if len(normalized) != len(set(normalized)):
        errors.append("duplicate_subreddit")

    contracts = {
        ROOT / "SKILL.md": "Never load the whole archive by default",
        ROOT / "references" / "publish-consistency.md": "never read the complete archive into context",
        ROOT / "references" / "proactive-playbook.md": "do not load the entire archive",
    }
    for path, needle in contracts.items():
        if needle not in path.read_text(encoding="utf-8"):
            errors.append(f"missing_contract:{path.name}:{needle}")

    if errors:
        print("SUBREDDIT_REFERENCE_CONTRACT=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("SUBREDDIT_REFERENCE_CONTRACT=PASS")
    print("revision=763")
    print("subreddit_rows=144")
    print("duplicates=0")
    print("retrieval=PROGRESSIVE_EXACT_OR_FILTERED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
