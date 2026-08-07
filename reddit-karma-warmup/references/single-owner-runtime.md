# Single-owner runtime

Runtime receipts use short opaque evidence tokens. Do not generate or check a
SHA-256 value on every wake, Chrome packet, or cleanup step; the queue accepts
legacy `*_sha256` field names as plain receipt references. Envelope re-hashing
is diagnostic-only with `REDDIT_STRICT_INTEGRITY=1`; normal operation checks
task/scope consistency without recomputing the digest.

## Ownership

The current Reddit operating task owns the mission in this task. It has one
mission envelope, one queue, an advisory Heartbeat when available, one Chrome
binding, and one primary Reddit tab. The five units are internal decisions. Do
not create a second owner inside this task. Do not inspect other tasks or
environments to decide whether this task may start.

## Start

1. After the four-answer intake, inspect only this task's own queue and
   mission, if present. If no current mission exists, continue and create one.
   Do not scan other Heartbeats, environments, locks, or handoffs. Queue
   inconsistencies are recorded locally; they are not a reason to search for a
   different task.
2. Resolve the exact current task ID from the task context, never from a
   delegated wrapper's `<source_thread_id>`. Immediately rename it to
   `Reddit 运营台`, pin it, and read back the exact title/pin when supported.
   Presentation failure is non-blocking; retry once at the next safe wake.
3. Compile the input with `scripts/compile_single_owner_mission.py`, then
   bootstrap `scripts/single_owner_queue.py` using that exact current task ID
   for `--owner-task-id`. The mission envelope, queue state, Heartbeat target,
   and cleanup command must repeat the same ID; never copy the wrapper's
   `source_thread_id` into any of them.
   and the envelope's unique `mission_id` as its queue scope. Never reuse a
   prior mission scope.
4. Perform one direct same-Chrome Reddit/session probe and create/claim the
   primary tab. Do not open a second neutral canary solely for validation.
5. Start the formal INITIAL packet immediately. In parallel, make one bounded
   recurring Heartbeat attempt. Its ID/readback is useful telemetry, not a
   startup gate; if unavailable, continue the current task and retry on the
   next opportunity. `MISSION_SCHEDULER_UNVERIFIED_CONTINUING` is advisory.

## Objective graph

Store two facts for every unit: the bounded packet outcome and the durable
objective state. `COMPLETED` is only a packet outcome. It does not mean a
comment/post/reply/profile change exists, and it must not close an action goal.

```text
browsing candidate pack ──> optional atomic `handoff` ──> comments/posts ACTION_ELIGIBLE
exact candidate/community rejection ──> `candidate-reject` ──> browsing PENDING
account-wide own-content sweep ──> follow-up ACTION_ELIGIBLE
explicit requested profile change ──> presence ACTION_ELIGIBLE
```

Use `PENDING`, `CANDIDATES_READY`, `ACTION_ELIGIBLE`, `ACTION_VERIFIED`,
`LIVE_GATE_UNVERIFIED`, `MATERIAL_REQUIRED`, `RULE_BLOCKED`, `SUBMISSION_UNCERTAIN`,
`NOT_APPLICABLE`, or `RESEARCH_ONLY`. Record a compact evidence/source
reference when a unit becomes `CANDIDATES_READY` or `ACTION_ELIGIBLE`.
`ACTION_VERIFIED` needs both verification evidence and the resulting own
permalink/source reference when it is used to arm a specific follow-up. In
`全面推进`, the account-wide own-content sweep does not require an upstream
handoff. In an `active` mission, it also re-arms the same action lane on the
next wake; a verified action is success evidence, not a reason to stop the lane.

- `MATERIAL_REQUIRED`: a bounded mission-wide audit established that every
  allowed truthful post format needs absent material. Supply
  `--block-scope MISSION` plus evidence; one failed format or missing project
  link is insufficient while a native discussion route remains possible.
- `RULE_BLOCKED`: reserve this terminal state for a mission-wide visible
  rule/approval/form blocker. Supply `--block-scope MISSION` plus evidence.
  One rejected candidate or incompatible community uses `candidate-reject`.
- `LIVE_GATE_UNVERIFIED`: a Chrome/content-channel/DOM/navigation failure
  prevented the live session, rule, duplicate, composer, or page-state gate
  from being completed. It is not a rule decision and remains recoverable:
  finish the packet as `YIELDED`, preserve the candidate/action-key state, and
  resume the same unit at the next task wake when available.
- `SUBMISSION_UNCERTAIN`: freeze the exact action key permanently; never use a
  recovery wake to resend it. A completed submit with delayed/no UI feedback may
  use one same-target read-only refresh for verification; it never creates a new
  action. If the refreshed target still lacks proof, keep the key uncertain.
