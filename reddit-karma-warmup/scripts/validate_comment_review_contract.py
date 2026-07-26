#!/usr/bin/env python3
"""Validate per-comment review, short-first copy, and qualitative Reddit voice."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(path: Path, needles: list[str], errors: list[str]) -> None:
    body = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{path.name}:{needle}")


errors: list[str] = []
defaults = json.loads((ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8"))
voice = defaults["voice"]
if voice["ordinary_comment_native_marker_frequency"] != "high":
    errors.append("ordinary_marker_frequency_not_high")
if voice["ordinary_comment_social_shorthand_frequency"] != "high_when_locally_supported":
    errors.append("social_shorthand_not_contextual_high")
if not voice["percentage_quota_is_forbidden"]:
    errors.append("percentage_quota_not_forbidden")
if voice["normal_marker_cap_per_item"] != 1 or voice["absolute_marker_cap_per_item"] != 2:
    errors.append("marker_density_caps")
mix = voice["length_mix"]
if mix["dominant"] != "micro_fragment_one_liner" or mix["short_tier_minimum"] != 7:
    errors.append("length_mix")

require(ROOT / "references" / "comments-playbook.md", [
    "For every individual comment",
    "fresh `per_comment_gate_id`",
    "current rule glance",
    "context_detail",
    "duplicate_to_avoid",
    "local_voice_sample",
    "micro, one-liner, and two-beat alternatives",
    "high-frequency locally supported Reddit/internet markers",
    "no percentage quota",
    "Normally use one marker, never more than two",
    "Never prewrite a cluster",
], errors)
require(ROOT / "references" / "outbound-copy-gate.md", [
    "PER_ITEM_COPY_GATE_REQUIRED=true",
    "cluster_copy_batching=forbidden",
    "qualitative session bands",
    "high when locally supported",
    "not a percentage quota",
    "short tiers dominate",
], errors)
require(ROOT / "references" / "reddit-us-voice-patterns.md", [
    "Current nearby replies and subreddit vocabulary always outrank it",
], errors)

outbound = (ROOT / "references" / "outbound-copy-gate.md").read_text(encoding="utf-8")
for forbidden in ("90-98%", "85-95%", "95-100%"):
    if forbidden in outbound:
        errors.append(f"forbidden_percentage_quota:{forbidden}")

if errors:
    print("COMMENT_REVIEW_CONTRACT=FAIL")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("COMMENT_REVIEW_CONTRACT=PASS")
print("copy_gate=PER_ITEM")
print("length=SHORT_FIRST_WITH_CONTEXTUAL_VARIATION")
print("voice=HIGH_FREQUENCY_LOCALLY_SUPPORTED")
print("marker_density=NORMAL_ONE_ABSOLUTE_MAX_TWO")
print("percentage_quota=FORBIDDEN")
