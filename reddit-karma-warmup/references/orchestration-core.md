# Autonomous Lane Orchestration

Canonical owner of one lane task's executable slot. It covers local mission state, dedicated Chrome tab, candidate decision, action verification, local scheduling handoff, and local reporting.

## Local State

Maintain only this lane's state:

```text
self_task_id + worker_task_id + lane + title
account + tier/substate
mission_id + latest user request + duration/count/intensity/style/language
operation_stop_at
mutation_phase_index + initial_mutation_not_before + phase_jitter_minutes + missed_phase_policy
action_target + action_remaining + slot_target_remaining + action_cap
qualified_read_target + qualified_read_remaining + qualified_read_count
vote_policy + vote_cap
optional browsing-only vote_target_mode + vote_target + vote_target_remaining + upvote_count + downvote_count
own_tab_id + own_tab_origin + optional group_id + current URL + tab_control_proof
surface_requested + surface_used + surface_reason + canonical_target_key
fallback_from + fallback_reason + route_result
own_history_ledger
own_heartbeat_id + target_binding_proof + next_due_local + next_due_utc
mission_target_remaining + mission_terminal_reason + heartbeat_retirement_proof
checkpoint_path + checkpoint_schema_version + checkpoint_updated_at
last_action/no_action/recovery proof
recovery_status + error_fingerprint + consecutive_failure_wakes + backoff_index + quiet_recovery
next_recovery_at_local + next_recovery_at_utc + account_recheck_required
quarantined_mutation_url + quarantined_outbound_text_hash
```

Do not store launcher state, sibling IDs, sibling timers, shared slot ledgers, or cross-lane status.

## Slot State Machine

| State | Required action | Exit |
|-|-|-|
| `SCOPE` | Apply the latest instruction for this lane; resolve `self_task_id` from exact current-task context; require it equals the delivered `worker_task_id`; load `operation-defaults.json` and `lane-action-ownership.md`; resolve exact action target/cap, hard read target, lane-owned action policy, checkpoint path, and model state. Only browsing resolves a vote target/cap; every other lane requires `DISABLED_BY_LANE` and zero vote cap. | local mission and worker identity clear |
| `RESTORE` | Load `lane-state-checkpoint.md` and this task's exact checkpoint. Reconcile the latest command with verified prior actions, reads, submission certainty, tab, and timer state. | atomic checkpoint is valid or safely reconstructed read-only |
| `PROBE` | Discover/reconnect Chrome, confirm account, local time and UTC. On failure enter the bounded, checkpointed cross-wake recovery state; do not loop or terminate the mission. | environment recorded or lane recovery persisted |
| `TAB` | Create/reclaim this task's one persistent dedicated Reddit primary tab; close stale or same-turn auxiliary tabs. | exact tab ownership plus account/URL/page-control proof confirmed |
| `HISTORY` | Restore this lane's recent actions, openings, lengths, targets, and permalinks. | local history ready |
| `DISCOVER` | Inspect current lane surfaces and candidate context. Count one qualified read only after the exact surface is readable, the configured dwell floor passes, and enough context is understood to score it. | candidate passes or concrete no-action |
| `CHECK_A` | Check pool, live rules/eligibility, context, and duplicate history. | pass/retarget/recover |
| `DRAFT` | Text lanes choose varied length and write target-specific copy; browsing chooses a vote/no-vote decision. | final candidate ready |
| `CHECK_B` | Recheck account, page, copy/direction, target, and duplicate state. | act/rewrite/retarget/recover |
| `ACT` | Perform at most the selected action and verify immediate result. | proof recorded |
| `RECONCILE` | Subtract only verified text actions from action remainders, qualified reads from the read remainder, and accepted votes from a present explicit vote remainder. Persist the checkpoint atomically, preserve every unfinished count, and compute the next due time from actual conditions. | any required remainder unfinished -> `SCHEDULE`; terminal -> `RETIRE` |
| `SCHEDULE` | For nonterminal work only, run the scheduler's pre-bind, explicit-bind, and post-bind transaction for this task's own Heartbeat. | exact target binding verified and timer state recorded |
| `RETIRE` | For explicit stop, deadline, or verified mission-target completion, delete this task's own Heartbeat and clear its timer state before reporting. | deletion success or timer already absent |
| `REPORT` | Return the three-line local result. | turn ends |

The first user command reaches `ACT` when its mutation phase is open and a candidate passes. Otherwise it reaches browser-backed qualified reading, discovery/checking/drafting, or a recorded `phase_wait` checkpoint in the current turn; task creation, planning alone, or deferring all work to a future Heartbeat is not execution.

For proactive comments, the state machine runs once per individual comment, not once per cluster. After one verified `ACT`, write the measured log, return to `DISCOVER`, assign a new `per_comment_gate_id`, and rerun `CHECK_A`, `DRAFT`, and `CHECK_B` for the next item. A prewritten batch or shared cluster-level copy decision is invalid.

