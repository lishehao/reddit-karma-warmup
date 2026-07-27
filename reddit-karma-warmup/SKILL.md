---
name: reddit-karma-warmup
description: Run authorized Reddit research, browsing, native posts, comments, follow-up, and profile/community work through one persistent user-visible Reddit operating task and the user's logged-in Chrome. Use when a user asks to operate, warm up, publish to, research, or monitor a Reddit account or community.
---

# Reddit Community Operations

## Bootstrap-only requests

If the user asks to install/upgrade from the HTTPS README and says not to enter
target mode, do only bootstrap. Verify raw/codeload origin, package layout,
manifest, offline validator, installed tree, current-task presence, and required
tool availability. Report `BOOTSTRAP_READY` and wait for a later direction,
duration, account, and explicit action authority. Do not open Chrome or Reddit,
run Web Search/API, create a mission envelope/queue/Heartbeat, or create unit
tasks in this phase.

## Default: one task, five internal units

Run one present, unarchived, user-visible `Reddit 运营台` for a mission. It owns
one durable mission record, one Heartbeat, one logged-in Chrome binding, and
one primary Reddit tab. Do not create unit tasks, a Chrome dispatcher, a lock
daemon, a callback tree, or a second Chrome owner.

| Unit | Owns | Never owns |
| --- | --- | --- |
| `browsing` | qualified reads and candidate packs; an explicitly authorized Upvote/Downvote | text publication, replies, profile/community changes |
| `comments` | consume a candidate pack; research and proactive comments | vote controls, posts, inbound replies, profile/community changes |
| `posts` | consume a community/candidate pack plus truthful material; native publication | vote controls, comments, inbound replies, profile/community changes |
| `follow-up` | consume a verified own permalink; notifications and explicitly authorized replies | vote controls, unrelated discovery, new posts, profile/community changes |
| `presence` | an explicitly authorized, concrete truthful profile/membership/flair/tag change | vote controls, text publication, replies |

The units are policy boundaries inside one task, not lanes or threads. Default
authority is research-only. Votes are disabled unless the mission explicitly
authorizes `browsing` with `VOTE_AUTHORIZED`; every other unit has vote cap zero
and must not inspect a vote locator.

## Surface contract

Use each surface only for the work it can prove.

| Surface | Allowed use | Never use it for |
| --- | --- | --- |
| Built-in Web Search | broad current discovery, terminology, primary sources, duplicate/FAQ risk | current Reddit permissions, account state, composer state, action proof |
| Official Reddit API via `scripts/community_index.py` | optional GET-only public index: community metadata, rules, and up to three hot-item pointers | content browsing, account endpoints, any Reddit write, a Chrome-failure fallback, publishing permission |
| Logged-in Chrome | every actual Reddit read, current community context/rules, account gate, composer, submit/reply/vote, and result verification | parallel multi-task control, evasion or fake-human techniques |

API is optional: use it during bootstrap or community expansion only when the
official OAuth token and truthful User-Agent are configured. Missing credentials
are normal; continue with Web Search plus Chrome. API output is an index, not a
publish gate. TikHub is not part of the default path.

Use Old Reddit first for ordinary text communities; make one semantic current-
Reddit fallback only when the required live capability is unavailable. Keep the
same account and primary tab. A content-channel timeout is
`CHROME_CONTENT_CHANNEL_TIMEOUT`, not a browser disconnect, missing tab, or
account risk.

## Required mission sequence

1. Compile one immutable mission envelope and bootstrap its single-owner queue.
   Bind it to the exact current task ID and use its unique `mission_id` as the
   queue scope before Chrome work. Include a business
   goal, community scope, coverage budget, soft action threshold, action
   budget, truthful material references, and evidence/output targets. Treat
   “high/low frequency” as a profile shorthand, never as a timer change.
2. Run a neutral HTTPS canary, then create or claim one dedicated Reddit tab.
3. Create one stable 15-minute recurring mission Heartbeat only while unfinished
   work remains, ending at `operation_stop_at + cleanup-grace`. Persist and read
   back its exact automation ID, target task, RRULE, `UNTIL`, next run, and proof;
   refresh that receipt after every completed wake. Align normal unit rechecks to
   that grid. A trigger within ±5 minutes is ordinary; earlier/later triggers
   retain their signed delay and never cause catch-up. A wake with nothing due is
   an atomic fast NOOP: do not open Chrome or rewrite the timer. Never use a
   one-shot self-rescheduling timer or phase-switching timer updates.
4. At each wake decide `RUN`, `WATCH`, `SKIP`, or `DEFER` for every due enabled
   unit. Run at most one Chrome packet and one public action in that wake.
   Record both the packet outcome and the unit objective state. `COMPLETED`
   only means that bounded packet ended; it never proves a public action or
   closes the objective.
5. Link units only through recorded evidence:
   `browsing candidate pack -> comments/posts ACTION_ELIGIBLE` and
   `verified own permalink -> follow-up ACTION_ELIGIBLE`. Do not poll a
   follow-up unit without a verified own permalink or a presence unit without a
   concrete requested change. Park `MATERIAL_REQUIRED`, `RULE_BLOCKED`,
   `SUBMISSION_UNCERTAIN`, and `NOT_APPLICABLE` units until a mission revision
   or fresh upstream evidence explicitly re-arms them.
   When the mission goal includes public action, an `ACTION_ELIGIBLE` unit
   outranks more exploratory browsing. Do not keep scanning the same
   communities after a passing route and truthful material are ready.
6. For `comments` or `posts`, complete:
   `research brief -> purpose-labelled query plan -> evidence synthesis -> Chrome live gate`.
   Use 4–6 distinct Web Search questions for a comment candidate pack and 8–12
   for a post candidate pack. Add an exact final query for the selected item and
   a source/objection query whenever the intended text contains a factual claim.
7. Before each public action persist a deterministic `MUTATION_INTENT` /
   `action_key`. Submit once. If acknowledgement or verification is uncertain,
   freeze that exact key permanently and do not reopen or retry it.
8. At completion or deadline, stop Reddit work and enter `FINALIZE_ONLY`.
   Recover or freeze any stale boundary first, then release only agent-owned
   tabs, delete the exact Heartbeat with proof, and retire the queue. Keep the
   visible `Reddit 运营台` available for a future mission.

Hard compliance and truthful evidence decide whether an action is possible.
Content quality is a secondary ranking aid, never a reason to bypass a current
rule or invent a project, metric, link, experience, or claim.

## Load only what the current decision needs

| Situation | Required reference |
| --- | --- |
| bootstrap, mission revision, timer, recovery, retirement | [single-owner runtime](references/single-owner-runtime.md) |
| Web Search, public API index, community shortlist, candidate evidence | [research and community index](references/research-and-community-index.md) |
| Chrome setup, surface routing, read/action boundaries, timeout recovery | [Chrome and actions](references/chrome-and-actions.md) |
| selected `browsing`, `comments`, `posts`, `follow-up`, or `presence` unit | [unit guides](references/unit-guides.md) |
| business goal, coverage, threshold, KPI, or community-scope choice | [mission goals and profiles](references/mission-goals-and-profiles.md) |
| numeric defaults or script configuration | [operation defaults](references/operation-defaults.json) |

Do not load historical lane, dispatcher, worker, callback, catalog-snapshot, or
legacy migration documents: they are not part of this production Skill.

## Compact receipt

```text
本轮完成：<完成/暂停/阻塞的单元、有效阅读、已验证动作>。
下轮时间：<当地时间与 UTC；终止则“无（Heartbeat 已删除）”>。
下轮计划：<下一个单元或恢复动作，以及真实风险>。
```
