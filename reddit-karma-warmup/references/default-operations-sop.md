# Operation Request Router

Use in `Reddit 分发台` to split a direct dispatch request, and inside a lane task to normalize only a later request for that lane. Load `operation-defaults.json` first; it is the only numeric default source.

## Resolve The Mission

1. Apply the latest explicit user lane, duration, count, intensity, style, language, target pool, vote target, or cap. A vote request always selects/adds the browsing lane; it never expands a text lane. Do not ask another confirmation.
2. Fill missing duration, intensity, and style from the top-level fields in `operation-defaults.json`, and account direction from `account-direction.md`.
3. Broad `开始/运营` enables comments, posts, and follow-up. K0 receives a post research/preflight mission with action target/cap `0/0`. Browsing is explicit-only; presence is explicit or first-profile-baseline only.
4. Resolve every range/default into one exact mission value before delivery: action target/cap, qualified-read target, pacing, cadence, and deadline. Resolve vote target mode, optional vote target, and hard vote cap only for browsing; every other lane receives `vote_policy=DISABLED_BY_LANE` and `vote_cap=0`.
5. When total count and hourly rate conflict, total count plus duration controls. Report the mismatch once without blocking.

A bare `继续` starts default dispatch only from `BOOTSTRAP_AWAITING_OPERATION`. After the distributor returns idle, it does not silently repeat the prior mission without a new pending instruction.

## Completion Semantics

`action_target` and `qualified_read_target` are independent hard objectives for numeric comment, post-research, and browsing rounds. Follow-up's hard read objective is a complete sweep of Notifications, supplied/known permalinks, recent own posts, and recent own comments. Presence follows its requested checklist.

Normal completion requires every applicable hard objective:

```text
action_remaining == 0
qualified_read_remaining == 0 or required_surface_sweep == complete
explicit_vote_target_remaining == 0 only for a browsing mission with a user-supplied vote target
```

If actions finish first, continue qualified lane-local reading without another text mutation. If reads finish first, continue candidate discovery toward the action target. A read target is not a maximum; additional reading is allowed while another hard objective remains. Stop short only for deadline, explicit user stop, or a current concrete blocker after bounded recovery and candidate expansion.

## Browsing-Lane Voting

Only `Reddit 浏览台` loads `browse-vote-playbook.md`. Its default voting is opportunity-only: resolve `vote_target_mode=opportunity`, omit `vote_target`, and apply the hard intensity cap from `operation-defaults.json`. Count Upvote and Downvote separately. Do not continue or widen scanning solely to cast a default vote.

A user-supplied combined or directional vote count sets `vote_target_mode=hard`. When no separate cap is supplied, the explicit target also becomes the cap. When both are supplied, require target `<=` cap; report and use the explicit cap as the maximum rather than exceeding it. Existing votes and `no_vote` do not fill a hard target.

Every vote uses the independent gate and configured score thresholds in `browse-vote-playbook.md`; comment/post/reply scores never become vote scores. One accepted click is final; do not toggle or repeatedly verify it. Comments, posts, follow-up, and presence never load this playbook and never inspect a vote control.

## Clustered Comments

Every proactive target of `2+` is decomposed into windows of at least two, normally two to four. Examples: `3 -> 3`, `5 -> 2+3`, `8 -> 3+2+3`.

Inside a window, each item gets a new `per_comment_gate_id` and independently runs context, rule, length, local voice, shortening, pacing, Check A/B, mutation, and measured logging. A cluster is only a timing/count envelope; prewriting or sharing a copy decision is forbidden.

One verified comment cannot complete the window unless the whole user mission explicitly requested exactly one total comment. User stop, deadline, or a current hard blocker may leave `cluster_incomplete`; preserve its exact remainder in the checkpoint.

## Target-Driven Scan Loop

1. Restore exact action/read remainders from `lane-state-checkpoint.md`; restore an optional vote remainder only in browsing.
2. Start with live `New`/`Rising` in highest-fit eligible communities; open actual content rather than counting feed impressions.
3. Score each candidate. Act immediately when it passes; record Watch/Skip and continue without drafting weak content.
4. While a hard remainder is positive and time remains, widen through more eligible communities, recent `Hot`, deeper chains, subreddit search, and adjacent current topics. Refresh surfaces rather than recycling rejected candidates.
5. Persist every qualified read, verified lane-owned action, remaining count, and mutation certainty before yielding. Browsing additionally persists vote/no-vote decisions.

Never lower thresholds, invent experience, reuse near-duplicate text, violate live rules, or exceed a cap to fill a target.

## Mission Card

Every dispatched lane mission contains:

```text
mission_id + mission_revision
worker_task_id=<exact destination task ID>
lane + single_objective + out_of_scope
account + account_direction + direction_source + mission_identity_focus
duration + intensity + style + language + operation_stop_at
action_target + action_cap + action_remaining
qualified_read_target + qualified_read_remaining
vote_policy=<DISABLED_BY_LANE for comments/posts/follow-up/presence; BROWSING_ONLY for browsing>
optional browsing-only vote_target_mode + vote_target + vote_cap
interaction_pacing=from operation-defaults.json
first_due=now + mutation_phase_index + initial_mutation_not_before
heartbeat_owner=self + heartbeat_target=worker_task_id
checkpoint_path + checkpoint_schema_version=1
dedicated_reddit_tab=required + launcher_callback=none + sibling_visibility=none
exact_role_pack + filtered target shortlist + required live gates
requested_model + requested_reasoning_effort + actual_model_pair
```

Comments also receive clustered-window fields. Posts receive `main_post_unlock`, `post_action_mode`, and exact posting-gate rows. Non-browsing missions also receive `vote_cap=0`, zero current vote counters, and `browse_vote_playbook=NOT_LOADED`. A traffic probe is not an action target until live traffic, action route, and account gates pass.

## Later Lane Mission

A later command inside a lane replaces conflicting old mission fields, increments `mission_revision`, starts the changed slot now, preserves valid tab/history, and updates only that task's checkpoint and Heartbeat. An off-lane request is not forwarded; name the canonical task briefly.
