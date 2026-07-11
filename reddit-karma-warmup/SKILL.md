---
name: reddit-karma-warmup
description: >-
  Run authorized Reddit community operations through the user's logged-in Chrome session. Use for zero-account bootstrap, proactive comments, main posts, notification/reply follow-up, natural browsing with occasional genuine votes, duration/intensity/style-based operations, later missions dispatched through the stable Loci Reddit operations task, or packaging and inspecting this workflow.
---

# Reddit Karma Warmup

Use one stable user-facing task named `Reddit 主控台` and four internal operation tasks: `Reddit 评论台`, `Reddit 发帖台`, `Reddit 跟进台`, and `Reddit 浏览台`. The main task is the only user-facing command surface; lane tasks are internal execution details.

## Select Runtime Context

Choose exactly one context before loading detailed references:

| Context | Trigger | Behavior |
|-|-|-|
| `INSTALL` | Install, upgrade, inspect, package, or explain | Load `references/runtime-and-setup.md`; do not mutate Reddit. |
| `BOOTSTRAP` | First `开始` after install, or `bootstrap_state` is not initialized and the visible account is blank/new/no-clean-history | Load `references/default-operations-sop.md`, `references/operation-style-profiles.md`, `references/thread-supervision-runtime.md`, `references/coordinator-playbook.md`, `references/risk-escalation.md`, `references/new-account-bootstrap.md`, `references/startup-health-check.md`, `references/orchestration-core.md`, and `references/scheduler-and-heartbeats.md`. |
| `MISSION` | The user gives a later active operation command in `Reddit 主控台` | Load `references/default-operations-sop.md`, `references/operation-style-profiles.md`, `references/thread-supervision-runtime.md`, `references/coordinator-playbook.md`, `references/risk-escalation.md`, `references/orchestration-core.md`, and only the affected lane playbook(s). |
| `STATUS` | Status, progress, risk, next run, pause, resume, or stop | Load `references/thread-supervision-runtime.md` and `references/coordinator-playbook.md`; read only relevant lane tasks unless a requested control change is needed. |
| `AUDIT` | The user asks whether workers, automations, execution, cadence, published content, length, or quality are following the plan | Load `references/thread-supervision-runtime.md`, `references/coordinator-playbook.md`, and `references/operations-audit.md`; inspect the relevant workers and their automations read-only by default. |
| `WORKER` | The task handoff explicitly says it owns one lane | Load `references/orchestration-core.md`, `references/operation-style-profiles.md`, `references/risk-escalation.md`, the assigned lane playbook, and `references/scheduler-and-heartbeats.md` only when continuation is required. Never become a coordinator. |

Lane references:

- comments/posts: `references/proactive-playbook.md`, `references/outbound-copy-gate.md`, and `references/publish-consistency.md`
- notifications/replies: `references/followup-playbook.md`; add copy/publish gates only when replying
- bootstrap-only profile/join/flair setup: `references/community-presence-playbook.md`
- natural browsing with optional genuine upvote/downvote: `references/browse-vote-playbook.md`
- operation direction and voice: `references/operation-style-profiles.md`
- persistent task creation/reuse/read/send supervision: `references/thread-supervision-runtime.md`
- on-demand worker, automation, cadence, and content audit: `references/operations-audit.md`
- worker-to-main risk escalation and user decision routing: `references/risk-escalation.md`
- no user target pool: `references/loci-subreddit-pool-v1.md`
- 8-12 hour run: `references/twelve-hour-ops-template.md`
- model assignment: `references/model-runtime.md`
- Chrome control/page/network error self-diagnosis: load `references/chrome-network-recovery.md` only after a browser control, navigation, or loading failure

Do not load every reference. The subreddit pool is routing data, not a workflow.

## End-To-End Operating Flow

### Phase 0: Install And Preflight

1. Install or atomically upgrade the Skill; do not mutate Reddit in `INSTALL`.
2. Confirm Chrome Browser control, the intended logged-in Reddit account, persistent task tools, heartbeat capability, and actual local/UTC time.
3. If one dependency is missing, keep installation complete and give one concrete repair action. On `继续`, resume only the missing preflight.
4. When healthy but no operation was requested, explain the available lanes/styles once and wait. Preserve `bootstrap_state` across upgrades.

