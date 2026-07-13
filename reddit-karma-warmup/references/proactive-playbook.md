# Proactive Playbook

Shared proactive policy for two distinct owners. `Reddit 评论台` loads the shared account/removal/pool rules plus `Comment Candidate Gate`, `Comment Execution`, and the comment report path; it must skip all main-post sections. `Reddit 发帖台` loads the shared rules plus `Main Post Gate`, `Post Diversity`, `Beginner-Trap Angle`, and the post report path; it must skip all comment-candidate/execution sections. Neither task may absorb the other lane. Each task may apply `browse-vote-playbook.md` in incidental mode only to external content already opened for its primary work. Lifecycle, target-driven scanning, risk, and reporting come from `default-operations-sop.md` and `orchestration-core.md`.

## Account Bands

Reddit does not publish a global safe comments-per-hour or posts-per-day limit. Account age and karma are only proxies: CQS/reputation signals, email verification, network/account-security signals, recent behavior, subreddit karma, and each community's eligibility rules also matter. Use the lowest supported tier across the observable signals; age alone never upgrades an inactive or low-quality account.

| Tier | Observable operating state | Maximum comment envelope | Maximum daily envelope | Main-post window |
|-|-|-:|-:|-:|
| `K0 New` | `<50` karma; use `fresh_bootstrap` when `<48h`, blank/no-history, unverified/unknown, or visibility is uncertain | up to `10/hour` | up to `60/day` only in explicit high-volume mode | `0-2/day` |
| `K1 Growing` | `50-199` karma plus `>=7d` clean recent state | up to `16/hour` after explicit override | up to `60/day` | `0-3/day` |
| `K2 Established` | `>=200` karma plus `>=14d` clean recent state | up to `20/hour` after explicit override | up to `60/day` | `0-3/day` |

These are internal defaults, not Reddit platform limits, safety guarantees, quotas, or authority to refuse an explicit operation. Normal operations use the low/standard/high envelopes from `default-operations-sop.md`. The user's latest explicit count/intensity/duration replaces the default envelope; distribute it across the requested window, give at most one non-blocking caution when it materially exceeds the tier suggestion, and publish only passing candidates. Historical or cleared incidents never clamp the requested envelope.

Use `new-account-bootstrap.md` when `K0` is in `fresh_bootstrap`. Passing its checkpoints changes the substate to `active_new` but does not create another tier. Promote to `K1/K2` only when both the karma band and account-level health signals pass. Community removals retire only their exact subreddits; they do not demote the account tier or create a generic slowdown.

### Fresh-account default

When the user asks only to start operating and the account is `K0 fresh_bootstrap`, default to the low envelope: target `3` and cap `4` proactive comments in the first hour, no more than `12` proactive comments in the first `24h`, and `0-1` main post that day. Prefer at least `3` low-restriction communities with clear ordinary participation paths. Do not use `A`, `A0`, `No-go`, account-denylisted, approval-gated, megathread-only, local-Karma-gated, or tightly formatted communities for bootstrap publishing.

This conservative default is not a no-action state. Start the first eligible comment slot immediately. A user's explicit count, intensity, duration, or target still overrides the default after one concise caution when materially riskier; live rules and the account denylist continue to veto the exact destination.

After every verified proactive comment, use a local `60-120 sec` pause before the next publish; discovery, reading, drafting, and verification time are additional. Main posts are heavier: default to at most one main post per subreddit per `24h`. The first eligible main post of the day has no skill-level `6h` waiting gate. Only a second same-day post requires a different community and audience/angle cluster, at least `6h` separation from the first, and a clean visibility check on the earlier post.

## Explicit Daily 60 Comment Mode

This is not the default. Enable it only when the user explicitly requests about `60 comments/day`, or explicitly selects high intensity for at least `6h`. It is a planning ceiling, never a quota that lowers the candidate threshold.

- All tiers may plan toward `60/day` only while clean and explicitly authorized. Use at least a `6h` operating window for the full target.
- For a shorter window, target at most `10 x available hours`; do not compress missed comments into a burst.
- High intensity starts with a `6-10` passing-comment first-hour envelope. The comment task records and verifies its own first permalink without an external acceptance task.
- After the first hour, continue within the selected high envelope. A subreddit visibility/removal failure retires only that subreddit; only an `R3` account-level signal disables this mode.
- Prefer at least `6` communities and `3` clusters across a 60-comment day when the eligible pool supports it; avoid more than `5` proactive comments in one subreddit per `24h`.
- Keep the normal `Act >=80`, truthfulness, copy-length, history, and `60-120 sec` post-submit pause. If the initial pool is short, continue the target-driven expansion loop; finish below target only at the deadline or a concrete blocker, never by lowering the gate.
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
- Add one consolidated non-blocking notice to this task's next report; do not ask the user for permission to continue.
- Continue in unaffected eligible communities at the same account tier, comment envelope, and post window.
- Do not impose a `24h/72h` account cooldown, Daily 60 shutdown, generic rate reduction, or account-wide post cap from removals alone.
- Inspect whether the removed items shared an avoidable rule/format mismatch before drafting the next item, but do not treat that review as a pause or lower the candidate threshold.
- Reopen a retired subreddit only after an explicit user decision backed by a clear moderator/rule explanation.

