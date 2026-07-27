#!/usr/bin/env python3
"""Validate production one-prompt single-owner mission compilation."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "scripts" / "compile_single_owner_mission.py"
DOCS = (ROOT / "SKILL.md", ROOT / "references" / "one-prompt-runtime.md", ROOT / "references" / "single-owner-runtime.md")


def invoke(raw, parent=None):
    with tempfile.TemporaryDirectory() as temporary:
        source = Path(temporary) / "input.json"
        output = Path(temporary) / "output.json"
        source.write_text(json.dumps(raw), encoding="utf-8")
        args = [sys.executable, str(COMPILER), "--input", str(source), "--output", str(output)]
        if parent:
            args.extend(("--parent-envelope", str(parent)))
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        assert result.stdout, result.stderr
        parsed = json.loads(result.stdout)
        persisted = json.loads(output.read_text(encoding="utf-8")) if output.exists() else None
        return result.returncode, parsed, persisted


def main():
    body = " ".join("\n".join(path.read_text(encoding="utf-8") for path in DOCS).split()).lower()
    for phrase in (
        "one task, five units", "hot-pluggable", "safe boundary", "one chrome binding",
        "default authority is research-only", "legacy_multi_lane_compat", "luna/high",
    ):
        assert phrase in body, phrase
    base = {
        "mission_id": "reddit-single-owner-validator-001",
        "account": "u/Shehao",
        "direction": "indie tools and truthful product discussion",
        "operation_start_at": "2026-07-27T00:00:00Z",
        "duration_hours": 3,
        "requested_work_types": ["all"],
        "vote_policy": "DISABLED",
        "explicit_user_overrides": {"intensity": "standard"},
        "source_prompt": "start all five work units with research only and no voting",
    }
    code, envelope, persisted = invoke(base)
    assert code == 0, envelope
    assert persisted == envelope
    assert envelope["execution_topology"] == "single_owner_v1"
    assert envelope["mission_revision"] == 1 and envelope["parent_envelope_sha256"] is None
    assert envelope["selected_units"] == ["browsing", "comments", "posts", "follow-up", "presence"]
    assert envelope["paused_units"] == []
    assert envelope["unit_authority"] == {
        "browsing": "READ_ONLY", "comments": "RESEARCH_ONLY", "posts": "RESEARCH_ONLY",
        "follow-up": "RESEARCH_ONLY", "presence": "RESEARCH_ONLY",
    }
    assert envelope["model_request"]["preferred_model"] == "gpt-5.6-luna"
    assert len(envelope["mission_envelope_sha256"]) == 64

    outward = dict(base)
    outward["unit_authority"] = {"comments": "COMMENT_AUTHORIZED"}
    code, invalid, _ = invoke(outward)
    assert code == 2 and invalid["status"] == "INVALID", invalid
    outward["authorization_receipt"] = "User explicitly authorizes one compliant comment when all gates pass."
    code, authorized, _ = invoke(outward)
    assert code == 0 and authorized["unit_authority"]["comments"] == "COMMENT_AUTHORIZED", authorized
    assert authorized["authorization_receipt_sha256"] is not None

    invalid_vote = dict(base)
    invalid_vote["unit_authority"] = {"comments": "VOTE_AUTHORIZED"}
    invalid_vote["authorization_receipt"] = "not valid cross-lane vote authorization"
    code, invalid, _ = invoke(invalid_vote)
    assert code == 2 and invalid["status"] == "INVALID", invalid

    nested = dict(base)
    nested["explicit_user_overrides"] = {"research_focus": {"comments": "COMMENT_AUTHORIZED"}}
    code, invalid, _ = invoke(nested)
    assert code == 2 and invalid["status"] == "INVALID", invalid
    print(json.dumps({
        "status": "PASS", "chrome_calls": 0,
        "all_units_compiled": True,
        "default_research_authority": True,
        "outward_authority_requires_receipt": True,
        "cross_lane_vote_authority_rejected": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
