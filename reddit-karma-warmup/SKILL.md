---
name: reddit-karma-warmup
description: Run authorized Reddit community operations through the user's logged-in Chrome session. Use for reusable stateless fresh-task dispatch, setup, proactive comments, native posts, follow-up replies, natural browsing and voting, profile/community presence, timed autonomous lane operation, or lane-local status and recovery.
---

# Reddit Karma Warmup

Use a reusable stateless launcher plus independent lane tasks. There is no persistent main coordinator.

## Roles

| Role | Stable title | Owns | Never does |
|-|-|-|-|
| `REDDIT_LAUNCHER` | pinned `Reddit 分发台` after temporary `Reddit 启动台` setup | install/upgrade, read-only preflight, rename and pin the exact current task after health passes, accept later dispatch commands, create fresh requested lane tasks, deliver each mission, then idle | Reddit actions, old-task discovery/reuse, ongoing supervision, worker callbacks, Heartbeats, cross-lane status |
| `COMMENTS_WORKER` | `Reddit 评论台` | proactive comment discovery, drafting, submission, verification, its own timer/recovery/report; incidental voting on already-read candidates | posts, follow-up, vote hunting, sibling inspection |
| `POSTS_WORKER` | `Reddit 发帖台` | subreddit/rules preflight, native posts, verification, its own timer/recovery/report; incidental voting on already-read external research samples | comments, follow-up, vote hunting, sibling inspection |
| `FOLLOWUP_WORKER` | `Reddit 跟进台` | Notifications and replies to own activity, incidental voting on already-read inbound replies, its own timer/recovery/report | proactive discovery, new posts, vote hunting, sibling inspection |
| `BROWSING_WORKER` | `Reddit 浏览台` | explicit pure-browse missions with qualified reading, independently gated Upvote/Downvote, its own timer/recovery/report | default broad-operation dispatch, text publishing, sibling inspection |
| `PRESENCE_WORKER` | `Reddit 主页台` | truthful profile, Join/subscribe, Flair/tag, membership review, optional own timer | outward content, sibling inspection |

Every task has one objective. Tasks do not callback, inspect, wait for, pause, amend, or report through another task. Sharing one Chrome profile or Reddit account is not a conflict; each task owns a separate tab or Tab Group.

## Route The Current Request

| Request | Action |
|-|-|
| install/setup/upgrade/explain | Immediately rename the current task `Reddit 启动台`; load `references/runtime-and-setup.md`. After preflight passes, rename the exact same task `Reddit 分发台`, pin it, and load `references/launcher-playbook.md`. |
| any new `开始/运营` or named publishing command in `Reddit 分发台` | Load `references/default-operations-sop.md`, create fresh requested lane tasks, send each its new mission, verify delivery, then idle. This route can be used repeatedly. |
| one named lane in an ordinary task | Rename the current task to that lane title when possible, load its playbook plus the shared runtime references, execute now, and own later continuation locally. |
| later instruction inside a lane task | Replace that lane's conflicting old mission fields, execute the first changed slot now, and update only that task's Heartbeat. |
| lane status/pause/resume/stop | Read or change only the current lane task and its own Heartbeat. |

Do not redirect a later lane request to the launcher. The user speaks directly to the relevant lane task after dispatch.

## Reference Ownership

