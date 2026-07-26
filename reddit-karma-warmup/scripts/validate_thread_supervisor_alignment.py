#!/usr/bin/env python3
"""Validate Reddit's scoped semantic alignment with generic task supervision."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(path: str, needles: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"{path}: missing {missing}")


defaults = json.loads(
    (ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8")
)
expected_chain = [
    {"model": "gpt-5.6-luna", "reasoning_effort": "high"},
    {"model": "gpt-5.6-terra", "reasoning_effort": "high"},
    {"model": "gpt-5.5", "reasoning_effort": "high"},
    {"model": "gpt-5.4", "reasoning_effort": "high"},
]
runtime = defaults["model_runtime"]
if runtime["fallback_chain"] != expected_chain:
    raise SystemExit("operation-defaults.json: invalid explicit model fallback chain")
expected_runtime = {
    "default_policy": "INHERIT_HOST_RUNTIME_NO_OVERRIDE",
    "explicit_user_override_required": True,
    "fallback_requires_explicit_user_consent": True,
    "request_preferred_pair_on_create": False,
    "request_preferred_pair_on_existing_task_dispatch": False,
    "unknown_launcher_model_policy": "KEEP_CURRENT_NO_DUPLICATE",
    "model_selection_is_liveness_or_replacement_evidence": False,
}
for key, expected in expected_runtime.items():
    if runtime.get(key) != expected:
        raise SystemExit(f"operation-defaults.json: model_runtime.{key} mismatch")

require(
    "references/thread-supervision-runtime.md",
    [
        "semantic task-health contract",
        "exact `task_id` plus `host_id`",
        "never treat a queued `clientThreadId` as a ready `threadId`",
        "omit model and reasoning overrides unless the current user command explicitly",
        "model choice\n  never proves liveness, delivery, archive state, or replacement eligibility",
        "LIVENESS_UNVERIFIED", "ROUTING_CAPABILITY_BLOCKED",
        "`DELIVERY_ACCEPTED` is the Reddit domain gate",
        "no-callback lane topology",
        "no shared version lock with the TikTok",
    ],
)
require(
    "references/runtime-and-setup.md",
    [
        "distinguish a ready `threadId` from a queued `clientThreadId`",
        "generic `thread-supervisor` Skill are not runtime dependencies",
        "The default\nruntime is inherited",
        "never create a\n   successor from unknown model metadata",
    ],
)
require(
    "references/model-runtime.md",
    [
        "The default is **inheritance**, not automatic migration",
        "unless the current user\nexplicitly supplies a model request",
        "No model request, accepted send, title, pin, or model readback is task-liveness",
        "Unknown model metadata always keeps the current\ntask",
    ],
)
require(
    "SKILL.md",
    [
        "independent account-scoped lane tasks",
        "[thread runtime](references/thread-supervision-runtime.md)",
        "An archived task is never healthy/reusable",
        "unknown liveness blocks that lane without",
    ],
)

print("thread supervisor semantic alignment validation passed")
