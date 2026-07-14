#!/usr/bin/env python3
"""Validate strict K0 post unlocking and account-gate audit coverage."""

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"
AUDIT = ROOT / "references" / "posting-account-gates-audit-2026-07-14.csv"


def require(path: Path, needles: list[str], errors: list[str]) -> None:
    body = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{path.name}:{needle}")


errors: list[str] = []

with AUDIT.open(newline="", encoding="utf-8-sig") as handle:
    rows = list(csv.DictReader(handle))

counts = Counter(row["audit_status"] for row in rows)
expected = {
    "verified_numeric": 5,
    "verified_qualitative": 10,
    "no_public_gate_found": 7,
    "unknown": 229,
    "blocked": 1,
    "organization_deny": 2,
}

if len(rows) != 254:
    errors.append(f"audit_rows:{len(rows)}!=254")
if dict(counts) != expected:
    errors.append(f"audit_status_counts:{dict(counts)}!={expected}")

require(ROOT / "references" / "new-account-bootstrap.md", [
    "main-post target/cap `0/0` while the account remains K0",
    "Every K0 account publishes no main post",
    "## Main Post Unlock",
    "combined sitewide Karma is at least `50`",
    "account age is at least `7d`",
    "at least `10` comments remain visible across at least `3` eligible communities",
    "`unknown`, `blocked`, and `organization_deny` are closed for K0 main posts",
], errors)

require(ROOT / "references" / "proactive-playbook.md", [
    "| locked at `0` |",
    "require `main_post_unlock=passed`",
    "never publish a second main post inside the same rolling `24h`",
], errors)

require(ROOT / "references" / "default-operations-sop.md", [
    "K0 always uses post action target/cap `0/0`",
    "post_action_mode=research_preflight_only",
    "Unknown audit rows never enter a K0/K1 post shortlist",
], errors)

require(ROOT / "references" / "posting-account-gates-audit-status.md", [
    "completed ordinary gate reviews: `22/252` (`8.73%`)",
    "The audit is not complete",
    "Blank fields mean not publicly confirmed, not zero",
], errors)

require(ROOT / "SKILL.md", [
    "unknown is closed for K1 publishing while K0 never publishes",
    "K0 is always research-only with target/cap `0/0`",
    "at least `50` combined Karma",
], errors)

if README.exists():
    require(README, [
        "主帖目标/上限固定为 `0/0`",
        "至少 50 combined Karma",
        "K1 解锁后仍最多每 24 小时 1 篇",
        "普通社区仅 22 个完成了本轮门槛判断",
        "这项审计尚未完成",
    ], errors)

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "audit_rows": len(rows),
    "completed_ordinary": 22,
    "ordinary_total": 252,
    "completion_pct": 8.73,
    "k0_post_target_cap": "0/0",
    "unlock_min_combined_karma": 50,
    "unlock_min_account_age_days": 7,
    "unlocked_k1_post_cap": "1/24h",
}, ensure_ascii=False, sort_keys=True))
