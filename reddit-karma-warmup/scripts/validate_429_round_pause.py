#!/usr/bin/env python3
"""Validate the explicit 429 one-round pause contract by semantic section."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


errors: list[str] = []


def require_text(label: str, text: str, needles: list[str]) -> None:
    missing = [needle for needle in needles if needle not in text]
    if missing:
        errors.append(f"{label}:missing:{missing}")


recovery = (ROOT / "references" / "chrome-network-recovery.md").read_text(encoding="utf-8")
heading = "### Explicit 429 Round Pause"
if recovery.count(heading) != 1:
    errors.append(f"recovery:heading_count:{recovery.count(heading)}")
    classification = recovery
    section = ""
    generic_loop = ""
else:
    classification, tail = recovery.split(heading, 1)
    section, separator, generic_loop = tail.partition("`attempt 0` is the original failure.")
    if not separator:
        errors.append("recovery:missing_generic_loop_boundary")

require_text(
    "recovery_classification",
    classification,
    [
        "An explicit `429` enters `429_ROUND_PAUSE` below",
    ],
)
require_text(
    "recovery_429_section",
    section,
    [
        "Perform no more Reddit navigation, reload, comment, reply, post, vote, Join, profile edit, or submit attempt",
        "Compute `resume_due` as the later of this lane's next normal round and any explicit `Retry-After`/displayed expiry",
        "next_due=min(resume_due, operation_stop_at)",
        "Never delete, deactivate, or mark the mission complete",
        "Do not create cross-task locks, callbacks, or pause messages",
    ],
)
require_text(
    "recovery_generic_loop",
    generic_loop,
    [
        "Explicit `429` bypasses every same-wake cycle and uses `429_ROUND_PAUSE`",
        "round_paused_429",
    ],
)

scheduler = (ROOT / "references" / "scheduler-and-heartbeats.md").read_text(encoding="utf-8")
require_text(
    "scheduler",
    scheduler,
    [
        "Explicit HTTP `429`/`Too Many Requests` is a round boundary",
        "Do not delete or pause the Heartbeat",
        "do not create a catch-up burst",
    ],
)

edge = (ROOT / "references" / "chrome-recovery-edge-cases.md").read_text(encoding="utf-8")
require_text(
    "edge_matrix",
    edge,
    [
        "HTTP `429` or `Too Many Requests`",
        "Enter `429_ROUND_PAUSE`; no same-wake probe, reload, navigation, or mutation",
        "Respect `Retry-After` and preserve the mission/Heartbeat",
    ],
)

skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
require_text(
    "skill",
    skill,
    [
        "HTTP `429` ends the current wake",
        "preserves checkpoint/mission/Heartbeat",
    ],
)

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "classification": "429_ROUND_PAUSE",
    "same_wake_actions": 0,
    "deadline_clamp": True,
}, ensure_ascii=False, sort_keys=True))
