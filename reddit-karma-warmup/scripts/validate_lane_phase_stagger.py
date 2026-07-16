#!/usr/bin/env python3
"""Validate the intentionally small lane-stagger contract."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
defaults = json.loads((ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8"))
if defaults["scheduler"]["first_mutation_phase_step_minutes"] != 10:
    raise SystemExit("scheduler phase step mismatch")
if defaults["scheduler"]["phase_jitter_minutes"] != [2, 4]:
    raise SystemExit("scheduler jitter mismatch")


def require(path: str, needles: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"{path}: missing {missing}")


require(
    "references/scheduler-and-heartbeats.md",
    [
        "comments -> follow-up -> posts -> browsing -> presence",
        "scheduler.first_mutation_phase_step_minutes * mutation_phase_index",
        "scheduler.phase_jitter_minutes",
        "next normal window",
        "No shared ledger, account lock, claim/complete protocol",
    ],
)
require(
    "references/default-operations-sop.md",
    [
        "first_due=now + mutation_phase_index + initial_mutation_not_before",
    ],
)
require(
    "references/launcher-playbook.md",
    [
        "mutation_phase_index",
        "initial_mutation_not_before=<resolved scheduler phase step * phase index>",
        "phase_jitter_minutes=<resolved scheduler range>",
    ],
)

print("lane phase stagger validation passed")
