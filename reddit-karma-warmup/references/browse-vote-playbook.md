# Browse And Vote Playbook

Load for `Reddit 浏览台` and for per-round vote targets inside comments, posts, and follow-up tasks. The browsing lane never publishes text. Other lanes retain their own candidate surfaces while using the same independent score, eligibility, pre-click state, one-click, target, and ledger rules.

## Two Modes

- `explicit_browse`: user explicitly requested pure browsing/voting. Use the read floor, vote target/cap, scan expansion, scheduling, and browse report below.
- `lane_round`: comments, posts, or follow-up use a hard per-round vote target on eligible external items inside that lane's normal surfaces. Resolve low `2/2`, standard `2/4`, or high `4/6` as combined target/cap. Continue lane-local candidate scanning while `vote_target_remaining > 0`; never switch to unrelated feeds or weaken the gate.

## Browse Slot

Select the slot budget from the operation contract:

| Intensity | Initial qualified-read floor | Default combined-vote target | Default cap |
|-|-:|-:|-:|
| `low` | `12-18` | `2` | `2` |
| `standard` | `20-30` | `2` | `4` |
| `high` | `30-45` | `4` | `6` |

An explicit user read count, combined vote target, vote cap, directional Upvote/Downvote target, interval/range, or browse-only instruction overrides the corresponding default. Upvote and Downvote are always separate counters. By default their accepted sum fills the hard target; never force one of each. If exact directional targets are supplied, each direction has its own remainder and both must pass for normal completion. The read number is the first checkpoint, not a maximum. If only a vote target is supplied, set a reasonable initial floor that can evaluate enough independent items.

Spread a standard slot across roughly `3-6` eligible communities. Use the resolved operation style to bias discovery, while preserving diversity and skipping unrelated targets. A qualified read means the worker opened the item, consumed the actual body/media, sampled enough thread context to understand it, can state one specific reason for its assessment, and kept the readable candidate open for the measured `30 sec` minimum in `interaction-pacing.md`. Feed-card impressions, title-only scans, sub-30-second opens, duplicates, ads, deleted/locked items, and accidental opens do not count.

Keep a rolling record:

```text
time | subreddit | url | content_type | qualified_read
topic | specific_observation | persona_fit | vote_decision | vote_score | vote_reason
eligible_views_since_vote | vote_result = vote_accepted | existing_vote | no_vote | explicit_failure
```

Use the slot's combined-vote target as a hard completion objective:

- Standard operation seeks at least `2` accepted votes in the slot and may continue up to the cap when more independently qualified items pass.
- Any mix of Upvote and Downvote is allowed; never force one of each or balance directions artificially.
- Do not vote before reading or before `candidate_dwell_seconds >=30`. One item may receive only one direction, and each decision needs its own score and reason.
- In `explicit_browse`, normal completion requires both the combined-vote target and qualified-read floor. In `lane_round`, normal completion requires the primary lane objective plus the combined or explicit directional vote target. Reaching one without the other means continue within eligible lane-local surfaces; when the vote cap is reached first, continue without further vote mutations and report any directional shortfall.
- Reaching the initial read floor below target means widen the live scan through more eligible communities, current `New`/`Rising`, recent `Hot`, and deeper comment context; it is not completion.
- Finish below target only at the deadline or a current concrete blocker after those expansion stages. Report the exact qualified-read count and do not lower thresholds.
- Do not bank missed votes into a later burst or exceed the cap unless the user explicitly changes it.

## Upvote Gate

Score only after a qualified read:

| Factor | Points | Simple question |
|-|-:|-|
| Specific value or originality | 0-30 | Is there something concretely useful, funny, insightful, or high-effort? |
| Interest fit | 0-25 | Does it naturally fit the declared truthful interests? |
| Community contribution | 0-20 | Does it improve this subreddit rather than bait engagement? |
| Context confidence | 0-15 | Was the body/media and enough discussion actually read? |
| Account coherence | 0-10 | Does the vote fit visible account interests without invented identity? |

Choose `upvote` only at `>=82` with one specific reason. Otherwise choose `no_vote`.

## Downvote Gate

Downvote is not a disagreement button. Score only an item with a concrete negative signal:

