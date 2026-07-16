# Browse And Vote Playbook

Load in `Reddit 浏览台` and in `lane_round` mode for comments, posts, and follow-up. Numeric read targets, vote caps, and score thresholds come only from `operation-defaults.json`.

## Modes

- `explicit_browse`: complete the intensity-sized hard qualified-read target. Voting is opportunity-only unless the user supplied a vote count.
- `lane_round`: use the primary lane's own hard read objective and candidate surfaces. Do not add the explicit-browse read target and never leave the lane's normal surfaces.

For both modes, default `vote_target_mode=opportunity`: there is no default vote count target. The intensity vote cap is always a hard ceiling. An explicit combined or directional vote count becomes a hard target under the resolved cap.

## Qualified Reading

An explicit browse slot resolves its exact hard target from `browsing.<intensity>.qualified_read_target` in `operation-defaults.json`. Higher intensity increases real reading, community coverage, and thread depth rather than default vote mutations. A target is a minimum completion condition, not a maximum.

A qualified read opens the item, consumes actual body/media, samples enough thread context to understand it, records one specific observation, and passes the measured dwell in `interaction-pacing.md`. Feed impressions, titles, sub-floor opens, duplicates, ads, deleted/locked items, and accidental opens do not count.

Standard explicit browsing normally spans three to six eligible communities. High browsing should deepen promising threads, including substantive replies, instead of rapidly flicking through cards. Never shrink the per-candidate dwell to meet the target.

Record:

```text
time + subreddit + url + content_type + qualified_read
topic + specific_observation + persona_fit
vote_decision + vote_score + vote_reason + vote_result
upvote_count + downvote_count + vote_cap_remaining
```

## Upvote Gate

Score after a qualified read:

| Factor | Points |
|-|-:|
| Specific value or originality | 0-30 |
| Interest fit | 0-25 |
| Community contribution | 0-20 |
| Context confidence | 0-15 |
| Account coherence | 0-10 |

Choose `upvote` only when the score reaches `votes.upvote_score_min` with one specific reason; otherwise `no_vote`.

## Downvote Gate

Downvote is not a disagreement button:

| Factor | Points |
|-|-:|
| Clear non-contribution | 0-35 |
| Harm or deception evidence | 0-30 |
| Rule/context mismatch | 0-20 |
| Confidence | 0-15 |

Choose `downvote` only when the score reaches `votes.downvote_score_min`. Competitor content, criticism, unfamiliar opinions, low production value, ordinary disagreement, or personal dislike are always `no_vote`.

## Eligibility And One-Click Evidence

- Use eligible `B/B+` destinations first. `A` is research-first and may receive a vote only for an unmistakably ordinary native reason. `A0`, No-go, research-only, retired, and denylisted destinations receive no votes.
- Never vote on own, affiliated/team, moderator/Automod, supplied campaign, or coordinated target content.
- Confirm the exact account/URL and exactly one intended visible enabled control.
- Inspect selected state once before clicking. If either direction is already selected, record `existing_vote`; if ambiguous, record `no_vote`.
- Click at most once. A click call that returns without exception after preflight is `vote_accepted` and counts immediately.
- Do not inspect styling, score change, reload persistence, profile history, or another surface after the click. Never click again because post-click state is hidden or ambiguous.
- Record `explicit_failure` only for an exception, Reddit error/banner, account mismatch, CAPTCHA, sitewide limit, warning, lock, or unavailable/ambiguous control before click.

Upvote and Downvote remain separate report counters even when both are zero.

## Completion And Scheduling

In `explicit_browse`, normal completion requires the hard qualified-read target and any explicit hard vote target. Without an explicit vote target, do not keep scanning after the read target solely to cast a vote. Finish below an explicit target only at deadline or a current concrete blocker after eligible expansion; never lower the score gate.

In `lane_round`, the vote assessment is incidental to the primary lane's normal reads. A default opportunity vote never creates another read target, another timer, or extra vote hunting. An explicit vote target travels with that lane's mission and remains restricted to its normal surfaces.

For continuing explicit browsing, choose the next whole-minute delay from `browsing.default_cadence_minutes` after the slot completes, convert to exact local/UTC time, and update the browsing task's own Heartbeat. Do not catch up missed slots.

Report qualified reads/target, Upvote count, Downvote count, hard cap, optional explicit target progress, key links, next verified wake, and next scope.
