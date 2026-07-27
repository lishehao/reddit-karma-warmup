---
name: reddit-karma-warmup
description: Run authorized Reddit research, browsing, native posts, comments, follow-up, and profile/community work through one persistent user-visible Reddit operating task and the user's logged-in Chrome. Use when a user asks to operate, warm up, publish to, research, or monitor a Reddit account or community.
---

# Reddit Community Operations

## Default: one task, five internal units

Run one present, unarchived, user-visible `Reddit 运营台` for a mission. It owns
one durable mission record, one Heartbeat, one logged-in Chrome binding, and
one primary Reddit tab. Do not create unit tasks, a Chrome dispatcher, a lock
daemon, a callback tree, or a second Chrome owner.

| Unit | Owns | Never owns |
| --- | --- | --- |
| `browsing` | qualified reads; an explicitly authorized Upvote/Downvote | text publication, replies, profile/community changes |
| `comments` | candidate research and proactive comments | vote controls, posts, inbound replies, profile/community changes |
| `posts` | community audit, native post research and publication | vote controls, comments, inbound replies, profile/community changes |
| `follow-up` | known post/comment chains, notifications, and explicitly authorized replies | vote controls, unrelated discovery, new posts, profile/community changes |
| `presence` | explicitly authorized truthful profile, membership, flair, or tag changes | vote controls, text publication, replies |

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
   Bind it to the exact current task ID before Chrome work.
2. Run a neutral HTTPS canary, then create or claim one dedicated Reddit tab.
3. Create one stable 15-minute recurring mission Heartbeat only while unfinished
   work remains. Align normal unit rechecks to that grid. A trigger within ±5
   minutes is ordinary; later triggers record the delay and recompute from
   actual time without catch-up. A wake with nothing due is a fast NOOP: do not
   open Chrome or rewrite the timer. Never use a one-shot self-rescheduling
   timer or phase-switching timer updates.
4. At each wake decide `RUN`, `WATCH`, `SKIP`, or `DEFER` for every due enabled
   unit. Run at most one Chrome packet and one public action in that wake.
5. For `comments` or `posts`, complete:
   `research brief -> purpose-labelled query plan -> evidence synthesis -> Chrome live gate`.
   Use 4–6 distinct Web Search questions for a comment candidate pack and 8–12
   for a post candidate pack. Add an exact final query for the selected item and
   a source/objection query whenever the intended text contains a factual claim.
6. Before each public action persist a deterministic `MUTATION_INTENT` /
   `action_key`. Submit once. If acknowledgement or verification is uncertain,
   freeze that exact key permanently and do not reopen or retry it.
7. At completion or deadline, settle all boundaries, release only agent-owned
   tabs, delete the mission Heartbeat, and retire the queue. Keep the visible
   `Reddit 运营台` available for a future mission.

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
| numeric defaults or script configuration | [operation defaults](references/operation-defaults.json) |

Do not load historical lane, dispatcher, worker, callback, catalog-snapshot, or
legacy migration documents: they are not part of this production Skill.

## Compact receipt

```text
本轮完成：<完成/暂停/阻塞的单元、有效阅读、已验证动作>。
下轮时间：<当地时间与 UTC；终止则“无（Heartbeat 已删除）”>。
下轮计划：<下一个单元或恢复动作，以及真实风险>。
```
