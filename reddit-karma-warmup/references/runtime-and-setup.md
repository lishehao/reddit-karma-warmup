# Runtime And Setup

This reference was split out of SKILL.md to keep the entrypoint small. Load it only when the SKILL.md routing table says it is needed.

## Runtime Requirements

This skill is instruction-only. It has no bundled scripts and does not require a Python environment, Node.js environment, package manager install, database, API key, or Lark/Figma/other external CLI.

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
- Worker/task capability is optional. Use it only when current host policy and user scope authorize delegation. Creating user-visible Codex tasks requires an explicit user request; otherwise run lanes sequentially in the current task.
- Distributed coordinator mode requires task create, read, and send/update capability as one bundle. Do not create workers that the coordinator cannot later read or steer. Task-title control is optional.
- Model/effort override capability is optional. When available, load `model-runtime.md`, request `gpt-5.6-sol/xhigh` for the coordinator and `gpt-5.6-luna/high` for workers; when unavailable, use the strongest actually exposed fallback and do not block the run.
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

Keep dependency details internal when all required checks pass. Return only a short Chinese result:

```text
状态健康。Skill、Chrome、Reddit 登录、Heartbeat 和当地时间均可用。当前账号：u/name。
可以执行主动评论、消息跟进、主页维护和内容浏览；主动发帖可选。是否开始 3 小时运营？
```

If required checks fail, return `状态异常` with only the failed capability, its impact, and a direct repair action. Do not list successful checks. Python absence is never a failed required capability. `状态健康` describes environment readiness only; live account/community risk is assessed during the first operating slot.

Do not report `状态异常`, pause installation, or ask the user to reply `继续` merely because the automation view omits `next_run_at`, DTSTART, or a displayed next-run label. Record `heartbeat_timing=created_unreadable` internally and continue. Only failed create/update/delete capability is a scheduler dependency failure.

Do not treat the first dropped/stale connection as failure. Run the Chrome recovery flow in `orchestration-core.md`. If Chrome remains unavailable after recovery, is logged out, shows the wrong account, or hits captcha/rate limit/account lock, do not perform real Reddit actions and tell the user the concrete state. Setup-only checks and non-account read-only explanations may continue.

## Runtime Start

The repository `README.md` owns installation and dependency preflight. Once it reports the environment ready and the user confirms start, restore its handoff instead of repeating the audit:

1. Restore the reported Chrome account, heartbeat support, task/model fallback, local timezone, and detected `scheduler_clock_mode`.
2. Confirm the already-validated Chrome control remains connected and still shows that Reddit account; read current local time and UTC again.
3. Choose the requested mode and execute the first slot immediately.
4. Do not send a final `已启动` acknowledgement until that slot yields a verified requested action or browser-backed no-action/blocker. Planning, worker dispatch, and heartbeat creation do not satisfy this gate.
5. Run the scheduler smoke test when the installed environment is new or previously drifted, after start proof and without replacing the first operating slot.
6. Report any runtime regression precisely. Do not silently replace Chrome control with Computer Use, the in-app Browser, Playwright, or another browser surface.

When installation/preflight is healthy but the user has not supplied an operating scope, return exactly this guided prompt with the blank line preserved:

```text
状态健康。当前账号：u/name。

你希望接下来怎么运营？可以指定时长、评论或发帖数量、目标社区，也可以只浏览并偶尔投票；如果暂时没想法，直接回复“开始”，我会按默认方案先试运行 3 小时。
```

Do not append dependency fields, model details, thread capability, or another confirmation question.
