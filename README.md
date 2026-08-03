# Reddit Karma Warmup

Protocol version: `2026.08.04.1`

This repository contains one production Skill: `reddit-karma-warmup/`.

## First-use prompt

```text
请通过 HTTPS 读取并遵循 https://raw.githubusercontent.com/lishehao/reddit-karma-warmup/main/README.md，安装或升级 reddit-karma-warmup，完成预检并一次性询问启动问题；收到完整回答后，在同一任务中立即开始第一轮正式运营。
```

## Startup flow

The initial message performs installation/upgrade and local preflight only,
reports `BOOTSTRAP_READY`, then asks exactly three questions at once:

1. **运行多久？** `2 小时 / 4 小时 / 8 小时`，或明确的自定义时长。
2. **这轮想围绕什么方向或哪些社区运营？**
   可选：`社交与社区 / 个人创作与独立项目 / 3D/游戏/共创`，也可自由描述。
3. **这轮希望做到哪一步？** `模拟浏览 / 参与讨论 / 全面推进`。

Do not ask for an account name or handle. The logged-in Chrome session is the
internal source of truth; read it silently once at startup and only recheck it
after a tab rebind, login change, recovery, or immediately before a mutation.
Use the interactive form once without `autoResolutionMs`. If it is unanswered,
partial, dismissed, or expires, list all three questions in a normal text
response and remain `WAITING_FOR_STARTUP_INPUT`; never infer defaults.

When all three answers are complete, start in the same task turn:

`current-task scope -> mission envelope -> one Chrome/session gate -> formal
INITIAL round -> advisory Heartbeat`

The INITIAL round performs real work immediately. It is not a preview or
pre-filter and does not wait for another “继续” or for the first Heartbeat.
Heartbeat is a continuation aid, not a prerequisite for the first round. If
creation or readback is unavailable, record it and retry in the background
without stopping current-task work.

Normal runtime receipts use short opaque evidence tokens; SHA-256 is reserved
for package/manifest or mission-envelope integrity checks and is not required
for each wake, Chrome read, or action receipt.

## Installation contract

1. Fetch this README and the GitHub codeload ZIP over HTTPS.
2. Validate the ZIP layout and `reddit-karma-warmup/manifest.json`.
3. Run `scripts/validate_single_owner_v2_contract.py` in the staged tree.
4. Compare the staged manifest/tree with the managed local Skill. If the staged
   release is newer and compatible, atomically hot-replace the complete
   directory by default; never merge versions. Record `HOT_REPLACED`, not a
   false `NOOP`.
5. An active runtime may remain on its pinned protocol while a compatible Skill
   is hot-replaced. Defer only when the staged schema/queue protocol is
   incompatible, an in-flight mutation cannot be settled, or the runtime facts
   are `UNCERTAIN`; record `REMOTE_NEWER_DEFERRED` and apply the staged release
   at the first proven release boundary. Stale JSON text or
   `chrome_release=PENDING` alone is not an active fence.

During installation and intake, do not open Chrome/Reddit, run research, or
create a mission, queue, or Heartbeat. Those begin only after all three answers
are complete.

## Runtime contract

- One present Reddit operating task owns all five internal units, one queue, one
  Chrome binding/tab, and an advisory 15-minute Heartbeat when available.
- The owner is the exact current task ID. A delegated wrapper's
  `source_thread_id` is creator provenance, never the execution task owner. Use
  the current task context directly; do not scan other tasks to resolve it.
- Startup trusts only this task's own mission, queue, and Heartbeat. Unrelated
  tasks, Heartbeats, environments, locks, and handoffs are not scanned.
- Built-in Web Search handles broad research; the optional official Reddit API
  is GET-only public indexing; logged-in Chrome performs every real Reddit read
  and every interactive action.
- Only current task scope, a readable Chrome session, and public-action gates
  (current rules, truthful evidence, composer state, duplicate check, and
  independent verification) are hard gates. Titles, scheduler readback, stale
  metadata, and auxiliary probes are observability, not startup blockers.
- Candidate evidence moves atomically from browsing to comments/posts; a
  verified own permalink can arm follow-up. One rejected candidate returns to
  browsing instead of blocking the whole mission.
- Every mutation has a persisted deterministic action key, one submission, and
  separate verification. An uncertain exact key is frozen and never retried.
- Heartbeat deliveries within ±5 minutes are normal. A late wake runs one
  currently due unit without replaying missed work. At the deadline, stop
  Reddit work, release owned tabs, delete the exact Heartbeat, and retire the
  queue.

Full operational rules live in the Skill's routed references; this README is
only the install and startup contract.

## Release rule

Publish updates directly to GitHub `main`: bump the version, run validators,
build a ZIP, verify fresh public codeload and ZIP contents, then perform the
default compatible atomic hot replacement. Only incompatible or uncertain
active-runtime state may defer the local replacement.
