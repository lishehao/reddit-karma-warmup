#!/usr/bin/env python3
"""Validate canonical targets, hard reads, vote semantics, and durable state."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULTS_PATH = ROOT / "references" / "operation-defaults.json"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def resolve_vote(intensity: str, target=None, cap=None):
    defaults = json.loads(DEFAULTS_PATH.read_text(encoding="utf-8"))
    default_cap = defaults["votes"]["caps_by_intensity"][intensity]
    if target is None:
        return {"mode": "opportunity", "target": None, "cap": default_cap, "mismatch": False}
    resolved_cap = target if cap is None else cap
    return {
        "mode": "hard",
        "target": target,
        "cap": resolved_cap,
        "mismatch": target > resolved_cap,
    }


errors = []
defaults = json.loads(DEFAULTS_PATH.read_text(encoding="utf-8"))

expected_chain = [
    {"model": "gpt-5.6-luna", "reasoning_effort": "high"},
    {"model": "gpt-5.5", "reasoning_effort": "high"},
    {"model": "gpt-5.4", "reasoning_effort": "high"},
]
if defaults["model_runtime"]["fallback_chain"] != expected_chain:
    errors.append("model_fallback_chain")

expected_comments = {
    "low": (3, 4, 9),
    "standard": (5, 6, 15),
    "high": (8, 10, 24),
}
for intensity, expected in expected_comments.items():
    row = defaults["comments"][intensity]
    actual = (row["action_target_per_hour"], row["action_cap_per_hour"], row["qualified_read_target"])
    if actual != expected:
        errors.append(f"comments_{intensity}:{actual}")

expected_browse_reads = {"low": 12, "standard": 25, "high": 50}
for intensity, expected in expected_browse_reads.items():
    if defaults["browsing"][intensity]["qualified_read_target"] != expected:
        errors.append(f"browse_reads_{intensity}")

votes = defaults["votes"]
if votes["default_target"] is not None or votes["default_target_mode"] != "opportunity":
    errors.append("default_vote_must_be_opportunity_without_target")
if votes["explicit_target_mode"] != "hard":
    errors.append("explicit_vote_target_not_hard")
if votes["caps_by_intensity"] != {"low": 1, "standard": 1, "high": 2}:
    errors.append("vote_caps")
if not votes["never_scan_only_for_default_vote"]:
    errors.append("default_vote_hunting_not_forbidden")

voice = defaults["voice"]
if voice["ordinary_comment_native_marker_frequency"] != "high":
    errors.append("native_marker_frequency")
if voice["ordinary_comment_social_shorthand_frequency"] != "high_when_locally_supported":
    errors.append("social_shorthand_frequency")
if not voice["percentage_quota_is_forbidden"]:
    errors.append("percentage_quota_not_forbidden")
if (voice["normal_marker_cap_per_item"], voice["absolute_marker_cap_per_item"]) != (1, 2):
    errors.append("marker_caps")

required = {
    "SKILL.md": [
        "`qualified_read_target` is a hard completion objective",
        "Voting has no default count target",
        "Only a user-supplied vote count creates a hard vote target",
        "gpt-5.6-luna/high -> gpt-5.5/high -> gpt-5.4/high",
    ],
    "references/default-operations-sop.md": [
        "action_remaining == 0",
        "qualified_read_remaining == 0 or required_surface_sweep == complete",
        "Default voting is opportunity-only",
        "Do not continue or widen scanning solely to cast a default vote",
    ],
    "references/comments-playbook.md": [
        "separate hard completion conditions",
        "Default voting is opportunity-only",
        "high-frequency locally supported Reddit/internet markers",
    ],
    "references/posts-playbook.md": [
        "live deep-read target is a hard research objective",
        "Default voting is opportunity-only",
    ],
    "references/browse-vote-playbook.md": [
        "browsing.<intensity>.qualified_read_target",
        "default `vote_target_mode=opportunity`",
        "vote cap is always a hard ceiling",
    ],
    "references/lane-state-checkpoint.md": [
        "lane-state/<username>/<lane>/<self_task_id>.json",
        "qualified_read_remaining",
        "checkpoint_path",
        "submission_uncertain",
    ],
}
for relative, needles in required.items():
    body = read(relative)
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{relative}:{needle}")

for obsolete in ("references/proactive-playbook.md", "references/twelve-hour-ops-template.md"):
    if (ROOT / obsolete).exists():
        errors.append(f"obsolete_file:{obsolete}")

default_vote = resolve_vote("standard")
if default_vote != {"mode": "opportunity", "target": None, "cap": 1, "mismatch": False}:
    errors.append(f"default_vote_scenario:{default_vote}")
explicit_vote = resolve_vote("standard", target=2)
if explicit_vote != {"mode": "hard", "target": 2, "cap": 2, "mismatch": False}:
    errors.append(f"explicit_vote_scenario:{explicit_vote}")
capped_vote = resolve_vote("standard", target=2, cap=1)
if capped_vote != {"mode": "hard", "target": 2, "cap": 1, "mismatch": True}:
    errors.append(f"capped_vote_scenario:{capped_vote}")

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "model_fallback": "5.6_LUNA_HIGH__5.5_HIGH__5.4_HIGH",
    "reading": "HARD_OBJECTIVE",
    "default_voting": "OPPORTUNITY_ONLY",
    "vote_caps": "HARD",
    "explicit_vote_target": "HARD",
    "voice": "HIGH_FREQUENCY_NO_PERCENTAGE_QUOTA",
    "state": "DURABLE_PER_ACCOUNT_LANE_TASK_CHECKPOINT",
}, ensure_ascii=False, sort_keys=True))
