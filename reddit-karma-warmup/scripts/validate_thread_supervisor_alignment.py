#!/usr/bin/env python3
"""Validate scoped task-routing alignment and the Reddit model fallback chain."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(path: str, needles: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"{path}: missing {missing}")


defaults = json.loads((ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8"))
expected = [
    {"model": "gpt-5.6-terra", "reasoning_effort": "high"},
    {"model": "gpt-5.6-luna", "reasoning_effort": "high"},
    {"model": "gpt-5.5", "reasoning_effort": "high"},
    {"model": "gpt-5.4", "reasoning_effort": "high"},
]
if defaults["model_runtime"]["fallback_chain"] != expected:
    raise SystemExit("operation-defaults.json: invalid model fallback chain")

require(
    "references/thread-supervision-runtime.md",
    [
        "thread-supervisor` revision `2026.07.14.5",
        "exact `task_id` plus `host_id`",
        "never treat a queued `clientThreadId` as a ready `threadId`",
        "gpt-5.6-terra/high",
        "gpt-5.6-luna/high",
        "gpt-5.5/high",
        "gpt-5.4/high",
        "Never recreate a healthy reusable task merely to change its model",
        "Never auto-unarchive it",
        "only when the user explicitly asks to resume that exact task",
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
        "first supported canonical fallback pair",
    ],
)
require(
    "SKILL.md",
    [
        "Five-Step Default Flow",
        "The generic `thread-supervisor` Skill is optional",
        "A queued `clientThreadId` is not ready",
        "gpt-5.6-terra/high -> gpt-5.6-luna/high -> gpt-5.5/high -> gpt-5.4/high",
    ],
)

print("thread supervisor alignment validation passed")
