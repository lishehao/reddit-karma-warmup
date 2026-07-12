---
name: reddit-karma-warmup
description: >-
  Run authorized Reddit community operations through the user's logged-in Chrome session. Use for zero-account bootstrap, proactive comments, main posts, notification/reply follow-up, natural browsing with occasional genuine votes, duration/intensity/style-based operations, later missions dispatched through the stable Loci Reddit operations task, or packaging and inspecting this workflow.
---

# Reddit Karma Warmup

Use one stable user-facing persistent task named `Reddit 主控台` and up to five single-purpose persistent execution tasks: `Reddit 评论台`, `Reddit 发帖台`, `Reddit 跟进台`, `Reddit 浏览台`, and the conditionally enabled `Reddit 主页台`. These are user-visible durable task owners, not temporary subagents. The main task is the only user-facing command surface; execution tasks are internal operation details.

## Select Runtime Context

Choose exactly one context before loading detailed references:

| Context | Trigger | Behavior |
|-|-|-|
| `INSTALL` | Install, upgrade, inspect, package, or explain | Load `references/runtime-and-setup.md`; do not mutate Reddit. |
| `BOOTSTRAP` | First `开始` after install, or `bootstrap_state` is not initialized and the visible account is blank/new/no-clean-history | Load `references/default-operations-sop.md`, `references/operation-style-profiles.md`, `references/thread-supervision-runtime.md`, `references/coordinator-playbook.md`, `references/risk-escalation.md`, `references/new-account-bootstrap.md`, `references/startup-health-check.md`, `references/orchestration-core.md`, and `references/scheduler-and-heartbeats.md`. |
| `MISSION` | The user gives a later active operation command in `Reddit 主控台` | Load `references/default-operations-sop.md`, `references/operation-style-profiles.md`, `references/thread-supervision-runtime.md`, `references/coordinator-playbook.md`, `references/risk-escalation.md`, `references/orchestration-core.md`, and only the affected lane playbook(s). |
| `STATUS` | Status, progress, risk, next run, pause, resume, or stop | Load `references/thread-supervision-runtime.md` and `references/coordinator-playbook.md`; read only relevant lane tasks unless a requested control change is needed. |
| `AUDIT` | The user asks whether workers, automations, execution, cadence, published content, length, or quality are following the plan | Load `references/thread-supervision-runtime.md`, `references/coordinator-playbook.md`, and `references/operations-audit.md`; inspect the relevant workers and their automations read-only by default. |
| `WORKER` | The task handoff explicitly says it owns one lane | Load `references/orchestration-core.md`, `references/operation-style-profiles.md`, `references/risk-escalation.md`, and only the assigned lane playbook. Never become a coordinator or mutate scheduling. |

Lane references:

- comments: comment-only sections of `references/proactive-playbook.md`, plus `references/outbound-copy-gate.md` and `references/publish-consistency.md`
- posts: post-only sections of `references/proactive-playbook.md`, plus `references/outbound-copy-gate.md` and `references/publish-consistency.md`
- notifications/replies: `references/followup-playbook.md`; add copy/publish gates only when replying
- profile/join/flair setup: `references/community-presence-playbook.md`; only `Reddit 主页台` loads it
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

### Canonical Rule Ownership

- `SKILL.md`: context selection, end-to-end phases, hard gates, shared invariants, and the exact three-line report.
- `default-operations-sop.md`: user-request parsing, planning envelopes, mission delta, and worker handoff payload only.
- `coordinator-playbook.md`: `Reddit 主控台` lifecycle, same-turn acceptance, first-hour supervision, status/risk/completion aggregation.
- `thread-supervision-runtime.md`: persistent task registry, create/reuse/send/read, task identity, pin/archive lifecycle.
- `orchestration-core.md`: one worker's slot state machine, lane boundary, tab ownership, decision classes, execution and reconciliation.
- `scheduler-and-heartbeats.md`: timer math, binding, time verification, update/reuse, and stop behavior.
- lane playbooks: candidate/action rules for their lane only.

When two references appear to cover the same decision, the owner above wins. Supporting references link to the owner instead of restating its procedure.

## End-To-End Stage Contract

Every stage has one owner and one exit proof. Do not advance on a plan, acknowledgement, task title, or automation card alone.

