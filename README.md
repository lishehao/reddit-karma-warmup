# Reddit Karma Warmup

Protocol version: `2026.07.30.3`

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

`runtime fence -> mission envelope -> Chrome/session gates -> recurring
Heartbeat readback -> formal INITIAL round`

The INITIAL round performs real work immediately. It is not a preview or
pre-filter and does not wait for another “继续” or for the first Heartbeat.
Heartbeat exists only for later continuation.

## Installation contract

1. Fetch this README and the GitHub codeload ZIP over HTTPS.
2. Validate the ZIP layout and `reddit-karma-warmup/manifest.json`.
3. Run `scripts/validate_single_owner_v2_contract.py` in the staged tree.
4. Compare the staged manifest/tree with the managed local Skill. Install the
   complete directory atomically; never merge versions.
5. If a verified active Reddit runtime exists, validate and stage the upgrade
   but defer local replacement until release. Stale JSON text or
   `chrome_release=PENDING` alone is not an active fence.

During installation and intake, do not open Chrome/Reddit, run research, or
create a mission, queue, or Heartbeat. Those begin only after all three answers
are complete.

## Runtime contract

- One present, unarchived `Reddit 运营台` owns all five internal units, one
  queue, one Chrome binding/tab, and one stable 15-minute Heartbeat.
- Built-in Web Search handles broad research; the optional official Reddit API
  is GET-only public indexing; logged-in Chrome performs every real Reddit read
  and every interactive action.
- Rules, truthful evidence, current session/composer state, duplicate checks,
  explicit authority, and independent verification are hard gates. Targets are
  planning signals, never forced-action quotas.
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
build a ZIP, verify fresh public codeload and ZIP contents, then upgrade the
local managed copy only when no active old-runtime fence exists.
