# Runtime And Setup

Load only for install, upgrade, dependency preflight, or initial lane allocation.

## Launcher Identity

The first available presentation action after a setup/install command is to rename the current task `Reddit 启动台`. Do this before download, preflight, or explanation. Rename failure is presentation-only and never blocks setup.

`Reddit 启动台` is temporary and owns only installation plus read-only runtime checks. After every required preflight item passes, immediately rename this same task `Reddit 分发台` and pin the exact current task. The distribution task accepts repeated user-triggered fresh lane dispatch, never becomes `Reddit 主控台`, never owns recurring Heartbeats, and never supervises or receives callbacks from workers. Between user commands it remains pinned, stateless, and idle.

## Runtime Requirements

- Codex Skill file access.
- Chrome Browser control using the user's existing Chrome login state. Do not substitute Computer Use, in-app Browser, Playwright, or another browser for Reddit mutations.
- The user is already logged in to the target Reddit account. Never handle credentials.
- Persistent task create/send support for every fresh dispatch.
- Current-task exact ID plus rename/pin support for the persistent distribution entrypoint. Do not search by title to recover self identity.
- Automation/Heartbeat support for multi-round work. Each lane worker creates and owns its own timer after its immediate first slot.
- Local time, timezone, UTC offset, and UTC readback.

Python, Node.js, Git, GitHub CLI, package managers, macOS Screen Recording, System Audio Recording, Accessibility, databases, API keys, and external CLIs are not runtime dependencies. Release validators under `scripts/` are optional install helpers.

## Install And Upgrade

Use repository root `README.md` and the public HTTPS archive. Compare `manifest.json` versions numerically. Install a whole managed folder atomically; never merge old and new trees. Back up the previous folder. Same version plus different content is a conflict; older incoming versions do not downgrade without explicit instruction; failed validation rolls back.

## Read-Only Preflight

1. Connect/reconnect Chrome control.
2. Open Reddit read-only and confirm the visible account.
3. Confirm persistent task create/read/send capability without creating operation tasks yet.
4. Confirm recurring Heartbeat create/update/read/delete capability. Hidden `next_run_at` is `created_unreadable`, not failure.
5. Read real local time/timezone and UTC.

If a required item needs user repair, remain `Reddit 启动台` and request only that repair. On `继续`, recheck only missing items.

When healthy, rename the same task `Reddit 分发台`, pin that exact task, then load `account-direction.md`. Present one broad truthful account direction together with the operation question. The direction prompt is non-blocking: if the user replies `开始`, accept the default direction plus standard intensity, mixed style, and three hours, then dispatch immediately. If the setup command already includes an operation, resolve an explicit or default direction, report it briefly, and dispatch without asking again. Rename or pin failure is presentation-only and does not block dispatch; report the missing presentation action once without searching for another task.

```text
状态健康。当前账号：u/name。

当前任务已切换为 Reddit 分发台。

分发台已置顶；后续新一轮运营都从这里分配。

建议账号方向：移动产品、3D/AR、游戏与 UGC、摄影与地点体验、创作工具。它是宽口径兴趣范围，不是虚构身份；单轮运营只需从中选一个重点。

你可以直接修改这个方向，也可以指定评论、发帖、跟进、纯浏览/投票、时长、强度和风格。暂时没想法就回复“开始”，我会按默认方向创建独立的评论台、发帖台和跟进台；它们会在本来就读到的内容上自然判断是否投票。纯浏览台仅在你明确要求时创建。
```
