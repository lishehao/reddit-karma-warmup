# Worker-Owned Scheduler And Heartbeat

Canonical owner of one lane task's recurring continuation. Load only inside the lane task that owns the mission.

## Ownership

The worker is the only scheduler for its lane. It creates, reads, updates, repairs, and retires one recurring Heartbeat explicitly targeted to its own exact task ID. There is no launcher/coordinator supervisor Heartbeat and no cross-lane timer registry.

Resolve `self_task_id` only from the host's exact current-task context. Never infer it from a title, task search/list result, lane registry entry, launcher task, sibling task, automation card title, or remembered ID. A distributor-delivered mission must contain `worker_task_id=<the exact destination task ID>`; a direct user command inside a lane sets `worker_task_id=self_task_id`. Before any Reddit action or timer mutation, require `self_task_id == worker_task_id`.

Maintain one mission-local ownership tuple and its durable checkpoint:

```text
self_task_id + worker_task_id + lane + mission_id + own_heartbeat_id
checkpoint_path + checkpoint_schema_version
```

`own_heartbeat_id` is valid only when it came from this task's own create/update response and is recorded in this tuple and checkpoint. Never touch an automation ID discovered from another task, a title search, or an unowned card. Load `lane-state-checkpoint.md` before creating, updating, or waking a timer.

## Self-Binding Transaction

Every Heartbeat create or update uses all three gates:

1. **Pre-bind:** read the exact current task ID from host context and compare it with the mission's `worker_task_id`. On mismatch, perform no Reddit action and no timer mutation; report `worker_identity_mismatch` in this task.
2. **Explicit bind:** persist the intended timer state, then call the automation create/update tool with `targetThreadId=self_task_id`. The Heartbeat instructions carry `checkpoint_path`, `checkpoint_schema_version`, `mission_id`, and `worker_task_id`. Never omit the target, use a title, inherit a launcher ID, or reuse a sibling ID.
3. **Post-bind:** immediately read/view the exact returned `automation_id`. Require its exposed `targetThreadId == self_task_id`, its mission identity matches the current `mission_id`, and its recurring state is active. Record `target_binding_proof=verified` only after this second read, then atomically persist the returned ID, verified binding, and exposed next-due fields.

Hidden scheduling time and hidden target identity are different states. Hidden `next_run_at` is non-blocking `created_unreadable`; hidden or mismatched `targetThreadId` is `target_binding_unverified`. Retry the exact read once. If it is still unverified, delete only the just-created/recorded `own_heartbeat_id`, clear the local next-due fields, and do not claim or run a scheduled continuation. The already completed first slot remains valid; report the timer-local issue in this task.

Before creating a new timer, read the recorded `own_heartbeat_id` when one exists. Update it instead of creating a duplicate when it is self-targeted and belongs to the current mission. For a reused lane task with a stale prior-mission timer, verify that the timer is both self-targeted and recorded by this same task, delete it, clear the old tuple, and then create the new mission timer. `one_active_heartbeat_per_mission=true`.

## Start Rule

1. Start the first requested slot immediately in the current user turn. Reading, discovery, eligibility checks, and drafting begin now. A mutation waits only when the mission carries a later `initial_mutation_not_before` phase.
2. If nonterminal work remains, run the Self-Binding Transaction and create or update one repeat-on Heartbeat with `targetThreadId=self_task_id`, a finite cutoff or explicit `operation_stop_at`, and the current mission fields.
3. Read back the exact automation ID, target task ID, repeat state, recurrence, next local time, UTC time, and deadline when exposed. Store the ID only after the create/update response identifies it as this task's timer.
4. Require `target_binding_proof=verified` before treating the Heartbeat as active. If only next-run fields are hidden, record `created_unreadable` and continue without asking the user to repair an unexposed time field.

Never use a future Heartbeat to defer the first action. Never create a new timer for every round. Reuse/update the same logical timer while the mission remains active.

## Cadence

Translate the current lane mission into a bounded next slot. Numeric defaults come only from `operation-defaults.json`; candidate thresholds remain quality gates:

| Lane | Standard cadence |
|-|-|
| comments | resolve the requested hourly average into `clustered_windows`; do not schedule one evenly spaced comment at a time |
| posts | resolve from `posts.research_cadence_minutes`; publish only when eligible |
| follow-up | resolve from the selected `followup.<intensity>_cadence_minutes` |
| browsing | resolve cadence from `browsing.default_cadence_minutes` and reads from the selected intensity |
| presence | terminal after one slot unless the user explicitly requests ongoing presence work |

Use `interaction-pacing.md` for measured human-scale waits. For any remaining delay at or below `interaction_pacing.local_sleep_max_seconds`, prefer local terminal `sleep <seconds>` while preserving the dedicated Reddit tab. Use the recurring Heartbeat for longer waits; never create one for an in-item pacing floor.

