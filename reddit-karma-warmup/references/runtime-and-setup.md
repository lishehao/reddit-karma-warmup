# Runtime And Setup

This reference was split out of SKILL.md to keep the entrypoint small. Load it only when the SKILL.md routing table says it is needed.

## Runtime Requirements

This skill is instruction-led. It bundles its compatible persistent-task supervision protocol in `thread-supervision-runtime.md`; a separate `thread-supervisor` Skill is not required. Release-contract validators may exist under `scripts/`, but they are optional installation helpers and never runtime dependencies. Python, Node.js, package managers, databases, API keys, and Lark/Figma/other external CLIs are not required for Reddit operation.

## Bootstrap Role And Immediate Naming

A setup/install command starts a presentation and environment role, not an operating mission:

```text
role=REDDIT_BOOTSTRAP
title=Reddit 启动台
objective=install or upgrade, validate dependencies, and hand off the same task
never=Reddit mutations, lane workers, mission Heartbeats, or operating slots
```

1. The first available UI action after receiving a setup/install command is to rename the current task `Reddit 启动台`. Do this before downloading, reading dependency state, running preflight, or explaining the plan.
2. Keep the same task ID, history, and existing pin state. Do not create a second installer task or a second future coordinator.
3. Install/upgrade and run read-only preflight while the current role remains `REDDIT_BOOTSTRAP`. If a hard user repair is needed, remain Bootstrap and request only that repair.
4. When the Skill and required runtime are healthy, transition this same task in place to `REDDIT_COORDINATOR` and immediately rename it `Reddit 主控台` before returning the health/handoff message.
5. If title control is unavailable, record `rename_unavailable`, continue setup or promotion, and retry at the next safe point. Naming is presentation state, not a dependency or blocker.
6. If the Skill is already installed and the user's first message is a direct operating mission rather than setup, use the direct-mission fast path: rename the current task `Reddit 主控台` immediately, restore/verify runtime state, and execute the first requested round in the same turn.

The Bootstrap role ends only at healthy same-task promotion. It never dispatches execution tasks or schedules mission continuation.

## Version And Upgrade

The repository root `README.md` is the single installation entrypoint and machine protocol. It downloads the public archive from `https://codeload.github.com/lishehao/reddit-karma-warmup/zip/refs/heads/main` over HTTPS and selects the `reddit-karma-warmup/` directory. Git, GitHub CLI, and a local clone are not required. Do not look for a second installer document. Read the downloaded Skill `manifest.json` and compare `name` plus `version` before dependency preflight.

- no installed copy: install normally
- installed copy without a manifest: treat as legacy, back up, then upgrade
- incoming version newer: back up the complete installed folder, atomically replace the complete managed folder, and validate again
- same version and same content: no-op
- same version with different content: stop as a conflict
- incoming version older: do not downgrade without explicit user direction
- failed post-replacement validation: restore the prior folder and report rollback

Never merge files from old and new managed trees. A whole-folder replacement prevents deleted or renamed references from surviving an upgrade. Preserve the old tree in a timestamped backup rather than silently copying unknown files into the new version.

For release maintenance, increment the final numeric segment of `YYYY.MM.DD.N` whenever any distributed Skill or installer file changes. Compare version segments numerically, not as an unparsed string, and keep the installed folder plus GitHub source on the same active version.

Required capabilities for real Reddit operations:

- Codex skill support with file access to this `SKILL.md` and its `references/` files.
- Chrome Browser control for publishing, replying, voting, joining/subscribing, profile edits, and account-state checks. Discover it automatically; the user does not need to mention or attach `@chrome`. Chrome is required because it holds the stable Reddit login state.
- Chrome Browser control uses the ChatGPT Chrome Extension plus its Native Messaging connection. macOS Screen Recording, System Audio Recording, and Accessibility permissions are not required and must not be included in dependency failures. Those permissions may apply to Computer Use or desktop/audio capture, which are outside this Skill's Chrome path.
- The target Reddit account must already be logged in by the user. Never enter passwords or handle credentials.
- Scheduler/automation capability is required for multi-round heartbeat operation. A successful create/delete probe proves capability even when the runtime does not expose persisted `next_run_at` or displayed run time. Missing timing readback lowers confidence but is not a dependency failure and must not block the first Reddit round. If creation itself is unavailable or fails, complete only the current round and report the intended next local/UTC time for manual continuation.
- Persistent task create, read, and send/update capability is required for real Reddit operations. The guided handoff below states that replying `开始` explicitly authorizes creation or reuse of the requested lane tasks. Do not silently downgrade to sequential execution in the main task.
- Default broad operation requires four user-visible workers: `Reddit 评论台`, `Reddit 发帖台`, `Reddit 跟进台`, and `Reddit 浏览台`. A named single-lane operation requires only its matching worker. Do not create workers that the coordinator cannot later read or steer. After healthy Bootstrap promotion, rename the same task `Reddit 主控台` and pin it when presentation control exists; keep workers unpinned. Task-title/pin control is presentation-only and does not replace exact task-ID checks.
- Model/effort override capability is optional. When available, load `model-runtime.md` and request `gpt-5.6-luna/high` for the coordinator and workers; when unavailable, use the strongest actually exposed fallback and do not block the run.
- Shell/Python/date utilities are optional helpers for time calculation or file inspection, not dependencies. If unavailable, compute timezone pairs and schedule checks with whatever tools the environment exposes.

