# Operation Request And Handoff Router

Use for `BOOTSTRAP` and `MISSION` only. This file owns request normalization, planning envelopes, mission deltas, and the worker handoff payload. It does not redefine task creation/supervision (`thread-supervision-runtime.md`), coordinator behavior (`coordinator-playbook.md`), lane execution (`orchestration-core.md` plus lane playbooks), timers (`scheduler-and-heartbeats.md`), or the three-line report (`SKILL.md`).

## Parse The User Request

The user always speaks to `Reddit 主控台`:

- `运营 [duration] [intensity] [style]`: enable comments, posts, follow-up, and natural browsing.
- `评论 ...`, `发帖 ...`, `跟进 ...`, or `自然浏览 ...`: enable only the named lane unless the user combines them.
- Defaults: `duration=3h`, `intensity=standard`, `operation_style=mixed`.
- Intensity aliases: `low/轻度/低`, `standard/标准/中等`, `high/高强度/高`.
- Resolve style aliases through `operation-style-profiles.md`: `mixed`, `builder`, `gaming-3d`, `spatial-place`, `social-creative`, or `custom`.
- An explicit per-lane count replaces that lane's intensity target. Duration, intensity, and counts remain quality-, rule-, and account-gated.

### Planning Envelope

These are planning targets, never quotas:

| Intensity | Comments | Posts | Follow-up | Natural browsing |
|-|-|-|-|-|
| `low` | `2-4/hour` | one candidate/preflight sweep per session | every `45-60 min` | `12-18` qualified reads; vote target/cap `2/2` |
| `standard` | `4-6/hour` | candidate/preflight sweep every `2-3h` | every `30-45 min` | `20-30` qualified reads; vote target/cap `2/4` |
| `high` | `6-10/hour` | candidate/preflight sweep every `60-90 min` | every `20-30 min` | `30-45` qualified reads; vote target/cap `4/6` |

Natural browsing includes qualified reading plus independently gated votes. After each browsing slot, choose the next delay independently from `20-40 min` unless the user overrides it. Profile setup, joins, and flair are bootstrap housekeeping, not a fifth recurring lane.

## Normalize BOOTSTRAP

Use `BOOTSTRAP` only when the user starts after installation and `bootstrap_state` is not initialized. Account age/Karma continues to affect pacing after initialization but does not rerun bootstrap.

Build:

```text
run_kind = BOOTSTRAP
mission_id
account + tier/substate
enabled_lanes
start_local + start_utc
operation_stop_at = start + requested duration
watch_deadline = min(operation_stop_at, start + 60m)
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

1. `new-account-bootstrap.md` and `community-presence-playbook.md` define the one-time truthful account baseline.
2. `thread-supervision-runtime.md` creates/reuses exact lane owners and verifies task IDs.
3. `coordinator-playbook.md` owns same-turn acceptance and the one-time first-hour watch.
4. Each worker receives the handoff below and starts its first due slot immediately.

Do not claim startup success until `coordinator-playbook.md` acceptance passes. Planning, task creation, and Heartbeat creation are not action proof.

## Normalize Later MISSION

After `bootstrap_state=initialized`, later commands reuse owners/history and never reinstall, redecorate a healthy profile, or restart first-hour supervision.

| User intent | Owner |
|-|-|
| comments or named comment communities | `Reddit 评论台` |
| main posts, angle, or post community | `Reddit 发帖台` |
| Notifications, replies, supplied permalink | `Reddit 跟进台` |
| browsing, reading, Upvote/Downvote | `Reddit 浏览台` |
| broad operation | all four owners |
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
- A style/voice change affects future slots only.
- Explicit browsing read/vote/cap/interval values replace only those fields.
- Count without duration derives a minimum window from the lane playbook when straightforward.

Send only this delta to the existing owner. `coordinator-playbook.md` owns same-turn acceptance; the worker owns later Heartbeats.

## STATUS And Control

- Status/progress/next run reads relevant owners once and merges the exact three-line report from `SKILL.md`.
- Pause/resume/stop routes only to affected owners; each changes only its own timer.
- A status request creates no worker, Goal Mode, Heartbeat, or Reddit action.
- Decision-requiring risk uses `risk-escalation.md`, not the ordinary report.

## Worker Handoff Payload

Every worker receives:

```text
role = WORKER
lane = comments | posts | follow-up | browsing
single_objective = exact one-line outcome from SKILL.md
out_of_scope = other lane outcomes and sibling coordination
worker_thread_id = exact persistent task ID
coordinator_thread_id = exact Reddit 主控台 task ID
operation_timer_id = NONE or exact lane-owned automation ID
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

The worker preserves one objective. Discovery, scoring, copy, rules, pacing, verification, reporting, recovery, and timer handling are supporting steps. It executes now, returns `start_proof`, and creates its logical timer only after first-slot proof. Later wakes return `slot_proof` before updating the same timer.

Workers send event returns only for a decision-requiring risk/blocker, one non-blocking `SUBREDDIT_RETIRED` notice per newly retired subreddit, or one terminal completion of the whole assigned mission. Ordinary slot progress remains local.

Terminal return:

```text
type = MISSION_COMPLETE
mission_id
lane
completion_reason = target_reached | deadline_reached | user_stopped | terminal_no_more_work
actual_result + key evidence
timer_state = cleared | stopped
remaining = 0 or exact unfulfilled count with reason
```

For a multi-lane mission, each lane returns once; only `Reddit 主控台` decides when the overall mission is complete.
