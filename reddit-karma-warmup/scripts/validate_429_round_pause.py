#!/usr/bin/env python3
"""Validate the explicit 429 one-round pause contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(path: str, needles: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"{path}: missing {missing}")


require(
    "references/chrome-network-recovery.md",
    [
        "429_ROUND_PAUSE",
        "Perform no more Reddit navigation, reload, comment, reply, post, vote, Join, profile edit, or submit attempt",
        "later of this lane's next normal round and any explicit `Retry-After`/displayed expiry",
        "Never delete, deactivate, or mark the mission complete",
        "Do not create cross-task locks, callbacks, or pause messages",
        "round_paused_429",
    ],
)
require(
    "references/scheduler-and-heartbeats.md",
    [
        "Explicit HTTP `429`/`Too Many Requests` is a round boundary",
        "Do not delete or pause the Heartbeat",
        "do not create a catch-up burst",
    ],
)
require(
    "SKILL.md",
    [
        "Explicit HTTP `429`/`Too Many Requests` ends every Reddit action in the current wake",
        "it never deletes the mission or Heartbeat",
    ],
)

print("429 round pause validation passed")