## Cross-Lane Phase Stagger

This is a lightweight best-effort stagger, not a shared scheduler or platform-safety guarantee.

1. The distributor orders enabled mutation-capable lanes as `comments -> follow-up -> posts -> browsing -> presence` and assigns `mutation_phase_index=0..n-1`.
2. `initial_mutation_not_before = start + (scheduler.first_mutation_phase_step_minutes * mutation_phase_index)`. All lanes may read and prepare immediately; only the first mutation is offset. The first comments lane therefore starts at phase `0` instead of waiting for a later round.
3. Later Heartbeats keep roughly the same relative phase and add bounded jitter from `scheduler.phase_jitter_minutes`. They do not read sibling state or negotiate a slot.
4. If browser recovery, candidate discovery, or another delay makes a lane miss its intended write window, keep useful read-only work and move the mutation to that lane's next normal window. Do not compress missed work into a catch-up burst.
5. An explicit user cadence replaces these defaults. Record the override once and continue without adding a second confirmation.

No shared ledger, account lock, claim/complete protocol, or cross-task collision check is allowed. The phase fields are static mission inputs only.

## Clustered Comment Windows

For comments, plan operational batches instead of a uniform per-comment clock:

1. Compute `effective_hourly_rate` from the latest controlling target and remaining time.
2. Resolve the number of batch windows and their varied gap from `comments.cluster_windows_per_hour` and `comments.cluster_window_gap_minutes`; do not repeat an exact interval.
3. Give each due window an exact `batch_target` from `comments.cluster_size_*` and an active work envelope from `comments.cluster_work_envelope_minutes`. `single_comment_cluster=forbidden` unless the entire mission explicitly requests one. Candidate quality, rules, and the mission cap still gate every action.
4. Inside a window, each comment independently loops through `CHECK_A -> DRAFT -> CHECK_B -> ACT -> measured log` with a new `per_comment_gate_id`; do not prewrite the remaining cluster or reuse another item's context, length tier, or slang choice. Apply the canonical dwell, readable-to-submit, pre-submit, and proactive-submit-gap values from `operation-defaults.json` through `interaction-pacing.md`. Use local sleep for waits at or below the configured local-sleep maximum; use the lane Heartbeat between windows.
5. Preserve `batch_target_remaining` and `slot_target_remaining`. After one verified proactive comment, the current wake stays active and continues discovery until the second passes; do not yield, schedule the next Heartbeat, or report a completed window after only one. A user-requested exact-one total is a single-action mission rather than a cluster. A user stop, deadline, or current hard blocker may produce `cluster_incomplete`, which carries its exact remainder forward without lowering thresholds or creating a catch-up burst.
6. Recompute later windows from actual verified count and remaining time. Do not precompute a mechanically identical all-day schedule.

Example: `80 comments / 10h` resolves to `8/hour`, not `10/hour`. A representative hour may use several compliant windows whose sizes and gaps are resolved from the canonical comment fields. The exact distribution changes with qualified candidates and actual completion time; it is not a promise to publish weak comments.

Before creating or updating the inter-window Heartbeat, assert `verified_comments_in_current_window >= comments.cluster_size_min` or `explicit_exact_one_mission=true`. If neither is true, keep working in the current wake. Recoverable browser/network failure does not satisfy the assertion; preserve the incomplete cluster and retry locally or on the same lane's continuation without calling it a completed window.

## Wake Flow

On every wake:

1. Read the exact current task ID from host context and load the Heartbeat-carried checkpoint path before any Reddit or timer mutation. Require checkpoint account/lane/task/mission identity to match `current_task_id == self_task_id == worker_task_id == Heartbeat.targetThreadId`. This wake-time check is mandatory even when creation previously passed.
2. Reconstruct read-only and repair the checkpoint atomically if it is missing or malformed; do not mutate Reddit until prior submission certainty and all remaining targets are known.
3. Read actual local time/timezone and UTC; compare with intended schedule.
4. Reconnect Chrome or reclaim only this task's tab.
5. If the slot is due, resume preserved action, qualified-read, and optional explicit-vote remainders and continue toward zero. A runtime boundary may yield an interim checkpoint, but does not complete or reset the slot.
6. If not due, record `not_due`; do not manufacture activity.
7. Recompute the next due time from exact remaining action/read/explicit-vote targets, current batch remainder, duration, and live conditions; unfinished targets receive the next permissible continuation rather than a fresh slot.
8. Atomically persist the reconciled checkpoint before updating only this task's recorded timer. When mission fields, cadence, or cutoff changed, rerun the complete Self-Binding Transaction.

