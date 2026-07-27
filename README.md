# Reddit Karma Warmup

Protocol version: `2026.07.27.19`

This repository contains one production Skill: `reddit-karma-warmup/`.

## Send this prompt

```text
请完整读取并执行 https://raw.githubusercontent.com/lishehao/reddit-karma-warmup/main/README.md：通过 HTTPS 安装或升级 reddit-karma-warmup，完成安装完整性与本机能力预检，并完成启动交接；不要进入目标模式。此阶段不得打开 Reddit/Chrome、运行 Web Search/API、创建 mission envelope/queue/Heartbeat，或创建浏览/评论/发帖/跟进/主页任务。预检通过后报告 `BOOTSTRAP_READY` 和已验证版本，并直接提出 README 定义的三个启动问题；不要要求我再写一段完整任务 Prompt，也不要询问账号。
```

## Bootstrap-only boundary

The prompt above is stage one only. Verify the raw/codeload source, package
layout, manifest version, offline validator, installed tree, current task
presence, and required tool availability. It may rename the current task to
`Reddit 启动台` as presentation only. It must not create a mission record,
queue, timer, Chrome binding, or Reddit tab, and must not search, read, or
mutate Reddit.

After `BOOTSTRAP_READY`, ask exactly these three questions in one request.
The user can answer all three as three short lines. Do not ask for an account:
resolve the actual `u/<name>` only through the same-Chrome live gate after the
answers are complete.

1. **运行多久？** `2 小时 / 4 小时 / 8 小时` are the preset choices; accept
   an explicit custom duration as `其他`.
2. **账号想往什么方向找社区，并塑造成怎样的 IP？** The preset choices are
   `社交与社区`、`个人创作与独立项目`、`3D/游戏/共创`. In the same answer
   require the desired account direction/IP and target audience; named
   communities are optional seeds, otherwise search expands from that direction.
3. **允许做什么，以及节奏？** The preset choices are `研究优先`、`评论优先`、
   `项目运营`. They map to the business goal, explicit unit authority, and
   default coverage/threshold/action-budget profiles. Accept `其他` only when
   the user names the exact allowed units and any intended override.

The complete mapping, defaults, and custom-answer rules are in
[`startup-intake.md`](reddit-karma-warmup/references/startup-intake.md). Once
all three answers arrive, compile them through the local deterministic startup
compiler into immutable mission-envelope inputs, run the same-Chrome account
gate, and start the mission. Do not ask a fourth
clarification merely because posts lack truthful material: compile that unit as
`MATERIAL_REQUIRED` while other authorized units may proceed.

Answer completion starts the mission directly: classify the local runtime,
compile the envelope, perform the technical canary/account gate, create and
read back the Heartbeat, then run the first formal `INITIAL` packet in the
same task turn. Those technical gates are not a preview, candidate-filter, or
second user-decision stage.

The three answers are a hard wait. When the task uses `request_user_input`,
it must omit `autoResolutionMs`; no answer or partial answer remains
`WAITING_FOR_STARTUP_INPUT`, not permission to choose defaults or start work.
Only an explicit user cancellation ends this intake.

“高频/低频”是兼容性简称，不改变 15 分钟 Heartbeat：它会被解释为
覆盖面、软行动门槛和动作预算的组合。版规、真实性、当前账号/表单状态、
明确授权与提交验证始终是不可降低的硬门槛。

## Runtime in one page

1. During bootstrap, install the complete Skill atomically under `${CODEX_HOME:-$HOME/.codex}/skills/`.
   Compare `manifest.json`; never merge versions.
2. Promote the same present task from `Reddit 启动台` to `Reddit 运营台` only
   after the mission envelope is bound. Read back the exact title and store its
   proof before the canary, then let that one operating task own one queue, one
   Heartbeat, one Chrome binding, and one primary Reddit tab.
   Before starting a new mission, classify any old local runtime record. A
   stale `ACTIVE` JSON value or `chrome_release=PENDING` does not itself block:
   only a running owner, held lock, or future Heartbeat does. A record whose
   cutoff has passed, task is not running, Heartbeat is absent/expired, and
   lock is unheld is reconciled locally and does not require user confirmation.
3. Built-in Web Search performs broad current research. The optional
   `scripts/community_index.py` uses official OAuth GET calls only for public
   community rules, metadata, and small hot-pointer indexes. It never writes,
   uses cookies, replaces Chrome, or grants action permission.
4. Chrome performs every real Reddit read and every interactive action:
   rules/context final check, account, composer, flair, publish/reply/vote, and
   result verification. Use Old Reddit first for ordinary text work and one
   bounded current-Reddit fallback only when necessary.
5. A post/comment/reply/profile change/vote needs explicit unit authority plus
   current rules, account, submit state, truthful evidence, pacing, and one
   verified result. Persist an `action_key` before submission; freeze uncertain
   results and never retry them.
6. Compile one business-goal profile: `community_discovery`,
   `conversation_entry`, `feedback_validation`, `project_distribution`,
   `relationship_maintenance`, or `profile_readiness`. Store community scope,
   coverage budget, soft action threshold, action budget, and evidence/output
   targets in the mission envelope. These are planning controls, never a quota
   that forces a public action.
7. Separate a bounded packet from its unit objective. A completed research
   packet never means a post, comment, follow-up, or presence objective is
   complete. Candidate packs explicitly arm the next eligible unit; verified
   own permalinks explicitly arm follow-up. Missing truthful material, a live
   rule block, an uncertain submission, or no applicable target parks only that
   unit and removes its recurring wake until a new mission revision or upstream
   evidence changes it.
8. Use one stable 15-minute mission Heartbeat with an explicit cleanup-grace
   `UNTIL`. Persist/read back its ID, target, RRULE, `UNTIL`, and future next run
   before work; record each delivered Heartbeat against that receipt and refresh
   it after each closed wake. A late observed delivery is not proof that an
   earlier delivery occurred: record a suspected scheduler gap and enter
   recovery/finalization on the next available task turn rather than inventing
   catch-up work. Align normal unit rechecks
   to that grid; a no-work wake is an atomic fast NOOP with no Chrome call. An
   authorized pending comment/post is clamped to the next grid if its default
   recheck would otherwise cross the mission cutoff; when no grid remains, it
   settles as `ACTION_WINDOW_EXPIRED` rather than wedging the wake. ±5 minutes
   is normal; outside it, record an early/late signed delta without catch-up.
   At deadline enter finalization only: recover stale work, release owned tabs,
   delete the Heartbeat with proof, then retire the queue.

## Release rule

Skill updates publish directly to GitHub `main`: bump the version, run the
offline validator, build the ZIP, verify a fresh public codeload, then replace
the local managed copy atomically only when no active old runtime fence exists.
