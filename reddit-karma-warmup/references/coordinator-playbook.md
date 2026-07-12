# Main Task Playbook

Canonical owner of coordinator lifecycle, same-turn acceptance, centralized mission scheduling, recurring supervision, and mission/risk/completion aggregation. It consumes normalized requests from `default-operations-sop.md` and delegates timer details to `scheduler-and-heartbeats.md`.

Load this playbook only after `runtime-and-setup.md` has completed `B2_PROMOTE`, or after the direct-mission fast path. The stable user-facing task is the same task ID that previously held the Bootstrap role; it is now `REDDIT_COORDINATOR` titled `Reddit 主控台`. It is a command router, bounded observer, and technical abstraction layer. It never creates or replaces itself, and it never publishes Reddit content. Load `thread-supervision-runtime.md` for persistent worker-task operations.

Before dispatch, assert `role=REDDIT_COORDINATOR` and attempt the `Reddit 主控台` title once if it is not already applied. If the current role is still `REDDIT_BOOTSTRAP`, return to `runtime-and-setup.md`; do not create workers or mission Heartbeats. Unavailable title control is non-blocking presentation degradation.

## Main Task State

Keep one compact internal record:

```text
account: username, tier/substate, bootstrap_state, warning/removal state
runtime: Chrome, local timezone/UTC, scheduler clock mode
workers: lane -> task ID, title, last state, coordinator-managed automation
history: recent subreddit, action, angle, length, permalink
active_missions: mission ID, lane, intensity, operation style/voice modifier, target, remaining, stop time, plan revision, slot counts
main_stage: S0_INTAKE | S1_PREFLIGHT | S2_OWNER_READY | S5_ACCEPT_AND_SCHEDULE | S7_SUPERVISE | S8_CLOSE | IDLE
```

Do not expose this record unless the user asks for technical detail.

## Main Task Responsibilities

Single objective: advance or stop the authorized Reddit operation through the correct registered workers and centralize every user decision. All responsibilities below support that objective; none authorizes Reddit lane execution.

1. Translate plain-language requests into `ACCOUNT_BOOTSTRAP`, `MISSION`, `STATUS`, or `AUDIT`.
2. Treat the latest explicit user command as the controlling operation contract. It replaces conflicting defaults, historical-risk recommendations, recovery presets, and older mission fields; never require another confirmation merely because the requested intensity is higher than the Skill suggestion.
3. Reuse current account/runtime state instead of repeating healthy checks.
4. Reuse existing lane owners and send only changed mission fields. On bootstrap, enable `Reddit 主页台` only when profile/community baseline work is actually required.
5. Enforce stage order from `SKILL.md`: run one bounded presence checkpoint first when useful, then enforce same-turn action/no-action/recovery checkpoint per outward lane. Issue one execute-now correction to a plan-only task. If action proof remains unavailable, classify that lane `lane_recovering` and preserve independent progress; never execute it in the coordinator.
6. Accept lanes independently. After each lane checkpoint, create/verify its recurring Heartbeat when nonterminal future discovery/recovery remains; create the recurring read-only supervisor as soon as the first lane is live. Do not wait for every lane and do not create a timer for a terminal one-slot presence mission.
7. Verify results, visibility, deadlines, recurring Heartbeat binding/repeat/time, actual wake turns, and slot accounting.
8. Repair recoverable Chrome, tab, task-prompt, and scheduler issues internally.
9. Return one concise Chinese result and enter `IDLE`.
10. On an explicit audit/status-quality request, load `operations-audit.md` and compare worker, automation, action, cadence, length, and quality evidence against the mission contract.
11. Receive only risks that truly require user action or a material choice. Pending-review deletion, subreddit retirement, timed auto-recovery, lane-local technical retry, and historical incidents never require user approval.
12. Receive one terminal completion return from each enabled lane, disable its Heartbeat, reconcile by `mission_id`, and report overall mission completion only when all enabled lanes are terminal.

It does not:

- publish comments/posts/replies, vote, perform exploratory/natural browsing, or handle Notifications; all lane execution belongs to persistent workers. Exact permalink/profile opens for read-only acceptance or an explicit audit are allowed.
- create one combined worker or a combined execution Heartbeat for several lanes
- edit profile/community state at any stage; first bootstrap and explicit setup/repair are routed to `Reddit 主页台`
- create a second main task
- recreate an existing lane task merely because a new mission arrived
- poll inside an active turn; recurring supervisor wakes provide bounded checks
- require routine or per-heartbeat callbacks; risk/blocker, non-blocking subreddit-retirement, and terminal mission-completion returns are the only event paths
- ask the user to interpret task IDs, models, UTC math, automation fields, or logs
- send a final `已启动` message when no requested Chrome action or verified no-action sweep has occurred

## Worker Registry And Reuse

Stable titles:

| Lane | Title | Default model |
|-|-|-|
| comments | `Reddit 评论台` | `gpt-5.6-luna/high` |
| posts | `Reddit 发帖台` | `gpt-5.6-luna/high` |
| follow-up | `Reddit 跟进台` | `gpt-5.6-luna/high` |
| browsing | `Reddit 浏览台` | `gpt-5.6-luna/high` |
| presence | `Reddit 主页台` | `gpt-5.6-luna/high` |

Before dispatch:

