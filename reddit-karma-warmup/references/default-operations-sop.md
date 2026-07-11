# Operating Flow Router

Use for `BOOTSTRAP` and `MISSION`. The main task is always `Reddit 主控台`; it delegates Reddit mutations to lane owners.

## User Operation Router

The user always talks to `Reddit 主控台`:

- `运营 [duration] [intensity] [style]`: enable comments, posts, follow-up, and natural browsing.
- `评论 ...`, `发帖 ...`, `跟进 ...`, or `自然浏览 ...`: enable only the named lane unless the user combines them.
- Duration may be supplied without intensity; intensity may be supplied without duration.
- Defaults: `duration=3h`, `intensity=standard`, `operation_style=mixed`.
- Intensity aliases: `low/轻度/低`, `standard/标准/中等`, `high/高强度/高`.
- Style aliases and profiles come from `operation-style-profiles.md`: `mixed`, `builder`, `gaming-3d`, `spatial-place`, `social-creative`, or `custom`.
- An explicit per-lane count replaces that lane's intensity target. User-supplied duration/intensity/count still remains quality-, rule-, and account-gated.

Use this planning envelope, not a quota:

| Intensity | Comments | Posts | Follow-up | Natural browsing |
|-|-|-|-|-|
| `low` | target `2-4/hour` | one candidate/preflight sweep per session; publish only a passing candidate | every `45-60 min` | `12-18` qualified reads; vote target `2`, cap `2` |
| `standard` | target `4-6/hour` | candidate/preflight sweep every `2-3h`; normally at most one passing post in a short session | every `30-45 min` | `20-30` qualified reads; vote target `2`, cap `4` |
| `high` | target `6-10/hour` | candidate/preflight sweep every `60-90 min`; live post limits still dominate | every `20-30 min` | `30-45` qualified reads; vote target `4`, cap `6` |

Natural browsing includes qualified reading plus gated Upvote/Downvote. The intensity table supplies a default target and cap, not permission to lower the vote gate. After each completed browsing slot, select the next delay independently from `20-40 min`; the delay starts after slot completion, not at slot start. An explicit user instruction may replace the read budget, vote target, cap, or delay range, including `0` votes for browse-only. Profile setup, joins, and flair are bootstrap housekeeping, not a fifth recurring operation lane.

## Flow A: BOOTSTRAP From Zero

Trigger when the user confirms the first start after installation, or `bootstrap_state` is not initialized and the visible account is blank, under `48h`, has very low/unknown Karma, or has no clean visible history.

### A1. Build The Contract

1. Reconfirm the logged-in account and actual local/UTC time; do not rerun installation.
2. Inspect account age, Karma, recent history, warnings/removals, profile completeness, memberships, and Notifications.
3. Set:

```text
run_kind = BOOTSTRAP
operation_stop_at = start + requested duration (default 3h)
watch_deadline = min(operation_stop_at, start + 60m)
intensity = requested intensity (default standard)
operation_style = requested/resolved style (default mixed)
voice_modifier = optional user modifier
comment_target_run = intensity envelope x run_hours, clamped by account/recovery state
browse_slot = intensity read budget (standard: 20-30 qualified reads)
vote_target_per_browse_slot = explicit user target or intensity default (standard: 2 combined votes)
vote_cap_per_browse_slot = explicit user cap or intensity cap (standard: 4 combined votes)
browse_next_delay = explicit user interval or a fresh integer from 20-40 min after slot completion
```

4. Keep the one-time post-install first-hour watch in ordinary task mode. Lane workers execute current work now. The coordinator uses one read-only logical heartbeat timer named `Reddit 主控台-首轮监督`, reusing its automation ID across delayed checkpoints; it must never carry lane actions or be named `首轮后续`.
5. Use `gpt-5.6-luna/high` for the main task and every worker.

### A2. Dispatch Once

The user's `开始`/operation command explicitly authorizes persistent task creation for its enabled lanes. Reuse valid owners; otherwise create these user-visible tasks before any lane work:

