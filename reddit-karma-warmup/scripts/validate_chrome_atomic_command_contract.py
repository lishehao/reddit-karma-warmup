#!/usr/bin/env python3
"""Validate Chrome command granularity, timeout, and ambient-network handling."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"
defaults = json.loads((ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8"))
runtime = defaults.get("chrome_command_runtime", {})
errors: list[str] = []

expected = {
    "outer_timeout_ms": 120000,
    "locator_action_timeout_ms": 90000,
    "browser_boundary_commands_per_cell": 1,
    "slow_success_threshold_ms": 20000,
    "ambient_network_disable_env": "BROWSER_USE_DISABLE_AMBIENT_NETWORK",
    "ambient_network_disable_value": "1",
    "ambient_network_flag_required": False,
    "bundle_wait_with_mutation": False,
    "bundle_observation_with_interaction": False,
    "preferred_interaction_surface": "fresh_dom_cua_node",
    "dom_cua_node_id_type": "string",
    "controlled_input_select_all_macos": "Meta+A",
    "controlled_input_select_all_other": "Control+A",
    "controlled_input_delete_key": "Backspace",
    "controlled_input_readback": "shadow_aware_live_value_projection",
    "controlled_input_fallback_readback": "fresh_visible_dom_exact_text",
    "locator_backend_deadline_class": "locator_backend_deadline",
    "locator_backend_retry_after_deadline": 0,
    "reuse_locator_after_accessible_name_change": False,
    "trust_action_ack_without_readback": False,
}
for key, value in expected.items():
    if runtime.get(key) != value:
        errors.append(f"default:{key}:{runtime.get(key)!r}")

required = {
    "SKILL.md": [
        "chrome-atomic-command-runtime.md",
        "First creation is three atomic calls",
        "The submit wait, one click, and readback are three separate operations",
        "A Chrome command that succeeds slowly is not a failure",
    ],
    "references/chrome-atomic-command-runtime.md": [
        "Every `node_repl` cell that crosses the Chrome browser boundary",
        "at most `browser_boundary_commands_per_cell` awaited browser-boundary command",
        "never bundle:",
        "fixed wait + mutation click",
        "mutation click + result verification",
        "Do not call `playwright.waitForTimeout` in the submit cell",
        "Run exactly one final click as the only browser-boundary command",
        "set `submission_uncertain`, quarantine the exact action, and never replay it",
        "classify `ambient_network_degraded`",
        "optional latency optimization, not a Skill dependency",
        "Classify `page_control_partial` only when one atomic command receives no acknowledgement after the full outer timeout",
        "Controlled Text Inputs",
        "preserve `node_id` as a string",
        "shadowRoot.activeElement",
        "locator_backend_deadline",
        "Do not use `fill(\"\")` as the sole proof",
    ],
    "references/orchestration-core.md": [
        "three-call creation transaction",
        "as its only browser-boundary command",
        "Run the remaining pre-submit wait outside the browser cell",
    ],
    "references/interaction-pacing.md": [
        "Never bundle that wait with click, fill, type, vote, or submit",
        "Every click, fill/type, and result observation is a separate `node_repl` cell",
    ],
    "references/comments-playbook.md": [
        "local wait, one click-only submit cell, and one separate targeted result read",
        "Never combine typing, submit, or verification",
        "verify the exact live value through the focused control's open Shadow DOM before Double-Check B",
    ],
    "references/chrome-network-recovery.md": [
        "configured `120 sec` outer timeout",
        "`slow_success`, not `page_control_partial`",
        "record `ambient_network_degraded`",
        "an internal locator-only deadline with healthy DOM/page reads is `locator_backend_deadline`",
    ],
}

if README.exists():
    required["../README.md"] = [
        "三次浏览器调用完成首次创建",
        "外层超时统一为 120 秒",
        "20–60 秒后成功返回属于慢成功",
    ]

for relative, needles in required.items():
    path = ROOT / relative
    body = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{relative}:{needle}")

combined = "\n".join(
    (ROOT / relative).read_text(encoding="utf-8")
    for relative in (
        "SKILL.md",
        "references/orchestration-core.md",
        "references/chrome-network-recovery.md",
    )
)
for stale in ("two-call creation transaction", "`60 sec`", "最多 60 秒"):
    if stale in combined:
        errors.append(f"stale_contract:{stale}")

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "outer_timeout_ms": runtime["outer_timeout_ms"],
    "browser_boundary_commands_per_cell": runtime["browser_boundary_commands_per_cell"],
    "ambient_network_flag_required": runtime["ambient_network_flag_required"],
    "mutation_shape": "WAIT_THEN_CLICK_ONLY_THEN_READBACK",
    "controlled_input_shape": "FRESH_DOM_CUA_THEN_SHADOW_AWARE_LIVE_VALUE",
}, ensure_ascii=False, sort_keys=True))
