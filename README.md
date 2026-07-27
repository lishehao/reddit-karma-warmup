# Reddit Karma Warmup

Protocol version: `2026.07.27.6`

This repository contains one production Skill: `reddit-karma-warmup/`.

## Send this prompt

```text
请完整读取并执行 https://raw.githubusercontent.com/lishehao/reddit-karma-warmup/main/README.md：通过 HTTPS 安装或升级 reddit-karma-warmup。完成只读预检后，创建或继续一个单一、持久化的“Reddit 运营台”，不要创建浏览/评论/发帖/跟进/主页的独立 Chrome 任务。它应在同一任务中处理五个内部单元，默认只研究、投票关闭；API 只用于可选的公开规则/社区索引，所有真实 Reddit 浏览、表单和写操作都走已登录 Chrome。
```

## Runtime in one page

1. Install the complete Skill atomically under `${CODEX_HOME:-$HOME/.codex}/skills/`.
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
6. Separate a bounded packet from its unit objective. A completed research
   packet never means a post, comment, follow-up, or presence objective is
   complete. Candidate packs explicitly arm the next eligible unit; verified
   own permalinks explicitly arm follow-up. Missing truthful material, a live
   rule block, an uncertain submission, or no applicable target parks only that
   unit and removes its recurring wake until a new mission revision or upstream
   evidence changes it.
7. Use one stable 15-minute mission Heartbeat. Align normal unit rechecks to
   that grid; a no-work wake is a fast NOOP with no Chrome call. ±5 minutes is
   normal; a later wake records the delay and continues from actual time without
   catch-up. Each work wake runs at most one Chrome packet plus one public action.
   At deadline: release owned tabs, delete the Heartbeat, retire the queue.

## Release rule

Skill updates publish directly to GitHub `main`: bump the version, run the
offline validator, build the ZIP, verify a fresh public codeload, then replace
the local managed copy atomically only when no active old runtime fence exists.
