# Operating Flow Router

Use for `BOOTSTRAP` and `MISSION`. The main task is always `Loci Reddit运营`; it delegates Reddit mutations to lane owners.

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
comment_target_first_hour = 10
comment_target_run = min(60, 10 x run_hours)
browse_slot = 8-12 qualified reads
vote_cap_per_browse_slot = 1 combined upvote/downvote
```

4. Keep the first-hour watch in ordinary task mode. Execute current work now and use one coordinator-owned one-shot heartbeat at a time for delayed checks; never enter Goal Mode.
5. Use `gpt-5.6-sol/xhigh` for the main task and `gpt-5.6-luna/high` for every worker.

### A2. Dispatch Once

Reuse valid owners; otherwise create these tasks:

| Task | First-hour responsibility |
|-|-|
| `主动评论` | Publish up to `10` passing short comments across at least `3` lower-restriction communities; pause `60-120 sec` after each verified submission. |
| `主页维护` | Apply minimum truthful profile setup and join `1-3` high-fit communities when due. |
| `消息跟进` | Sweep Notifications and recent own activity; reply only to actionable items. |
| `内容浏览` | Read `8-12` qualified items across `2-4` eligible communities; cast at most one combined vote only when its quality gate passes. |
| `主动发帖` | Disabled by default; create only when the user enables posts or a strong eligible post mission exists. |

Each worker starts now in its own Reddit tab. Do not wait for another lane. Posts remain optional and never replace the comment target.

Before the coordinator sends any final response, at least one enabled requested lane must return verified `start_proof`. If workers are still preparing, only planned, or cannot be read immediately, the coordinator runs the first requested micro-slot sequentially. It may then return ownership of later slots to the workers.

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

Workers continue independently until `operation_stop_at`. For the default `3h` run, the comment planning target is `30`; do not catch up with bursts when fewer candidates pass. The main task stays idle until the user returns.

## Flow B: MISSION Through The Main Task

Trigger when the user later gives an active operation command in `Loci Reddit运营`, including while the account remains new after `bootstrap_state=initialized`. Do not reinstall, redecorate a healthy profile, or repeat BOOTSTRAP.

### B1. Route The Command

| User intent | Owner |
|-|-|
| `评论 N 条`, `主动评论`, named comment communities | `主动评论` |
| `发 N 篇帖子`, `主动发帖`, post angle/community | `主动发帖` |
| `看回复`, `看 Notifications`, supplied permalink | `消息跟进` |
| `装修主页`, `join`, `flair/tag` | `主页维护` |
| `浏览`, `刷帖`, `偶尔投票`, `upvote/downvote` | `内容浏览` |
| `运营 N 小时`, multiple actions | only affected existing owners; default comments + follow-up + presence + browsing, posts optional |
| `暂停/继续/停止 X` | affected owner(s) only |

### B2. Build A Mission Delta

Read only the relevant workers plus current account state. Create:

```text
mission_id
lane(s)
requested_count_or_action
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

### B3. Reuse, Amend, Execute

1. Reuse the matching lane task from the registry. Create one only when no valid owner exists.
2. Send only the mission delta; do not resend installation instructions or reset history.
3. The owner immediately executes the first due slot using `gpt-5.6-luna/high`.
4. Main reads the owner in the current turn until it returns a verified requested action or concrete browser-backed no-action/blocker. If it returns only planning/acknowledgement or cannot execute now, main runs the first micro-slot sequentially.
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
lane = [comments|posts|follow-up|presence|browsing]
model = gpt-5.6-luna
thinking_effort = high
account = u/name
mission_id
target/count/pool/urls
operation_stop_at = local + UTC
scheduler_clock_mode
first_due = now or exact time
```

Every worker must load only its lane references, start the first due action immediately, verify visible results, update its local history, maintain at most one next trigger, and keep all status in its own task. Workers never callback or coordinate sibling lanes.

A newly dispatched worker's first response must include `start_proof`; it cannot end after reading, planning, naming, or scheduling. It creates its continuation heartbeat only after the first micro-slot is verified.

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