When the checkpoint says `recovery_status=recovering|quiet_recovery`, normal lane cadence does not overwrite `next_recovery_at`. Resolve it from `operation-defaults.json.chrome_recovery.recovery_backoff_minutes`, bounded jitter, and any later `Retry-After`, then clamp it to `operation_stop_at`; a deadline-clamped wake performs cleanup only. Persist local and UTC values before updating the same Heartbeat. A healthy wake returns to normal cadence only after the Chrome recovery contract's readable-proof and account-recheck threshold passes.

## Survival And Repair

Technical failure is not timer termination. Candidate scarcity is also not timer termination. Keep the lane Heartbeat repeat-on through Chrome disconnect, stale tab, DNS/network/proxy/TLS errors, `ERR_BLOCKED_BY_CLIENT`, blank/loading pages, route failure, candidate exhaustion, rules rejection, subreddit retirement, timed rate limit, uncertain exact mutation, or a failed recovery wake. Persist and resume the same action/read/explicit-vote remainders after recovery. If every current expansion route is genuinely exhausted, yield an interim checkpoint and retry fresh surfaces on the next wake rather than declaring a target complete.

Repeated technical wakes use the same logical timer and the configured `5/10/20/40/60` minute backoff with bounded jitter. After the quiet-mode threshold, run one read-only diagnostic cycle per due wake and suppress duplicate notices; do not delete the Heartbeat, spawn replacement tasks, or poll continuously. Missed normal slots are recomputed from current remainders and remaining time, never replayed as a catch-up burst.

Explicit HTTP `429`/`Too Many Requests` is a round boundary, not a terminal condition: stop all Reddit work in the current wake, preserve the exact remaining target, and schedule the later of the next normal lane round or the server-displayed retry time. Do not delete or pause the Heartbeat, and do not create a catch-up burst after recovery.

For a malformed or missing timer whose target identity is already verified as this task, repair in place when possible; otherwise create and verify one corrected self-targeted replacement before removing the old timer. For a target mismatch on this task's recorded `own_heartbeat_id`, perform no Reddit action, delete that known misbound timer first so it cannot wake another task, then create and post-bind-verify one corrected self-targeted timer. If the mismatched automation ID is not this task's recorded `own_heartbeat_id`, never inspect further, pause, repair, or delete it. Never inspect, pause, repair, or delete another task's timer.

If an update/readback fails while a previously verified self-owned recurring Heartbeat still exists, keep that timer and checkpoint the desired due time; do not create a duplicate. Repair it on its next wake. If the first create/readback cannot prove a self-targeted recurring timer after one retry, set `scheduler_repair_required`, report that autonomous continuation is not established, and request one concrete user repair in this lane. Never describe checkpoint state alone as a scheduled future wake.

## Terminal Reasons

Retire this lane's Heartbeat only after:

- explicit user stop for this lane;
- `operation_stop_at` reached;
- verified completion of all required action, qualified-reading or required-surface, and explicit vote-target components; or
- verified corrected replacement plus retirement of the old timer.

The stage governed by this Heartbeat is the full current user-authorized lane mission, not one comment cluster, hourly pacing bucket, one completed target component, or intermediate slot. If that full mission target is verified complete, remaining wall-clock authorization is not unfinished work.

If `operation_stop_at` arrives while the lane is recovering, the deadline is terminal: do not perform a final Chrome probe or mutation. Retire the timer and tab using the cleanup transaction and report the remaining targets truthfully.

## Completion Cleanup Transaction

At a terminal condition, cleanup is ordered and mandatory:

1. Stop creating or updating future wakes.
2. Delete this task's exact `own_heartbeat_id`; a successful delete response or an already-absent timer is sufficient proof.
3. Clear `own_heartbeat_id`, `next_due_local`, and `next_due_utc`; record `heartbeat_retirement_proof` and persist the terminal checkpoint atomically.
4. Release only this task's Chrome tab.
5. Only then emit the terminal three-line receipt with `下轮时间：无` and no continuation plan.

Do not report the mission complete while its Heartbeat remains active. A transient deletion-tool failure gets bounded retry and a `cleanup_pending` checkpoint, not another Reddit-action wake and not a false completion receipt. This cleanup rule does not apply to recoverable browser/network failures, candidate scarcity, one rejected subreddit, or an incomplete comment cluster; those keep the mission and its Heartbeat alive.

At termination, do not notify the launcher or any sibling.

## Three-Line Receipt

```text
本轮完成：<该 lane 动作、链接或恢复结果>。
下轮时间：<验证后的当地时间>；绑定：本任务已核验。终止则写“无（Heartbeat 已删除）”。
下轮计划：<该 lane 下一项工作和当前真实风险>。
```
