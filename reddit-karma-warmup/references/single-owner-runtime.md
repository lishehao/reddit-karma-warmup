# Single-owner runtime

## Ownership

One current, unarchived `Reddit 运营台` owns the entire mission. It has one
mission envelope, one append-only queue, one recurring Heartbeat, one Chrome
binding, and one primary Reddit tab. The five units are internal decisions; do
not create a launcher, executor, worker, lane, callback registry, browser
proxy, or second Chrome task.

## Start

1. After the three-answer intake and before creating a new envelope, inspect
   every pre-existing local Reddit runtime record. This is local-only: do not
   open Chrome, Reddit, or an old task just to settle a stale file. Use
   `scripts/runtime_fence.py` with four independently obtained facts:

   - exact owner task state from `read_thread` (`running`, `idle`, `notLoaded`,
     `archived`, `absent`, or `unknown`);
   - exact Heartbeat state (`future`, `absent`, `expired`, or `unknown`);
   - current local lock state (`held`, `unheld`, or `unknown`);
   - recorded operation cutoff and queue state.

   `notLoaded`, an empty task read, `ACTIVE` in JSON, and
   `chrome_release=PENDING` are each insufficient by themselves. Classify:

   | Result | Required evidence | Startup behavior |
   | --- | --- | --- |
   | `ACTIVE_OWNER` | running task, held lock, or future Heartbeat | block new mission |
   | `STALE_RUNTIME` | cutoff passed, task not running, Heartbeat absent/expired, and lock unheld | run `runtime_fence.py --reconcile`; keep old evidence, do not touch task/Chrome/automation, then continue |
   | `UNCERTAIN` | any needed fact unknown or conflicting | block and report exact missing fact |
   | `NO_FENCE` | already retired/released record with no live owner evidence | continue |

   Reconciliation writes an immutable local marker rather than rewriting an
   old queue. It must never request user permission, archive an old task,
   delete an old automation, or claim a historical Chrome tab. A new mission
   will create/claim its own dedicated tab only after its own canary.
2. Verify the current task is present and unarchived. After binding its mission
   envelope, rename that exact task from `Reddit 启动台` to `Reddit 运营台`, read
   the exact ID/title back, and record `presentation-promote` with the readback
   proof. Do not pass the canary while the task still presents as a launcher.
3. Compile the input with `scripts/compile_single_owner_mission.py`, then
   bootstrap `scripts/single_owner_queue.py` using the exact current task ID
   and the envelope's unique `mission_id` as its queue scope. Never reuse a
   prior mission scope.
4. Perform a neutral HTTPS canary before Reddit work. Create/claim a dedicated
   primary tab only after it passes.
5. If work remains, create and read back one recurring task Heartbeat with an
   `UNTIL` at `operation_stop_at + cleanup_grace`. The Heartbeat belongs to this
   task, never a unit. It is not an unbounded recurring timer. Persist the
   `automation_id`, exact owner task ID, RRULE, `UNTIL`, next occurrence,
   readback time, and readback proof in the queue before declaring it healthy.

## Objective graph

Store two facts for every unit: the bounded packet outcome and the durable
objective state. `COMPLETED` is only a packet outcome. It does not mean a
comment/post/reply/profile change exists, and it must not close an action goal.

```text
browsing candidate pack ──> atomic `handoff` ──> comments/posts ACTION_ELIGIBLE
verified own post/comment permalink ──> follow-up ACTION_ELIGIBLE
explicit requested profile change ──> presence ACTION_ELIGIBLE
```

Use `PENDING`, `CANDIDATES_READY`, `ACTION_ELIGIBLE`, `ACTION_VERIFIED`,
`LIVE_GATE_UNVERIFIED`, `MATERIAL_REQUIRED`, `RULE_BLOCKED`, `SUBMISSION_UNCERTAIN`,
`NOT_APPLICABLE`, or `RESEARCH_ONLY`. Record a compact evidence/source
reference when a unit becomes `CANDIDATES_READY` or `ACTION_ELIGIBLE`.
`ACTION_VERIFIED` needs both verification evidence and the resulting own
permalink/source reference before it can arm follow-up.

- `MATERIAL_REQUIRED`: one bounded audit established that the user has not
  supplied the truthful artifact, relationship, observation, or claim needed
  for the requested action. Stop re-researching until a revision supplies it.
- `RULE_BLOCKED`: record the current visible rule/approval/form blocker and
  park the unit. Do not keep probing hidden gates.