## Lane Boundaries

| Lane | Owns | Excludes |
|-|-|-|
| comments | proactive comment discovery, qualified reading, and comment submission | main posts, notifications, every Upvote/Downvote control, profile changes |
| posts | native main-post research, qualified reading, preflight, submission, and required withdrawal cleanup | comments, notifications, every Upvote/Downvote control, profile changes |
| follow-up | Notifications/known chains/recent activity reading, replies, and required withdrawal cleanup | proactive discovery, new posts, every Upvote/Downvote control |
| browsing | explicit pure-browse missions with qualified reading and independently gated votes | default broad-operation dispatch, publishing text, notifications, profile changes |
| presence | profile/about, Join/subscribe, truthful Flair/tag | outward content, notifications, votes |

An off-lane user request is not forwarded. Tell the user which canonical task handles it and continue only the current lane if applicable.

## Dedicated Chrome Context

1. Discover Chrome control automatically. Every execution task owns one persistent dedicated Reddit primary tab. A task-specific Tab Group is optional visual organization and never substitutes for the tab.
2. On the first healthy mission turn, use a three-call creation transaction. The first completed browser call only creates the primary tab with the supported Chrome API and returns/persists `own_tab_id` in the tool result/local mission state. A second browser call navigates that recorded tab with `tab.goto("https://old.reddit.com/")` as its only browser-boundary command and gives the outer `node_repl` call `120 sec`; a third browser call performs one page-state read and then records origin and URL from that returned evidence. Old Reddit is only the `old_first_modern_fallback` starting surface: load `reddit-surface-routing.md` and use its capability matrix for later routes. Never combine `tabs.new()`, `goto`, and page-state reading. Do not navigate by page-side script or simulate the Chrome address bar with `CUA`/`Meta+L`.
3. A `goto` timeout or REPL reset is an uncertain navigation acknowledgement, not proof that navigation failed. Reconnect the same Chrome/profile, enumerate current tabs, reclaim the exact recorded `own_tab_id`, and perform one post-timeout page-state read. If that single read proves the URL moved and the page is readable, treat navigation as recovered success. If it remains blank or unreadable, retry once in the same tab; do not create a second primary tab.
4. On later turns and Heartbeats, enumerate current Chrome tabs, match the recorded `own_tab_id`, and claim the exact returned tab object. Never guess an ID. URL/title metadata from `openTabs()` is discovery only; the tab is usable only after a fresh page-state read succeeds.
5. If the recorded tab is genuinely missing or stale after enumeration, discard only that binding and create one replacement primary tab from the existing healthy browser binding. Never claim an arbitrary user tab, launcher tab, or sibling task tab merely because it already shows Reddit, and never describe another task's occupied tab as this lane's blocker.
6. Before every action, reselect the primary tab and confirm the expected account, canonical target, surface, and URL. A host change never creates a new candidate or mutation key. The lane may open a temporary lane-owned read-only auxiliary tab only when the primary workflow genuinely needs it; close every auxiliary tab in the same turn and never persist more than one primary tab.
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

One candidate rejection, an empty scan batch/pool page, completion of only one target component, route error, or failed wake is never terminal while another required remainder and authorized time remain.

The terminal stage is the complete objective carried by the current Heartbeat: the latest user-authorized lane mission target across its operation window. Normal completion requires `action_remaining == 0`, `qualified_read_remaining == 0` or the follow-up required-surface sweep complete, and `vote_target_remaining == 0` only inside a browsing mission with a user-supplied vote target. A comment cluster, hourly pacing bucket, one partial follow-up surface, or intermediate slot is not that terminal stage. Once all required components reach zero, unused duration does not justify another wake.

## Action Verification

Load `interaction-pacing.md` and `chrome-atomic-command-runtime.md` before action. Require the measured candidate, readable-to-submit, pre-submit, and inter-click clocks for the exact action; a planned wait is not evidence. Run the remaining pre-submit wait outside the browser cell, then use one native click as the only browser-boundary command with the full outer timeout. Record immediate UI state, permalink/target when available, exact copy or vote direction, time, and any current warning. Delayed survivor/profile visibility is a quality signal rather than a prerequisite for continuing the lane.

Only browsing applies the vote verification contract: inspect the control state once before clicking; selected means `existing_vote`, ambiguous means `no_vote`, and one accepted transition is final. Comments, posts, follow-up, and presence never inspect or focus vote controls. For uncertain text submission, inspect the exact target once before considering any retry; never duplicate an uncertain mutation.

## Reporting

Report only this lane's actions, next verified wake, next plan, and current lane-local risk. Do not mention launcher or sibling implementation details.
