#!/usr/bin/env python3
"""Validate launcher Chrome layering, tab safety, and content-scope routing."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"
DEFAULTS = json.loads(
    (ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8")
)
RUNTIME = DEFAULTS["chrome_command_runtime"]
ERRORS: list[str] = []


def require(relative: str, needles: list[str]) -> None:
    path = ROOT / relative
    body = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            ERRORS.append(f"missing:{relative}:{needle}")


def route(metadata_ok: bool, content_ok: bool, neutral_content_ok):
    if not metadata_ok:
        return "PAGE_CONTROL_PARTIAL_OR_CONTROL_CHANNEL"
    if content_ok:
        return "REDDIT_ACCOUNT_PROOF_ELIGIBLE"
    if neutral_content_ok is True:
        return "CHROME_CONTENT_CHANNEL_TIMEOUT:REDDIT_SCOPE"
    if neutral_content_ok is False:
        return "CHROME_CONTENT_CHANNEL_TIMEOUT:GLOBAL_SCOPE"
    return "CHROME_CONTENT_CHANNEL_TIMEOUT:UNKNOWN_SCOPE"


def select_launcher_tab(open_reddit_tab_ids: list[str], occupied_tab_ids: set[str]):
    return next((tab_id for tab_id in open_reddit_tab_ids
                 if tab_id not in occupied_tab_ids), None)


assert RUNTIME["metadata_timeout_ms"] == 30000
assert RUNTIME["outer_timeout_ms"] == 120000
assert RUNTIME["metadata_commands_per_cell"] == 4
assert RUNTIME["blocking_page_commands_per_cell"] == 1
assert RUNTIME["metadata_allowed_operations"] == [
    "openTabs", "claimTab", "url", "title"
]

require("SKILL.md", [
    "load `references/runtime-and-setup.md`, `references/reddit-surface-routing.md`, `references/chrome-atomic-command-runtime.md`",
    "Load `references/chrome-network-recovery.md` only if Chrome preflight fails",
    "healthy metadata channel is not proof that page content or the Reddit account is readable",
])
require("references/runtime-and-setup.md", [
    "Initialize its browser",
    "once per fresh Node session",
    "reuse an existing `agent.browsers` runtime",
    "read the full",
    "Only an explicit browser-disconnected result invalidates the",
    "one lightweight metadata transaction under `metadata_timeout_ms`",
    "exact-object `claimTab()`",
    "exclude every exact tab ID recorded",
    "Claim only a",
    "provably unowned Reddit tab",
    "never navigate,",
    "or repurpose an unrelated",
    "user, launcher, or sibling-lane tab as fallback",
    "cheapest page-state surface",
    "only blocking page command in its cell",
    "CHROME_METADATA_HEALTHY",
    "CHROME_TAB_CLAIMED",
    "CHROME_CONTENT_CHANNEL_TIMEOUT",
    "REDDIT_PAGE_UNVERIFIED",
    "at most one neutral",
    "do not recommend reinstalling or re-enabling the extension",
    "never wrap browser work in `Promise.race()`",
])
require("references/chrome-atomic-command-runtime.md", [
    "metadata-only cell may use at most `metadata_commands_per_cell`",
    "members of `metadata_allowed_operations`",
    "at most `blocking_page_commands_per_cell` potentially",
    "not permission to combine a claim",
    "Never implement timeout with `Promise.race()`",
    "reuse `agent.browsers` when",
])
require("references/chrome-network-recovery.md", [
    "exact-object claim or URL/title metadata times out, classify `page_control_partial`",
    "classify `chrome_content_channel_timeout`",
    "do not cycle through DOM, screenshot, and evaluate",
    "content-read timeout alone never",
])

if README.exists():
    body = README.read_text(encoding="utf-8")
    for needle in (
        "元数据事务可在一个 30 秒调用内完成",
        "绝不拿无关用户、启动台或 sibling lane 标签改道",
        "未被其他启动台或执行台的 checkpoint 记录为占用",
        "CHROME_CONTENT_CHANNEL_TIMEOUT",
        "REDDIT_PAGE_UNVERIFIED",
        "元数据已成功时不建议重装或重新启用扩展",
    ):
        if needle not in body:
            ERRORS.append(f"missing:../README.md:{needle}")

scenarios = {
    "metadata_failed": route(False, False, None),
    "account_readable": route(True, True, None),
    "reddit_content_only_failed": route(True, False, True),
    "global_content_failed": route(True, False, False),
    "content_scope_unknown": route(True, False, None),
}
assert scenarios == {
    "metadata_failed": "PAGE_CONTROL_PARTIAL_OR_CONTROL_CHANNEL",
    "account_readable": "REDDIT_ACCOUNT_PROOF_ELIGIBLE",
    "reddit_content_only_failed": "CHROME_CONTENT_CHANNEL_TIMEOUT:REDDIT_SCOPE",
    "global_content_failed": "CHROME_CONTENT_CHANNEL_TIMEOUT:GLOBAL_SCOPE",
    "content_scope_unknown": "CHROME_CONTENT_CHANNEL_TIMEOUT:UNKNOWN_SCOPE",
}

assert select_launcher_tab(["user-reddit"], set()) == "user-reddit"
assert select_launcher_tab(["worker-reddit"], {"worker-reddit"}) is None
assert select_launcher_tab(
    ["worker-reddit", "user-reddit"], {"worker-reddit"}
) == "user-reddit"

if ERRORS:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": ERRORS}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "metadata_transaction": "OPEN_TABS_CLAIM_URL_TITLE_ONLY",
    "blocking_page_commands_per_cell": 1,
    "unrelated_user_tab_fallback": "FORBIDDEN",
    "sibling_lane_tab_fallback": "FORBIDDEN",
    "extension_reinstall_from_content_timeout": "FORBIDDEN",
    "scenarios": scenarios,
}, ensure_ascii=False, sort_keys=True))
