# Autonomous Lane Orchestration

Canonical owner of one lane task's executable slot. It covers local mission state, dedicated Chrome tab, candidate decision, action verification, local scheduling handoff, and local reporting.

## Local State

Maintain only this lane's state:

```text
self_task_id + lane + title
account + tier/substate
mission_id + latest user request + duration/count/intensity/style/language
operation_stop_at + remaining_target
own_tab_id + optional group_id + current URL
own_history_ledger
own_heartbeat_id + next_due_local + next_due_utc
last_action/no_action/recovery proof
```

Do not store launcher state, sibling IDs, sibling timers, shared slot ledgers, or cross-lane status.

## Slot State Machine

| State | Required action | Exit |
|-|-|-|
| `SCOPE` | Apply the latest instruction for this lane; replace conflicting old fields/defaults. | local mission clear |
| `PROBE` | Discover/reconnect Chrome, confirm account, local time and UTC. | environment recorded |
| `TAB` | Create/reclaim only this task's dedicated tab or Tab Group. | tab/account/URL confirmed |
| `HISTORY` | Restore this lane's recent actions, openings, lengths, targets, and permalinks. | local history ready |
| `DISCOVER` | Inspect current lane surfaces and candidate context. | candidate passes or concrete no-action |
| `CHECK_A` | Check pool, live rules/eligibility, context, and duplicate history. | pass/retarget/recover |
| `DRAFT` | Text lanes choose varied length and write target-specific copy; browsing chooses a vote/no-vote decision. | final candidate ready |
| `CHECK_B` | Recheck account, page, copy/direction, target, and duplicate state. | act/rewrite/retarget/recover |
| `ACT` | Perform at most the selected action and verify immediate result. | proof recorded |
| `RECONCILE` | Update remaining work and next due time from actual conditions. | next state known |
| `SCHEDULE` | Create/update/retain only this task's own Heartbeat. | timer state recorded |
| `REPORT` | Return the three-line local result. | turn ends |

The first user command reaches `ACT` or a browser-backed no-action/recovery checkpoint in the current turn. Task creation, planning, or a future Heartbeat is not execution.

## Lane Boundaries

| Lane | Owns | Excludes |
|-|-|-|
| comments | proactive comment discovery and submission | main posts, notifications, votes, profile changes |
| posts | native main post discovery/preflight/submission | comments, notifications, votes, profile changes |
| follow-up | Notifications and replies to own activity | proactive discovery, new posts, votes |
| browsing | qualified reading and independently gated votes | publishing text, notifications, profile changes |
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

One candidate rejection, empty pool, route error, or failed wake is never terminal.

## Action Verification

Use one native click for the selected action. Record immediate UI state, permalink/target when available, exact copy or vote direction, time, and any current warning. Delayed survivor/profile visibility is a quality signal rather than a prerequisite for continuing the lane.

For votes, one accepted click is sufficient proof. Do not toggle or repeatedly inspect selected state. For uncertain text submission, inspect the exact target once before considering any retry; never duplicate an uncertain mutation.

## Reporting

Report only this lane's actions, next verified wake, next plan, and current lane-local risk. Do not mention launcher or sibling implementation details.
