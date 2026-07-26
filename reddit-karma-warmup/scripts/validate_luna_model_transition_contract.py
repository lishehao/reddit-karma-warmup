#!/usr/bin/env python3
"""Validate explicit-only model overrides (kept at the legacy filename)."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def decide_model_action(request_kind, available, current_task, migration_requested):
    if request_kind == "inherit":
        return "INHERIT_NO_OVERRIDE"
    if request_kind == "exact" and not available:
        return "MODEL_REQUEST_UNAVAILABLE_NO_SUBSTITUTION"
    if request_kind == "preferred_with_fallback" and available:
        return "REQUEST_USER_AUTHORIZED_FALLBACK_CHAIN"
    if migration_requested and current_task == "nonpreferred_confirmed":
        return "ONE_EXPLICIT_MIGRATION_GATE"
    return "REQUEST_EXACT_PAIR"


defaults = json.loads(read("references/operation-defaults.json"))
runtime = defaults["model_runtime"]
expected_chain = [
    {"model": "gpt-5.6-luna", "reasoning_effort": "high"},
    {"model": "gpt-5.6-terra", "reasoning_effort": "high"},
    {"model": "gpt-5.5", "reasoning_effort": "high"},
    {"model": "gpt-5.4", "reasoning_effort": "high"},
]
assert runtime["fallback_chain"] == expected_chain
assert runtime["default_policy"] == "INHERIT_HOST_RUNTIME_NO_OVERRIDE"
assert runtime["explicit_user_override_required"] is True
assert runtime["fallback_requires_explicit_user_consent"] is True
assert runtime["request_preferred_pair_on_create"] is False
assert runtime["request_preferred_pair_on_existing_task_dispatch"] is False
assert runtime["current_turn_in_place_switch_supported_by_skill"] is False
assert runtime["unknown_launcher_model_policy"] == "KEEP_CURRENT_NO_DUPLICATE"
assert runtime["model_selection_is_liveness_or_replacement_evidence"] is False

documents = {
    "SKILL.md": read("SKILL.md"),
    "agents/openai.yaml": read("agents/openai.yaml"),
    "model-runtime.md": read("references/model-runtime.md"),
    "runtime-and-setup.md": read("references/runtime-and-setup.md"),
    "thread-supervision-runtime.md": read("references/thread-supervision-runtime.md"),
    "launcher-playbook.md": read("references/launcher-playbook.md"),
}
joined = "\n".join(documents.values())
required = (
    "The default is **inheritance**, not automatic migration",
    "unless the current user\nexplicitly supplies a model request",
    "MODEL_INHERITED",
    "MODEL_REQUEST_UNAVAILABLE",
    "MODEL_REQUESTED_UNVERIFIED",
    "MODEL_FALLBACK_CONFIRMED",
    "do not create a successor merely to change models",
    "Unknown model metadata always keeps the current",
    "model choice\n  never proves liveness, delivery, archive state, or replacement eligibility",
    "Model choice is not a Chrome-recovery mechanism",
)
missing = [item for item in required if item not in joined]
assert not missing, missing

scenarios = {
    "default_new_task": decide_model_action("inherit", False, "unknown", False),
    "exact_pair_unavailable": decide_model_action("exact", False, "unknown", False),
    "preferred_with_fallback": decide_model_action("preferred_with_fallback", True, "unknown", False),
    "explicit_migration": decide_model_action("exact", True, "nonpreferred_confirmed", True),
}
assert scenarios == {
    "default_new_task": "INHERIT_NO_OVERRIDE",
    "exact_pair_unavailable": "MODEL_REQUEST_UNAVAILABLE_NO_SUBSTITUTION",
    "preferred_with_fallback": "REQUEST_USER_AUTHORIZED_FALLBACK_CHAIN",
    "explicit_migration": "ONE_EXPLICIT_MIGRATION_GATE",
}

print(json.dumps({
    "status": "PASS",
    "default": "INHERIT_HOST_RUNTIME_NO_OVERRIDE",
    "scenarios": scenarios,
}, ensure_ascii=False, sort_keys=True))
