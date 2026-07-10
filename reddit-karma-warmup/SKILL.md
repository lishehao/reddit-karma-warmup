---
name: reddit-karma-warmup
description: >-
  Run authorized Reddit community operations through the user's logged-in Chrome session. Use for zero-account bootstrap, proactive comments or posts, notification/reply follow-up, profile/community presence, read-only browsing with occasional genuine votes, multi-hour scheduling, later missions dispatched through the stable Loci Reddit operations task, or packaging and inspecting this workflow.
---

# Reddit Karma Warmup

Use one stable user-facing task named `Loci Reddit运营` and five internal lane tasks: `主动评论`, `主动发帖`, `消息跟进`, `主页维护`, and `内容浏览`. The main task accepts commands and coordinates; lane tasks execute Reddit actions.

## Select Runtime Context

Choose exactly one context before loading detailed references:

| Context | Trigger | Behavior |
|-|-|-|
| `INSTALL` | Install, upgrade, inspect, package, or explain | Load `references/runtime-and-setup.md`; do not mutate Reddit. |
| `BOOTSTRAP` | First `开始` after install, or `bootstrap_state` is not initialized and the visible account is blank/new/no-clean-history | Load `references/default-operations-sop.md`, `references/coordinator-playbook.md`, `references/new-account-bootstrap.md`, `references/startup-health-check.md`, `references/orchestration-core.md`, and `references/scheduler-and-heartbeats.md`. |
| `MISSION` | The user gives a later active operation command in `Loci Reddit运营` | Load `references/default-operations-sop.md`, `references/coordinator-playbook.md`, `references/orchestration-core.md`, and only the affected lane playbook(s). |
| `STATUS` | Status, progress, risk, next run, pause, resume, or stop | Load `references/coordinator-playbook.md`; read only relevant lane tasks unless a requested control change is needed. |
| `WORKER` | The task handoff explicitly says it owns one lane | Load `references/orchestration-core.md`, the assigned lane playbook, and `references/scheduler-and-heartbeats.md` only when continuation is required. Never become a coordinator. |

Lane references:

- comments/posts: `references/proactive-playbook.md`, `references/outbound-copy-gate.md`, and `references/publish-consistency.md`
- notifications/replies: `references/followup-playbook.md`; add copy/publish gates only when replying
- profile/join/flair: `references/community-presence-playbook.md`
- browsing/occasional votes: `references/browse-vote-playbook.md`
- no user target pool: `references/loci-subreddit-pool-v1.md`
- 8-12 hour run: `references/twelve-hour-ops-template.md`
- model assignment: `references/model-runtime.md`

Do not load every reference. The subreddit pool is routing data, not a workflow.

## Entrypoint Contract

- Healthy install without an operation request: return the multiline guided prompt from `runtime-and-setup.md` and wait once.
- If Chrome control or Reddit login is missing on a first-time setup, keep installation complete, return one novice repair action from `runtime-and-setup.md`, and resume preflight when the user replies `继续`. Never create an account, enter credentials, or start workers before the logged-in account is confirmed.
- User replies `开始` with no other scope: enter `BOOTSTRAP`, default to `3 hours`, and start the first actions immediately.
- A later user command in `Loci Reddit运营`: enter `MISSION`; reuse existing lane tasks and never rerun installation or bootstrap after `bootstrap_state=initialized`, even while the account remains `K0 fresh_bootstrap`.
- A user asks what is possible: list comments, posts, follow-up, profile/community presence, and browsing with optional genuine votes; do not mutate until they issue an operation command.
- A lane worker receives a resume heartbeat: restore its own history and unfinished target; do not create a main task or restart the session.

The main task remains the user's only operational entrypoint. A user command such as `评论 20 条` routes to `主动评论`; it does not rename the main task or make the main task publish.

## Start-Now Gate

An operation command means execute now, not plan now and act on the next heartbeat. In the same user turn that receives `开始`, a duration, a count, or a concrete operation:

1. Open/reclaim the relevant Chrome lane tab and perform the first requested micro-slot.
2. Produce `start_proof`: at least one verified requested action, or a verified browser sweep with concrete no-action/blocker evidence.
3. Only after `start_proof`, create the next heartbeat when more work remains.
4. Only after action verification and heartbeat handoff may the turn send its final report.

Reading references, inspecting tasks, planning, dispatching a worker, creating a heartbeat, or saying `已启动` is not `start_proof`. A no-action result must name the surfaces/candidates actually checked and the concrete gate that rejected them; “still preparing” is not valid. Commentary may say work is starting, but never send a final `已启动` acknowledgement before proof.

When an authorized lane worker can execute and be read back in the current turn, delegate and wait for its first proof. If worker dispatch is unavailable, not authorized, delayed, or returns only a plan, the current task executes the first micro-slot sequentially. Background ownership may take over subsequent slots; it must never delay the user's first visible action.

## Canonical Main Flow

