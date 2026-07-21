---
name: reddit-karma-warmup
description: Run authorized Reddit community operations through the user's logged-in Chrome session. Use for reusable account-scoped setup and lane dispatch, proactive comments, native posts, follow-up replies, explicit browsing and voting, profile/community presence, timed autonomous operation, or lane-local status and recovery.
---

# Reddit Community Operations

Use one reusable distributor plus independent account-scoped lane tasks. There is no persistent main coordinator, callback path, shared scheduler, or cross-lane runtime state.

## Five-Step Default Flow

| Step | Owner | Required result |
|-|-|-|
| `1 SETUP` | temporary `Reddit 启动台` | install/upgrade and read-only preflight |
| `2 READY` | same task renamed/pinned `Reddit 分发台` | ask once for direction + duration, or normalize supplied values |
| `3 DISPATCH` | `Reddit 分发台` | reuse exact healthy account+lane tasks, create only missing/unusable lanes, deliver complete missions |
| `4 EXECUTE` | independent lane tasks | start browser-backed work now; own one tab, checkpoint, Heartbeat, recovery, and report |
| `5 RETIRE OR REUSE` | each lane task | delete its own Heartbeat at mission terminal; retain task/history for a later new mission ID |

The generic `thread-supervisor` Skill is optional. When present, use its current host tool/identity semantics. `thread-supervision-runtime.md` remains authoritative for Reddit's independent no-callback topology.

## Route The Request

| Request | Load and act |
|-|-|
| install/setup/upgrade/explain | Rename current task `Reddit 启动台`; load `references/runtime-and-setup.md`, `references/reddit-surface-routing.md`, `references/chrome-atomic-command-runtime.md`, `references/model-runtime.md`, and `references/thread-supervision-runtime.md`. Load `references/chrome-network-recovery.md` only if Chrome preflight fails. |
| healthy Bootstrap answer or later dispatch in `Reddit 分发台` | Load `references/launcher-playbook.md`, `references/lane-action-ownership.md`, `references/default-operations-sop.md`, and `references/operation-defaults.json`; dispatch immediately. |
| named lane in an ordinary task | Rename to the stable lane title when possible; load the exact role pack below and execute now. |
| later command/status/pause/resume/stop inside a lane | Change only that lane mission and its own checkpoint/Heartbeat. |

After dispatch, the user speaks directly to the relevant lane task for in-progress work. The distributor accepts future dispatch commands but does not supervise between them.

## Canonical Defaults

`references/operation-defaults.json` is the machine-authoritative source for model fallback, duration, intensity targets, read targets, vote caps, pacing, Chrome recovery budgets, post unlock numbers, and ordinary voice density. Role files reference its fields rather than redefining them. Human-facing README summaries are non-authoritative and must pass the defaults-alignment validator.

Model preference is `gpt-5.6-terra/high -> gpt-5.6-luna/high -> gpt-5.5/high -> gpt-5.4/high`, selecting the first pair exposed by the destination host. An explicit user model request overrides the chain. A running healthy task is not recreated only to switch models, and a requested override is not treated as applied until actual runtime metadata confirms it.

The latest explicit user duration, count, lane, target pool, language, intensity, and style overrides ordinary defaults. Current live Reddit rules, organization denylist, account repair state, browsing-lane vote cap, and post unlock still gate the exact action.

For every numeric lane round, `qualified_read_target` is a hard completion objective separate from the text-action target. Only `Reddit 浏览台` may vote; its default is `vote_target_mode=opportunity` under a hard intensity cap, and only a user-supplied vote count creates a hard vote target. Comments, posts, follow-up, and presence always use `vote_policy=DISABLED_BY_LANE`, `vote_cap=0`, and no vote target.

## Role Packs

Every worker loads `references/orchestration-core.md`, `references/lane-action-ownership.md`, `references/reddit-surface-routing.md`, `references/lane-state-checkpoint.md`, `references/interaction-pacing.md`, `references/chrome-atomic-command-runtime.md`, `references/scheduler-and-heartbeats.md`, `references/risk-escalation.md`, `references/chrome-network-recovery.md`, `references/publish-consistency.md`, and `references/operation-defaults.json`.

