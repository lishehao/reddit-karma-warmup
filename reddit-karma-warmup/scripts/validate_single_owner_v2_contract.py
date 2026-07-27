#!/usr/bin/env python3
"""Validate the compact single-owner Reddit Skill without network or Chrome."""

import hashlib
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
INTAKE_COMPILER = ROOT / "scripts" / "compile_startup_intake.py"
QUEUE = ROOT / "scripts" / "single_owner_queue.py"
BROWSER_LEDGER = ROOT / "scripts" / "validate_browser_step_ledger.py"
STARTUP_INTAKE = ROOT / "references" / "startup-intake.md"
RUNTIME_FENCE = ROOT / "scripts" / "runtime_fence.py"


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


def promote(shared: tuple[str, ...], now: str, proof: str) -> dict:
    return run(
        str(QUEUE), "presentation-promote", *shared,
        "--presentation-title", "Reddit 运营台",
        "--proof-sha256", proof,
        "--now-utc", now,
    )


def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    defaults = json.loads(DEFAULTS.read_text(encoding="utf-8"))
    version = manifest["version"]
    assert version == "2026.07.28.2"
    assert defaults["topology"]["chrome_owners"] == 1
    assert defaults["topology"]["cross_task_dispatch"] == "FORBIDDEN"
    assert defaults["scheduler"]["ordinary_trigger_tolerance_seconds"] == 300
    assert defaults["scheduler"]["heartbeat_interval_minutes"] == 15
    assert defaults["scheduler"]["unit_recheck_grid_minutes"] == 15
    assert defaults["scheduler"]["no_work_wake"] == "FAST_NOOP_NO_CHROME"
    assert defaults["scheduler"]["recheck_minutes"]["browsing"] == 30
    assert defaults["objective_linking"]["packet_outcome_is_not_objective_completion"] is True
    assert defaults["objective_linking"]["never_schedule_after_mission_cutoff"] is True
    assert defaults["schema"] == "reddit_single_owner_defaults/v14"
    intake_defaults = defaults["startup_intake"]
    assert intake_defaults["question_count"] == 3
    assert intake_defaults["request_user_input_auto_resolution"] == "OMIT_AUTO_RESOLUTION_MS"
    assert intake_defaults["completion"] == "ALL_THREE_EXPLICIT_OR_STARTUP_CANCELLED_BY_USER"
    assert intake_defaults["unanswered_or_partial"] == "WAITING_FOR_STARTUP_INPUT_NO_MISSION_QUEUE_HEARTBEAT_CHROME_OR_RESEARCH"
    assert intake_defaults["silence"] == "NEVER_IMPLICITLY_CANCELLED"
    assert intake_defaults["compiler"] == "scripts/compile_startup_intake.py"
    assert intake_defaults["compiler_success"] == "STARTUP_ANSWERS_COMPLETE"
    direction_defaults = defaults["direction_intake"]
    assert direction_defaults["question"] == "ONE_ACCOUNT_DIRECTION_PERSONA_AUDIENCE_TOPICS_AND_COMMUNITY_SEEDS_NOT_SEPARATE_FIELDS"
    assert direction_defaults["primary_presets"] == [
        "SOCIAL_AND_COMMUNITY",
        "PERSONAL_CREATION_AND_INDEPENDENT_PROJECTS",
        "SPATIAL_GAMES_AND_CO_CREATION",
    ]
    assert direction_defaults["community_scope"] == "OPTIONAL_SEED_COMMUNITIES_CLOSED_ONLY_IF_EXPLICIT_OTHERWISE_EXPANDABLE_OR_DISCOVER"
    assert direction_defaults["business_goal_source"] == "QUESTION_3_ACTION_SCOPE"
    assert direction_defaults["material_refs"] == "OPTIONAL_AT_STARTUP_MISSING_MATERIAL_PARKS_POSTS_LATER"
    action_scope_defaults = defaults["action_scope_intake"]
    assert action_scope_defaults["question"] == "USER_VISIBLE_ACTION_SCOPE_NOT_FREQUENCY_QUOTA_OR_INTERNAL_PROFILE"
    assert action_scope_defaults["primary_presets"] == [
        "SIMULATE_BROWSING", "DISCUSSION_PARTICIPATION", "FULL_PROGRESSION",
    ]
    assert action_scope_defaults["legacy_aliases"] == "INPUT_COMPATIBILITY_ONLY_NEVER_DISPLAY_IN_NEW_INTAKE"
    startup_transition = defaults["startup_transition"]
    assert startup_transition["question_two_completion"] == "DIRECTION_AND_IP_ONLY_NO_SCOPE_OR_MATERIAL_FOLLOWUP"
    assert startup_transition["missing_optional_defaults"] == "COMMUNITY_SCOPE_DISCOVER_OR_NAMED_SEEDS_EXPANDABLE_MATERIAL_REFS_EMPTY"
    assert startup_transition["answer_compilation"] == "LOCAL_THREE_ANSWER_COMPILER_BEFORE_RUNTIME_FENCE_NO_SECOND_ROUND"
    assert startup_transition["after_three_answers"] == "RUNTIME_FENCE_ENVELOPE_TECHNICAL_GATES_HEARTBEAT_READBACK_INITIAL_PACKET_SAME_TASK_TURN"
    assert startup_transition["initial_packet"] == "FORMAL_ROUND_ONE_NOT_PREVIEW_PLAN_OR_PREFILTER"
    assert startup_transition["technical_gates"] == "REQUIRED_BUT_NOT_A_SEPARATE_USER_DECISION_STAGE"
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
    assert defaults["runtime_fence"]["pending_chrome_release"] == "LEDGER_EVIDENCE_ONLY_NOT_A_LIVE_OCCUPANCY_PROOF"
    assert defaults["runtime_fence"]["stale_reconciliation"] == "LOCAL_IMMUTABLE_MARKER_NO_OLD_TASK_CHROME_OR_AUTOMATION_MUTATION"
    assert set(defaults["units"]) == {"browsing", "comments", "posts", "follow-up", "presence"}
    documents = [SKILL]
    repository_readme = ROOT.parent / "README.md"
    if repository_readme.is_file():
        documents.append(repository_readme)
    text = " ".join("\n".join(path.read_text(encoding="utf-8") for path in documents).split())
    for phrase in ("user-visible `Reddit 运营台`", "presentation-promote", "heartbeat-observe", "Official Reddit API", "Chrome", "MUTATION_INTENT", "±5 minutes", "fast NOOP", "browsing candidate pack -> comments/posts ACTION_ELIGIBLE", "BOOTSTRAP_READY", "high/low frequency", "business goal", "cleanup-grace", "exactly three", "Do not ask for an account", "STALE_RUNTIME", "ACTIVE_OWNER", "autoResolutionMs", "WAITING_FOR_STARTUP_INPUT", "STARTUP_ANSWERS_COMPLETE", "compile_startup_intake.py", "INITIAL formal packet", "preview or pre-filter"):
        assert phrase in text, phrase
    runtime = (ROOT / "references" / "single-owner-runtime.md").read_text(encoding="utf-8")
    guides = (ROOT / "references" / "unit-guides.md").read_text(encoding="utf-8")
    assert "ACTION_WINDOW_CLAMPED_TO_NEXT_GRID" in runtime
    for phrase in ("notLoaded", "chrome_release=PENDING", "runtime_fence.py --reconcile", "UNCERTAIN"):
        assert phrase in runtime, phrase
    assert "live_gate_checkpoint" in guides
    installed_text = " ".join(SKILL.read_text(encoding="utf-8").split())
    for phrase in ("browsing candidate pack -> comments/posts ACTION_ELIGIBLE", "BOOTSTRAP_READY", "MUTATION_INTENT"):
        assert phrase in installed_text, phrase
    assert "legacy_multi_lane_compat" not in text
    required = {"single-owner-runtime.md", "research-and-community-index.md", "chrome-and-actions.md", "unit-guides.md", "mission-goals-and-profiles.md", "startup-intake.md", "operation-defaults.json"}
    actual = {path.name for path in (ROOT / "references").iterdir()}
    assert actual == required, actual
    intake = STARTUP_INTAKE.read_text(encoding="utf-8")
    assert intake.count("## Question ") == 3
    for phrase in ("Do not ask for an account", "2 hours", "4 hours", "8 hours", "社交与社区", "个人创作与独立项目", "3D/游戏/共创", "one account direction", "not separate required fields", "Question 3", "模拟浏览", "参与讨论", "全面推进", "action scope", "MATERIAL_REQUIRED", "no fourth question", "autoResolutionMs", "WAITING_FOR_STARTUP_INPUT", "STARTUP_CANCELLED_BY_USER", "STARTUP_ANSWERS_COMPLETE", "compile_startup_intake.py", "silence never does", "do not ask a second-round question", "INITIAL formal packet", "not a preview, pre-filter, or separate planning round"):
        assert phrase in intake, phrase
    scripts = {path.name for path in (ROOT / "scripts").iterdir()}
    assert scripts == {"compile_startup_intake.py", "compile_single_owner_mission.py", "single_owner_queue.py", "community_index.py", "runtime_fence.py", "validate_browser_step_ledger.py", "validate_single_owner_v2_contract.py"}, scripts
    assert run(str(INTAKE_COMPILER), "--self-test")["status"] == "PASS"
    assert run(str(BROWSER_LEDGER), "--self-test")["status"] == "PASS"
    assert run(str(RUNTIME_FENCE), "--self-test")["status"] == "PASS"
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        status = run(str(INDEX), "--root", str(work / "index"), "status")
        assert status["status"] == "READY" and status["community_count"] == 0
        unavailable = run(str(INDEX), "--root", str(work / "index"), "refresh", "--subreddit", "r/SideProject")
        assert unavailable["status"] == "UNCONFIGURED_OFFICIAL_REDDIT_API"
        # Full startup path: exactly three answers -> normalized intake ->
        # immutable envelope -> scheduler receipt -> first formal packet.
        # No Chrome or Reddit call is performed by this simulation.
        startup_answers = work / "three-answers.json"
        startup_normalized = work / "startup-normalized.json"
        startup_answers.write_text(json.dumps({
            "duration_hours": 2,
            "direction": "个人创作与独立项目",
            "authority_profile": "参与讨论",
        }), encoding="utf-8")
        compiled_intake = run(str(INTAKE_COMPILER), "--input", str(startup_answers), "--output", str(startup_normalized))
        assert compiled_intake["status"] == "STARTUP_ANSWERS_COMPLETE"
        assert compiled_intake["normalized"]["mission_strategy"]["community_scope"] == "discover"
        assert compiled_intake["normalized"]["mission_strategy"]["material_refs"] == []
        assert compiled_intake["normalized"]["authority_profile"] == "discussion_participation"
        assert compiled_intake["normalized"]["requested_work_types"] == ["browsing", "comments"]
        partial_answers = work / "partial-answers.json"
        partial_answers.write_text(json.dumps({"duration_hours": 2}), encoding="utf-8")
        assert run(str(INTAKE_COMPILER), "--input", str(partial_answers))["status"] == "WAITING_FOR_STARTUP_INPUT"
        stale_evidence = work / "stale-runtime.json"
        stale_evidence.write_text(json.dumps({
            "owner_task_id": "019fa29e-2cb5-70d0-9519-b6d993fe7e71",
            "mission_id": "old-reddit-contract",
            "queue_state": "ACTIVE",
            "operation_stop_at": "2026-07-27T06:00:00Z",
            "task_state": "notLoaded",
            "heartbeat_state": "absent",
            "lock_state": "unheld",
        }), encoding="utf-8")
        fenced = run(str(RUNTIME_FENCE), "--input", str(stale_evidence), "--now-utc", "2026-07-27T08:00:00Z", "--reconcile", "--registry-root", str(work / "runtime-fence"))
        assert fenced["status"] == "STALE_RUNTIME" and fenced["reconciliation"] == "RECORDED"
        startup_source = work / "startup-mission.json"
        startup_envelope = work / "startup-envelope.json"
        startup_payload = dict(compiled_intake["normalized"])
        startup_payload.update({
            "mission_id": "three-answer-contract",
            "account": "u/example",
            "operation_start_at": "2026-07-27T08:00:00Z",
            "source_prompt": "three explicit startup answers",
        })
        startup_source.write_text(json.dumps(startup_payload), encoding="utf-8")
        startup_mission = run(str(COMPILER), "--input", str(startup_source), "--output", str(startup_envelope))
        assert startup_mission["selected_units"] == ["browsing", "comments"]
        startup_shared = ("--root", str(work / "startup-queue"), "--scope", "three-answer-contract", "--owner-task-id", "owner-startup", "--mission-envelope", str(startup_envelope))
        assert run(str(QUEUE), "bootstrap", *startup_shared, "--now-utc", "2026-07-27T08:00:00Z")["status"] == "BOOTSTRAPPED"
        startup_proof = "1" * 64
        assert promote(startup_shared, "2026-07-27T08:00:00Z", startup_proof)["status"] == "PRESENTATION_PROMOTED"
        assert run(str(QUEUE), "canary-pass", *startup_shared, "--proof-sha256", startup_proof)["status"] == "CANARY_PASSED"
        assert heartbeat_record(startup_shared, "2026-07-27T08:00:00Z", "2026-07-27T10:25:00Z", "2026-07-27T08:15:00Z", "owner-startup", startup_proof)["status"] == "HEARTBEAT_VERIFIED"
        initial_wake = run(str(QUEUE), "wake-open", *startup_shared, "--wake-source", "INITIAL", "--expected-at-utc", "2026-07-27T08:00:00Z", "--now-utc", "2026-07-27T08:01:00Z")
        assert initial_wake["status"] == "WAKE_OPEN" and initial_wake["due_units"] == ["browsing", "comments"]
        assert run(str(QUEUE), "decide", *startup_shared, "--unit", "browsing", "--decision", "RUN", "--reason", "first formal community research packet", "--now-utc", "2026-07-27T08:01:01Z")["status"] == "DECISION_RECORDED"
        assert run(str(QUEUE), "decide", *startup_shared, "--unit", "comments", "--decision", "DEFER", "--reason", "requires real upstream candidate evidence", "--now-utc", "2026-07-27T08:01:02Z")["status"] == "DECISION_RECORDED"
        first_packet = run(str(QUEUE), "start", *startup_shared, "--now-utc", "2026-07-27T08:01:03Z")
        assert first_packet["status"] == "PACKET_STARTED" and first_packet["unit"] == "browsing"
        assert run(str(QUEUE), "boundary-open", *startup_shared, "--boundary-id", "initial-read-1", "--boundary-kind", "DOM_READ", "--now-utc", "2026-07-27T08:01:04Z")["status"] == "BOUNDARY_OPEN"
        assert run(str(QUEUE), "boundary-settle", *startup_shared, "--boundary-id", "initial-read-1", "--boundary-outcome", "READ_OK", "--now-utc", "2026-07-27T08:01:05Z")["status"] == "BOUNDARY_SETTLED"
        initial_completed = run(str(QUEUE), "finish", *startup_shared, "--outcome", "COMPLETED", "--objective-state", "CANDIDATES_READY", "--objective-reason", "real first-packet community evidence", "--candidate-ref", "pack:initial:1", "--now-utc", "2026-07-27T08:01:06Z")
        assert initial_completed["status"] == "COMPLETED"
        assert initial_completed["objective_state"]["browsing"] == "CANDIDATES_READY"
        assert initial_completed["timer_policy"] == "CONTINUE_STABLE_RECURRENCE"
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
        shared = ("--root", str(queue_root), "--scope", "v2-contract", "--owner-task-id", "owner-1", "--mission-envelope", str(envelope))
        bootstrapped = run(str(QUEUE), "bootstrap", *shared, "--now-utc", "2026-07-27T00:00:00Z")
        assert bootstrapped["status"] == "BOOTSTRAPPED" and bootstrapped["due_units"] == ["browsing", "posts"]
        proof = "0" * 64
        assert run(str(QUEUE), "canary-pass", *shared, "--proof-sha256", proof)["status"] == "PRESENTATION_REQUIRED"
        assert promote(shared, "2026-07-27T00:00:00Z", proof)["status"] == "PRESENTATION_PROMOTED"
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
        observed = run(str(QUEUE), "heartbeat-observe", *shared, "--now-utc", "2026-07-27T00:00:02Z")
        assert observed["status"] == "HEARTBEAT_EARLY_OBSERVED"
        assert run(str(QUEUE), "wake-open", *shared, "--wake-source", "INITIAL", "--expected-at-utc", "2026-07-27T00:00:00Z", "--now-utc", "2026-07-27T00:04:59Z")["status"] == "WAKE_OPEN"
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
        assert run(str(QUEUE), "heartbeat-observe", *shared, "--now-utc", "2026-07-27T00:15:00Z")["status"] == "HEARTBEAT_OBSERVED"
        action_due = run(str(QUEUE), "wake-open", *shared, "--expected-at-utc", "2026-07-27T00:15:00Z", "--now-utc", "2026-07-27T00:15:00Z")
        assert action_due["status"] == "WAKE_OPEN" and action_due["due_units"] == ["posts"]
        action_defer = run(str(QUEUE), "decide", *shared, "--unit", "posts", "--decision", "DEFER", "--reason", "candidate packet first", "--now-utc", "2026-07-27T00:15:01Z")
        assert action_defer["scheduler_adjustment"] == "ACTION_WINDOW_CLAMPED_TO_NEXT_GRID"
        assert run(str(QUEUE), "start", *shared, "--now-utc", "2026-07-27T00:15:02Z")["status"] == "NO_PACKET"
        assert heartbeat_record(shared, "2026-07-27T00:15:03Z", "2026-07-27T02:25:00Z", "2026-07-27T00:30:00Z", "owner-1", proof)["status"] == "HEARTBEAT_VERIFIED"
        assert run(str(QUEUE), "heartbeat-observe", *shared, "--now-utc", "2026-07-27T00:20:00Z")["status"] == "HEARTBEAT_EARLY_OBSERVED"
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
        action_shared = ("--root", str(queue_root), "--scope", "objective-contract", "--owner-task-id", "owner-2", "--mission-envelope", str(action_envelope))
        boot = run(str(QUEUE), "bootstrap", *action_shared, "--now-utc", "2026-07-27T01:00:00Z")
        assert boot["objective_state"]["posts"] == "PENDING"
        assert boot["objective_state"]["comments"] == "PENDING"
        assert boot["objective_state"]["follow-up"] == "NOT_APPLICABLE"
        assert promote(action_shared, "2026-07-27T01:00:00Z", proof)["status"] == "PRESENTATION_PROMOTED"
        assert run(str(QUEUE), "canary-pass", *action_shared, "--proof-sha256", proof)["status"] == "CANARY_PASSED"
        assert heartbeat_record(action_shared, "2026-07-27T01:00:00Z", "2026-07-27T03:25:00Z", "2026-07-27T01:15:00Z", "owner-2", proof)["status"] == "HEARTBEAT_VERIFIED"
        assert run(str(QUEUE), "wake-open", *action_shared, "--wake-source", "INITIAL", "--expected-at-utc", "2026-07-27T01:00:00Z", "--now-utc", "2026-07-27T01:00:00Z")["status"] == "WAKE_OPEN"
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
        priority_shared = ("--root", str(queue_root), "--scope", "priority-contract", "--owner-task-id", "owner-3", "--mission-envelope", str(priority_envelope))
        run(str(QUEUE), "bootstrap", *priority_shared, "--now-utc", "2026-07-27T03:00:00Z")
        promote(priority_shared, "2026-07-27T03:00:00Z", proof)
        run(str(QUEUE), "canary-pass", *priority_shared, "--proof-sha256", proof)
        assert heartbeat_record(priority_shared, "2026-07-27T03:00:00Z", "2026-07-27T05:25:00Z", "2026-07-27T03:15:00Z", "owner-3", proof)["status"] == "HEARTBEAT_VERIFIED"
        run(str(QUEUE), "objective-set", *priority_shared, "--unit", "posts", "--objective-state", "ACTION_ELIGIBLE", "--objective-reason", "live route plus real material", "--source-ref", "route:verified:1", "--now-utc", "2026-07-27T03:00:01Z")
        assert run(str(QUEUE), "heartbeat-observe", *priority_shared, "--now-utc", "2026-07-27T03:15:00Z")["status"] == "HEARTBEAT_OBSERVED"
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
        expiry_shared = ("--root", str(queue_root), "--scope", "expiry-contract", "--owner-task-id", "owner-4", "--mission-envelope", str(expiry_envelope))
        run(str(QUEUE), "bootstrap", *expiry_shared, "--now-utc", "2026-07-27T04:00:00Z")
        promote(expiry_shared, "2026-07-27T04:00:00Z", proof)
        run(str(QUEUE), "canary-pass", *expiry_shared, "--proof-sha256", proof)
        assert heartbeat_record(expiry_shared, "2026-07-27T04:00:00Z", "2026-07-27T05:25:00Z", "2026-07-27T04:15:00Z", "owner-4", proof)["status"] == "HEARTBEAT_VERIFIED"
        assert run(str(QUEUE), "cleanup-open", *expiry_shared, "--cleanup-reason", "work still pending", "--now-utc", "2026-07-27T04:01:00Z")["status"] == "CLEANUP_NOT_DUE"
        assert run(str(QUEUE), "heartbeat-observe", *expiry_shared, "--now-utc", "2026-07-27T04:45:00Z")["status"] == "SCHEDULER_GAP_SUSPECTED"
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
        trigger_shared = ("--root", str(queue_root), "--scope", "trigger-contract", "--owner-task-id", "owner-5", "--mission-envelope", str(trigger_envelope))
        run(str(QUEUE), "bootstrap", *trigger_shared, "--now-utc", "2026-07-27T06:00:00Z")
        promote(trigger_shared, "2026-07-27T06:00:00Z", proof)
        run(str(QUEUE), "canary-pass", *trigger_shared, "--proof-sha256", proof)
        assert heartbeat_record(trigger_shared, "2026-07-27T06:00:00Z", "2026-07-27T07:25:00Z", "2026-07-27T06:15:00Z", "owner-5", proof)["status"] == "HEARTBEAT_VERIFIED"
        assert run(str(QUEUE), "heartbeat-observe", *trigger_shared, "--now-utc", "2026-07-27T06:09:00Z")["status"] == "HEARTBEAT_EARLY_OBSERVED"
        early = run(str(QUEUE), "wake-open", *trigger_shared, "--expected-at-utc", "2026-07-27T06:15:00Z", "--now-utc", "2026-07-27T06:09:00Z")
        assert early["status"] == "EARLY_WAKE_NOOP" and early["heartbeat"]["state"] == "NEEDS_READBACK"
        assert heartbeat_record(trigger_shared, "2026-07-27T06:09:01Z", "2026-07-27T07:25:00Z", "2026-07-27T06:15:00Z", "owner-5", proof)["status"] == "HEARTBEAT_VERIFIED"
        assert run(str(QUEUE), "heartbeat-observe", *trigger_shared, "--now-utc", "2026-07-27T06:21:00Z")["status"] == "HEARTBEAT_LATE_OBSERVED"
        late = run(str(QUEUE), "wake-open", *trigger_shared, "--expected-at-utc", "2026-07-27T06:15:00Z", "--now-utc", "2026-07-27T06:21:00Z")
        assert late["status"] == "WAKE_OPEN" and late["due_units"] == ["browsing"]
        assert run(str(QUEUE), "decide", *trigger_shared, "--unit", "browsing", "--decision", "RUN", "--reason", "recovery proof", "--now-utc", "2026-07-27T06:21:01Z")["status"] == "DECISION_RECORDED"
        assert run(str(QUEUE), "start", *trigger_shared, "--now-utc", "2026-07-27T06:21:02Z")["status"] == "PACKET_STARTED"
        assert run(str(QUEUE), "recover", *trigger_shared, "--recovery-reason", "lease still current", "--now-utc", "2026-07-27T06:21:03Z")["status"] == "RECOVERY_NOT_STALE"
        recovered = run(str(QUEUE), "recover", *trigger_shared, "--recovery-reason", "task resumed after lease", "--recovery-action-key", "1" * 64, "--now-utc", "2026-07-27T06:36:03Z")
        assert recovered["status"] == "RECOVERED_YIELDED" and recovered["frozen_action_key_count"] == 1 and recovered["due_units"] == ["browsing"]

        revised = work / "v2-revision.json"
        revised_payload = json.loads(envelope.read_text(encoding="utf-8"))
        revised_payload["mission_revision"] = 2
        revised_payload["mission_strategy"] = dict(revised_payload["mission_strategy"])
        revised_payload["mission_strategy"]["action_budget"] = "minimal"
        unsigned = dict(revised_payload)
        unsigned.pop("mission_envelope_sha256")
        revised_payload["mission_envelope_sha256"] = hashlib.sha256(
            json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        revised.write_text(json.dumps(revised_payload), encoding="utf-8")
        mismatch_shared = ("--root", str(queue_root), "--scope", "v2-contract", "--owner-task-id", "owner-1", "--mission-envelope", str(revised))
        assert run(str(QUEUE), "inspect", *mismatch_shared, "--now-utc", "2026-07-27T00:30:00Z")["status"] == "ENVELOPE_MISMATCH"
        wrong_scope = ("--root", str(queue_root), "--scope", "wrong-scope", "--owner-task-id", "owner-1", "--mission-envelope", str(envelope))
        assert run(str(QUEUE), "inspect", *wrong_scope, "--now-utc", "2026-07-27T00:30:01Z")["status"] == "MISSION_SCOPE_MISMATCH"
    print(json.dumps({"status": "PASS", "version": version, "single_owner": True, "api_get_only_optional": True, "chrome_live_gate_required": True, "legacy_files_removed": True}, sort_keys=True))


if __name__ == "__main__":
    main()
