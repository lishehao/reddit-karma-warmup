#!/usr/bin/env python3
"""Reject accidental regression to multi-task Chrome ownership by default."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
RUNTIME = ROOT / "references" / "single-owner-runtime.md"
OWNERSHIP = ROOT / "references" / "lane-action-ownership.md"


def main():
    skill = " ".join(SKILL.read_text(encoding="utf-8").split())
    runtime = " ".join(RUNTIME.read_text(encoding="utf-8").split())
    ownership = " ".join(OWNERSHIP.read_text(encoding="utf-8").split())
    for phrase in (
        "Default topology: one task, five units", "one Chrome binding", "Do not create one Chrome-owning task per unit",
        "execution_topology=legacy_multi_lane_compat", "Safe hot-plugging", "Only `browsing` may inspect or operate",
    ):
        assert phrase in skill, phrase
    assert "production runtime for `execution_topology=single_owner_v1`" in runtime
    assert "The five units are policy boundaries, not five threads" in runtime
    assert "table defines unit authority; it does not create five separate tasks" in ownership
    assert "independent account-scoped lane tasks" not in skill
    assert "Reddit 分发台" not in skill
    print(json.dumps({
        "status": "PASS", "default_topology": "single_owner_v1",
        "legacy_topology": "explicit_compatibility_only", "chrome_calls": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