- `NOT_APPLICABLE`: follow-up is not authorized outside `全面推进`, or no
  concrete presence change. In `全面推进`, an empty account sweep is recorded
  as `FOLLOW_UP_SWEEP_EMPTY`, not as a reason to disable the unit.

Only a mission revision or a recorded upstream evidence handoff may re-arm a
parked action unit. Do not use a generic cadence to revive it.

## Action-first rounds

When any outward unit is authorized, every formal round, including `INITIAL`,
must attempt an authorized public action before it finishes. Comments are the
default action-first unit when enabled; a comments packet may search and choose
its own target instead of waiting for a browsing handoff. Read up to 60 new
target posts in that packet and, for an `active` mission, continue to a second
distinct target after the first verified action until the packet or hourly cap.
This is a throughput target with a hard ceiling, not permission to post filler.

The only honest no-action outcomes are: no authority, mission cutoff, Chrome or
content-channel failure, a visible blocker on every tested target, no truthful
contribution after the expanded search, or an uncertain submission. Record the
reason and continue the same unit at the next wake; do not turn one rejected
target into a mission-wide block. Browsing-only missions remain research-only.

For `discover` and `seeded_expandable` missions, a handoff-supplied
comments/posts target that cannot pass must call `candidate-reject` before the
packet finishes. A self-selecting action packet keeps a compact local rejected
set and continues searching; it does not park the lane or schedule a separate
browsing wake for every failed target.

## Goal profile and priority

The mission envelope stores one business goal plus community scope, coverage
budget, soft action threshold, rhythm, action budget, material references, and
planning targets. The fourth startup answer (`低 / 标准 / 高`) compiles to
coverage/threshold/budget only; it never changes the Heartbeat. Hourly action
counters reset by UTC hour bucket rather than persisting as a mission-wide
lifetime quota.

Post/follow-up/presence gates require explicit authority, live rule/format fit,
truthful material or claim, current session/composer state, duplicate/recent
history, and one verified submission. Comments use the lighter target/context,
one visible rule or submit signal, composer, truthful text, and one verified
submission path. The threshold only ranks candidates after their action-type
gate; it is never a reason to stop searching for the first workable comment.

When an enabled comment/post/follow-up/presence unit is authorized, schedule its
action-first packet before exploratory browsing. A browsing packet may call
`single_owner_queue.py handoff` when it has a useful dated route, but the target
unit may also self-select in the same packet. Do not finish an
action-authorized round with only a candidate pack. If a post is parked as
`MATERIAL_REQUIRED` or `RULE_BLOCKED`, keep comments or another authorized
action moving; record the unmet post goal honestly rather than forcing a post.
In `全面推进`, follow-up may start from the account-wide own-content sweep
without an upstream permalink handoff; direction and community-discovery
filters do not narrow that sweep.

## Wake and units

For every due enabled unit, persist one `RUN`, `WATCH`, `SKIP`, or `DEFER`
decision. A normal wake selects one action unit and gets one Chrome packet.
When the wake is delayed by more than five minutes, the queue exposes up to
three packet slots; select useful currently due units up to that cap. They are
opened and completed **serially** on the same Chrome owner, never concurrently.
The queue starts the next selected unit automatically after a completed packet,
and returns `PACKET_COMPLETED_CONTINUE` so the task keeps working. Comments/posts may submit up to two distinct actions; follow-up may batch up to
three verified own permalinks, subject to the hourly ceiling. The unit may
complete, skip, block, or yield. On finish, persist
an objective state as well as the packet outcome whenever the unit has outward
authority. A yielded unit resumes before a later unit. For an
action-authorized mission, `RUN` must be an action-first packet unless one of
the explicit no-action outcomes above is recorded.

Use one deterministic selection ladder: `RECOVERY_FIRST`, then `follow-up`,
`comments`, `posts`, `presence`, and `browsing`, restricted to units enabled and
due for this scope. Break ties by due action, unseen community, and older due
work. After a packet completes, open the next due unit while a serial slot
remains; do not stop after a candidate pack. `NOOP` is valid only after this
ladder finds no runnable unit or every remaining unit is parked.

