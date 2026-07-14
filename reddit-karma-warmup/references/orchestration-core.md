# Autonomous Lane Orchestration

Canonical owner of one lane task's executable slot. It covers local mission state, dedicated Chrome tab, candidate decision, action verification, local scheduling handoff, and local reporting.

## Local State

Maintain only this lane's state:

```text
self_task_id + worker_task_id + lane + title
account + tier/substate
mission_id + latest user request + duration/count/intensity/style/language
operation_stop_at + remaining_target
mutation_phase_index + initial_mutation_not_before + phase_jitter_minutes + missed_phase_policy
action_target + slot_target_remaining + action_cap + qualified_read_floor + incidental_vote_count
own_tab_id + optional group_id + current URL
own_history_ledger
own_heartbeat_id + target_binding_proof + next_due_local + next_due_utc
mission_target_remaining + mission_terminal_reason + heartbeat_retirement_proof
last_action/no_action/recovery proof
```

Do not store launcher state, sibling IDs, sibling timers, shared slot ledgers, or cross-lane status.

## Slot State Machine

| State | Required action | Exit |
|-|-|-|
| `SCOPE` | Apply the latest instruction for this lane; resolve `self_task_id` from exact current-task context; require it equals the delivered `worker_task_id`; replace conflicting old fields/defaults; resolve exact target/cap/read floor and voting mode. | local mission and worker identity clear |
| `PROBE` | Discover/reconnect Chrome, confirm account, local time and UTC. | environment recorded |
| `TAB` | Create/reclaim only this task's dedicated tab or Tab Group. | tab/account/URL confirmed |
| `HISTORY` | Restore this lane's recent actions, openings, lengths, targets, and permalinks. | local history ready |
| `DISCOVER` | Inspect current lane surfaces and candidate context. | candidate passes or concrete no-action |
| `CHECK_A` | Check pool, live rules/eligibility, context, and duplicate history. | pass/retarget/recover |
| `DRAFT` | Text lanes choose varied length and write target-specific copy; browsing chooses a vote/no-vote decision. | final candidate ready |
| `CHECK_B` | Recheck account, page, copy/direction, target, and duplicate state. | act/rewrite/retarget/recover |
| `ACT` | Perform at most the selected action and verify immediate result. | proof recorded |
| `RECONCILE` | Subtract only verified actions from `slot_target_remaining`; preserve unfinished count and compute the next due time from actual conditions. | unfinished -> `SCHEDULE`; terminal -> `RETIRE` |
| `SCHEDULE` | For nonterminal work only, run the scheduler's pre-bind, explicit-bind, and post-bind transaction for this task's own Heartbeat. | exact target binding verified and timer state recorded |
| `RETIRE` | For explicit stop, deadline, or verified mission-target completion, delete this task's own Heartbeat and clear its timer state before reporting. | deletion success or timer already absent |
| `REPORT` | Return the three-line local result. | turn ends |

The first user command reaches `ACT` when its mutation phase is open. Otherwise it reaches browser-backed discovery/checking/drafting plus a recorded `phase_wait` checkpoint in the current turn; task creation, planning alone, or deferring all work to a future Heartbeat is not execution.

For proactive comments, the state machine runs once per individual comment, not once per cluster. After one verified `ACT`, write the measured log, return to `DISCOVER`, assign a new `per_comment_gate_id`, and rerun `CHECK_A`, `DRAFT`, and `CHECK_B` for the next item. A prewritten batch or shared cluster-level copy decision is invalid.

## Lane Boundaries

| Lane | Owns | Excludes |
|-|-|-|
| comments | proactive comment discovery and submission; independently gated incidental votes on already-read candidates | main posts, notifications, vote hunting, profile changes |
| posts | native main post discovery/preflight/submission; independently gated incidental votes on already-read external research samples | comments, notifications, vote hunting, profile changes |
| follow-up | Notifications and replies to own activity; independently gated incidental votes on already-read inbound replies | proactive discovery, new posts, vote hunting |
| browsing | explicit pure-browse missions with qualified reading and independently gated votes | default broad-operation dispatch, publishing text, notifications, profile changes |
| presence | profile/about, Join/subscribe, truthful Flair/tag | outward content, notifications, votes |

An off-lane user request is not forwarded. Tell the user which canonical task handles it and continue only the current lane if applicable.

## Dedicated Chrome Context

1. Discover Chrome control automatically.
2. Open or reclaim one tab owned by this task; use a task-specific Tab Group when available.
3. Before every action, reselect that tab and confirm account and URL.
4. Never navigate, close, regroup, inspect, or wait for another task's tab.
5. Shared Chrome profile/account use is normal and requires no collision check.

Load `chrome-network-recovery.md` for failures. Retry only this task's action and never infer sibling state.

## Decision Classes

- `act`: current candidate and action pass live gates.
- `skip_candidate`: reject one candidate and continue discovery.
- `retarget`: current subreddit/surface is unsuitable; select another allowed target.
- `recover_lane`: technical/account state blocks the exact action now; preserve mission and own Heartbeat.
- `user_repair`: current visible state requires user action in this task.
- `terminal`: explicit stop, deadline, or verified lane completion.

One candidate rejection, an empty scan batch/pool page, completed read floor, route error, or failed wake is never terminal while the action target and authorized time remain.

The terminal stage is the complete objective carried by the current Heartbeat: the latest user-authorized lane mission target across its operation window. A comment cluster, hourly pacing bucket, individual follow-up sweep, candidate-read floor, or intermediate slot is not that terminal stage unless the user explicitly made it the whole mission. Once `mission_target_remaining == 0`, unused duration does not justify another wake.

## Action Verification

Use one native click for the selected action. Record immediate UI state, permalink/target when available, exact copy or vote direction, time, and any current warning. Delayed survivor/profile visibility is a quality signal rather than a prerequisite for continuing the lane.

For votes, inspect the control state once before clicking. If either direction is already explicitly selected, record `existing_vote` and do not click; if state is ambiguous, record `no_vote`. After one accepted click, do not toggle or repeatedly verify it. For uncertain text submission, inspect the exact target once before considering any retry; never duplicate an uncertain mutation.

## Reporting

Report only this lane's actions, next verified wake, next plan, and current lane-local risk. Do not mention launcher or sibling implementation details.
