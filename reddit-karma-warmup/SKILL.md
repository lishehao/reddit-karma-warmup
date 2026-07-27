---
name: reddit-karma-warmup
description: Run authorized Reddit community operations through the user's logged-in Chrome session. Use for Reddit account setup, community research, browsing, comments, native posts, follow-up replies, profile/community presence, and safe single-owner mission operations.
---

# Reddit Community Operations

## Default topology: one task, five units

The production default is one user-visible, pinned `Reddit 运营台`. It owns the
complete mission, one Chrome binding, one primary Reddit tab, its Heartbeat,
and a durable queue of five work units:

| Unit | May do | Never does |
| --- | --- | --- |
| `browsing` | authorized reading; only explicitly authorized Upvote/Downvote | text publishing, replies, profile/community changes |
| `comments` | candidate research and proactive comments | vote control inspection, posts, inbound replies, profile/community changes |
| `posts` | community audit, native post preparation and publication | vote control inspection, comments, inbound replies, profile/community changes |
| `follow-up` | known inbound-chain review and eligible replies | vote control inspection, proactive discovery, new posts, profile/community changes |
| `presence` | truthful profile, community membership, flair/tag work | vote control inspection, text publishing, replies |

Do not create one Chrome-owning task per unit. Do not create a Chrome dispatcher,
baton holder, cross-task lock daemon, sibling worker, or callback tree. The
`Reddit 运营台` serializes every focus, input, click, submit, verification,
tab-claim, tab-close, and finalization boundary itself. It may use at most two
agent-owned public read tabs only after a healthy canary; this never permits
parallel mutations or shared user tabs.

`execution_topology=legacy_multi_lane_compat` is an explicit migration-only
compatibility mode. Never select it from a broad or ordinary Reddit request.

## Non-negotiable invariants

1. Compile and hash one immutable mission envelope before Chrome work. The
   envelope names the exact account, duration, selected units, per-unit
   authority, vote policy, model request state, and source-prompt hash.
2. Default authority is research-only. A text publish, reply, profile/community
   change, or vote requires the matching explicit unit authorization **and** all
   current live Reddit/rule/account/submit gates. No target count forces an
   action.
   For posts, apply **hard compliance -> truthful minimum content floor ->
   secondary ranking**. A writing score may improve a compliant candidate but
   must not block an otherwise compliant, truthful native discussion.
3. Only `browsing` may inspect or operate Upvote/Downvote controls. Every other
   unit has `vote_policy=DISABLED_BY_LANE`, `vote_cap=0`, and never loads a vote
   locator.
4. Before an outward action, persist one deterministic `MUTATION_INTENT` /
   `action_key`. A timeout or ambiguous result freezes that exact key forever;
   do not duplicate an uncertain Reddit mutation, retry, reopen, or use another
   unit to test it.
5. A Chrome browser binding, tab metadata, page content channel, route, and
   account state are separate health layers. `openTabs`/claim/title success does
   not prove a readable page; content timeout is not a disconnection or account
   risk.
6. A Heartbeat belongs only to the single `Reddit 运营台`. Timing within the
   configured ±5-minute tolerance is ordinary; continue without repair or
   notification. Do not use `COUNT=1` self-rescheduling for a mission.
7. Prefer Luna/High for this user-authorized operating task when the host exposes
   a model request. Record requested, actual, and evidence state separately.
   Never create a duplicate task merely because model metadata is missing or a
   model change cannot be verified.

## Safe hot-plugging

All five units are hot-pluggable, but only at a **safe boundary**:

```text
no RUNNING unit
AND no open read batch
AND no browser boundary in flight
AND every uncertain mutation has a frozen exact action_key
AND mission is not retired
```

