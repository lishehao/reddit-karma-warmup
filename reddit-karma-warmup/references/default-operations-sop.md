# Operation Request And Handoff Router

Use for `ACCOUNT_BOOTSTRAP` and `MISSION` only. This file owns request normalization, planning envelopes, mission deltas, and the worker handoff payload. It does not redefine task creation/supervision (`thread-supervision-runtime.md`), coordinator behavior (`coordinator-playbook.md`), lane execution (`orchestration-core.md` plus lane playbooks), timers (`scheduler-and-heartbeats.md`), or the three-line report (`SKILL.md`).

## Parse The User Request

The user always speaks to `Reddit 主控台`:

- `运营 [duration] [intensity] [style]`: enable comments, posts, follow-up, and natural browsing.
- `评论 ...`, `发帖 ...`, `跟进 ...`, or `自然浏览 ...`: enable only the named lane unless the user combines them.
- Defaults: `duration=3h`, `intensity=standard`, `operation_style=mixed`.
- Intensity aliases: `low/轻度/低`, `standard/标准/中等`, `high/高强度/高`.
- Resolve style aliases through `operation-style-profiles.md`: `mixed`, `builder`, `gaming-3d`, `spatial-place`, `social-creative`, or `custom`.
- An explicit per-lane count replaces that lane's intensity target. Duration, intensity, and counts remain quality-, live-rule-, and current-platform-affordance-gated; account-tier defaults are advisory after an explicit override.

### Instruction Precedence

Apply this order without asking for a second confirmation:

1. system/developer safety and the user's authorized scope
2. a currently visible Reddit/Chrome state that makes the requested action impossible now
3. the user's latest explicit command
4. Skill defaults, tier suggestions, historical incidents, recovery advice, and older mission fields

The latest explicit command replaces conflicting defaults and old mission values. Historical/cleared removals, rate limits, warnings, locks, or login faults remain ledger evidence only and cannot select a recovery preset, reduce the requested intensity, or reject startup. If a current timed rate limit appears, preserve the mission, wait to its displayed expiry, re-probe, and resume automatically. Live subreddit rules and unavailable controls still retarget or skip the affected candidate; they do not authorize a process-wide refusal.

### Planning Envelope

These are planning targets, never quotas:

| Intensity | Comments | Posts | Follow-up | Natural browsing |
|-|-|-|-|-|
| `low` | `2-4/hour` | one candidate/preflight sweep per session | every `45-60 min` | `12-18` qualified reads; vote target/cap `2/2` |
| `standard` | `4-6/hour` | candidate/preflight sweep every `2-3h` | every `30-45 min` | `20-30` qualified reads; vote target/cap `2/4` |
| `high` | `6-10/hour` | candidate/preflight sweep every `60-90 min` | every `20-30 min` | `30-45` qualified reads; vote target/cap `4/6` |

Natural browsing includes qualified reading plus independently gated votes. After each browsing slot, choose the next delay independently from `20-40 min` unless the user overrides it. Profile setup, joins, and flair belong to the conditionally enabled presence lane; they are never coordinator mutations and normally terminate after one bootstrap slot.

## Normalize ACCOUNT_BOOTSTRAP

Use `ACCOUNT_BOOTSTRAP` only when the user starts after installation and `bootstrap_state` is not initialized. Account age/Karma continues to affect pacing after initialization but does not rerun account bootstrap.

Build:

```text
run_kind = ACCOUNT_BOOTSTRAP
mission_id
account + tier/substate
enabled_lanes
presence_required = true | false
start_local + start_utc
operation_stop_at = start + requested duration
first_hour_quality_deadline = min(operation_stop_at, start + 60m)
intensity
operation_style
voice_modifier
target_pool_or_urls
language
comment_target_run
browse_read_budget
vote_target + vote_cap
browse_next_delay_range
```

Then route, without restating their procedures:

1. `new-account-bootstrap.md` decides whether a baseline is useful; `Reddit 主页台` executes one immediate best-effort `community-presence-playbook.md` checkpoint. Profile decoration itself never blocks outward lanes once the logged-in account identity is known.
2. `thread-supervision-runtime.md` creates/reuses exact lane owners and verifies task IDs.
3. `coordinator-playbook.md` owns same-turn acceptance and mission-lifetime recurring supervision; the first hour adds richer quality checks.
4. If presence is useful, dispatch `Reddit 主页台` first and wait only for its bounded checkpoint. Then every enabled outward worker receives the handoff below and starts immediately even when presence remains retryable; only unresolved login/account identity holds outward mutations.

