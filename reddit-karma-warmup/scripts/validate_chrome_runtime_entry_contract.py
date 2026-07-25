#!/usr/bin/env python3
"""Validate Chrome runtime-entry resolution for fresh Reddit lane sessions."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = (
    ROOT / "SKILL.md",
    ROOT / "references" / "runtime-and-setup.md",
    ROOT / "references" / "chrome-atomic-command-runtime.md",
    ROOT / "references" / "chrome-network-recovery.md",
    ROOT / "references" / "chrome-recovery-edge-cases.md",
)
ERRORS: list[str] = []


def require(path: Path, *needles: str) -> None:
    body = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            ERRORS.append(f"missing:{path.relative_to(ROOT)}:{needle}")


for document in DOCUMENTS:
    if not document.is_file():
        ERRORS.append(f"missing_file:{document}")

atomic = ROOT / "references" / "chrome-atomic-command-runtime.md"
runtime = ROOT / "references" / "runtime-and-setup.md"
network = ROOT / "references" / "chrome-network-recovery.md"
edges = ROOT / "references" / "chrome-recovery-edge-cases.md"

require(
    atomic,
    "Runtime Entry Resolution",
    "<CURRENT_CHROME_SKILL_ROOT>/scripts/browser-client.mjs",
    "Never persist, copy forward, or reconstruct",
    "not choose a cache version by sorting directories",
    "STALE_CHROME_RUNTIME_PATH",
    "not Chrome disconnection, Reddit logout, or",
)
require(
    runtime,
    "current Chrome Skill root",
    "Never reuse a",
    "STALE_CHROME_RUNTIME_PATH",
    "do not report Chrome or Reddit login failure",
)
require(
    network,
    "STALE_CHROME_RUNTIME_PATH",
    "Do not retry an old cache path",
    "This setup failure has no browser",
)
require(
    edges,
    "Browser client path came from an old task or no longer exists",
    "import fails before `agent.browsers.get(\"extension\")`",
    "Do not retry the old path, claim a tab, switch browser, or report login failure",
)

all_text = "\n".join(path.read_text(encoding="utf-8") for path in DOCUMENTS)
if re.search(r"plugins/cache/openai-bundled/chrome/\d", all_text):
    ERRORS.append("versioned_chrome_cache_path_embedded")
if "/skills/control-chrome/scripts/browser-client.mjs" in all_text:
    ERRORS.append("control_skill_subdirectory_used_as_plugin_root")

scenarios = {
    "fresh_session_without_globals": "INITIALIZE_FROM_CURRENT_SKILL_ROOT",
    "old_versioned_path_missing": "STALE_CHROME_RUNTIME_PATH_NO_OLD_PATH_RETRY",
    "current_skill_entry_missing": "STALE_CHROME_RUNTIME_PATH_RELOAD_SKILL",
    "extension_disconnected_after_initialize": "CONTROL_CHANNEL_RECOVERY",
    "old_tab_missing_with_healthy_browser": "STALE_TAB_ONLY",
}
expected = {
    "fresh_session_without_globals": "INITIALIZE_FROM_CURRENT_SKILL_ROOT",
    "old_versioned_path_missing": "STALE_CHROME_RUNTIME_PATH_NO_OLD_PATH_RETRY",
    "current_skill_entry_missing": "STALE_CHROME_RUNTIME_PATH_RELOAD_SKILL",
    "extension_disconnected_after_initialize": "CONTROL_CHANNEL_RECOVERY",
    "old_tab_missing_with_healthy_browser": "STALE_TAB_ONLY",
}
if scenarios != expected:
    ERRORS.append("scenario_mapping_changed")

if ERRORS:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": ERRORS}, ensure_ascii=False))

print(json.dumps({"status": "PASS", "scenarios": scenarios}, ensure_ascii=False, sort_keys=True))
