#!/usr/bin/env python3
"""Validate the scoped Thread Supervisor alignment contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(path: str, needles: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"{path}: missing {missing}")


require(
    "references/thread-supervision-runtime.md",
    [
        "thread-supervisor` revision `2026.07.14.5",
        "exact `task_id` plus `host_id`",
        "never treat a queued `clientThreadId` as a ready `threadId`",
        "omit model and reasoning overrides unless the user explicitly requested them",
        "never choose by recency alone",
        "A create response, readable summary, rename, or pin alone is not",
        "no-callback lane topology",
    ],
)
require(
    "references/runtime-and-setup.md",
    [
        "distinguish a ready `threadId` from a queued `clientThreadId`",
        "generic `thread-supervisor` Skill are not runtime dependencies",
        "exact ready task IDs, optional host IDs",
    ],
)
require(
    "SKILL.md",
    [
        "Five-Step Default Flow",
        "The generic `thread-supervisor` Skill is optional",
        "A queued `clientThreadId` is not ready",
    ],
)

print("thread supervisor alignment validation passed")
