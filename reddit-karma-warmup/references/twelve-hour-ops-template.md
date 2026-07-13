# Twelve-Hour Autonomous Lane Template

Use inside one lane task when the user requests a long timed run. A broad request is already split by `Reddit 分发台`; each task follows this template independently.

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
| comments | use `clustered_windows`: normally 2-3 short batches per active hour for a 6-10/hour target, with varied 20-35m inter-window gaps; preserve copy/community variation and assess incidental votes only on already-read candidates |
| posts | perform periodic live rules/eligibility sweeps; publish only passing native posts; assess incidental votes only on opened external samples |
| follow-up | check Notifications and own activity on a varied cadence; reply only to Act items; assess incidental votes only on opened inbound replies |
| browsing | explicit-only pure browsing: run qualified-read batches with independently gated votes and varied `20-40m` intervals |
| presence | normally one slot; continue only when explicitly requested |

Deliberate short comment windows are allowed; catch-up floods are not. If a window underfills, carry the remainder and replan from actual time and remaining quality opportunities without compressing later spacing or lowering quality gates.
