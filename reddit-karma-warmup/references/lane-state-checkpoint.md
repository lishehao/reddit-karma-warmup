# Lane State Checkpoint

Canonical owner of durable worker state across normal turns, Heartbeat wakes, context compaction, browser recovery, and task reuse. Load in every execution lane before its first Chrome action.

## Paths

Persist one task-owned checkpoint outside the managed Skill tree:

```text
${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/lane-state/<username>/<lane>/<self_task_id>.json
```

Append verified outward actions and measured reads to the account+lane history:

```text
${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/lane-history/<username>/<lane>.ndjson
```

A replacement task may read the matching account+lane history but never another account or lane's checkpoint. Upgrades preserve both directories. Never store credentials, cookies, page HTML, private messages, or unrelated browser history.

## Checkpoint Schema

```text
checkpoint_schema_version=1
account + lane + self_task_id + worker_task_id
mission_id + mission_revision + mission_status
latest_user_request + intensity + style + language
operation_started_at + operation_stop_at
action_target + action_cap + action_verified + action_remaining
qualified_read_target + qualified_read_verified + qualified_read_remaining
vote_policy + vote_cap
optional browsing-only vote_target_mode + vote_target + upvote_count + downvote_count
current_cluster_id + cluster_target + cluster_verified + cluster_remaining
own_tab_id + own_tab_origin + current_url + tab_control_proof
surface_requested + surface_used + surface_reason + canonical_target_key
fallback_from + fallback_reason + route_result
own_heartbeat_id + target_binding_proof + next_due_local + next_due_utc
mutation_state + mutation_key + candidate_url + outbound_text_hash + submission_certainty
recovery_state_version=1
recovery_status + error_fingerprint + error_class + exact_code + failure_scope
consecutive_failure_wakes + same_wake_recovery_cycles + backoff_index
next_recovery_at_local + next_recovery_at_utc + quiet_recovery
last_healthy_probe_at + healthy_read_proofs + account_recheck_required
quarantined_mutation_url + quarantined_outbound_text_hash
last_verified_action + last_recovery + updated_at
```

For comments, posts, follow-up, and presence, persist `vote_policy=DISABLED_BY_LANE`, `vote_cap=0`, zero current vote counters, and no target/remainder. For browsing, persist `vote_policy=BROWSING_ONLY`; `vote_target` is absent by default and exists only when the user explicitly requested a vote count. A reused non-browsing task preserves legacy vote counters only as history and zeros them for the new mission revision.

The recovery fields are optional when reading a checkpoint written by an older Skill version. Upgrade them in place with zero/empty defaults before any new mutation; do not discard verified counters or create a replacement mission. Compute `error_fingerprint` as `error_class|exact_code|failure_scope|hostname`. A new route inside the same failed host/scope does not reset the fingerprint.

## Atomic Lifecycle

1. Create or replace the checkpoint atomically after the exact task/account/mission identity is accepted and before Chrome mutation.
2. Before every outward mutation, write `mutation_state=prepared`, the host-independent `mutation_key`, exact candidate URL, actual surface, canonical target key, and an outbound-text hash when text exists.
3. After the one mutation attempt, write `verified`, `explicit_failure`, or `submission_uncertain` before another candidate is considered. Never retry `submission_uncertain`.
4. After every qualified read, verified lane-owned action, surface switch, recovery, Heartbeat mutation, or schedule calculation, update counters and timestamps atomically. Browsing additionally updates vote decisions/counters. The same canonical target across hosts updates one history item and never increments the read or action count twice.
5. Before a nonterminal turn ends, require checkpoint `mission_status=active`, exact remaining counts, exact tab binding, and the current timer state.
6. At mission terminal cleanup, retain the checkpoint as `mission_status=completed|stopped|deadline`, clear tab/timer/next-due fields, and record Heartbeat retirement proof. Do not delete the history.

For a retryable Chrome failure, increment `consecutive_failure_wakes` at most once per Heartbeat wake, persist the selected backoff before editing the timer, and keep the exact action/read remainders unchanged; browsing also preserves its explicit vote remainder. Reset the recovery fields only after the configured number of healthy readable Chrome proofs and expected-account confirmation. `submission_uncertain` also records the exact candidate URL and outbound hash in the quarantine fields; no upgrade, reconnect, or later wake may replay that mutation automatically.

## Wake And Recovery

Every Heartbeat carries `checkpoint_path`, `checkpoint_schema_version`, `mission_id`, and `worker_task_id`. On wake, load the checkpoint first and require its account, lane, task ID, mission ID, and Heartbeat target to match current host context.

If the checkpoint is missing or malformed, perform read-only reconstruction from the current task, exact recorded Heartbeat response, current Chrome tab inventory, and recent account+lane history. Do not publish or vote until identity, prior submission certainty, remaining targets, and timer ownership are reconstructed. Repair this task's checkpoint atomically and continue; never inspect sibling state.

A new mission in a reused task increments `mission_revision`, replaces conflicting mission fields, and starts with a new `mission_id`. It never reuses a retired Heartbeat or resets verified history.
