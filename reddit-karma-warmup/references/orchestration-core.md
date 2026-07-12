# Orchestration Core

Canonical owner of one worker's executable slot: state restoration, lane/tab boundary, candidate decision, action verification, reconciliation, and proof handoff. Coordinator/task-registry/timer procedures remain in their owning references. Lane playbooks own candidate selection and lane-specific gates.

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
| `worker_registry` | task ID, lane, title, last read time, status, remaining target, and coordinator-managed automation targeting this worker |
| `startup_handoff` | batch objective, per-lane first-round state, immediate/delayed visibility result, retry count, heartbeat readback, and handoff result |
| `browser_context` | this lane's dedicated `tab_id`, optional `group_id`, current URL, and confirmed account |
| `action_log` | verified actions and candidate skips |
| `operation_timer` | coordinator-managed recurring timer ID, expected next wake, deadline, and expected/actual worker task binding |
| `turn_gate` | `start_proof_by_lane` for a user command and `slot_proof` for each execution-lane heartbeat resume |

Do not create large parallel state tables unless the user asks for an export.

## State Machine

Every first run and resume follows the same state machine:

| State | Required action | Exit |
|-|-|-|
| `SCOPE` | Parse the latest user request; replace conflicting defaults, historical-recovery advice, and older mission fields. | scope is unambiguous |
| `PROBE` | Auto-discover/reconnect Chrome, confirm account/time, then check scheduler/task capabilities. | environment recorded |
| `HISTORY` | Restore recent profile/session actions and stable identity claims. | history ledger ready |
| `ROUTE` | Select tier, lower-restriction eligible pool, lane(s), and Luna/high for coordinator/workers. | lane owner(s), pool, and model ready |
| `NAME` | Ensure the already-promoted coordinator is titled `Reddit 主控台`, then rename dispatched lane tasks after state is fixed. Bootstrap naming/promotion is owned by `runtime-and-setup.md`. | concise Chinese titles applied or unavailability recorded |
| `PLAN_SLOT` | Create only the next executable slot from remaining time/count. | slot has target and time budget |
| `DISCOVER` | Inspect lane surfaces and candidate context. | candidate passes or pool exhausted |
| `CHECK_A` | Check pool/rules/history/eligibility before drafting. | pass / retarget / recover |
| `DRAFT` | Text lanes choose length and write target-specific copy; browsing applies its vote gate without drafting text. | final draft or vote decision ready |
| `CHECK_B` | Text lanes recheck account/page/copy/history/duplicate; browsing rechecks account/URL/direction and eligibility. | submit / vote / rewrite / retarget / recover |
| `ACT` | Reselect this lane's dedicated tab, confirm account/target, perform action, and verify. | result recorded |
| `RECONCILE` | Update remaining target from actual time and quality. | next decision known |
| `SCHEDULE_HANDOFF` | Return proof and proposed next due state to the coordinator; never mutate automations. | proof/state returned |
| `REPORT` | Return compact operational record. | turn ends |

Every enabled lane on first activation must reach `ACT` or a browser-backed no-action/recovery checkpoint before `SCHEDULE_HANDOFF` and `REPORT`. `START_NOW_PROOF_BY_LANE` prevents plan-only deferral but does not require a successful mutation. A lane Heartbeat resume starts at `PROBE`, refreshes `HISTORY`, completes one due slot or records `not_due`, then returns proof/state. The coordinator creates and maintains all recurring Heartbeats.

## Scope And Authorization

- The user's latest explicit request overrides defaults for lane, target, language, duration, count, pool, and output.
- `运营` enables four outward lanes: comments, posts, follow-up, and natural browsing. A first bootstrap additionally enables presence only when the profile/community baseline is incomplete. Missing duration defaults to `3 hours`; missing intensity defaults to `standard`. A named action enables only its matching lane.
- User model/effort overrides take priority when available. Otherwise use `model-runtime.md`: coordinator and workers request `gpt-5.6-luna/high`, and unavailable overrides do not block execution.
- Session-level authorization covers ordinary actions in the active session and subsequent wakes of the coordinator-managed recurring Heartbeat targeting that lane. Do not ask before every item.
- Infer ordinary operational details from the latest command, selected style, live rules, and safest eligible substitute. Ask only when the user explicitly required one exact target/action and every compliant interpretation materially changes that requirement. A worker sends that rare question to the coordinator; it never asks inside the lane task.
- Do not silently turn requested posts into comments or requested follow-up into discovery.

