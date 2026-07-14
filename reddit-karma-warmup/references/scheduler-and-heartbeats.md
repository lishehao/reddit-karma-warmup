# Worker-Owned Scheduler And Heartbeat

Canonical owner of one lane task's recurring continuation. Load only inside the lane task that owns the mission.

## Ownership

The worker is the only scheduler for its lane. It creates, reads, updates, repairs, and retires one recurring Heartbeat explicitly targeted to its own exact task ID. There is no launcher/coordinator supervisor Heartbeat and no cross-lane timer registry.

Resolve `self_task_id` only from the host's exact current-task context. Never infer it from a title, task search/list result, lane registry entry, launcher task, sibling task, automation card title, or remembered ID. A distributor-delivered mission must contain `worker_task_id=<the exact destination task ID>`; a direct user command inside a lane sets `worker_task_id=self_task_id`. Before any Reddit action or timer mutation, require `self_task_id == worker_task_id`.

Maintain one mission-local ownership tuple:

```text
self_task_id + worker_task_id + lane + mission_id + own_heartbeat_id
```

`own_heartbeat_id` is valid only when it came from this task's own create/update response and is recorded in this tuple. Never touch an automation ID discovered from another task, a title search, or an unowned card.

## Self-Binding Transaction

Every Heartbeat create or update uses all three gates:

1. **Pre-bind:** read the exact current task ID from host context and compare it with the mission's `worker_task_id`. On mismatch, perform no Reddit action and no timer mutation; report `worker_identity_mismatch` in this task.
2. **Explicit bind:** call the automation create/update tool with `targetThreadId=self_task_id`. Never omit the target, use a title, inherit a launcher ID, or reuse a sibling ID.
3. **Post-bind:** immediately read/view the exact returned `automation_id`. Require its exposed `targetThreadId == self_task_id`, its mission identity matches the current `mission_id`, and its recurring state is active. Record `target_binding_proof=verified` only after this second read.

Hidden scheduling time and hidden target identity are different states. Hidden `next_run_at` is non-blocking `created_unreadable`; hidden or mismatched `targetThreadId` is `target_binding_unverified`. Retry the exact read once. If it is still unverified, delete only the just-created/recorded `own_heartbeat_id`, clear the local next-due fields, and do not claim or run a scheduled continuation. The already completed first slot remains valid; report the timer-local issue in this task.

Before creating a new timer, read the recorded `own_heartbeat_id` when one exists. Update it instead of creating a duplicate when it is self-targeted and belongs to the current mission. For a reused lane task with a stale prior-mission timer, verify that the timer is both self-targeted and recorded by this same task, delete it, clear the old tuple, and then create the new mission timer. `one_active_heartbeat_per_mission=true`.

## Start Rule

1. Start the first requested slot immediately in the current user turn. Reading, discovery, eligibility checks, and drafting begin now. A mutation waits only when the mission carries a later `initial_mutation_not_before` phase.
2. If nonterminal work remains, run the Self-Binding Transaction and create or update one repeat-on Heartbeat with `targetThreadId=self_task_id`, a finite cutoff or explicit `operation_stop_at`, and the current mission fields.
3. Read back the exact automation ID, target task ID, repeat state, recurrence, next local time, UTC time, and deadline when exposed. Store the ID only after the create/update response identifies it as this task's timer.
4. Require `target_binding_proof=verified` before treating the Heartbeat as active. If only next-run fields are hidden, record `created_unreadable` and continue without asking the user to repair an unexposed time field.

Never use a future Heartbeat to defer the first action. Never create a new timer for every round. Reuse/update the same logical timer while the mission remains active.

## Cadence

Translate the current lane mission into a bounded next slot. Defaults remain advisory and quality-gated:

| Lane | Standard cadence |
|-|-|
| comments | resolve the requested hourly average into `clustered_windows`; do not schedule one evenly spaced comment at a time |
| posts | one candidate/rules sweep every `2-3h`; publish only when eligible |
| follow-up | every `30-45m` |
| browsing | every `20-40m`; normally `20-30` qualified reads |
| presence | terminal after one slot unless the user explicitly requests ongoing presence work |

Use short in-turn sleep only for human-scale submit pauses below roughly five minutes. Use the recurring Heartbeat for longer waits.

## Cross-Lane Phase Stagger

This is a lightweight best-effort stagger, not a shared scheduler or platform-safety guarantee.

1. The distributor orders enabled mutation-capable lanes as `comments -> follow-up -> posts -> browsing -> presence` and assigns `mutation_phase_index=0..n-1`.
2. `initial_mutation_not_before = start + (10 minutes * mutation_phase_index)`. All lanes may read and prepare immediately; only the first mutation is offset. The first comments lane therefore starts at phase `0` instead of waiting for a later round.
3. Later Heartbeats keep roughly the same relative phase and add only `2-4m` of bounded jitter. They do not read sibling state or negotiate a slot.
4. If browser recovery, candidate discovery, or another delay makes a lane miss its intended write window, keep useful read-only work and move the mutation to that lane's next normal window. Do not compress missed work into a catch-up burst.
5. An explicit user cadence replaces these defaults. Record the override once and continue without adding a second confirmation.