1. Classify the request as `BOOTSTRAP`, `MISSION`, or `STATUS`.
2. Restore the known Chrome account, worker registry, account tier, history, scheduler clock mode, and active operations. Reconnect recoverable Chrome state automatically.
3. Convert the request into a contract: lane(s), target/count, duration, pool, language, `operation_stop_at`, and watch deadline.
4. Reuse each matching lane task when authorized and immediately controllable; create/name one only when allowed and no valid owner exists.
5. Send each owner its delta: objective, remaining count, pool, stop time, first due slot, and model `gpt-5.6-luna/high`.
6. Pass the `Start-Now Gate` in this same turn. Read the worker's verified first result; if it cannot produce proof now, execute the first micro-slot sequentially in the current task. Never enter Goal Mode or call `create_goal`.
7. Verify the first result. Only now may a worker/current task create a one-shot heartbeat for delayed continuation.
8. For `BOOTSTRAP`, keep the main task's read-only watch through one-shot heartbeats for the first hour. For an ongoing `MISSION`, watch for at most the first hour; a verified one-shot mission with no continuation may close earlier.
9. Return the compact Chinese report with actual first-round evidence and heartbeat handoff, then end the current turn. A runtime that omits persisted next-run fields lowers timing confidence but does not invalidate a successfully created heartbeat.
10. In `IDLE`, do not poll. A later user command begins a new `MISSION` from current state.

## Zero-Account Defaults

- Main model: `gpt-5.6-sol/xhigh`. Every lane worker: `gpt-5.6-luna/high`.
- Default duration: `3 hours`; comment planning target: `10/hour`, therefore `30` across the default run when enough candidates pass; daily planning target remains `60`.
- First hour: target `10` passing comments across at least `3` lower-restriction communities. After each verified comment, use a local `60-120 sec` pause; discovery, reading, drafting, and checks are additional.
- Presence: truthful minimum profile setup plus `1-3` high-fit joins when due.
- Follow-up: inspect Notifications and recent own activity; reply only to actionable items.
- Browsing: read `8-12` qualified items per slot across eligible communities and cast at most one combined genuine vote when the dedicated gate passes; a zero-vote slot is valid.
- Posts: off by default during bootstrap unless the user requests them or a fully eligible native candidate passes live preflight.
- The main task checks the first outward permalink immediately, again after `15-30 min`, and at the first-hour boundary while workers continue independently.

## Shared Invariants

- Real account actions require the already logged-in Chrome Browser control. Never enter credentials and never substitute Computer Use, the in-app Browser, Playwright, or ordinary Web Search.
- Each worker owns a dedicated Reddit tab and optional Tab Group. Workers do not inspect, wait for, compare, or modify other workers' tabs, targets, actions, or automations.
- Each worker owns at most one next one-shot heartbeat for its lane and may mutate only an automation targeting that same task/lane.
- Main and worker deadlines use actual local time plus UTC. Read back the persisted next-run time when the runtime exposes it; absence of that field is not a blocker. Never schedule at or after `operation_stop_at` and never silently extend a deadline.
- Goal Mode is not an operations scheduler. Do not keep an active turn alive while waiting for a future slot: delays over `5-10 min` use one verified one-shot heartbeat, and the current turn ends after reporting that handoff.
- A heartbeat is continuation-only. Never create it as the first operational outcome after a user command, and never use its future wakeup to defer the first requested Chrome micro-slot.
- Heartbeat capability and heartbeat timing observability are separate. Successful create/update with an automation ID/card proves capability; missing `next_run_at` or hidden display time means `created_unreadable`, not failure. Continue current Reddit work, never ask the user to repair an unexposed field, and validate timing when the heartbeat actually fires.
- The user's latest explicit duration, count, language, target community, and lane override defaults. Counts remain candidate- and rule-gated.
- Main posts require same-day rules, eligibility, flair, frequency, and moderation-state checks. Ordinary comments require target-context and obvious-risk checks.
- Every verified comment/reply appends its measured character count, word count, sentence form, and length tier. Before drafting the next one, consult the latest `10` comment/reply entries and choose a context-appropriate length instead of defaulting to a repeated two-sentence shape.
- Pool layers are gates: `B/B+` may enter action discovery when row rules fit; `A` is research-first; `A0/No-go` are read-only.
- Never invent identity, experience, expertise, metrics, product use, testing, or affiliation. Votes must follow a qualified read and a specific quality reason; never force a vote to satisfy cadence, coordinate votes, spam, harass, doxx, or bypass subreddit rules.

## Recovery And User Abstraction

Automatically repair stale Chrome control, lane-tab recovery, missing first-round evidence, scheduler encoding/readback, and worker prompt drift. Keep task IDs, model fallback, tab IDs, UTC math, automation IDs, retries, scores, and technical logs internal.

Ask the user only when they must act: Reddit is logged out/wrong-account, credentials are required, captcha/rate limit/lock persists, Chrome Browser control remains unavailable, or a material product/risk choice cannot be inferred.

## Compact Report

User-facing reports are Chinese and use exactly four fields:

```text
本轮完成：做了什么；实际发布/处理了多少项。
发布/处理：r/subreddit + 动作类型 + permalink；没有发布时写“未发布：原因”。
下一轮：本地日期、时间、时区，以及准备做什么；结束时写“已结束，不再调度”。
风险：无；或只写当前具体风险及影响。
```

Do not expose intermediate worker reports or technical implementation details unless the user asks.
