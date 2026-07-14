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
    parser.add_argument("--lane", choices=("all", "comments", "posts"), default="all")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--reference-sweep-limit", type=int, default=100)
    parser.add_argument("--min-weekly-visitors", type=int, default=5_000)
    parser.add_argument("--include-traffic-probes", action="store_true")
    args = parser.parse_args()

    query_tags = set()
    for rules in (TAG_RULES["topic_tags"], TAG_RULES["audience_tags"], TAG_RULES["need_tags"]):
        query_tags.update(matched_tags(args.direction, rules))
    if not query_tags:
        raise SystemExit("No canonical profile tags matched the supplied direction")

    candidates = []
    catalog_rows_scanned = 0
    with INDEX.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            catalog_rows_scanned += 1
            if row["launcher_state"] not in {"candidate", "research_only"}:
                continue
            if args.lane == "comments" and row["comment_route"] not in {"default", "conditional"}:
                continue
            if args.lane == "posts" and row["post_route"] != "conditional":
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
            if args.lane in {"all", "comments"}:
                score += 4 if row["comment_route"] == "default" else 2 if row["comment_route"] == "conditional" else 0
            if args.lane == "posts":
                score += 3 if row["post_route"] == "conditional" else 0

            risk_tags = tag_set(row["risk_tags"])
            friction_penalties = {
                "approval_gate": 8,
                "megathread_gate": 6,
                "account_gate": 4,
                "topic_purity": 3,
                "promotion_restricted": 2,
            }
            friction_penalty = sum(friction_penalties.get(tag, 0) for tag in risk_tags)
            score -= friction_penalty
            rule_friction_score = max(0, 20 - friction_penalty)
            rule_friction_band = "low" if friction_penalty <= 3 else "medium" if friction_penalty <= 8 else "high"
            if score <= 0:
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
                    "rule_friction_score": rule_friction_score,
                    "rule_friction_band": rule_friction_band,
                    "rule_friction_reasons": sorted(tag for tag in risk_tags if tag in friction_penalties),
                    "launcher_state": row["launcher_state"],
                    "traffic_state": traffic_state,
                    "weekly_visitors": visitors or None,
                    "next_gate": "live_traffic_check" if traffic_state in {"unknown", "stale"} else "exact_rule_and_account_preflight",
                }
            )

    candidates.sort(
        key=lambda item: (item["score"], item["rule_friction_score"], item["weekly_visitors"] or 0),
        reverse=True,
    )
    action_candidates = [item for item in candidates if item["launcher_state"] == "candidate"]
    research_candidates = [item for item in candidates if item["launcher_state"] == "research_only"]
    passed = [item for item in action_candidates if item["traffic_state"] == "pass"]
    probes = [item for item in action_candidates if item["traffic_state"] in {"unknown", "stale"}]
    research_matches = [item for item in research_candidates if item["traffic_state"] == "pass"]
    operating_shortlist = select_diverse(passed, args.limit)
    result = {
        "direction": args.direction,
        "lane": args.lane,
        "query_tags": sorted(query_tags),
        "minimum_weekly_visitors": args.min_weekly_visitors,
        "catalog_rows_scanned": catalog_rows_scanned,
        "catalog_matches_assessed": len(candidates),
        "reference_sweep": action_candidates[: max(0, min(args.reference_sweep_limit, 100))],
        "operating_shortlist": operating_shortlist,
        "traffic_probe_queue": select_diverse(probes, args.limit) if args.include_traffic_probes else [],
        "research_matches": select_diverse(research_matches, args.limit),
    }
    if args.lane == "comments":
        result["comment_shortlist"] = operating_shortlist
    elif args.lane == "posts":
        result["post_reference_shortlist"] = operating_shortlist
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