## Task Naming

Setup naming is outside this worker state machine and is owned by `runtime-and-setup.md`: a setup command immediately names the current task `Reddit 启动台`, then healthy preflight promotes and renames that same task `Reddit 主控台`. For a direct mission on an installed Skill, rename the current task `Reddit 主控台` before `SCOPE`/Chrome work. After `ROUTE`, rename each dispatched task immediately after creation when task-title control is available.

Naming rules:

- Chinese by default; retain English only when it is an unavoidable product/proper name.
- Prefer exactly `4` Chinese characters; maximum `8` characters.
- Name by durable responsibility, not temporary counts, timestamps, subreddit names, or model names.
- Rename once at each real role transition: setup arrival -> Bootstrap title, healthy handoff -> coordinator title, or task creation -> lane title. Do not rename on every heartbeat.
- If current-task ID/title control or child-title control is unavailable, record `title_unavailable` internally and continue. Never block publishing or ask the user only for naming.

Default titles:

| Responsibility | Title |
|-|-|
| setup/bootstrap role on the future coordinator task | `Reddit 启动台` |
| global coordinator | `Reddit 主控台` |
| proactive comment lane | `Reddit 评论台` |
| proactive post lane | `Reddit 发帖台` |
| follow-up lane | `Reddit 跟进台` |
| browsing lane | `Reddit 浏览台` |
| profile/community presence lane | `Reddit 主页台` |

During setup, the user-facing task keeps `Reddit 启动台`. After healthy promotion, that same task ID keeps `Reddit 主控台`, including for a single-lane MISSION. Only an explicitly handed-off WORKER task uses a lane title. Never create a second main task for the role transition. Account tier and mission type never change these titles.

After resolving exact task IDs, pin `Reddit 主控台` and explicitly keep every execution task unpinned. Pinning is presentation state, not ownership proof. Do not archive active or idle registered workers; archive only completed temporary probes/diagnostics and retired workers after their heartbeat is removed and tab state is released.

## Independent Lane Tabs

Chrome is required for account mutations, but the shared Chrome profile and Reddit account are not cross-task locks.

1. Discover Chrome control automatically; never require the user to type `@chrome`.
2. Each lane opens or reclaims its own Reddit tab. Create a lane-specific Tab Group when the Chrome tool exposes that capability; otherwise keep a dedicated tab.
3. Record `tab_id`, optional `group_id`, current URL, and confirmed account in that worker only.
4. Before every action, reselect the lane tab and confirm its account and URL. Do not rely on the globally focused tab.
5. Never navigate, close, regroup, or reuse another lane's tab. Do not inspect or wait for other workers.
6. Each task executes and verifies only its own lane. Other workers' targets, actions, timing, and account use are outside its state.

## Chrome Recovery

Load `chrome-network-recovery.md` whenever Chrome control, navigation, or page loading fails. Treat stale tabs, missing controls, dropped browser sessions, `ERR_BLOCKED_BY_CLIENT`, and ordinary connection errors as recoverable first. `ERR_BLOCKED_BY_CLIENT`, DNS/network codes, blank pages, or HTTP `5xx` are not evidence of an account restriction by themselves.

1. Stop the current click/type sequence in this lane's tab.
2. Record the last verified state: target URL, whether text was entered, whether submit was clicked, and whether visibility was confirmed.
3. Follow the classified layer: reconnect Chrome only for an explicit `control_channel` disconnect; for `stale_tab`, preserve the browser binding and open/reclaim only this lane's replacement tab. Navigate to Reddit and confirm the intended account after recovery.
4. If the disconnect happened after or near submit, inspect the target thread/profile first. If the action exists, log it and continue; do not resubmit.
5. If no send occurred, reopen the target in this lane's tab, re-read current context, and continue from the last safe step.
6. Use the reference's bounded two-attempt state machine. The second attempt may be a `5-10 min` recovery Heartbeat using this lane's existing timer; do not loop indefinitely or create another timer.

