# Lane Action Ownership

This is the single authority for which Reddit task may perform each action.
Load it in the distributor and every execution lane before mission acceptance.
Lane ownership is a hard authorization boundary, not a pacing preference.

## Ownership Matrix

| Lane | May read | May mutate | Never does |
|-|-|-|-|
| `comments` / `Reddit 评论台` | candidate posts, parent comments, nearby replies, rules, account history | proactive comments only | Upvote, Downvote, main posts, notifications work |
| `posts` / `Reddit 发帖台` | listings, rules, survivor posts, submit requirements, account history | native main posts and required withdrawal cleanup only | Upvote, Downvote, comments, notification replies |
| `follow-up` / `Reddit 跟进台` | Notifications, supplied/known permalinks, recent own posts/comments, exact inbound chains | replies and required withdrawal cleanup only | Upvote, Downvote, proactive discovery, main posts |
| `browsing` / `Reddit 浏览台` | authorized listings, posts, media, comment context, rules | independently gated Upvote or Downvote only | comments, replies, main posts, profile changes |
| `presence` / `Reddit 主页台` | profile/community presence surfaces | authorized profile, Join/subscribe, Flair/tag actions | Upvote, Downvote, comments, replies, main posts |

Reading remains part of comments, posts, and follow-up because those lanes need
context and qualified-read objectives. That reading never creates permission to
touch a vote control.

## Mission Contract

For `comments`, `posts`, `follow-up`, and `presence`, every mission and restored
checkpoint must resolve:

```text
vote_policy=DISABLED_BY_LANE
vote_cap=0
upvote_count=0
downvote_count=0
vote_target=<absent>
browse_vote_playbook=NOT_LOADED
```

These lanes do not inspect, score, focus, click, or verify Upvote/Downvote
controls. They do not carry an explicit vote remainder, and vote state is never
part of their completion condition or report.

Only `browsing` may resolve:

```text
vote_policy=BROWSING_ONLY
vote_target_mode=opportunity|hard
vote_target=<absent unless explicitly supplied>
vote_cap=<resolved browsing cap>
upvote_count + downvote_count
browse_vote_playbook=LOADED
```

## Routing Explicit Vote Requests

- A distributor command that includes comments/posts/follow-up plus voting
  becomes separate missions: the text lane receives no vote fields or ability,
  and the explicit vote portion goes to `Reddit 浏览台`.
- A broad `开始/运营` command still creates only comments, posts, and follow-up;
  it does not imply a browsing/vote mission.
- A vote request issued inside a non-browsing lane is off-lane. Do not forward
  or execute it there; briefly identify `Reddit 浏览台` as the canonical task.
- Never merge lanes because a browsing task is unavailable. Report only that
  requested lane as unresolved and continue every other authorized lane.

## Reused Checkpoints

When a non-browsing task loads a legacy checkpoint containing vote counters,
preserve them as historical evidence only. For the new mission revision set
`vote_policy=DISABLED_BY_LANE`, zero the current mission's vote counters/cap,
remove every vote target/remainder, and never replay or continue an old vote.

A browsing task owns its own vote history and mutation uncertainty. No text lane
may read that state to justify a vote, and the browsing task never publishes
text while validating a vote.