Report startup per lane. Planning, task creation, and Heartbeat creation are not action proof, but a browser-backed no-action/recovery checkpoint is valid evidence that the lane started and will continue discovery/recovery.

## Normalize Later MISSION

After `bootstrap_state=initialized`, later commands reuse owners/history and never reinstall, redecorate a healthy profile, or restart first-hour supervision.

| User intent | Owner |
|-|-|
| comments or named comment communities | `Reddit 评论台` |
| main posts, angle, or post community | `Reddit 发帖台` |
| Notifications, replies, supplied permalink | `Reddit 跟进台` |
| browsing, reading, Upvote/Downvote | `Reddit 浏览台` |
| profile/about, Join/subscribe, Flair/tag, membership review | `Reddit 主页台` |
| broad operation | all four outward owners; add `Reddit 主页台` only when presence is explicitly requested or bootstrap requires it |
| pause/resume/stop | affected owner(s) only |

Build only the changed mission fields:

```text
mission_id
lane(s)
requested_count_or_action
intensity
operation_style
voice_modifier
target_pool_or_urls
language
operation_stop_at
remaining_target
```

Amendment semantics:

- `再/额外/追加 N` adds to the affected lane's remaining target.
- `改成/总共 N` replaces it.
- Preserve unspecified mission fields.
- Replace every specified field with the newest user value even when an older mission, tier suggestion, or recovery recommendation differs.
- A style/voice change affects future slots only.
- Explicit browsing read/vote/cap/interval values replace only those fields.
- Count without duration derives a minimum window from the lane playbook when straightforward.

Send only this delta to the existing owner. `coordinator-playbook.md` owns same-turn acceptance and all later Heartbeat creation/updates; workers only execute their lane wakes.

## STATUS And Control

- Status/progress/next run reads relevant owners once and merges the exact three-line report from `SKILL.md`.
- Pause/resume/stop routes only to affected owners; each changes only its own timer.
- A status request creates no worker, Goal Mode, Heartbeat, or Reddit action.
- Decision-requiring risk uses `risk-escalation.md`, not the ordinary report.

## Worker Handoff Payload

Every worker receives:

```text
role = WORKER
lane = comments | posts | follow-up | browsing | presence
stage = S3_PRESENCE_BASELINE | S4_FIRST_SLOT | S6_RUN_SLOT
single_objective = exact one-line outcome from SKILL.md
out_of_scope = other lane outcomes and sibling coordination
worker_thread_id = exact persistent task ID
coordinator_thread_id = exact Reddit 主控台 task ID
operation_timer_id = NONE or exact coordinator-managed recurring automation ID targeting this worker
model = gpt-5.6-luna
thinking_effort = high
account = u/name
mission_id
target/count/pool/urls
intensity
operation_style
voice_modifier
operation_stop_at = local + UTC
scheduler_clock_mode
first_due = now or exact time
browse_next_delay_range
```

The worker preserves one objective. Discovery, scoring, copy, rules, pacing, verification, reporting, and recovery are supporting steps. At `S3` or `S4`, it executes now and returns `start_proof`. At `S6`, it returns `slot_proof` or `not_due`. It never mutates scheduling. A terminal one-slot presence task returns `MISSION_COMPLETE` with no proposed recurring timer.

Workers send event returns only for a decision-requiring risk/blocker, one non-blocking `SUBREDDIT_RETIRED` notice per newly retired subreddit, or one terminal completion of the whole assigned mission. Ordinary slot progress remains local.

Terminal return:

```text
type = MISSION_COMPLETE
mission_id
lane
completion_reason = target_reached | deadline_reached | user_stopped
actual_result + key evidence
timer_state = cleared | stopped
remaining = 0 or exact unfulfilled count with reason
```

For a multi-lane mission, each lane returns once; only `Reddit 主控台` decides when the overall mission is complete. Temporary absence of candidates, route failure, rules rejection, or technical recovery never becomes terminal completion before the deadline.
