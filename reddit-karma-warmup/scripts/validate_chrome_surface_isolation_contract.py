#!/usr/bin/env python3
"""Validate Reddit's long Chrome budget plus tab/control isolation contract."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = ROOT / "references" / "operation-defaults.json"
LEASE = ROOT / "scripts" / "chrome_surface_lease.py"
DOCS = (
    ROOT / "SKILL.md",
    ROOT / "references" / "chrome-atomic-command-runtime.md",
    ROOT / "references" / "chrome-network-recovery.md",
    ROOT / "references" / "orchestration-core.md",
    ROOT / "references" / "thread-supervision-runtime.md",
)


def invoke(root, *arguments):
    result = subprocess.run(
        [sys.executable, str(LEASE), "--root", str(root), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode, json.loads(result.stdout)


def main():
    runtime = json.loads(DEFAULTS.read_text(encoding="utf-8"))["chrome_command_runtime"]
    assert runtime["outer_timeout_ms"] == 120000
    assert runtime["metadata_timeout_ms"] == 30000
    assert runtime["blocking_page_commands_per_cell"] == 1
    assert runtime["metadata_commands_per_cell"] == 4
    assert runtime["control_slot_scope"] == "chrome-default-control"
    assert runtime["control_slot_wait_ms"] == 5000
    assert runtime["control_slot_ttl_seconds"] == 150
    assert runtime["tab_lease_ttl_seconds"] == 14400
    joined = " ".join("\n".join(path.read_text(encoding="utf-8") for path in DOCS).split()).lower()
    for term in (
        "chrome_tab_lease/v1",
        "chrome_control_slot/v1",
        "creates its tab as one browser action, then creates",
        "CHROME_CONTROL_SLOT_BUSY",
        "not a Chrome-control fault",
        "120-second outer timeout",
        "tab sharing is forbidden",
        "no sibling page/content inspection",
    ):
        assert term.lower() in joined, term

    with tempfile.TemporaryDirectory() as raw:
        state_root = Path(raw)
        common = ("--scope", "chrome-default-control")
        code, record = invoke(state_root, "acquire", "--kind", "control", *common,
                              "--owner-task-id", "reddit-comments", "--lease-id", "slot-comments")
        assert code == 0 and record["status"] == "ACQUIRED"
        code, record = invoke(state_root, "acquire", "--kind", "control", *common,
                              "--owner-task-id", "reddit-posts", "--lease-id", "slot-posts")
        assert code == 3 and record["status"] == "BUSY"
        code, record = invoke(state_root, "release", "--kind", "control", *common,
                              "--owner-task-id", "reddit-comments", "--lease-id", "slot-comments")
        assert code == 0 and record["status"] == "RELEASED"
        tab_args = ("--scope", "extension-default:tab-3:nonce-comments")
        code, record = invoke(state_root, "acquire", "--kind", "tab", *tab_args,
                              "--owner-task-id", "reddit-comments", "--lease-id", "tab-comments",
                              "--ttl-seconds", "14400")
        assert code == 0 and record["status"] == "ACQUIRED"
        code, record = invoke(state_root, "acquire", "--kind", "tab", *tab_args,
                              "--owner-task-id", "reddit-posts", "--lease-id", "tab-posts")
        assert code == 3 and record["status"] == "BUSY"
        code, record = invoke(state_root, "release", "--kind", "tab", *tab_args,
                              "--owner-task-id", "reddit-comments", "--lease-id", "tab-comments")
        assert code == 0 and record["status"] == "RELEASED"

    print(json.dumps({
        "status": "PASS",
        "outer_timeout_ms": runtime["outer_timeout_ms"],
        "control_slot": "serialized_per_atomic_browser_call",
        "tab_isolation": "one_exact_lease_per_lane",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
