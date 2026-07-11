# Orchestration Core

Use this reference for every real Reddit operation. It owns shared state, lifecycle, browser coordination, risk classification, and compact reporting. Lane playbooks own candidate selection and lane-specific gates.

## Session State

Maintain one small state record:

| Field | Meaning |
|-|-|
| `scope` | run kind, mission ID, user request, authorization, duration/intensity/count, language, pool, stop time |
| `environment` | Chrome capability, account, connection/recovery status, local time/timezone/UTC, scheduler support, detected `scheduler_clock_mode`, and authorized worker support |
| `account_tier` | `K0 New`, `K1 Growing`, or `K2 Established`; separate `bootstrap_state` records workflow initialization without changing tier |
| `model_runtime` | coordinator and worker request/actual `gpt-5.6-luna/high`, fallback reason |
| `history_ledger` | recent outward subreddit, cluster, angle, measured `char_count`/`word_count`/`sentence_form`/length tier, opening, claims, and permalinks |
| `browse_ledger` | qualified reads, subreddit/URL/topic, specific observation, persona fit, vote/no-vote decision, score/reason, and views since last vote |
| `operation_style` | resolved style profile and optional voice modifier used for future candidate discovery |
| `eligible_pool` | user/default pool after layer, row restriction, account fit, and history filtering |
| `lanes` | enabled lane owners, status, current slot, remaining target |
| `task_titles` | current task title and dispatched lane task titles after routing |
| `worker_registry` | task ID, lane, title, last read time, status, remaining target, and owned automation |
| `startup_handoff` | batch objective, per-lane first-round state, immediate/delayed visibility result, retry count, heartbeat readback, and handoff result |
| `browser_context` | this lane's dedicated `tab_id`, optional `group_id`, current URL, and confirmed account |
| `action_log` | verified actions and candidate skips |
| `next_trigger` | at most one one-shot continuation per lane, with automation ID plus expected/actual worker thread binding |
| `turn_gate` | `start_proof_by_lane` for a user command and `slot_proof` for each execution-lane heartbeat resume |

Do not create large parallel state tables unless the user asks for an export.

## State Machine

Every first run and resume follows the same state machine:

| State | Required action | Exit |
|-|-|-|
| `SCOPE` | Parse latest user request and overrides. | scope is unambiguous |
| `PROBE` | Auto-discover/reconnect Chrome, confirm account/time, then check scheduler/task capabilities. | environment recorded |
| `HISTORY` | Restore recent profile/session actions and stable identity claims. | history ledger ready |
| `ROUTE` | Select tier, lower-restriction eligible pool, lane(s), and Luna/high for coordinator/workers. | lane owner(s), pool, and model ready |
| `NAME` | Rename the current task and dispatched lane tasks after state is fixed. | concise Chinese titles applied or unavailability recorded |
| `PLAN_SLOT` | Create only the next executable slot from remaining time/count. | slot has target and time budget |
| `DISCOVER` | Inspect lane surfaces and candidate context. | candidate passes or pool exhausted |
| `CHECK_A` | Check pool/rules/history/eligibility before drafting. | pass / retarget / stop |
| `DRAFT` | Text lanes choose length and write target-specific copy; browsing applies its vote gate without drafting text. | final draft or vote decision ready |
| `CHECK_B` | Text lanes recheck account/page/copy/history/duplicate; browsing rechecks account/URL/direction and eligibility. | submit / vote / rewrite / retarget / stop |
| `ACT` | Reselect this lane's dedicated tab, confirm account/target, perform action, and verify. | result recorded |
| `RECONCILE` | Update remaining target from actual time and quality. | next decision known |
| `SCHEDULE` | Create one next one-shot trigger if needed and read timing back when exposed. | verified, created_unreadable, or manual fallback |
| `REPORT` | Return compact operational record. | turn ends |

Every enabled lane on first activation must reach `ACT` or a verified no-action/blocker result before both `SCHEDULE` and `REPORT`. `START_NOW_PROOF_BY_LANE` is a hard transition guard: no path from `SCOPE`, `ROUTE`, `NAME`, `PLAN_SLOT`, or worker dispatch may jump directly to `SCHEDULE`/`REPORT`. An execution-lane heartbeat resume starts at `PROBE`, refreshes `HISTORY`, completes the current slot, records `SLOT_PROOF`, and only then schedules its successor. A coordinator-watch heartbeat is read-only and may only observe lanes that already passed their start gate.