### Phase 1: First Operational Start

1. `开始` means `3 hours`, `standard` intensity, and `mixed` style unless the user overrides them. It explicitly authorizes creation/reuse of the required persistent lane tasks.
2. Rename the current task `Reddit 主控台`, resolve its exact ID, and pin it. Confirm account/tier/history and convert the request into lane, count/duration, style, pool, language, and `operation_stop_at`.
3. Broad `开始/运营` requires four distinct persistent owners: `Reddit 评论台`, `Reddit 发帖台`, `Reddit 跟进台`, and `Reddit 浏览台`. A named lane command requires only that owner. Keep every worker unpinned.
4. Capture and verify every `worker_thread_id`. Do not replace a lane with a subagent, combined worker, or coordinator execution.

### Phase 2: Execute Now And Accept

1. Send each enabled owner its mission with `first_due=now`; every worker opens/reclaims its own Chrome tab and performs the first micro-slot immediately.
2. Every worker returns `start_proof`: a verified action/permalink, or exact browser surfaces/candidates plus the valid gate producing no action/blocker.
3. The coordinator reads every enabled worker in the same user turn. A plan-only worker receives one execute-now correction; if proof still fails, mark only that lane `startup_blocked`.
4. Planning, task creation, heartbeat creation, or `已启动` is not proof. No worker creates its logical operation timer before current-slot proof.
5. Report the actual first result in Chinese, then end the turn; never keep an active turn waiting for the next delayed slot.

### Phase 3: Independent Worker Continuation

1. Each worker owns one lane, dedicated tab/history, and one logical heartbeat timer explicitly bound to its own task ID for the mission lifetime.
2. On every heartbeat wake, the worker restores state, executes/verifies the current slot, records `slot_proof`, and only then updates the same timer to the next due time when work remains.
3. Workers keep routine progress locally. They never coordinate siblings or ask the user directly.
4. Decision-requiring risks use `risk-escalation.md`: pause the affected scope, return evidence to `Reddit 主控台`, and await the routed user decision.
5. When the lane's whole mission reaches its target, deadline, user stop, or terminal no-more-work condition, send exactly one `MISSION_COMPLETE` return to `Reddit 主控台`. This is mission-level completion, never a per-heartbeat callback.

### Phase 4: One-Time First-Hour Supervision

1. Run this phase only for the first post-install `BOOTSTRAP` while `bootstrap_state` is not initialized.
2. The coordinator owns one read-only logical heartbeat timer, reuses its automation ID, and checks workers near `start+15m`, `start+35m`, and the `start+60m` boundary.
3. Check worker status, action/no-action evidence, permalink visibility, heartbeat binding/time, cadence, risks, and a small length/quality sample. The coordinator never performs lane actions.
4. At the final boundary, reconcile the first hour, delete the coordinator heartbeat, set `bootstrap_state=initialized`, and enter `IDLE`.
5. Later missions and Skill upgrades never restart this phase unless the user explicitly asks for renewed supervision.

### Phase 5: Later Missions

1. The user continues speaking only in `Reddit 主控台`; classify the command as `MISSION` and reuse the relevant owners/history.
2. Send only the changed mission fields. The affected worker executes its first due slot now, and the coordinator performs same-turn acceptance exactly as Phase 2.
3. Worker-owned heartbeats continue remaining work. The coordinator returns to `IDLE` and does not create another first-hour watch.

### Phase 6: Status, Audit, Control, And Risk

- `STATUS`: read relevant workers once; report progress, risk, and next run. Do not create work.
- `AUDIT`: use `operations-audit.md` to inspect ownership, automation timing, execution, visibility, cadence, length, and quality.
- pause/resume/stop: route the control to affected owners and verify their own heartbeat change.
- risk callback: explain evidence, impact, current pause, and recommendation in `Reddit 主控台`; ask the user to continue, adjust, or stop, then route the decision back to the owner.
- In `IDLE`, never poll. Worker risk callbacks, mission-completion returns, or a new user command are the only re-entry paths after the one-time Bootstrap watch.

## Single-Objective Task Contract

Every persistent task has one outcome. Discovery, scoring, drafting, rules, pacing, verification, reporting, and heartbeat handling are supporting steps or constraints, not additional objectives.