| Role | Stable title | Additional required references | Excludes |
|-|-|-|-|
| comments | `Reddit 评论台` | `references/proactive-common.md`, `references/comments-playbook.md`, `references/outbound-copy-gate.md`, `references/reddit-us-voice-patterns.md` | posts, notifications, every Upvote/Downvote control |
| posts | `Reddit 发帖台` | `references/proactive-common.md`, `references/posts-playbook.md`, `references/community-selection-funnel.md`, `references/new-account-bootstrap.md`, exact `references/posting-account-gates-audit-2026-07-14.csv` rows, `references/outbound-copy-gate.md` | comments, notifications, every Upvote/Downvote control |
| follow-up | `Reddit 跟进台` | `references/followup-playbook.md`, `references/outbound-copy-gate.md`, `references/reddit-us-voice-patterns.md` | proactive discovery, new posts, every Upvote/Downvote control |
| browsing | `Reddit 浏览台` | `references/browse-vote-playbook.md` | text publishing, notifications, profile changes |
| presence | `Reddit 主页台` | `references/community-presence-playbook.md`, `references/account-direction.md` | outward content, notifications, votes |

A task never loads another lane's playbook. Temporary subagents may assist bounded read-only analysis but never own Chrome mutations, the lane, its Heartbeat, or user communication.

## Community Data Routing

Load only filtered rows needed for the current account direction:

- discovery/taxonomy: `references/subreddit-catalog-taxonomy.md`, `references/subreddit-profile-index.csv`, `references/subreddit-catalog-expansion-2026-07-14.csv`, `references/reddit-community-search-snapshot-2026-07-14.json`
- action authority: `references/organization-community-denylist.md`, then `references/community-action-routing-overrides.md`, then current live rules
- evidence on demand: `references/community-live-audit-30-2026-07-13.md`, `references/community-expansion-pending-review-2026-07-13.md`, `references/community-action-expansion-public-audit-2026-07-13.md`, `references/posting-account-gates-audit-status.md`
- historical archive: exact rows only from `references/loci-subreddit-pool-v1.md`; never load the whole archive by default
- optional ranking/style: `references/operation-style-profiles.md`, `references/community-selection-funnel.md`

Discovery, traffic, survivor posts, and pending/public audits never grant publishing permission. Deny, retired, downgraded, `research_only`, unknown K1 post-gate, and current live-rule failures stay closed.

## Launcher Lifecycle

1. Rename current task `Reddit 启动台` before setup narration.
2. Run read-only Chrome/login, task-tool, automation-schema, local-time, and UTC preflight. Follow the installed Chrome Plugin's browser-binding/tab-binding model and the launcher sequence in `runtime-and-setup.md`; a healthy metadata channel is not proof that page content or the Reddit account is readable. Never create a probe Heartbeat.
3. Resolve account direction through `references/account-direction.md`. On success rename/pin the same task `Reddit 分发台`.
4. If direction or duration is missing, emit only the Bootstrap Success Prompt from `runtime-and-setup.md`. In `BOOTSTRAP_AWAITING_OPERATION`, bare `继续` means saved/default direction plus `3h` and immediately dispatches comments, posts, and follow-up. In repair state it only rechecks the failed dependency.
5. Resolve exact ready task IDs through the account-keyed registry. A queued `clientThreadId` is not ready. Send every mission with `worker_task_id=<exact destination task ID>`, new `mission_id`, first due now, static first-write phase, `heartbeat_owner=self`, checkpoint path, exact role pack, resolved targets, and actual model pair.
6. Full dispatch requires exact message acceptance by comments, posts, and follow-up. Report partial delivery honestly, then return pinned idle.

## Worker Lifecycle

