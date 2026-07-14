# Operation Request Router

Use in the reusable distributor to split each direct dispatch request, and in a lane task to normalize only that lane's later request.

## Defaults

- missing duration: `3h`
- missing intensity: `standard`
- missing style: `mixed`
- missing account direction: resolve the broad default in `account-direction.md`
- missing comment pacing: `clustered_windows`
- comment cluster completion floor: `minimum_completed_cluster_size=2`
- missing post angle: `beginner-common-mistake`
- broad `开始/运营`: comments + posts + follow-up
- browsing: only when the user explicitly requests pure browsing, voting, feed reading, Upvote, or Downvote
- presence: only when explicitly requested or the first profile baseline is incomplete

Resolve style through `operation-style-profiles.md`. Explicit user counts, duration, language, pool, style, or lane replace defaults without another confirmation.

When total comment count and hourly rate conflict, the latest explicit user quantity controls. If both appear in the same instruction, treat the total count plus duration as authoritative, compute `effective_hourly_rate = total / hours`, and report the mismatch once without blocking. Example: `80 comments / 10h = 8/hour`; `10/hour for 10h = 100 comments`.

Planning targets are quality-gated. Resolve every range to one exact `action_target` and one `action_cap` before the first slot. The action target is the primary completion condition inside the authorized window; the cap is the most that lane may publish or cast without a new user instruction. A candidate-read floor is a discovery-depth checkpoint, never a substitute for the action target and never a reason to stop early.

| Intensity | Comment target/cap; candidate-read floor | Post target/cap; research floor | Follow-up | Browse floor; vote target/cap |
|-|-|-|-|-|
| low | `3/4 per hour`; `9` | `1/1 per session`; `3` subreddit-angle candidates with `5` survivor samples each | full sweep every `45-60m` | `12`; `2/2` |
| standard | `5/6 per hour`; `15` | `1/1 every 2-3h`; `3` subreddit-angle candidates with `5` survivor samples each | full sweep every `30-45m` | `20`; `2/4` |
| high | `8/10 per hour`; `24` | `1/1 every 60-90m`; `4` subreddit-angle candidates with `5` survivor samples each | full sweep every `20-30m` | `30`; `4/6` |

An explicit user count replaces both the corresponding target and cap unless the user separately provides a cap. Follow-up is demand-driven: its target is to inspect every required surface and process every passing `Act`, not to manufacture a reply count. Presence uses its own playbook ceiling and exact requested target.

For proactive comments, decompose every target of `2+` into windows whose planned sizes are all at least `2`. Examples: `3 -> 3`, `5 -> 2+3`, `8 -> 3+2+3`. `single_comment_cluster=forbidden`: after the first verified comment in a window, continue discovery and publishing until at least the second verified comment before yielding, reporting a completed window, or scheduling the next Heartbeat. A user instruction explicitly requesting exactly `1` total comment is a single-action mission, not a cluster, and is the only count-based exception. User stop, deadline, or a current hard blocker may interrupt a window after one action, but it remains `cluster_incomplete` with its remainder preserved; never relabel it completed.

## Target-Driven Scan Loop

Each lane works backward from the exact action target instead of stopping after an arbitrary first batch:

1. Set `action_target`, `action_cap`, `qualified_read_floor`, `deadline`, and the lane's score threshold. Store `slot_target_remaining = action_target - verified_actions` and preserve it across every continuation.
2. Start with live `New`/`Rising` items in the highest-fit eligible communities. Open the actual post or comment chain; titles and feed impressions do not count.
3. Score each exact candidate. Act immediately when it passes; record `Watch`/`Skip` and continue without drafting weak content.
4. While `slot_target_remaining > 0`, keep scanning while authorized time remains: widen to more eligible communities, then recent `Hot`, deeper comment chains, subreddit search, and adjacent current topics. Refresh live surfaces instead of recycling rejected candidates. Reaching the read floor with too few actions means expand, not finish.
5. Complete a comment or post slot normally only when `slot_target_remaining == 0`. Once the target is verified, do not keep reading merely to fill the read floor. Stop short only when the user deadline/operation cutoff is reached, the user explicitly stops, or a current hard blocker prevents the remaining action. A thin first page, one empty community, candidate scarcity, or a completed read floor is never terminal.

More qualified reading is always allowed while the action target remains. Fewer actions are not an acceptable convenience outcome while authorized time and recoverable discovery surfaces remain. Never lower a score threshold, invent experience, reuse near-duplicate text, violate live rules, or exceed the action cap merely to fill the number. If execution must yield before the target is met, record an interim checkpoint, carry the exact remaining count into the same slot's next Heartbeat, and continue. A final shortfall report is allowed only at a terminal condition and must state verified actions/target, qualified candidates assessed, expansion stages attempted, and the exact terminal reason.

## Natural Incidental Voting

Comments, posts, and follow-up tasks may independently score and cast a natural vote only on content they already had to open for their primary objective:

- comments: the candidate post or parent chain already read for comment discovery
- posts: external survivor/reference posts already read during live rules and angle research
- follow-up: another user's inbound reply already read during Notifications or own-activity review

Incidental voting has no separate target, cap, or read floor. Never extend a slot, widen discovery, or delay the primary lane merely to find votes. The dedicated `BROWSING_WORKER` remains available only for an explicit pure-browse/vote request and is the only mode with a vote target and browse floor.

Every vote uses the independent score in `browse-vote-playbook.md`; comment, post, or reply scores never become vote scores. Before clicking, inspect the intended control once: if either direction is already explicitly selected, record `existing_vote` and do not click; if the state cannot be determined reliably, record `no_vote`. After one successful click, accept it without repeated verification. Never vote on own, team/affiliated, moderator/Automod, or supplied campaign content.

## Launcher Dispatch

For every distributor command, generate a new mission ID and build one independent mission per enabled lane. The mission ID is new even when delivery reuses the existing account+lane task:

```text
mission_id
lane
single_objective
out_of_scope
account
account_direction + direction_source
duration/count/intensity/style/language
pacing_mode=clustered_windows
minimum_completed_cluster_size=2
single_comment_cluster=forbidden
post_default_angle=beginner-common-mistake
target_pool_or_urls
start_local + start_utc
operation_stop_at
first_due=now
heartbeat_owner=self
launcher_callback=none
sibling_visibility=none
incidental_voting=already_read_content_only
action_target + action_cap + qualified_read_floor
```

The missions share only user-provided scope, account identity, and the resolved broad account direction. They do not share runtime state, Heartbeats, risk, completion, cadence, history, or control.

## Later Lane Mission

When the user speaks inside a lane task:

1. Accept only instructions for that lane.
2. Replace conflicting old mission fields with the latest command.
3. Preserve this lane's verified account, tab, history, and own Heartbeat when still valid.
4. Execute the first changed slot now.
5. Update only this task's Heartbeat for remaining work.

If the request belongs to another lane, answer briefly with the correct task title. Do not message, create, inspect, or amend that task.

## Status And Stop

A status request reports only the current lane. Pause/resume/stop changes only the current lane and its own Heartbeat unless the user separately addresses other tasks.