| Task | Single objective | Success evidence | Explicitly outside the objective |
|-|-|-|-|
| `Reddit 主控台` | Advance or stop the authorized Reddit operation through the correct workers and centralize every user decision. | Correct routing, same-turn acceptance, risk consolidation, and accurate status/audit. | Performing Reddit lane actions. |
| `Reddit 评论台` | Publish only qualified new comments on existing Reddit discussions. | Verified comment permalink, or browser-backed no-action evidence after valid candidate gates. | Main posts, Notifications/replies, browsing quotas, sibling coordination. |
| `Reddit 发帖台` | Publish only eligible native main posts after full live preflight. | Verified post permalink, or exact candidate/preflight rejection evidence. | Proactive comments, Notifications, general browsing/voting. |
| `Reddit 跟进台` | Process actionable responses and account follow-up surfaces. | Verified reply/action, or a concrete Notifications plus own-activity sweep with no actionable item. | Unrelated discovery, proactive posts/comments, natural browsing. |
| `Reddit 浏览台` | Complete qualified reading and independently gated vote decisions. | Qualified-read ledger plus verified vote/no-vote decisions for the slot. | Writing comments/posts/replies, profile/community changes. |

One worker may process several items only when they all serve its single objective. A request spanning objectives is split across workers. An off-lane instruction is returned to `Reddit 主控台`; the worker never absorbs it.

## Hard Gates

- `Reddit 主控台` is the only user-facing command/decision surface and never executes comments, posts, replies, browsing, or votes.
- Real lane owners are persistent tasks with exact IDs. Subagents may assist bounded read-only analysis but never own Chrome mutations, a lane, heartbeat, or risk decision.
- An operation command executes in the current turn. The first heartbeat may continue the second slot, never defer the first.
- A no-action result needs concrete browser-backed evidence and a valid Skill gate; otherwise the lane is not started.
- Missing task create/read/send capability blocks only the affected lane; the coordinator never silently performs it sequentially.
- Delays over `5-10 min` use the lane's verified logical heartbeat timer. Reuse/update the same automation ID across hours; do not use Goal Mode, a terminal sleep, or a new timer per round.
- Naming uses `<platform> <responsibility>台`. Pin only `Reddit 主控台`; keep active/idle workers unpinned and unarchived. Archive completed probes, diagnostics, and retired workers only after their heartbeat/tab state is released.

## Zero-Account Defaults

- Main model and every lane worker: `gpt-5.6-luna/high`.
- Default operation: `3 hours` at `standard` intensity and `mixed` style, automatically decomposed across comments, posts, follow-up, and natural browsing.
- Profile/community setup is a one-time bootstrap step only when the visible account is incomplete; it is not a recurring operation lane.
- Comment/post volumes come from the intensity envelope and account tier. After each verified comment, use a local `60-120 sec` pause; discovery, reading, drafting, and checks are additional.
- Follow-up: inspect Notifications and recent own activity; reply only to actionable items.
- Natural browsing: use the selected intensity's read budget and vote target. Standard defaults to `20-30` qualified reads and a target of `2` combined genuine votes per slot, with up to `4` when additional items independently pass. After a slot completes, the next browsing slot defaults to a freshly selected `20-40 min` delay. An explicit user read, vote, or interval setting, including `0` votes, overrides only that field; a below-target slot is valid when the read/time budget is exhausted without enough passing items.
- The post lane is enabled during broad operation, but publishing still requires a fully eligible native candidate and live preflight; a verified no-post result is valid.
- During the one-time post-install BOOTSTRAP only, the main task checks the first outward permalink immediately, near `+15 min`, and at the first-hour boundary while workers continue independently.

## Shared Invariants

