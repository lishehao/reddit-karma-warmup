# Main Task Playbook

Canonical owner of coordinator lifecycle, same-turn acceptance, first-hour supervision, and mission/risk/completion aggregation. It consumes normalized requests from `default-operations-sop.md` and does not redefine worker slot or timer procedures.

The stable user-facing task is `Reddit 主控台`. It is a command router, bounded observer, and technical abstraction layer. Load `thread-supervision-runtime.md` for persistent task operations. It never publishes Reddit content.

## Main Task State

Keep one compact internal record:

```text
account: username, tier/substate, bootstrap_state, warning/removal state
runtime: Chrome, local timezone/UTC, scheduler clock mode
workers: lane -> task ID, title, last state, owned automation
history: recent subreddit, action, angle, length, permalink
active_missions: mission ID, lane, intensity, operation style/voice modifier, target, remaining, stop time
main_state: INTAKE | DISPATCH | WATCH | HANDOFF | IDLE
```

Do not expose this record unless the user asks for technical detail.

## Main Task Responsibilities

Single objective: advance or stop the authorized Reddit operation through the correct registered workers and centralize every user decision. All responsibilities below support that objective; none authorizes Reddit lane execution.

1. Translate plain-language requests into `BOOTSTRAP`, `MISSION`, `STATUS`, or `AUDIT`.
2. Treat the latest explicit user command as the controlling operation contract. It replaces conflicting defaults, historical-risk recommendations, recovery presets, and older mission fields; never require another confirmation merely because the requested intensity is higher than the Skill suggestion.
3. Reuse current account/runtime state instead of repeating healthy checks.
4. Reuse existing lane owners and send only changed mission fields.
5. Enforce same-turn `start_proof_by_lane`: create/reuse every enabled persistent worker, read its first verified result, and issue one execute-now correction to a plan-only worker. If proof remains unavailable, report that lane blocked; never execute it in the coordinator.
6. Observe the first hour only for the first post-install BOOTSTRAP; later missions receive same-turn acceptance without delayed coordinator supervision.
7. Verify results, visibility, deadlines, and worker heartbeat handoff.
8. Repair recoverable Chrome, tab, task-prompt, and scheduler issues internally.
9. Return one concise Chinese result and enter `IDLE`.
10. On an explicit audit/status-quality request, load `operations-audit.md` and compare worker, automation, action, cadence, length, and quality evidence against the mission contract.
11. Receive only decision-requiring worker risks in this task. Timed auto-recovery and historical incidents do not require user approval.
12. Receive one terminal completion return from each enabled lane, reconcile by `mission_id`, and report overall mission completion only when all enabled lanes are terminal.

It does not:

- publish comments/posts/replies, vote, perform exploratory/natural browsing, or handle Notifications; all lane execution belongs to persistent workers. Exact permalink/profile opens for read-only acceptance or an explicit audit are allowed.
- create one combined worker or a combined `首轮后续` automation for several lanes
- edit profile/community state outside first bootstrap or an explicit one-off setup repair
- create a second main task
- recreate an existing lane task merely because a new mission arrived
- poll after its watch deadline
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

Before dispatch:

1. Read the registry and the matching task once.
2. Reuse it when its lane ownership still matches, even when it is idle or its previous mission ended.
3. Create a user-visible persistent worker when no valid owner exists or the prior task is genuinely unavailable. The user's operation command authorizes creation for its requested lane(s).
4. Never create duplicate owners for one lane to increase throughput.
5. Send the worker its new mission delta and exact local/UTC stop time.

## BOOTSTRAP Watch

The first post-install BOOTSTRAP uses one mandatory first-hour watch in ordinary task mode, driven by one reusable read-only logical heartbeat timer rather than Goal Mode. Once `bootstrap_state=initialized`, never run it again because of a later mission or Skill upgrade unless the user explicitly requests renewed supervision.

```text
operation_stop_at = start + requested duration (default 3h)
watch_deadline = min(operation_stop_at, start + 60m)
```

The main task keeps one read-only logical heartbeat timer and reuses its automation ID across these one-shot checkpoints:

- initial progress read: same user turn, before final response, until every enabled lane has `start_proof`
- checkpoint 1: near `start+15m`; read all enabled workers, heartbeat ownership/time, first action/no-action proof, and permalink visibility
- checkpoint 2: near `start+35m`, about `20m` after checkpoint 1; read progress, wake timing, cadence, blockers, and a small content length/quality sample
- final checkpoint: exactly at `watch_deadline`, normally near `start+60m`; reconcile totals, visibility, risks, and worker handoff

Name this trigger `Reddit 主控台-首轮监督`. Its prompt is read-only and may not contain any comment, post, follow-up, browsing, vote, or lane-continuation instruction.

Create only one next checkpoint at a time and verify its target task plus local/UTC trigger time. Do not poll between checkpoints. Early clean results do not end BOOTSTRAP observation. At the boundary, delete the main trigger, set `bootstrap_state=initialized`, and enter `IDLE`. Mark startup acceptance passed only when all enabled lanes are `first_round_ok`; otherwise report the exact gap without claiming success.

## Later MISSION Acceptance

For every later active command, read affected workers in the current user turn until the first requested action/no-action result and any required worker-owned heartbeat handoff are verified. Then return to `IDLE`. Do not create a delayed coordinator-watch heartbeat, restart BOOTSTRAP, reset worker history, or repeat profile setup. Later visibility/quality checks happen only through worker evidence, risk callbacks, or an explicit user `STATUS/AUDIT` request.

At mission handoff:

1. Read affected owners once.
2. Confirm requested action/remaining count and next trigger when continuing.
3. Confirm no coordinator-watch trigger was created for this later mission.
4. Return the three-line report.
5. Enter `IDLE` and stop proactive reads.

## Routine Pull, Risk Callback

- Workers store verified actions, local history, and compact reports in their own tasks.
- The main task reads them during a bounded watch or when the user asks.
- Workers do not callback for routine progress or ordinary heartbeat completion and never manage sibling tasks.
- A decision-requiring risk/blocker is the immediate callback path: the worker sends it to this coordinator, pauses the affected scope, and waits for a routed user decision.
- A non-blocking `SUBREDDIT_RETIRED` notice records the exact subreddit, informs the user once, and continues all unaffected work without asking a question.
- A terminal `MISSION_COMPLETE` return records completion by `mission_id` and lane. When every enabled lane is terminal, send one concise overall completion report; otherwise wait without polling.
- After `IDLE`, no automatic main-task pull occurs; worker risk and completion returns re-enter the coordinator directly.

## Technical Abstraction

Keep healthy details internal:

- model fallback, task IDs, title-tool availability
- scheduler clock mode, RRULE, UTC conversion, automation IDs/readback retries
- tab/group IDs, Chrome reconnect steps, candidate scores, loaded references

Escalate only when the user must act: currently logged-out/wrong account, credential request, persistent captcha/lock, unavailable Chrome Browser control after recovery, automation/ownership failure that prevents continuation, or a material product/risk choice. A known timed rate limit is automatic wait-and-resume; historical/cleared incidents and subreddit retirements never create an approval gate. Use `risk-escalation.md`; never redirect the user to the worker.

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