For `ERR_BLOCKED_BY_CLIENT`, reconnect Chrome only when control also dropped; otherwise preserve the browser binding, open a clean dedicated tab, and retry through a native Reddit entry surface such as the subreddit home, Notifications, profile history, or an already visible link instead of repeating only the blocked deep URL. If one candidate/route remains blocked after recovery, record `skip_candidate`, continue the remaining slot on another eligible route/community, and keep the lane in recurring recovery if Chrome control remains unavailable.

If Chrome remains unavailable after one wake's bounded recovery, report `chrome_unavailable_after_reconnect`, keep the Heartbeat active, and re-probe on later wakes. Ask the user only after the same control failure persists across three consecutive recovery wakes. If Reddit shows a timed rate limit, keep read-only/independent work active and resume mutations automatically at expiry. Login/account mismatch, credentials, CAPTCHA/challenge, lock/suspension, or required acknowledgement with no automatic path enters the hard user-repair allowlist; never infer one from history alone.

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
| `presence` | profile/about, Join/subscribe, truthful Flair/tag, membership review | comments, posts, replies, voting, Notifications, or general browsing quotas |

Each lane follows one fixed microflow; its playbook owns the detailed gates:

| Lane | Microflow | Slot exit |
|-|-|-|
| `comments` | discover discussion -> inspect context/rules/history -> choose length -> draft -> double-check -> submit -> verify | permalink or candidate-backed no-action |
| `posts` | choose community/angle -> live rules/eligibility/flair/frequency preflight -> draft native post -> double-check -> submit -> verify visibility | permalink or preflight-backed no-action |
| `follow-up` | inspect Notifications plus own activity -> triage Act/Watch/Skip -> draft only for Act -> submit -> verify | reply/action proof or completed quiet sweep |
| `browsing` | discover -> qualified read -> score direction/quality -> independently gate vote -> click at most once -> ledger | read ledger plus accepted vote/no-vote decisions |
| `presence` | inspect profile/membership -> compute cadence -> score target -> edit/Join/Flair only when eligible -> verify state | changed-state proof or inspected no-action; normally terminal |

Real operations require persistent task create/read/send capability. The user's `开始` or concrete operation command is explicit authorization to create the requested user-visible lane tasks. Default broad operation requires the four outward workers; `ACCOUNT_BOOTSTRAP` adds the presence worker only when required; a named single-lane mission requires that one worker. Never replace them with sequential coordinator execution or invisible subagents.

For the first turn of a new operation, delegation is valid per lane when the coordinator reads its verified `ACT` or browser-backed no-action/recovery checkpoint. Worker creation or mission delivery alone is not execution. A plan-only worker gets one execute-now correction. A temporarily unreachable lane becomes `lane_recovering`; it never delays acceptance or scheduling of another lane, and coordinator execution remains forbidden.

The `Reddit 主控台` task is not another lane. It stores the registry/slot ledger, answers the user, accepts first proof, centrally creates recurring Heartbeats, and supervises continuation. It never performs lane mutations or creates a combined execution continuation. Load `coordinator-playbook.md`. Workers do not send routine callbacks; they return only decision-requiring risks/blockers, non-blocking subreddit-retirement notices, and exactly one terminal lane-mission completion.

For every multi-slot mission, the coordinator remains responsible through a recurring read-only supervisor Heartbeat until the deadline. The first `ACCOUNT_BOOTSTRAP` hour adds checkpoints near `+15m`, `+35m`, and `+60m`; later supervision verifies wake turns, slot counts, binding, recurrence, and continuation. It must not use Goal Mode or poll inside an active turn.

The coordinator is the technical abstraction boundary. Recover implementation faults internally when possible and keep task, model, scheduler, tab, retry, and scoring details out of normal user reports. Escalate only a concrete user-required repair using the short schema in `coordinator-playbook.md`.

Automation management is centralized; execution ownership still follows lane and target task:

