# Runtime And Setup

Load only for install, upgrade, dependency preflight, or initial lane allocation.

## Launcher Identity

The first available presentation action after a setup/install command is to rename the current task `Reddit 启动台`. Do this before download, preflight, or explanation. Rename failure is presentation-only and never blocks setup.

`Reddit 启动台` is temporary and owns only installation plus read-only runtime checks. After every required preflight item passes, immediately rename this same task `Reddit 分发台` and pin the exact current task. The distribution task accepts repeated user-triggered account-scoped lane dispatch, keeps only an external account+lane task registry, never becomes `Reddit 主控台`, never owns recurring Heartbeats, and never supervises or receives callbacks from workers. Between user commands it remains pinned and idle.

## Runtime Requirements

- Codex Skill file access.
- Chrome Browser control using the user's existing Chrome login state. Do not substitute Computer Use, in-app Browser, Playwright, or another browser for Reddit mutations.
- The user is already logged in to the target Reddit account. Never handle credentials.
- Persistent task list/read/send/create plus archive-state support for lane reuse and replacement. Host-aware task operations must preserve returned `host_id`; create must distinguish a ready `threadId` from a queued `clientThreadId`.
- Current-task exact ID plus rename/pin support for the persistent distribution entrypoint. Do not search by title to recover self identity.
- Automation/Heartbeat tool capability for multi-round work, including explicit `targetThreadId` and exact-automation target readback. Bootstrap checks the callable schema only; each lane worker performs the first real create/readback for its own mission after its immediate first slot.
- Local time, timezone, UTC offset, and UTC readback.

Python, Node.js, Git, GitHub CLI, package managers, macOS Screen Recording, System Audio Recording, Accessibility, databases, API keys, external CLIs, and the generic `thread-supervisor` Skill are not runtime dependencies. When `thread-supervisor` is installed, use its current generic tool semantics while retaining this Skill's Reddit-specific topology.

## Install And Upgrade

Use repository root `README.md` and the public HTTPS archive. Compare `manifest.json` versions numerically. Install a whole managed folder atomically; never merge old and new trees. Back up the previous folder. Same version plus different content is a conflict; older incoming versions do not downgrade without explicit instruction; failed validation rolls back.

## Read-Only Preflight

1. Connect/reconnect Chrome control.
2. Open Reddit read-only and confirm the visible account.
3. Confirm persistent task list/read/send/create, rename, and archive/unarchive capability without creating operation tasks yet. Confirm the create schema exposes returned identifier type and host-aware read/send fields when the host supports them.
4. Confirm from the available automation tool/schema that recurring Heartbeat create/update/read/delete, explicit `targetThreadId`, and exact-automation target readback are callable. Do not create, update, or delete a bootstrap test Heartbeat or smoke-probe automation. Hidden `next_run_at` is handled by the first real worker timer as `created_unreadable`; an unreadable target binding is not verified and cannot schedule continuation.
5. Read real local time/timezone and UTC.

If a required item needs user repair, remain `Reddit 启动台`, persist `bootstrap_state=BOOTSTRAP_REPAIR_REQUIRED`, and request only that repair. In this state, `继续` rechecks only the missing items and never dispatches an operation mission.

When healthy, load `account-direction.md` before switching to the distributor. Resolve the exact visible Reddit account's user-owned direction file under `${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/account-directions/`, but keep this preflight state internal.

- Matching valid file: reuse it silently as the fallback account portfolio; the bootstrap question still asks for this run's direction and duration.
- Missing/malformed/mismatched file: prepare the broad default silently. Persist the user's answer, or the default when the user explicitly chooses it.
- Explicit direction and duration in the setup command: normalize/persist the direction and dispatch immediately without a redundant question.
- Persist atomically outside the managed Skill tree. Never store credentials or copy one account's direction to another account automatically.

After successful preflight, rename the same task `Reddit 分发台` and pin that exact task. If the setup command did not already provide both direction and duration, persist `bootstrap_state=BOOTSTRAP_AWAITING_OPERATION`, emit only the Bootstrap Success Prompt below, and wait for one answer. Do not prepend or append version, install/NOOP, validator, account, schema, preflight, rename/pin, no-action, source-link, or probe details. Those remain internal unless one concrete failure requires user repair. Rename or pin failure is presentation degradation; report only that concrete issue instead of a success prompt.

The answer starts dispatch immediately. Direction-only answers use `3h`; duration-only answers use the matching saved direction or the broad default. Only while `bootstrap_state=BOOTSTRAP_AWAITING_OPERATION`, `继续`, `开始`, `默认`, or `没想法` means matching saved direction or broad default plus `3h`, and immediately dispatches the first comments + posts + follow-up missions. Never ask a second confirmation or a second operation question. Clear the Bootstrap state only after dispatch is attempted; a later bare `继续` in pinned idle must not duplicate the previous mission without a new pending request.

Keep the account-keyed lane registry outside the managed Skill tree at `${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/lane-registry/<username>.json`. Upgrades preserve it. It contains only canonical lane names, exact ready task IDs, optional host IDs, titles, and last successful delivery metadata; never queued client IDs, credentials, Reddit content, Heartbeat IDs, or worker status.

## Bootstrap Success Prompt

Use exactly this user-facing shape after a successful first Bootstrap:

```text
你希望这个 Reddit 账号往什么方向运营，先运营多久？

- 方向：指账号接下来主要参与的主题范围，例如移动产品、3D/AR、游戏与 UGC、摄影与地点体验。可以给 1–3 个相邻方向；没有想法就使用默认方向。
- 时长：指本轮自动运营持续多久。期间电脑需要保持开机且不要休眠，Chrome 保持登录，网络尽量稳定；关机、休眠、关闭 Chrome 或断网会影响后续轮次。

请直接回复，例如：`3D/AR、地点体验，先运营 3 小时。`
没有特别要求也可以回复：`继续`（按已有或默认方向运营 3 小时）。
```

`BOOTSTRAP_SUCCESS_OUTPUT_EXACT=true`. Successful Bootstrap output contains this prompt only. Internal proofs stay in local state and are available only when the user later asks for diagnostics.
