# Follow-Up Playbook

Use only for notifications, supplied Reddit URLs, replies to the account's own recent posts/comments, and mod/Automod follow-up. Shared lifecycle and scheduling come from `orchestration-core.md` and `scheduler-and-heartbeats.md`.

## Cadence And Surfaces

Derive the base sweep cadence from operation intensity while the session is active: low `45-60 min`, standard `30-45 min`, high `20-30 min`.

Check:

1. Reddit notifications/full inbox, including official account notices and mod/Automod.
2. Supplied URLs and prior-session permalinks.
3. The account's recent posts for new top-level comments, direct replies, removal/approval state, and broad performance signals.
4. The account's recent comments for child replies and nearby continuation context.

Do not browse unrelated feeds in this lane. Notifications alone are insufficient because replies may be missed; known permalinks and recent profile activity are part of the sweep.

Shorten the next sweep only for an active direct exchange or time-sensitive mod clarification. Lengthen after a quiet sweep.

## Triage

- `Act`: a direct question, useful correction/feedback, real disagreement, misunderstanding worth clarifying, socially expected compact acknowledgement, or safe mod/Automod response.
- `Watch`: thread is developing, tone is unclear, another person already answered, or only performance changed.
- `Skip`: generic praise needing no reply, bait/hostility, unsafe/sensitive topic, locked/removed/old target, or a reply that would require invented experience or promotion.
- `Closed`: resolved chain, removed item, withdrawn pending post, or no further useful action.

Session-level authorization covers `Act` replies. Do not request per-reply confirmation.

## Reply Execution

1. Read the parent and nearby chain, not only the notification preview.
2. Load `publish-consistency.md`, compare history, and run Double-Check A.
3. Load `outbound-copy-gate.md` and choose length based on the parent and recent length mix.
4. Add one useful thing: acknowledgement, clarification, precise thanks, compact answer, or one question.
5. Enter the reply and run Double-Check B.
6. Reselect this lane's dedicated Reddit tab, verify account/target, wait `18-70 sec`, submit, and verify.
7. Append history; keep at least `1 min` between follow-up replies and vary only when context supports it.
8. Mark the item Act/Watch/Skip/Closed and set the next check only if still open.

Avoid customer-support boilerplate, repeated thanks, essays, links outside scope, and fixed two-sentence replies.

## Mod And Approval Handling

- Never argue with moderators.
- If Automod/moderators removed or filtered content, retire that subreddit, send `SUBREDDIT_RETIRED`, do not repost there, and continue other follow-up work.
- If an own recent post is awaiting moderator approval, withdraw/delete when possible, verify cleanup, retire that subreddit, send the non-blocking notice, and close that item without pausing unrelated work.
- If the author deletes/locks the parent of an active own comment or reply, retire that subreddit and send the same non-blocking notice. A random old/removed item discovered during scanning is only `Skip` and does not retire a community.
- If a mod requests an edit, summarize it and act only when the current authorization clearly covers that edit.
- Account warnings, captcha, rate limit, or login mismatch are global hard stops.

## Next Sweep

On a direct user command or execution-heartbeat resume, complete the current Notifications + known-permalink/recent-activity sweep before scheduling another check. The processed reply/close result or the concrete quiet-queue sweep is `slot_proof`; merely deciding the next sweep time is not.

- normal queue: selected intensity cadence
- active direct exchange: `12-20 min`
- quiet queue: `40-90 min`
- several replies or uncertainty: `57-96 min`

Choose from state, not random imitation. Update/reuse the lane's logical timer for one next due time, verify local/UTC readback and automation ID, and never stack another follow-up trigger for the same slot.

The follow-up lane owns only its follow-up automation. It may read proactive comment, post, or browsing automation status for context, but must not pause, resume, delete, or rewrite those triggers. If a global policy affects them, update the follow-up trigger only and report the other implications to their owner tasks or coordinator.

## Follow-Up Report

Use the three-line compact report from `orchestration-core.md`:

- `本轮完成`：已检查的 Notifications、本人帖子/评论，以及完成的回复或清理动作和 permalink
- `下一轮心跳`：核验后的本地日期时间、时区及 UTC
- `下轮计划`：下一次跟进范围和目标动作

Keep queue size, Act/Watch/Skip/Closed triage, final reply text/translation, visibility, UTC, and scheduler readback internal unless they explain a risk or the user asks.
