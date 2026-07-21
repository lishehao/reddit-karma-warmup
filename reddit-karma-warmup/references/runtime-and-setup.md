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
- A host-supported model pair selected from `operation-defaults.json`: prefer `gpt-5.6-terra/high`, then `gpt-5.6-luna/high`, then `gpt-5.5/high`, then `gpt-5.4/high`. Unsupported preferred models trigger fallback and never block Reddit operation.

Python, Node.js, Git, GitHub CLI, package managers, macOS Screen Recording, System Audio Recording, Accessibility, databases, API keys, external CLIs, and the generic `thread-supervisor` Skill are not runtime dependencies. When `thread-supervisor` is installed, use its current generic tool semantics while retaining this Skill's Reddit-specific topology.

## Install And Upgrade

Use repository root `README.md` and the public HTTPS archive. Compare `manifest.json` versions numerically. Install a whole managed folder atomically; never merge old and new trees. Back up the previous folder. Same version plus different content is a conflict; older incoming versions do not downgrade without explicit instruction; failed validation rolls back. Preserve all user-owned runtime data outside the managed Skill tree, including `account-directions/`, `lane-registry/`, `lane-state/`, and `lane-history/`.

## Read-Only Preflight

Before the first Chrome call, load `chrome-atomic-command-runtime.md` and follow
the installed Chrome Plugin as the transport authority. Initialize its browser
runtime once per fresh Node session, reuse an existing `agent.browsers` runtime,
select the explicit Chrome extension browser once, read the full Chrome
documentation once, and reuse that browser binding. A new turn, a stale
tab, an empty tab list, or a page timeout does not by itself justify selecting
Chrome again. Only an explicit browser-disconnected result invalidates the
browser binding; a real kernel reset creates a fresh Node session and therefore
requires normal one-time initialization again.

Use this preflight sequence:

1. Run one lightweight metadata transaction under `metadata_timeout_ms`.
   `openTabs()` may be followed by local selection, exact-object `claimTab()`,
   `url()`, and `title()` in the same metadata-only cell, up to
   `metadata_commands_per_cell`. Never guess a tab ID.
2. Prefer a currently open Reddit tab whose URL/title/recency identify it, but
   first exclude every exact tab ID recorded in the available launcher/lane
   checkpoints as another task's primary or disposable tab. Claim only a
   provably unowned Reddit tab. If none exists, create one disposable
   launcher-owned tab and navigate it in separate calls. If tab creation fails
   because the current window cannot create/group a tab, ask the user to open
   Reddit in Chrome; never navigate, close, inspect, or repurpose an unrelated
   user, launcher, or sibling-lane tab as fallback.
3. If the launcher created a disposable Reddit tab, open the Old Reddit
   starting surface from `reddit-surface-routing.md`; if it is unavailable, use
   its one bounded current-Reddit fallback. If the launcher instead claimed a
   provably unowned, already-open Reddit tab, verify it on its current native
   surface and do not navigate it merely to enforce Old Reddit. Confirm the
   visible account with exactly one
   cheapest page-state surface: DOM snapshot, screenshot, or a bounded read-only
   projection. This content read is the only blocking page command in its cell
   and uses `outer_timeout_ms`. Do not require both DOM and screenshot by
   default. URL/title metadata proves only extension and tab reachability and
   never proves the account. The launcher records the actual surface used; it
   does not change the account-wide Reddit preference.
4. Preserve a user-opened Reddit tab. Close only a disposable tab created by
   this launcher, using the installed Chrome Plugin's cleanup contract. Do not
   retain a worker-style primary tab from preflight.
5. Confirm persistent task list/read/send/create, rename, and archive/unarchive capability without creating operation tasks yet. Confirm the create schema exposes returned identifier type and host-aware read/send fields when the host supports them.
6. Confirm from the available automation tool/schema that recurring Heartbeat create/update/read/delete, explicit `targetThreadId`, and exact-automation target readback are callable. Do not create, update, or delete a bootstrap test Heartbeat or smoke-probe automation. Hidden `next_run_at` is handled by the first real worker timer as `created_unreadable`; an unreadable target binding is not verified and cannot schedule continuation.
7. Read real local time/timezone and UTC.
8. Detect available task model choices when the host exposes them. Select the first supported canonical fallback pair; if availability is not queryable, let new-task creation attempt the chain in order. Record the actual selected pair internally and do not expose it in the healthy Bootstrap prompt.

