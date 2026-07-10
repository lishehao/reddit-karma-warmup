# Browse And Vote Playbook

Load only for the `browsing` lane named `内容浏览`. This lane reads Reddit surfaces and may cast an occasional genuine vote. It never publishes comments/posts, handles Notifications, edits the profile, joins communities, or performs another lane's work.

## Browse Slot

Plan one slot around `8-12` qualified reads across `2-4` eligible communities. A qualified read means the worker opened the item, consumed the actual body/media, sampled enough thread context to understand it, and can state one specific reason for its assessment. Feed-card impressions, title-only scans, duplicates, ads, deleted/locked items, and accidental opens do not count.

Keep a rolling record:

```text
time | subreddit | url | content_type | qualified_read
topic | specific_observation | persona_fit | vote_decision | vote_score | vote_reason
eligible_views_since_vote
```

The long-run cadence target is one combined vote per roughly `8-12` qualified reads:

- A slot may cast at most `1` total vote, either up or down.
- Do not vote before reading. Do not cast both directions in one slot.
- The cadence opens a vote opportunity; it is not a quota. If no item passes, finish with `0` votes and continue reading in a later slot.
- Do not bank missed opportunities into a later burst or lower the score to preserve the ratio.

## Upvote Gate

Score only after a qualified read:

| Factor | Points | Good signal |
|-|-:|-|
| Specific quality or originality | 0-30 | a concrete useful, funny, insightful, high-effort, or constructive element |
| Declared-interest fit | 0-25 | naturally fits the truthful AR/3D/games/creative-tech/place/social interests, or the user's supplied interests |
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
- Reselect this lane's dedicated Chrome tab and confirm the intended account/URL before voting.
- After voting, refresh/reopen once and confirm the selected arrow remains active. If state is uncertain, log `unverified_vote`; do not click again blindly.
- Record every qualified read and every vote/no-vote decision. A no-vote slot is a valid completed result.

## Scheduling And Report

Execute the first browse slot immediately. For a continuing run, reconcile against the stop time and schedule one next one-shot trigger for this lane; do not create a fixed recurrence or catch up missed slots.

Use the shared compact report:

```text
本轮完成：浏览 <N> 条；Upvote <N>，Downvote <N>。
发布/处理：<r/subreddit | 投票方向 | URL>；无投票则写“未投票：没有达到门槛的内容”。
下一轮：<本地日期时间与浏览动作>。
风险：<无 | 具体异常>。
```