Use a new, fully hashed mission revision rather than editing the prior envelope.
`ADD`, `PAUSE`, `REMOVE`, `RESUME`, and a scoped authority/vote-policy change
create an append-only revision record. An authority increase still requires a
new direct user receipt; a hot-plug never manufactures permission.
An active unit must finish or yield first; a paused/removed unit retains history
and is never silently deleted. Resuming creates a fresh unit generation, not a
rewrite of old evidence. Read [single-owner runtime](references/single-owner-runtime.md)
and [one-prompt runtime](references/one-prompt-runtime.md) before applying a
revision.

## Progressive route

| Situation | Load now | Load only when needed |
| --- | --- | --- |
| install / first preflight | [single-owner runtime](references/single-owner-runtime.md), [model runtime](references/model-runtime.md), [operation defaults](references/operation-defaults.json) | [community audit pool](references/community-audit-pool.md) for local public-cache setup |
| every mission or revision | [single-owner runtime](references/single-owner-runtime.md), [unit ownership](references/lane-action-ownership.md), [Chrome atomic runtime](references/chrome-atomic-command-runtime.md) | [network recovery](references/chrome-network-recovery.md) only after a failure |
| browsing unit | [browse/vote playbook](references/browse-vote-playbook.md) | vote policy only when the envelope authorizes browsing votes |
| comments unit | [comments playbook](references/comments-playbook.md), [Web Search preflight](references/web-search-preflight.md) | [outbound copy gate](references/outbound-copy-gate.md) immediately before a draft/submission |
| posts unit | [posts playbook](references/posts-playbook.md), [post KPI](references/post-coverage-and-kpi.md), [Web Search preflight](references/web-search-preflight.md) | [selection funnel](references/community-selection-funnel.md), [copy gate](references/outbound-copy-gate.md) only when relevant |
| follow-up unit | [follow-up playbook](references/followup-playbook.md) | copy gate only for an eligible reply |
| presence unit | [presence playbook](references/community-presence-playbook.md), [account direction](references/account-direction.md) | no text-publishing or vote playbook |
| live rule/account/action issue | [risk escalation](references/risk-escalation.md) | [Chrome edge cases](references/chrome-recovery-edge-cases.md) only when classified |
| explicit legacy migration | [legacy multi-lane compatibility](references/thread-supervision-runtime.md) | never load for a default mission |

## Community evidence

Use the shared [community audit pool](references/community-audit-pool.md) for
public rule/metadata cache only. Filter `subreddit-profile-index.csv`, then
apply `organization-community-denylist.md` and
`community-action-routing-overrides.md`. Historical audits, traffic snapshots,
and API pointers are discovery evidence; never treat them as publishing
permission or load an archive by default. For a candidate expansion, use
[subreddit catalog](references/subreddit-catalog-taxonomy.md) and the
[selection funnel](references/community-selection-funnel.md) only for the
active comments/posts unit. Current Chrome rules and submit state remain final.

Web Search is mandatory before comment and post candidate narrowing:
`research_brief -> query_plan -> evidence_synthesis -> Chrome live gate`.
Built-in Web Search supplies discovery and factual research; logged-in Chrome is
the final authority for Reddit rules, eligibility, composer state, and action
success.

## Runtime sequence

```text
COMPILE ENVELOPE -> BOOTSTRAP QUEUE -> NEUTRAL CANARY ->
START ONE UNIT -> DISCOVER/QUALIFY -> [DRAFT] -> ACT/VERIFY ->
COMPLETE or YIELD -> NEXT UNIT -> RELEASE -> RETIRE
```

`YIELDED` is a same-mission recovery state. It blocks later queued units until
the same unit is resumed or an explicitly accepted safe-boundary revision pauses
or removes it. Do not create another task, reset its budget, or duplicate an
uncertain action.

## Output

```text
本轮完成：<已完成/暂停/阻塞的单元、有效阅读和已验证动作>。
下轮时间：<当地时间与 UTC；终止则“无（Heartbeat 已删除）”>。
下轮计划：<下一个队列单元或恢复动作，以及真实风险>。
```
