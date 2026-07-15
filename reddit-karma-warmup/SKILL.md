---
name: reddit-karma-warmup
description: Run authorized Reddit community operations through the user's logged-in Chrome session. Use for reusable account-scoped lane dispatch, setup, proactive comments, native posts, follow-up replies, natural browsing and voting, profile/community presence, timed autonomous lane operation, or lane-local status and recovery.
---

# Reddit Karma Warmup

Use a reusable distributor plus independent account-scoped lane tasks. There is no persistent main coordinator.

## Five-Step Default Flow

| Step | Owner | Result |
|-|-|-|
| `1 SETUP` | current task as temporary `Reddit 启动台` | install/upgrade, read-only preflight, exact current-task identity |
| `2 READY` | same task renamed and pinned as `Reddit 分发台` | ask once for direction + duration, or immediately normalize supplied inputs |
| `3 DISPATCH` | `Reddit 分发台` | resolve exact account+lane task IDs, reuse healthy tasks, create only missing/unusable tasks, deliver complete missions |
| `4 EXECUTE` | independent lane tasks | start browser-backed work now, own one persistent dedicated Reddit primary tab plus only their state/Heartbeat, and report locally |
| `5 RETIRE OR REUSE` | each lane task | delete its own Heartbeat on mission completion; keep the task available for a later new mission ID |

The generic `thread-supervisor` Skill is optional. When available, use its current tool/identity semantics; this Skill's `thread-supervision-runtime.md` remains the authority for Reddit's no-callback, independent-lane topology.

## Roles

| Role | Stable title | Owns | Never does |
|-|-|-|-|
| `REDDIT_LAUNCHER` | pinned `Reddit 分发台` after temporary `Reddit 启动台` setup | install/upgrade, read-only preflight, rename and pin the exact current task after health passes, accept later dispatch commands, reuse the exact registered account+lane tasks when healthy, create only missing/unusable lanes, deliver each mission, then idle | Reddit actions, ongoing supervision between commands, worker callbacks, worker Heartbeats, cross-lane status |
| `COMMENTS_WORKER` | `Reddit 评论台` | proactive comment discovery, drafting, submission, verification, its own timer/recovery/report; incidental voting on already-read candidates | posts, follow-up, vote hunting, sibling inspection |
| `POSTS_WORKER` | `Reddit 发帖台` | subreddit/rules preflight, native posts, verification, its own timer/recovery/report; incidental voting on already-read external research samples | comments, follow-up, vote hunting, sibling inspection |
| `FOLLOWUP_WORKER` | `Reddit 跟进台` | Notifications and replies to own activity, incidental voting on already-read inbound replies, its own timer/recovery/report | proactive discovery, new posts, vote hunting, sibling inspection |
| `BROWSING_WORKER` | `Reddit 浏览台` | explicit pure-browse missions with qualified reading, independently gated Upvote/Downvote, its own timer/recovery/report | default broad-operation dispatch, text publishing, sibling inspection |
| `PRESENCE_WORKER` | `Reddit 主页台` | truthful profile, Join/subscribe, Flair/tag, membership review, optional own timer | outward content, sibling inspection |

Every task has one objective. Tasks do not callback, inspect, wait for, pause, amend, or report through another task. Sharing one Chrome profile or Reddit account is not a conflict. Every execution task owns one persistent dedicated Reddit primary tab. An optional task-specific Tab Group is only visual organization; it never replaces the required tab or grants access to another task's tabs.

## Route The Current Request

| Request | Action |
|-|-|
| install/setup/upgrade/explain | Immediately rename the current task `Reddit 启动台`; load `references/runtime-and-setup.md`. After preflight passes, rename the exact same task `Reddit 分发台`, pin it, and load `references/launcher-playbook.md`. |
| healthy Bootstrap answer, any new `开始/运营`, or named publishing command in `Reddit 分发台` | Load `references/default-operations-sop.md`, resolve each requested lane through the account-keyed registry, reuse its healthy existing task or create a replacement only when needed, send the new mission, verify delivery, then idle. In `BOOTSTRAP_AWAITING_OPERATION`, bare `继续` means saved/default direction + `3h` and immediately dispatches comments, posts, and follow-up. In `BOOTSTRAP_REPAIR_REQUIRED`, it only rechecks the missing dependency. |
| one named lane in an ordinary task | Rename the current task to that lane title when possible, load its playbook plus the shared runtime references, execute now, and own later continuation locally. |
| later instruction inside a lane task | Replace that lane's conflicting old mission fields, execute the first changed slot now, and update only that task's Heartbeat. |
| lane status/pause/resume/stop | Read or change only the current lane task and its own Heartbeat. |