If a required item needs user repair, remain `Reddit 启动台`, persist `bootstrap_state=BOOTSTRAP_REPAIR_REQUIRED`, and request only that repair. In this state, `继续` rechecks only the missing items and never dispatches an operation mission.

If `openTabs()`, exact-object `claimTab()`, URL, and title succeed but the one
chosen DOM/screenshot/projection read times out after the full outer budget,
record the four launcher facts `CHROME_METADATA_HEALTHY`,
`CHROME_TAB_CLAIMED`, `CHROME_CONTENT_CHANNEL_TIMEOUT`, and
`REDDIT_PAGE_UNVERIFIED`; the canonical error class is
`chrome_content_channel_timeout`. Do not report Chrome disconnected, target tab missing,
Reddit login failure, or account risk. Load `chrome-network-recovery.md` and, only
while there is no draft, mutation, or uncertain submit, run at most one neutral
HTTPS content probe in a disposable launcher-owned tab. Reddit failing while the
neutral content read works scopes the fault to Reddit/site content; both content
reads failing scopes it to the browser content channel or network path. A
healthy metadata response means the native Chrome extension setup check already
passed, so do not recommend reinstalling or re-enabling the extension unless an
explicit extension/native-messaging/disconnected error later appears. Request
one evidence-matched repair or later recheck and stay in
`BOOTSTRAP_REPAIR_REQUIRED`.

Use the tool's real `timeout_ms`; never wrap browser work in `Promise.race()` or
another model-side pseudo-timeout, because it does not cancel the underlying
Chrome request and can leave later reads blocked.

When healthy, load `account-direction.md` before switching to the distributor. Resolve the exact visible Reddit account's user-owned direction file under `${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/account-directions/`, but keep this preflight state internal.

- Matching valid file: reuse it silently as the fallback account portfolio; the bootstrap question still asks for this run's direction and duration.
- Missing/malformed/mismatched file: prepare the broad default silently. Persist the user's answer, or the default when the user explicitly chooses it.
- Explicit direction and duration in the setup command: normalize/persist the direction and dispatch immediately without a redundant question.
- Persist atomically outside the managed Skill tree. Never store credentials or copy one account's direction to another account automatically.

After successful preflight, rename the same task `Reddit 分发台` and pin that exact task. If the setup command did not already provide both direction and duration, persist `bootstrap_state=BOOTSTRAP_AWAITING_OPERATION`, emit only the Bootstrap Success Prompt below, and wait for one answer. Do not prepend or append version, install/NOOP, validator, account, schema, preflight, rename/pin, no-action, source-link, or probe details. Those remain internal unless one concrete failure requires user repair. Rename or pin failure is presentation degradation; report only that concrete issue instead of a success prompt.

The answer starts dispatch immediately. Direction-only answers use `3h`; duration-only answers use the matching saved direction or the broad default. Only while `bootstrap_state=BOOTSTRAP_AWAITING_OPERATION`, `继续`, `开始`, `默认`, or `没想法` means matching saved direction or broad default plus `3h`, and immediately dispatches the first comments + posts + follow-up missions. Never ask a second confirmation or a second operation question. Clear the Bootstrap state only after dispatch is attempted; a later bare `继续` in pinned idle must not duplicate the previous mission without a new pending request.

Keep the account-keyed lane registry outside the managed Skill tree at `${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/lane-registry/<username>.json`. Upgrades preserve it. It contains only canonical lane names, exact ready task IDs, optional host IDs, titles, and last successful delivery metadata; never queued client IDs, credentials, Reddit content, Heartbeat IDs, or worker status. Worker runtime belongs separately under the exact paths in `lane-state-checkpoint.md`; upgrades preserve those checkpoints and append-only lane histories as well.

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
