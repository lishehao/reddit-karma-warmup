# Persistent Task Supervision Runtime

Load only in the user-facing `Loci Reddit运营` coordinator for `BOOTSTRAP`, `MISSION`, `STATUS`, or `AUDIT`. This is the bundled supervision subset for Reddit operations; no external `thread-supervisor` Skill is required.

## Required Capability Bundle

The host must expose equivalent operations for:

- list/search existing Codex tasks
- create a persistent user-visible task
- read a task's recent result
- send or amend a task instruction
- send a decision-requiring risk/blocker from a worker back to the exact coordinator task
- rename a task when title control exists
- view each relevant task-owned automation and its persisted binding/schedule/run evidence when the host exposes it

The user's `开始` or concrete operation command explicitly authorizes creation of the requested lane tasks. Do not create them during install/preflight and do not create unrelated tasks.

Persistent tasks are intentional: each lane needs durable history, an exact task ID, an owned heartbeat, independent recovery, and a reliable risk-return path. A temporary subagent may assist a worker with bounded read-only analysis when available, but it cannot own Chrome mutations, a lane, a continuation heartbeat, or a user-risk decision.

## Registry

Maintain one owner per lane:

```text
lane | title | worker_thread_id | status | mission_id | last_proof | owned_heartbeat
comments | 主动评论
posts | 主动发帖
follow-up | 消息跟进
browsing | 自然浏览
```

Reuse an owner when its title/role still matches and it remains readable. Create a replacement only when no owner exists or the prior task is genuinely unavailable. Never create duplicate owners to increase throughput.

## Dispatch

1. Resolve enabled lanes before creating anything. Broad `开始/运营` enables all four; a named lane enables only that lane.
2. List/reconcile the registry once.
3. Create every missing persistent task, capture the returned thread/task ID as `worker_thread_id`, and rename it immediately when title control exists.
4. Read/list the created tasks and verify four distinct IDs for broad operation, with each ID mapped to exactly one lane title. A title, plan, or heartbeat card without a persistent task ID is not a worker. If an enabled lane lacks its own readable ID, mark that lane `startup_blocked`; never let the coordinator absorb it.
5. Send each worker the `default-operations-sop.md` handoff contract: `role=WORKER`, lane, `worker_thread_id`, coordinator thread ID, account, mission, intensity, style, targets, stop time, first due=`now`, and its required references.
6. Require the worker to execute its first Chrome slot immediately and return `start_proof`; task creation or acknowledgement is not proof.
7. Read each enabled worker in the same coordinator turn. A plan-only worker receives one explicit amendment: execute the assigned lane now, verify it, then report proof.
8. If the amended worker still has no proof, mark only that lane `startup_blocked`. Never execute the lane in the coordinator and never merge it into another worker.

## Supervision

- Pull routine worker state from the coordinator during its bounded first-hour watch. Do not require routine callbacks; require structured risk/blocker callbacks under `risk-escalation.md`.
- Read only the latest result needed to classify `running`, `first_round_ok`, `blocked`, or `completed`.
- Send amendments only for the same lane's current mission. Queue unrelated future changes in coordinator state until the worker is idle.
- Every worker owns its dedicated Chrome tab, history, and one continuation heartbeat explicitly targeting `worker_thread_id`. The worker creates/updates that heartbeat inside its own task and verifies the stored target after every change.
- The coordinator may own only the read-only `Loci Reddit运营-首轮监督` heartbeat. It cannot execute Reddit actions or continue lane work.
- If creation of the coordinator watch reports that its task already owns a heartbeat, inspect only that coordinator-targeted item. A prompt containing comment/post/follow-up/browsing execution proves a misbound lane heartbeat: do not treat the lane as handed off, deactivate/remove the wrong item, and instruct the actual lane worker to create its own explicitly bound replacement. Do not inspect unrelated correctly bound worker heartbeats.
- The coordinator never batch-creates lane heartbeats. It checks worker reports for `thread_binding_verified` or provisional `creator_thread_bound` and repairs only a reported mismatch.
- Different lane tasks sharing one Chrome profile/account remain independent; do not pause one merely because another is active.
- When the user explicitly requests an execution/quality audit, load `operations-audit.md`, read the relevant workers' latest evidence and owned automations, and compare them with the coordinator's mission contract. This is an on-demand pull, not continuous monitoring or a callback requirement.
- When a worker escalates a substantive blocker, the coordinator becomes the only user-facing decision surface. It may instruct affected owners to pause, but workers never contact the user or ask for confirmation in their own tasks.

## User Surface

The user continues speaking only in `Loci Reddit运营`. Report lane titles and concrete blockers when useful, but keep task IDs, tool names, registry internals, and worker prompts hidden unless explicitly requested.

## Exclusions

- no invisible subagents in place of persistent tasks
- no routine callback requirement; decision-requiring risk/blocker return to the coordinator is mandatory
- no Goal Mode
- no combined worker or combined execution heartbeat
- no coordinator fallback that publishes, replies, performs exploratory/natural browsing, or votes; exact read-only permalink/profile verification during acceptance or audit is allowed
- no model rules from an external supervisor Skill; use `model-runtime.md`