- `runtime-and-setup.md`: installation, preflight, immediate launcher naming, and launcher exit.
- `account-direction.md`: one broad truthful account interest portfolio, onboarding resolution, and the boundary between durable direction and per-run style.
- `subreddit-catalog-taxonomy.md` and `subreddit-profile-index.csv`: lightweight profile/tag/traffic discovery index. Query it after direction resolution; catalog matches never grant publishing permission.
- `subreddit-catalog-expansion-2026-07-14.csv` and `reddit-community-search-snapshot-2026-07-14.json`: curated `>=5K` traffic expansion plus its read-only Reddit search evidence. Load only filtered rows needed for account-direction discovery; every added row stays `research_only` until a separate action audit changes its route.
- `launcher-playbook.md`: reusable stateless fresh allocation and delivery proof.
- `thread-supervision-runtime.md`: create one fresh independent task per requested lane; never search or reuse old tasks.
- `default-operations-sop.md`: normalize the first mission, exact action targets/caps, target-driven scan loop, incidental voting, and lane-specific later mission.
- `orchestration-core.md`: one lane's executable slot, dedicated Chrome tab, action verification, and local state.
- `scheduler-and-heartbeats.md`: worker-owned recurring Heartbeat, time verification, retry, update, and terminal cleanup.
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
| `L1_PREFLIGHT` | Install/upgrade and read-only check Chrome control, Reddit account, task creation, Heartbeat support, local time and UTC. | healthy runtime or one concrete user repair |
| `L1_DIRECTION` | Load `account-direction.md`. For the exact visible Reddit account, read its user-owned direction file. If absent, show the broad truthful default and wait once for `确认`, a modification, or `确认并开始`; then atomically persist the confirmed direction outside the managed Skill tree. | account-keyed direction exists and matches the visible Reddit account |
| `L2_READY` | After every required preflight item passes, rename this same task `Reddit 分发台`, then call the host thread-pin tool with the exact current task ID and `pinned=true`; then ask for the first operation or accept the operation already present in the setup command. | distribution title attempted; exact self ID reports pinned or non-blocking `pin_unavailable`; no second user turn when operation was already requested |
| `L3_DISPATCH` | Resolve requested lanes; call task creation once per lane without listing/searching history; capture only the newly returned IDs; rename and unpin them; send each complete mission with `first_due=now`, `heartbeat_owner=self`, and `launcher_callback=none`. | one newly created exact task ID and successful mission delivery per requested lane |
| `L4_IDLE` | Keep this distribution task pinned, return the created titles plus the fixed task-routing instruction card, and wait for another direct user command here. | pinned state retained or `pin_unavailable`; no background reads/callbacks/scheduling/aggregation; a later user dispatch returns to `L3_DISPATCH` with a new run ID |

If setup needs login, CAPTCHA, Chrome, or another real user repair, remain `Reddit 启动台`. When healthy, rename to and pin `Reddit 分发台`; do not rename to `Reddit 主控台` and do not create one. Resolve self identity from the host's exact current-thread context only; never list/search by title to find the task to pin. Pin/rename failure is presentation degradation and never blocks dispatch.

After dispatch, the user may either continue the current run inside its execution task or return to `Reddit 分发台` and issue another command. Every distribution command creates another fresh run; no worker ever returns to the launcher.

## Worker Lifecycle

Every lane task independently follows:

1. Apply the latest user mission and confirm its own exact lane.
2. Discover/reconnect Chrome and create or reclaim only its own tab.
3. Confirm the visible Reddit account, current local time, UTC, and stop time.
4. Load `organization-community-denylist.md` and exclude matches before any subreddit visit. Then load the exact row from `community-action-routing-overrides.md` when present before consulting the historical pool. Any `research-only` or downgraded row forbids comments, posts, and votes. For the 30 live-audited communities, consult the exact row in `community-live-audit-30-2026-07-13.md` only when evidence or a gate needs explanation; the action override remains authoritative. Use `community-expansion-pending-review-2026-07-13.md` and `community-action-expansion-public-audit-2026-07-13.md` only to discover and rank future preflight candidates; every listed candidate remains closed until its required live review passes. Read live context only for remaining eligible destinations. For posts, always recheck current subreddit rules, account age/Karma/Flair requirements, and recent posting eligibility before drafting.
5. Resolve the account direction and the narrower per-run operation style, then resolve the slot's exact target/cap/read floor and execute immediately. Before every comment/reply, run the short-first and native-marker requirements in `outbound-copy-gate.md`; missing local voice evidence is `Watch`, not permission to draft. Proactive comments use hard clustered windows: unless the user explicitly requested exactly one total comment, a completed comment window contains at least `2` verified comments. One verified comment is an incomplete window, so keep discovering and do not schedule the next Heartbeat or report the window complete. For comments and posts, verified action count is the primary completion condition; reading is discovery evidence, not completion. Continue live discovery until the target is met or the current runtime must yield.

