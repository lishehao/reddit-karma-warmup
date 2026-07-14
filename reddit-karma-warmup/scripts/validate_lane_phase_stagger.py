#!/usr/bin/env python3
"""Validate the intentionally small lane-stagger contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(path: str, needles: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"{path}: missing {missing}")


require(
    "references/scheduler-and-heartbeats.md",
    [
        "comments -> follow-up -> posts -> browsing -> presence",
        "10 minutes * mutation_phase_index",
        "2-4m",
        "next normal window",
        "No shared ledger, account lock, claim/complete protocol",
        "3-5m",
    ],
)
require(
    "references/default-operations-sop.md",
    [
        "mutation_phase_index=<0..n-1>",
        "initial_mutation_not_before=<start + 10m * phase index>",
        "missed_phase_policy=next_own_window",
        "first_due=now` starts read-only work immediately",
    ],
)
require(
    "references/launcher-playbook.md",
    [
        "mutation_phase_index",
        "initial_mutation_not_before=start + 10m * phase index",
        "phase_jitter_minutes=2-4",
    ],
)

print("lane phase stagger validation passed")
