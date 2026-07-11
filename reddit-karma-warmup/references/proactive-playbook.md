# Proactive Playbook

Use only for new comments on existing Reddit threads and optional main posts. Dedicated browsing and vote decisions belong to `browse-vote-playbook.md`. Shared lifecycle, Chrome lease, risk, scheduling, and reporting come from `orchestration-core.md`.

## Account Bands

Reddit does not publish a global safe comments-per-hour or posts-per-day limit. Account age and karma are only proxies: CQS/reputation signals, email verification, network/account-security signals, recent behavior, subreddit karma, and each community's eligibility rules also matter. Use the lowest supported tier across the observable signals; age alone never upgrades an inactive or low-quality account.

| Tier | Observable operating state | Maximum comment envelope | Maximum daily envelope | Main-post window |
|-|-|-:|-:|-:|
| `K0 New` | `<50` karma; use `fresh_bootstrap` when `<48h`, blank/no-history, unverified/unknown, or visibility is uncertain | up to `10/hour` | up to `60/day` only in explicit high-volume mode | `0-2/day` |
| `K1 Growing` | `50-199` karma plus `>=7d` clean recent state | up to `16/hour` after explicit override | up to `60/day` | `0-3/day` |
| `K2 Established` | `>=200` karma plus `>=14d` clean recent state | up to `20/hour` after explicit override | up to `60/day` | `0-3/day` |

These are internal ceilings, not Reddit platform limits, safety guarantees, or quotas. Normal operations use the low/standard/high envelopes from `default-operations-sop.md`; account tier and recovery state clamp those envelopes. The user may request another count; distribute it across the requested window, warn once when it materially exceeds the current tier, and publish only passing candidates.

Use `new-account-bootstrap.md` when `K0` is in `fresh_bootstrap`. Passing its checkpoints changes the substate to `active_new` but does not create another tier. Promote to `K1/K2` only when both the karma band and account-level health signals pass. Community removals retire only their exact subreddits; they do not demote the account tier or create a generic slowdown.

After every verified proactive comment, use a local `60-120 sec` pause before the next publish; discovery, reading, drafting, and verification time are additional. Main posts are heavier: default to at most one main post per subreddit per `24h`. The first eligible main post of the day has no skill-level `6h` waiting gate. Only a second same-day post requires a different community and audience/angle cluster, at least `6h` separation from the first, and a clean visibility check on the earlier post.

## Explicit Daily 60 Comment Mode

This is not the default. Enable it only when the user explicitly requests about `60 comments/day`, or explicitly selects high intensity for at least `6h`. It is a planning ceiling, never a quota that lowers the candidate threshold.

- All tiers may plan toward `60/day` only while clean and explicitly authorized. Use at least a `6h` operating window for the full target.
- For a shorter window, target at most `10 x available hours`; do not compress missed comments into a burst.
- High intensity starts with a `6-10` passing-comment first-hour envelope. The coordinator checks the first permalink in parallel without pausing the comment worker.
- After the first hour, continue within the selected high envelope. A subreddit visibility/removal failure retires only that subreddit; only an `R3` account-level signal disables this mode.
- Prefer at least `6` communities and `3` clusters across a 60-comment day when the eligible pool supports it; avoid more than `5` proactive comments in one subreddit per `24h`.
- Keep the normal `Act >=80`, truthfulness, copy-length, history, and `60-120 sec` post-submit pause. If not enough candidates pass, publish fewer.
- Only `R3` disables Daily 60 mode. `R1/R2` retire the affected subreddit(s) but keep the account tier and authorized envelope in unrelated eligible communities. Do not compensate for retired candidates with bursts.

## Removal Scope Levels

Count a native Reddit mod/Automod removal, moderation lock on a newly submitted item, confirmed filter/invisibility, subreddit ban, parent-post deletion that invalidates the interaction, or explicit community warning. Do not count the user's intentional deletion or an ordinary archival lock on an old thread. These are community-level signals unless Reddit separately shows an account-wide warning.

### `R1 Isolated`

Trigger: one removal/filter/lock/ban or invalidating parent deletion in one community, with no explicit account-wide warning.

