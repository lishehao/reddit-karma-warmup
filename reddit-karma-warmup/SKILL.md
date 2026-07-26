---
name: reddit-karma-warmup
description: Run authorized Reddit community operations through the user's logged-in Chrome session. Use for account-scoped setup and lane dispatch, proactive comments, native posts, follow-up replies, explicit browsing and voting, profile/community presence, or lane-local recovery.
---

# Reddit Community Operations

Use one reusable `Reddit 分发台` and independent account-scoped lane tasks. It
is not a central coordinator: after exact mission delivery it returns idle and
does not supervise workers, share a scheduler, or aggregate later results.

## Fixed identities

| Identity | Sole responsibility | Never does |
| --- | --- | --- |
| `Reddit 启动台 → Reddit 分发台` | read-only preflight; resolve present/unarchived lanes; deliver a new mission | browse or mutate Reddit after dispatch |
| `Reddit 评论台` | discover, read context, and publish proactive comments | posts, notifications, votes |
| `Reddit 发帖台` | scan eligible communities, verify rules, and publish native posts | comments, notifications, votes |
| `Reddit 跟进台` | read inbound/known chains and reply when warranted | proactive discovery, new posts, votes |
| `Reddit 浏览台` | read authorized surfaces and, only when explicitly authorized, vote | text publishing, notifications, profile work |
| `Reddit 主页台` | profile, Join/subscribe, and truthful Flair/tag maintenance | content publishing and votes |

`Reddit 启动台` becomes `Reddit 分发台` only after preflight. All other rows
are durable lane titles, not permissions inferred from a title. Exact task ID,
account, and mission identity control every action. No subagent owns a Chrome
mutation, a lane Heartbeat, or user communication.

## Non-negotiable rules

1. Load [lane action ownership](references/lane-action-ownership.md) before
   accepting a lane mission. Only `Reddit 浏览台` may inspect or operate
   Upvote/Downvote controls; every other lane has `vote_policy=DISABLED_BY_LANE`
   and `vote_cap=0`.
2. `operation-defaults.json` is the only numeric-default authority. The latest
   explicit user scope overrides defaults; current live Reddit rules, account
   state, and exact submit state still govern the action.
3. An archived task is never healthy/reusable. Reuse only an exact present,
   unarchived, account-matched task with a verified delivery receipt. Replace
   only after exact archived, missing, or permanent-delivery-rejection proof;
   `notLoaded`, empty, timeout, or unknown liveness blocks that lane without
   creating a duplicate.
4. Do not duplicate an uncertain Reddit mutation. Persist uncertainty and
   inspect the exact target once before considering any new action.
5. For posts, apply **hard compliance → truthful minimum content floor →
   secondary ranking**. A writing/engagement score may suggest a rewrite; it
   must not block an otherwise compliant, truthful native discussion.
6. Each lane owns only its own tab, checkpoint, Heartbeat, history, and report.
   Its tab must hold an active `chrome_tab_lease/v1`; it never reads, changes,
   or waits on a sibling lane. A short `chrome_control_slot/v1` serializes one
   shared Chrome boundary call at a time without transferring page ownership.

## Route and load progressively

| Situation | Load now | Load only when the condition occurs |
| --- | --- | --- |
| setup / dispatch | [launcher playbook](references/launcher-playbook.md), [model runtime](references/model-runtime.md), ownership, [operation defaults](references/operation-defaults.json) | [runtime setup](references/runtime-and-setup.md) for Chrome preflight; [thread runtime](references/thread-supervision-runtime.md) only for task create/reuse semantics |
| every lane slot | [orchestration core](references/orchestration-core.md), [checkpoint](references/lane-state-checkpoint.md), [Chrome atomic runtime](references/chrome-atomic-command-runtime.md), ownership | [surface routing](references/reddit-surface-routing.md) while selecting a surface; [scheduler](references/scheduler-and-heartbeats.md) only when work remains; [network recovery](references/chrome-network-recovery.md) only after a failure |
| comment lane | [comments playbook](references/comments-playbook.md), [Web Search preflight](references/web-search-preflight.md) | [outbound copy gate](references/outbound-copy-gate.md) and [US voice](references/reddit-us-voice-patterns.md) only before a draft/submission |
| posts lane | [posts playbook](references/posts-playbook.md), [post KPI](references/post-coverage-and-kpi.md), [Web Search preflight](references/web-search-preflight.md) | [selection funnel](references/community-selection-funnel.md) while widening; [new-account gate](references/new-account-bootstrap.md) only for K0/K1; copy gate only before drafting |
| follow-up lane | [follow-up playbook](references/followup-playbook.md) | copy gate only for a reply candidate |
| browsing lane | [browse/vote playbook](references/browse-vote-playbook.md) | no text-copy playbook |
| presence lane | [presence playbook](references/community-presence-playbook.md), [account direction](references/account-direction.md) | no publishing or vote playbook |
| catalog expansion / a blocked destination | [subreddit catalog](references/subreddit-catalog-taxonomy.md) | exact historical audit row only for the candidate being checked; it never grants permission |
| visible rate limit, removal, approval, or account warning | [risk escalation](references/risk-escalation.md) | [Chrome edge cases](references/chrome-recovery-edge-cases.md) only when the recovery classifier selects one |

Load [publish consistency](references/publish-consistency.md) only immediately
before an outward action. Load [interaction pacing](references/interaction-pacing.md)
only immediately before its measured pause/click. Load
[Chrome edge cases](references/chrome-recovery-edge-cases.md) only after the
network-recovery classifier selects an edge case. Do not preload all of these
documents "just in case."

## Community data

Use current live rules and submit state as final authority. Filter
`subreddit-profile-index.csv`, then apply `organization-community-denylist.md`
and `community-action-routing-overrides.md`. Historical audits, traffic
snapshots, and `loci-subreddit-pool-v1.md` are evidence lookup only: read an
exact row when needed, never load an archive by default, and never treat it as
publishing permission.

## One lane slot

```text
RESTORE → PROBE → [WEB RESEARCH: comment/post only] → TAB → DISCOVER → QUALIFY → [DRAFT] → ACT → VERIFY
→ RECONCILE → SCHEDULE or RETIRE
```

`DRAFT` exists only for a text action. First work begins in the current turn;
do not defer all discovery to a future Heartbeat. A nonterminal lane updates
one self-targeted recurring Heartbeat; a terminal lane deletes only its own
Heartbeat, releases only its own tab, and reports three concise Chinese lines.
Heartbeat timing within the configured ±5-minute tolerance is ordinary and
continues without repair or notification.

`WEB RESEARCH` uses the host's built-in Web Search before Chrome candidate
discovery and must produce `research_brief -> query_plan -> evidence_synthesis`
before any draft. It is mandatory for comment and post lanes, but it never
proves current Reddit rules, logged-in eligibility, composer state, or mutation
success; Chrome remains the final live authority for those facts.

## Output

```text
本轮完成：<本 lane 动作、进度、有效阅读；仅浏览台可含投票数量>。
下轮时间：<经验证的当地时间与 UTC；终止则“无（Heartbeat 已删除）”>。
下轮计划：<本 lane 下一项工作和真实风险>。
```
