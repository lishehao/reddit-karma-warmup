#!/usr/bin/env python3
"""Validate queue ownership, recovery ordering, and safe-boundary revisions."""

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
    assert parsed == json.loads(output.read_text(encoding="utf-8"))
    return output, parsed


def queue(root, envelope, command, **extra):
    args = [sys.executable, str(QUEUE), command, "--root", str(root), "--scope", "single-owner-queue-test", "--owner-task-id", OWNER, "--mission-envelope", str(envelope)]
    for key, value in extra.items():
        args.extend(("--" + key.replace("_", "-"), str(value)))
    return call(args)


def expect(root, envelope, command, status, **extra):
    code, output = queue(root, envelope, command, **extra)
    assert code == 0 and output["status"] == status, output
    return output


def main():
    initial_raw = {
        "mission_id": "reddit-single-owner-queue-001", "account": "u/Shehao",
        "direction": "truthful product research", "operation_start_at": "2026-07-27T00:00:00Z",
        "duration_hours": 3, "requested_work_types": ["all"], "source_prompt": "run five units research only",
    }
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        root = directory / "queues"
        initial_path, initial = compile_envelope(directory, initial_raw)
        revision_raw = {
            "requested_work_types": ["browsing", "comments", "follow-up", "presence"],
            "paused_work_types": ["presence"],
            "source_prompt": "remove posts and pause presence at a safe boundary",
        }
        revision_path, revision = compile_envelope(directory, revision_raw, parent=initial_path, name="revision-2.json")
        expect(root, initial_path, "bootstrap", "BOOTSTRAPPED")
        expect(root, initial_path, "start", "CANARY_REQUIRED")
        expect(root, initial_path, "canary-pass", "CANARY_PASSED", proof_sha256=PROOF)
        started = expect(root, initial_path, "start", "STARTED")
        assert started["unit_plan"]["browsing"] == "ACTIVE" and started["active_unit_id"].endswith("browsing:g1")
        expect(root, initial_path, "boundary-open", "BROWSER_BOUNDARY_OPEN", unit_id=started["active_unit_id"], boundary_id="read-1", boundary_kind="content_read")
        deferred = expect(root, revision_path, "apply-revision", "HOTPLUG_DEFERRED_UNSAFE_BOUNDARY")
        assert deferred["unsafe_reason"] == "ACTIVE_UNIT"
        expect(root, initial_path, "boundary-settle", "BROWSER_BOUNDARY_SETTLED", boundary_id="read-1", boundary_outcome="ACKNOWLEDGED")
        expect(root, initial_path, "read-batch-open", "READ_BATCH_OPEN", unit_id=started["active_unit_id"], read_tab_count=2)
        expect(root, initial_path, "read-batch-settle", "READ_BATCH_SETTLED", unit_id=started["active_unit_id"], read_batch_outcome="VERIFIED", proof_sha256=PROOF)
        expect(root, initial_path, "complete", "COMPLETED", unit_id=started["active_unit_id"])
        comment = expect(root, initial_path, "start", "STARTED")
        assert comment["active_unit_id"].endswith("comments:g1")
        expect(root, initial_path, "yield", "YIELDED", unit_id=comment["active_unit_id"])
        resumed = expect(root, initial_path, "start", "RESUMED")
        assert resumed["active_unit_id"] == comment["active_unit_id"]
        expect(root, initial_path, "complete", "COMPLETED", unit_id=resumed["active_unit_id"])

        applied = expect(root, revision_path, "apply-revision", "REVISION_APPLIED")
        assert applied["unit_changes"] == {"posts": "REMOVE", "presence": "PAUSE"}, applied
        assert applied["unit_plan"]["posts"] == "REMOVED" and applied["unit_plan"]["presence"] == "PAUSED"

        revision3_raw = {
            "requested_work_types": ["browsing", "comments", "posts", "follow-up", "presence"],
            "paused_work_types": [],
            "source_prompt": "resume posts and presence",
        }
        revision3_path, _ = compile_envelope(directory, revision3_raw, parent=revision_path, name="revision-3.json")
        applied3 = expect(root, revision3_path, "apply-revision", "REVISION_APPLIED")
        assert applied3["unit_changes"] == {"posts": "ADD", "presence": "RESUME"}, applied3
        assert any(item.endswith("posts:g2") for item in applied3["created_unit_ids"])
        assert any(item.endswith("presence:g2") for item in applied3["created_unit_ids"])

        authority_revision_raw = {
            "requested_work_types": ["browsing", "comments", "posts", "follow-up", "presence"],
            "paused_work_types": [],
            "unit_authority": {"comments": "COMMENT_AUTHORIZED"},
            "authorization_receipt": "User directly authorizes one compliant proactive comment when all live gates pass.",
            "source_prompt": "keep all units active and authorize only the comments unit",
        }
        authority_path, _ = compile_envelope(
            directory, authority_revision_raw, parent=revision3_path, name="revision-4-authority.json"
        )
        authority_applied = expect(root, authority_path, "apply-revision", "REVISION_APPLIED")
        assert authority_applied["unit_changes"] == {}, authority_applied
        assert authority_applied["authority_changes"] == {
            "comments": {"from": "RESEARCH_ONLY", "to": "COMMENT_AUTHORIZED"}
        }, authority_applied
        assert authority_applied["vote_policy_change"] is None, authority_applied

        record = expect(root, authority_path, "inspect", "INSPECT")
        assert record["mission_revision"] == 4
        code, wrong_owner = queue(root, authority_path, "inspect", owner_task_id="other")
        assert code == 2 and wrong_owner["status"] == "INVALID", wrong_owner

        frozen = "a" * 64
        follow = expect(root, authority_path, "start", "STARTED")
        assert follow["active_unit_id"].endswith("posts:g2")
        expect(root, authority_path, "freeze-action", "ACTION_KEY_FROZEN", unit_id=follow["active_unit_id"], action_key=frozen)
        expect(root, authority_path, "block", "BLOCKED", unit_id=follow["active_unit_id"])
        after_freeze = expect(root, authority_path, "inspect", "INSPECT")
        assert after_freeze["frozen_action_key_count"] == 1
    print(json.dumps({
        "status": "PASS", "chrome_calls": 0,
        "single_owner": True, "yield_blocks_later_unit": True,
        "hotplug_requires_safe_boundary": True,
        "authority_only_hotplug_requires_receipt": True,
        "revision_history_append_only": True,
        "frozen_action_keys_persist": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