1. Resolve `self_task_id` from exact current-task context and require it equals `worker_task_id`; accept only the canonical lane.
2. Load `lane-state-checkpoint.md`; create/recover the exact task-owned checkpoint and account+lane history before mutation.
3. Discover/reconnect Chrome; create or reclaim this task's one persistent dedicated Reddit primary tab. First creation is three atomic calls: create and persist the tab ID, navigate to the Old Reddit starting surface with `tab.goto(...)`, then read page state. Apply `reddit-surface-routing.md` for every later capability-specific route; Old is a starting preference, not a hard dependency. A pure metadata transaction uses the configured 30-second budget; every potentially blocking navigation, content read, interaction, or mutation uses the 120-second outer command contract. Page-side script navigation and another task's tab are forbidden.
4. Confirm account, local time, UTC, stop time, mission revision, remaining action/read counts, lane-owned action policy, and current timer ownership. Only browsing resolves a vote mode/cap; every other lane verifies `DISABLED_BY_LANE` and zero vote cap.
5. Apply denylist -> action override -> filtered data -> current live rules. Load only this lane's role pack.
6. Run `SCOPE -> RESTORE -> PROBE -> TAB -> HISTORY -> DISCOVER -> CHECK_A -> DRAFT -> CHECK_B -> ACT -> RECONCILE`. Persist prepared and final mutation certainty around the single click. For controlled text, resolve one fresh visible DOM node, preserve its `node_id` as a string, and separate focus, typing, and shadow-aware live-value readback. The submit wait, one click, and readback are three separate operations; never duplicate an uncertain mutation.
7. Continue until both the action objective and hard read objective pass, or a terminal condition occurs. Once a text target/cap is reached, finish required reading without another text mutation. Only browsing may assess optional vote opportunities; text lanes never inspect or touch vote controls.
8. If nonterminal work remains, create/update one recurring Heartbeat with explicit `targetThreadId=self_task_id`, carry checkpoint path and mission identity, read back the exact target, and keep the same logical timer through recoverable failures.
9. At explicit stop, deadline, or verified mission completion, delete only this task's Heartbeat, clear tab/timer/next-due checkpoint fields, close its tab, record retirement proof, then report terminal completion.

Ordinary native account posts in `POSTS_WORKER` do not use GPT Inf and must not be routed through `loci-prepare-reddit-post`. Comments and replies run `outbound-copy-gate.md` per item, remain short-first, and use high-frequency locally supported Reddit/internet markers across the session without a percentage quota or forced slang.

## Independence And Recovery

No coordinator task, coordinator registry, coordinator supervisor Heartbeat, callback contract, shared-tab check, sibling inspection, or centralized completion report. One lane fault affects only that lane.

Recover stale tabs, dropped Chrome control, DNS/network/proxy/TLS errors, blank/loading pages, `ERR_BLOCKED_BY_CLIENT`, candidate exhaustion, route failures, and malformed self-owned timer state locally. A Chrome command that succeeds slowly is not a failure; optional `Statsig`/`ab.chatgpt.com` timeout logs are not Reddit or account evidence. An action-induced control identity change is not page-control failure. A locator-only internal deadline while visible DOM and page projection remain healthy is `locator_backend_deadline`: switch that control to fresh DOM CUA once and do not repeat the locator. HTTP `429` ends the current wake, preserves checkpoint/mission/Heartbeat, and resumes at the later of the next normal round or displayed retry time.

Recovery is mission-persistent but wake-bounded: load `references/chrome-recovery-edge-cases.md` only after `references/chrome-network-recovery.md` classifies a failure, persist its fingerprint/backoff in the lane checkpoint, and retry through the same Heartbeat until recovery or a real terminal condition. Never use a later wake to replay an uncertain mutation.

Ask the user only in the affected lane for currently visible login/credentials, persistent CAPTCHA/challenge, account lock/suspension, required acknowledgement, or an exact prohibited target with no authorized substitute. Pending-review own posts are withdrawn immediately; retire that subreddit and continue elsewhere.

## Output

Workers use three concise Chinese lines:

```text
本轮完成：<动作/链接；动作进度；有效阅读进度；仅浏览台附 Upvote/Downvote 数量>。
下轮时间：<经验证的当地时间和 UTC；终止则写“无（Heartbeat 已删除）”>。
下轮计划：<该 lane 下一项工作和当前真实风险>。
```

After accepted first dispatch, the launcher reports that the three execution tasks received missions and reminds the user that future missions can be issued from the same `Reddit 分发台`. It never aggregates later worker results.