Do not redirect a later lane request to the launcher. The user speaks directly to the relevant lane task after dispatch.

## Reference Ownership

- `runtime-and-setup.md`: installation, preflight, immediate launcher naming, and launcher exit.
- `account-direction.md`: one broad truthful account interest portfolio, onboarding resolution, and the boundary between durable direction and per-run style.
- `subreddit-catalog-taxonomy.md` and `subreddit-profile-index.csv`: lightweight profile/tag/traffic discovery index. Query it after direction resolution; catalog matches never grant publishing permission.
- `community-selection-funnel.md`: lane-specific account-direction sweep across up to 100 reference rows, comment shortlist handoff, and the post worker's 20-30 minute broad-to-deep destination search. Load in the distributor for comments/posts and in the post worker before live candidate preflight.
- `posting-account-gates-audit-status.md` and `posting-account-gates-audit-2026-07-14.csv`: current coverage summary plus exact public account-age/Karma/participation-gate rows. Load the status for audit questions and exact rows for every K0/K1 post shortlist; unknown is closed for K1 publishing while K0 never publishes.
- `subreddit-catalog-expansion-2026-07-14.csv` and `reddit-community-search-snapshot-2026-07-14.json`: curated `>=5K` traffic expansion plus its read-only Reddit search evidence. Load only filtered rows needed for account-direction discovery; every added row stays `research_only` until a separate action audit changes its route.
- `launcher-playbook.md`: reusable account-scoped lane routing and delivery proof.
- `thread-supervision-runtime.md`: exact task ID + host identity, returned-identifier readiness, account-keyed registry, bounded legacy adoption, reuse, and replacement rules aligned with the generic Thread Supervisor contract.
- `default-operations-sop.md`: normalize the first mission, exact action targets/caps, target-driven scan loop, incidental voting, and lane-specific later mission.
- `orchestration-core.md`: one lane's executable slot, dedicated Chrome tab, action verification, and local state.
- `scheduler-and-heartbeats.md`: worker-owned recurring Heartbeat, lightweight cross-lane first-write phase staggering, time verification, retry, update, and terminal cleanup.
- `risk-escalation.md`: lane-local recovery and direct user repair inside the affected lane.
- lane playbooks: candidate and action rules for that lane only.
- `chrome-network-recovery.md`: bounded Chrome/page/network recovery in the current lane.
- `outbound-copy-gate.md` and `publish-consistency.md`: hard outbound quality gates. Comments default to `80-90%` micro/fragment/one-liner. Almost every ordinary comment must carry one locally supported colloquial marker, Redditism, or abbreviation; vary the marker across outputs instead of stacking several in one item. Posts retain their own longer context rules.
- `reddit-us-voice-patterns.md`: progressive fallback table for concise, assertive, US-leaning Reddit voice. Nearby current replies always outrank the static table.
- `organization-community-denylist.md`: permanent Loci-wide exclusions across owned, employee, agency, and otherwise coordinated accounts. Check it before the bundled pool or any live subreddit visit.
- `community-action-routing-overrides.md`: latest action-level routing for comments, main posts, and product mention. Apply after the denylist and before the historical pool.
- `community-live-audit-30-2026-07-13.md`: read-only Chrome evidence for the 30 newly audited communities. Load only the exact row when the reason behind an override or a preflight detail is needed; it never grants permission independently.
- `community-expansion-pending-review-2026-07-13.md`: offline expansion evidence with 18 post-suspension re-preflight candidates and 29 newly discovered names. Discovery only; never grants execution permission.
- `community-action-expansion-public-audit-2026-07-13.md`: newer public-rule audit of 30 additional candidates: 14 current/recent rule confirmations, 3 weaker signals, and 13 name-only rows. It prioritizes future live preflight but grants no current action permission.
- `operation-style-profiles.md` and `loci-subreddit-pool-v1.md`: optional style and the large default community archive. Never load the whole archive by default; retrieve only exact subreddit rows or a small keyword-filtered candidate set.

