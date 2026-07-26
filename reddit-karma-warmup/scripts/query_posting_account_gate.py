#!/usr/bin/env python3
"""Query the bundled subreddit posting-account gate audit."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


AUDIT = Path(__file__).resolve().parents[1] / "references" / "posting-account-gates-audit-2026-07-14.csv"


def normalize(value: str) -> str:
    value = value.strip()
    if value.lower().startswith("r/"):
        value = value[2:]
    return value.lower()


parser = argparse.ArgumentParser()
parser.add_argument("--subreddit", help="Exact subreddit name, with or without r/")
parser.add_argument("--summary", action="store_true", help="Print audit coverage")
args = parser.parse_args()

with AUDIT.open(newline="", encoding="utf-8-sig") as handle:
    rows = list(csv.DictReader(handle))

if args.summary:
    counts = Counter(row["audit_status"] for row in rows)
    completed = sum(
        counts[key]
        for key in ("verified_numeric", "verified_qualitative", "no_public_gate_found")
    )
    print(json.dumps({
        "rows": len(rows),
        "ordinary_total": len(rows) - counts["organization_deny"],
        "completed_ordinary": completed,
        "audit_status": dict(counts),
    }, ensure_ascii=False, sort_keys=True))

if args.subreddit:
    wanted = normalize(args.subreddit)
    matches = [row for row in rows if normalize(row["subreddit"]) == wanted]
    if not matches:
        raise SystemExit(json.dumps({"status": "NOT_FOUND", "subreddit": args.subreddit}, ensure_ascii=False))
    print(json.dumps(matches[0], ensure_ascii=False, sort_keys=True))

if not args.summary and not args.subreddit:
    parser.error("provide --summary or --subreddit")