### `R3 Account Stop`

Trigger: the current Chrome/Reddit surface explicitly shows an active captcha, sitewide rate limit, lock/suspension, account-wide warning, login mismatch, credential request, or spam/automation-abuse restriction. A past or already-cleared event never triggers `R3`.

- Pause only the actions the active state makes impossible and preserve the user's latest mission unchanged.
- For a visible timed rate limit, wait until the displayed expiry using the current turn or the lane's existing Heartbeat as appropriate, re-probe once, and automatically resume the original mission. Do not ask for confirmation.
- For captcha, credentials, login mismatch, or a persistent lock/warning that requires user repair, ask for the exact repair directly in this task; after the state clears, automatically resume the latest mission unless the user changed or stopped it.
- Do not impose a `24h/72h` recovery tier, lower comment/post envelope, or recovery preset after resumption. Defaults remain advisory and the user's explicit command remains controlling.
- A dropped Chrome connection alone is not `R3`; reconnect and verify whether the prior action posted before retrying.

## Role Gate

- A handoff with `lane=comments` is accepted only by `Reddit 评论台`; execute comment sections and ignore every post target/section.
- A handoff with `lane=posts` is accepted only by `Reddit 发帖台`; execute post sections and ignore every comment target/section.
- There is no mixed proactive worker. Broad `运营` enables two independent tasks with separate targets, tabs, proof, and ledgers; never count comments as posts or let one task backfill the other.
- An off-role request is not forwarded. Tell the user the canonical task title for that lane and do not reinterpret it locally.

## Active Pool Gate

User-provided targets override the bundled pool. Otherwise query `loci-subreddit-pool-v1.md` through the progressive retrieval protocol in `publish-consistency.md`; do not load the entire archive. Use `operation-style-profiles.md` to rank direction fit and `publish-consistency.md` to build the eligible pool.

Before opening any candidate subreddit, load `account-community-denylist.md`. A matching entry is a hard destination veto even when the user supplies a broad topic or the archive ranks it highly. Do not open, read, vote, join, comment, post, test access, or revalidate that subreddit unless the user explicitly removes the denylist entry.

- `B`: eligible when the row and live context fit.
- `B+`: ordinary comments and low-frequency feedback/demo contexts when row rules fit.
- `A`: research-first; interact only for a clear ordinary non-product reason.
- `A0` and `No-go`: read-only; no post, comment, vote, join, flair, or warm-up action.

For `K0 fresh_bootstrap`, narrow this further: use only `B/B+` rows whose live rules show an ordinary participation path without special approval, local/community Karma, mandatory megathread placement, or unusually rigid formatting. Treat stricter rows as unavailable for bootstrap rather than spending the slot probing them.

Within `B/B+`, start from communities with the clearest ordinary participation path, lowest row restriction, and strongest resolved-style fit. A retired subreddit is closed for future outward actions. Retirements in other communities carry no account-tier, pacing, or candidate-score penalty.

Treat rule friction as a routing cost:

- low friction: clear on-topic/civility rules and ordinary comments or native posts; use first
- medium friction: required flair/title/format or narrow topical fit, but an ordinary participation path remains; use sparingly after low-friction options
- high friction: moderator approval, local/community Karma, mandatory megathread, infrequent developer/self-promo windows, subjective anti-promotion/showcase enforcement, or multiple special placement rules; do not proactively visit in default operations

An `A` row is not a default operating destination. Open it only when the user explicitly targets it or when low/medium-friction `B/B+` options are exhausted and the stored row already shows a clear ordinary non-product participation path. Never visit `A0`, `No-go`, retired, or account-denylisted communities merely to see whether access or rules changed.

Prefer `New` and `Rising` for early comment opportunities. Use `Hot` and `Top` to learn community language and survivor patterns.

## Comment Candidate Gate

Score the exact post and intended parent comment, not only the subreddit.

