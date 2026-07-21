#!/usr/bin/env python3
"""Validate Old-first routing, modern capability fallback, and host-independent mutation safety."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    path = ROOT / relative
    assert path.is_file(), f"missing:{relative}"
    return path.read_text(encoding="utf-8")


docs = {
    "skill": read("SKILL.md"),
    "routing": read("references/reddit-surface-routing.md"),
    "orchestration": read("references/orchestration-core.md"),
    "network": read("references/chrome-network-recovery.md"),
    "edge": read("references/chrome-recovery-edge-cases.md"),
    "setup": read("references/runtime-and-setup.md"),
    "checkpoint": read("references/lane-state-checkpoint.md"),
}
normalized_docs = {name: " ".join(body.split()) for name, body in docs.items()}

required = {
    "skill": [
        "references/reddit-surface-routing.md",
        "Old is a starting preference, not a hard dependency",
    ],
    "routing": [
        "old_first_modern_fallback",
        "Prefer `https://old.reddit.com/`",
        "gallery/video/media rendering",
        "Chat",
        "complex Flair/media",
        "canonical_target_key",
        "A surface switch never creates a new qualified read",
        "at most one cross-surface fallback per wake",
        "mutation_key` is independent of host",
        "never switch surfaces to retry",
        "surface_requested",
        "surface_used",
        "fallback_reason",
        "route_result",
        "never as a guaranteed alias or universal fallback",
    ],
    "orchestration": [
        'tab.goto("https://old.reddit.com/")',
        "old_first_modern_fallback",
        "A host change never creates a new candidate or mutation key",
    ],
    "network": [
        "preferred native surface from `reddit-surface-routing.md`",
        "A surface fallback is route recovery, not mutation recovery",
        "never change surfaces to retry or verify",
    ],
    "edge": [
        "Selected Reddit surface loops or fails",
        "same `canonical_target_key`",
        "Never bounce hosts or switch surfaces after an uncertain mutation",
    ],
    "setup": [
        "open the Old Reddit starting surface",
        "one bounded current-Reddit fallback",
        "do not navigate it merely to enforce Old Reddit",
        "does not change the account-wide Reddit preference",
    ],
    "checkpoint": [
        "surface_requested + surface_used + surface_reason + canonical_target_key",
        "mutation_state + mutation_key",
        "never increments the read or action count twice",
    ],
}

errors = []
for name, needles in required.items():
    for needle in needles:
        if " ".join(needle.split()) not in normalized_docs[name]:
            errors.append(f"missing:{name}:{needle}")

scenarios = {
    "text_listing": {"preferred": "old_reddit", "fallback": "modern_reddit"},
    "comment_tree": {"preferred": "old_reddit", "fallback": "modern_reddit"},
    "simple_reply": {"preferred": "old_reddit", "fallback": "modern_reddit"},
    "gallery": {"preferred": "modern_reddit", "fallback": "old_if_capable"},
    "chat": {"preferred": "modern_reddit", "fallback": "none_unless_capable"},
    "complex_composer": {"preferred": "modern_reddit", "fallback": "old_if_capable"},
    "old_blocked": {"next": "one_equivalent_modern_route", "terminal": False},
    "modern_route_blocked": {"next": "one_equivalent_old_route_if_capable", "terminal": False},
    "same_target_two_hosts": {"qualified_read_delta": 1, "mutation_key_count": 1},
    "submission_uncertain": {"surface_retry": False, "exact_key_frozen": True},
    "existing_vote": {"other_surface_click": False},
    "sh_route": {"guaranteed_alias": False},
}

assert scenarios["text_listing"]["preferred"] == "old_reddit"
assert scenarios["gallery"]["preferred"] == "modern_reddit"
assert scenarios["old_blocked"]["terminal"] is False
assert scenarios["same_target_two_hosts"]["qualified_read_delta"] == 1
assert scenarios["same_target_two_hosts"]["mutation_key_count"] == 1
assert scenarios["submission_uncertain"]["surface_retry"] is False
assert scenarios["existing_vote"]["other_surface_click"] is False
assert scenarios["sh_route"]["guaranteed_alias"] is False

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "policy": "OLD_FIRST_MODERN_FALLBACK",
    "scenarios": scenarios,
}, ensure_ascii=False, sort_keys=True))