The launcher maps the resolved account direction to the tagged subreddit index before dispatch. Attach only cached `>=5K` weekly-visitor matches plus a bounded `traffic_probe_queue`; a probe must pass a live traffic check before any worker treats it as an action candidate.

Ordinary native account posts in `POSTS_WORKER` do not use GPT Inf and must not be routed through `loci-prepare-reddit-post`. Draft them directly from current subreddit context, then apply the live rules, truthfulness, account-history, copy-shape, and final-submit checks in this Skill. Use an external rewriting service only when the user explicitly requests it for that exact post.
6. If nonterminal work remains, create or update one recurring Heartbeat targeting this same task. The task owns that Heartbeat for its mission lifetime.
7. On each wake, resume the same unfinished slot with its exact `slot_target_remaining`; do not reset the count or treat candidate scarcity as completion. Record `not_due`/no-action/recovery only as an interim checkpoint, then keep or update the same timer.
8. At explicit stop, deadline, or verified lane completion, remove only its own Heartbeat and report locally.

## Independence Gates

- No coordinator task, coordinator registry, coordinator supervisor Heartbeat, callback contract, or centralized completion report.
- A worker never reads or sends messages to another Reddit task. It never checks for task collisions.
- A worker never changes another lane's tab, mission, timer, status, cadence, candidate history, or risk state.
- A fault in one lane affects only that lane. Other tasks continue without awareness or permission.
- A task may replace only its own malformed/misbound Heartbeat and must verify the replacement before retiring the old timer. It never replaces or revives a historical task.
- Temporary subagents may assist bounded read-only analysis but never own Chrome mutations, the lane, its Heartbeat, or user communication.

## User Priority And Recovery

The latest explicit user command controls lane, duration, count, target pool, language, intensity, and style. Defaults and historical warnings are advisory only. Current live subreddit rules and current platform state still gate the exact action.

Automatically recover stale tabs, dropped Chrome control, DNS/network/proxy/TLS errors, `ERR_BLOCKED_BY_CLIENT`, blank/loading pages, timed rate limits, candidate exhaustion, and route failures. Keep the lane's recurring Heartbeat active and retry on later wakes. Do not stop the mission because one candidate, subreddit, page, or wake failed.

Ask the user directly in the affected lane task only for a currently visible login/credential requirement, persistent CAPTCHA/challenge, account lock/suspension, required acknowledgement with no automatic path, or an exact user-required prohibited target with no authorized substitute. Do not return the issue to the launcher.

Pending-review own posts are deleted/withdrawn immediately, that subreddit is retired for the current account, and the post worker retargets without confirmation. Historical removals are ledger context, not mission-wide blockers.

## Output

Ordinary worker output uses three concise Chinese lines:

```text
本轮完成：<动作/链接，或具体无动作/恢复结果>。
下轮时间：<经验证的当地时间；终止则写“无”>。
下轮计划：<该 lane 下一项工作；风险仅写该 lane 当前真实风险>。
```

The launcher returns only setup/dispatch status, created lane titles, and this routing instruction using only tasks created in that dispatch:

```text
已启动：<created titles>。

后续请直接到对应任务操作：
- 评论、候选帖子互动：Reddit 评论台
- 主帖、版规和发帖候选：Reddit 发帖台
- Notifications、回复和后续互动：Reddit 跟进台
- 自然浏览/投票：随以上执行台读取内容时完成；纯浏览任务才单独创建 Reddit 浏览台
- 新开一轮或重新分配任务：回到 Reddit 分发台
```

Omit any execution route whose task was not created. Always retain the natural-browsing explanation and final launcher route. The launcher never aggregates later worker results.
