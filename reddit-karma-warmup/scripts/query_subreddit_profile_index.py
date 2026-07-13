#!/usr/bin/env python3
"""Query the tagged subreddit index for an account direction."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from build_subreddit_profile_index import TAG_RULES, matched_tags


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "references" / "subreddit-profile-index.csv"


def tag_set(value: str) -> set[str]:
    return {item for item in value.split(";") if item}


def select_diverse(items: list[dict], limit: int) -> list[dict]:
    quotas = {"direct": 6, "adjacent": 3, "exploration": 3}
    selected = []
    used = set()
    for match_type, quota in quotas.items():
        for item in (candidate for candidate in items if candidate["match_type"] == match_type):
            if len([row for row in selected if row["match_type"] == match_type]) >= quota or len(selected) >= limit:
                break
            selected.append(item)
            used.add(item["subreddit"].lower())
    for item in items:
        if len(selected) >= limit:
            break
        if item["subreddit"].lower() not in used:
            selected.append(item)
            used.add(item["subreddit"].lower())
    return selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--direction", required=True, help="Account direction or profile pillars")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--min-weekly-visitors", type=int, default=5_000)
    parser.add_argument("--include-traffic-probes", action="store_true")
    args = parser.parse_args()

    query_tags = set()
    for rules in (TAG_RULES["topic_tags"], TAG_RULES["audience_tags"], TAG_RULES["need_tags"]):
        query_tags.update(matched_tags(args.direction, rules))
    if not query_tags:
        raise SystemExit("No canonical profile tags matched the supplied direction")

    candidates = []
    with INDEX.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["launcher_state"] not in {"candidate", "research_only"}:
                continue
            visitors = int(row["weekly_visitors"] or 0)
            traffic_state = row["traffic_state"]
            if traffic_state == "below_floor" or (visitors and visitors < args.min_weekly_visitors):
                continue
            if traffic_state in {"unknown", "stale"} and not args.include_traffic_probes:
                continue
            topic = tag_set(row["topic_tags"])
            audience = tag_set(row["audience_tags"])
            needs = tag_set(row["need_tags"])
            direct = query_tags & topic
            audience_match = query_tags & audience
            need_match = query_tags & needs
            if not (direct or audience_match or need_match):
                continue
            score = 5 * len(direct) + 3 * len(audience_match) + 2 * len(need_match)
            score += 3 if row["tier"] == "B" else 2 if row["tier"] == "B+" else 0
            score += 2 if row["comment_route"] == "default" else 1 if row["comment_route"] == "conditional" else 0
            if not score:
                continue
            match_type = "direct" if len(direct) >= 2 else "adjacent" if direct else "exploration"
            candidates.append(
                {
                    "subreddit": row["subreddit"],
                    "score": score,
                    "matched_tags": sorted(direct | audience_match | need_match),
                    "match_type": match_type,
                    "tier": row["tier"],
                    "comment_route": row["comment_route"],
                    "post_route": row["post_route"],
                    "launcher_state": row["launcher_state"],
                    "traffic_state": traffic_state,
                    "weekly_visitors": visitors or None,
                    "next_gate": "live_traffic_check" if traffic_state in {"unknown", "stale"} else "exact_rule_and_account_preflight",
                }
            )

    candidates.sort(key=lambda item: (item["score"], item["weekly_visitors"] or 0), reverse=True)
    action_candidates = [item for item in candidates if item["launcher_state"] == "candidate"]
    research_candidates = [item for item in candidates if item["launcher_state"] == "research_only"]
    passed = [item for item in action_candidates if item["traffic_state"] == "pass"]
    probes = [item for item in action_candidates if item["traffic_state"] in {"unknown", "stale"}]
    research_matches = [item for item in research_candidates if item["traffic_state"] == "pass"]
    result = {
        "direction": args.direction,
        "query_tags": sorted(query_tags),
        "minimum_weekly_visitors": args.min_weekly_visitors,
        "operating_shortlist": select_diverse(passed, args.limit),
        "traffic_probe_queue": select_diverse(probes, args.limit) if args.include_traffic_probes else [],
        "research_matches": select_diverse(research_matches, args.limit),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
