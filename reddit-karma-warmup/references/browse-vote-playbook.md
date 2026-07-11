# Browse And Vote Playbook

Load only for the `browsing` lane task named `Reddit 浏览台`. This lane reads Reddit surfaces and may cast an occasional genuine Upvote or Downvote. It never publishes comments/posts, handles Notifications, edits the profile, joins communities, or performs another lane's work.

## Browse Slot

Select the slot budget from the operation contract:

| Intensity | Qualified-read budget | Default combined-vote target | Default cap |
|-|-:|-:|-:|
| `low` | `12-18` | `2` | `2` |
| `standard` | `20-30` | `2` | `4` |
| `high` | `30-45` | `4` | `6` |

An explicit user read count, vote target, vote cap, interval/range, or browse-only instruction overrides the corresponding default. If only a vote target is supplied, set a reasonable read budget that can evaluate enough independent items; do not promise that every target will pass.

Spread a standard slot across roughly `3-6` eligible communities. Use the resolved operation style to bias discovery, while preserving diversity and skipping unrelated targets. A qualified read means the worker opened the item, consumed the actual body/media, sampled enough thread context to understand it, and can state one specific reason for its assessment. Feed-card impressions, title-only scans, duplicates, ads, deleted/locked items, and accidental opens do not count.

Keep a rolling record:

```text
time | subreddit | url | content_type | qualified_read
topic | specific_observation | persona_fit | vote_decision | vote_score | vote_reason
eligible_views_since_vote | vote_runtime_stability | verification_level
```

Use the slot's combined-vote target as an active search objective:

- Standard operation seeks at least `2` verified votes in the slot and may continue up to the cap when more independently qualified items pass.
- Any mix of Upvote and Downvote is allowed; never force one of each or balance directions artificially.
- Do not vote before reading. One item may receive only one direction, and each decision needs its own score and reason.
- Continue until the target is reached or the read/time budget is exhausted. If too few items pass, finish below target, report the shortfall, and do not lower thresholds.
- Do not bank missed votes into a later burst or exceed the cap unless the user explicitly changes it.

## Upvote Gate

Score only after a qualified read:

| Factor | Points | Good signal |
|-|-:|-|
| Specific quality or originality | 0-30 | a concrete useful, funny, insightful, high-effort, or constructive element |
| Declared-interest fit | 0-25 | naturally fits the resolved truthful operation style or the user's supplied interests |
| Community contribution | 0-20 | useful to the subreddit and not merely engagement bait |
| Context confidence | 0-15 | body/media and enough surrounding discussion were actually read |
| Account coherence | 0-10 | the action fits prior visible interests without inventing an identity |

Choose `upvote` only at `>=82` with one specific reason. Otherwise choose `no_vote`.

## Downvote Gate

Downvote is not a disagreement button. Score only an item with a concrete negative signal:

| Factor | Points | Good signal |
|-|-:|-|
| Clear non-contribution | 0-35 | spam, unrelated solicitation, hostility, or content that adds nothing |
| Harm or deception evidence | 0-30 | materially misleading claim, manipulation, harassment, or scam pattern |
| Rule/context mismatch | 0-20 | obvious violation visible from the current community context |
| Confidence | 0-15 | enough evidence was read; no guess based on title or viewpoint |

Choose `downvote` only at `>=92`. Ordinary disagreement, competitor content, criticism of Loci, unfamiliar opinions, low production value, or personal dislike always resolve to `no_vote`.

## Eligibility And Verification

- Use `B/B+` communities first. `A` remains research-first and may receive a vote only for an unmistakably ordinary native reason. `A0/No-go` is read-only with no votes.
- Never vote on own content, affiliated/team content, a supplied campaign target, or the same target from another account. Never coordinate votes.
- Reselect this lane's dedicated Chrome tab and confirm the intended account/URL. Require exactly one intended vote control that is visible and enabled before clicking.
- Click each target at most once. A click call that resolves without an exception after the preflight above is `interaction_confirmed` and counts toward the slot. If the immediate UI also exposes `aria-pressed`, selected styling, `upmod/downmod`, score change, or an equivalent intended active state, upgrade it to `state_confirmed`.
- Reload/reopen is not required after every vote. At most once per slot, optionally sample persistence when the UI is stable. If the post-reload DOM does not expose vote state but there is no opposite state or Reddit error, log `state_unobservable_after_reload`; keep the vote counted, continue the slot, do not click again, and do not ask the user.
- When the user has explicitly confirmed that this Chrome/account voting path is stable, store `vote_runtime_stability=user_confirmed` for the mission. Do not ask for repeated confirmation unless a concrete failure below occurs.
- Stop the affected voting action only for a click exception, an explicit opposite-state result, Reddit error/banner, account mismatch/logout, captcha, rate limit, warning, lock, or an unavailable/ambiguous control before click. A merely hidden post-reload state is not a failure.
- `ERR_BLOCKED_BY_CLIENT` on one page/control is a recoverable route failure: apply `orchestration-core.md` Chrome recovery, then continue the slot through another eligible native Reddit route when needed. Do not convert one blocked route into a lane-wide stop or count unqualified impressions toward the read budget.
- Record every qualified read and every vote/no-vote decision. A below-target or no-vote slot is valid only after the configured read/time budget was actually exhausted or a concrete blocker appeared.

## Scheduling And Report

Execute the first browse slot immediately. Every execution-heartbeat resume must also complete its current qualified-read slot and record the read/vote/no-vote result as `slot_proof` before scheduling another trigger.

For a continuing run:

1. Use the user's interval or range when supplied.
2. Otherwise select a fresh whole-minute delay from `20-40 min` after the current slot completes. Do not reuse a fixed repeating interval.
3. Convert that delay into one exact local and UTC next-run time, reconcile it against the stop time, and update/reuse this lane's logical timer for that one-shot due time.
4. Do not create a fixed recurrence, schedule from the prior slot's start time, or catch up missed slots.
5. Carry `vote_runtime_stability` and this verification policy into the continuation heartbeat. Never regenerate the old rule that hidden reload state stops the mission or requires user confirmation.

Use the shared compact report:

```text
本轮完成：浏览 <N>/<阅读预算> 条；Upvote <N>，Downvote <N>；附关键 r/subreddit/URL；未达到目标则写明差额和原因。
下一轮心跳：<本地日期时间、时区及 UTC；结束则写“无，任务已结束”>。
下轮计划：<下轮阅读预算、投票目标与候选范围；结束则写“无”>。
```