| Stage | Owner | Input | Required work | Exit proof |
|-|-|-|-|-|
| `S0 INTAKE` | `Reddit 主控台` | latest user command | classify context; resolve lanes, duration/count, intensity, style, pool, language, stop time | normalized mission contract |
| `S1 PREFLIGHT` | `Reddit 主控台` | mission contract | confirm Chrome control, account, task/heartbeat capability, local time and UTC; determine whether presence baseline is required | runtime record plus `presence_required` |
| `S2 OWNER_READY` | `Reddit 主控台` | enabled lanes | resolve exact persistent owner candidates; if presence is required, dispatch only that lane first | candidate IDs resolved; presence owner live when required |
| `S3 PRESENCE_BASELINE` | `Reddit 主页台` when required | profile/membership baseline mission | inspect and perform only truthful profile, Join/subscribe, or Flair actions; otherwise return verified no-action | presence `start_proof` plus terminal/nonterminal state |
| `S4 FIRST_SLOT` | `Reddit 主控台` then enabled outward tasks | accepted presence baseline plus outward mission | main sends each outward handoff with `first_due=now`; each task executes one bounded slot independently in its own tab | one live task ID and `start_proof` per outward lane |
| `S5 ACCEPT_AND_SCHEDULE` | `Reddit 主控台` | all required first proofs | accept/reject proof; issue one execute-now correction to plan-only tasks; create recurring lane timers only for nonterminal future work plus one supervisor timer | accepted lane set, verified bindings, first Chinese report |
| `S6 RUN_SLOT` | each execution task on its own wake | current lane state and due slot | restore state, execute/verify one bounded slot, update local ledger | `slot_proof`, `not_due`, risk event, retirement event, or terminal event |
| `S7 SUPERVISE` | read-only main supervisor | mission contract, task reports, timers | reconcile actual wakes, proof, cadence, bindings and slot counts; repair orchestration once | updated mission ledger or surfaced orchestration failure |
| `S8 CLOSE` | lane task then `Reddit 主控台` | lane terminal state | task returns one `MISSION_COMPLETE`; main removes its timer; after all enabled lanes finish, stop supervisor and reconcile totals | final mission report and `IDLE` |

Execution order:

1. `INSTALL` stops after preflight. An operational command continues through `S0-S2` in the same user turn.
2. On a first-account bootstrap, complete and accept `S3` before starting outward operation tasks. If no presence change is required, record verified no-action and continue immediately.
3. After `S3`, dispatch every enabled outward task in parallel at `S4`; the current user turn does not end before every lane has proof or a concrete lane blocker.
4. `S5` hands delayed continuation to recurring Heartbeats. The main turn then ends; workers never keep it alive waiting for another slot.
5. Later missions reuse healthy owners and skip `S3` unless the user explicitly requests profile/community work. A presence-only mission runs `S3`, then acceptance/scheduling or close without entering `S4`; mixed presence plus outward work completes `S3` before `S4`.
6. `STATUS`, `AUDIT`, pause, resume, and stop are control paths owned by `Reddit 主控台`; they do not create lane work unless the user explicitly amends the mission.
7. Workers keep routine progress locally. Only decision-requiring risk/blocker, one `SUBREDDIT_RETIRED` event per subreddit, and one terminal `MISSION_COMPLETE` event return to the main task.

## Single-Objective Task Contract

Every persistent task has one outcome. Discovery, scoring, drafting, rules, pacing, verification, reporting, and heartbeat handling are supporting steps or constraints, not additional objectives.

| Task | Single objective | Success evidence | Explicitly outside the objective |
|-|-|-|-|
| `Reddit 主控台` | Advance or stop the authorized Reddit operation through the correct workers and centralize every user decision. | Correct routing, same-turn acceptance, risk consolidation, and accurate status/audit. | Performing Reddit lane actions. |
| `Reddit 评论台` | Publish only qualified new comments on existing Reddit discussions. | Verified comment permalink, or browser-backed no-action evidence after valid candidate gates. | Main posts, Notifications/replies, browsing quotas, sibling coordination. |
| `Reddit 发帖台` | Publish only eligible native main posts after full live preflight. | Verified post permalink, or exact candidate/preflight rejection evidence. | Proactive comments, Notifications, general browsing/voting. |
| `Reddit 跟进台` | Process actionable responses and account follow-up surfaces. | Verified reply/action, or a concrete Notifications plus own-activity sweep with no actionable item. | Unrelated discovery, proactive posts/comments, natural browsing. |
| `Reddit 浏览台` | Complete qualified reading and independently gated vote decisions. | Qualified-read ledger plus verified vote/no-vote decisions for the slot. | Writing comments/posts/replies, profile/community changes. |
| `Reddit 主页台` | Establish or repair truthful profile and community-presence state. | Verified profile/Join/Flair change, or exact inspected surfaces plus valid no-action evidence. | Comments, posts, replies, voting, sibling coordination, recurring general browsing. |

