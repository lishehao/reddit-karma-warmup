#!/usr/bin/env python3
"""Prove critical recovery validators fail closed under representative mutations."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def inject_and_expect_failure(
    name: str,
    relative: str,
    old: str,
    new: str,
    validator: str,
) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="reddit-recovery-fi-") as td:
        clone = Path(td) / ROOT.name
        shutil.copytree(ROOT, clone)
        target = clone / relative
        body = target.read_text(encoding="utf-8")
        if old not in body:
            return {"case": name, "result": "HARNESS_NEEDLE_MISSING"}
        target.write_text(body.replace(old, new, 1), encoding="utf-8")
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(
            ["python3", str(clone / "scripts" / validator)],
            cwd=clone,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "case": name,
            "result": "BLOCKED" if result.returncode != 0 else "FAIL_OPEN",
            "validator": validator,
        }


cases = [
    inject_and_expect_failure(
        "chrome_outer_timeout_deflated",
        "references/operation-defaults.json",
        '"outer_timeout_ms": 120000',
        '"outer_timeout_ms": 30000',
        "validate_chrome_atomic_command_contract.py",
    ),
    inject_and_expect_failure(
        "chrome_boundary_bundle_enabled",
        "references/operation-defaults.json",
        '"browser_boundary_commands_per_cell": 1',
        '"browser_boundary_commands_per_cell": 3',
        "validate_chrome_atomic_command_contract.py",
    ),
    inject_and_expect_failure(
        "ambient_network_flag_made_required",
        "references/operation-defaults.json",
        '"ambient_network_flag_required": false',
        '"ambient_network_flag_required": true',
        "validate_chrome_atomic_command_contract.py",
    ),
    inject_and_expect_failure(
        "same_wake_cap_inflated",
        "references/operation-defaults.json",
        '"same_wake_recovery_cycle_cap": 2',
        '"same_wake_recovery_cycle_cap": 99',
        "validate_chrome_recovery_contract.py",
    ),
    inject_and_expect_failure(
        "uncertain_mutation_replay_enabled",
        "references/operation-defaults.json",
        '"uncertain_mutation_retry_allowed": false',
        '"uncertain_mutation_retry_allowed": true',
        "validate_chrome_recovery_contract.py",
    ),
    inject_and_expect_failure(
        "429_classification_detached",
        "references/chrome-network-recovery.md",
        "An explicit `429` enters `429_ROUND_PAUSE` below",
        "An explicit `429` enters an unspecified pause below",
        "validate_429_round_pause.py",
    ),
    inject_and_expect_failure(
        "deadline_clamp_removed",
        "references/chrome-network-recovery.md",
        "next_recovery_at=min(proposed_recovery_due, operation_stop_at)",
        "next_recovery_at=proposed_recovery_due",
        "validate_chrome_recovery_contract.py",
    ),
    inject_and_expect_failure(
        "partial_page_control_class_removed",
        "references/chrome-network-recovery.md",
        "classify `page_control_partial`",
        "classify an unspecified page failure",
        "validate_chrome_recovery_contract.py",
    ),
    inject_and_expect_failure(
        "scheduler_repair_removed",
        "references/scheduler-and-heartbeats.md",
        "scheduler_repair_required",
        "scheduler_state_unknown",
        "validate_chrome_recovery_contract.py",
    ),
    inject_and_expect_failure(
        "edge_reference_missing",
        "SKILL.md",
        "`references/chrome-recovery-edge-cases.md`",
        "`references/chrome-recovery-edge-cases-missing.md`",
        "validate_progressive_role_structure.py",
    ),
    inject_and_expect_failure(
        "click_only_submit_rule_removed",
        "references/chrome-atomic-command-runtime.md",
        "Run exactly one final click as the only browser-boundary command",
        "Run the final click together with verification",
        "validate_chrome_atomic_command_contract.py",
    ),
    inject_and_expect_failure(
        "controlled_input_readback_weakened",
        "references/operation-defaults.json",
        '"controlled_input_readback": "fresh_locator_evaluate_value_property"',
        '"controlled_input_readback": "action_ack_only"',
        "validate_chrome_atomic_command_contract.py",
    ),
    inject_and_expect_failure(
        "stale_locator_reuse_enabled",
        "references/operation-defaults.json",
        '"reuse_locator_after_accessible_name_change": false',
        '"reuse_locator_after_accessible_name_change": true',
        "validate_chrome_atomic_command_contract.py",
    ),
    inject_and_expect_failure(
        "fill_empty_treated_as_clear_proof",
        "references/chrome-atomic-command-runtime.md",
        'Do not use `fill(\"\")` as the sole proof',
        'Use `fill(\"\")` as sufficient proof',
        "validate_chrome_atomic_command_contract.py",
    ),
]

failures = [row for row in cases if row["result"] != "BLOCKED"]
if failures:
    raise SystemExit(json.dumps({"status": "FAIL", "failures": failures}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "fault_injections": len(cases),
    "all_mutations": "BLOCKED",
}, ensure_ascii=False, sort_keys=True))
