# Operation Request Router

Use in the one-time launcher to split a broad first request, and in a lane task to normalize only that lane's later request.

## Defaults

- missing duration: `3h`
- missing intensity: `standard`
- missing style: `mixed`
- broad `开始/运营`: comments + posts + follow-up + browsing
- presence: only when explicitly requested or the first profile baseline is incomplete

Resolve style through `operation-style-profiles.md`. Explicit user counts, duration, language, pool, style, or lane replace defaults without another confirmation.

Planning targets are quality-gated:

| Intensity | Comments | Posts | Follow-up | Browsing |
|-|-|-|-|-|
| low | `2-4/hour` | one candidate/rules sweep per session | `45-60m` | `12-18` qualified reads; vote target/cap `2/2` |
| standard | `4-6/hour` | one candidate/rules sweep every `2-3h` | `30-45m` | `20-30` qualified reads; vote target/cap `2/4` |
| high | `6-10/hour` | one candidate/rules sweep every `60-90m` | `20-30m` | `30-45` qualified reads; vote target/cap `4/6` |

## Launcher Split

Build one independent mission per enabled lane:

```text
mission_id
lane
single_objective
out_of_scope
account
duration/count/intensity/style/language
target_pool_or_urls
start_local + start_utc
operation_stop_at
first_due=now
heartbeat_owner=self
launcher_callback=none
sibling_visibility=none
```

The missions share only user-provided scope and account identity. They do not share runtime state, Heartbeats, risk, completion, cadence, history, or control.

## Later Lane Mission

When the user speaks inside a lane task:

1. Accept only instructions for that lane.
2. Replace conflicting old mission fields with the latest command.
3. Preserve this lane's verified account, tab, history, and own Heartbeat when still valid.
4. Execute the first changed slot now.
5. Update only this task's Heartbeat for remaining work.

If the request belongs to another lane, answer briefly with the correct task title. Do not message, create, inspect, or amend that task.

## Status And Stop

A status request reports only the current lane. Pause/resume/stop changes only the current lane and its own Heartbeat unless the user separately addresses other tasks.
