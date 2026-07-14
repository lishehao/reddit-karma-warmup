# Runtime And Setup

Load only for install, upgrade, dependency preflight, or initial lane allocation.

## Launcher Identity

The first available presentation action after a setup/install command is to rename the current task `Reddit 启动台`. Do this before download, preflight, or explanation. Rename failure is presentation-only and never blocks setup.

`Reddit 启动台` is temporary and owns only installation plus read-only runtime checks. After every required preflight item passes, immediately rename this same task `Reddit 分发台` and pin the exact current task. The distribution task accepts repeated user-triggered account-scoped lane dispatch, keeps only an external account+lane task registry, never becomes `Reddit 主控台`, never owns recurring Heartbeats, and never supervises or receives callbacks from workers. Between user commands it remains pinned and idle.

## Runtime Requirements

- Codex Skill file access.
- Chrome Browser control using the user's existing Chrome login state. Do not substitute Computer Use, in-app Browser, Playwright, or another browser for Reddit mutations.
- The user is already logged in to the target Reddit account. Never handle credentials.
- Persistent task list/read/send/create plus archive-state support for lane reuse and replacement.
- Current-task exact ID plus rename/pin support for the persistent distribution entrypoint. Do not search by title to recover self identity.
- Automation/Heartbeat support for multi-round work. Each lane worker creates and owns its own timer after its immediate first slot.
- Local time, timezone, UTC offset, and UTC readback.

Python, Node.js, Git, GitHub CLI, package managers, macOS Screen Recording, System Audio Recording, Accessibility, databases, API keys, and external CLIs are not runtime dependencies. Release validators under `scripts/` are optional install helpers.

## Install And Upgrade

Use repository root `README.md` and the public HTTPS archive. Compare `manifest.json` versions numerically. Install a whole managed folder atomically; never merge old and new trees. Back up the previous folder. Same version plus different content is a conflict; older incoming versions do not downgrade without explicit instruction; failed validation rolls back.

## Read-Only Preflight

1. Connect/reconnect Chrome control.
2. Open Reddit read-only and confirm the visible account.
3. Confirm persistent task list/read/send/create, rename, and archive/unarchive capability without creating operation tasks yet.
4. Confirm recurring Heartbeat create/update/read/delete capability. Hidden `next_run_at` is `created_unreadable`, not failure.
5. Read real local time/timezone and UTC.

If a required item needs user repair, remain `Reddit 启动台` and request only that repair. On `继续`, recheck only missing items.

When healthy, load `account-direction.md` before switching to the distributor. Resolve the exact visible Reddit account's user-owned direction file under `${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/account-directions/`.

- Matching valid file: reuse it without confirmation.
- Missing/malformed/mismatched file: remain `Reddit 启动台`, show the one-time default direction prompt, and wait for `确认`, a modification, or `确认并开始`.
- Explicit direction in the setup command: treat it as confirmation, normalize and persist it without a redundant question.
- Persist atomically outside the managed Skill tree. Never store credentials or copy one account's direction to another account automatically.

After direction resolution, rename the same task `Reddit 分发台`, pin that exact task, and ask for the operation only when the user's confirmation did not already include `开始` and the setup command did not already specify one. `确认并开始` dispatches standard intensity, mixed style, and three hours immediately. Rename or pin failure is presentation-only and does not block dispatch; report the missing presentation action once without searching for another task.

Keep the account-keyed lane registry outside the managed Skill tree at `${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/lane-registry/<username>.json`. Upgrades preserve it. It contains only canonical lane names, exact task IDs, titles, and last successful delivery metadata; never credentials, Reddit content, Heartbeat IDs, or worker status.

```text
建议账号方向：移动产品、3D/AR、游戏与 UGC、摄影与地点体验、创作工具。它是宽口径兴趣范围，不是虚构身份；单轮运营只需从中选一个重点。

请回复“确认”，或直接告诉我需要增加/删除的方向；回复“确认并开始”会保存后立即按默认 3 小时运营。
```

After confirmation and distributor transition, use:

```text
状态健康。当前账号：u/name。

账号方向已确认：<3-5 个兴趣支柱>。

当前任务已切换为 Reddit 分发台。

分发台已置顶；后续新一轮运营都从这里分配。

你可以指定评论、发帖、跟进、纯浏览/投票、时长、强度和风格；暂时没想法就回复“开始”。
```