| Task | First-hour responsibility |
|-|-|
| `Reddit 评论台` | Execute the current intensity envelope across diverse lower-restriction communities; pause `60-120 sec` after each verified submission. |
| `Reddit 发帖台` | Run one live candidate/preflight micro-slot; publish only when a native candidate passes, otherwise record verified no-post proof. |
| `Reddit 跟进台` | Sweep Notifications and recent own activity; reply only to actionable items. |
| `Reddit 浏览台` | Use the selected read budget across eligible communities; standard starts with `20-30` qualified reads and targets `2` verified combined votes, without lowering either vote gate. |

Before dispatch, perform bootstrap-only profile/membership setup in the main task when the account is visibly incomplete. Then create/reclaim all enabled workers, send each mission, and have every worker start now in its own Reddit tab. For default broad operation, all four rows above are mandatory. Do not collapse them into one task or let the main task perform their work.

Before the coordinator sends any final response, every enabled requested lane must return verified `start_proof`. If a worker is still preparing or returns only a plan, send one execute-now correction and read it again. If proof still cannot be read, mark that lane `startup_blocked` and report it; never run its micro-slot in the coordinator.

### A3. Main First-Hour Watch

The main task is read-only across workers:

1. Read initial progress in the same user turn, before final response. The first delayed checkpoint is not permission to defer initial execution.
2. As soon as the first outward permalink appears, apply `startup-health-check.md` without pausing the comment worker.
3. Schedule only the next checkpoint at a time: first near `start+15m`, second near `start+35m` (about `20m` later), and final at `watch_deadline` near `start+60m`. Read back target task and local/UTC time after each creation.
4. At `+15m`, read all enabled worker states, verify their owned heartbeat binding/time, and recheck the first permalink/first no-action proof.
5. At `+35m`, read progress again and check actual actions, cadence, automation wake evidence, blockers, and a small sample of published length/quality.
6. At `watch_deadline`, run the mandatory final sweep: first-hour totals, visibility, warnings, worker next-trigger readback, deadlines, and any unresolved risk.
7. After every checkpoint, report only a concise meaningful delta; risk uses `risk-escalation.md`. Do not poll between checkpoints.
8. Delete the main task's temporary trigger and enter `IDLE` after the final sweep. Never continue proactive main-task polling after the boundary.
9. Record `bootstrap_state=initialized` when the account/profile baseline, worker registry, and final first-hour result are stored. This state means future user commands route to MISSION; it does not promote the Karma tier or erase new-account safeguards. Skill upgrades/version changes do not reset it.

Startup acceptance passes only when all enabled lanes are accepted at the final sweep. A gap is reported accurately and is not marked as success.

### A4. Handoff

Workers continue independently until `operation_stop_at` using the selected intensity envelope. Do not catch up with bursts when fewer candidates pass. The main task stays idle until the user returns.

## Flow B: MISSION Through The Main Task

Trigger when the user later gives an active operation command in `Reddit 主控台`, including while the account remains new after `bootstrap_state=initialized`. Do not reinstall, redecorate a healthy profile, or repeat BOOTSTRAP.

### B1. Route The Command

| User intent | Owner |
|-|-|
| `评论 N 条`, `主动评论`, named comment communities | `Reddit 评论台` |
| `发 N 篇帖子`, `主动发帖`, post angle/community | `Reddit 发帖台` |
| `看回复`, `看 Notifications`, supplied permalink | `Reddit 跟进台` |
| `浏览`, `自然浏览`, `刷帖`, `偶尔投票`, `upvote/downvote` | `Reddit 浏览台` |
| `运营 [N 小时] [强度] [风格]` | comments + posts + follow-up + natural browsing |
| `换成游戏/3D风格`, `后续更专业一点` | update style/modifier for future slots of active lanes; if idle, store as the next mission default |
| `暂停/继续/停止 X` | affected owner(s) only |

### B2. Build A Mission Delta

Read only the relevant workers plus current account state. Create:

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

- Later missions receive same-turn coordinator acceptance through the first verified result and worker heartbeat handoff. They do not create delayed coordinator-watch heartbeats.
- User count without duration: estimate the minimum window from the lane playbook; do not ask when the derivation is straightforward.
- `再/额外/追加 N` adds to the affected lane's remaining target.
- `改成/总共 N` replaces that lane's remaining target.
- `暂停/停止/继续` changes only the named lane; unaffected missions and heartbeats continue.
- The latest explicit community, language, or deadline replaces that field only; preserve unspecified mission fields.
- The latest explicit operation style or voice modifier replaces only that field. Resolve aliases through `operation-style-profiles.md` before dispatch.
- For natural browsing, parse an explicit read count, vote target, vote cap, interval/range, or `只浏览不投票`. Explicit values replace only the corresponding browsing field. Without an interval instruction, select each next delay independently from `20-40 min` after the current slot completes.