| Factor | Points | Simple question |
|-|-:|-|
| Exact context relevance | 0-25 | Did we read the actual post/parent and understand the point? |
| New value available | 0-25 | Can we add one thing not already repeated? |
| Freshness and visibility | 0-20 | Is the thread still alive enough for the reply to be seen? |
| Community/account fit | 0-15 | Does it naturally fit the subreddit and truthful account history? |
| Rules and truthfulness | 0-15 | Is it permitted, non-promotional, and free of invented experience? |

- `Act`: `>=80`; if replying to a particular comment, target fit should be `>=82`.
- `Watch`: `68-79`; read/learn, do not force a reply.
- `Skip`: `<68`, stale, saturated, unsafe, generic, or dependent on fake experience/product mention.

For a fast-rising topic, also require a clear current hook: the thread is still young, the reply adds something not already dominant, and the topic is native to the subreddit. Search the exact current topic when freshness affects correctness; turn research into one compact insight rather than a source dump.

The comment target is the slot's primary completion condition. A qualified candidate read requires opening the exact post, reading its body/media and enough existing comments to score non-duplication; title-only impressions do not count. After every `Watch`/`Skip`, continue the `Target-Driven Scan Loop` in `default-operations-sop.md`. Reaching the candidate-read floor with fewer verified comments requires broader discovery. Preserve the exact remaining comment count across Heartbeats and stop short only at the authorized deadline, explicit user stop, or a current hard blocker after expansion and recovery were attempted.

## Comment Execution

1. Open the exact post and run the quick rule glance required by `publish-consistency.md`; do not reuse a stale or uncertain rule assumption.
2. Read the full post/media, intended parent, and enough nearby replies to record `context_detail`, `duplicate_to_avoid`, and `local_voice_sample`.
3. Score the candidate, compare history, and run Double-Check A. Missing rule/context/voice evidence is `Watch`, not permission to draft.
4. Load `outbound-copy-gate.md`; read the last `10` measured comment/reply lengths, then generate internal micro/one-liner/two-beat alternatives from the same specific hook.
5. Prefer one specific observation, distinction, useful question, or precise praise. Choose the shortest passing alternative and use context-native Reddit shorthand/fragments where they genuinely fit.
6. Enter the draft only after the evidence and copy gates pass, then run Double-Check B.
7. Reselect this lane's dedicated Reddit tab, verify account/target, wait `18-70 sec`, submit, and verify permalink/profile visibility.
8. Measure the exact published text and append `char_count`, `word_count`, `sentence_form`, `length_tier`, `why_this_length`, and the four pre-draft evidence fields to history and follow-up state. After a verified proactive comment, use a local `60-120 sec` pause before the next publish; first follow-up is normally `20-40 min` later.
9. During a new start, use the selected intensity envelope. Respect subreddit/cluster diversity and do not lower the candidate threshold to fill the target.

Before drafting, independently score the already qualified-read post or parent through the incidental mode in `browse-vote-playbook.md`. A passing natural vote may be cast once, but there is no vote target and submitting a comment never requires a vote. Comment score never becomes vote score; do not read extra items or delay the comment to hunt for votes.

Comments should be mostly short, while longer replies remain available when the target genuinely needs explanation. Do not default to two polished sentences, mechanically rotate lengths, add filler, summarize the post, repeat top comments, or mention Loci/product links unless the user explicitly requests it and rules permit it.

## Default Conservative Post Tendency

Unless the user supplies another angle, start with `beginner-common-mistake`: one narrow question about a mistake, misleading assumption, premature optimization, or setup choice that many members personally encountered and can answer from experience. This is a community-memory prompt, not a generic request for tips.

Priority order:

1. common beginner mistake with a delayed consequence
2. workflow friction that appears after the first simple success
3. a concrete tool/setup tradeoff with two plausible choices
4. a specific observation or artifact question when beginner prompts do not fit

Use this default only when the subreddit has a real skill threshold and recent native advice/discussion posts survive. Before drafting:

- search the subreddit for the exact topic and close variants; skip if it is an FAQ, pinned topic, recurring low-effort question, or substantially duplicated in the recent active window
- identify the community-specific object, decision, and consequence; reject a question that could be pasted unchanged into another subreddit
- prefer questions that invite short personal stories or contrasting lessons, not one canonical factual answer
- never pretend to have used a tool, shipped a project, made a mistake, or be a beginner when that is untrue; ask directly or frame it as an observation
- never use helplessness, deliberate factual errors, fake urgency, or obvious bait to manufacture corrections
- keep the title self-contained and the body to zero or a short context line plus one clear ask when live survivor patterns support it

Strong forms:

- `What's the Unity mistake that feels harmless in a prototype but hurts once you try to ship?`
- `What do new Blender users usually optimize way too early?`
- `Which Quest performance "fix" tends to create a worse problem later?`

