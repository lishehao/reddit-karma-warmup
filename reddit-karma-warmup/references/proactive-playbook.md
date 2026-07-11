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

Use `new-account-bootstrap.md` when `K0` is in `fresh_bootstrap`. Passing its checkpoints changes the substate to `active_new` but does not create another tier. Promote to `K1/K2` only when both the karma band and clean-history window pass. Apply the explicit recovery levels below after removals or account signals; do not use an undefined generic slowdown.

After every verified proactive comment, use a local `60-120 sec` pause before the next publish; discovery, reading, drafting, and verification time are additional. Main posts are heavier: default to at most one main post per subreddit per `24h`. The first eligible main post of the day has no skill-level `6h` waiting gate. Only a second same-day post requires a different community and audience/angle cluster, at least `6h` separation from the first, and a clean visibility check on the earlier post.

## Explicit Daily 60 Comment Mode

This is not the default. Enable it only when the user explicitly requests about `60 comments/day`, or explicitly selects high intensity for at least `6h`. It is a planning ceiling, never a quota that lowers the candidate threshold.

- All tiers may plan toward `60/day` only while clean and explicitly authorized. Use at least a `6h` operating window for the full target.
- For a shorter window, target at most `10 x available hours`; do not compress missed comments into a burst.
- High intensity starts with a `6-10` passing-comment first-hour envelope. The coordinator checks the first permalink in parallel without pausing the comment worker.
- After the first hour, continue within the selected high envelope. A concrete visibility or account failure disables this mode and activates the matching recovery level.
- Prefer at least `6` communities and `3` clusters across a 60-comment day when the eligible pool supports it; avoid more than `5` proactive comments in one subreddit per `24h`.
- Keep the normal `Act >=80`, truthfulness, copy-length, history, and `60-120 sec` post-submit pause. If not enough candidates pass, publish fewer.
- Any `R1`, `R2`, or `R3` event immediately disables Daily 60 mode and applies the corresponding recovery range. Never resume Daily 60 during the same recovery window.

## Removal And Recovery Levels

Count a native Reddit mod/Automod removal, confirmed filter/invisibility, or explicit community warning. Do not count the user's intentional deletion. A pending post that is withdrawn before approval is a failed post candidate but not automatically an account-level removal.

### `R1 Isolated`

Trigger: one removal/filter in one community, with no account-wide warning and no second affected community in `24h`.

- Pause posts and comments in the affected subreddit for `72h` and recheck its rules before returning.
- For the next `24h`, use the following account-wide recovery range; do not compensate in other communities.
- Main posts are capped at `0-1/day` during this window.
- Restore the original tier after `24h` with no new removal, warning, captcha, rate limit, or visibility failure.

| Original tier | Recovery comments/hour | Recovery comments/day |
|-|-:|-:|
| `K0 New` | `3-7` | `6-15` |
| `K1 Growing` | `6-12` | `18-45` |
| `K2 Established` | `7-15` | `30-60` |

### `R2 Repeated`

Trigger: at least two removal/filter/visibility failures across at least two communities in `24h`, or an explicit mod/Automod warning indicating a repeated pattern.

- Downgrade one full account tier for `72h`: `K2 -> K1`, `K1 -> K0`.
- `K0` cannot downgrade further: use `K0 recovery` at `2-5 comments/hour`, `4-10 comments/day`, and no main post for the first `24h`.
- During the first `24h`, all other tiers are capped at one main post; after a clean `24h`, use the downgraded tier's ordinary post window.
- Keep every affected subreddit paused for at least `7d` or until a clear rule/mod explanation resolves the cause.
- Restore one tier only after `72h` with no further removal, warning, captcha, rate limit, or visibility failure. Never catch up missed volume.

| Original tier | Temporary tier | Comments/hour | Comments/day | Posts after first clean `24h` |
|-|-|-:|-:|-:|
| `K0 New` | `K0 recovery` | `2-5` | `4-10` | `0-1/day` |
| `K1 Growing` | `K0 New` | `6-12` | `15-35` | `0-2/day` |
| `K2 Established` | `K1 Growing` | `8-16` | `25-60` | `0-3/day` |

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

Within `B/B+`, start from communities with the clearest ordinary participation path, lowest row restriction, and strongest resolved-style fit. Avoid strict-on-topic, high-removal-risk, account-gated, sensitive, or moderator-approval communities when a comparable lower-restriction target exists.

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
- `hard_stop`: captcha/rate limit/account warning, clear prohibition, immediate removal/filter, or a submitted post becomes `awaiting moderator approval`.

If an own submitted post is awaiting moderator approval, delete/withdraw it when the control exists, verify cleanup, do not repost, and stop the post lane for this round.

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