## Scope And Authorization

- The user's latest explicit request overrides defaults for lane, target, language, duration, count, pool, and output.
- `运营` enables four lanes: comments, posts, follow-up, and natural browsing. Missing duration defaults to `3 hours`; missing intensity defaults to `standard`. A named action enables only its matching lane.
- User model/effort overrides take priority when available. Otherwise use `model-runtime.md`: coordinator and workers request `gpt-5.6-luna/high`, and unavailable overrides do not block execution.
- Session-level authorization covers ordinary actions in the active session and its one-shot continuations. Do not ask before every item.
- Ask only when the request is genuinely ambiguous or a concrete soft-risk choice materially changes the action. A worker sends that question to the coordinator under `risk-escalation.md`; it never asks inside the lane task.
- Do not silently turn requested posts into comments or requested follow-up into discovery.

## Task Naming

After `ROUTE` determines the account state and enabled lanes, rename the current task before normal execution and rename each dispatched task immediately after creation when task-title control is available.

Naming rules:

- Chinese by default; retain English only when it is an unavoidable product/proper name.
- Prefer exactly `4` Chinese characters; maximum `8` characters.
- Name by durable responsibility, not temporary counts, timestamps, subreddit names, or model names.
- Rename once after routing. Rename again only when the task's lane or responsibility materially changes; do not rename on every heartbeat.
- If current-task ID/title control or child-title control is unavailable, record `title_unavailable` internally and continue. Never block publishing or ask the user only for naming.

Default titles:

| Responsibility | Title |
|-|-|
| global coordinator | `Loci Reddit运营` |
| proactive comment lane | `主动评论` |
| proactive post lane | `主动发帖` |
| follow-up lane | `消息跟进` |
| browsing lane | `自然浏览` |

The user-facing task always keeps `Loci Reddit运营`, including for a single-lane MISSION. Only an explicitly handed-off WORKER task uses a lane title. Account tier and mission type never change these titles.

## Independent Lane Tabs

Chrome is required for account mutations, but the shared Chrome profile and Reddit account are not cross-task locks.

1. Discover Chrome control automatically; never require the user to type `@chrome`.
2. Each lane opens or reclaims its own Reddit tab. Create a lane-specific Tab Group when the Chrome tool exposes that capability; otherwise keep a dedicated tab.
3. Record `tab_id`, optional `group_id`, current URL, and confirmed account in that worker only.
4. Before every action, reselect the lane tab and confirm its account and URL. Do not rely on the globally focused tab.
5. Never navigate, close, regroup, or reuse another lane's tab. Do not inspect or wait for other workers.
6. Each task executes and verifies only its own lane. Other workers' targets, actions, timing, and account use are outside its state.

## Chrome Recovery

Treat stale tabs, missing controls, dropped browser sessions, `ERR_BLOCKED_BY_CLIENT`, and ordinary connection errors as recoverable first. `ERR_BLOCKED_BY_CLIENT` on one Reddit route is not evidence of an account restriction and is not permission to end the whole lane.

1. Stop the current click/type sequence in this lane's tab.
2. Record the last verified state: target URL, whether text was entered, whether submit was clicked, and whether visibility was confirmed.
3. Reacquire/reconnect Chrome control, reclaim this lane's tab or open a replacement dedicated tab, navigate to Reddit, and confirm the intended account.
4. If the disconnect happened after or near submit, inspect the target thread/profile first. If the action exists, log it and continue; do not resubmit.
5. If no send occurred, reopen the target in this lane's tab, re-read current context, and continue from the last safe step.
6. Allow up to two recovery attempts for one incident. Do not loop indefinitely.

For `ERR_BLOCKED_BY_CLIENT`, reconnect/reacquire Chrome, open a clean dedicated tab, and retry through a native Reddit entry surface such as the subreddit home, Notifications, profile history, or an already visible link instead of repeating only the blocked deep URL. If one candidate/route remains blocked after recovery, record `skip_candidate`, continue the remaining slot on another eligible route/community, and stop the lane only when Chrome control itself remains unavailable after both recovery attempts.