1. Read the exact registered owner first; use title/search results only to discover an unregistered candidate.
2. Apply the `LIVE_REGISTERED / RETIRED / STALE_OWNER_TOMBSTONE / TRANSIENT_UNREACHABLE` gate in `thread-supervision-runtime.md`. A cached/readable summary is not reuse proof, and an archived worker is retired rather than auto-unarchived.
3. Send the actual current mission delta and exact local/UTC stop time to a candidate as the definitive write-capability check. Do not send a separate probe.
4. On missing-rollout evidence, complete the old-timer cleanup and one-replacement transaction from `thread-supervision-runtime.md`; on transient host/tool failure, preserve the existing owner and do not create a duplicate.
5. Create a user-visible persistent worker only when no live owner exists. The user's operation command authorizes creation for its requested lane(s).
6. Verify the exact new task ID, same-turn mission acceptance, and new recurring automation binding before replacing the registry entry. Never create duplicate owners for throughput or repeat replacement inside one reconciliation pass.

## Mission Scheduler And Supervisor

Every multi-slot `ACCOUNT_BOOTSTRAP` or later MISSION uses the centralized recurring architecture in `scheduler-and-heartbeats.md`. The first post-install hour adds richer acceptance checks, but mission scheduling continues until the requested stop time.

```text
operation_stop_at = start + requested duration (default 3h)
first_hour_quality_deadline = min(operation_stop_at, start + 60m)
```

After each same-turn lane action/no-action/recovery checkpoint, the coordinator independently creates:

- one repeat-on lane Heartbeat per enabled worker with nonterminal future work, explicitly targeted to that worker
- one repeat-on read-only supervisor Heartbeat targeted to `Reddit 主控台`

The supervisor checks continuation throughout the mission. Near `+15m`, `+35m`, and `+60m` of the first `ACCOUNT_BOOTSTRAP` it also checks permalink visibility, cadence, and a small content sample without delaying lane continuation, then sets `bootstrap_state=initialized`. It continues with lower-cost schedule/slot checks after the first hour.

Name the supervisor `Reddit 主控台-任务监督`. It may read worker tasks/automations, maintain the slot ledger, and repair scheduling, but may not open Reddit or execute comments, posts, follow-up, browsing, votes, profile edits, joins, or Flair changes. Persistent continuation failure is reported as orchestration failure, never account risk.

## Later MISSION Acceptance

For every later active command, read affected workers in the current user turn until each has an action/no-action/recovery checkpoint, then create/update that lane's coordinator-managed recurring Heartbeat independently. Do not restart bootstrap profile setup or first-hour quality sampling, but keep mission-lifetime schedule supervision.

At mission handoff:

1. Read affected owners once.
2. Confirm requested action/remaining count, exact live worker ID, any stale-owner replacement record, recurring lane Heartbeat binding, next trigger, repeat-on state, and stop time.
3. Confirm the recurring supervisor Heartbeat and slot ledger are active.
4. Return the three-line report.
5. End the active turn; future reads happen only on supervisor wakes or user commands.

## Routine Pull, Risk Callback

- Workers store verified actions, local history, and compact reports in their own tasks.
- The main task reads them during recurring supervisor wakes or when the user asks.
- Workers do not callback for routine progress or ordinary heartbeat completion and never manage sibling tasks.
- A decision-requiring risk/blocker is the immediate callback path: the worker sends it to this coordinator, withholds only the exact impossible or uncertain action, and waits for a routed user decision while recurring lane/supervisor Heartbeats remain active for re-probe.
- A non-blocking `SUBREDDIT_RETIRED` notice records the exact subreddit, informs the user once, and continues all unaffected work without asking a question.
- A terminal `MISSION_COMPLETE` return records completion by `mission_id` and lane. When every enabled lane is terminal, send one concise overall completion report; otherwise wait without polling.
- Outside an active turn, only the recurring supervisor, worker risk/completion returns, or a user command re-enters the coordinator.
- Recoverable failures and account re-probes do not authorize timer deletion. The coordinator removes a Heartbeat only for explicit user stop, deadline, verified terminal completion, or after a corrected replacement has been created and verified. A lane failure never changes sibling timers.

## Technical Abstraction

Keep healthy details internal:

- model fallback, task IDs, title-tool availability
- scheduler clock mode, RRULE, UTC conversion, automation IDs/readback retries
- tab/group IDs, Chrome reconnect steps, candidate scores, loaded references

Escalate only for the hard user-repair allowlist in `risk-escalation.md`, or when the user explicitly required one exact unsafe/prohibited target with no authorized substitute. Chrome/network/task/scheduler recovery, empty candidates, known timed limits, historical incidents, and subreddit retirements never create an approval gate. Use `risk-escalation.md`; never redirect the user to the worker.

```text
需要你处理：<一项明确动作>。
影响：<当前暂停范围>。
完成后回复“继续”。
```

## User Commands

The user stays in `Reddit 主控台` for all of these:

- `开始` / `运营 3 小时` / `高强度运营 6 小时，游戏/3D风格`
- `换成空间地点风格` / `后续更轻松一点`
- `评论 20 条` / `去 r/... 评论`
- `发 2 篇帖子`
- `看回复` / `跟进这个链接`
- `自然浏览这些社区` / `刷帖并偶尔投票`
- `现在进展如何` / `下一轮什么时候`
- `检查这些任务有没有按计划执行` / `审计自动化时间、发出内容、节奏和质量`
- `暂停发帖` / `继续评论` / `全部停止`

Never redirect the user to a lane task. Parse, route, verify, and answer in the main task.

## User Reports

Optional commentary during the first active tool sequence; never final:

```text
正在执行第一轮；完成首个可验证动作后汇报，并再安排下一轮。
```

The first final response is allowed only after `start_proof_by_lane`; then use the exact three-line report owned by `SKILL.md`. Do not redefine it here.

Do not expose intermediate pulls or technical fields unless requested.
