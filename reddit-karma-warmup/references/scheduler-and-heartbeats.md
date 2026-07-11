# Scheduler And Heartbeats

Canonical owner of operation-time planning and logical Heartbeat lifecycle. Other references may request a next due time but must not redefine binding, timezone, update/reuse, or stop rules.

Use for duration/count planning, multi-round operation, waits longer than one active slot, timezone drift, and durable logical heartbeat timer verification.

## Planning Rule

Plan the session once, but execute one small slot at a time. The first slot starts in the same user turn. Scheduling is not execution: no heartbeat may be the first operational result after the user says start.

Accept `duration only`, `count only`, or both:

- Duration only: derive a quality-gated recommendation from account tier and lane.
- Explicit Daily 60 comment mode: plan around `10 comments/hour`; require at least `6h` for the full target. For shorter windows, cap the plan at `10 x available hours` and do not catch up after a late or missed slot.
- Newly installed/started broad operation: execute all four lane micro-slots immediately using the selected intensity envelope. Use a local `60-120 sec` pause after each verified comment; no heartbeat is needed for that short pause.
- Count only: estimate a minimum window from work time, spacing, preflight, and verification.
- Both: spread the requested work across the window; do not front-load it.

Only for the first post-install BOOTSTRAP broad start, keep two boundaries: worker operations stop at `operation_stop_at`, while the coordinator's one-time watch stops at `startup_watch_deadline = min(operation_stop_at, start + 60 min)`. Keep one coordinator logical timer and reuse its automation ID across one-shot checkpoints near `+15m`, `+35m`, and the final boundary near `+60m`. Later missions do not create coordinator-watch heartbeats. Never create or retain a Goal Mode merely to wait. Never create a lane trigger at or after `operation_stop_at`.

Default estimates are `2 min` of action work per comment/reply plus the proactive comment lane's `60-120 sec` post-submit pause, and `5 min` per main post. Discovery, rule checks, browser reconnects, and longer waits are additional.

Use varied micro-slots, usually `12-35 min`, with a small executable target. Variation should reflect workload and candidate availability, not an attempt to evade detection.

Minimum schedule columns:

```text
slot | start_local | end_local | lane | planned_actions | target_surface | status | operation_timer_id | next_trigger
```

After each slot, replace future rows when actual time, candidate quality, Reddit state, or the user request changes.

## Wait Decision

| Delay until next action | Mode |
|-|-|
| `<=5 min` | local wait is allowed inside the active slot |
| `>5-10 min` | prefer one-shot automation; use local wait only when automation is unavailable and the current slot remains active |
| `>10 min` | use one-shot automation or stop with a manual next time; do not block a terminal |

Second-level pre-submit pauses remain local waits.

After creating or updating the logical heartbeat timer and reading back every field the runtime actually exposes, end the current turn. Do not emit repeated “not due yet” turns, poll the clock, use Goal Mode, or use automatic continuation while waiting for the heartbeat.

This handoff is legal only after the initial command turn has verified `START_NOW_PROOF_BY_LANE`, or an execution-lane heartbeat turn has verified `SLOT_PROOF`. The heartbeat resumes the next incomplete slot. On resume, execute that slot before creating another heartbeat. If no requested action/no-action sweep happened in the current execution turn, return to lane execution instead of scheduling.

## Durable Logical Timer Contract

Each active lane owns one logical timer for the entire mission. The timer may operate for minutes or many hours:

1. The first slot still executes immediately in the user-command turn.
2. After first proof, create the lane timer once and store its `operation_timer_id`.
3. Each trigger remains one-shot and repeat-off, but after `slot_proof` the worker updates/reuses the same automation ID for the next exact due time.
4. Do not create a new automation every round. Replace the timer only after a proven binding/update failure and removal of the old item.
5. At `operation_stop_at`, completion, user stop, or hard-stop termination, delete/pause the exact timer, clear it from the registry, and send the lane's one terminal `MISSION_COMPLETE` return to `Reddit 主控台` after final evidence is recorded.
6. Do not install a fixed recurring schedule unless the user explicitly asks and fixed cadence is genuinely required; adaptive lane timing normally updates the same one-shot timer.

Create or update only the next continuation for the current lane. A long mission is represented by one repeatedly updated logical timer, not one long-running active turn.

### Thread Binding Gate

Every lane heartbeat must bind explicitly to its persistent worker task:

1. The coordinator passes `worker_thread_id` from the task-creation result into the worker handoff and registry.
2. The worker itself creates or updates its continuation. The coordinator never creates a lane heartbeat on the worker's behalf.
3. When the automation API exposes `targetThreadId`, always send `targetThreadId=worker_thread_id` on create and update; never rely only on the currently focused task or automation name.
4. Immediately view/read back the automation and compare `actual_target_thread_id` with `worker_thread_id`. When tool readback hides it and local automation config is available, inspect that config's `target_thread_id`.
5. Classify `thread_binding_verified` only on an exact match. If the field is hidden everywhere but the worker itself created the heartbeat, use provisional `creator_thread_bound` and verify on the first actual wakeup; do not ask the user.
6. On mismatch, do not leave the automation active. Update the same automation once with the explicit correct target and read it back. If it still mismatches, delete it and have the worker create one replacement from its own task. Never create a second active trigger before the first is removed.
7. A heartbeat that wakes in another task is `thread_binding_failed`: stop its Reddit action, record the observed/expected task IDs, remove that wrong trigger, and recreate from the correct worker.

