# Mission Scheduler And Heartbeats

Canonical owner of multi-hour scheduling, recurring Heartbeat creation, binding, time verification, slot accounting, continuation repair, and mission shutdown.

The coordinator is the only scheduler. Workers execute Reddit slots; they never create, update, renew, replace, pause, or delete Heartbeats.

## Core Contract

For any operation that extends beyond the current slot:

1. Execute the first lane slot immediately in the user's command turn.
2. After each enabled lane returns `start_proof`, `Reddit 主控台` creates one recurring, repeat-on Heartbeat explicitly targeting that worker's exact `worker_thread_id` only when nonterminal future work remains. A terminal one-slot presence mission receives no lane Heartbeat.
3. The same Heartbeat remains active for the whole mission. It must not be `COUNT=1` or depend on a worker creating its successor.
4. The coordinator also creates one recurring, read-only supervisor Heartbeat targeting `Reddit 主控台` for the mission lifetime.
5. Every timer carries `mission_id`, lane, local/UTC start and stop, `operation_stop_at`, current plan revision, and an explicit no-action-after-deadline guard.
6. Use finite recurrence with `UNTIL` or an equivalent scheduler cutoff when supported. The prompt deadline guard and coordinator cleanup remain mandatory even when the scheduler encodes an end.
7. User amendments are applied by updating the existing coordinator-owned Heartbeat(s), never by creating duplicates.
8. On completion, stop, or deadline, the coordinator deletes/deactivates the affected Heartbeats and reconciles the final slot ledger.

Heartbeat recurrence is infrastructure cadence, not a quota to mutate Reddit. A worker may wake before its next planned action and record `not_due`; it never publishes merely because a Heartbeat fired.

## Mission Ledger

The coordinator stores:

```text
mission_id
operation_start_at | operation_stop_at
plan_revision
enabled_lanes
lane -> worker_thread_id | heartbeat_id | recurrence | next_due_at | last_wake_at | last_slot_proof_at
planned_slots | started_slots | completed_slots | blocked_slots | missed_slots
last_verified_at
supervisor_heartbeat_id
mission_state = starting | running | degraded | partial_completed | completed | stopped
```

Minimum per-slot record:

```text
slot_id | lane | planned_due_local | planned_due_utc | actual_wake_utc | started_at | completed_at | status | proof
```

`not_due` infrastructure wakes are recorded separately and do not inflate planned/started/completed slot counts.

## Planning

Accept duration, count, or both. Spread requested work across the window; do not front-load or catch up with bursts.

Default work estimates remain `2 min` per comment/reply plus the proactive lane's local pause, and `5 min` per main post. Discovery, rules, browser recovery, and candidate rejection are additional.

Plan adaptive action due times in the ledger. Use a recurring dispatcher cadence frequent enough to observe them:

| Lane | Low | Standard | High |
|-|-|-|-|
| comments | every `30m` | every `20m` | every `10m` |
| posts | every `120m` | every `60m` | every `30m` |
| follow-up | every `45m` | every `30m` | every `20m` |
| browsing | every `40m` | every `30m` | every `20m` |
| coordinator supervisor | every `45m` | every `30m` | every `20m` |

An explicit user cadence replaces the matching default. If a platform only supports coarser recurrence, choose the nearest supported interval and record the expected tolerance. Do not add randomness merely to mimic a person.

Short waits inside one slot remain local:

| Delay | Mode |
|-|-|
| `<=5 min` | local wait is allowed while the slot is active |
| `>5 min` or future slot | end the turn; recurring Heartbeat provides the next wake |

## Coordinator Creation Flow

After same-turn `start_proof`:

1. Resolve the exact coordinator and worker task IDs.
2. Compute recurrence, first future wake, local/UTC stop, and plan revision.
3. Create one recurring lane Heartbeat from `Reddit 主控台` with explicit `targetThreadId=worker_thread_id`.
4. Create/update the recurring read-only supervisor Heartbeat with explicit `targetThreadId=coordinator_thread_id`.
5. Read every field the runtime exposes and verify:
   - exact target task
   - repeat is on
   - next run matches intended local/UTC time within `5 min`
   - recurrence matches the mission plan
   - cutoff/deadline is present in the schedule or prompt guard
   - automation ID is unique for account + mission + lane
6. Store all IDs and schedule evidence in the mission ledger.
7. Only then report `持续调度已建立`.

Automation names are labels, never ownership proof. Creation success without target verification is `created_unverified`, not a valid handoff.

## Worker Wake Contract

The worker receives the recurring Heartbeat but does not manage it.

On every wake:

