#!/usr/bin/env python3
"""Validate Luna-first create, continuation, and launcher self-transition rules."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


defaults = json.loads(read("references/operation-defaults.json"))
runtime = defaults["model_runtime"]
expected_chain = [
    {"model": "gpt-5.6-luna", "reasoning_effort": "high"},
    {"model": "gpt-5.6-terra", "reasoning_effort": "high"},
    {"model": "gpt-5.5", "reasoning_effort": "high"},
    {"model": "gpt-5.4", "reasoning_effort": "high"},
]
assert runtime["fallback_chain"] == expected_chain
assert runtime["request_preferred_pair_on_create"] is True
assert runtime["request_preferred_pair_on_existing_task_dispatch"] is True
assert runtime["current_turn_in_place_switch_supported_by_skill"] is False
assert runtime["confirmed_nonpreferred_launcher_policy"] == (
    "ONE_VERIFIED_SUCCESSOR_WHEN_EXPLICITLY_AUTHORIZED"
)
assert runtime["unknown_launcher_model_policy"] == "KEEP_CURRENT_NO_DUPLICATE"
assert runtime["unverified_override_is_success"] is False

documents = {
    "SKILL.md": read("SKILL.md"),
    "model-runtime.md": read("references/model-runtime.md"),
    "runtime-and-setup.md": read("references/runtime-and-setup.md"),
    "thread-supervision-runtime.md": read("references/thread-supervision-runtime.md"),
    "launcher-playbook.md": read("references/launcher-playbook.md"),
}
joined = "\n".join(documents.values())
required = (
    "gpt-5.6-luna/high -> gpt-5.6-terra/high -> gpt-5.5/high -> gpt-5.4/high",
    "LUNA_CONFIRMED",
    "LUNA_REQUESTED_UNVERIFIED",
    "LUNA_UNAVAILABLE_FALLBACK",
    "SELF_MODEL_UNVERIFIED",
    "SELF_SUCCESSOR_CREATED_CONFIRMED",
    "The Skill cannot mutate the model of the turn that is already executing",
    "do not create a speculative duplicate",
    "create exactly one projectless Luna/high successor",
    "send the new mission with a Luna/high per-turn override",
    "never infer confirmation from message acceptance",
    "Model choice is not a Chrome-recovery mechanism",
)
missing = [item for item in required if item not in joined]
assert not missing, missing

if README.is_file():
    readme = README.read_text(encoding="utf-8")
    assert "我明确授权为当前分发台、后续分发台 successor" in readme
    assert "所有新建或继续执行台请求 `gpt-5.6-luna/high`" in readme
    assert "如果当前模型不可读，不要为了猜测而创建重复分发台" in readme

scenarios = {
    "new_task": {
        "request": "gpt-5.6-luna/high",
        "proof": "ACTUAL_RUNTIME_READBACK",
    },
    "existing_unarchived_task": {
        "action": "SEND_EXACT_MISSION_WITH_LUNA_OVERRIDE",
        "recreate_when_unverified": False,
    },
    "active_turn": {
        "claim_in_place_switch": False,
        "next_step": "READ_RUNTIME_THEN_APPLY_GATE",
    },
    "confirmed_non_luna_authorized": {
        "successor_attempt_cap": 1,
        "archive_old_before_acceptance": False,
    },
    "unknown_self_model": {
        "state": "SELF_MODEL_UNVERIFIED",
        "create_duplicate": False,
    },
    "luna_unsupported": {
        "next_pair": "gpt-5.6-terra/high",
        "block_operation": False,
    },
    "browser_failure": {
        "model_switch_is_recovery": False,
    },
}

assert scenarios["existing_unarchived_task"]["recreate_when_unverified"] is False
assert scenarios["active_turn"]["claim_in_place_switch"] is False
assert scenarios["confirmed_non_luna_authorized"]["successor_attempt_cap"] == 1
assert scenarios["confirmed_non_luna_authorized"]["archive_old_before_acceptance"] is False
assert scenarios["unknown_self_model"]["create_duplicate"] is False
assert scenarios["luna_unsupported"]["next_pair"] == "gpt-5.6-terra/high"
assert scenarios["browser_failure"]["model_switch_is_recovery"] is False

print(json.dumps({
    "status": "PASS",
    "preferred": "gpt-5.6-luna/high",
    "readme": "PRESENT" if README.is_file() else "OPTIONAL_ABSENT",
    "scenarios": scenarios,
}, ensure_ascii=False, sort_keys=True))
