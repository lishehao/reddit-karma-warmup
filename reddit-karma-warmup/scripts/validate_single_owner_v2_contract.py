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
    assert version == "2026.08.04.1"
    assert defaults["runtime_protocol_version"] == version
    assert defaults["runtime_evidence_policy"] == {
        "normal_receipts": "OPAQUE_TOKEN_NO_SHA256_FORMAT_CHECK",
        "sha256_scope": "PACKAGE_MANIFEST_AND_MISSION_ENVELOPE_BOUNDARIES_ONLY",
        "legacy_sha256_field_names": "ACCEPT_AS_OPAQUE_TOKENS",
    }
    upgrade = defaults["upgrade"]
    assert upgrade["default_mode"] == "ATOMIC_HOT_REPLACE"
    assert upgrade["compatible_active_runtime"] == "HOT_REPLACE_WHILE_MISSION_REMAINS_PINNED_TO_RECORDED_PROTOCOL_AND_NO_MUTATION_IS_IN_FLIGHT"
    assert upgrade["defer_only"] == ["INCOMPATIBLE_SCHEMA_OR_QUEUE_PROTOCOL", "IN_FLIGHT_MUTATION_UNSETTLED", "UNCERTAIN_RUNTIME_FACTS"]
    assert upgrade["remote_newer_status"] == "REMOTE_NEWER_DEFERRED_NOT_NOOP"
    assert upgrade["pending_apply"] == "FIRST_PROVEN_RELEASE_BOUNDARY"
    assert defaults["topology"]["chrome_owners"] == 1
    assert defaults["topology"]["cross_task_dispatch"] == "FORBIDDEN"
    assert defaults["topology"]["owner_task_binding"] == "EXACT_CURRENT_TASK_ID_ONLY_NEVER_DELEGATION_SOURCE_THREAD_ID"
    assert defaults["topology"]["owner_task_unavailable"] == "USE_CURRENT_TASK_CONTEXT_NO_CROSS_TASK_LOOKUP"
    assert defaults["scheduler"]["ordinary_trigger_tolerance_seconds"] == 300
    assert defaults["scheduler"]["heartbeat_interval_minutes"] == 15
    assert defaults["scheduler"]["unit_recheck_grid_minutes"] == 15
    assert defaults["scheduler"]["no_work_wake"] == "FAST_NOOP_NO_CHROME_ONLY_FOR_EARLY_DUPLICATE_RECOVERY_OR_EXHAUSTED_FRONTIER"
    assert defaults["scheduler"]["runtime_timeout_policy"] == "CHROME_OR_DOM_TIMEOUT_YIELDS_LIVE_GATE_UNVERIFIED_NOT_RULE_BLOCKED_AND_NEXT_DUE_RUNS_RECOVERY_PROBE"
    assert defaults["scheduler"]["unit_recheck_phase"] == "ALIGN_TO_TASK_HEARTBEAT_PHASE_WHEN_AVAILABLE_NEVER_ABSOLUTE_UTC_QUARTER_HOURS"
    assert defaults["scheduler"]["late_wake"] == "RUN_AT_MOST_ONE_CURRENTLY_DUE_UNIT_NO_CATCH_UP_MEANS_NO_REPLAY_NOT_SKIP"
    assert defaults["scheduler"]["recoverable_runtime_failure"] == "NEXT_DUE_DECISION_MUST_RUN_RECOVERY_FIRST_NOT_SKIP_WATCH_DEFER_OR_FAST_NOOP"
    assert defaults["scheduler"]["heartbeat_prompt"] == "IDENTITY_AND_BOUNDARIES_ONLY_LOAD_INSTALLED_SKILL_AND_QUEUE_AT_EACH_WAKE_NO_EMBEDDED_CADENCE_OR_NOOP_POLICY"
    assert defaults["scheduler"]["recheck_minutes"]["browsing"] == 30
    chrome_defaults = defaults["chrome"]
    assert chrome_defaults["outer_operation_budget_ms"] == 120000
    assert chrome_defaults["outer_budget_policy"] == "USE_ONLY_WHEN_CURRENT_WRAPPER_SUPPORTS_EXPLICIT_PER_CALL_TIMEOUT"
    assert chrome_defaults["startup_neutral_probe_limit"] == 2
    assert chrome_defaults["startup_neutral_probe_urls"] == ["https://example.com/", "https://www.iana.org/domains/reserved/"]
    assert chrome_defaults["reconnect_limit_after_explicit_disconnect"] == 1
    assert chrome_defaults["timeout_readback"] == "METADATA_IMMEDIATELY_BEFORE_ANY_NEW_NAVIGATION_OR_FRESH_TAB_CLAIM"
    assert chrome_defaults["global_neutral_failure"] == "CHROME_CONTENT_CHANNEL_TIMEOUT_GLOBAL_SUSPECTED_NETWORK_EXTENSION_OR_RENDERER_UNRESOLVED"
    assert chrome_defaults["route_failure_after_neutral_success"] == "REDDIT_ROUTE_OR_CLIENT_FILTER_SUSPECTED"
    assert chrome_defaults["cua_address_bar_after_neutral_goto_timeout"] == "FORBIDDEN"
    assert defaults["objective_linking"]["packet_outcome_is_not_objective_completion"] is True
    assert defaults["objective_linking"]["never_schedule_after_mission_cutoff"] is True
    assert defaults["objective_linking"]["recoverable_states"] == ["LIVE_GATE_UNVERIFIED"]
    assert defaults["objective_linking"]["candidate_rejection"] == "EXACT_CANDIDATE_OR_COMMUNITY_REJECTION_RETURNS_TO_BROWSING_NEXT_HEARTBEAT_AND_CANNOT_BE_REARMED"
    assert defaults["objective_linking"]["rule_block_scope"] == "RULE_BLOCKED_REQUIRES_MISSION_WIDE_EVIDENCE_CANDIDATE_OR_COMMUNITY_BLOCK_USES_CANDIDATE_REJECT"
    assert defaults["objective_linking"]["material_block_scope"] == "MATERIAL_REQUIRED_REQUIRES_MISSION_WIDE_ALL_FORMAT_AUDIT_AND_EVIDENCE"
    assert defaults["schema"] == "reddit_single_owner_defaults/v16"
    intake_defaults = defaults["startup_intake"]
    assert intake_defaults["question_count"] == 3
    assert intake_defaults["request_user_input_auto_resolution"] == "OMIT_AUTO_RESOLUTION_MS"
    assert intake_defaults["interactive_form_attempts"] == 1
    assert intake_defaults["unanswered_form_fallback"] == "DIRECT_TEXT_LIST_ALL_THREE_QUESTIONS_NO_REQUEST_USER_INPUT_REPEAT"
    assert intake_defaults["partial_reply_fallback"] == "DIRECT_TEXT_LIST_ALL_THREE_QUESTIONS_WITH_RECOGNIZED_AND_MISSING_FIELDS"
    assert intake_defaults["completion"] == "ALL_THREE_EXPLICIT_OR_STARTUP_CANCELLED_BY_USER"
    assert intake_defaults["unanswered_or_partial"] == "WAITING_FOR_STARTUP_INPUT_NO_MISSION_QUEUE_HEARTBEAT_CHROME_OR_RESEARCH"
    assert intake_defaults["silence"] == "NEVER_IMPLICITLY_CANCELLED"
    assert intake_defaults["compiler"] == "scripts/compile_startup_intake.py"
    assert intake_defaults["compiler_success"] == "STARTUP_ANSWERS_COMPLETE"
    assert intake_defaults["session_identity"] == "SILENT_CHROME_DERIVATION_AT_STARTUP_RECHECK_ONLY_ON_REBIND_LOGIN_CHANGE_RECOVERY_STALE_CHECKPOINT_OR_PRE_MUTATION_NO_HANDLE_IN_RECEIPTS"
    direction_defaults = defaults["direction_intake"]
    assert direction_defaults["question"] == "ONE_OPERATING_DIRECTION_PERSONA_AUDIENCE_TOPICS_AND_COMMUNITY_SEEDS_NOT_SEPARATE_FIELDS"
    assert direction_defaults["primary_presets"] == [
        "SOCIAL_AND_COMMUNITY",
        "PERSONAL_CREATION_AND_INDEPENDENT_PROJECTS",
        "SPATIAL_GAMES_AND_CO_CREATION",
    ]
    assert direction_defaults["community_scope"] == "OPTIONAL_SEED_COMMUNITIES_CLOSED_ONLY_IF_EXPLICIT_OTHERWISE_EXPANDABLE_OR_DISCOVER"
    assert direction_defaults["business_goal_source"] == "QUESTION_3_ACTION_SCOPE"
    assert direction_defaults["material_refs"] == "OPTIONAL_AT_STARTUP_MISSING_LINK_REQUIRES_TRUTHFUL_FORMAT_AUDIT_NOT_AUTOMATIC_POST_PARKING"
    action_scope_defaults = defaults["action_scope_intake"]
    assert action_scope_defaults["question"] == "USER_VISIBLE_ACTION_SCOPE_NOT_FREQUENCY_QUOTA_OR_INTERNAL_PROFILE"
    assert action_scope_defaults["primary_presets"] == [
        "SIMULATE_BROWSING", "DISCUSSION_PARTICIPATION", "FULL_PROGRESSION",
    ]
    assert action_scope_defaults["legacy_aliases"] == "INPUT_COMPATIBILITY_ONLY_NEVER_DISPLAY_IN_NEW_INTAKE"
    startup_transition = defaults["startup_transition"]
    assert startup_transition["question_two_completion"] == "DIRECTION_AND_IP_ONLY_NO_SCOPE_OR_MATERIAL_FOLLOWUP"
    assert startup_transition["missing_optional_defaults"] == "COMMUNITY_SCOPE_DISCOVER_OR_NAMED_SEEDS_EXPANDABLE_MATERIAL_REFS_EMPTY"
    assert startup_transition["answer_compilation"] == "LOCAL_THREE_ANSWER_COMPILER_BEFORE_CURRENT_TASK_SCOPE_NO_SECOND_ROUND"
    assert startup_transition["after_three_answers"] == "CURRENT_TASK_SCOPE_ENVELOPE_ONE_CHROME_SESSION_INITIAL_DIRECT_THEN_ADVISORY_HEARTBEAT"
    assert startup_transition["initial_packet"] == "FORMAL_ROUND_ONE_NOT_PREVIEW_PLAN_OR_PREFILTER_WITH_ATOMIC_HANDOFF"
    assert startup_transition["technical_gates"] == "ONE_CURRENT_TASK_AND_CHROME_SESSION_GATE_NO_SCHEDULER_OR_TITLE_BLOCK"
    assert defaults["scheduler"]["wake_lease_seconds"] == 900
    assert defaults["scheduler"]["packet_lease_seconds"] == 900
    assert defaults["scheduler"]["heartbeat_receipt"] == "ADVISORY_RECORD_AUTOMATION_ID_TARGET_TASK_RRULE_NEXT_RUN_WHEN_AVAILABLE"
    assert defaults["scheduler"]["heartbeat_create_recovery"] == "ONE_BACKGROUND_ATTEMPT_THEN_ONE_NORMALIZED_RETRY_NO_STARTUP_BLOCK"
    assert defaults["scheduler"]["scheduler_gate"] == "ADVISORY_NEVER_BLOCK_INITIAL_OR_CURRENT_TASK_WAKE"
    assert defaults["scheduler"]["wake_without_verified_heartbeat"] == "CONTINUE_WITH_SCHEDULER_UNVERIFIED_CONTINUING"
    assert defaults["scheduler"]["count_fallback"].startswith("FREQ=MINUTELY_INTERVAL_15")
    assert set(defaults["mission_profiles"]["business_goals"]) == {
        "community_discovery", "conversation_entry", "feedback_validation",
        "project_distribution", "relationship_maintenance", "profile_readiness",
    }
    assert defaults["mission_profiles"]["frequency_aliases"]["high"]["coverage_budget"] == "broad"
    assert defaults["mission_profiles"]["frequency_aliases"]["low"]["action_threshold"] == "high"
    assert defaults["research"]["community_index"]["methods"] == ["GET"]
    assert defaults["research"]["community_index"]["account_or_write_endpoints"] == "FORBIDDEN"
    assert defaults["research"]["web_search"]["comments_query_min"] == 2
    assert defaults["research"]["web_search"]["comments_query_max"] == 4
    assert defaults["research"]["web_search"]["posts_query_min"] == 4
    assert defaults["research"]["web_search"]["posts_query_max"] == 8
    assert defaults["runtime_fence"]["preflight"] == "CURRENT_TASK_ONLY_NO_CROSS_TASK_SCAN"
    assert defaults["runtime_fence"]["pending_chrome_release"] == "LEDGER_EVIDENCE_ONLY_NOT_A_LIVE_OCCUPANCY_PROOF"
    assert defaults["runtime_fence"]["stale_reconciliation"] == "CURRENT_TASK_LOCAL_MARKER_ONLY"
    assert defaults["runtime_fence"]["uncertain_runtime"] == "BLOCK_ONLY_CURRENT_TASK_CONFLICT"
    assert defaults["runtime_fence"]["other_tasks"] == "IGNORE_BY_DEFAULT"
    assert defaults["runtime_fence"]["other_heartbeats"] == "IGNORE_BY_DEFAULT"
    assert defaults["runtime_fence"]["other_environments"] == "IGNORE_BY_DEFAULT"
    assert defaults["runtime_fence"]["handoff_inspection"] == "NOT_REQUIRED_AT_STARTUP"
    assert set(defaults["units"]) == {"browsing", "comments", "posts", "follow-up", "presence"}
    documents = [SKILL]
    repository_readme = ROOT.parent / "README.md"
    if repository_readme.is_file():
        documents.append(repository_readme)
        readme = repository_readme.read_text(encoding="utf-8")
        assert "不要进入目标模式" not in readme
        assert "收到完整回答后，在同一任务中立即开始第一轮正式运营" in readme
        assert len(readme.splitlines()) <= 100
    assert len(SKILL.read_text(encoding="utf-8").splitlines()) <= 150
    text = " ".join("\n".join(path.read_text(encoding="utf-8") for path in documents).split())
    for phrase in ("Reddit 运营台", "canary", "heartbeat-observe", "Official Reddit API", "Chrome", "MUTATION_INTENT", "±5 minutes", "fast NOOP", "atomic `handoff`", "BOOTSTRAP_READY", "HOT_REPLACED", "REMOTE_NEWER_DEFERRED", "high/low frequency", "business goal", "exactly three", "Do not ask for an account name or handle", "same-Chrome", "One operating-direction answer", "current task", "source_thread_id", "other Heartbeats", "startup-wide scan", "autoResolutionMs", "WAITING_FOR_STARTUP_INPUT", "STARTUP_ANSWERS_COMPLETE", "compile_startup_intake.py", "INITIAL` packet", "preview or pre-filter", "LIVE_GATE_UNVERIFIED", "normal text response", "at most once", "advisory Heartbeat"):
        assert phrase in text, phrase
    runtime = (ROOT / "references" / "single-owner-runtime.md").read_text(encoding="utf-8")
    guides = (ROOT / "references" / "unit-guides.md").read_text(encoding="utf-8")
    for phrase in ("ACTION_WINDOW_CLAMPED_TO_NEXT_HEARTBEAT", "single_owner_queue.py handoff", "next task wake", "genuinely exhausted/parked", "candidate-reject", "runtime_protocol_version", "no replay"):
        assert phrase in runtime, phrase
    for phrase in ("current task", "other Heartbeats", "UNCERTAIN"):
        assert phrase in runtime, phrase
    assert "live_gate_checkpoint" in guides
    chrome = (ROOT / "references" / "chrome-and-actions.md").read_text(encoding="utf-8")
    for phrase in ("not `RULE_BLOCKED`", "Bounded startup and recovery", "CHROME_CONTENT_CHANNEL_TIMEOUT", "scheduler receipt", "same logged-in Chrome", "Do not use `Promise.race`", "post_timeout_readback=true"):
        assert phrase in chrome, phrase
    installed_text = " ".join(SKILL.read_text(encoding="utf-8").split())
    for phrase in ("atomic `handoff`", "BOOTSTRAP_READY", "MUTATION_INTENT"):
        assert phrase in installed_text, phrase
    assert "legacy_multi_lane_compat" not in text
    required = {"single-owner-runtime.md", "research-and-community-index.md", "chrome-and-actions.md", "unit-guides.md", "mission-goals-and-profiles.md", "startup-intake.md", "operation-defaults.json"}
    actual = {path.name for path in (ROOT / "references").iterdir()}
    assert actual == required, actual
    intake = STARTUP_INTAKE.read_text(encoding="utf-8")
    intake_flat = " ".join(intake.split())
    assert len(intake.splitlines()) <= 115
    assert intake.count("## Question ") == 3
    for phrase in ("Do not ask for an account name or handle", "2 hours", "4 hours", "8 hours", "社交与社区", "个人创作与独立项目", "3D/游戏/共创", "operating direction", "不需要拆开追问", "Question 3", "模拟浏览", "参与讨论", "全面推进", "action scope", "MATERIAL_REQUIRED", "no fourth question", "autoResolutionMs", "WAITING_FOR_STARTUP_INPUT", "STARTUP_CANCELLED_BY_USER", "STARTUP_ANSWERS_COMPLETE", "compile_startup_intake.py", "silence never does", "do not ask a second-round question", "INITIAL direct packet", "not a preview, pre-filter, or separate planning round", "Text fallback after an unanswered form", "do **not** submit `request_user_input` again", "请先回答以下三个问题", "这轮想围绕什么方向或哪些社区运营", "这轮希望做到哪一步", "all three questions"):
        assert phrase in intake_flat, phrase
    assert "希望账号在 Reddit 上成为什么样的人" not in intake_flat
    assert "这轮希望账号做到哪一步" not in intake_flat
    # Python may create __pycache__ while validators run. Only packaged files
    # are part of the Skill contract; generated directories must not make an
    # otherwise complete installation fail validation.
    scripts = {path.name for path in (ROOT / "scripts").iterdir() if path.is_file()}
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
        partial = run(str(INTAKE_COMPILER), "--input", str(partial_answers))
        assert partial["status"] == "WAITING_FOR_STARTUP_INPUT"
        assert partial["missing"] == ["direction", "authority_profile"]
        assert partial["text_fallback"]["channel"] == "DIRECT_TEXT"
        assert partial["text_fallback"]["request_user_input_repeat"] is False
        assert "请先回答以下三个问题" in partial["text_fallback"]["message"]
        assert all(label in partial["text_fallback"]["message"] for label in ("1)", "2)", "3)"))
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
        startup_proof = "startup-proof-token"
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
        initial_handoff = run(
            str(QUEUE), "handoff", *startup_shared,
            "--target-unit", "comments",
            "--objective-state", "ACTION_ELIGIBLE",
            "--objective-reason", "initial browsing found a specific contribution route",
            "--candidate-ref", "https://old.reddit.com/r/example/comments/initial",
            "--source-ref", "pack:initial:discussion:1",
            "--now-utc", "2026-07-27T08:01:05Z",
        )
        assert initial_handoff["status"] == "HANDOFF_RECORDED"
        assert initial_handoff["objective_state"]["comments"] == "ACTION_ELIGIBLE"
        assert initial_handoff["next_due_at_utc"]["comments"] == "2026-07-27T08:15:00Z"
        initial_completed = run(str(QUEUE), "finish", *startup_shared, "--outcome", "COMPLETED", "--objective-state", "CANDIDATES_READY", "--objective-reason", "real first-packet community evidence", "--candidate-ref", "pack:initial:1", "--now-utc", "2026-07-27T08:01:06Z")
        assert initial_completed["status"] == "COMPLETED"
        assert initial_completed["objective_state"]["browsing"] == "CANDIDATES_READY"
        assert initial_completed["timer_policy"] == "CONTINUE_STABLE_RECURRENCE"
        assert heartbeat_record(startup_shared, "2026-07-27T08:01:07Z", "2026-07-27T10:25:00Z", "2026-07-27T08:15:00Z", "owner-startup", startup_proof)["status"] == "HEARTBEAT_VERIFIED"
        assert run(str(QUEUE), "heartbeat-observe", *startup_shared, "--now-utc", "2026-07-27T08:15:00Z")["status"] == "HEARTBEAT_OBSERVED"
        continuation_wake = run(str(QUEUE), "wake-open", *startup_shared, "--expected-at-utc", "2026-07-27T08:15:00Z", "--now-utc", "2026-07-27T08:15:00Z")
        assert continuation_wake["status"] == "WAKE_OPEN" and continuation_wake["due_units"] == ["comments"]
        continuous_source = work / "continuous-mission.json"
        continuous_envelope = work / "continuous-envelope.json"
        continuous_source.write_text(json.dumps({
            "mission_id": "active-browsing-continuation",
            "account": "u/example",
            "direction": "active personal creator discovery",
            "operation_start_at": "2026-07-27T09:00:00Z",
            "duration_hours": 2,
            "requested_work_types": ["browsing", "comments"],
            "unit_authority": {"comments": "COMMENT_AUTHORIZED"},
            "authorization_receipt": "explicit active browsing",
            "mission_strategy": {
                "business_goal": "conversation_entry",
                "community_scope": "discover",
                "coverage_budget": "broad",
                "action_threshold": "standard",
                "action_budget": "active",
                "material_refs": [],
                "planning_targets": {"candidate_packs": 3},
            },
            "source_prompt": "keep coverage moving without empty wake gaps",
        }), encoding="utf-8")
        run(str(COMPILER), "--input", str(continuous_source), "--output", str(continuous_envelope))
        continuous_shared = ("--root", str(work / "continuous-queue"), "--scope", "active-browsing-continuation", "--owner-task-id", "owner-continuous", "--mission-envelope", str(continuous_envelope))
        assert run(str(QUEUE), "bootstrap", *continuous_shared, "--now-utc", "2026-07-27T09:00:00Z")["status"] == "BOOTSTRAPPED"
        assert promote(continuous_shared, "2026-07-27T09:00:00Z", startup_proof)["status"] == "PRESENTATION_PROMOTED"
        assert run(str(QUEUE), "canary-pass", *continuous_shared, "--proof-sha256", startup_proof)["status"] == "CANARY_PASSED"
        assert heartbeat_record(continuous_shared, "2026-07-27T09:00:00Z", "2026-07-27T11:25:00Z", "2026-07-27T09:11:00Z", "owner-continuous", startup_proof)["status"] == "HEARTBEAT_VERIFIED"
        initial_continuous_wake = run(str(QUEUE), "wake-open", *continuous_shared, "--wake-source", "INITIAL", "--expected-at-utc", "2026-07-27T09:00:00Z", "--now-utc", "2026-07-27T09:00:00Z")
        assert initial_continuous_wake["status"] == "WAKE_OPEN" and initial_continuous_wake["due_units"] == ["browsing", "comments"]
        assert run(str(QUEUE), "decide", *continuous_shared, "--unit", "browsing", "--decision", "RUN", "--reason", "first direct coverage packet", "--now-utc", "2026-07-27T09:00:01Z")["status"] == "DECISION_RECORDED"
        assert run(str(QUEUE), "decide", *continuous_shared, "--unit", "comments", "--decision", "DEFER", "--reason", "requires a real upstream route", "--now-utc", "2026-07-27T09:00:01Z")["status"] == "DECISION_RECORDED"
        assert run(str(QUEUE), "start", *continuous_shared, "--now-utc", "2026-07-27T09:00:02Z")["status"] == "PACKET_STARTED"
        active_handoff = run(
            str(QUEUE), "handoff", *continuous_shared,
            "--target-unit", "comments",
            "--objective-state", "ACTION_ELIGIBLE",
            "--objective-reason", "current candidate has a truthful contribution boundary",
            "--candidate-ref", "https://old.reddit.com/r/example/comments/runtime",
            "--source-ref", "pack:coverage:comment:1",
            "--now-utc", "2026-07-27T09:00:03Z",
        )
        assert active_handoff["status"] == "HANDOFF_RECORDED"
        active_browsing_done = run(str(QUEUE), "finish", *continuous_shared, "--outcome", "COMPLETED", "--objective-state", "CANDIDATES_READY", "--objective-reason", "coverage remains open", "--candidate-ref", "pack:coverage:1", "--now-utc", "2026-07-27T09:00:03Z")
        assert active_browsing_done["next_due_at_utc"]["browsing"] == "2026-07-27T09:11:00Z"
        assert active_browsing_done["next_due_at_utc"]["comments"] == "2026-07-27T09:11:00Z"
        assert heartbeat_record(continuous_shared, "2026-07-27T09:00:04Z", "2026-07-27T11:25:00Z", "2026-07-27T09:11:00Z", "owner-continuous", startup_proof)["status"] == "HEARTBEAT_VERIFIED"
        assert run(str(QUEUE), "heartbeat-observe", *continuous_shared, "--now-utc", "2026-07-27T09:11:00Z")["status"] == "HEARTBEAT_OBSERVED"
        continuous_wake = run(str(QUEUE), "wake-open", *continuous_shared, "--expected-at-utc", "2026-07-27T09:11:00Z", "--now-utc", "2026-07-27T09:11:00Z")
        assert continuous_wake["status"] == "WAKE_OPEN" and continuous_wake["due_units"] == ["comments", "browsing"], continuous_wake
        assert run(str(QUEUE), "decide", *continuous_shared, "--unit", "comments", "--decision", "RUN", "--reason", "eligible continuation runs first", "--now-utc", "2026-07-27T09:11:01Z")["status"] == "DECISION_RECORDED"
        deferred_browsing = run(str(QUEUE), "decide", *continuous_shared, "--unit", "browsing", "--decision", "DEFER", "--reason", "eligible comment has this packet", "--now-utc", "2026-07-27T09:11:02Z")
        assert deferred_browsing["next_due_at_utc"]["browsing"] == "2026-07-27T09:26:00Z"
        assert run(str(QUEUE), "start", *continuous_shared, "--now-utc", "2026-07-27T09:11:03Z")["status"] == "PACKET_STARTED"
        bad_rule_block = run(
            str(QUEUE), "finish", *continuous_shared,
            "--outcome", "BLOCKED",
            "--objective-state", "RULE_BLOCKED",
            "--objective-reason", "Live community rule evidence incomplete after DOM timeout",
            "--now-utc", "2026-07-27T09:11:04Z",
        )
        assert bad_rule_block["status"] == "INVALID" and "recoverable_runtime_failure_requires_live_gate_unverified" in bad_rule_block["error"], bad_rule_block
        yielded_gate = run(
            str(QUEUE), "finish", *continuous_shared,
            "--outcome", "YIELDED",
            "--objective-state", "LIVE_GATE_UNVERIFIED",
            "--objective-reason", "Live community rule gate unverified after DOM timeout",
            "--candidate-ref", "https://old.reddit.com/r/example/comments/runtime",
            "--source-ref", "pack:coverage:comment:1",
            "--now-utc", "2026-07-27T09:11:05Z",
        )
        assert yielded_gate["status"] == "YIELDED"
        assert yielded_gate["objective_state"]["comments"] == "LIVE_GATE_UNVERIFIED"
        assert yielded_gate["due_units"] == ["comments"]
        assert heartbeat_record(continuous_shared, "2026-07-27T09:11:06Z", "2026-07-27T11:25:00Z", "2026-07-27T09:26:00Z", "owner-continuous", startup_proof)["status"] == "HEARTBEAT_VERIFIED"
        assert run(str(QUEUE), "heartbeat-observe", *continuous_shared, "--now-utc", "2026-07-27T09:26:00Z")["status"] == "HEARTBEAT_OBSERVED"
        recovery_wake = run(str(QUEUE), "wake-open", *continuous_shared, "--expected-at-utc", "2026-07-27T09:26:00Z", "--now-utc", "2026-07-27T09:26:00Z")
        assert recovery_wake["status"] == "WAKE_OPEN" and recovery_wake["due_units"] == ["comments"]
        skip_after_timeout = run(
            str(QUEUE), "decide", *continuous_shared,
            "--unit", "comments",
            "--decision", "SKIP",
            "--reason", "prior navigation timed out and no verified fresh page is available",
            "--now-utc", "2026-07-27T09:26:01Z",
        )
        assert skip_after_timeout["status"] == "RECOVERABLE_RUNTIME_FAILURE_REQUIRES_RUN", skip_after_timeout
        assert run(str(QUEUE), "decide", *continuous_shared, "--unit", "comments", "--decision", "RUN", "--reason", "RECOVERY_FIRST bounded read probe", "--now-utc", "2026-07-27T09:26:02Z")["status"] == "DECISION_RECORDED"
        assert run(str(QUEUE), "start", *continuous_shared, "--now-utc", "2026-07-27T09:26:03Z")["status"] == "PACKET_STARTED"
        assert run(str(QUEUE), "finish", *continuous_shared, "--outcome", "YIELDED", "--objective-state", "LIVE_GATE_UNVERIFIED", "--objective-reason", "content channel still unavailable after bounded recovery probe", "--now-utc", "2026-07-27T09:26:04Z")["status"] == "YIELDED"
        assert heartbeat_record(continuous_shared, "2026-07-27T09:26:05Z", "2026-07-27T11:25:00Z", "2026-07-27T09:41:00Z", "owner-continuous", startup_proof)["status"] == "HEARTBEAT_VERIFIED"
        assert run(str(QUEUE), "heartbeat-observe", *continuous_shared, "--now-utc", "2026-07-27T09:41:00Z")["status"] == "HEARTBEAT_OBSERVED"
        reject_wake = run(str(QUEUE), "wake-open", *continuous_shared, "--expected-at-utc", "2026-07-27T09:41:00Z", "--now-utc", "2026-07-27T09:41:00Z")
        assert reject_wake["due_units"] == ["comments"]
        assert run(str(QUEUE), "decide", *continuous_shared, "--unit", "comments", "--decision", "RUN", "--reason", "RECOVERY_FIRST live gate now readable", "--now-utc", "2026-07-27T09:41:01Z")["status"] == "DECISION_RECORDED"
        assert run(str(QUEUE), "start", *continuous_shared, "--now-utc", "2026-07-27T09:41:02Z")["status"] == "PACKET_STARTED"
        rejected = run(
            str(QUEUE), "candidate-reject", *continuous_shared,
            "--candidate-ref", "https://old.reddit.com/r/example/comments/runtime",
            "--source-ref", "pack:coverage:comment:1",
            "--objective-reason", "visible rule proved this exact candidate route incompatible",
            "--objective-evidence-sha256", startup_proof,
            "--now-utc", "2026-07-27T09:41:03Z",
        )
        assert rejected["status"] == "CANDIDATE_REJECTED_REFILL_SCHEDULED"
        assert rejected["objective_state"]["comments"] == "NOT_APPLICABLE"
        assert rejected["objective_state"]["browsing"] == "PENDING"
        assert rejected["next_due_at_utc"]["browsing"] == "2026-07-27T09:56:00Z"
        rejected_done = run(str(QUEUE), "finish", *continuous_shared, "--outcome", "COMPLETED", "--now-utc", "2026-07-27T09:41:04Z")
        assert rejected_done["candidate_rejection_count"] == 1
        assert heartbeat_record(continuous_shared, "2026-07-27T09:41:05Z", "2026-07-27T11:25:00Z", "2026-07-27T09:56:00Z", "owner-continuous", startup_proof)["status"] == "HEARTBEAT_VERIFIED"
        assert run(str(QUEUE), "heartbeat-observe", *continuous_shared, "--now-utc", "2026-07-27T09:56:00Z")["status"] == "HEARTBEAT_OBSERVED"
        refill_wake = run(str(QUEUE), "wake-open", *continuous_shared, "--expected-at-utc", "2026-07-27T09:56:00Z", "--now-utc", "2026-07-27T09:56:00Z")
        assert refill_wake["due_units"] == ["browsing"]
        assert run(str(QUEUE), "decide", *continuous_shared, "--unit", "browsing", "--decision", "RUN", "--reason", "fresh candidate refill", "--now-utc", "2026-07-27T09:56:01Z")["status"] == "DECISION_RECORDED"
        assert run(str(QUEUE), "start", *continuous_shared, "--now-utc", "2026-07-27T09:56:02Z")["status"] == "PACKET_STARTED"
        replay = run(
            str(QUEUE), "handoff", *continuous_shared,
            "--target-unit", "comments",
            "--objective-state", "ACTION_ELIGIBLE",
            "--objective-reason", "accidental replay",
            "--candidate-ref", "https://old.reddit.com/r/example/comments/runtime",
            "--source-ref", "pack:coverage:comment:replay",
            "--now-utc", "2026-07-27T09:56:03Z",
        )
        assert replay["status"] == "HANDOFF_CANDIDATE_PREVIOUSLY_REJECTED"
        fresh_handoff = run(
            str(QUEUE), "handoff", *continuous_shared,
            "--target-unit", "comments",
            "--objective-state", "ACTION_ELIGIBLE",
            "--objective-reason", "new exact candidate passed upstream fit",
            "--candidate-ref", "https://old.reddit.com/r/example/comments/fresh",
            "--source-ref", "pack:coverage:comment:fresh",
            "--now-utc", "2026-07-27T09:56:04Z",
        )
        assert fresh_handoff["status"] == "HANDOFF_RECORDED"
        assert run(str(QUEUE), "finish", *continuous_shared, "--outcome", "COMPLETED", "--objective-state", "CANDIDATES_READY", "--objective-reason", "fresh candidate pack", "--candidate-ref", "pack:coverage:fresh", "--now-utc", "2026-07-27T09:56:05Z")["status"] == "COMPLETED"
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
        proof = "runtime-proof-token"
        assert run(str(QUEUE), "canary-pass", *shared, "--proof-sha256", proof)["status"] == "CANARY_PASSED"
        assert run(str(QUEUE), "wake-open", *shared, "--expected-at-utc", "2026-07-27T00:00:00Z", "--now-utc", "2026-07-27T00:00:00Z")["status"] == "WAKE_OPEN"
        assert run(str(QUEUE), "decide", *shared, "--unit", "browsing", "--decision", "RUN", "--reason", "read current context", "--now-utc", "2026-07-27T00:05:00Z")["status"] == "DECISION_RECORDED"
        assert run(str(QUEUE), "decide", *shared, "--unit", "posts", "--decision", "DEFER", "--reason", "not due for one packet", "--now-utc", "2026-07-27T00:05:01Z")["status"] == "DECISION_RECORDED"
        started = run(str(QUEUE), "start", *shared, "--now-utc", "2026-07-27T00:05:02Z")
        assert started["status"] == "PACKET_STARTED" and started["unit"] == "browsing"
        assert run(str(QUEUE), "boundary-open", *shared, "--boundary-id", "read-1", "--boundary-kind", "DOM_READ", "--now-utc", "2026-07-27T00:05:03Z")["status"] == "BOUNDARY_OPEN"
        assert run(str(QUEUE), "boundary-settle", *shared, "--boundary-id", "read-1", "--boundary-outcome", "READ_OK", "--now-utc", "2026-07-27T00:05:04Z")["status"] == "BOUNDARY_SETTLED"
        completed = run(str(QUEUE), "finish", *shared, "--outcome", "COMPLETED", "--objective-state", "CANDIDATES_READY", "--objective-reason", "dated candidate pack", "--candidate-ref", "pack:sideproject:1", "--now-utc", "2026-07-27T00:05:05Z")
        assert completed["status"] == "COMPLETED"
        bad_timer = run(
            str(QUEUE), "heartbeat-record", *shared,
            "--automation-id", "automation-1",
            "--heartbeat-target-task-id", "owner-1",
            "--heartbeat-rrule", "FREQ=MINUTELY;INTERVAL=15;COUNT=1;UNTIL=20260727T022500Z",
            "--heartbeat-until-at-utc", "2026-07-27T02:25:00Z",
            "--heartbeat-next-run-at-utc", "2026-07-27T00:15:00Z",
            "--proof-sha256", proof,
            "--now-utc", "2026-07-27T00:05:06Z",
        )
        assert bad_timer["status"] == "INVALID" and "heartbeat_rrule" in bad_timer["error"]
        recorded = heartbeat_record(shared, "2026-07-27T00:05:07Z", "2026-07-27T02:25:00Z", "2026-07-27T00:15:00Z", "owner-1", proof)
        assert recorded["status"] == "HEARTBEAT_VERIFIED" and recorded["heartbeat"]["next_run_at_utc"] == "2026-07-27T00:15:00Z"
        observed = run(str(QUEUE), "heartbeat-observe", *shared, "--now-utc", "2026-07-27T00:05:08Z")
        assert observed["status"] == "HEARTBEAT_EARLY_OBSERVED"
        assert completed["heartbeat_interval_minutes"] == 15
        assert completed["timer_policy"] == "CONTINUE_STABLE_RECURRENCE"
        assert completed["objective_state"]["browsing"] == "CANDIDATES_READY"
        assert completed["next_due_at_utc"]["browsing"] == "2026-07-27T00:15:00Z"
        assert completed["next_due_at_utc"]["posts"] == "2026-07-27T00:15:00Z"
        assert completed["mission_strategy"]["action_budget"] == "active"
        assert completed["heartbeat"]["state"] == "PENDING"
        assert run(str(QUEUE), "heartbeat-observe", *shared, "--now-utc", "2026-07-27T00:15:00Z")["status"] == "HEARTBEAT_OBSERVED"
        action_due = run(str(QUEUE), "wake-open", *shared, "--expected-at-utc", "2026-07-27T00:15:00Z", "--now-utc", "2026-07-27T00:15:00Z")
        assert action_due["status"] == "WAKE_OPEN" and action_due["due_units"] == ["browsing", "posts"], action_due
        action_defer = run(str(QUEUE), "decide", *shared, "--unit", "posts", "--decision", "DEFER", "--reason", "candidate packet first", "--now-utc", "2026-07-27T00:15:01Z")
        assert action_defer["scheduler_adjustment"] == "ACTION_WINDOW_CLAMPED_TO_NEXT_HEARTBEAT"
        assert run(str(QUEUE), "decide", *shared, "--unit", "browsing", "--decision", "RUN", "--reason", "active coverage continues", "--now-utc", "2026-07-27T00:15:02Z")["status"] == "DECISION_RECORDED"
        assert run(str(QUEUE), "start", *shared, "--now-utc", "2026-07-27T00:15:03Z")["status"] == "PACKET_STARTED"
        continued = run(str(QUEUE), "finish", *shared, "--outcome", "COMPLETED", "--objective-state", "CANDIDATES_READY", "--objective-reason", "active coverage frontier remains open", "--candidate-ref", "pack:sideproject:2", "--now-utc", "2026-07-27T00:15:04Z")
        assert continued["next_due_at_utc"]["browsing"] == "2026-07-27T00:30:00Z"
        assert run(str(QUEUE), "heartbeat-observe", *shared, "--now-utc", "2026-07-27T00:20:00Z")["status"] == "HEARTBEAT_EARLY_OBSERVED"
        no_work = run(str(QUEUE), "wake-open", *shared, "--expected-at-utc", "2026-07-27T00:20:00Z", "--now-utc", "2026-07-27T00:20:00Z")
        assert no_work["status"] == "NOOP" and no_work["due_units"] == []
        assert no_work["heartbeat"]["state"] == "VERIFIED"
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
        assert heartbeat_record(action_shared, "2026-07-27T01:00:00Z", "2026-07-27T03:25:00Z", "2026-07-27T01:12:00Z", "owner-2", proof)["status"] == "HEARTBEAT_VERIFIED"
        assert run(str(QUEUE), "wake-open", *action_shared, "--wake-source", "INITIAL", "--expected-at-utc", "2026-07-27T01:00:00Z", "--now-utc", "2026-07-27T01:00:00Z")["status"] == "WAKE_OPEN"
        assert run(str(QUEUE), "decide", *action_shared, "--unit", "comments", "--decision", "DEFER", "--reason", "post audit first", "--now-utc", "2026-07-27T01:00:01Z")["status"] == "DECISION_RECORDED"
        assert run(str(QUEUE), "decide", *action_shared, "--unit", "posts", "--decision", "RUN", "--reason", "one truthful audit", "--now-utc", "2026-07-27T01:00:02Z")["status"] == "DECISION_RECORDED"
        started = run(str(QUEUE), "start", *action_shared, "--now-utc", "2026-07-27T01:00:03Z")
        assert started["status"] == "PACKET_STARTED" and started["unit"] == "posts"
        required = run(str(QUEUE), "finish", *action_shared, "--outcome", "COMPLETED", "--now-utc", "2026-07-27T01:00:04Z")
        assert required["status"] == "OBJECTIVE_STATE_REQUIRED"
        premature_material_block = run(
            str(QUEUE), "finish", *action_shared,
            "--outcome", "COMPLETED",
            "--objective-state", "MATERIAL_REQUIRED",
            "--objective-reason", "no project link was supplied at startup",
            "--now-utc", "2026-07-27T01:00:05Z",
        )
        assert premature_material_block["status"] == "INVALID"
        assert "candidate_or_format_gap_requires_more_research" in premature_material_block["error"]
        parked = run(
            str(QUEUE), "finish", *action_shared,
            "--outcome", "COMPLETED",
            "--objective-state", "MATERIAL_REQUIRED",
            "--objective-reason", "bounded mission-wide audit proved every allowed post format requires absent truthful material",
            "--objective-evidence-sha256", proof,
            "--block-scope", "MISSION",
            "--now-utc", "2026-07-27T01:00:05Z",
        )
        assert parked["objective_state"]["posts"] == "MATERIAL_REQUIRED"
        assert parked["next_due_at_utc"]["posts"] is None and "posts" not in parked["due_units"]
        comment_armed = run(
            str(QUEUE), "objective-set", *action_shared,
            "--unit", "comments",
            "--objective-state", "ACTION_ELIGIBLE",
            "--objective-reason", "browsing candidate pack",
            "--candidate-ref", "https://old.reddit.com/r/SideProject/comments/comment-candidate",
            "--source-ref", "pack:sideproject:1",
            "--now-utc", "2026-07-27T01:00:06Z",
        )
        assert comment_armed["objective_state"]["comments"] == "ACTION_ELIGIBLE"
        assert comment_armed["next_due_at_utc"]["comments"] == "2026-07-27T01:12:00Z"
        candidate_rule_block = run(
            str(QUEUE), "objective-set", *action_shared,
            "--unit", "comments",
            "--objective-state", "RULE_BLOCKED",
            "--objective-reason", "one candidate is incompatible with one community rule",
            "--objective-evidence-sha256", proof,
            "--now-utc", "2026-07-27T01:00:06Z",
        )
        assert candidate_rule_block["status"] == "INVALID"
        assert "candidate_or_community_block_requires_candidate_reject" in candidate_rule_block["error"]
        technical_rule_block = run(
            str(QUEUE), "objective-set", *action_shared,
            "--unit", "comments",
            "--objective-state", "RULE_BLOCKED",
            "--objective-reason", "community rule DOM timed out",
            "--objective-evidence-sha256", proof,
            "--block-scope", "MISSION",
            "--now-utc", "2026-07-27T01:00:06Z",
        )
        assert technical_rule_block["status"] == "INVALID"
        assert "recoverable_runtime_failure_requires_live_gate_unverified" in technical_rule_block["error"]
        mission_rule_block = run(
            str(QUEUE), "objective-set", *action_shared,
            "--unit", "comments",
            "--objective-state", "RULE_BLOCKED",
            "--objective-reason", "bounded mission-wide audit proved every allowed community disallows this comment objective",
            "--objective-evidence-sha256", proof,
            "--block-scope", "MISSION",
            "--now-utc", "2026-07-27T01:00:06Z",
        )
        assert mission_rule_block["status"] == "OBJECTIVE_RECORDED"
        assert mission_rule_block["objective_state"]["comments"] == "RULE_BLOCKED"
        comment_rearmed = run(
            str(QUEUE), "objective-set", *action_shared,
            "--unit", "comments",
            "--objective-state", "ACTION_ELIGIBLE",
            "--objective-reason", "mission revision supplied a newly eligible route",
            "--candidate-ref", "https://old.reddit.com/r/SideProject/comments/comment-candidate-2",
            "--source-ref", "revision:new-comment-route",
            "--now-utc", "2026-07-27T01:00:06Z",
        )
        assert comment_rearmed["status"] == "OBJECTIVE_RECORDED"
        rearmed = run(
            str(QUEUE), "objective-set", *action_shared,
            "--unit", "posts",
            "--objective-state", "ACTION_ELIGIBLE",
            "--objective-reason", "truthful material supplied",
            "--candidate-ref", "https://old.reddit.com/r/SideProject/submit?selftext=true",
            "--source-ref", "material:verified:1",
            "--now-utc", "2026-07-27T01:00:07Z",
        )
        assert rearmed["objective_state"]["posts"] == "ACTION_ELIGIBLE"
        verified = run(str(QUEUE), "objective-set", *action_shared, "--unit", "posts", "--objective-state", "ACTION_VERIFIED", "--objective-reason", "post visible after reload", "--objective-evidence-sha256", proof, "--source-ref", "https://www.reddit.com/r/example/comments/abc", "--now-utc", "2026-07-27T01:00:08Z")
        assert verified["objective_state"]["posts"] == "ACTION_VERIFIED"
        armed = run(str(QUEUE), "objective-set", *action_shared, "--unit", "follow-up", "--objective-state", "ACTION_ELIGIBLE", "--objective-reason", "verified own permalink", "--source-ref", "https://www.reddit.com/r/example/comments/abc", "--now-utc", "2026-07-27T01:00:09Z")
        assert armed["status"] == "OBJECTIVE_RECORDED"
        assert armed["objective_state"]["follow-up"] == "ACTION_ELIGIBLE"
        assert armed["next_due_at_utc"]["follow-up"] == "2026-07-27T01:12:00Z", armed
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
        run(
            str(QUEUE), "objective-set", *priority_shared,
            "--unit", "posts",
            "--objective-state", "ACTION_ELIGIBLE",
            "--objective-reason", "live route plus real material",
            "--candidate-ref", "https://old.reddit.com/r/SideProject/submit?selftext=true",
            "--source-ref", "route:verified:1",
            "--now-utc", "2026-07-27T03:00:01Z",
        )
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
        assert early["status"] == "EARLY_WAKE_NOOP" and early["heartbeat"]["state"] == "VERIFIED"
        assert heartbeat_record(trigger_shared, "2026-07-27T06:09:01Z", "2026-07-27T07:25:00Z", "2026-07-27T06:15:00Z", "owner-5", proof)["status"] == "HEARTBEAT_VERIFIED"
        assert run(str(QUEUE), "heartbeat-observe", *trigger_shared, "--now-utc", "2026-07-27T06:21:00Z")["status"] == "HEARTBEAT_LATE_OBSERVED"
        late = run(str(QUEUE), "wake-open", *trigger_shared, "--expected-at-utc", "2026-07-27T06:15:00Z", "--now-utc", "2026-07-27T06:21:00Z")
        assert late["status"] == "WAKE_OPEN" and late["due_units"] == ["browsing"]
        assert run(str(QUEUE), "decide", *trigger_shared, "--unit", "browsing", "--decision", "RUN", "--reason", "recovery proof", "--now-utc", "2026-07-27T06:21:01Z")["status"] == "DECISION_RECORDED"
        assert run(str(QUEUE), "start", *trigger_shared, "--now-utc", "2026-07-27T06:21:02Z")["status"] == "PACKET_STARTED"
        assert run(str(QUEUE), "recover", *trigger_shared, "--recovery-reason", "lease still current", "--now-utc", "2026-07-27T06:21:03Z")["status"] == "RECOVERY_NOT_STALE"
        recovered = run(str(QUEUE), "recover", *trigger_shared, "--recovery-reason", "task resumed after lease", "--recovery-action-key", "1" * 64, "--now-utc", "2026-07-27T06:36:03Z")
        assert recovered["status"] == "RECOVERED_YIELDED" and recovered["frozen_action_key_count"] == 1 and recovered["due_units"] == ["browsing"]
        assert recovered["resume_unit"] == "browsing"
        assert heartbeat_record(trigger_shared, "2026-07-27T06:36:04Z", "2026-07-27T07:25:00Z", "2026-07-27T06:45:00Z", "owner-5", proof)["status"] == "HEARTBEAT_VERIFIED"
        assert run(str(QUEUE), "heartbeat-observe", *trigger_shared, "--now-utc", "2026-07-27T06:45:00Z")["status"] == "HEARTBEAT_OBSERVED"
        recovered_wake = run(str(QUEUE), "wake-open", *trigger_shared, "--expected-at-utc", "2026-07-27T06:45:00Z", "--now-utc", "2026-07-27T06:45:00Z")
        assert recovered_wake["status"] == "WAKE_OPEN" and recovered_wake["due_units"] == ["browsing"]
        stale_skip = run(
            str(QUEUE), "decide", *trigger_shared,
            "--unit", "browsing",
            "--decision", "SKIP",
            "--reason", "old tab disappeared",
            "--now-utc", "2026-07-27T06:45:01Z",
        )
        assert stale_skip["status"] == "RECOVERABLE_RUNTIME_FAILURE_REQUIRES_RUN"
        assert run(str(QUEUE), "decide", *trigger_shared, "--unit", "browsing", "--decision", "RUN", "--reason", "RECOVERY_FIRST rebuild one fresh tab", "--now-utc", "2026-07-27T06:45:02Z")["status"] == "DECISION_RECORDED"
        assert run(str(QUEUE), "start", *trigger_shared, "--now-utc", "2026-07-27T06:45:03Z")["status"] == "PACKET_STARTED"
        recovered_done = run(str(QUEUE), "finish", *trigger_shared, "--outcome", "COMPLETED", "--objective-state", "CANDIDATES_READY", "--objective-reason", "fresh tab read succeeded", "--candidate-ref", "pack:recovered:1", "--now-utc", "2026-07-27T06:45:04Z")
        assert recovered_done["status"] == "COMPLETED" and recovered_done["resume_unit"] is None

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
