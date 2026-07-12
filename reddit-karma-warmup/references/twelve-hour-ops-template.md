# Twelve-Hour Autonomous Lane Template

Use inside one lane task when the user requests a long timed run. A broad request is already split by `Reddit 启动台`; each task follows this template independently.

## Contract

- `operation_stop_at = start + 12h` unless the user supplied another cutoff.
- Execute the first lane slot immediately.
- Create/update one repeat-on Heartbeat targeting this exact task.
- Keep the same timer through recoverable failures.
- At each wake, run one due slot or record `not_due`, then compute the next local/UTC wake.
- Retire only this task's timer at stop, deadline, verified lane completion, or verified replacement.
- Never inspect, report through, pause, or modify another lane task.

## Lane Examples

| Lane | Typical 12-hour behavior |
|-|-|
| comments | distribute passing comments across varied periods and communities; preserve length/angle variation |
| posts | perform periodic live rules/eligibility sweeps; publish only passing native posts |
| follow-up | check Notifications and own activity on a varied cadence; reply only to Act items |
| browsing | run qualified-read batches with independently gated votes and varied `20-40m` intervals |
| presence | normally one slot; continue only when explicitly requested |

Do not catch up after a delay with bursts. Replan from actual time and remaining quality opportunities.