- Retire the affected subreddit from future Loci posts/comments and record the exact removal or ban evidence. Do not retry, repost, or route another account into the same subreddit.
- Notify the user once, but do not ask for a decision unless that exact subreddit was mission-critical.
- Continue in other eligible communities at the account's existing tier and selected operating envelope. Do not downgrade the account, cap unrelated main posts, or pause the wider cycle because of this isolated event.
- Reopen the subreddit only after an explicit user decision backed by a clear moderator/rule explanation; time passing alone does not reopen it.

### `R2 Multiple Community Retirements`

Trigger: removals/filters/locks/bans have retired at least two communities. This remains a set of subreddit-level outcomes, not an inferred account penalty.

- Retire every affected subreddit from future posts/comments and preserve each exact notice/permalink.
- Send one consolidated non-blocking notice to `Reddit 主控台`; do not ask the user for permission to continue.
- Continue in unaffected eligible communities at the same account tier, comment envelope, and post window.
- Do not impose a `24h/72h` account cooldown, Daily 60 shutdown, generic rate reduction, or account-wide post cap from removals alone.
- Inspect whether the removed items shared an avoidable rule/format mismatch before drafting the next item, but do not treat that review as a pause or lower the candidate threshold.
- Reopen a retired subreddit only after an explicit user decision backed by a clear moderator/rule explanation.

### `R3 Account Stop`

Trigger: captcha, sitewide rate limit, lock/suspension, account-wide warning, login mismatch, credential request, or Reddit explicitly identifies spam/automation abuse.

- Stop all account mutations; do not schedule more publishing.
- Resume only after the user restores the account/session and the warning state is understood.
- The first clean `24h` after resumption uses `K0 recovery`: `2-5 comments/hour`, `4-10 comments/day`, and `0-1` fully preflighted main post.
- A dropped Chrome connection alone is not `R3`; reconnect and verify whether the prior action posted before retrying.

## Choose The Lane

- `comment lane`: the user asks for comments or broad participation.
- `post lane`: the user explicitly asks for main posts or a post window is enabled by the broad SOP.
- `mixed`: keep separate comment and post targets; never count comments as posts.

For early accounts, execute comments first. Broad `运营` still enables the post candidate/preflight lane; a comment-only command does not add posts.

## Active Pool Gate

User-provided targets override the bundled pool. Otherwise load `loci-subreddit-pool-v1.md`. Use `operation-style-profiles.md` to rank direction fit and `publish-consistency.md` to build the eligible pool.

- `B`: eligible when the row and live context fit.
- `B+`: ordinary comments and low-frequency feedback/demo contexts when row rules fit.
- `A`: research-first; interact only for a clear ordinary non-product reason.
- `A0` and `No-go`: read-only; no post, comment, vote, join, flair, or warm-up action.

Within `B/B+`, start from communities with the clearest ordinary participation path, lowest row restriction, and strongest resolved-style fit. A retired subreddit is closed for future outward actions. Retirements in other communities carry no account-tier, pacing, or candidate-score penalty.

Prefer `New` and `Rising` for early comment opportunities. Use `Hot` and `Top` to learn community language and survivor patterns.

## Comment Candidate Gate

Score the exact post and intended parent comment, not only the subreddit.

| Factor | Points |
|-|-:|
| Specific context and contribution opportunity | 0-25 |
| Community and topic fit | 0-20 |
| Timing and thread visibility | 0-15 |
| Non-duplication versus existing comments | 0-15 |
| Account credibility without invented experience | 0-15 |
| Rule, safety, and promotion risk | 0-10 |

- `Act`: `>=80`; if replying to a particular comment, target fit should be `>=82`.
- `Watch`: `68-79`; read/learn, do not force a reply.
- `Skip`: `<68`, stale, saturated, unsafe, generic, or dependent on fake experience/product mention.

For a fast-rising topic, also require a clear current hook: the thread is still young, the reply adds something not already dominant, and the topic is native to the subreddit. Search the exact current topic when freshness affects correctness; turn research into one compact insight rather than a source dump.

## Comment Execution