One worker may process several items only when they all serve its single objective. A request spanning objectives is split across workers. An off-lane instruction is returned to `Reddit 主控台`; the worker never absorbs it.

## Hard Gates

- `Reddit 主控台` is the only user-facing command/decision surface and never executes comments, posts, replies, browsing, or votes.
- Real lane owners are persistent tasks with exact IDs. Temporary subagents may assist bounded read-only analysis but never own Chrome mutations, an execution lane, Heartbeat, or risk decision.
- An operation command executes in the current turn. The first heartbeat may continue the second slot, never defer the first.
- A no-action result needs concrete browser-backed evidence and a valid Skill gate; otherwise the lane is not started.
- Missing task create/read/send capability blocks only the affected lane; the coordinator never silently performs it sequentially.
- Delays over `5-10 min` use the lane's verified logical heartbeat timer. Reuse/update the same automation ID across hours; do not use Goal Mode, a terminal sleep, or a new timer per round.
- Naming uses `<platform> <responsibility>台`. Pin only `Reddit 主控台`; keep active/idle workers unpinned and unarchived. Archive completed probes, diagnostics, and retired workers only after their heartbeat/tab state is released.

## Zero-Account Defaults

- Main model and every lane worker: `gpt-5.6-luna/high`.
- Default operation: `3 hours` at `standard` intensity and `mixed` style, automatically decomposed across comments, posts, follow-up, and natural browsing.
- Profile/community setup is owned by `Reddit 主页台` and enabled only when the visible account is incomplete or the user explicitly requests setup/repair. It normally completes in one bootstrap slot and receives no recurring timer after terminal proof.
- Comment/post volumes come from the intensity envelope and account tier. After each verified comment, use a local `60-120 sec` pause; discovery, reading, drafting, and checks are additional.
- Follow-up: inspect Notifications and recent own activity; reply only to actionable items.
- Natural browsing: use the selected intensity's read budget and vote target. Standard defaults to `20-30` qualified reads and a target of `2` combined genuine votes per slot, with up to `4` when additional items independently pass. After a slot completes, the next browsing slot defaults to a freshly selected `20-40 min` delay. An explicit user read, vote, or interval setting, including `0` votes, overrides only that field; a below-target slot is valid when the read/time budget is exhausted without enough passing items.
- The post lane is enabled during broad operation, but publishing still requires a fully eligible native candidate and live preflight; a verified no-post result is valid.
- During the first post-install hour, the recurring coordinator supervisor adds permalink and content-quality checks; afterward it continues lower-cost schedule/slot reconciliation until mission end.

## Shared Invariants