Python absence must never block an already installed Skill or real Reddit operations. During install/upgrade, use a bundled/system validator when available; otherwise perform equivalent structural checks on ZIP integrity, the single Skill root, SKILL.md frontmatter, manifest name/version/schema, agents metadata, reference readability, and referenced-file existence. Operational quality is unchanged; only the installation check is less automated.

## User-Facing Health Result

For a first-time user who has never used Reddit, installation and account creation are separate stages. Codex may install and validate the Skill, but the user must personally create/login to Reddit in the same Chrome profile and complete any verification Reddit displays. Never request, enter, store, or relay credentials.

Return exactly one repair at a time:

```text
需要你处理：请打开 Chrome，安装或启用 ChatGPT Chrome Extension，并保持 Chrome 运行。
影响：Skill 已安装，但 Reddit 操作尚未开始。
完成后回复“继续”。
```

After Chrome control works, if Reddit is logged out or unverified:

```text
需要你处理：请在当前 Chrome 手动打开 reddit.com，创建或登录账号，并完成 Reddit 页面显示的验证。不要把密码发给 Codex。
影响：Skill 已安装，但 Reddit 操作尚未开始。
完成后回复“继续”。
```

On `继续`, resume only the missing preflight checks. Do not reinstall a healthy Skill, repeat successful checks to the user, or ask the user to understand Chrome Extension, Native Messaging, scheduler, task, model, or timezone internals.

Keep dependency details internal when all required checks pass. First promote the same task to `REDDIT_COORDINATOR` and attempt the `Reddit 主控台` rename; then return only a short Chinese result:

```text
状态健康。Skill、Chrome、Reddit 登录、独立任务、Heartbeat 和当地时间均可用。当前账号：u/name。
可以执行评论、发帖、跟进和自然浏览（含符合门槛的 Upvote/Downvote）。回复“开始”即授权创建或复用四个独立工作任务，并按标准强度、混合探索风格开始 3 小时运营。
```

If required checks fail, return `状态异常` with only the failed capability, its impact, and a direct repair action. Do not list successful checks. Python absence is never a failed required capability. `状态健康` describes environment readiness only; live account/community risk is assessed during the first operating slot.

Do not report `状态异常`, pause installation, or ask the user to reply `继续` merely because the automation view omits `next_run_at`, DTSTART, or a displayed next-run label. Record `heartbeat_timing=created_unreadable` internally and continue. Only failed create/update/delete capability is a scheduler dependency failure.

Do not treat the first dropped/stale connection or page-loading code as failure. Run `chrome-network-recovery.md` through `orchestration-core.md`: record the exact code, distinguish control/tab/network/proxy/site/route/account scope, and perform bounded recovery in the same logged-in Chrome session. Keep retrying through recurring wakes; Chrome-control failure becomes user-repair eligible only after three consecutive recovery wakes. Timed rate limits resume automatically at expiry. Login/account mismatch, credentials, CAPTCHA/challenge, lock/suspension, or required acknowledgement with no automatic path withholds only the impossible mutations; tell the user only for the allowlisted repair while permitted work continues.

## Runtime Start

The repository `README.md` owns installation and dependency preflight. Runtime start is valid only in `REDDIT_COORDINATOR`; it either follows healthy same-task promotion from Bootstrap or uses the direct-mission fast path. Never create a replacement main task. Once the environment is ready and the user confirms start, restore its handoff instead of repeating the audit:

1. Restore the reported Chrome account, heartbeat support, task/model fallback, local timezone, and detected `scheduler_clock_mode`.
2. Confirm the already-validated Chrome control remains connected and still shows that Reddit account; read current local time and UTC again.
3. Choose the requested mode, create or reuse every enabled persistent lane task, and send each task its execute-now mission. Default broad operation uses the four outward workers; when bootstrap presence is useful, run one bounded `Reddit 主页台` checkpoint first, then start outward lanes without waiting for decoration retries once account identity is known.
4. Report startup per lane after a verified requested action or browser-backed no-action/recovery checkpoint. Planning, worker dispatch, and heartbeat creation alone do not satisfy this gate, but one recovering lane never delays healthy lanes.
5. Run the scheduler smoke test when the installed environment is new or previously drifted, after start proof and without replacing the first operating slot.
6. Report any runtime regression precisely. Do not silently replace Chrome control with Computer Use, the in-app Browser, Playwright, or another browser surface.

When installation/preflight is healthy but the user has not supplied an operating scope, return exactly this guided prompt with the blank line preserved:

```text
状态健康。当前账号：u/name。

你希望接下来怎么运营？可以指定时长、低/标准/高强度，以及混合探索、建设者、游戏/3D、空间地点、轻社交/创意或自定义风格；也可以直接指定评论、发帖、跟进、自然浏览。如果暂时没想法，回复“开始”即授权我创建或复用 Reddit 评论台、Reddit 发帖台、Reddit 跟进台和 Reddit 浏览台，并按标准强度、混合探索风格运行 3 小时。
```

Do not append dependency fields, model details, thread capability, or another confirmation question.
