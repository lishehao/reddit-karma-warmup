#!/usr/bin/env python3
"""Validate mandatory built-in Web Search preflight for Reddit text lanes."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "references"


def read(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"missing {path}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    defaults = json.loads(read(REF / "operation-defaults.json"))
    web = defaults["web_search"]
    assert web["tool_requirement"] == "BUILT_IN_WEB_SEARCH"
    assert web["comments"]["cluster_discovery_query_min"] >= 4
    assert web["comments"]["cluster_discovery_query_cap"] >= web["comments"]["cluster_discovery_query_min"]
    assert web["comments"]["per_comment_exact_query_min"] >= 1
    assert web["posts"]["query_pack_min"] >= 12
    assert web["posts"]["query_pack_target"] >= web["posts"]["query_pack_min"]
    assert web["posts"]["query_pack_cap"] >= web["posts"]["query_pack_target"]
    assert len(web["posts"]["required_query_families"]) >= 4

    required = {
        "SKILL.md": ["WEB RESEARCH", "Web Search preflight", "Chrome remains the final live authority"],
        "comments-playbook.md": ["comment-window built-in Web Search query pack", "web_search_item_id"],
        "posts-playbook.md": ["built-in Web Search post query pack", "Web Search query pack and live Reddit"],
        "community-selection-funnel.md": ["Web Search post query pack", "query_pack_min", "Web Search results do not replace"],
        "publish-consistency.md": ["web_search_item_id", "completed `web_search.posts` query pack"],
        "web-search-preflight.md": ["Built-in Web Search", "Before **every individual comment**", "default 12", "never proves live Reddit permission"],
        "chrome-recovery-edge-cases.md": ["as a Chrome recovery substitute", "Normal pre-action Web Search research remains separate"],
        "chrome-network-recovery.md": ["separate mandatory built-in Web Search research stage"],
    }
    for name, phrases in required.items():
        body = " ".join(read(ROOT / name if name == "SKILL.md" else REF / name).split())
        for phrase in phrases:
            assert " ".join(phrase.split()) in body, f"{name}: missing {phrase!r}"

    print(json.dumps({
        "status": "PASS",
        "comment_window_query_range": [
            web["comments"]["cluster_discovery_query_min"],
            web["comments"]["cluster_discovery_query_cap"],
        ],
        "post_query_range": [web["posts"]["query_pack_min"], web["posts"]["query_pack_cap"]],
        "per_comment_exact_query_min": web["comments"]["per_comment_exact_query_min"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
