#!/usr/bin/env python3
"""Validate the tagged discovery catalog and launcher retrieval contract."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "references" / "subreddit-profile-index.csv"
EXPANSION = ROOT / "references" / "subreddit-catalog-expansion-2026-07-14.csv"
SNAPSHOT = ROOT / "references" / "reddit-community-search-snapshot-2026-07-14.json"
QUERY = ROOT / "scripts" / "query_subreddit_profile_index.py"


def require(path: Path, needles: list[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [f"{path.name}: missing {needle!r}" for needle in needles if needle not in text]


def main() -> int:
    errors = []
    checks = {
        ROOT / "SKILL.md": [
            "subreddit-catalog-taxonomy.md",
            "subreddit-profile-index.csv",
            "cached `>=5K` weekly-visitor matches",
        ],
        ROOT / "references" / "account-direction.md": [
            "direction_tags",
            "query_subreddit_profile_index.py",
            "operating_shortlist",
            "traffic_probe_queue",
            "below `5,000` never enters either list",
        ],
        ROOT / "references" / "launcher-playbook.md": [
            "subreddit_shortlist",
            "traffic_probe_queue",
            "at least `5,000` weekly visitors",
        ],
        ROOT / "references" / "subreddit-catalog-taxonomy.md": [
            "Two-Layer Model",
            "The default discovery floor is `5,000` weekly visitors",
            "Catalog-only expansion does not require a full rule audit",
            "subreddit-catalog-expansion-2026-07-14.csv",
            "traffic_verified",
        ],
    }
    for path, needles in checks.items():
        if not path.exists():
            errors.append(f"missing file: {path}")
        else:
            errors.extend(require(path, needles))

    with INDEX.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    keys = [row["subreddit"].lower() for row in rows]
    if len(rows) < 254:
        errors.append(f"catalog too small: {len(rows)}")
    if len(keys) != len(set(keys)):
        errors.append("duplicate subreddit keys")
    for field in ("topic_tags", "audience_tags", "need_tags"):
        missing = [row["subreddit"] for row in rows if not row[field]]
        if missing:
            errors.append(f"missing {field}: {missing}")
    for row in rows:
        if row["traffic_state"] == "below_floor" and int(row["weekly_visitors"] or 0) >= 5_000:
            errors.append(f"bad below-floor state: {row['subreddit']}")
        if row["traffic_state"] == "pass" and int(row["weekly_visitors"] or 0) < 5_000:
            errors.append(f"bad pass state: {row['subreddit']}")

    with EXPANSION.open(encoding="utf-8", newline="") as handle:
        expansion_rows = list(csv.DictReader(handle))
    if len(expansion_rows) != 80:
        errors.append(f"unexpected 2026-07-14 expansion size: {len(expansion_rows)}")
    for row in expansion_rows:
        if int(row["weekly_visitors"] or 0) < 5_000:
            errors.append(f"expansion below traffic floor: {row['subreddit']}")
        if row["launcher_state"] != "research_only" or row["comment_route"] != "research-only":
            errors.append(f"expansion improperly action-enabled: {row['subreddit']}")
        if row["post_route"] != "closed" or row["product_route"] != "closed":
            errors.append(f"expansion publishing route open: {row['subreddit']}")

    snapshot_rows = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if len(snapshot_rows) != 141:
        errors.append(f"unexpected traffic snapshot size: {len(snapshot_rows)}")

    query = subprocess.run(
        [
            sys.executable,
            str(QUERY),
            "--direction",
            "年轻人 泛娱乐 轻社交 3D AR 游戏 地点体验",
            "--limit",
            "12",
            "--include-traffic-probes",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if query.returncode:
        errors.append(f"query failed: {query.stderr.strip()}")
    else:
        payload = json.loads(query.stdout)
        if not {"operating_shortlist", "traffic_probe_queue", "research_matches"} <= payload.keys():
            errors.append("query output missing shortlist buckets")
        for row in payload.get("operating_shortlist", []):
            if (row["weekly_visitors"] or 0) < 5_000:
                errors.append(f"shortlist below floor: {row['subreddit']}")
        if len(payload.get("traffic_probe_queue", [])) > 12:
            errors.append("traffic probe queue exceeds limit")
        for row in payload.get("research_matches", []):
            if row["launcher_state"] != "research_only":
                errors.append(f"research bucket contains action candidate: {row['subreddit']}")
            if row["comment_route"] != "research-only" or row["post_route"] != "closed":
                errors.append(f"research bucket contains open action route: {row['subreddit']}")

    if errors:
        print("SUBREDDIT_CATALOG_CONTRACT=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("SUBREDDIT_CATALOG_CONTRACT=PASS")
    print(f"catalog_rows={len(rows)}")
    print(f"launcher_candidates={sum(row['launcher_state'] == 'candidate' for row in rows)}")
    print(f"traffic_pass={sum(row['traffic_state'] == 'pass' for row in rows)}")
    print(f"traffic_unknown={sum(row['traffic_state'] == 'unknown' for row in rows)}")
    print(f"traffic_expansion={len(expansion_rows)}_RESEARCH_ONLY")
    print("traffic_floor=5000_WEEKLY_VISITORS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