- The registry supplies the exact `worker_thread_id`; the coordinator passes it as explicit `targetThreadId` when creating/updating that lane's recurring Heartbeat.
- Before creating, updating, pausing, or deleting an automation, the coordinator verifies target, lane prompt, recurrence, next wake, and deadline.
- A lane task never mutates any automation and never inspects sibling tasks/timers.
- A global policy message delivered to several lane tasks applies to the current lane only. Do not inspect or coordinate the other lane tasks.
- The coordinator sends mission amendments to workers and updates the corresponding recurring Heartbeat itself.
- Different lanes sharing an account, target, or policy window remain independent. Do not compare them for collisions.
- The recurring coordinator supervisor reads enabled lanes on its bounded cadence until mission end. STATUS and AUDIT may also perform one bounded evidence pull. Workers record routine state locally and return only risk/blocker, subreddit-retirement, or terminal-completion events.
- The coordinator owns one recurring read-only automation named `Reddit 主控台-任务监督` plus one distinct recurring Heartbeat per enabled lane that still has nonterminal future work. The supervisor cannot open Reddit or execute lane work; a terminal one-slot presence mission has no lane Heartbeat.
- Automation name, prompt, or lane title never proves task ownership. Exact `target_thread_id` plus repeat/time/deadline verification from `scheduler-and-heartbeats.md` is required.

## Decision Classes

Use one of four decisions; never say only `account safety`.

- `act`: rules, context, account state, quality, and lane gate pass.
- `skip_candidate`: low score, stale/saturated thread, weak fit, unclear eligibility for one target, duplicate angle, or unavailable control. Search another candidate.
- `recover_lane`: a tab, route, client-block, network, or control failure prevents the current step. Preserve mutation integrity, run bounded recovery, keep the lane Heartbeat active, and continue another safe candidate/surface when possible. Never ask for confirmation or affect siblings.
- `hard_user_repair`: only credentials required, persistent wrong/logged-out account, manual CAPTCHA/challenge, explicit account lock/suspension or required acknowledgement, or Chrome control unavailable across three consecutive recovery wakes. Preserve Heartbeats and all permitted work while waiting. A timed rate limit is `recover_lane`; clear rule prohibition or unsafe/deceptive copy is `skip_candidate`/retarget, never a mission stop. Historical/cleared states never qualify.

If an own newly submitted main post is awaiting moderator approval, delete/withdraw it immediately without asking, verify cleanup once, retire that subreddit, send `SUBREDDIT_RETIRED`, and continue the post lane with another eligible community. A temporary cleanup-route failure enters the observing lane's retry queue and does not pause post discovery, follow-up processing, browsing, comments, presence work, or sibling Heartbeats.

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

## Resume And Scheduler Handoff

After each slot:

- mark actual actions and remaining target
- recompute from actual local time, not the original ideal timeline
- stop only at user stop/deadline/target completion; when no quality candidate remains in the current budget, record a no-action checkpoint and schedule fresh discovery
- if continuing, report proposed `next_due_at`, remaining work, and current proof to the coordinator; do not touch scheduling
- if the recurring Heartbeat fired, include actual wake time so the coordinator supervisor can reconcile it
- if the worker observes a wrong/missing timer card, report evidence but do not repair it

The coordinator must not create the recurring lane Heartbeat until the current user-command turn has `START_NOW_PROOF_BY_LANE`. The first Heartbeat resumes a later slot, never the first. Every wake executes one due slot or records `not_due`; no successor creation exists.

## Report Handoff

Use the exact three-line report owned by `SKILL.md` after every ordinary slot and Heartbeat wake. Risk/blocker messages use `risk-escalation.md`; do not restate or extend the ordinary schema here.

The detailed action log still stores final text/translation, score/triage, Check A/B, history comparison, visibility, account/tier, model runtime, this lane's tab/group identity, and schedule readback. Keep those internal by default. Surface only the detail that explains a risk, blocker, failed schedule, or explicit user question.

Write the entire user-facing report in Chinese. Preserve English only for proper nouns, identifiers, links, subreddit names, model names, and exact Reddit UI/error messages that would lose precision when translated.
