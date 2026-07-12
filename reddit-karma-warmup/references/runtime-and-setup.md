# Runtime And Setup

Load only for install, upgrade, dependency preflight, or initial lane allocation.

## Launcher Identity

The first available presentation action after a setup/install command is to rename the current task `Reddit 启动台`. Do this before download, preflight, or explanation. Rename failure is presentation-only and never blocks setup.

`Reddit 启动台` owns installation, read-only runtime checks, and repeated user-triggered fresh lane dispatch. It never becomes `Reddit 主控台`, never owns recurring Heartbeats, and never supervises or receives callbacks from workers. Between user commands it remains stateless and idle.

## Runtime Requirements

- Codex Skill file access.
- Chrome Browser control using the user's existing Chrome login state. Do not substitute Computer Use, in-app Browser, Playwright, or another browser for Reddit mutations.
- The user is already logged in to the target Reddit account. Never handle credentials.
- Persistent task create/send support for every fresh dispatch.
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

When healthy, ask how to operate. If the user replies `开始`, default to standard intensity, mixed style, and three hours; dispatch the independent lane tasks immediately. Do not rename or promote the launcher.

```text
状态健康。当前账号：u/name。

你希望怎么运营？可以指定评论、发帖、跟进、自然浏览、时长、强度和风格。暂时没想法就回复“开始”，我会创建独立的评论台、发帖台、跟进台和浏览台；它们之后各自运行，你直接去对应任务继续沟通。
```
