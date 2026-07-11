# Persistent Task Supervision Runtime

Canonical owner of persistent task identity, registry, create/reuse/send/read operations, and task presentation/lifecycle. It does not define lane execution, timer math, or coordinator policy.

Load only in the user-facing `Reddit 主控台` coordinator for `BOOTSTRAP`, `MISSION`, `STATUS`, or `AUDIT`. This is the bundled supervision subset for Reddit operations; no external `thread-supervisor` Skill is required.

## Required Capability Bundle

The host must expose equivalent operations for:

- list/search existing Codex tasks
- create a persistent user-visible task
- read a task's recent result
- send or amend a task instruction
- send a decision-requiring risk/blocker, non-blocking subreddit-retirement notice, or terminal mission-completion return from a worker back to the exact coordinator task
- rename a task when title control exists
- pin/unpin a task when presentation control exists
- archive a completed temporary or retired task after ownership is released
- view each relevant task-owned automation and its persisted binding/schedule/run evidence when the host exposes it

The user's `开始` or concrete operation command explicitly authorizes creation of the requested lane tasks. Do not create them during install/preflight and do not create unrelated tasks.

Persistent tasks are intentional: each lane needs durable history, an exact task ID, an owned logical operation timer, independent recovery, and a reliable risk-return path. A temporary subagent may assist a worker with bounded read-only analysis when available, but it cannot own Chrome mutations, a lane, an operation timer, or a user-risk decision.

## Registry

Maintain one owner per lane:

```text
lane | title | single_objective | worker_thread_id | status | mission_id | last_proof | operation_timer_id
comments | Reddit 评论台 | qualified new comments only
posts | Reddit 发帖台 | eligible native main posts only
follow-up | Reddit 跟进台 | actionable account follow-up only
browsing | Reddit 浏览台 | qualified reading and gated vote decisions only
```

Reuse an owner when its title/role still matches and it remains readable. Create a replacement only when no owner exists or the prior task is genuinely unavailable. Never create duplicate owners to increase throughput.

Every task handoff begins with this compact objective card; do not bury it below setup details:

```text
唯一目标：<one lane outcome>
本轮交付：<count/time/deadline>
明确不做：<other lane outcomes>
长期计时：复用 operation_timer_id；首轮立即执行
```

The card defines one outcome, not one action. A worker may search, score, draft, check rules, pace, verify, and report only as supporting steps toward that outcome.

## Dispatch

1. Resolve enabled lanes before creating anything. Broad `开始/运营` enables all four; a named lane enables only that lane.
2. List/reconcile the registry once.
3. Create every missing persistent task, capture the returned thread/task ID as `worker_thread_id`, and rename it immediately when title control exists.
4. Pin the verified `Reddit 主控台`; explicitly unpin every worker. Read/list the created tasks and verify four distinct IDs for broad operation, with each ID mapped to exactly one lane title. A title, plan, or heartbeat card without a persistent task ID is not a worker. If an enabled lane lacks its own readable ID, mark that lane `startup_blocked`; never let the coordinator absorb it.
5. Send each worker the `default-operations-sop.md` handoff contract: `role=WORKER`, lane, `single_objective`, `out_of_scope`, `worker_thread_id`, coordinator thread ID, account, mission, intensity, style, targets, stop time, first due=`now`, and its required references.
6. Require the worker to execute its first Chrome slot immediately and return `start_proof`; task creation or acknowledgement is not proof.
7. Read each enabled worker in the same coordinator turn. A plan-only worker receives one explicit amendment: execute the assigned lane now, verify it, then report proof.
8. If the amended worker still has no proof, mark only that lane `startup_blocked`. Never execute the lane in the coordinator and never merge it into another worker.

## Supervision

- Pull routine worker state from the coordinator only during the first post-install BOOTSTRAP checkpoints near `+15m`, `+35m`, and `+60m`. Later missions receive same-turn acceptance but no delayed pull unless the user requests `STATUS/AUDIT`. Do not require routine callbacks; require risk/blocker returns, non-blocking `SUBREDDIT_RETIRED` notices, and one terminal `MISSION_COMPLETE` return per assigned lane mission.
- Read only the latest result needed to classify `running`, `first_round_ok`, `blocked`, or `completed`.
- Send amendments only for the same lane's current mission. Queue unrelated future changes in coordinator state until the worker is idle.
- Every worker owns its dedicated Chrome tab, history, and one logical operation timer heartbeat explicitly targeting `worker_thread_id`. The worker creates it only after first proof, then updates/reuses the same automation ID until mission completion and verifies the stored target/time after every change.
- Only during the first post-install BOOTSTRAP, the coordinator may own the read-only `Reddit 主控台-首轮监督` heartbeat. It cannot execute Reddit actions or continue lane work, and later missions must not recreate it.
- If creation of the coordinator watch reports that its task already owns a heartbeat, inspect only that coordinator-targeted item. A prompt containing comment/post/follow-up/browsing execution proves a misbound lane heartbeat: do not treat the lane as handed off, deactivate/remove the wrong item, and instruct the actual lane worker to create its own explicitly bound replacement. Do not inspect unrelated correctly bound worker heartbeats.
- The coordinator never batch-creates lane heartbeats. It checks worker reports for `thread_binding_verified` or provisional `creator_thread_bound` and repairs only a reported mismatch.
- Different lane tasks sharing one Chrome profile/account remain independent; do not pause one merely because another is active.
- When the user explicitly requests an execution/quality audit, load `operations-audit.md`, read the relevant workers' latest evidence and owned automations, and compare them with the coordinator's mission contract. This is an on-demand pull, not continuous monitoring or a callback requirement.
- When a worker escalates a substantive blocker, the coordinator becomes the only user-facing decision surface. It may instruct affected owners to pause, but workers never contact the user or ask for confirmation in their own tasks.
- When a worker returns `MISSION_COMPLETE`, the coordinator marks only that lane terminal. It reports overall completion only after every lane enabled for the same `mission_id` has returned terminal state; a single lane's ordinary heartbeat completion is not overall completion.
- When a worker returns `SUBREDDIT_RETIRED`, record the subreddit in the shared retired set, notify the user once, and leave all workers/timers running. Never convert this event into a risk decision without separate account-level evidence.

## User Surface

The user continues speaking only in `Reddit 主控台`. Report lane titles and concrete blockers when useful, but keep task IDs, tool names, registry internals, and worker prompts hidden unless explicitly requested.

## Presentation And Lifecycle

- Pin: `Reddit 主控台` only.
- Keep unpinned/unarchived: `Reddit 评论台`, `Reddit 发帖台`, `Reddit 跟进台`, and `Reddit 浏览台`, including while idle between missions.
- Archive after completion: installer probes, timezone diagnostics, smoke tests, and other temporary tasks that own no active heartbeat/tab.
- Retired worker: stop/remove its heartbeat, release its tab, remove it from the registry, unpin it, then archive it.
- Never archive a task merely to hide a blocker or while an automation still targets it.
- Missing pin/archive presentation controls do not block Reddit operations; record the unavailable UI action internally.

## Exclusions

- no invisible subagents in place of persistent tasks
- no routine or per-heartbeat callback requirement; only risk/blocker, non-blocking subreddit retirement, and terminal mission completion are event returns
- no Goal Mode
- no combined worker or combined execution heartbeat
- no coordinator fallback that publishes, replies, performs exploratory/natural browsing, or votes; exact read-only permalink/profile verification during acceptance or audit is allowed
- no model rules from an external supervisor Skill; use `model-runtime.md`