1. Open and read the post plus enough comments to understand local context.
2. Score the candidate, compare history, and run Double-Check A.
3. Load `outbound-copy-gate.md`; read the last `10` measured comment/reply lengths, then choose length from target context, nearby native style, and recent mix.
4. Prefer one specific observation, distinction, useful question, or precise praise.
5. Enter the draft and run Double-Check B.
6. Reselect this lane's dedicated Reddit tab, verify account/target, wait `18-70 sec`, submit, and verify permalink/profile visibility.
7. Measure the exact published text and append `char_count`, `word_count`, `sentence_form`, `length_tier`, and `why_this_length` to history and follow-up state. After a verified proactive comment, use a local `60-120 sec` pause before the next publish; first follow-up is normally `20-40 min` later.
8. During a new start, use the selected intensity envelope. Respect subreddit/cluster diversity and do not lower the candidate threshold to fill the target.

Comments should be mostly short, while longer replies remain available when the target genuinely needs explanation. Do not default to two polished sentences, mechanically rotate lengths, add filler, summarize the post, repeat top comments, or mention Loci/product links unless the user explicitly requests it and rules permit it.

## Main Post Gate

Choose subreddit + audience + angle after history comparison and before drafting. Treat this live same-day preflight as the post-specific part of Double-Check A:

Do not reject a first daily post merely because the account is `K0` or because six hours have not elapsed. `6h` is only the spacing gate between the first and second same-day posts. The first post still requires all live subreddit eligibility, account-age/Karma, format, history, and moderation checks below.

1. home/about/sidebar/rules
2. pinned moderator posts
3. recent `New`, `Hot`, and `Top Month` survivor patterns
4. submit fields: flair, title format, body/link mode, Automod hints
5. karma/account-age restrictions and account-visible post controls
6. main feed vs megathread placement
7. link, media, self-promo, product, survey, and feedback rules
8. same-subreddit `24h` history and recent team/account angle duplication
9. moderator-approval or restricted-posting signal

Decision:

- `pass`: eligibility and format are clear, similar native content survives, angle fits.
- `skip_candidate`: eligibility is unclear, required format cannot be met, same-subreddit window is used, angle is repetitive, or submit surface says moderator approval is required.
- `retire_subreddit`: an own item is removed/filtered/locked, the account is banned from that subreddit, the parent post is deleted/locked in a way that invalidates the action, or a submitted post becomes `awaiting moderator approval`.
- `hard_stop`: captcha, sitewide rate limit, account-wide warning, lock/suspension, login mismatch, credential request, or clear unsafe/deceptive action.

On `retire_subreddit`, delete/withdraw a pending post when possible, verify cleanup, never repost in that subreddit, send the non-blocking retirement notice, and continue the same lane in another eligible community.

After drafting, run Double-Check B on the final title/body/flair, live submit state, history, length/structure, and duplicate-send risk before clicking Post.

## Post Diversity

For multiple planned posts, vary both community cluster and angle when viable:

- builder/product
- creator/dev/3D
- AR/VR/spatial
- social/AI/companion
- place/outdoor/location
- competitor/product communities

Diversity never justifies a weak target. Publish fewer posts if no second distinct community passes.

## Beginner-Trap Angle

Use beginner-trap questions only where members share a real skill threshold and recent survivor posts show an advice culture. Require:

- a concrete domain/workflow mistake
- at least two recent examples of tips, mistakes, critique, or `what I wish I knew`
- no FAQ, low-effort-question, survey, or beginner-post prohibition
- no product, waitlist, or fake expertise needed

Strong: `What's the Unity beginner trap that only shows up once you try to ship?`

Weak: `Any tips for beginners?`

## Proactive Slot Report

On a direct user command or execution-heartbeat resume, finish and verify the current comment/post micro-slot before scheduling or reporting. Record the permalink/action as `slot_proof`, or record the exact candidates/surfaces checked and rejection gate as verified no-action proof. Planning the next post/comment window is not a completed slot.

Use the three-line compact report from `orchestration-core.md`:

- `本轮完成`：已完成的评论、主帖、数量、subreddit 和 permalink
- `下一轮心跳`：核验后的本地日期时间、时区及 UTC
- `下轮计划`：计划进行的评论或发帖工作及目标数量

Keep candidate scores, `insight_basis`, final text/translation, preflight, Check A/B, and history/length comparisons in the internal action log. Show them only when the user asks or they explain a risk or missing action.