If Chrome remains unavailable after recovery attempts, report `chrome_unavailable_after_reconnect` and pause account mutations. If Reddit is logged out, on the wrong account, asks for credentials, or shows captcha/rate limit/lock, stop immediately. A worker sends the evidence to `Loci Reddit运营` under `risk-escalation.md`; only the coordinator asks the user to repair the session. Never enter credentials.

## Active Pool

- User targets override the bundled Loci pool.
- Within the eligible pool, use `operation-style-profiles.md` to rank topic/community fit before candidate scoring. Style never upgrades an `A0/No-go` target or bypasses live rules.
- Merge custom and bundled targets only when the user allows expansion or gives no exclusive pool.
- `B`: may enter native posts/comments when row rules fit.
- `B+`: may enter ordinary comments and low-frequency feedback/demo contexts when row rules fit.
- `A`: research-first; interact only with a clear ordinary, non-product reason.
- `A0` and `No-go`: read-only; no posts, comments, votes, joins, flair, or warm-up actions.
- The bundled row is a routing hint. A main post still needs live same-day preflight.

## Lane Ownership

| Lane | Owns | Must not do |
|-|-|-|
| `follow-up` | notifications, supplied URLs, own recent posts/comments, mod/Automod | unrelated discovery or new main posts |
| `comments` | new comments on existing threads | notifications, main posts, or voting |
| `posts` | new main posts and full live preflight | ordinary comment volume or notifications |
| `browsing` | qualified reading and optional gated upvote/downvote decisions | comments, posts, replies, profile edits, joins, or Notifications |

Real operations require persistent task create/read/send capability. The user's `开始` or concrete operation command is explicit authorization to create the requested user-visible lane tasks. Default broad operation requires all four workers; a named single-lane mission requires that one worker. Never replace them with sequential coordinator execution or invisible subagents.

For the first turn of a new operation, delegation is valid only when the coordinator can read every enabled worker's verified `ACT`/no-action result before its own final response. Worker creation or mission delivery alone is not execution. A plan-only worker gets one execute-now correction. If proof remains unavailable, mark that lane `startup_blocked`; coordinator execution is forbidden.

The `Loci Reddit运营` task is not another lane. It stores the worker registry, answers the user, accepts the first round of each newly dispatched batch, and reads workers later when the user asks. It never performs lane mutations or owns a combined continuation. Load `coordinator-playbook.md`. Workers do not send routine callbacks; they must return decision-requiring risks/blockers to it.

The coordinator remains responsible through the fixed first-hour watch in `coordinator-playbook.md`, but only through its verified one-shot heartbeat. Dispatch and early acceptance are insufficient: it runs the mandatory boundary sweep at `startup_watch_deadline`. It must not use Goal Mode or generate progress-only turns while waiting. After that handoff, workers continue independently and the coordinator becomes user-driven again.

The coordinator is the technical abstraction boundary. Recover implementation faults internally when possible and keep task, model, scheduler, tab, retry, and scoring details out of normal user reports. Escalate only a concrete user-required repair using the short schema in `coordinator-playbook.md`.

Automation ownership follows the lane and target thread:

- The registry supplies the exact `worker_thread_id`; the worker passes it as explicit `targetThreadId` whenever the automation API supports that field.
- Before creating, updating, pausing, or deleting an automation, verify its `target_thread_id` equals the registered `worker_thread_id` for the current lane and that its prompt belongs to the same lane.
- A lane task may mutate only its own automation. Other lanes are outside its state; it must not inspect, classify, pause, rewrite, or absorb their work.
- A global policy message delivered to several lane tasks applies to the current lane only. Do not inspect or coordinate the other lane tasks.
- The coordinator sends amendments to lane owners instead of taking over their automations. Each owner changes only its own trigger.
- Different lanes sharing an account, target, or policy window remain independent. Do not compare them for collisions.
- During BOOTSTRAP, the coordinator reads all enabled lanes through the full first-hour watch. During MISSION, it reads only affected lanes until verified one-shot completion or the bounded watch deadline. STATUS reads relevant lanes once. AUDIT performs one bounded evidence pull under `operations-audit.md`, including exact read-only permalink verification when needed. Workers record routine state locally and callback only for decision-requiring risks/blockers.
- The coordinator may own one temporary read-only watch automation named `Loci Reddit运营-首轮监督`. Its prompt may only read worker state and report; it cannot open Reddit, publish, vote, reply, or continue lane work. BOOTSTRAP keeps it through the fixed first-hour boundary; ongoing MISSION keeps it for at most one hour; one-shot MISSION may delete it after verified completion. Lane automations remain owned by their lane tasks.
- Automation name, prompt, or lane title never proves thread ownership. Exact `target_thread_id` match or provisional creator-thread evidence from `scheduler-and-heartbeats.md` is required.

