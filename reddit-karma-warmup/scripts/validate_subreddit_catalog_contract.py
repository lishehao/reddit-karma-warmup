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
    if len(rows) < 174:
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
        if "operating_shortlist" not in payload or "traffic_probe_queue" not in payload:
            errors.append("query output missing shortlist buckets")
        for row in payload.get("operating_shortlist", []):
            if (row["weekly_visitors"] or 0) < 5_000:
                errors.append(f"shortlist below floor: {row['subreddit']}")
        if len(payload.get("traffic_probe_queue", [])) > 12:
            errors.append("traffic probe queue exceeds limit")

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
    print("traffic_floor=5000_WEEKLY_VISITORS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
