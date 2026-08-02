---
name: reddit-karma-warmup
description: Run authorized Reddit research, browsing, native posts, comments, follow-up, and profile/community work through one persistent user-visible Reddit operating task and the user's logged-in Chrome. Use when a user asks to operate, warm up, publish to, research, or monitor a Reddit account or community.
---

# Reddit Community Operations

## Startup state machine

Treat an HTTPS install/upgrade request as the start of one intake flow:

1. Verify the raw/codeload source, manifest, installed tree, offline validator,
   current task, and required tools. Do not open Chrome/Reddit, run research, or
   create a mission/queue/Heartbeat during this bootstrap step. Report
   `BOOTSTRAP_READY`.
2. Ask exactly three startup questions from
   [startup intake](references/startup-intake.md): duration, one operating
   direction, and action scope. Never ask for an account name or handle. The
   logged-in Chrome session is read silently as an internal gate; it is not a
   startup answer and is not repeated in normal receipts. Use
   `request_user_input` at most once and omit `autoResolutionMs`. If the form
   is unanswered, partial, dismissed, or expires, send the prescribed normal
   text response listing all three questions. Remain
   `WAITING_FOR_STARTUP_INPUT`; silence never starts or cancels work.
3. Persist the three answers and run `scripts/compile_startup_intake.py`. Only
   `STARTUP_ANSWERS_COMPLETE` continues. One operating-direction answer is
   complete; do not ask separately for audience, topics, communities, links,
   account name, or materials.
4. In that same task turn run:
   `runtime fence -> envelope -> technical live gates -> Heartbeat readback ->
   INITIAL packet`. The `INITIAL` packet is formal round one, not a preview or
   pre-filter, and it must do real mission work immediately. Do not wait for a
   second user message or the first Heartbeat.

Before compiling a new mission, classify local runtime records with
`scripts/runtime_fence.py`. A stale `ACTIVE` word or
`chrome_release=PENDING` alone is not occupancy. Reconcile a proven
`STALE_RUNTIME` locally; only `ACTIVE_OWNER` or `UNCERTAIN` blocks startup.

## One task, five internal units

Run one present, unarchived, user-visible `Reddit 运营台`. It owns one mission
record, one queue, one Heartbeat, one Chrome binding, and one primary Reddit
tab. Never create unit tasks, a browser dispatcher, a lock daemon, or a second
Chrome owner.

| Unit | Owns | Never owns |
| --- | --- | --- |
| `browsing` | qualified reads, candidate packs, and explicitly authorized votes | publication, replies, profile changes |
| `comments` | candidate research and proactive comments | votes, posts, replies, profile changes |
| `posts` | rule-qualified native posts using truthful material | votes, comments, replies, profile changes |
| `follow-up` | verified own permalinks, notifications, and authorized replies | votes, unrelated discovery, new posts |
| `presence` | explicit truthful profile/community/flair changes | votes, publication, replies |

Default authority is research-only. Votes require explicit
`browsing=VOTE_AUTHORIZED`; every other unit has vote cap zero and must not
inspect vote controls.

## Surface contract

| Surface | Use | Never treat as |
| --- | --- | --- |
| Built-in Web Search | broad current discovery, terminology, primary sources, duplicate/FAQ risk | current Reddit permission or action proof |
| Official Reddit API via `scripts/community_index.py` | optional GET-only public community metadata, rules, and up to three hot pointers | browsing, account access, writes, or a Chrome fallback |
| Logged-in Chrome | every real Reddit read, live rule/session/composer gate, action, and verification | parallel task control or evasion |

Missing API credentials are normal. Start with Old Reddit for ordinary text
work and use one equivalent current-Reddit fallback only when the required live
capability is absent. A content timeout is
`CHROME_CONTENT_CHANNEL_TIMEOUT`, not a disconnect, missing tab, session risk,
or `RULE_BLOCKED`; follow [Chrome and actions](references/chrome-and-actions.md).

## Mission loop

1. Compile one immutable envelope and queue, bind the exact current task, rename
   it to `Reddit 运营台`, read it back, and record `presentation-promote`.
   Store the business goal, community scope, coverage budget, soft action
   threshold, action budget, truthful material references, and evidence/output
   targets. `high/low frequency` changes these profiles, not the timer.
2. Pass the neutral canary and establish the silent same-Chrome session gate
   once. Then create one stable 15-minute recurring Heartbeat through
   `operation_stop_at + cleanup-grace`,
   and persist/read back its exact ID, task, RRULE, `UNTIL`, next run, and proof.
   The prompt carries only stable identity/boundaries and
   `runtime_protocol_version`; each wake reloads this installed Skill and queue.
3. Run the formal `INITIAL` packet immediately. Every later wake first records
   `heartbeat-observe`, then decides `RUN|WATCH|SKIP|DEFER` for due units. Run at
   most one unit, one Chrome packet, and one public action per wake. ±5 minutes
   is normal. A late wake runs one currently due unit; no catch-up means no
   replay. A fast NOOP is only for early/duplicate, recovery, or genuinely
   exhausted/parked work.
4. Link work only through recorded evidence: browsing candidate pack -> atomic
   `handoff` to comments/posts, and verified own permalink -> follow-up. An
   `ACTION_ELIGIBLE` unit outranks more browsing. Reject one bad candidate with
   `candidate-reject`; do not turn it into mission-wide `RULE_BLOCKED` or
   `MATERIAL_REQUIRED`. A runtime read failure is `LIVE_GATE_UNVERIFIED`; yield
   the same unit and run `RECOVERY_FIRST` at the next verified Heartbeat.
5. For comments/posts perform
   `research brief -> labelled query plan -> evidence synthesis -> Chrome live
   gate`: 4-6 distinct Web Search questions for a comment pack and 8-12 for a
   post pack, plus exact-target and source/objection queries when factual claims
   require them. Rules, truthful evidence, duplicate state, session identity, composer,
   and submit state are hard gates; content quality only ranks passing routes.
6. Before every public action persist deterministic `MUTATION_INTENT` and
   `action_key`. Submit once and verify separately. Freeze uncertain exact keys
   permanently; never reopen or retry them. At completion/deadline enter
   `FINALIZE_ONLY`, release only owned tabs, delete the exact Heartbeat with
   proof, retire the queue, and keep the visible operating task available.

## Load only what the current decision needs

| Situation | Reference |
| --- | --- |
| intake | [startup intake](references/startup-intake.md) |
| mission, timer, recovery, retirement | [single-owner runtime](references/single-owner-runtime.md) |
| Web Search, API index, community/candidate evidence | [research and community index](references/research-and-community-index.md) |
| Chrome and action boundaries | [Chrome and actions](references/chrome-and-actions.md) |
| selected unit | [unit guides](references/unit-guides.md) |
| goal, KPI, coverage, threshold, scope | [mission goals and profiles](references/mission-goals-and-profiles.md) |
| numeric/script defaults | [operation defaults](references/operation-defaults.json) |

Do not load historical lane, dispatcher, worker, callback, or migration files.

## Compact receipt

```text
本轮完成：<完成/暂停/阻塞的单元、有效阅读、已验证动作>。
下轮时间：<当地时间与 UTC；终止则“无（Heartbeat 已删除）”>。
下轮计划：<下一个单元或恢复动作，以及真实风险>。
```
