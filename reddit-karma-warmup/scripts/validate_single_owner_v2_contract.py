#!/usr/bin/env python3
"""Validate the compact single-owner Reddit Skill without network or Chrome."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
DEFAULTS = ROOT / "references" / "operation-defaults.json"
INDEX = ROOT / "scripts" / "community_index.py"
COMPILER = ROOT / "scripts" / "compile_single_owner_mission.py"
QUEUE = ROOT / "scripts" / "single_owner_queue.py"


def run(*args: str) -> dict:
    result = subprocess.run([sys.executable, *args], text=True, capture_output=True, check=False)
    assert result.stdout, result.stderr
    return json.loads(result.stdout)


def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    defaults = json.loads(DEFAULTS.read_text(encoding="utf-8"))
    version = manifest["version"]
    assert version == "2026.07.27.4"
    assert defaults["topology"]["chrome_owners"] == 1
    assert defaults["topology"]["cross_task_dispatch"] == "FORBIDDEN"
    assert defaults["scheduler"]["ordinary_trigger_tolerance_seconds"] == 300
    assert defaults["research"]["community_index"]["methods"] == ["GET"]
    assert defaults["research"]["community_index"]["account_or_write_endpoints"] == "FORBIDDEN"
    assert defaults["research"]["web_search"]["posts_query_min"] >= 8
    assert set(defaults["units"]) == {"browsing", "comments", "posts", "follow-up", "presence"}
    documents = [SKILL]
    repository_readme = ROOT.parent / "README.md"
    if repository_readme.is_file():
        documents.append(repository_readme)
    text = "\n".join(path.read_text(encoding="utf-8") for path in documents)
    for phrase in ("user-visible `Reddit 运营台`", "Official Reddit API", "Chrome", "MUTATION_INTENT", "±5 minutes"):
        assert phrase in text, phrase
    assert "legacy_multi_lane_compat" not in text
    required = {"single-owner-runtime.md", "research-and-community-index.md", "chrome-and-actions.md", "unit-guides.md", "operation-defaults.json"}
    actual = {path.name for path in (ROOT / "references").iterdir()}
    assert actual == required, actual
    scripts = {path.name for path in (ROOT / "scripts").iterdir()}
    assert scripts == {"compile_single_owner_mission.py", "single_owner_queue.py", "community_index.py", "validate_single_owner_v2_contract.py"}, scripts
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        status = run(str(INDEX), "--root", str(work / "index"), "status")
        assert status["status"] == "READY" and status["community_count"] == 0
        unavailable = run(str(INDEX), "--root", str(work / "index"), "refresh", "--subreddit", "r/SideProject")
        assert unavailable["status"] == "UNCONFIGURED_OFFICIAL_REDDIT_API"
        source = work / "mission.json"
        envelope = work / "envelope.json"
        source.write_text(json.dumps({"mission_id": "v2-contract", "account": "u/example", "direction": "truthful research", "operation_start_at": "2026-07-27T00:00:00Z", "duration_hours": 2, "requested_work_types": ["browsing", "posts"], "source_prompt": "compact one task"}), encoding="utf-8")
        compiled = run(str(COMPILER), "--input", str(source), "--output", str(envelope))
        assert compiled["selected_units"] == ["browsing", "posts"]
        queue_root = work / "queue"
        shared = ("--root", str(queue_root), "--scope", "v2", "--owner-task-id", "owner-1", "--mission-envelope", str(envelope))
        bootstrapped = run(str(QUEUE), "bootstrap", *shared)
        assert bootstrapped["status"] == "BOOTSTRAPPED" and bootstrapped["due_units"] == ["browsing", "posts"]
        proof = "0" * 64
        assert run(str(QUEUE), "canary-pass", *shared, "--proof-sha256", proof)["status"] == "CANARY_PASSED"
        assert run(str(QUEUE), "wake-open", *shared, "--expected-at-utc", "2026-07-27T00:00:00Z", "--now-utc", "2026-07-27T00:04:59Z")["status"] == "WAKE_OPEN"
        assert run(str(QUEUE), "decide", *shared, "--unit", "browsing", "--decision", "RUN", "--reason", "read current context", "--now-utc", "2026-07-27T00:05:00Z")["status"] == "DECISION_RECORDED"
        assert run(str(QUEUE), "decide", *shared, "--unit", "posts", "--decision", "DEFER", "--reason", "not due for one packet", "--now-utc", "2026-07-27T00:05:01Z")["status"] == "DECISION_RECORDED"
        started = run(str(QUEUE), "start", *shared, "--now-utc", "2026-07-27T00:05:02Z")
        assert started["status"] == "PACKET_STARTED" and started["unit"] == "browsing"
        assert run(str(QUEUE), "boundary-open", *shared, "--boundary-id", "read-1", "--boundary-kind", "DOM_READ", "--now-utc", "2026-07-27T00:05:03Z")["status"] == "BOUNDARY_OPEN"
        assert run(str(QUEUE), "boundary-settle", *shared, "--boundary-id", "read-1", "--boundary-outcome", "READ_OK", "--now-utc", "2026-07-27T00:05:04Z")["status"] == "BOUNDARY_SETTLED"
        assert run(str(QUEUE), "finish", *shared, "--outcome", "COMPLETED", "--now-utc", "2026-07-27T00:05:05Z")["status"] == "COMPLETED"
    print(json.dumps({"status": "PASS", "version": version, "single_owner": True, "api_get_only_optional": True, "chrome_live_gate_required": True, "legacy_files_removed": True}, sort_keys=True))


if __name__ == "__main__":
    main()
