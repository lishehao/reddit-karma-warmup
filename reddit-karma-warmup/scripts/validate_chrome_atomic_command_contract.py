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
    "metadata_timeout_ms": 30000,
    "locator_action_timeout_ms": 90000,
    "blocking_page_commands_per_cell": 1,
    "metadata_commands_per_cell": 4,
    "metadata_allowed_operations": ["openTabs", "claimTab", "url", "title"],
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
        "Load `references/chrome-network-recovery.md` only if Chrome preflight fails",
        "First creation is three atomic calls",
        "The submit wait, one click, and readback are three separate operations",
        "A Chrome command that succeeds slowly is not a failure",
        "pure metadata transaction uses the configured 30-second budget",
    ],
    "references/chrome-atomic-command-runtime.md": [
        "Load in the Reddit launcher and every Chrome-backed Reddit execution task",
        "pass the tool's real",
        "A metadata-only transaction uses `metadata_timeout_ms`",
        "at most `metadata_commands_per_cell` awaited calls",
        "members of `metadata_allowed_operations`",
        "at most `blocking_page_commands_per_cell` potentially",
        "never bundle:",
        "fixed wait + mutation click",
        "mutation click + result verification",
        "Do not call `playwright.waitForTimeout` in the submit cell",
        "Run exactly one final click as the only browser-boundary command",
        "set `submission_uncertain`, quarantine the exact action, and never replay it",
        "classify `ambient_network_degraded`",
        "optional latency optimization, not a Skill dependency",
        "Never implement timeout with `Promise.race()`",
        "classify `chrome_content_channel_timeout`",
        "After navigation, clicking, scrolling, typing, or another interaction, collect",
        "Do not request DOM and screenshot by default",
        "Controlled Text Inputs",
        "preserve `node_id` as a string",
        "shadowRoot.activeElement",
        "locator_backend_deadline",
        "Do not use `fill(\"\")` as the sole proof",
        "not by one exact placeholder",
        "Do not hard-code Reddit placeholder copy as control identity",
        "`control_ambiguous`, not a Chrome disconnect or page-control failure",
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
        "pure metadata transaction its configured `30 sec` budget",
        "configured `120 sec` outer timeout",
        "`slow_success`, not `page_control_partial`",
        "record `ambient_network_degraded`",
        "an internal locator-only deadline with healthy DOM/page reads is `locator_backend_deadline`",
    ],
}

if README.exists():
    required["../README.md"] = [
        "三次浏览器调用完成首次创建",
        "元数据事务使用 30 秒预算且最多 4 个调用",
        "使用 120 秒外层预算",
        "20–60 秒后成功返回属于慢成功",
        "DOM snapshot、截图和 targeted projection 不默认叠加",
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
    "metadata_timeout_ms": runtime["metadata_timeout_ms"],
    "blocking_page_commands_per_cell": runtime["blocking_page_commands_per_cell"],
    "metadata_commands_per_cell": runtime["metadata_commands_per_cell"],
    "ambient_network_flag_required": runtime["ambient_network_flag_required"],
    "mutation_shape": "WAIT_THEN_CLICK_ONLY_THEN_READBACK",
    "controlled_input_shape": "FRESH_DOM_CUA_THEN_SHADOW_AWARE_LIVE_VALUE",
}, ensure_ascii=False, sort_keys=True))
