# Follow-Up Playbook

Use only for notifications, supplied Reddit URLs, replies to the account's own recent posts/comments, and mod/Automod follow-up. Shared lifecycle and scheduling come from `orchestration-core.md` and `scheduler-and-heartbeats.md`. Load `browse-vote-playbook.md` in incidental mode for another user's inbound reply already opened during this sweep.

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

Score each exact inbound item:

| Factor | Points | Simple question |
|-|-:|-|
| Reply need | 0-30 | Is there a direct question, correction, misunderstanding, or expected acknowledgement? |
| Useful value | 0-25 | Can the account add a clear answer, clarification, or precise thanks? |
| Conversation freshness | 0-20 | Is the exchange still active and worth continuing now? |
| Tone and context fit | 0-15 | Does a reply fit the parent chain rather than interrupt it? |
| Truthfulness and safety | 0-10 | Can it be answered without invention, promotion, or unsafe claims? |

- `Act >=75`: reply when the lane has session authorization.
- `Watch 60-74`: keep open and reassess in the next full sweep.
- `Skip <60`: generic praise needing no reply, bait/hostility, unsafe/sensitive topic, locked/removed/old target, or a reply requiring invented experience or promotion.
- `Closed`: resolved chain, removed item, withdrawn pending post, or no further useful action.

Session-level authorization covers `Act` replies. Do not request per-reply confirmation.

After reading the exact inbound chain, independently assess the other user's reply for an incidental vote. Never vote on the account's own item, team/affiliated content, moderator/Automod content, or a supplied campaign target. There is no vote quota: do not browse unrelated feeds, reopen closed chains, or delay a reply to find votes. Record `incidental_vote_count`, `existing_vote`, or `no_vote` locally and continue triage.

This lane has no artificial reply quota. Its completion target is one full required-surface sweep plus every passing `Act` available in that sweep. Continue through Notifications, supplied/known permalinks, recent own posts, and recent own comments even when the first surface is quiet; never report a partial sweep as completion.

## Reply Execution

1. Read the parent and nearby chain, not only the notification preview.
2. Load `publish-consistency.md`, compare history, and run Double-Check A.
3. Load `outbound-copy-gate.md`; classify the reply as ordinary follow-up, technical, sensitive/support, or mod acknowledgement, then apply that surface's length and slang/abbreviation band against the rolling last `10` outputs. An ordinary follow-up normally needs one locally supported colloquial marker or abbreviation; technical, sensitive, and moderator contexts retain the lower exception bands.
4. Add one useful thing: acknowledgement, clarification, precise thanks, compact answer, or one question.
5. Enter the reply and run Double-Check B.
6. Reselect this lane's dedicated Reddit tab, verify account/target, wait `18-70 sec`, submit, and verify.
7. Append length, `voice_band`, `native_marker_used`, and `slang_or_abbrev_used` to history; keep at least `1 min` between follow-up replies and vary only when context supports it.
8. Mark the item Act/Watch/Skip/Closed and set the next check only if still open.

Avoid customer-support boilerplate, repeated thanks, essays, links outside scope, and fixed two-sentence replies.

## Mod And Approval Handling

- Never argue with moderators.
- If Automod/moderators removed or filtered content, retire that subreddit, send `SUBREDDIT_RETIRED`, do not repost there, and continue other follow-up work.
- If an own recent post shows `Post is awaiting moderator approval`, `Waiting for approval`, or equivalent pending-review UI, treat it as pre-authorized cleanup: immediately open its own controls, choose Delete/Withdraw, confirm the deletion dialog when shown, and accept one visible `Post deleted`/missing-own-post result as cleanup proof. Retire that subreddit, send the non-blocking notice, close the item, and continue the sweep. Never ask the user whether to delete, wait for moderator review, or pause any lane.
- If the cleanup route is temporarily blocked, record the exact permalink in this lane's cleanup queue, run `chrome-network-recovery.md`, and retry on the next due follow-up wake. The post and subreddit remain closed for engagement immediately; the follow-up lane continues other items, and every sibling lane remains unchanged.
- If the author deletes/locks the parent of an active own comment or reply, retire that subreddit and send the same non-blocking notice. A random old/removed item discovered during scanning is only `Skip` and does not retire a community.
- If a mod requests an edit, summarize it and act only when the current authorization clearly covers that edit.
- Currently active account warnings, captcha, rate limit, or login mismatch pause the actions they prevent. A timed rate limit automatically resumes at expiry; historical/cleared states do not stop follow-up.

## Next Sweep

On a direct user command or execution-heartbeat resume, complete the current Notifications + known-permalink/recent-activity sweep before scheduling another check. The processed reply/close result or the concrete quiet-queue sweep is `slot_proof`; merely deciding the next sweep time is not.

- normal queue: selected intensity cadence
- active direct exchange: `12-20 min`
- quiet queue: `40-90 min`
- several replies or uncertainty: `57-96 min`

Choose from state, not random imitation. Compute one exact local/UTC next due time and update/reuse this follow-up task's own logical Heartbeat.

The follow-up lane owns its execution state, cleanup queue, and self-targeted recurring Heartbeat. It never inspects or mutates sibling tasks/timers and reports scheduling evidence only in this task.

## Follow-Up Report

Use the three-line compact report from `orchestration-core.md`:

- `本轮完成`：已检查的 Notifications、本人帖子/评论，以及完成的回复、清理动作、附带投票数量和 permalink
- `下一轮心跳`：核验后的本地日期时间、时区及 UTC
- `下轮计划`：下一次跟进范围和目标动作

Keep queue size, Act/Watch/Skip/Closed triage, final reply text/translation, visibility, UTC, and scheduler readback internal unless they explain a risk or the user asks.