| Factor | Points | Simple question |
|-|-:|-|
| Clear non-contribution | 0-35 | Is it spam, unrelated solicitation, hostility, or content adding nothing? |
| Harm or deception evidence | 0-30 | Is there concrete manipulation, harassment, scam, or material deception? |
| Rule/context mismatch | 0-20 | Is an obvious violation visible from current community context? |
| Confidence | 0-15 | Was enough evidence read beyond the title or viewpoint? |

Choose `downvote` only at `>=92`. Ordinary disagreement, competitor content, criticism of Loci, unfamiliar opinions, low production value, or personal dislike always resolve to `no_vote`.

## Eligibility And Verification

- Use `B/B+` communities first. `A` remains research-first and may receive a vote only for an unmistakably ordinary native reason. `A0/No-go` is read-only with no votes.
- Never vote on own content, affiliated/team content, moderator/Automod content, a supplied campaign target, or the same target from another account. Never coordinate votes.
- Reselect this lane's dedicated Chrome tab and confirm the intended account/URL. Require exactly one intended Upvote/Downvote control that is visible and enabled.
- Before clicking, inspect the intended controls once. If either direction is already explicitly selected, record `existing_vote` and do not click. If selected state cannot be determined reliably, record `no_vote`; do not risk toggling an existing vote.
- Click each target at most once. A click call that returns without an exception after this preflight is final `vote_accepted` evidence and immediately counts toward the slot.
- After the click, do not inspect selected styling, `aria-pressed`, score change, `upmod/downmod`, reload persistence, profile history, or another surface to reconfirm a vote. Do not reopen the target for vote verification and do not maintain stronger/weaker vote evidence levels.
- Never click again because the post-click state is hidden, unchanged, ambiguous, or no longer readable. A successful click call remains accepted unless that same call returns an explicit failure.
- Record `explicit_failure` only for a click exception, Reddit error/banner, account mismatch/logout, captcha, sitewide rate limit, warning, lock, or an unavailable/ambiguous control before click. Do not ask the user to confirm whether a normal click worked.
- `ERR_BLOCKED_BY_CLIENT` on one page/control is a recoverable route failure: apply `orchestration-core.md` Chrome recovery, then continue the slot through another eligible native Reddit route when needed. Do not convert one blocked route into a lane-wide stop or count unqualified impressions toward the read budget.
- Record every qualified read and every vote/existing-vote/no-vote decision. In either mode, a below-target round is terminal only after the authorized window ended or a concrete blocker/scope exhaustion appeared, with the scan stages and exact Upvote/Downvote shortfall documented. `no_vote` is a valid candidate decision but never fills the hard accepted-vote target.

## Scheduling And Report

In `explicit_browse`, execute the first browse slot immediately. Every execution-heartbeat resume must also complete its current qualified-read slot and record the read/vote/no-vote result as `slot_proof` before scheduling another trigger. In `lane_round`, the vote remainder travels with that lane's current round and its own Heartbeat; it never creates a separate browsing timer.

For a continuing run:

1. Use the user's interval or range when supplied.
2. Otherwise select a fresh whole-minute delay from `20-40 min` after the current slot completes. Do not reuse a fixed repeating interval.
3. Convert that delay into one exact local and UTC `next_due_at`, reconcile it against the stop time, and update/reuse this browsing task's own recurring Heartbeat.
4. Do not create a fixed recurrence, schedule from the prior slot's start time, or catch up missed slots.
5. Carry the one-click `vote_accepted` rule into the continuation Heartbeat. Never regenerate selected-state, reload, persistence, or user-confirmation checks.

Use the shared compact report:

```text
本轮完成：有效阅读 <N> 条（初始下限 <N>）；Upvote <N>/<目标或“合计目标”>，Downvote <N>/<目标或“合计目标”>，合计 <N>/<硬目标>；附关键 r/subreddit/URL；未达到目标则写明扩展扫描范围、差额和原因。
下一轮心跳：<本地日期时间、时区及 UTC；结束则写“无，任务已结束”>。
下轮计划：<下轮阅读预算、投票目标与候选范围；结束则写“无”>。
```
