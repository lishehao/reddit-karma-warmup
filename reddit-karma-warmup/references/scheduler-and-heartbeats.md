# Scheduler And Heartbeats

Use for duration/count planning, multi-round operation, waits longer than one active slot, timezone drift, and one-shot continuation verification.

## Planning Rule

Plan the session once, but execute one small slot at a time. The first slot starts immediately.

Accept `duration only`, `count only`, or both:

- Duration only: derive a quality-gated recommendation from account tier and lane.
- Daily 60 comment mode: plan around `10 comments/hour`; require at least `6h` for the full target. For shorter windows, cap the plan at `10 x available hours` and do not catch up after a late or missed slot.
- Newly installed/started broad operation: make the proactive comment lane's first hour an immediate `10`-comment target. Use a local `60-120 sec` pause after each verified submission; no heartbeat is needed for that short pause.
- Count only: estimate a minimum window from work time, spacing, preflight, and verification.
- Both: spread the requested work across the window; do not front-load it.

For a broad start, keep two boundaries: worker operations stop at `operation_stop_at`, while the coordinator's bounded watch stops at `startup_watch_deadline = min(operation_stop_at, start + 60 min)`. Keep one coordinator one-shot trigger at a time through that first hour, including a mandatory final boundary sweep. Never create or retain a Goal Mode merely to wait. Never create a lane trigger at or after `operation_stop_at`; never extend coordinator follow-up beyond the first hour.

Default estimates are `2 min` of action work per comment/reply plus the proactive comment lane's `60-120 sec` post-submit pause, and `5 min` per main post. Discovery, rule checks, browser reconnects, and longer waits are additional.

Use varied micro-slots, usually `12-35 min`, with a small executable target. Variation should reflect workload and candidate availability, not an attempt to evade detection.

Minimum schedule columns:

```text
slot | start_local | end_local | lane | planned_actions | target_surface | status | next_trigger
```

After each slot, replace future rows when actual time, candidate quality, Reddit state, or the user request changes.

## Wait Decision

| Delay until next action | Mode |
|-|-|
| `<=5 min` | local wait is allowed inside the active slot |
| `>5-10 min` | prefer one-shot automation; use local wait only when automation is unavailable and the current slot remains active |
| `>10 min` | use one-shot automation or stop with a manual next time; do not block a terminal |

Second-level pre-submit pauses remain local waits.

After creating the one-shot heartbeat and reading back every field the runtime actually exposes, end the current turn. Do not emit repeated “not due yet” turns, poll the clock, use Goal Mode, or use automatic continuation while waiting for the heartbeat.

## One-Shot Contract

Create only the next continuation for the current lane. Do not install a fixed recurring schedule unless the user explicitly asks for one.

Use the `scheduler_clock_mode` detected by the installer Markdown's no-Reddit create/readback probe when it is available. The current known desktop runtime may use `UTC_FIELDS`, where RRULE fields such as `BYHOUR`, `BYMINUTE`, and `BYSECOND` are UTC; in that mode, `11:29:43 Asia/Shanghai` is written as `03:29:43 UTC`. Another machine must not assume this result. Prefer an explicit one-shot target accepted by the automation tool. If the runtime hides persisted timing, keep the intended local and UTC pair in the heartbeat prompt and classify the result as `created_unreadable` rather than blocking current work.

Before creation, record:

- actual local time and timezone/UTC offset
- detected `scheduler_clock_mode` and its probe evidence when available; otherwise `unknown`
- target local time
- target UTC instant
- expected delay
- lane, next slot, and session stop time

After creation, immediately read back:

- stored trigger or displayed next run
- timezone/UTC interpretation when visible
- repeat setting; it must be off
- automation ID/name
- the scheduler's persisted `next_run_at` when the runtime exposes it; convert that epoch to both UTC and the intended local timezone

Creation and timing observability are separate. Classify:

- `verified`: persisted/displayed next run converted to both UTC and local time matches the intended instant within `5 min`, repeat is off
- `created_unreadable`: create/update returned success plus an automation ID/card, but persisted/displayed timing is not exposed; keep the trigger, do not claim exact timing verification, and compare actual wake time with the stored local/UTC target when it fires
- `display_suspect`: raw UTC is correct but UI display appears shifted
- `rescheduled`: first item was wrong, replacement was read back correctly
- `blocked`: create/update failed, wrong date or `>=60 min` drift is visible, repeat is visibly on, or an actual wakeup proves an uncorrectable timing error

`created_unreadable` is not `blocked`. Never delete a successful trigger, pause the first Reddit round, or ask the user to repair the scheduler merely because `next_run_at`, DTSTART, or a displayed next-run label is absent. The user cannot repair a field the runtime does not expose.

Never leave duplicate active triggers for the same account + lane + slot.

If the stored next run is exactly one local UTC offset away from the intended instant, classify it as `timezone_encoding_error`, update the existing automation in place using the detected `scheduler_clock_mode`, and read it back again. Do not wait for the incorrectly shifted trigger and do not create a duplicate.

## Adaptive Next Interval

Choose the next interval from lane state:

- follow-up: normally `20-40 min`; shorter only for an active direct exchange, longer for a quiet queue
- presence: based on next due profile/join/flair action, usually much longer than one comment slot
- comments: next incomplete workload slot after required spacing and candidate availability
- posts: next eligible post window after live rules, same-subreddit history, and diversity checks

Intervals may differ between rounds because state differs. Avoid exact repeated schedules when a nearby time is equally valid, but do not add randomness solely to mimic a person.

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

Triggers in different lanes coexist independently. A worker inspects only its own lane trigger and keeps at most one next one-shot trigger for that lane. It does not scan, compare, pause, delete, or reschedule another lane because of shared Chrome/account use, overlapping times, targets, or actions.

Before mutating an automation, verify only that `target_thread_id` is the current task and the prompt belongs to the current lane. A follow-up task cannot mutate comment/post/presence automations; a comment task cannot mutate post/follow-up/presence automations, and so on. When one user policy affects several lanes, each owner updates only its own trigger after receiving that instruction.
