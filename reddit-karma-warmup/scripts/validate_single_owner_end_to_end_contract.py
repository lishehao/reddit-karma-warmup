#!/usr/bin/env python3
"""Exercise five unit packets across decision rounds, then retire offline."""

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
START = "2026-07-27T00:00:00Z"
LANES = ("browsing", "comments", "posts", "follow-up", "presence")


def invoke(args):
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    assert result.stdout, result.stderr
    return result.returncode, json.loads(result.stdout)


def queue(root, envelope, command, **extra):
    if command == "wake-open" and "expected_at_utc" not in extra:
        extra["expected_at_utc"] = extra["now_utc"]
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


def run_round(root, envelope, lane, index, now):
    opened = expect(root, envelope, "wake-open", "WAKE_OPENED", wake_id="wake-" + str(index), now_utc=now)
    assert lane in opened["due_units"], opened
    unit_id = None
    for due_lane in opened["due_units"]:
        decision = "RUN" if due_lane == lane else "DEFER"
        extra = {"next_due_minutes": 20} if decision != "RUN" else {}
        selected = expect(
            root, envelope, "decide", "DECISION_RECORDED", wake_id="wake-" + str(index),
            unit=due_lane, decision=decision, reason="offline end-to-end " + decision.lower(),
            now_utc=now, **extra,
        )
        if decision == "RUN":
            unit_id = selected["unit_id"]
    started = expect(root, envelope, "start", "STARTED", now_utc=now)
    assert started["active_unit_id"] == unit_id
    if lane == "browsing":
        expect(root, envelope, "read-batch-open", "READ_BATCH_OPEN", unit_id=unit_id, read_tab_count=2, now_utc=now)
        expect(root, envelope, "read-batch-settle", "READ_BATCH_SETTLED", unit_id=unit_id, read_batch_outcome="VERIFIED", proof_sha256=PROOF, now_utc=now)
    expect(root, envelope, "complete", "COMPLETED", unit_id=unit_id, now_utc=now)
    return unit_id


def main():
    raw = {
        "mission_id": "reddit-single-owner-e2e-001", "account": "u/Shehao",
        "direction": "truthful product research", "operation_start_at": START,
        "duration_hours": 6, "requested_work_types": ["all"],
        "source_prompt": "five units, serial decision rounds",
    }
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        source, envelope_path = directory / "input.json", directory / "envelope.json"
        source.write_text(json.dumps(raw), encoding="utf-8")
        code, envelope = invoke([sys.executable, str(COMPILER), "--input", str(source), "--output", str(envelope_path)])
        assert code == 0, envelope
        root = directory / "queues"
        expect(root, envelope_path, "bootstrap", "BOOTSTRAPPED", now_utc=START)
        expect(root, envelope_path, "canary-pass", "CANARY_PASSED", proof_sha256=PROOF, now_utc=START)
        checkpoints = (
            "2026-07-27T00:00:00Z", "2026-07-27T00:20:00Z",
            "2026-07-27T00:40:00Z", "2026-07-27T01:00:00Z",
            "2026-07-27T01:20:00Z",
        )
        completed = [run_round(root, envelope_path, lane, index, checkpoints[index]) for index, lane in enumerate(LANES)]
        assert [value.split(":")[-2] for value in completed] == list(LANES)
        expect(root, envelope_path, "release-tabs", "TABS_RELEASED", proof_sha256=PROOF, now_utc="2026-07-27T02:00:00Z")
        retired = expect(root, envelope_path, "retire", "RETIRED", now_utc="2026-07-27T02:00:00Z")
        assert retired["state"] == "RETIRED" and retired["chrome_release_state"] == "RELEASED"
        record = json.loads(next(root.glob("*.json")).read_text(encoding="utf-8"))
        assert len(record["history"]) == 5
        assert not record["queue"] and record["wake"] is None and record["active"] is None
    print(json.dumps({
        "status": "PASS", "chrome_calls": 0, "five_units_serialized": True,
        "five_distinct_decision_rounds": True, "canary_read_batch_release_retire_proven": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
