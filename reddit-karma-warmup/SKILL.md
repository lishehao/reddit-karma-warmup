---
name: reddit-karma-warmup
description: Run authorized Reddit research, browsing, native posts, comments, follow-up, and profile/community work through one persistent user-visible Reddit operating task and the user's logged-in Chrome. Use when a user asks to operate, warm up, publish to, research, or monitor a Reddit account or community.
---

# Reddit Community Operations

## Startup state machine

Treat an HTTPS install/upgrade request as the start of one intake flow:

1. Verify the raw/codeload source, manifest, installed tree, offline validator,
   current task, and required tools. If the staged release is newer and its
   schema/queue protocol is compatible, atomically hot-replace the complete
   local Skill by default and report `HOT_REPLACED` before `BOOTSTRAP_READY`;
   never merge trees or call a remote-newer install `NOOP`. An active mission stays pinned to its
   recorded protocol. Defer only for an unsettled mutation, incompatible
   schema/queue protocol, or `UNCERTAIN` runtime facts, recording
   `REMOTE_NEWER_DEFERRED` for the first safe release boundary. Do not open
   Chrome/Reddit, run research, or create a mission/queue/Heartbeat during this
   bootstrap step.
2. Ask exactly three startup questions from
   [startup intake](references/startup-intake.md): duration, one operating
   direction, and action scope. Do not ask for an account name or handle. The
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
   `current-task scope -> envelope -> technical live gates -> Heartbeat
   readback -> INITIAL packet`. The `INITIAL` packet is formal round one, not
   a preview or pre-filter, and it must do real mission work immediately. Do
   not wait for a second user message or the first Heartbeat.

Use the current task as the authority. Resolve the exact current Codex task ID
from the current task context before compiling anything. A
`<source_thread_id>` inside a delegated wrapper is provenance only; it is the
parent/creator task and MUST NOT be used as this task's owner ID. The queue
owner, mission owner, Heartbeat target, and finalization target must all equal
the exact current task ID. If the current ID cannot be resolved, stop before
queue bootstrap with `CURRENT_TASK_ID_UNAVAILABLE` rather than guessing.
Inspect only its own mission/queue and
its own Heartbeat when one already exists. Do not scan other tasks, other
Heartbeats, other environments, locks, or historical handoffs. If this task
has no mission yet, create its queue after the three answers; do not block on
an unrelated runtime. `scripts/runtime_fence.py` remains an explicit
diagnostic tool, not a startup-wide scan.

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

1. Resolve and record the exact current task ID (never the delegation
   `source_thread_id`), then compile one immutable envelope and queue, bind that
   exact task, rename
   it to `Reddit 运营台`, read it back, and record `presentation-promote`.
   Store the business goal, community scope, coverage budget, soft action
   threshold, action budget, truthful material references, and evidence/output
   targets. `high/low frequency` changes these profiles, not the timer.
2. Pass the neutral canary and establish the silent same-Chrome session gate
   once. Then create one stable 15-minute recurring Heartbeat through
   `operation_stop_at + cleanup-grace`, and persist/read back its exact ID,
   task, RRULE, next run, and proof. If the scheduler rejects an immediate
   `DTSTART`, retry once without `DTSTART`; if an `UNTIL` form reports no
   future occurrence, use one bounded `COUNT` fallback sized to the cleanup
   window and record its exact count/cutoff. Do not stop the mission after the
   first scheduler-tool timeout.
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
5. For comments/posts do a short research brief, then a small purpose-specific
   Web Search pass and the Chrome live gate. Use 2-4 queries for comments and
   4-8 for posts; add a query only when the selected target or a factual claim
   needs it. The only action gates are current rules/format, truthful content,
   current session/composer, duplicate/recent history, and one verified submit.
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
