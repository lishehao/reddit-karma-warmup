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
            "comment_shortlist",
            "post_reference_shortlist",
            "reference_rows_assessed",
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

    lane_payloads = {}
    for lane, alias in (("comments", "comment_shortlist"), ("posts", "post_reference_shortlist")):
        query = subprocess.run(
            [
                sys.executable,
                str(QUERY),
                "--direction",
                "年轻人 泛娱乐 轻社交 3D AR 游戏 地点体验",
                "--lane",
                lane,
                "--reference-sweep-limit",
                "100",
                "--limit",
                "20",
                "--include-traffic-probes",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if query.returncode:
            errors.append(f"{lane} query failed: {query.stderr.strip()}")
            continue
        payload = json.loads(query.stdout)
        lane_payloads[lane] = payload
        required_keys = {
            "operating_shortlist",
            alias,
            "reference_sweep",
            "catalog_rows_scanned",
            "catalog_matches_assessed",
            "traffic_probe_queue",
            "research_matches",
        }
        if not required_keys <= payload.keys():
            errors.append(f"{lane} query output missing shortlist buckets")
        if len(payload.get("reference_sweep", [])) > 100:
            errors.append(f"{lane} reference sweep exceeds 100")
        if payload.get("catalog_rows_scanned") != len(rows):
            errors.append(f"{lane} catalog scan did not cover all indexed rows")
        for row in payload.get("reference_sweep", []):
            if row["launcher_state"] != "candidate":
                errors.append(f"{lane} reference sweep contains non-candidate: {row['subreddit']}")
            if not {"rule_friction_score", "rule_friction_band", "rule_friction_reasons"} <= row.keys():
                errors.append(f"{lane} reference row missing friction fields: {row['subreddit']}")
        for row in payload.get("operating_shortlist", []):
            if (row["weekly_visitors"] or 0) < 5_000:
                errors.append(f"{lane} shortlist below floor: {row['subreddit']}")
            if lane == "comments" and row["comment_route"] not in {"default", "conditional"}:
                errors.append(f"comment shortlist route closed: {row['subreddit']}")
            if lane == "posts" and row["post_route"] != "conditional":
                errors.append(f"post shortlist route closed: {row['subreddit']}")
        if len(payload.get("traffic_probe_queue", [])) > 20:
            errors.append(f"{lane} traffic probe queue exceeds limit")
        for row in payload.get("research_matches", []):
            if row["launcher_state"] != "research_only":
                errors.append(f"{lane} research bucket contains action candidate: {row['subreddit']}")
            if row["comment_route"] != "research-only" or row["post_route"] != "closed":
                errors.append(f"{lane} research bucket contains open action route: {row['subreddit']}")

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
    if lane_payloads:
        print("lane_prefilter=COMMENTS_AND_POSTS")
        print("reference_sweep_cap=100")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
