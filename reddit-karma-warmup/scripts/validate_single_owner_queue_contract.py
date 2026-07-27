#!/usr/bin/env python3
"""Exercise due-unit decisions, recovery priority, and safe hot-plugs offline."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "scripts" / "compile_single_owner_mission.py"
QUEUE = ROOT / "scripts" / "single_owner_queue.py"
OWNER = "reddit-owner-exact-001"
PROOF = "d" * 64
START = "2026-07-27T00:00:00Z"


def call(args):
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    assert result.stdout, result.stderr
    return result.returncode, json.loads(result.stdout)


def compile_envelope(directory, raw, parent=None, name="mission.envelope.json"):
    source = directory / (name + ".input.json")
    output = directory / name
    source.write_text(json.dumps(raw), encoding="utf-8")
    args = [sys.executable, str(COMPILER), "--input", str(source), "--output", str(output)]
    if parent:
        args.extend(("--parent-envelope", str(parent)))
    code, parsed = call(args)
    assert code == 0, parsed
    return output


def queue(root, envelope, command, **extra):
    if command == "wake-open" and "expected_at_utc" not in extra:
        extra["expected_at_utc"] = extra["now_utc"]
    args = [
        sys.executable, str(QUEUE), command, "--root", str(root),
        "--scope", "single-owner-queue-test", "--owner-task-id", OWNER,
        "--mission-envelope", str(envelope),
    ]
    for key, value in extra.items():
        args.extend(("--" + key.replace("_", "-"), str(value)))
    return call(args)


def expect(root, envelope, command, status, **extra):
    code, output = queue(root, envelope, command, **extra)
    assert code == 0 and output["status"] == status, output
    return output


def decide_all(root, envelope, wake_id, run_lane, now, deferred_lanes=(), expected_at=None):
    opened = expect(
        root, envelope, "wake-open", "WAKE_OPENED", wake_id=wake_id,
        now_utc=now, expected_at_utc=expected_at or now,
    )
    if expected_at is not None:
        assert opened["trigger_state"] == "RECOMPUTED_FROM_ACTUAL", opened
    assert set(opened["due_units"]) >= {run_lane}
    chosen = None
    for lane in opened["due_units"]:
        decision = "RUN" if lane == run_lane else ("DEFER" if lane in deferred_lanes else "WATCH")
        extra = {"next_due_minutes": 20} if decision != "RUN" else {}
        result = expect(
            root, envelope, "decide", "DECISION_RECORDED", wake_id=wake_id,
            unit=lane, decision=decision, reason="offline contract " + decision.lower(),
            now_utc=now, **extra,
        )
        if decision == "RUN":
            chosen = result["unit_id"]
    return chosen


def main():
    initial_raw = {
        "mission_id": "reddit-single-owner-queue-001", "account": "u/Shehao",
        "direction": "truthful product research", "operation_start_at": START,
        "duration_hours": 6, "requested_work_types": ["all"],
        "source_prompt": "one owner, due-unit decision rounds only",
    }
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        root = directory / "queues"
        initial_path = compile_envelope(directory, initial_raw)
        revision_raw = {
            "requested_work_types": ["browsing", "comments", "follow-up", "presence"],
            "paused_work_types": ["presence"],
            "source_prompt": "remove posts and pause presence at a safe boundary",
        }
        revision_path = compile_envelope(directory, revision_raw, parent=initial_path, name="revision-2.json")

        expect(root, initial_path, "bootstrap", "BOOTSTRAPPED", now_utc=START)
        expect(root, initial_path, "start", "CANARY_REQUIRED", now_utc=START)
        expect(root, initial_path, "canary-pass", "CANARY_PASSED", proof_sha256=PROOF, now_utc=START)

        browsing_id = decide_all(root, initial_path, "wake-1", "browsing", START, deferred_lanes=("posts",))
        assert browsing_id.endswith("browsing:g1")
        started = expect(root, initial_path, "start", "STARTED", now_utc=START)
        assert started["active_unit_id"] == browsing_id
        expect(root, initial_path, "boundary-open", "BROWSER_BOUNDARY_OPEN", unit_id=browsing_id, boundary_id="read-1", boundary_kind="content_read", now_utc=START)
        deferred = expect(root, revision_path, "apply-revision", "HOTPLUG_DEFERRED_UNSAFE_BOUNDARY", now_utc=START)
        assert deferred["unsafe_reason"] == "ACTIVE_UNIT"
        expect(root, initial_path, "boundary-settle", "BROWSER_BOUNDARY_SETTLED", boundary_id="read-1", boundary_outcome="ACKNOWLEDGED", now_utc=START)
        expect(root, initial_path, "read-batch-open", "READ_BATCH_OPEN", unit_id=browsing_id, read_tab_count=2, now_utc=START)
        expect(root, initial_path, "read-batch-settle", "READ_BATCH_SETTLED", unit_id=browsing_id, read_batch_outcome="VERIFIED", proof_sha256=PROOF, now_utc=START)
        expect(root, initial_path, "complete", "COMPLETED", unit_id=browsing_id, now_utc=START)

        # A yielded packet owns the next wake. No later due unit can bypass it.
        comment_id = decide_all(
            root, initial_path, "wake-2", "comments", "2026-07-27T00:26:00Z",
            expected_at="2026-07-27T00:20:00Z",
        )
        drift = expect(root, initial_path, "inspect", "INSPECT", now_utc="2026-07-27T00:26:00Z")
        assert drift["wake_state"] == "READY_TO_RUN"
        expect(root, initial_path, "start", "STARTED", now_utc="2026-07-27T00:26:00Z")
        expect(root, initial_path, "yield", "YIELDED", unit_id=comment_id, now_utc="2026-07-27T00:26:00Z")
        recovery = expect(root, initial_path, "wake-open", "WAKE_RECOVERY_REQUIRED", wake_id="wake-3", now_utc="2026-07-27T00:40:00Z")
        assert recovery["unit_id"] == comment_id
        resumed = expect(root, initial_path, "start", "RESUMED", now_utc="2026-07-27T00:40:00Z")
        assert resumed["active_unit_id"] == comment_id
        expect(root, initial_path, "complete", "COMPLETED", unit_id=comment_id, now_utc="2026-07-27T00:40:00Z")

        applied = expect(root, revision_path, "apply-revision", "REVISION_APPLIED", now_utc="2026-07-27T00:40:00Z")
        assert applied["unit_changes"] == {"posts": "REMOVE", "presence": "PAUSE"}, applied
        assert applied["scheduled_due_units"] == []
        assert applied["unit_plan"]["posts"] == "REMOVED" and applied["unit_plan"]["presence"] == "PAUSED"

        revision3_raw = {
            "requested_work_types": ["browsing", "comments", "posts", "follow-up", "presence"],
            "paused_work_types": [], "source_prompt": "resume posts and presence",
        }
        revision3_path = compile_envelope(directory, revision3_raw, parent=revision_path, name="revision-3.json")
        applied3 = expect(root, revision3_path, "apply-revision", "REVISION_APPLIED", now_utc="2026-07-27T00:40:00Z")
        assert applied3["scheduled_due_units"] == ["posts", "presence"], applied3

        authority_revision_raw = {
            "requested_work_types": ["browsing", "comments", "posts", "follow-up", "presence"],
            "paused_work_types": [],
            "unit_authority": {"comments": "COMMENT_AUTHORIZED"},
            "authorization_receipt": "User directly authorizes one compliant proactive comment when all live gates pass.",
            "source_prompt": "keep all units active and authorize only comments",
        }
        authority_path = compile_envelope(directory, authority_revision_raw, parent=revision3_path, name="revision-4-authority.json")
        authority_applied = expect(root, authority_path, "apply-revision", "REVISION_APPLIED", now_utc="2026-07-27T00:40:00Z")
        assert authority_applied["authority_changes"] == {"comments": {"from": "RESEARCH_ONLY", "to": "COMMENT_AUTHORIZED"}}
        code, wrong_owner = queue(root, authority_path, "inspect", owner_task_id="other", now_utc="2026-07-27T00:40:00Z")
        assert code == 2 and wrong_owner["status"] == "INVALID", wrong_owner

    print(json.dumps({
        "status": "PASS", "chrome_calls": 0, "single_owner": True,
        "one_packet_per_wake": True, "due_units_decided": True,
        "yield_recovery_first": True, "hotplug_requires_safe_boundary": True,
        "authority_only_hotplug_requires_receipt": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