Weak forms: `I'm new, any tips?`, `What mistakes should I avoid?`, or the same template with only the subreddit noun replaced.

## Main Post Gate

Choose subreddit + audience + angle after history comparison and before drafting. Treat this live same-day preflight as the post-specific part of Double-Check A:

After live eligibility is known, score the exact subreddit + audience + angle:

| Factor | Points | Simple question |
|-|-:|-|
| Live rules and eligibility | 0-25 | Are age/Karma, flair, format, placement, and promotion rules clearly satisfied? |
| Audience and pain fit | 0-25 | Does this community actually care about the post's problem or experience? |
| Current demand and timing | 0-20 | Do recent live posts/comments show current interest in this angle? |
| Native format fit | 0-15 | Does the shape match recent surviving posts without copying them? |
| Originality and account coherence | 0-15 | Is it distinct from recent history and truthful for this account? |

`pass` requires `post_candidate_score >=82`, at least `20/25` on live rules and eligibility, and no mandatory-rule conflict. `watch` is `70-81`: continue research or retarget. `skip_candidate` is `<70` or any live eligibility blocker. A high total never overrides a failed mandatory rule.

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
- `recover_lane`: a sitewide timed rate limit or temporary technical/account state prevents submission now; preserve the mission/Heartbeat, continue permitted work, and re-probe automatically.
- `hard_user_repair`: only credentials, persistent login/account mismatch, manual CAPTCHA/challenge, explicit lock/suspension/required acknowledgement, or Chrome control unavailable across three recovery wakes. Unsafe/deceptive content is abandoned or rewritten; it never blocks the mission. Past/cleared evidence is never sufficient.

On `retire_subreddit`, a pending-review own post must be deleted/withdrawn immediately without confirmation. Confirm the native deletion dialog when shown, accept one visible deleted/missing result as cleanup proof, never repost there, send the non-blocking retirement notice, and continue the same lane in another eligible community. If the cleanup route fails, queue only that exact permalink for automatic recovery/retry while post discovery continues elsewhere; do not ask the user or pause this lane or any sibling lane.

The post target is an execution objective. A failed candidate causes immediate retargeting and continued live scanning while the slot and authorized window remain. Do not treat one subreddit preflight, one pending-review deletion, or one weak angle as completion. Finish below target only after the target-driven expansion stages are exhausted by the deadline or a current concrete post-lane blocker remains.

Recent external posts already opened during research receive one independent incidental vote assessment through `browse-vote-playbook.md`. Never vote on the account's own post, affiliated content, moderator/Automod content, or merely because a source inspired the draft. There is no vote target and no extra browsing for votes.

After drafting, run Double-Check B on the final title/body/flair, live submit state, history, length/structure, and duplicate-send risk before clicking Post.

## Post Diversity

For multiple planned posts, vary both community cluster and angle when viable:

- builder/product
- creator/dev/3D
- AR/VR/spatial
- social/AI/companion
- place/outdoor/location
- competitor/product communities

Diversity never justifies a weak target. Keep widening the eligible live search while time remains; publish fewer only when the authorized deadline arrives without a second passing community.

## Beginner-Trap Angle Gate

This gate specializes the default tendency. Use beginner-trap questions only where members share a real skill threshold and recent survivor posts show an advice culture. Require:

- a concrete domain/workflow mistake
- at least two recent examples of tips, mistakes, critique, or `what I wish I knew`
- no FAQ, low-effort-question, survey, or beginner-post prohibition
- no product, waitlist, or fake expertise needed
- no invented novice identity or fabricated personal mistake
- no recent duplicate or FAQ answer that makes the post redundant

Strong: `What's the Unity beginner trap that only shows up once you try to ship?`

Weak: `Any tips for beginners?`

## Proactive Slot Report

On a direct user command or execution-heartbeat resume, work the assigned comment or post target immediately. A slot is complete only when its verified action target is met or a terminal condition is reached. If runtime must yield first, record an interim progress checkpoint and schedule continuation of the same remaining target; a no-action scan is not completed-slot proof. Planning another window is not a completed slot.

Use the three-line compact report from `orchestration-core.md`:

- `本轮完成`：写本任务已完成的评论或主帖、`verified/target`、剩余数量、附带投票数量、subreddit 和 permalink；未达目标时明确标为“进行中”
- `下一轮心跳`：核验后的本地日期时间、时区及 UTC
- `下轮计划`：仅写本任务下一轮评论或发帖工作及目标数量

Keep candidate scores, `insight_basis`, final text/translation, preflight, Check A/B, and history/length comparisons in the internal action log. Show them only when the user asks or they explain a risk or missing action.
