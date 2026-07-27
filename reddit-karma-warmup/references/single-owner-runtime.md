# Single-owner runtime

## Ownership

One current, unarchived `Reddit 运营台` owns the entire mission. It has one
mission envelope, one append-only queue, one recurring Heartbeat, one Chrome
binding, and one primary Reddit tab. The five units are internal decisions; do
not create a launcher, executor, worker, lane, callback registry, browser
proxy, or second Chrome task.

## Start

1. Verify the current task is present and unarchived; name/pin it only as a
   presentation step.
2. Compile the input with `scripts/compile_single_owner_mission.py`, then
   bootstrap `scripts/single_owner_queue.py` using the exact current task ID.
3. Perform a neutral HTTPS canary before Reddit work. Create/claim a dedicated
   primary tab only after it passes.
4. If work remains, create and read back one recurring task Heartbeat with an
   `UNTIL` at `operation_stop_at + cleanup_grace`. The Heartbeat belongs to this
   task, never a unit. It is not an unbounded recurring timer.

## Objective graph

Store two facts for every unit: the bounded packet outcome and the durable
objective state. `COMPLETED` is only a packet outcome. It does not mean a
comment/post/reply/profile change exists, and it must not close an action goal.

```text
browsing candidate pack ──> comments/posts ACTION_ELIGIBLE
verified own post/comment permalink ──> follow-up ACTION_ELIGIBLE
explicit requested profile change ──> presence ACTION_ELIGIBLE
```

Use `PENDING`, `CANDIDATES_READY`, `ACTION_ELIGIBLE`, `ACTION_VERIFIED`,
`MATERIAL_REQUIRED`, `RULE_BLOCKED`, `SUBMISSION_UNCERTAIN`,
`NOT_APPLICABLE`, or `RESEARCH_ONLY`. Record a compact evidence/source
reference when a unit becomes `CANDIDATES_READY` or `ACTION_ELIGIBLE`.
`ACTION_VERIFIED` needs both verification evidence and the resulting own
permalink/source reference before it can arm follow-up.

- `MATERIAL_REQUIRED`: one bounded audit established that the user has not
  supplied the truthful artifact, relationship, observation, or claim needed
  for the requested action. Stop re-researching until a revision supplies it.
- `RULE_BLOCKED`: record the current visible rule/approval/form blocker and
  park the unit. Do not keep probing hidden gates.
- `SUBMISSION_UNCERTAIN`: freeze the exact action key permanently; never use a
  recovery wake to resend it.
- `NOT_APPLICABLE`: no verified own permalink for follow-up, or no concrete
  presence change. It is not a recurring inspection task.

Only a mission revision or a recorded upstream evidence handoff may re-arm a
parked action unit. Do not use a generic cadence to revive it.

## Goal profile and priority

The mission envelope stores one business goal plus community scope, coverage
budget, soft action threshold, action budget, material references, and planning
targets. The user may say “high/low frequency”, but that shorthand never
changes the Heartbeat: it compiles to coverage/threshold/budget only.

Hard action gates are invariant: explicit authority, live rule/format fit,
truthful material or claim, current account/composer state, duplicate/recent
history, and one verified submission. The threshold only ranks candidates that
already pass those gates.

When an enabled comment/post/follow-up/presence unit becomes `ACTION_ELIGIBLE`
for the business goal, schedule it before more exploratory browsing. A browsing
packet that establishes a dated route plus the truthful contribution boundary
must explicitly arm the relevant comment/post objective before it finishes; do
not use a pause/resume revision merely to make that action unit due. If a
post is parked as `MATERIAL_REQUIRED` or `RULE_BLOCKED`, do not keep repeating
the same route sweep. Record the unmet goal honestly; a planning target is not
permission to force an action.

## Wake and units

For every due enabled unit, persist one `RUN`, `WATCH`, `SKIP`, or `DEFER`
decision. Select at most one `RUN`; it gets one Chrome packet and at most one
public action. The unit may complete, skip, block, or yield. On finish, persist
an objective state as well as the packet outcome whenever the unit has outward
authority. A yielded unit resumes before a later unit.

The task creates one stable 15-minute recurring Heartbeat through the mission
window plus one cleanup grace; it is not reconfigured for ordinary unit changes.
Read back the recurrence and its `UNTIL` before claiming the Heartbeat healthy.
Unit rechecks align
to its 15-minute grid: browsing 30 minutes, comments 45, posts 180, follow-up
90 (15 for an active known chain), and presence 24 hours. They are recheck
timings, never action quotas. Coverage and action threshold do not alter this
timer; they change what a bounded packet studies and which eligible candidate
it prefers. Rechecks apply only to objective states that remain runnable. For
an action-oriented goal, an authorized pending/candidate-ready `comments` or
`posts` unit may not be deferred beyond the cutoff: the queue records an
`ACTION_WINDOW_CLAMPED_TO_NEXT_GRID` adjustment instead. A packet must never
schedule a unit after the mission cutoff. A wake
with no due unit records `NOOP` and does
not claim, open, or read Chrome. An actual trigger within ±5 minutes is
ordinary. A later trigger records `LATE_WAKE`, recomputes from actual time,
and never catches up missed actions or creates a second timer.

## Permission and uncertainty

The compiler accepts only `browsing`, `comments`, `posts`, `follow-up`, and
`presence`. Explicit authority is required for every non-read action and does
not override current rules, account state, truthful evidence, composer state,
or pacing. Persist `MUTATION_INTENT` / `action_key` before an outward action.
Unknown submit state freezes that exact key forever.

Apply a revision only at a safe boundary: no active unit, open wake, read batch,
or Chrome boundary. It can add, pause, remove, resume, or change scoped
authority without erasing history. A new direct authorization is always needed
for an authority increase.

## End

At deadline stop new Reddit work. Settle boundaries, release only agent-owned
tabs, delete the exact Heartbeat, and retire the queue. Keep the task itself
available for the next mission.