## Decision Classes

Use one of four decisions; never say only `account safety`.

- `act`: rules, context, account state, quality, and lane gate pass.
- `skip_candidate`: low score, stale/saturated thread, weak fit, unclear eligibility for one target, duplicate angle, or unavailable control. Search another candidate.
- `soft_pause`: action appears allowed but has concrete elevated moderation or pacing risk. Pause only that lane/candidate and escalate once to the coordinator with a safer variant.
- `hard_stop`: captcha, rate limit, lock/suspension, wrong/logged-out account, credential request, account-wide warning, clear rule prohibition, locked/removed target, or unsafe/deceptive action. A community-specific removal/visibility failure stops that target and activates `R1/R2` from `proactive-playbook.md`; it becomes account-wide only when the recovery definition says so.

If an own newly submitted main post is awaiting moderator approval, delete/withdraw it when possible and stop only the post lane unless Reddit also shows an account-wide blocker.

Never invent firsthand experience, identity, expertise, metrics, affiliations, product usage, or testing. Do not coordinate votes, use another account on the same target, harass, doxx, or engage sensitive/vulnerable-user threads.

## Slot Execution

For the current lane:

The `browsing` lane loads `browse-vote-playbook.md` and uses its qualified-read ledger, vote opportunity, gate, and verification flow. It does not run text drafting or publishing checks. The numbered flow below applies to comments, posts, and follow-up replies.

1. Define a small time/count target that can finish without a burst.
2. Restore history and choose a lower-restriction eligible community.
3. Apply the resolved operation style, inspect the relevant Reddit surfaces, and score/triage the candidate. Do not force a style into an unrelated target.
4. Load `publish-consistency.md`; run Double-Check A.
5. Run `outbound-copy-gate.md`, choose length from context/history, and enter the final draft.
6. Run Double-Check B immediately before submit.
7. Reselect this lane's dedicated tab, confirm account/target, pause briefly, submit, and verify.
8. Append the action to history and log URL, text/translation, exact character/word counts, sentence form, length tier/reason, score/triage, visibility, and warnings.
9. Continue within the slot only while quality, diversity, and pacing permit; otherwise reconcile early.

Counts are planning targets, not permission to lower candidate thresholds. Do not compensate for delays or misses with compressed activity.

## Resume And Schedule

After each slot:

- mark actual actions and remaining target
- recompute from actual local time, not the original ideal timeline
- stop at user stop time or when no quality candidate remains in the budget
- if continuing, create one one-shot trigger for this lane; verify local time, UTC time, repeat-off state, and scheduler readback when those fields are exposed
- if creation succeeds but persisted timing is hidden, record `created_unreadable`, keep the trigger, finish the current slot, and validate timing at the next real wakeup; do not pause Reddit work or ask the user to repair it
- if creation itself fails, finish the current slot and report a manual next local/UTC time

Never run this scheduling section until the current user-command turn has `START_NOW_PROOF_BY_LANE`, or the current execution-heartbeat turn has `SLOT_PROOF`. The first heartbeat may resume the second slot, never the first; every later heartbeat must execute its own slot before creating another.

## Compact Report Schema

```text
本轮完成：<主要动作；完成数量>
发布/处理：<r/subreddit | 评论/帖子/回复/主页动作 | permalink>；无动作则写“未发布：<原因>”
下一轮：<YYYY-MM-DD HH:mm 时区 | 下一轮动作>；结束则写“已结束，不再调度”
风险：<无 | 具体风险、影响和是否已暂停>
```

The detailed action log still stores final text/translation, score/triage, Check A/B, history comparison, visibility, account/tier, model runtime, this lane's tab/group identity, and schedule readback. Keep those internal by default. Surface only the detail that explains a risk, blocker, failed schedule, or explicit user question.

Write the entire user-facing report in Chinese. Preserve English only for proper nouns, identifiers, links, subreddit names, model names, and exact Reddit UI/error messages that would lose precision when translated.
