# Reddit Karma Warmup

Protocol version: `2026.07.27.12`

This repository contains one production Skill: `reddit-karma-warmup/`.

## Send this prompt

```text
请完整读取并执行 https://raw.githubusercontent.com/lishehao/reddit-karma-warmup/main/README.md：通过 HTTPS 安装或升级 reddit-karma-warmup，完成安装完整性与本机能力预检，并完成启动交接；不要进入目标模式。此阶段不得打开 Reddit/Chrome、运行 Web Search/API、创建 mission envelope/queue/Heartbeat，或创建浏览/评论/发帖/跟进/主页任务。完成后仅报告 `BOOTSTRAP_READY`、已验证版本和等待的下一条方向/时长/账号/授权指令。
```

## Bootstrap-only boundary

The prompt above is stage one only. Verify the raw/codeload source, package
layout, manifest version, offline validator, installed tree, current task
presence, and required tool availability. It may rename the current task to
`Reddit 启动台` as presentation only. It must not create a mission record,
queue, timer, Chrome binding, or Reddit tab, and must not search, read, or
mutate Reddit.

Stop at `BOOTSTRAP_READY`. A later user message moves the same present task
into the `Reddit 运营台` mission sequence only when it gives an account,
business goal, duration, and explicit action authority. It may use this compact
shape:

```text
Reddit 运营：目标=<找社区/参与讨论/获得反馈/发布项目/维护已有内容/完善主页>；
素材=<真实链接、项目或“无”>；主题=<受众或话题>；范围=<发现新社区/指定社区>；
时长=<…>；覆盖=<窄/标准/广>；行动门槛=<高/标准/低>；
授权=<浏览、评论、发帖、跟进、主页>。
```

“高频/低频”是兼容性简称，不改变 15 分钟 Heartbeat：它会被解释为
覆盖面、软行动门槛和动作预算的组合。版规、真实性、当前账号/表单状态、
明确授权与提交验证始终是不可降低的硬门槛。

## Runtime in one page

1. During bootstrap, install the complete Skill atomically under `${CODEX_HOME:-$HOME/.codex}/skills/`.
   Compare `manifest.json`; never merge versions.
2. One present, unarchived `Reddit 运营台` owns one mission envelope, one
   queue, one Heartbeat, one Chrome binding, and one primary Reddit tab.
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
   before work; refresh that receipt after each wake. Align normal unit rechecks
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