No shared ledger, account lock, claim/complete protocol, or cross-task collision check is allowed. The phase fields are static mission inputs only.

## Clustered Comment Windows

For comments, plan operational batches instead of a uniform per-comment clock:

1. Compute `effective_hourly_rate` from the latest controlling target and remaining time.
2. For roughly `6-10 comments/hour`, normally create `2-3` batch windows per hour. Vary the gap from actual completion time, usually `20-35m`, instead of repeating an exact interval.
3. Give each due window an exact `batch_target` of at least `2`, normally `2-4` verified comments, and an active work envelope of about `6-15m`. `minimum_completed_cluster_size=2`, `single_comment_cluster=forbidden`, and `cluster_copy_batching=forbidden`. Candidate quality, rules, and the mission cap still gate every action.
4. Inside a window, each comment independently loops through `CHECK_A -> DRAFT -> CHECK_B -> ACT -> measured log` with a new `per_comment_gate_id`; do not prewrite the remaining cluster or reuse another item's context, length tier, or slang choice. Keep the existing pre-submit pause and a varied `3-5m` pause after each verified proactive comment before another comment is submitted. Use local sleep for these at-most-five-minute waits; use the lane Heartbeat between windows.
5. Preserve `batch_target_remaining` and `slot_target_remaining`. After one verified proactive comment, the current wake stays active and continues discovery until the second passes; do not yield, schedule the next Heartbeat, or report a completed window after only one. A user-requested exact-one total is a single-action mission rather than a cluster. A user stop, deadline, or current hard blocker may produce `cluster_incomplete`, which carries its exact remainder forward without lowering thresholds or creating a catch-up burst.
6. Recompute later windows from actual verified count and remaining time. Do not precompute a mechanically identical all-day schedule.

Example: `80 comments / 10h` resolves to `8/hour`, not `10/hour`. A representative hour may use three windows such as `3 + 2 + 3`, with each window starting after a varied `20-35m` gap. The exact distribution changes with qualified candidates and actual completion time; it is not a promise to publish weak comments.

Before creating or updating the inter-window Heartbeat, assert `verified_comments_in_current_window >= 2` or `explicit_exact_one_mission=true`. If neither is true, keep working in the current wake. Recoverable browser/network failure does not satisfy the assertion; preserve the incomplete cluster and retry locally or on the same lane's continuation without calling it a completed window.

## Wake Flow

On every wake:

1. Read the exact current task ID from host context, then require `current_task_id == self_task_id == worker_task_id == Heartbeat.targetThreadId` and the Heartbeat mission identity equals `mission_id`. This wake-time check is mandatory even when creation previously passed.
2. Read actual local time/timezone and UTC; compare with intended schedule.
3. Reconnect Chrome or reclaim only this task's tab.
4. If the slot is due, resume its preserved `slot_target_remaining` and continue discovery/action toward zero. A runtime boundary may yield an interim checkpoint, but does not complete or reset the slot.
5. If not due, record `not_due`; do not manufacture activity.
6. Recompute the next due time from the exact remaining duration/count, current batch remainder, and live conditions; unfinished action targets receive the next permissible continuation rather than a fresh slot.
7. Update only this task's recorded timer when mission fields, cadence, or cutoff changed, and rerun the complete Self-Binding Transaction after the update.

## Survival And Repair

Technical failure is not timer termination. Candidate scarcity is also not timer termination. Keep the lane Heartbeat repeat-on through Chrome disconnect, stale tab, DNS/network/proxy/TLS errors, `ERR_BLOCKED_BY_CLIENT`, blank/loading pages, route failure, candidate exhaustion, rules rejection, subreddit retirement, timed rate limit, uncertain exact mutation, or a failed recovery wake. Resume the same remaining target after recovery. If every current expansion route is genuinely exhausted, yield an interim checkpoint and retry fresh surfaces on the next wake rather than declaring the action target complete.

For a malformed or missing timer whose target identity is already verified as this task, repair in place when possible; otherwise create and verify one corrected self-targeted replacement before removing the old timer. For a target mismatch on this task's recorded `own_heartbeat_id`, perform no Reddit action, delete that known misbound timer first so it cannot wake another task, then create and post-bind-verify one corrected self-targeted timer. If the mismatched automation ID is not this task's recorded `own_heartbeat_id`, never inspect further, pause, repair, or delete it. Never inspect, pause, repair, or delete another task's timer.

## Terminal Reasons

Retire this lane's Heartbeat only after:

- explicit user stop for this lane;
- `operation_stop_at` reached;
- verified completion of this lane's requested count/objective; or
- verified corrected replacement plus retirement of the old timer.

The stage governed by this Heartbeat is the full current user-authorized lane mission, not one comment cluster, hourly pacing bucket, read floor, or intermediate slot. If that full mission target is verified complete, remaining wall-clock authorization is not unfinished work.

## Completion Cleanup Transaction

At a terminal condition, cleanup is ordered and mandatory:

1. Stop creating or updating future wakes.
2. Delete this task's exact `own_heartbeat_id`; a successful delete response or an already-absent timer is sufficient proof.
3. Clear `own_heartbeat_id`, `next_due_local`, and `next_due_utc`; record `heartbeat_retirement_proof`.
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
