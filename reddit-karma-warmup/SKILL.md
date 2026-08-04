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
   `current-task scope -> envelope -> one Chrome/session gate -> INITIAL
   packet`. Rename the current task to `Reddit 运营台`, pin it, and read back when
   supported; presentation failure is non-blocking and retries next wake. The `INITIAL` packet is formal round one, not a preview or
   pre-filter, and it must do real mission work immediately. Heartbeat creation
   and readback are advisory continuation work; they must not block INITIAL.
   Do not wait for a second user message or the first Heartbeat.
Use the current task as the authority. Resolve the exact current Codex task ID
from the current task context before compiling anything. A
`<source_thread_id>` inside a delegated wrapper is provenance only; it is the
parent/creator task and MUST NOT be used as this task's owner ID. The queue
owner, mission owner, Heartbeat target, and finalization target must all equal
the exact current task ID. The current task context is the only identity
source. If the runtime exposes a parent/source ID instead of the current ID,
keep the source as provenance and use the task's own ID for queue/Heartbeat
fields; do not perform a cross-task search to resolve it.
Inspect only its own mission/queue and
its own Heartbeat when one already exists. Do not scan other tasks, other
Heartbeats, other environments, locks, or historical handoffs. If this task
has no mission yet, create its queue after the three answers; do not block on
an unrelated runtime. `scripts/runtime_fence.py` remains an explicit
diagnostic tool, not a startup-wide scan.

## One task, five internal units

Run one present Reddit operating task. It owns one mission record, one queue,
an advisory Heartbeat when available, one Chrome binding, and one primary
Reddit tab. Never create unit tasks, a browser dispatcher, a lock daemon, or a
second Chrome owner.

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
   `source_thread_id`), rename and pin that task as `Reddit 运营台`, then compile
   one immutable envelope and queue. Read back title/pin when supported; either presentation failure is non-blocking and retries next wake.
   Store the business goal, community scope, coverage budget, soft action
   threshold, action budget, truthful material references, and evidence/output
   targets. `high/low frequency` changes these profiles, not the timer.
2. Establish one readable same-Chrome session gate. Do not create a separate
   neutral canary tab just to prove the browser. Start INITIAL as soon as this
   gate passes. In parallel, make a best-effort 15-minute Heartbeat attempt;
   use the existing DTSTART/UNTIL/COUNT fallback once, record any failure, and
   retry later without blocking current-task work.
   The prompt carries only stable identity/boundaries and
   `runtime_protocol_version`; each wake reloads this installed Skill and queue.
3. Run the formal `INITIAL` packet immediately. Later wakes may record
   `heartbeat-observe` when available, then decide `RUN|WATCH|SKIP|DEFER` for
   due units. Run at most one unit, one Chrome packet, and one public action per
   wake. ±10 minutes is normal. A late wake runs one currently due unit; no
   catch-up means no replay. A fast NOOP is only for early/duplicate, recovery,
   or genuinely exhausted/parked work; scheduler uncertainty is not a reason
   to skip current-task work, and a missing observation is not a second gate.
4. Link work only through recorded evidence: browsing candidate pack -> atomic
   `handoff` to comments/posts, and verified own permalink -> follow-up. An
   `ACTION_ELIGIBLE` unit outranks more browsing. Reject one bad candidate with
   `candidate-reject`; do not turn it into mission-wide `RULE_BLOCKED` or
   `MATERIAL_REQUIRED`. A runtime read failure is `LIVE_GATE_UNVERIFIED`; the
   next wake must create/claim one fresh agent-owned tab and run one real content
   probe before continuing or yielding the same unit. URL-only checks/finalize
   do not count; retry later and never permanently park a due unit.
5. Comments use a fast path: read the target and nearby context, one basic
   current rule or fresh cache, and the visible composer; use zero Web Search
   queries unless a factual/technical/unfamiliar claim needs one. Same-target
   duplicate checking is enough. Posts keep the 4-8 query research pass and
   fuller rule, truth, duplicate, format, session, and submit gates.
6. Before every public action persist deterministic `MUTATION_INTENT` and
   `action_key`. Submit once and verify separately. Freeze uncertain exact keys
   permanently; never reopen or retry them. At completion/deadline enter
   `FINALIZE_ONLY`, release only owned tabs, delete the exact Heartbeat with
   proof, retire the queue, and keep the visible operating task available. Runtime receipt tokens are opaque; envelope re-hashing is diagnostic-only (`REDDIT_STRICT_INTEGRITY=1`).
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
