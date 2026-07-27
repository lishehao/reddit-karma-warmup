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
4. If work remains, create and read back one recurring task Heartbeat. The
   Heartbeat belongs to this task, never a unit.

## Wake and units

For every due enabled unit, persist one `RUN`, `WATCH`, `SKIP`, or `DEFER`
decision. Select at most one `RUN`; it gets one Chrome packet and at most one
public action. The unit may complete, skip, block, or yield. A yielded unit
resumes before a later unit.

The task creates one stable 15-minute recurring Heartbeat through the mission
window; it is not reconfigured for ordinary unit changes. Unit rechecks align
to its 15-minute grid: browsing 30 minutes, comments 45, posts 180, follow-up
90 (15 for an active known chain), and presence 24 hours. They are recheck
timings, never action quotas. A wake with no due unit records `NOOP` and does
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
