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


def heartbeat_record(shared: tuple[str, ...], now: str, until: str, next_run: str, owner: str, proof: str) -> dict:
    rrule_until = until.replace("-", "").replace(":", "")
    return run(
        str(QUEUE), "heartbeat-record", *shared,
        "--automation-id", "automation-1",
        "--heartbeat-target-task-id", owner,
        "--heartbeat-rrule", f"FREQ=MINUTELY;INTERVAL=15;UNTIL={rrule_until}",
        "--heartbeat-until-at-utc", until,
        "--heartbeat-next-run-at-utc", next_run,
        "--proof-sha256", proof,
        "--now-utc", now,
    )


def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    defaults = json.loads(DEFAULTS.read_text(encoding="utf-8"))
    version = manifest["version"]
    assert version == "2026.07.27.11"
    assert defaults["topology"]["chrome_owners"] == 1
    assert defaults["topology"]["cross_task_dispatch"] == "FORBIDDEN"
    assert defaults["scheduler"]["ordinary_trigger_tolerance_seconds"] == 300
    assert defaults["scheduler"]["heartbeat_interval_minutes"] == 15
    assert defaults["scheduler"]["unit_recheck_grid_minutes"] == 15
    assert defaults["scheduler"]["no_work_wake"] == "FAST_NOOP_NO_CHROME"
    assert defaults["scheduler"]["recheck_minutes"]["browsing"] == 30
    assert defaults["objective_linking"]["packet_outcome_is_not_objective_completion"] is True
    assert defaults["objective_linking"]["never_schedule_after_mission_cutoff"] is True
    assert defaults["schema"] == "reddit_single_owner_defaults/v6"
    assert defaults["scheduler"]["wake_lease_seconds"] == 900
    assert defaults["scheduler"]["packet_lease_seconds"] == 900
    assert "HEARTBEAT" in defaults["scheduler"]["heartbeat_receipt"]
    assert set(defaults["mission_profiles"]["business_goals"]) == {
        "community_discovery", "conversation_entry", "feedback_validation",
        "project_distribution", "relationship_maintenance", "profile_readiness",
    }
    assert defaults["mission_profiles"]["frequency_aliases"]["high"]["coverage_budget"] == "broad"
    assert defaults["mission_profiles"]["frequency_aliases"]["low"]["action_threshold"] == "high"
    assert defaults["research"]["community_index"]["methods"] == ["GET"]
    assert defaults["research"]["community_index"]["account_or_write_endpoints"] == "FORBIDDEN"
    assert defaults["research"]["web_search"]["posts_query_min"] >= 8
    assert set(defaults["units"]) == {"browsing", "comments", "posts", "follow-up", "presence"}
    documents = [SKILL]
    repository_readme = ROOT.parent / "README.md"
    if repository_readme.is_file():
        documents.append(repository_readme)
    text = " ".join("\n".join(path.read_text(encoding="utf-8") for path in documents).split())
    for phrase in ("user-visible `Reddit 运营台`", "Official Reddit API", "Chrome", "MUTATION_INTENT", "±5 minutes", "fast NOOP", "browsing candidate pack -> comments/posts ACTION_ELIGIBLE", "BOOTSTRAP_READY", "high/low frequency", "business goal", "cleanup-grace"):
        assert phrase in text, phrase
    runtime = (ROOT / "references" / "single-owner-runtime.md").read_text(encoding="utf-8")
    guides = (ROOT / "references" / "unit-guides.md").read_text(encoding="utf-8")
    assert "ACTION_WINDOW_CLAMPED_TO_NEXT_GRID" in runtime
    assert "live_gate_checkpoint" in guides
    installed_text = " ".join(SKILL.read_text(encoding="utf-8").split())
    for phrase in ("browsing candidate pack -> comments/posts ACTION_ELIGIBLE", "BOOTSTRAP_READY", "MUTATION_INTENT"):
        assert phrase in installed_text, phrase
    assert "legacy_multi_lane_compat" not in text
    required = {"single-owner-runtime.md", "research-and-community-index.md", "chrome-and-actions.md", "unit-guides.md", "mission-goals-and-profiles.md", "operation-defaults.json"}
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
        source.write_text(json.dumps({"mission_id": "v2-contract", "account": "u/example", "direction": "truthful research", "operation_start_at": "2026-07-27T00:00:00Z", "duration_hours": 2, "requested_work_types": ["browsing", "posts"], "unit_authority": {"posts": "POST_AUTHORIZED"}, "authorization_receipt": "explicit post authority", "mission_strategy": {"business_goal": "project_distribution", "community_scope": "discover", "frequency": "high", "action_threshold": "high", "material_refs": ["https://example.test/project"], "planning_targets": {"eligible_routes": 1, "verified_actions": 1}}, "source_prompt": "compact one task"}), encoding="utf-8")
        compiled = run(str(COMPILER), "--input", str(source), "--output", str(envelope))
        assert compiled["selected_units"] == ["browsing", "posts"]
        assert compiled["mission_strategy"]["business_goal"] == "project_distribution"
        assert compiled["mission_strategy"]["coverage_budget"] == "broad"
        assert compiled["mission_strategy"]["action_threshold"] == "high"
        unchanged_source = work / "unchanged-revision.json"
        unchanged_source.write_text(json.dumps({"source_prompt": "same mission with no policy change"}), encoding="utf-8")
        unchanged = run(str(COMPILER), "--input", str(unchanged_source), "--parent-envelope", str(envelope))
        assert unchanged["status"] == "INVALID" and "strategy change" in unchanged["error"], unchanged
        queue_root = work / "queue"
        shared = ("--root", str(queue_root), "--scope", "v2", "--owner-task-id", "owner-1", "--mission-envelope", str(envelope))
        bootstrapped = run(str(QUEUE), "bootstrap", *shared, "--now-utc", "2026-07-27T00:00:00Z")
        assert bootstrapped["status"] == "BOOTSTRAPPED" and bootstrapped["due_units"] == ["browsing", "posts"]
        proof = "0" * 64
        assert run(str(QUEUE), "canary-pass", *shared, "--proof-sha256", proof)["status"] == "CANARY_PASSED"
        assert run(str(QUEUE), "wake-open", *shared, "--expected-at-utc", "2026-07-27T00:00:00Z", "--now-utc", "2026-07-27T00:00:00Z")["status"] == "MISSION_SCHEDULER_UNVERIFIED"
        bad_timer = run(
            str(QUEUE), "heartbeat-record", *shared,
            "--automation-id", "automation-1",
            "--heartbeat-target-task-id", "owner-1",
            "--heartbeat-rrule", "FREQ=MINUTELY;INTERVAL=15;COUNT=1;UNTIL=20260727T022500Z",
            "--heartbeat-until-at-utc", "2026-07-27T02:25:00Z",
            "--heartbeat-next-run-at-utc", "2026-07-27T00:15:00Z",
            "--proof-sha256", proof,
            "--now-utc", "2026-07-27T00:00:01Z",
        )
        assert bad_timer["status"] == "INVALID" and "heartbeat_rrule" in bad_timer["error"]
        recorded = heartbeat_record(shared, "2026-07-27T00:00:01Z", "2026-07-27T02:25:00Z", "2026-07-27T00:15:00Z", "owner-1", proof)
        assert recorded["status"] == "HEARTBEAT_VERIFIED" and recorded["heartbeat"]["next_run_at_utc"] == "2026-07-27T00:15:00Z"
        assert run(str(QUEUE), "wake-open", *shared, "--expected-at-utc", "2026-07-27T00:00:00Z", "--now-utc", "2026-07-27T00:04:59Z")["status"] == "WAKE_OPEN"
        assert run(str(QUEUE), "decide", *shared, "--unit", "browsing", "--decision", "RUN", "--reason", "read current context", "--now-utc", "2026-07-27T00:05:00Z")["status"] == "DECISION_RECORDED"
        assert run(str(QUEUE), "decide", *shared, "--unit", "posts", "--decision", "DEFER", "--reason", "not due for one packet", "--now-utc", "2026-07-27T00:05:01Z")["status"] == "DECISION_RECORDED"
        started = run(str(QUEUE), "start", *shared, "--now-utc", "2026-07-27T00:05:02Z")
        assert started["status"] == "PACKET_STARTED" and started["unit"] == "browsing"
        assert run(str(QUEUE), "boundary-open", *shared, "--boundary-id", "read-1", "--boundary-kind", "DOM_READ", "--now-utc", "2026-07-27T00:05:03Z")["status"] == "BOUNDARY_OPEN"
        assert run(str(QUEUE), "boundary-settle", *shared, "--boundary-id", "read-1", "--boundary-outcome", "READ_OK", "--now-utc", "2026-07-27T00:05:04Z")["status"] == "BOUNDARY_SETTLED"
        completed = run(str(QUEUE), "finish", *shared, "--outcome", "COMPLETED", "--objective-state", "CANDIDATES_READY", "--objective-reason", "dated candidate pack", "--candidate-ref", "pack:sideproject:1", "--now-utc", "2026-07-27T00:05:05Z")
        assert completed["status"] == "COMPLETED"
        assert completed["heartbeat_interval_minutes"] == 15
        assert completed["timer_policy"] == "CONTINUE_STABLE_RECURRENCE"
        assert completed["objective_state"]["browsing"] == "CANDIDATES_READY"
        assert completed["next_due_at_utc"]["browsing"] == "2026-07-27T00:45:00Z"
        assert completed["next_due_at_utc"]["posts"] == "2026-07-27T00:15:00Z"
        assert completed["mission_strategy"]["action_budget"] == "active"
        assert completed["heartbeat"]["state"] == "NEEDS_READBACK"
        assert heartbeat_record(shared, "2026-07-27T00:05:06Z", "2026-07-27T02:25:00Z", "2026-07-27T00:15:00Z", "owner-1", proof)["status"] == "HEARTBEAT_VERIFIED"
        action_due = run(str(QUEUE), "wake-open", *shared, "--expected-at-utc", "2026-07-27T00:15:00Z", "--now-utc", "2026-07-27T00:15:00Z")
        assert action_due["status"] == "WAKE_OPEN" and action_due["due_units"] == ["posts"]
        action_defer = run(str(QUEUE), "decide", *shared, "--unit", "posts", "--decision", "DEFER", "--reason", "candidate packet first", "--now-utc", "2026-07-27T00:15:01Z")
        assert action_defer["scheduler_adjustment"] == "ACTION_WINDOW_CLAMPED_TO_NEXT_GRID"
        assert run(str(QUEUE), "start", *shared, "--now-utc", "2026-07-27T00:15:02Z")["status"] == "NO_PACKET"
        assert heartbeat_record(shared, "2026-07-27T00:15:03Z", "2026-07-27T02:25:00Z", "2026-07-27T00:30:00Z", "owner-1", proof)["status"] == "HEARTBEAT_VERIFIED"
        no_work = run(str(QUEUE), "wake-open", *shared, "--expected-at-utc", "2026-07-27T00:20:00Z", "--now-utc", "2026-07-27T00:20:00Z")
        assert no_work["status"] == "NOOP" and no_work["due_units"] == []
        assert no_work["heartbeat"]["state"] == "NEEDS_READBACK"
        action_source = work / "action-mission.json"
        action_envelope = work / "action-envelope.json"
        action_source.write_text(json.dumps({
            "mission_id": "objective-contract",
            "account": "u/example",
            "direction": "truthful action", 
            "operation_start_at": "2026-07-27T01:00:00Z",
            "duration_hours": 2,
            "requested_work_types": ["comments", "posts", "follow-up", "presence"],
            "unit_authority": {"comments": "COMMENT_AUTHORIZED", "posts": "POST_AUTHORIZED", "follow-up": "FOLLOWUP_AUTHORIZED", "presence": "PRESENCE_AUTHORIZED"},
            "authorization_receipt": "explicit user authorization",
            "source_prompt": "compact objective graph"
        }), encoding="utf-8")
        run(str(COMPILER), "--input", str(action_source), "--output", str(action_envelope))
        action_shared = ("--root", str(queue_root), "--scope", "objectives", "--owner-task-id", "owner-2", "--mission-envelope", str(action_envelope))
        boot = run(str(QUEUE), "bootstrap", *action_shared, "--now-utc", "2026-07-27T01:00:00Z")
        assert boot["objective_state"]["posts"] == "PENDING"
        assert boot["objective_state"]["comments"] == "PENDING"
        assert boot["objective_state"]["follow-up"] == "NOT_APPLICABLE"
        assert run(str(QUEUE), "canary-pass", *action_shared, "--proof-sha256", proof)["status"] == "CANARY_PASSED"
        assert heartbeat_record(action_shared, "2026-07-27T01:00:00Z", "2026-07-27T03:25:00Z", "2026-07-27T01:15:00Z", "owner-2", proof)["status"] == "HEARTBEAT_VERIFIED"
        assert run(str(QUEUE), "wake-open", *action_shared, "--expected-at-utc", "2026-07-27T01:00:00Z", "--now-utc", "2026-07-27T01:00:00Z")["status"] == "WAKE_OPEN"
        assert run(str(QUEUE), "decide", *action_shared, "--unit", "comments", "--decision", "DEFER", "--reason", "post audit first", "--now-utc", "2026-07-27T01:00:01Z")["status"] == "DECISION_RECORDED"
        assert run(str(QUEUE), "decide", *action_shared, "--unit", "posts", "--decision", "RUN", "--reason", "one truthful audit", "--now-utc", "2026-07-27T01:00:02Z")["status"] == "DECISION_RECORDED"
        started = run(str(QUEUE), "start", *action_shared, "--now-utc", "2026-07-27T01:00:03Z")
        assert started["status"] == "PACKET_STARTED" and started["unit"] == "posts"
        required = run(str(QUEUE), "finish", *action_shared, "--outcome", "COMPLETED", "--now-utc", "2026-07-27T01:00:04Z")
        assert required["status"] == "OBJECTIVE_STATE_REQUIRED"
        parked = run(str(QUEUE), "finish", *action_shared, "--outcome", "COMPLETED", "--objective-state", "MATERIAL_REQUIRED", "--objective-reason", "no truthful material supplied", "--now-utc", "2026-07-27T01:00:05Z")
        assert parked["objective_state"]["posts"] == "MATERIAL_REQUIRED"
        assert parked["next_due_at_utc"]["posts"] is None and "posts" not in parked["due_units"]
        comment_armed = run(str(QUEUE), "objective-set", *action_shared, "--unit", "comments", "--objective-state", "ACTION_ELIGIBLE", "--objective-reason", "browsing candidate pack", "--source-ref", "pack:sideproject:1", "--now-utc", "2026-07-27T01:00:06Z")
        assert comment_armed["objective_state"]["comments"] == "ACTION_ELIGIBLE"
        assert comment_armed["next_due_at_utc"]["comments"] == "2026-07-27T01:15:00Z"
        rearmed = run(str(QUEUE), "objective-set", *action_shared, "--unit", "posts", "--objective-state", "ACTION_ELIGIBLE", "--objective-reason", "truthful material supplied", "--source-ref", "material:verified:1", "--now-utc", "2026-07-27T01:00:07Z")
        assert rearmed["objective_state"]["posts"] == "ACTION_ELIGIBLE"
        verified = run(str(QUEUE), "objective-set", *action_shared, "--unit", "posts", "--objective-state", "ACTION_VERIFIED", "--objective-reason", "post visible after reload", "--objective-evidence-sha256", proof, "--source-ref", "https://www.reddit.com/r/example/comments/abc", "--now-utc", "2026-07-27T01:00:08Z")
        assert verified["objective_state"]["posts"] == "ACTION_VERIFIED"
        armed = run(str(QUEUE), "objective-set", *action_shared, "--unit", "follow-up", "--objective-state", "ACTION_ELIGIBLE", "--objective-reason", "verified own permalink", "--source-ref", "https://www.reddit.com/r/example/comments/abc", "--now-utc", "2026-07-27T01:00:09Z")
        assert armed["status"] == "OBJECTIVE_RECORDED"
        assert armed["objective_state"]["follow-up"] == "ACTION_ELIGIBLE"
        assert armed["next_due_at_utc"]["follow-up"] == "2026-07-27T01:15:00Z", armed
        priority_source = work / "priority-mission.json"
        priority_envelope = work / "priority-envelope.json"
        priority_source.write_text(json.dumps({
            "mission_id": "priority-contract",
            "account": "u/example",
            "direction": "truthful launch",
            "operation_start_at": "2026-07-27T03:00:00Z",
            "duration_hours": 2,
            "requested_work_types": ["browsing", "posts"],
            "unit_authority": {"posts": "POST_AUTHORIZED"},
            "authorization_receipt": "explicit post authority",
            "mission_strategy": {"business_goal": "project_distribution", "community_scope": "discover", "coverage_budget": "broad", "action_threshold": "high", "action_budget": "standard", "material_refs": ["https://example.test/project"], "planning_targets": {"eligible_routes": 1}},
            "source_prompt": "prioritize an eligible truthful post"
        }), encoding="utf-8")
        run(str(COMPILER), "--input", str(priority_source), "--output", str(priority_envelope))
        priority_shared = ("--root", str(queue_root), "--scope", "priority", "--owner-task-id", "owner-3", "--mission-envelope", str(priority_envelope))
        run(str(QUEUE), "bootstrap", *priority_shared, "--now-utc", "2026-07-27T03:00:00Z")
        run(str(QUEUE), "canary-pass", *priority_shared, "--proof-sha256", proof)
        assert heartbeat_record(priority_shared, "2026-07-27T03:00:00Z", "2026-07-27T05:25:00Z", "2026-07-27T03:15:00Z", "owner-3", proof)["status"] == "HEARTBEAT_VERIFIED"
        run(str(QUEUE), "objective-set", *priority_shared, "--unit", "posts", "--objective-state", "ACTION_ELIGIBLE", "--objective-reason", "live route plus real material", "--source-ref", "route:verified:1", "--now-utc", "2026-07-27T03:00:01Z")
        priority_wake = run(str(QUEUE), "wake-open", *priority_shared, "--expected-at-utc", "2026-07-27T03:15:00Z", "--now-utc", "2026-07-27T03:15:00Z")
        assert priority_wake["due_units"][:2] == ["posts", "browsing"], priority_wake

        expiry_source = work / "expiry-mission.json"
        expiry_envelope = work / "expiry-envelope.json"
        expiry_source.write_text(json.dumps({
            "mission_id": "expiry-contract",
            "account": "u/example",
            "direction": "bounded post decision",
            "operation_start_at": "2026-07-27T04:00:00Z",
            "duration_hours": 1,
            "requested_work_types": ["posts"],
            "unit_authority": {"posts": "POST_AUTHORIZED"},
            "authorization_receipt": "explicit post authority",
            "source_prompt": "deadline action window"
        }), encoding="utf-8")
        run(str(COMPILER), "--input", str(expiry_source), "--output", str(expiry_envelope))
        expiry_shared = ("--root", str(queue_root), "--scope", "expiry", "--owner-task-id", "owner-4", "--mission-envelope", str(expiry_envelope))
        run(str(QUEUE), "bootstrap", *expiry_shared, "--now-utc", "2026-07-27T04:00:00Z")
        run(str(QUEUE), "canary-pass", *expiry_shared, "--proof-sha256", proof)
        assert heartbeat_record(expiry_shared, "2026-07-27T04:00:00Z", "2026-07-27T05:25:00Z", "2026-07-27T04:15:00Z", "owner-4", proof)["status"] == "HEARTBEAT_VERIFIED"
        assert run(str(QUEUE), "cleanup-open", *expiry_shared, "--cleanup-reason", "work still pending", "--now-utc", "2026-07-27T04:01:00Z")["status"] == "CLEANUP_NOT_DUE"
        assert run(str(QUEUE), "wake-open", *expiry_shared, "--expected-at-utc", "2026-07-27T04:45:00Z", "--now-utc", "2026-07-27T04:45:00Z")["status"] == "WAKE_OPEN"
        expired = run(str(QUEUE), "decide", *expiry_shared, "--unit", "posts", "--decision", "DEFER", "--reason", "no action window remains", "--now-utc", "2026-07-27T04:45:01Z")
        assert expired["status"] == "DECISION_RECORDED" and expired["scheduler_adjustment"] == "ACTION_WINDOW_EXPIRED"
        expired_settled = run(str(QUEUE), "start", *expiry_shared, "--now-utc", "2026-07-27T04:45:02Z")
        assert expired_settled["status"] == "NO_PACKET" and expired_settled["next_due_at_utc"]["posts"] is None
        assert run(str(QUEUE), "wake-open", *expiry_shared, "--expected-at-utc", "2026-07-27T05:00:00Z", "--now-utc", "2026-07-27T05:00:00Z")["status"] == "MISSION_STOPPED"
        assert run(str(QUEUE), "cleanup-open", *expiry_shared, "--cleanup-reason", "mission deadline", "--now-utc", "2026-07-27T05:00:01Z")["status"] == "CLEANUP_OPEN"
        assert run(str(QUEUE), "retire", *expiry_shared, "--now-utc", "2026-07-27T05:00:02Z")["status"] == "RETIRE_BLOCKED"
        assert run(str(QUEUE), "release-tabs", *expiry_shared, "--proof-sha256", proof, "--now-utc", "2026-07-27T05:00:03Z")["status"] == "TABS_RELEASED"
        assert run(str(QUEUE), "retire", *expiry_shared, "--now-utc", "2026-07-27T05:00:04Z")["status"] == "RETIRE_BLOCKED"
        assert run(str(QUEUE), "heartbeat-delete", *expiry_shared, "--proof-sha256", proof, "--now-utc", "2026-07-27T05:00:05Z")["status"] == "HEARTBEAT_DELETED"
        assert run(str(QUEUE), "retire", *expiry_shared, "--now-utc", "2026-07-27T05:00:06Z")["status"] == "RETIRED"

        trigger_source = work / "trigger-mission.json"
        trigger_envelope = work / "trigger-envelope.json"
        trigger_source.write_text(json.dumps({
            "mission_id": "trigger-contract",
            "account": "u/example",
            "direction": "timing classification",
            "operation_start_at": "2026-07-27T06:00:00Z",
            "duration_hours": 1,
            "requested_work_types": ["browsing"],
            "authorization_receipt": "read only",
            "source_prompt": "early late heartbeat"
        }), encoding="utf-8")
        run(str(COMPILER), "--input", str(trigger_source), "--output", str(trigger_envelope))
        trigger_shared = ("--root", str(queue_root), "--scope", "trigger", "--owner-task-id", "owner-5", "--mission-envelope", str(trigger_envelope))
        run(str(QUEUE), "bootstrap", *trigger_shared, "--now-utc", "2026-07-27T06:00:00Z")
        run(str(QUEUE), "canary-pass", *trigger_shared, "--proof-sha256", proof)
        assert heartbeat_record(trigger_shared, "2026-07-27T06:00:00Z", "2026-07-27T07:25:00Z", "2026-07-27T06:15:00Z", "owner-5", proof)["status"] == "HEARTBEAT_VERIFIED"
        early = run(str(QUEUE), "wake-open", *trigger_shared, "--expected-at-utc", "2026-07-27T06:15:00Z", "--now-utc", "2026-07-27T06:09:00Z")
        assert early["status"] == "EARLY_WAKE_NOOP" and early["heartbeat"]["state"] == "NEEDS_READBACK"
        assert heartbeat_record(trigger_shared, "2026-07-27T06:09:01Z", "2026-07-27T07:25:00Z", "2026-07-27T06:15:00Z", "owner-5", proof)["status"] == "HEARTBEAT_VERIFIED"
        late = run(str(QUEUE), "wake-open", *trigger_shared, "--expected-at-utc", "2026-07-27T06:15:00Z", "--now-utc", "2026-07-27T06:21:00Z")
        assert late["status"] == "WAKE_OPEN" and late["due_units"] == ["browsing"]
        assert run(str(QUEUE), "decide", *trigger_shared, "--unit", "browsing", "--decision", "RUN", "--reason", "recovery proof", "--now-utc", "2026-07-27T06:21:01Z")["status"] == "DECISION_RECORDED"
        assert run(str(QUEUE), "start", *trigger_shared, "--now-utc", "2026-07-27T06:21:02Z")["status"] == "PACKET_STARTED"
        assert run(str(QUEUE), "recover", *trigger_shared, "--recovery-reason", "lease still current", "--now-utc", "2026-07-27T06:21:03Z")["status"] == "RECOVERY_NOT_STALE"
        recovered = run(str(QUEUE), "recover", *trigger_shared, "--recovery-reason", "task resumed after lease", "--recovery-action-key", "1" * 64, "--now-utc", "2026-07-27T06:36:03Z")
        assert recovered["status"] == "RECOVERED_YIELDED" and recovered["frozen_action_key_count"] == 1 and recovered["due_units"] == ["browsing"]

        mismatch_shared = ("--root", str(queue_root), "--scope", "v2", "--owner-task-id", "owner-1", "--mission-envelope", str(trigger_envelope))
        assert run(str(QUEUE), "inspect", *mismatch_shared, "--now-utc", "2026-07-27T00:30:00Z")["status"] == "ENVELOPE_MISMATCH"
    print(json.dumps({"status": "PASS", "version": version, "single_owner": True, "api_get_only_optional": True, "chrome_live_gate_required": True, "legacy_files_removed": True}, sort_keys=True))


if __name__ == "__main__":
    main()