Automation names are labels, not ownership proof. Each worker stores one unique `operation_timer_id`; no two lanes may share one.

Use the `scheduler_clock_mode` detected by the repository README's no-Reddit create/readback probe when it is available. Compute the intended UTC instant before constructing any schedule. The current known desktop runtime may use `UTC_FIELDS`, where RRULE fields such as `BYHOUR`, `BYMINUTE`, and `BYSECOND` are UTC; in that mode, `11:29:43 Asia/Shanghai` must be written as `03:29:43 UTC`, never with local `BYHOUR=11`. Another machine must not assume this result. Prefer an explicit one-shot target accepted by the automation tool. If the runtime hides persisted timing, keep the intended local and UTC pair in the heartbeat prompt and classify the result as `created_unreadable` rather than blocking current work.

Before creation, record:

- actual local time and timezone/UTC offset
- detected `scheduler_clock_mode` and its probe evidence when available; otherwise `unknown`
- target local time
- target UTC instant
- expected delay
- lane, next slot, and session stop time
- `worker_thread_id` and intended `targetThreadId`

After creation, immediately read back:

- stored trigger or displayed next run
- timezone/UTC interpretation when visible
- repeat setting; it must be off
- automation ID/name
- actual `target_thread_id` or the strongest available creator-thread binding evidence
- the scheduler's persisted `next_run_at` when the runtime exposes it; convert that epoch to both UTC and the intended local timezone

Before leaving the trigger active, compare the persisted schedule fields themselves with `scheduler_clock_mode`. Under `UTC_FIELDS`, `BYHOUR/BYMINUTE/BYSECOND` must equal the computed UTC clock fields, not the local clock fields. An exact local UTC-offset difference is a repair condition even when the automation card otherwise looks healthy.

Creation and timing observability are separate. Classify:

- `verified`: target thread matches, persisted/displayed next run converted to both UTC and local time matches the intended instant within `5 min`, repeat is off
- `created_unreadable`: create/update returned success plus an automation ID/card, but persisted/displayed timing is not exposed; keep the trigger, do not claim exact timing verification, and compare actual wake time with the stored local/UTC target when it fires
- `display_suspect`: raw UTC is correct but UI display appears shifted
- `rescheduled`: first item was wrong, replacement was read back correctly
- `blocked`: create/update failed, wrong date or `>=60 min` drift is visible, repeat is visibly on, or an actual wakeup proves an uncorrectable timing error

`created_unreadable` is not `blocked`. Never delete a successful trigger, pause the first Reddit round, or ask the user to repair the scheduler merely because `next_run_at`, DTSTART, or a displayed next-run label is absent. The user cannot repair a field the runtime does not expose.

Never leave duplicate active timers/triggers for the same account + lane + mission. Never create a coordinator-targeted heartbeat that combines execution from several lanes. The coordinator's optional first-hour heartbeat explicitly targets the coordinator task and is a separate read-only supervision timer; each lane operation timer explicitly targets its own persistent worker task.

If the stored next run is exactly one local UTC offset away from the intended instant, classify it as `timezone_encoding_error`, update the existing automation in place using the detected `scheduler_clock_mode`, and read it back again. Do not wait for the incorrectly shifted trigger and do not create a duplicate.

## Adaptive Next Interval

Choose the next interval from lane state:

- follow-up: use low `45-60 min`, standard `30-45 min`, or high `20-30 min`; shorter only for an active direct exchange, longer for a quiet queue
- comments: next incomplete workload slot after required spacing and candidate availability
- posts: next eligible post window after live rules, same-subreddit history, and diversity checks
- natural browsing: use the user's interval/range when supplied; otherwise select a fresh whole-minute delay from `20-40 min` after the current browsing slot completes

Intervals may differ between rounds because state differs. Natural browsing deliberately uses the user-requested `20-40 min` default range; record the sampled delay and exact next local/UTC time. Other lanes should not add randomness solely to mimic a person.

At resume, compare current UTC with the stored target UTC. If late, replan from now. Never catch up with a burst.

## Scheduler Smoke Test

Use a no-Reddit smoke test only on a new/unverified machine, after proxy/timezone changes, after observed hour-level drift, or before unattended multi-hour work.

1. Execute the current Reddit slot first if the user asked for real operations.
2. Choose a one-shot diagnostic `7-10 min` ahead.
3. Store both local and UTC target in the diagnostic prompt.
4. Create and immediately read back the item.
5. If it fires, compare actual UTC with target UTC and delete/close it.
6. If timing is readable and wrong, repair it before relying on continuation. If timing is unreadable but creation succeeded, leave the diagnostic active and validate at its real wakeup; do not block current Reddit actions. If it does not fire within about `5 min` after target, stop relying on unattended continuation and switch future waits to manual next times until the scheduler is repaired.

The smoke test never opens Reddit or changes account state.

## Trigger Ownership

Timers in different lanes coexist independently. A worker inspects only its own `operation_timer_id` and keeps at most one active next trigger for that lane/mission. It does not scan, compare, pause, delete, or reschedule another lane because of shared Chrome/account use, overlapping times, targets, or actions.

Before mutating an automation, verify that `target_thread_id` exactly equals this worker's registered `worker_thread_id` and that the prompt belongs to the current lane. A follow-up task cannot mutate comment/post/browsing automations; a comment task cannot mutate post/follow-up/browsing automations, and so on. When one user policy affects several lanes, each owner updates only its own trigger after receiving that instruction.
