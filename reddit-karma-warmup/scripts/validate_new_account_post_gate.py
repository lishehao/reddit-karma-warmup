#!/usr/bin/env python3
"""Validate K0 post lock, K1 unlock, and account-gate audit coverage."""

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

defaults = json.loads((ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8"))
posts = defaults["posts"]
if (posts["k0_action_target"], posts["k0_action_cap"]) != (0, 0):
    errors.append("k0_post_target_cap")
if posts["main_post_unlock_min_combined_karma"] != 50:
    errors.append("unlock_karma")
if posts["main_post_unlock_min_account_age_days"] != 7:
    errors.append("unlock_age")
if posts["k1_rolling_24h_cap"] != 1:
    errors.append("k1_rolling_cap")

require(ROOT / "references" / "new-account-bootstrap.md", [
    "K0 posts from `posts.k0_action_*`",
    "Every K0 account publishes no main post",
    "## Main Post Unlock",
    "posts.main_post_unlock_min_combined_karma",
    "posts.main_post_unlock_min_account_age_days",
    "posts.main_post_unlock_min_visible_comments",
    "posts.main_post_unlock_min_eligible_communities",
    "`unknown`, `blocked`, and `organization_deny` are closed for K0 main posts",
], errors)
require(ROOT / "references" / "posts-playbook.md", [
    "K0 is always `research_preflight_only` with `posts.k0_action_*`",
    "K1 requires `main_post_unlock=passed`",
    "posts.k1_rolling_24h_cap",
], errors)
require(ROOT / "references" / "default-operations-sop.md", [
    "K0 receives a post research/preflight mission with action target/cap `0/0`",
    "main_post_unlock",
    "posting-gate rows",
], errors)
require(ROOT / "references" / "posting-account-gates-audit-status.md", [
    "completed ordinary gate reviews: `22/252` (`8.73%`)",
    "The audit is not complete",
    "Blank fields mean not publicly confirmed, not zero",
], errors)
if README.exists():
    require(README, [
        "主帖目标/上限固定为 `0/0`",
        "至少 50 combined Karma",
        "K1 解锁后仍最多每 24 小时 1 篇",
    ], errors)

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "audit_rows": len(rows),
    "k0_posts": "LOCKED_0_0",
    "unlock": "50_KARMA_7D_PLUS_LIVE_GATES",
    "k1_cap": "ONE_PER_ROLLING_24H",
}, ensure_ascii=False, sort_keys=True))
