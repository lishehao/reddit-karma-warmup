# Operating Flow Router

Use for `BOOTSTRAP` and `MISSION`. The main task is always `Loci Reddit运营`; it delegates Reddit mutations to lane owners.

## User Operation Router

The user always talks to `Loci Reddit运营`:

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

4. Keep the first-hour watch in ordinary task mode. Lane workers execute current work now. The coordinator may use one read-only one-shot heartbeat named `Loci Reddit运营-首轮监督` for delayed checks; it must never carry lane actions or be named `首轮后续`.
5. Use `gpt-5.6-luna/high` for the main task and every worker.

### A2. Dispatch Once

The user's `开始`/operation command explicitly authorizes persistent task creation for its enabled lanes. Reuse valid owners; otherwise create these user-visible tasks before any lane work:

| Task | First-hour responsibility |
|-|-|
| `主动评论` | Execute the current intensity envelope across diverse lower-restriction communities; pause `60-120 sec` after each verified submission. |
| `主动发帖` | Run one live candidate/preflight micro-slot; publish only when a native candidate passes, otherwise record verified no-post proof. |
| `消息跟进` | Sweep Notifications and recent own activity; reply only to actionable items. |
| `自然浏览` | Use the selected read budget across eligible communities; standard starts with `20-30` qualified reads and targets `2` verified combined votes, without lowering either vote gate. |

Before dispatch, perform bootstrap-only profile/membership setup in the main task when the account is visibly incomplete. Then create/reclaim all enabled workers, send each mission, and have every worker start now in its own Reddit tab. For default broad operation, all four rows above are mandatory. Do not collapse them into one task or let the main task perform their work.

Before the coordinator sends any final response, every enabled requested lane must return verified `start_proof`. If a worker is still preparing or returns only a plan, send one execute-now correction and read it again. If proof still cannot be read, mark that lane `startup_blocked` and report it; never run its micro-slot in the coordinator.

### A3. Main First-Hour Watch

The main task is read-only across workers:

1. Read initial progress in the same user turn, before final response. `5-10 min` is the first delayed recheck window after start proof, not permission to defer initial execution.
2. As soon as the first outward permalink appears, apply `startup-health-check.md` without pausing the comment worker.
3. Recheck that permalink in the `15-30 min` visibility window.
4. Read worker progress about every `10-15 min` as useful and automatically repair recoverable setup/scheduler issues.
5. At `watch_deadline`, run the mandatory final sweep: first-hour totals, visibility, warnings, worker next-trigger readback, and deadlines.
6. Delete the main task's temporary trigger and enter `IDLE`. Never continue proactive main-task polling after the boundary.
7. Record `bootstrap_state=initialized` when the account/profile baseline, worker registry, and final first-hour result are stored. This state means future user commands route to MISSION; it does not promote the Karma tier or erase new-account safeguards.

Startup acceptance passes only when all enabled lanes are accepted at the final sweep. A gap is reported accurately and is not marked as success.

### A4. Handoff

Workers continue independently until `operation_stop_at` using the selected intensity envelope. Do not catch up with bursts when fewer candidates pass. The main task stays idle until the user returns.

## Flow B: MISSION Through The Main Task

Trigger when the user later gives an active operation command in `Loci Reddit运营`, including while the account remains new after `bootstrap_state=initialized`. Do not reinstall, redecorate a healthy profile, or repeat BOOTSTRAP.

### B1. Route The Command

| User intent | Owner |
|-|-|
| `评论 N 条`, `主动评论`, named comment communities | `主动评论` |
| `发 N 篇帖子`, `主动发帖`, post angle/community | `主动发帖` |
| `看回复`, `看 Notifications`, supplied permalink | `消息跟进` |
| `浏览`, `自然浏览`, `刷帖`, `偶尔投票`, `upvote/downvote` | `自然浏览` |
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
watch_deadline
remaining_target
```

- One-shot mission with no future trigger: `watch_deadline = verified completion`, capped by the user deadline.
- Ongoing/multi-hour mission: `watch_deadline = min(operation_stop_at, start + 60m)`.
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
5. Only after that proof, update/create the owner's next trigger for the new remaining target/deadline; do not stack another.
6. Main reports the actual result, not merely `已启动`, and then continues bounded observation through one-shot heartbeats or returns to `IDLE` as appropriate.

## Flow C: STATUS And Control

- Status/progress/next run/risk: read relevant workers once, merge the four-field report, return to `IDLE`.
- Pause/resume/stop: send the change to affected owners; each owner updates only its own trigger. Confirm the result, then return to `IDLE`.
- A status request never creates a worker, Goal Mode, heartbeat, or Reddit action.

## Worker Handoff Contract

Every worker receives:

```text
role = WORKER
lane = [comments|posts|follow-up|browsing]
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

Every worker must load only its lane references, start the first due action immediately, verify visible results, update its local history, maintain at most one next trigger, and keep all status in its own task. Workers never callback or coordinate sibling lanes.

A newly dispatched worker's first response must include `start_proof`; it cannot end after reading, planning, naming, or scheduling. Every later execution-heartbeat response must include `slot_proof`. It creates its continuation heartbeat only after the current micro-slot is verified.

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

The first final response and all normal handoffs use the four-field report from `SKILL.md`, with an actual action/permalink or concrete verified no-action evidence.