When two references conflict, the owner above wins.

## Launcher Lifecycle

| Stage | Required work | Exit proof |
|-|-|-|
| `L0_NAME` | First available presentation action: rename current task `Reddit 启动台`. | temporary setup title applied or non-blocking `rename_unavailable` |
| `L1_PREFLIGHT` | Install/upgrade and internally check Chrome control, Reddit login, task operations, automation schema, local time and UTC. Never create a bootstrap probe Heartbeat. Persist `BOOTSTRAP_REPAIR_REQUIRED` for a real repair or continue healthy setup. | healthy runtime or one concrete user repair |
| `L1_DIRECTION` | Load `account-direction.md`. For the exact visible Reddit account, silently read its user-owned direction file or prepare the broad default. Do not emit technical or direction-status narration. | account-keyed fallback resolved internally |
| `L2_READY` | After every required preflight item passes, rename this same task `Reddit 分发台`, then call the host thread-pin tool with the exact current task ID and `pinned=true`. If direction and duration were not already supplied, persist `BOOTSTRAP_AWAITING_OPERATION` and emit only the Bootstrap Success Prompt from `runtime-and-setup.md`. | exact prompt only, or immediate dispatch when both inputs already exist |
| `L3_DISPATCH` | Resolve requested lanes for the visible Reddit account; load its exact lane registry; reuse each healthy registered task only when its exact task ID is ready, passing host ID when applicable; perform bounded one-time legacy adoption only when the lane is unregistered, or create and register a replacement when no exact reusable task exists. A queued `clientThreadId` is not ready. Send each complete mission with `worker_task_id=<exact destination task ID>`, `first_due=now`, a static `0/10/20/30...m` first-write phase, `heartbeat_owner=self`, and `launcher_callback=none`. | one exact ready reused/adopted/created task ID and successful mission delivery per requested lane; registry persisted |
| `L4_IDLE` | Keep this distribution task pinned, return the concise complete/partial dispatch receipt plus the reminder that all future Reddit operation distribution can be requested here, and wait for another direct user command. | pinned state retained or `pin_unavailable`; no background reads/callbacks/scheduling/aggregation; a later explicit user dispatch returns to `L3_DISPATCH` with a new mission ID |

If setup needs login, CAPTCHA, Chrome, or another real user repair, remain `Reddit 启动台` and report only that repair. When healthy, rename to and pin `Reddit 分发台`; do not rename to `Reddit 主控台` and do not create one. Resolve self identity from the host's exact current-thread context only; never list/search by title to find the task to pin. On success, do not expose version, validator count, NOOP/install state, account name, preflight checklist, schema migration, rename/pin result, no-action narration, source links, or probe artifacts.

After dispatch, the user may either continue the current mission inside its execution task or return to `Reddit 分发台` and issue another command. Later commands normally reuse the same registered lane tasks for that Reddit account while issuing new mission IDs; no worker ever returns to the launcher.

## Worker Lifecycle

Every lane task independently follows:

1. Resolve `self_task_id` only from the host's exact current-task context; require it equals the mission's `worker_task_id`; then apply the latest user mission and confirm its own exact lane. Never infer self identity from a title, task search, registry row, launcher ID, sibling ID, or automation card.
2. Discover/reconnect Chrome and create or reclaim only its one persistent dedicated Reddit primary tab. The first healthy turn uses a two-call creation transaction: the first completed browser call only creates the tab and returns/persists `own_tab_id`; a second browser call performs the first awaited `tab.goto(...)` with up to 60 seconds. Never combine `tabs.new()` and the first `goto` in one browser call. Later turns reclaim that exact recorded tab from the current Chrome tab inventory. A timeout or REPL reset makes only the navigation acknowledgement uncertain: reconnect the same Chrome/profile, reclaim the exact `own_tab_id`, and inspect URL/title plus DOM/screenshot page state. If the URL moved and the page is readable, continue as recovered; if it is still blank, retry the same tab once and preserve it for the next wake. `openTabs()` URL/title metadata alone is not control proof. Never delete the primary tab on a nonterminal navigation failure, create another while it exists, use page-side script navigation or `CUA` address-bar simulation, or claim an arbitrary user/launcher/sibling tab. Before a nonterminal turn ends, preserve the primary tab with `chrome.tabs.finalize({keep: [{tab: own_tab, status: "handoff"}]})`; at mission terminal cleanup, call `own_tab.close()` before empty finalization and clear its ID. Temporary lane-owned read-only tabs are allowed only when necessary and must be closed in the same turn.
3. Confirm the visible Reddit account, current local time, UTC, and stop time.
4. Load `organization-community-denylist.md` and exclude matches before any subreddit visit. Then load the exact row from `community-action-routing-overrides.md` when present before consulting the historical pool. Any `research-only` or downgraded row forbids comments, posts, and votes. For the 30 live-audited communities, consult the exact row in `community-live-audit-30-2026-07-13.md` only when evidence or a gate needs explanation; the action override remains authoritative. Use `community-expansion-pending-review-2026-07-13.md` and `community-action-expansion-public-audit-2026-07-13.md` only to discover and rank future preflight candidates; every listed candidate remains closed until its required live review passes. Read live context only for remaining eligible destinations. For posts, load `new-account-bootstrap.md` plus exact rows from `posting-account-gates-audit-2026-07-14.csv`: K0 is always research-only with target/cap `0/0`. `main_post_unlock` begins only at K1 with at least `50` combined Karma, `7d` account age, sufficient visible participation, and clean account state; K1 then permits at most one main post per rolling `24h`. An `unknown`, `blocked`, or deny audit row remains closed. Every post still rechecks current subreddit rules, account age/Karma/Flair requirements, and recent posting eligibility before drafting. Default question posts use a truthful beginner-readable community-memory angle, require `discussion_potential_score >=80` from local survivor evidence, and never impersonate a novice or fabricate confusion.
5. Resolve the account direction and the narrower per-run operation style, then resolve the slot's exact target/cap/read floor and start immediately. Reading, discovery, checks, and drafting do not wait for the assigned first-write phase; only the mutation does. Before every individual comment/reply, run the short-first and native-marker requirements in `outbound-copy-gate.md`; missing local voice evidence is `Watch`, not permission to draft. Inside a proactive comment cluster, repeat `CHECK_A -> DRAFT -> CHECK_B -> ACT -> measured log` from scratch for each item; batch drafting or reusing the first comment's length/voice decision is forbidden. Proactive comments use hard clustered windows: unless the user explicitly requested exactly one total comment, a completed comment window contains at least `2` verified comments. One verified comment is an incomplete window, so keep discovering and do not schedule the next Heartbeat or report the window complete. For comments and posts, verified action count is the primary completion condition; reading is discovery evidence, not completion. Continue live discovery until the target is met or the current runtime must yield.

The launcher maps the resolved account direction and current `mission_identity_focus` to the tagged subreddit index before dispatch. For comments and posts, use `community-selection-funnel.md` to assess up to 100 reference rows and attach lane-specific low-friction shortlists. Attach only cached `>=5K` weekly-visitor matches plus a bounded `traffic_probe_queue`; a probe must pass a live traffic check before any worker treats it as an action candidate.

