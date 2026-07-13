# Worker-Owned Scheduler And Heartbeat

Canonical owner of one lane task's recurring continuation. Load only inside the lane task that owns the mission.

## Ownership

The worker is the only scheduler for its lane. It creates, reads, updates, repairs, and retires one recurring Heartbeat explicitly targeted to its own exact task ID. There is no launcher/coordinator supervisor Heartbeat and no cross-lane timer registry.

## Start Rule

1. Execute the first requested slot immediately in the current user turn.
2. If nonterminal work remains, create one repeat-on Heartbeat with `targetThreadId=self_task_id`, a finite cutoff or explicit `operation_stop_at`, and the current mission fields.
3. Read back the exact automation ID, target, repeat state, recurrence, next local time, UTC time, and deadline when exposed.
4. If next-run fields are hidden, record `created_unreadable` and continue. Do not ask the user to repair an unexposed field.

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

## Clustered Comment Windows

For comments, plan operational batches instead of a uniform per-comment clock:

1. Compute `effective_hourly_rate` from the latest controlling target and remaining time.
2. For roughly `6-10 comments/hour`, normally create `2-3` batch windows per hour. Vary the gap from actual completion time, usually `20-35m`, instead of repeating an exact interval.
3. Give each due window an exact `batch_target` of at least `2`, normally `2-4` verified comments, and an active work envelope of about `4-8m`. `minimum_completed_cluster_size=2` and `single_comment_cluster=forbidden`. Candidate quality, rules, and the mission cap still gate every action.
4. Inside a window, keep the existing pre-submit pause and `60-120 sec` pause after each verified proactive comment. Use local sleep for these sub-five-minute waits; use the lane Heartbeat between windows.
5. Preserve `batch_target_remaining` and `slot_target_remaining`. After one verified proactive comment, the current wake stays active and continues discovery until the second passes; do not yield, schedule the next Heartbeat, or report a completed window after only one. A user-requested exact-one total is a single-action mission rather than a cluster. A user stop, deadline, or current hard blocker may produce `cluster_incomplete`, which carries its exact remainder forward without lowering thresholds or creating a catch-up burst.
6. Recompute later windows from actual verified count and remaining time. Do not precompute a mechanically identical all-day schedule.

Example: `80 comments / 10h` resolves to `8/hour`, not `10/hour`. A representative hour may use three windows such as `3 + 2 + 3`, with each window starting after a varied `20-35m` gap. The exact distribution changes with qualified candidates and actual completion time; it is not a promise to publish weak comments.

Before creating or updating the inter-window Heartbeat, assert `verified_comments_in_current_window >= 2` or `explicit_exact_one_mission=true`. If neither is true, keep working in the current wake. Recoverable browser/network failure does not satisfy the assertion; preserve the incomplete cluster and retry locally or on the same lane's continuation without calling it a completed window.

## Wake Flow

On every wake:

1. Verify the Heartbeat targets this exact task and current lane mission.
2. Read actual local time/timezone and UTC; compare with intended schedule.
3. Reconnect Chrome or reclaim only this task's tab.
4. If the slot is due, resume its preserved `slot_target_remaining` and continue discovery/action toward zero. A runtime boundary may yield an interim checkpoint, but does not complete or reset the slot.
5. If not due, record `not_due`; do not manufacture activity.
6. Recompute the next due time from the exact remaining duration/count, current batch remainder, and live conditions; unfinished action targets receive the next permissible continuation rather than a fresh slot.
7. Update only this task's timer when mission fields, cadence, or cutoff changed.

## Survival And Repair

Technical failure is not timer termination. Candidate scarcity is also not timer termination. Keep the lane Heartbeat repeat-on through Chrome disconnect, stale tab, DNS/network/proxy/TLS errors, `ERR_BLOCKED_BY_CLIENT`, blank/loading pages, route failure, candidate exhaustion, rules rejection, subreddit retirement, timed rate limit, uncertain exact mutation, or a failed recovery wake. Resume the same remaining target after recovery. If every current expansion route is genuinely exhausted, yield an interim checkpoint and retry fresh surfaces on the next wake rather than declaring the action target complete.

For a malformed/missing/misbound timer, repair in place when possible. Otherwise create and verify one corrected self-targeted replacement before removing the old timer. Never inspect, pause, repair, or delete another task's timer.

## Terminal Reasons

Retire this lane's Heartbeat only after:

- explicit user stop for this lane;
- `operation_stop_at` reached;
- verified completion of this lane's requested count/objective; or
- verified no-gap replacement by a corrected timer.

At termination, release only this task's Chrome tab and report in this task. Do not notify the launcher or any sibling.

## Three-Line Receipt

```text
本轮完成：<该 lane 动作、链接或恢复结果>。
下轮时间：<验证后的当地时间；终止则写“无”>。
下轮计划：<该 lane 下一项工作和当前真实风险>。
```
