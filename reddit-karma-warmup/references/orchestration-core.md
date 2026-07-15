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
action_target + slot_target_remaining + action_cap + qualified_read_floor
vote_target_mode + combined_vote_target + vote_cap + vote_target_remaining + upvote_count + downvote_count
own_tab_id + own_tab_origin + optional group_id + current URL + tab_control_proof
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
| `TAB` | Create/reclaim this task's one persistent dedicated Reddit primary tab; close stale or same-turn auxiliary tabs. | exact tab ownership plus account/URL/page-control proof confirmed |
| `HISTORY` | Restore this lane's recent actions, openings, lengths, targets, and permalinks. | local history ready |
| `DISCOVER` | Inspect current lane surfaces and candidate context. | candidate passes or concrete no-action |
| `CHECK_A` | Check pool, live rules/eligibility, context, and duplicate history. | pass/retarget/recover |
| `DRAFT` | Text lanes choose varied length and write target-specific copy; browsing chooses a vote/no-vote decision. | final candidate ready |
| `CHECK_B` | Recheck account, page, copy/direction, target, and duplicate state. | act/rewrite/retarget/recover |
| `ACT` | Perform at most the selected action and verify immediate result. | proof recorded |
| `RECONCILE` | Subtract only verified text actions from `slot_target_remaining` and accepted votes from `vote_target_remaining`; preserve both unfinished counts and compute the next due time from actual conditions. | either remainder unfinished -> `SCHEDULE`; terminal -> `RETIRE` |
| `SCHEDULE` | For nonterminal work only, run the scheduler's pre-bind, explicit-bind, and post-bind transaction for this task's own Heartbeat. | exact target binding verified and timer state recorded |
| `RETIRE` | For explicit stop, deadline, or verified mission-target completion, delete this task's own Heartbeat and clear its timer state before reporting. | deletion success or timer already absent |
| `REPORT` | Return the three-line local result. | turn ends |

The first user command reaches `ACT` when its mutation phase is open. Otherwise it reaches browser-backed discovery/checking/drafting plus a recorded `phase_wait` checkpoint in the current turn; task creation, planning alone, or deferring all work to a future Heartbeat is not execution.

For proactive comments, the state machine runs once per individual comment, not once per cluster. After one verified `ACT`, write the measured log, return to `DISCOVER`, assign a new `per_comment_gate_id`, and rerun `CHECK_A`, `DRAFT`, and `CHECK_B` for the next item. A prewritten batch or shared cluster-level copy decision is invalid.

## Lane Boundaries

| Lane | Owns | Excludes |
|-|-|-|
| comments | proactive comment discovery/submission plus its hard per-round combined-vote target on eligible candidate posts/parents | main posts, notifications, unrelated-feed vote hunting, profile changes |
| posts | native main post discovery/preflight/submission plus its hard per-round combined-vote target on eligible external research samples | comments, notifications, unrelated-feed vote hunting, profile changes |
| follow-up | Notifications/replies plus its hard per-round combined-vote target on eligible inbound replies | proactive discovery, new posts, unrelated-feed vote hunting |
| browsing | explicit pure-browse missions with qualified reading and independently gated votes | default broad-operation dispatch, publishing text, notifications, profile changes |
| presence | profile/about, Join/subscribe, truthful Flair/tag | outward content, notifications, votes |

An off-lane user request is not forwarded. Tell the user which canonical task handles it and continue only the current lane if applicable.

## Dedicated Chrome Context

1. Discover Chrome control automatically. Every execution task owns one persistent dedicated Reddit primary tab. A task-specific Tab Group is optional visual organization and never substitutes for the tab.
2. On the first healthy mission turn, use a two-call creation transaction. The first completed browser call only creates the primary tab with the supported Chrome API and returns/persists `own_tab_id` in the tool result/local mission state. A second browser call navigates that recorded tab with `tab.goto("https://www.reddit.com/")`, allows the awaited call up to `60 sec`, and records origin, URL, and a successful DOM/screenshot/page-state read. Never combine `tabs.new()` and the first `goto` in one browser call. Do not navigate by page-side script or simulate the Chrome address bar with `CUA`/`Meta+L`.
3. A `goto` timeout or REPL reset is an uncertain navigation acknowledgement, not proof that navigation failed. Reconnect the same Chrome/profile, enumerate current tabs, reclaim the exact recorded `own_tab_id`, and perform a post-timeout page-state check of URL/title plus DOM or screenshot. If the URL moved and the page is readable, treat navigation as recovered success. If it remains blank or unreadable, retry once in the same tab; do not create a second primary tab.
4. On later turns and Heartbeats, enumerate current Chrome tabs, match the recorded `own_tab_id`, and claim the exact returned tab object. Never guess an ID. URL/title metadata from `openTabs()` is discovery only; the tab is usable only after a fresh page-state read succeeds.
5. If the recorded tab is genuinely missing or stale after enumeration, discard only that binding and create one replacement primary tab from the existing healthy browser binding. Never claim an arbitrary user tab, launcher tab, or sibling task tab merely because it already shows Reddit, and never describe another task's occupied tab as this lane's blocker.
6. Before every action, reselect the primary tab and confirm the expected account and URL. The lane may open a temporary lane-owned read-only auxiliary tab only when the primary workflow genuinely needs it; close every auxiliary tab in the same turn and never persist more than one primary tab.
7. Before a nonterminal turn ends, including navigation recovery that must continue later, persist the tab state and make Chrome finalization the last browser action: `chrome.tabs.finalize({keep: [{tab: own_tab, status: "handoff"}]})`. This releases control while leaving the exact primary tab available for the next wake. Never call `finalize({keep: []})` for a nonterminal navigation failure, and do not call Chrome again after finalization.
8. At explicit stop, deadline, or verified mission completion, call `own_tab.close()` for the task-owned primary tab, then run `chrome.tabs.finalize({keep: []})` and clear `own_tab_id`; do not leave an idle lane tab behind.
9. Never navigate, close, regroup, inspect, or wait for another task's tab. Shared Chrome profile/account use is normal and requires no collision check.

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
