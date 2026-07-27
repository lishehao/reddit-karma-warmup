#!/usr/bin/env python3
"""Exercise the production five-unit queue through a clean retirement path."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "scripts" / "compile_single_owner_mission.py"
QUEUE = ROOT / "scripts" / "single_owner_queue.py"
OWNER = "reddit-owner-e2e-001"
PROOF = "c" * 64


def invoke(args):
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    assert result.stdout, result.stderr
    return result.returncode, json.loads(result.stdout)


def queue(root, envelope, command, **extra):
    args = [sys.executable, str(QUEUE), command, "--root", str(root), "--scope", "single-owner-e2e", "--owner-task-id", OWNER, "--mission-envelope", str(envelope)]
    for key, value in extra.items():
        args.extend(("--" + key.replace("_", "-"), str(value)))
    code, output = invoke(args)
    assert code == 0, output
    return output


def expect(root, envelope, command, status, **extra):
    output = queue(root, envelope, command, **extra)
    assert output["status"] == status, output
    return output


def main():
    raw = {
        "mission_id": "reddit-single-owner-e2e-001", "account": "u/Shehao",
        "direction": "truthful product research", "operation_start_at": "2026-07-27T00:00:00Z",
        "duration_hours": 1, "requested_work_types": ["all"],
        "source_prompt": "all five work units research only",
    }
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        source = directory / "input.json"
        envelope_path = directory / "envelope.json"
        source.write_text(json.dumps(raw), encoding="utf-8")
        code, envelope = invoke([sys.executable, str(COMPILER), "--input", str(source), "--output", str(envelope_path)])
        assert code == 0, envelope
        root = directory / "queues"
        expect(root, envelope_path, "bootstrap", "BOOTSTRAPPED")
        expect(root, envelope_path, "canary-pass", "CANARY_PASSED", proof_sha256=PROOF)
        completed = []
        for lane in ("browsing", "comments", "posts", "follow-up", "presence"):
            started = expect(root, envelope_path, "start", "STARTED")
            assert started["active_unit_id"].split(":")[-2] == lane, started
            if lane == "browsing":
                expect(root, envelope_path, "read-batch-open", "READ_BATCH_OPEN", unit_id=started["active_unit_id"], read_tab_count=2)
                expect(root, envelope_path, "read-batch-settle", "READ_BATCH_SETTLED", unit_id=started["active_unit_id"], read_batch_outcome="VERIFIED", proof_sha256=PROOF)
            done = expect(root, envelope_path, "complete", "COMPLETED", unit_id=started["active_unit_id"])
            completed.append(done["unit_id"] if "unit_id" in done else started["active_unit_id"])
        expect(root, envelope_path, "start", "QUEUE_EMPTY")
        expect(root, envelope_path, "release-tabs", "TABS_RELEASED", proof_sha256=PROOF)
        retired = expect(root, envelope_path, "retire", "RETIRED")
        assert retired["state"] == "RETIRED" and retired["chrome_release_state"] == "RELEASED"
        records = list(root.glob("*.json"))
        assert len(records) == 1
        record = json.loads(records[0].read_text(encoding="utf-8"))
        assert len(record["history"]) == 5
        assert record["active"] is None and record["active_read_batch"] is None and record["browser_boundary"] is None
    print(json.dumps({
        "status": "PASS", "chrome_calls": 0,
        "five_units_serialized": True,
        "canary_read_batch_release_retire_proven": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
