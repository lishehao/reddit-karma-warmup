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
| comments | `4-6/hour`, with at least the lane's configured minimum spacing |
| posts | one candidate/rules sweep every `2-3h`; publish only when eligible |
| follow-up | every `30-45m` |
| browsing | every `20-40m`; normally `20-30` qualified reads |
| presence | terminal after one slot unless the user explicitly requests ongoing presence work |

Use short in-turn sleep only for human-scale submit pauses below roughly five minutes. Use the recurring Heartbeat for longer waits.

## Wake Flow

On every wake:

1. Verify the Heartbeat targets this exact task and current lane mission.
2. Read actual local time/timezone and UTC; compare with intended schedule.
3. Reconnect Chrome or reclaim only this task's tab.
4. If the slot is due, execute one bounded lane slot and record action/no-action/recovery proof.
5. If not due, record `not_due`; do not manufacture activity.
6. Recompute the next due time from remaining duration/count and live conditions.
7. Update only this task's timer when mission fields, cadence, or cutoff changed.

## Survival And Repair

Technical failure is not timer termination. Keep the lane Heartbeat repeat-on through Chrome disconnect, stale tab, DNS/network/proxy/TLS errors, `ERR_BLOCKED_BY_CLIENT`, blank/loading pages, route failure, candidate exhaustion, rules rejection, subreddit retirement, timed rate limit, uncertain exact mutation, or a failed recovery wake.

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