Ordinary native account posts in `POSTS_WORKER` do not use GPT Inf and must not be routed through `loci-prepare-reddit-post`. Draft them directly from current subreddit context, then apply the live rules, truthfulness, account-history, copy-shape, and final-submit checks in this Skill. Use an external rewriting service only when the user explicitly requests it for that exact post.
6. If nonterminal work remains, create or update one recurring Heartbeat with explicit `targetThreadId=self_task_id`, then read the exact returned automation and require its target equals `self_task_id` before recording the timer active. Hidden next-run time is non-blocking; hidden/mismatched target binding is not verified and must not run a continuation.
7. On each wake, recheck `current_task_id == self_task_id == worker_task_id == Heartbeat.targetThreadId`, then resume the same unfinished slot with its exact `slot_target_remaining`; do not reset the count or treat candidate scarcity as completion. Record `not_due`/no-action/recovery only as an interim checkpoint, then keep or update the same timer.
8. At explicit stop, deadline, or verified completion of the current Heartbeat-carried mission target, run mandatory terminal cleanup before reporting: delete only its own Heartbeat, clear `own_heartbeat_id` and every `next_due` field, and set the receipt's next time to `无`. A completed mission may not retain an idle Heartbeat merely because unused authorized time remains. Do not issue the terminal receipt until deletion succeeds or the timer is already absent.

## Independence Gates

- No coordinator task, coordinator registry, coordinator supervisor Heartbeat, callback contract, or centralized completion report.
- A worker never reads or sends messages to another Reddit task. It never checks for task collisions.
- Static phase fields delivered independently with each mission do not create shared runtime state. Workers never negotiate, reserve, or inspect one another's write windows.
- A worker never changes another lane's tab, mission, timer, status, cadence, candidate history, or risk state.
- A worker never treats a visible shared Reddit tab as its own. Its recorded dedicated primary tab is the only persistent browser surface it may reclaim across turns.
- A fault in one lane affects only that lane. Other tasks continue without awareness or permission.
- A task may mutate only its recorded `own_heartbeat_id`. For a correctly targeted malformed timer it verifies the replacement before retiring the old timer; for its own target-mismatched timer it performs no Reddit action, deletes that known misbound timer first, and then creates and post-bind-verifies a corrected timer. Unknown automation IDs are never touched. Reusing a lane task never revives a completed mission or its retired Heartbeat; the new mission starts immediately and owns its own timer lifecycle.
- Temporary subagents may assist bounded read-only analysis but never own Chrome mutations, the lane, its Heartbeat, or user communication.

## User Priority And Recovery

The latest explicit user command controls lane, duration, count, target pool, language, intensity, and style. Defaults and historical warnings are advisory only. Current live subreddit rules and current platform state still gate the exact action.

Automatically recover stale tabs, dropped Chrome control, DNS/network/proxy/TLS errors, `ERR_BLOCKED_BY_CLIENT`, blank/loading pages, timed rate limits, candidate exhaustion, and route failures. Keep the lane's recurring Heartbeat active and retry on later wakes. Explicit HTTP `429`/`Too Many Requests` ends every Reddit action in the current wake and resumes at the later of the lane's next normal round or exposed retry time; it never deletes the mission or Heartbeat. Do not stop the mission because one candidate, subreddit, page, or wake failed.

Ask the user directly in the affected lane task only for a currently visible login/credential requirement, persistent CAPTCHA/challenge, account lock/suspension, required acknowledgement with no automatic path, or an exact user-required prohibited target with no authorized substitute. Do not return the issue to the launcher.

Pending-review own posts are deleted/withdrawn immediately, that subreddit is retired for the current account, and the post worker retargets without confirmation. Historical removals are ledger context, not mission-wide blockers.

## Output

Ordinary worker output uses three concise Chinese lines:

```text
本轮完成：<动作/链接，或具体无动作/恢复结果>。
下轮时间：<经验证的当地时间>；绑定：本任务已核验。终止则写“无（Heartbeat 已删除）”。
下轮计划：<该 lane 下一项工作；风险仅写该 lane 当前真实风险>。
```

After all three first default mission messages are accepted, the launcher returns:

```text
第一轮已分发：Reddit 评论台、Reddit 发帖台、Reddit 跟进台已收到任务。

后续所有 Reddit 运营任务都可以继续在这个 Reddit 分发台下达；告诉我方向、时长或具体动作即可，我会优先沿用已有执行台。

进行中的评论、发帖或跟进，请直接到对应执行台查看或调整。
```

For later dispatches, use `本轮已分发：<actual accepted task titles>已收到任务。`. If any requested lane failed or is uncertain, use `本轮部分分发` and name the missing lane. The launcher never claims full dispatch before exact message acceptance and never aggregates later worker results.