- Real account actions require the already logged-in Chrome Browser control. Never enter credentials and never substitute Computer Use, the in-app Browser, Playwright, or ordinary Web Search.
- Each worker owns a dedicated Reddit tab and optional Tab Group. Workers do not inspect, wait for, compare, or modify other workers' tabs, targets, actions, or automations.
- Each worker heartbeat is created/updated by that worker with explicit `targetThreadId=worker_thread_id` when supported, then read back for an exact target match. Names never prove ownership; a mismatch is repaired before the trigger remains active.
- The main task never owns an execution heartbeat. Its optional first-hour watch heartbeat is read-only, is named as supervision rather than continuation, and cannot contain Reddit lane actions.
- Each worker owns one logical heartbeat timer for its active mission and may mutate only that exact automation targeting its same task/lane. Reuse its automation ID until stop/completion.
- Routine progress is pull-based. Two callbacks are mandatory exceptions: a substantive risk/blocker returns immediately, and one terminal `MISSION_COMPLETE` returns when the lane's whole assigned mission ends. Neither is emitted after ordinary heartbeat slots.
- Main and worker deadlines use actual local time plus UTC. Read back the persisted next-run time when the runtime exposes it; absence of that field is not a blocker. Never schedule at or after `operation_stop_at` and never silently extend a deadline.
- Goal Mode is not an operations scheduler. Do not keep an active turn alive while waiting for a future slot: delays over `5-10 min` use the lane's verified logical heartbeat timer, and the current turn ends after reporting that handoff.
- A heartbeat is continuation-only. Never create it as the first operational outcome after a user command, and never use its future wakeup to defer the first requested Chrome micro-slot.
- Heartbeat capability and heartbeat timing observability are separate. Successful create/update with an automation ID/card proves capability; missing `next_run_at` or hidden display time means `created_unreadable`, not failure. Continue current Reddit work, never ask the user to repair an unexposed field, and validate timing when the heartbeat actually fires.
- The user's latest explicit duration, intensity, operation style/voice modifier, count, language, target community, and lane override defaults. Counts remain candidate- and rule-gated.
- Main posts require same-day rules, eligibility, flair, frequency, and moderation-state checks. Ordinary comments require target-context and obvious-risk checks.
- Every verified comment/reply appends its measured character count, word count, sentence form, and length tier. Before drafting the next one, consult the latest `10` comment/reply entries and choose a context-appropriate length instead of defaulting to a repeated two-sentence shape.
- Pool layers are gates: `B/B+` may enter action discovery when row rules fit; `A` is research-first; `A0/No-go` are read-only.
- Never invent identity, experience, expertise, metrics, product use, testing, or affiliation. Votes must follow a qualified read and a specific quality reason; never force a vote to satisfy cadence, coordinate votes, spam, harass, doxx, or bypass subreddit rules.
- For voting, a unique enabled control plus a successful one-time click is operational confirmation. Immediate selected state is stronger evidence; reload persistence is optional sampling. Hidden post-reload state alone never triggers a user confirmation, retry click, or lane pause. Preserve an explicit user confirmation that the account/browser vote path is stable until a concrete click/account/Reddit error disproves it.

## Recovery And User Abstraction

Automatically repair stale Chrome control, lane-tab recovery, missing first-round evidence, scheduler encoding/readback, and worker prompt drift. On Chrome control/navigation/loading failure, load `chrome-network-recovery.md`, classify the exact returned code and scope, infer an evidence-based `可能原因`, and run bounded recovery before declaring a blocker. Transient recovery stays within the three-line report; persistent failure returns the code, possible cause, attempts, and user repair through `Reddit 主控台`. Keep task IDs, model fallback, tab IDs, UTC math, automation IDs, retries, scores, and technical logs internal.

Ask the user only in `Reddit 主控台` when they must act: Reddit is logged out/wrong-account, credentials are required, captcha/rate limit/lock persists, Chrome Browser control remains unavailable, or a material product/risk choice cannot be inferred. Workers escalate these states and never ask the user directly.

## Compact Report

Every ordinary worker result, including every heartbeat wake, uses exactly three Chinese lines. Keep links and no-action reasons inside the first line. Decision-requiring risks use the separate risk callback schema.

```text
本轮完成：<动作、数量、r/subreddit 和 permalink；无动作则写明已检查什么及原因>
下一轮心跳：<YYYY-MM-DD HH:mm:ss 时区（UTC 时间）；结束则写“无，任务已结束”>
下轮计划：<下一轮准备完成的具体动作和目标数量；结束则写“无”>
```

The heartbeat time must come from the timer's intended/read-back schedule, not a vague interval or an invented value. Do not expose intermediate worker reports or technical implementation details unless the user asks.