- Operational precedence is strict: system/developer safety and the user's authorized scope first; a currently visible platform-impossibility state second; the user's latest explicit operation command third; Skill defaults, account-tier suggestions, historical incidents, recovery advice, and older mission fields last. Within the authorized scope, the latest explicit duration, intensity, count, lane, language, target, and style replace conflicting older/default values and execute without a second confirmation.
- Historical or already-cleared removals, warnings, rate limits, locks, and login faults are ledger context only. They never create a recovery tier, cooldown, reduced envelope, approval prompt, or refusal for a new command. A current state may pause only the action it actually makes impossible; after it clears, automatically resume the unchanged latest user command unless the user has since amended or stopped it.
- Real account actions require the already logged-in Chrome Browser control. Never enter credentials and never substitute Computer Use, the in-app Browser, Playwright, or ordinary Web Search.
- Each worker owns a dedicated Reddit tab and optional Tab Group. Workers do not inspect, wait for, compare, or modify other workers' tabs, targets, actions, or automations.
- The coordinator creates, updates, verifies, and stops every mission Heartbeat. Lane Heartbeats explicitly target their worker tasks; the recurring coordinator supervisor Heartbeat explicitly targets `Reddit 主控台` and is read-only.
- Create a lane Heartbeat only when that lane has verified nonterminal future work after its first slot. A terminal one-slot presence mission receives no recurring timer.
- Workers never create, update, renew, replace, pause, or delete Heartbeats. They execute the bounded lane slot delivered by their recurring Heartbeat and report proof/state only.
- Routine progress is pull-based. Three event returns are exceptions: a substantive risk/blocker, one non-blocking `SUBREDDIT_RETIRED` notice per newly retired subreddit, and one terminal `MISSION_COMPLETE` when the lane mission ends. A retirement notice never pauses unrelated work or asks for a decision.
- Removal, filtering, lock, pending approval, parent deletion, or a subreddit ban is not account-wide evidence. Retire only the exact subreddit and continue at the same account tier/envelope. Only currently active, explicit account-level warning/rate-limit/captcha/lock/suspension/login evidence may pause the actions it prevents.
- Main and worker deadlines use actual local time plus UTC. Read back the persisted next-run time when the runtime exposes it; absence of that field is not a blocker. Never schedule at or after `operation_stop_at` and never silently extend a deadline.
- Goal Mode is not an operations scheduler. Do not keep an active turn alive while waiting for a future slot: delays over `5-10 min` use the lane's verified logical heartbeat timer, and the current turn ends after reporting that handoff.
- A heartbeat is continuation-only. Never create it as the first operational outcome after a user command, and never use its future wakeup to defer the first requested Chrome micro-slot.
- Heartbeat capability and heartbeat timing observability are separate. Successful create/update with an automation ID/card proves capability; missing `next_run_at` or hidden display time means `created_unreadable`, not failure. Continue current Reddit work, never ask the user to repair an unexposed field, and validate timing when the heartbeat actually fires.
- The user's latest explicit duration, intensity, operation style/voice modifier, count, language, target community, and lane override defaults, tier suggestions, recovery recommendations, and older mission fields. Do not convert a warning into a permission gate or ask the user to select a safer preset after they already gave a concrete command. Counts remain candidate-, live-rule-, and current-affordance-gated.
- Main posts require same-day rules, eligibility, flair, frequency, and moderation-state checks. Ordinary comments require target-context and obvious-risk checks.
- Every verified comment/reply appends its measured character count, word count, sentence form, and length tier. Before drafting the next one, consult the latest `10` comment/reply entries and choose a context-appropriate length instead of defaulting to a repeated two-sentence shape.
- Pool layers are gates: `B/B+` may enter action discovery when row rules fit; `A` is research-first; `A0/No-go` are read-only.
- Never invent identity, experience, expertise, metrics, product use, testing, or affiliation. Votes must follow a qualified read and a specific quality reason; never force a vote to satisfy cadence, coordinate votes, spam, harass, doxx, or bypass subreddit rules.
- For voting, one unique visible/enabled control plus a one-time click call that returns without exception is final `vote_accepted` evidence. Count it immediately. Never inspect selected state, score change, reload/reopen persistence, profile history, or another surface; never ask the user to confirm and never click again because state is hidden or ambiguous.

## Recovery And User Abstraction

Automatically repair stale Chrome control, lane-tab recovery, missing first-round evidence, scheduler encoding/readback, and worker prompt drift. On Chrome control/navigation/loading failure, load `chrome-network-recovery.md`, classify the exact returned code and scope, infer an evidence-based `可能原因`, and run bounded recovery before declaring a blocker. Transient recovery stays within the three-line report; persistent failure returns the code, possible cause, attempts, and user repair through `Reddit 主控台`. Keep task IDs, model fallback, tab IDs, UTC math, automation IDs, retries, scores, and technical logs internal.

Ask the user only in `Reddit 主控台` when they must perform an external repair: Reddit is currently logged out/wrong-account, credentials are required, captcha/lock persists, Chrome Browser control remains unavailable, or a material product/risk choice cannot be inferred. A visible timed rate limit is handled automatically: preserve the original mission, wait until the displayed expiry, re-probe once, and resume without asking for a recovery preset. Workers escalate user-repair states and never ask the user directly.

## Compact Report

Every ordinary worker result, including every heartbeat wake, uses exactly three Chinese lines. Keep links and no-action reasons inside the first line. Decision-requiring risks use the separate risk callback schema.

```text
本轮完成：<动作、数量、r/subreddit 和 permalink；无动作则写明已检查什么及原因>
下一轮心跳：<YYYY-MM-DD HH:mm:ss 时区（UTC 时间）；结束则写“无，任务已结束”>
下轮计划：<下一轮准备完成的具体动作和目标数量；结束则写“无”>
```

The heartbeat time must come from the timer's intended/read-back schedule, not a vague interval or an invented value. Do not expose intermediate worker reports or technical implementation details unless the user asks.