1. Confirm `mission_id`, lane, worker task identity, current local/UTC time, and `operation_stop_at`.
2. If at/after the deadline, perform no Reddit mutation and return `deadline_reached` plus terminal lane evidence.
3. Restore mission/history and compare now with `next_due_at`.
4. If not due, record `heartbeat_seen/not_due`; do not manufacture a slot.
5. If due, execute one bounded lane slot, record `slot_proof`, and update the worker's local action history plus proposed `next_due_at`.
6. Never create/update/delete the Heartbeat. Schedule changes are returned as evidence for the coordinator supervisor to apply.
7. Continue to use the exact three-line worker report. The Heartbeat itself supplies the next wake, so `下一轮心跳` reports the persisted recurring schedule or next expected wake, not a newly created timer.

Routine wake results remain in the worker task. Risks, subreddit retirement, and terminal mission completion use their existing event paths.

## Coordinator Supervisor Heartbeat

Every multi-slot mission, including later missions, has one coordinator-owned recurring supervisor Heartbeat until the mission ends. It is read-only and never opens Reddit or performs lane actions.

On each supervisor wake:

1. Read the mission ledger and each enabled worker's latest turn.
2. Verify each lane Heartbeat still exists, is active/repeat-on, targets the right worker, remains before the stop time, and has produced a new worker turn near its expected wake.
3. Reconcile `planned_slots`, `started_slots`, `completed_slots`, `blocked_slots`, `missed_slots`, and `last_verified_at` from worker proof.
4. Apply worker-proposed `next_due_at` or user amendments by updating the existing recurring timer/prompt when required.
5. Repair one missing, stopped, misbound, or malformed Heartbeat in place. Never leave a duplicate active.
6. If continuation still fails, mark `SCHEDULER_CONTINUATION_FAILURE`, preserve completed Reddit actions, set mission `degraded` or `partial_completed`, and report through `Reddit 主控台`. This is orchestration failure, not account risk.
7. At the deadline or after all lanes are terminal, delete/deactivate every mission Heartbeat, reconcile totals, and issue one final mission report.

The first post-install hour still receives richer health/quality checks, but it uses this same mission-lifetime supervisor Heartbeat. Do not create a separate one-shot bootstrap timer.

## Binding And Time Verification

Use the scheduler clock mode detected on the current machine. Store intended local and UTC instants before create/update. Never assume another machine uses the same RRULE interpretation.

Classify:

- `verified_recurring`: exact target, repeat-on, recurrence, next run, and deadline guard pass
- `created_unreadable`: create returned success and ID/card, but one or more persisted fields are hidden; keep it active and verify target/wake at the first supervisor checkpoint
- `display_suspect`: raw UTC is correct but UI rendering appears shifted
- `repaired`: one in-place correction passes readback
- `scheduler_failed`: create/update failed, target is wrong after repair, repeat is off, time drift is `>15m` without cause, no worker turn appears after expected wake plus tolerance, or the item stops before deadline

Hidden `next_run_at` alone is not failure. A visible `COUNT=1` or repeat-off lane timer for a multi-slot mission is failure and must be replaced before claiming sustained operation.

If an exact UTC-offset error is visible, update the same Heartbeat in place using the detected scheduler clock mode. Do not wait for the wrong trigger.

## Continuation Failure

Trigger `SCHEDULER_CONTINUATION_FAILURE` when any enabled lane was promised ongoing execution but:

- has no recurring lane Heartbeat after first proof
- has repeat-off or `COUNT=1`
- is bound to the wrong task
- has no corresponding worker wake/turn after the expected time plus tolerance
- stopped before `operation_stop_at` without terminal proof
- cannot be repaired by one bounded coordinator attempt

Report:

```text
type = SCHEDULER_CONTINUATION_FAILURE
mission_id
affected_lanes
planned_slots | started_slots | completed_slots | blocked_slots | missed_slots
last_verified_at
timer_evidence
repair_attempt
mission_state = degraded | partial_completed
```

Never claim `持续运行中` from first-round proof plus timer creation alone. Sustained operation is proven only after at least one recurring wake produces a new worker turn and reconciled slot proof.

## Stop And Amendment

- User pause/stop: coordinator updates/deletes affected recurring Heartbeats and verifies they are inactive.
- Duration/intensity/count/style change: coordinator increments `plan_revision`, updates ledger and existing timers/prompts, and preserves completed work.
- Worker terminal return: coordinator marks that lane terminal and disables its Heartbeat.
- Deadline: prompt guard prevents new mutation even if scheduler cleanup is late; supervisor performs cleanup and final reconciliation.
- Do not archive a worker while a Heartbeat still targets it.

## Smoke Test

On a new/unverified machine or after timezone/proxy/runtime changes, run one no-Reddit recurring diagnostic only when real operation is not already providing immediate proof. Verify two consecutive wakes before trusting unattended multi-hour continuation, then delete the probe. A one-shot diagnostic cannot validate recurring continuation.
