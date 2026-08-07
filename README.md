# Reddit Karma Warmup

Protocol version: `2026.08.07.6`

This repository contains one production Skill: `reddit-karma-warmup/`.

## First-use prompt

```text
请通过 HTTPS 读取并遵循 https://raw.githubusercontent.com/lishehao/reddit-karma-warmup/main/README.md，安装或升级 reddit-karma-warmup，完成预检；若 Prompt 没有给出完整目标帖子、动作和时长，再一次性询问启动问题，随后在同一任务中立即开始第一轮正式运营。
```

## Startup flow

The initial message performs installation/upgrade and local preflight only,
reports `BOOTSTRAP_READY`, then uses one of two intake paths. A complete direct
target assignment (target Reddit post URLs, allowed units, and duration) skips
the form and starts the first formal round in the same task. Otherwise ask
exactly four questions at once:

1. **运行多久？** `2 小时 / 4 小时 / 8 小时`，或明确的自定义时长。
2. **这轮想围绕什么方向或哪些社区运营？**
   可选：`社交与社区 / 个人创作与独立项目 / 3D/游戏/共创`，也可自由描述。
3. **这轮希望做到哪一步？** `模拟浏览 / 参与讨论 / 全面推进`。
4. **互动节奏希望怎样？** `低 / 标准 / 高`。

Do not ask for an account name or handle. The logged-in Chrome session is the
internal source of truth; read it silently once at startup and only recheck it
after a tab rebind, login change, recovery, or immediately before a mutation.
Use the interactive form once without `autoResolutionMs`. If it is unanswered,
partial, dismissed, or expires, list all four questions in a normal text
response and remain `WAITING_FOR_STARTUP_INPUT`; never infer defaults.

When the four answers or a complete direct target assignment are available,
start in the same task turn:

`current-task scope -> rename/pin current task -> mission envelope -> one Chrome/session gate -> formal INITIAL round -> advisory Heartbeat`

Rename the current task to `Reddit 运营台`, pin it, and read back when supported; presentation failure is non-blocking. The INITIAL round performs real work immediately, is not a preview or pre-filter, and does not wait for “继续” or the first Heartbeat. Heartbeat is a continuation aid; unavailable creation/readback is retried without stopping current-task work. Delivery is advisory: ±10 minutes is ordinary, and a late trigger runs one currently due unit without replaying missed work.

Normal runtime receipts use short opaque evidence tokens; SHA-256 is not required for each wake, Chrome read, or action receipt. Envelope re-hashing is diagnostic-only (`REDDIT_STRICT_INTEGRITY=1`); normal operation trusts the compiled envelope and checks task/scope consistency. Chrome calls must carry an explicit 120-second outer budget at the actual call site (not only in the ledger); await `Script running` instead of reissuing it, and claim a visible user tab before session-bound Reddit work.

## Installation contract

1. Fetch this README and the GitHub codeload ZIP over HTTPS.
2. Validate the ZIP layout and `reddit-karma-warmup/manifest.json`.
3. Run `scripts/validate_single_owner_v2_contract.py` in the staged tree.
4. Run `scripts/resolve_remote_sync.py --apply` against the managed local
   Skill. Any compatible tree difference is atomically applied, including
   same-version drift; identical content is `NOOP_ALREADY_SYNCED`, and an older
   remote is never an implicit downgrade. Read back the installed manifest/tree
   and rerun the validator before reporting `BOOTSTRAP_READY`.
5. An active runtime may remain on its pinned protocol while a compatible Skill
   is hot-replaced. Defer only for an incompatible schema/queue protocol, an
   unsettled mutation, or `UNCERTAIN` runtime facts; record
   `REMOTE_NEWER_DEFERRED`. Stale JSON text or `chrome_release=PENDING` alone
   is not an active fence.

During installation and intake, do not open Chrome/Reddit, run research, or
create a mission, queue, or Heartbeat. Those begin only after the four answers
or a complete direct target assignment are available. An incomplete direct
assignment gets one concise text reminder; do not invent missing targets.

## Runtime contract

- One present Reddit operating task owns all five internal units, one queue, one
  Chrome binding/tab, and an advisory 15-minute Heartbeat when available.
- The owner is the exact current task ID. A delegated wrapper's
  `source_thread_id` is creator provenance, never the execution task owner. Use
  the current task context directly; do not scan other tasks to resolve it.
- Startup trusts only this task's own mission, queue, and Heartbeat. Unrelated
  tasks, Heartbeats, environments, locks, and handoffs are not scanned.
- Built-in Web Search handles broad research; the optional official Reddit API is GET-only public indexing; logged-in Chrome performs every real Reddit read and interactive action.
- `r/saas` is globally excluded: discovery, API indexing, direct targets, and all browser actions skip or reject it.
- Voting is removed: no vote controls or mutations; compatibility is always
  `vote_policy=DISABLED`.
- Mission compilation requests `gpt-5.6-luna` with `xhigh` reasoning when the host supports it. Public writing defaults to short, conversational, varied text; markers are optional, comments normally stay within 5–50 words (70 only for explicitly detailed feedback), and posts within 40–120 words. Before each draft, read the bounded per-account recent-public-content library and rewrite exact or template-similar text. In discover/expandable scope, cover four or five distinct communities before repeating one; use recovery -> follow-up -> comments -> posts -> presence -> browsing priority; this is a routing target, not a filler quota. Rotate openings and rhetorical moves without manufacturing typos, repeated catchphrases, or personal facts.
- When comments/posts/follow-up/presence are authorized, `INITIAL` and each
  formal round are action-first: one Chrome packet may submit up to two distinct
  comment/post actions, or batch up to five verified follow-ups with a separate
  hourly cap that does not consume the new comment/post/presence action cap.
  Active missions re-arm verified action lanes on later wakes; browsing-only missions remain research-only.
- In `全面推进`, follow-up sweeps the user's own posts/comments,
  notifications, and known permalinks independent of business direction; it handles every eligible unanswered/new-reply conversation and carries the remainder to the next wake.
  It also reviews own profile posts; score `<= -2` uses hide-first/delete-fallback
  cleanup, with ownership and post-state verification.
- Only current task scope, readable Chrome, and action-type gates are hard gates.
  Comments use target/context fit, a basic current rule check, composer state,
  and one verified submit; posts retain the fuller rule, truth, duplicate, and
  format review. Titles, scheduler readback, stale metadata, and auxiliary
  probes are observability, not startup blockers.
- Candidate evidence moves atomically from browsing to comments/posts; a
  verified own permalink can arm follow-up. One rejected candidate returns to
  browsing instead of blocking the whole mission.
- Every mutation has a persisted deterministic action key, one submission, and
  separate verification; if a completed submit has no UI echo, allow one
  same-target refresh/read only; an uncertain key stays frozen, never retried.
- Heartbeat deliveries within ±10 minutes are normal. A late wake runs one
  currently due unit without replaying missed work. At the deadline, stop
  Reddit work, release owned tabs, delete the exact Heartbeat, and retire the
  queue.
Full operational rules live in the Skill's routed references; this README is only the install and startup contract.
## Release rule
Publish updates directly to GitHub `main`: bump the version, run validators, build a ZIP, verify public codeload/ZIP, then perform compatible atomic hot replacement. Only incompatible or uncertain active-runtime state may defer it.