- `LIVE_GATE_UNVERIFIED`: a Chrome/content-channel/DOM/navigation failure
  prevented the live account, rule, duplicate, composer, or page-state gate
  from being completed. It is not a rule decision and remains recoverable:
  finish the packet as `YIELDED`, preserve the candidate/action-key state, and
  resume the same unit at the next verified Heartbeat.
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
must call `single_owner_queue.py handoff` before it finishes. The handoff is
the only cross-unit path permitted while a packet is active; it records the
source reference, arms the target, and schedules that target for the task's
next verified Heartbeat occurrence. Do not close browsing and then leave its
candidate to a generic 30/45/180-minute recheck. If a post is parked as
`MATERIAL_REQUIRED` or `RULE_BLOCKED`, do not keep repeating the same route
sweep. Record the unmet goal honestly; a planning target is not permission to
force an action.

## Wake and units

For every due enabled unit, persist one `RUN`, `WATCH`, `SKIP`, or `DEFER`
decision. Select at most one `RUN`; it gets one Chrome packet and at most one
public action. The unit may complete, skip, block, or yield. On finish, persist
an objective state as well as the packet outcome whenever the unit has outward
authority. A yielded unit resumes before a later unit.

The task creates one stable 15-minute recurring Heartbeat through the mission
window plus one cleanup grace; it is not reconfigured for ordinary unit changes.
Read back its exact ID, target task, recurrence, `UNTIL`, and a future next
occurrence before claiming it healthy. At every delivered scheduler turn, run
`heartbeat-observe` before `wake-open`; it records the signed delivery gap and
advances the expected occurrence. More than one elapsed interval is
`SCHEDULER_GAP_SUSPECTED`: it proves only that the expected schedule was not
observed in this task, not that a platform execution was lost. Do not catch up
missed actions. Refresh the receipt after every closed wake before the next
work wake. An unfinished mission with no verifiable future occurrence is
`MISSION_SCHEDULER_UNVERIFIED`, not healthy. A later manual/task turn that
finds a suspected gap must recover or finalize; a Skill cannot observe a timer
delivery that never reaches any task turn.
Only a first packet inside the opening five-minute tolerance may declare
`wake-source=INITIAL`; every later `wake-open` requires an observation from the
same Heartbeat turn. This prevents a manually resumed task from silently
calling overdue work a healthy scheduler delivery.
Normal unit rechecks align to its 15-minute grid: browsing 30 minutes, comments
45, posts 180, follow-up 90 (15 for an active known chain), and presence 24
hours. They are recheck timings, never action quotas. An `ACTION_ELIGIBLE`
handoff is different: it is a continuation and must be due on the next
verified task Heartbeat, not the next absolute grid boundary. For an active
action-budget mission, runnable browsing likewise remains due on the next
verified Heartbeat until its coverage frontier is exhausted or an action
handoff supersedes it. Coverage and action threshold determine what a bounded
packet studies and which eligible candidate it prefers. Rechecks apply only to
objective states that remain runnable. For an action-oriented goal, an
authorized pending/candidate-ready `comments` or `posts` unit may not be
deferred beyond the cutoff: the queue records an
`ACTION_WINDOW_CLAMPED_TO_NEXT_GRID` adjustment instead. A packet must never
schedule a unit after the mission cutoff. A wake with no due unit atomically
records `NOOP` and does not claim, open, or read Chrome. It is valid only for
an early/duplicate delivery, recovery, or a genuinely exhausted/parked
frontier; it is not normal spacing after an eligible handoff. An actual trigger
within ±5 minutes is ordinary. A trigger beyond that window records
`EARLY_WAKE` or `LATE_WAKE` with its signed delta; an early wake does no work,
and a late wake recomputes from actual time. Neither catches up missed actions
or creates a second timer.

Every open wake and running packet has one 15-minute lease. If the owning task
returns after that lease, or after the operation deadline, it must run one
bounded recovery: settle the stale boundary, preserve lower-bound evidence,
freeze a supplied uncertain `action_key`, and yield the same unit for a later
wake. It must not replay a mutation, create another Heartbeat, or create a new
mission. A no-work wake never creates an open wake. If an action-window defer
cannot fit another grid before cutoff, record `ACTION_WINDOW_EXPIRED`, clear
that unit's schedule, and close the wake normally; do not leave it open.

A prior Chrome timeout is not a durable reason to skip future due work. When a
due unit's last failure was `CHROME_CONTENT_CHANNEL_TIMEOUT`, `about:blank`,
or a rule/composer read timeout, the next wake must run one bounded recovery or
read probe and then either continue or yield again. Do not record repeated
`SKIP` decisions whose only reason is the previous navigation or DOM timeout.

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

At deadline stop new Reddit work. Enter `FINALIZE_ONLY`; it may not browse,
publish, vote, or make another Reddit mutation. It may only recover a stale
boundary, release agent-owned tabs, delete the exact Heartbeat, and retire the
queue. The cleanup grace gives the recurring timer time to reach this state; it
does not extend permission for Reddit work. Retirement requires a finalize
state, no open wake/packet, tab-release proof, and Heartbeat-deletion proof.
If all enabled objectives become terminal earlier, the same finalization order
is allowed early. Keep the task itself available for the next mission.