The task attempts one stable 15-minute recurring Heartbeat through the mission
window plus cleanup grace. Readback is telemetry. At each delivered turn run
`heartbeat-observe` when possible; it records the signed delivery gap and
advances the next occurrence. A missing or conflicting receipt is
`MISSION_SCHEDULER_UNVERIFIED_CONTINUING`, not a reason to block INITIAL or a
current-task wake. A normal closed wake keeps any verified timer; there is no
second readback gate, and a missing observation never blocks a valid wake.
More than one elapsed interval records `SCHEDULER_GAP_SUSPECTED`; do not replay
missed actions, but expand the current wake to its bounded serial packet slots.
A delay of five to twenty minutes yields two slots; longer delays may yield
three, never more. A timer with a valid future occurrence remains healthy.
Keep the automation prompt to identity and immutable boundary facts: mission
ID, owner task ID, queue/envelope paths, cutoff, authority, and the queue's
`runtime_protocol_version`. Do not copy cadence, NOOP, catch-up, or
unit-selection policy into the prompt. Each wake reloads the installed Skill
and queue. A running mission stays pinned to its recorded protocol version.
The first packet may use `wake-source=INITIAL` even when startup was delayed;
the normal expected-time window records the signed delay. Later wakes use their
expected time window and record whether scheduler telemetry was present. They
do not require a same-turn observation before running current due work.
Normal unit rechecks align to the task Heartbeat phase when available—not absolute UTC
quarter-hours: browsing 30 minutes, comments 15, posts 120, follow-up 60, and
presence 24 hours. They are recheck timings, never action quotas. An
`ACTION_VERIFIED` comment/post/follow-up in an active action budget re-arms on
the next task wake; a follow-up packet may batch up to three verified own
permalinks. Standard/minimal missions use the normal recheck. An `ACTION_ELIGIBLE`
handoff is different: it is a continuation and should be due on the next task
wake when available, not the next absolute grid boundary. For an active
action-budget mission, runnable browsing likewise remains due on the next task
wake until its coverage frontier is exhausted or an action
handoff supersedes it. Coverage and action threshold determine what a bounded
packet studies and which eligible candidate it prefers. Rechecks apply only to
objective states that remain runnable. For an action-oriented goal, an
authorized pending/candidate-ready `comments` or `posts` unit may not be
deferred beyond the cutoff: the queue records an
`ACTION_WINDOW_CLAMPED_TO_NEXT_HEARTBEAT` adjustment instead. A packet must never
schedule a unit after the mission cutoff. A wake with no due unit atomically
records `NOOP` and does not claim, open, or read Chrome. It is valid only for
an early/duplicate delivery, recovery, or a genuinely exhausted/parked
frontier; it is not normal spacing after an eligible handoff. An actual trigger
within ±10 minutes is ordinary. A trigger beyond that window records
`EARLY_WAKE` or `LATE_WAKE` with its signed delta; an early wake does no work.
The queue records `packet_slots`, `packets_started`, and `completed_units` in
the open wake. “No catch-up” means no replay of missed packets or mutations;
it never means skipping currently due work. If one packet yields or a mutation
becomes uncertain, freeze/resume that exact unit, but use any remaining serial
slot for an independent selected unit. A global content-channel failure will
usually make that next probe fail quickly and close the wake; it must not create
an unbounded retry loop.
Neither case creates a second timer.

Every open wake and running packet has one 15-minute lease. If the owning task
returns after that lease, or after the operation deadline, it must run one
bounded recovery: settle the stale boundary, preserve lower-bound evidence,
freeze a supplied uncertain `action_key`, and yield the same unit for a later
wake. It must not replay a mutation, create another Heartbeat, or create a new
mission. A no-work wake never creates an open wake. If an action-window defer
cannot fit another task wake before cutoff, record
`ACTION_WINDOW_EXPIRED`, clear
that unit's schedule, and close the wake normally; do not leave it open.

A prior Chrome timeout is not a durable reason to skip future due work. When a
due unit's last failure was `CHROME_CONTENT_CHANNEL_TIMEOUT`, `about:blank`,
or a rule/composer read timeout, the next wake must claim or create one fresh agent-owned tab
and run one real content probe, then either continue or yield
again. URL-only checks and tab finalization do not settle recovery. `resume_unit`
and `LIVE_GATE_UNVERIFIED` force `RUN`/`RECOVERY_FIRST`; `WATCH`, `SKIP`,
`DEFER`, and fast NOOP are invalid until that probe is attempted. Later wakes
may keep retrying the same unit; there is no permanent recovery parking.

## Permission and uncertainty

The compiler accepts only `browsing`, `comments`, `posts`, `follow-up`, and
`presence`. Explicit authority is required for every non-read action and does
not override current rules, session identity, truthful evidence, composer state,
or pacing. Persist `MUTATION_INTENT` / `action_key` before an outward action.
Unknown submit state freezes that exact key forever.

Apply a revision only at a safe boundary: no active unit, open wake, read batch,
or Chrome boundary. It can add, pause, remove, resume, or change scoped
authority without erasing history. A new direct authorization is always needed
for an authority increase.

## End

At deadline stop new Reddit work. Enter `FINALIZE_ONLY`; it may not browse,
publish, or make another Reddit mutation. It may only recover a stale
boundary, release agent-owned tabs, delete the exact Heartbeat, and retire the
queue. The cleanup grace gives the recurring timer time to reach this state; it
does not extend permission for Reddit work. Retirement requires a finalize
state, no open wake/packet, tab-release proof, and Heartbeat-deletion proof.
If all enabled objectives become terminal earlier, the same finalization order
is allowed early. Keep the task itself available for the next mission.