### B3. Reuse, Amend, Execute

1. Reuse the matching persistent lane task from the registry. Create it when no valid owner exists; the current operation command is explicit authorization for that requested lane.
2. Send only the mission delta; do not resend installation instructions or reset history.
3. The owner immediately executes the first due slot using `gpt-5.6-luna/high`.
4. Main reads the owner in the current turn until it returns a verified requested action or concrete browser-backed no-action/blocker. If it returns only planning/acknowledgement, send one execute-now correction and read again. If it still cannot execute, report the lane blocker; main never performs the lane action.
5. Only after that proof, update/reuse the owner's logical operation timer for the new remaining target/deadline; do not stack another.
6. Main reports the actual result, not merely `已启动`, then returns to `IDLE`. Worker-owned heartbeats continue the mission; the coordinator does not restart post-install supervision.

## Flow C: STATUS And Control

- Status/progress/next run: read relevant workers once, merge the three-line report, return to `IDLE`. Decision-requiring risks use the separate risk callback.
- Pause/resume/stop: send the change to affected owners; each owner updates only its own trigger. Confirm the result, then return to `IDLE`.
- A status request never creates a worker, Goal Mode, heartbeat, or Reddit action.

## Worker Handoff Contract

Every worker receives:

```text
role = WORKER
lane = [comments|posts|follow-up|browsing]
single_objective = exact one-line outcome from SKILL.md
out_of_scope = other three lane outcomes and sibling coordination
worker_thread_id = exact persistent task ID returned at create/reuse time
coordinator_thread_id = Reddit 主控台 task ID
operation_timer_id = NONE or exact lane-owned automation ID
model = gpt-5.6-luna
thinking_effort = high
account = u/name
mission_id
target/count/pool/urls
intensity = low | standard | high
operation_style = mixed | builder | gaming-3d | spatial-place | social-creative | custom
voice_modifier = optional
operation_stop_at = local + UTC
scheduler_clock_mode
first_due = now or exact time
browse_next_delay_range = custom or 20-40 min
```

Every worker must preserve its one `single_objective`; discovery, scoring, copy, rule checks, pacing, verification, reporting, and timer work are supporting steps. It loads only its lane references plus `risk-escalation.md`, starts the first due action immediately, verifies visible results, updates local history, and maintains one logical heartbeat timer explicitly bound to `worker_thread_id`. An off-lane request returns to the coordinator instead of becoming a second objective. Ordinary slot status stays in its own task. Workers never coordinate sibling lanes. They send a structured callback to `coordinator_thread_id` only for a decision-requiring risk/blocker or the one terminal completion of the whole assigned mission.

A newly dispatched worker's first response must include `start_proof`; it cannot end after reading, planning, naming, or scheduling. Every later execution-heartbeat response must include `slot_proof`. It creates its logical operation timer only after the first micro-slot is verified, then updates and reuses that same timer for later slots.

At terminal mission completion, clear/stop the lane timer and return exactly once:

```text
type = MISSION_COMPLETE
mission_id = exact mission ID
lane = comments | posts | follow-up | browsing
completion_reason = target_reached | deadline_reached | user_stopped | terminal_no_more_work
actual_result = counts plus concise verified outcomes
evidence = key permalinks or no-action proof
timer_state = cleared | stopped
remaining = 0 or exact unfulfilled count with reason
```

Do not emit this after an ordinary heartbeat slot. If several lanes belong to one mission, each lane returns once; `Reddit 主控台` alone decides when the overall mission is complete.

## User-Facing Messages

Optional start commentary while tools are running; never use as the final answer:

```text
正在执行第一轮；完成首个可验证动作后汇报，并再安排下一轮。
```

User-required repair only:

```text
需要你处理：<一项明确动作>。
影响：<当前暂停范围>。
完成后回复“继续”。
```

The first final response, every heartbeat result, and all normal handoffs use the exact three-line report from `SKILL.md`, with an actual action/permalink or concrete verified no-action evidence in `本轮完成`.
