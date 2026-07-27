# Single-owner Reddit Runtime

This is the production runtime for `execution_topology=single_owner_v1`.
One present, unarchived user-visible `Reddit 运营台` owns the mission and all
Chrome control. It is not a dispatcher, a parent task, or a coordinator for
sibling executors.

## Ownership

```text
one user prompt
  -> one pinned Reddit 运营台
       -> one immutable mission envelope / revision chain
       -> one durable queue: browsing -> comments -> posts -> follow-up -> presence
       -> one Chrome binding + one primary Reddit tab
       -> optional <=2 public read tabs after a neutral canary
```

No other task may own a Reddit tab or Chrome mutation for this mission. The
local queue script is a durable state record, not a daemon, scheduler, lock
server, browser client, or permission source.

## Bootstrap

1. Rename/pin the current healthy operating task `Reddit 运营台`.
2. Resolve the current Chrome runtime path and perform only the required
   read-only preflight. Do not create a test Heartbeat.
3. Compile `reddit_single_owner_mission/v1` with
   `scripts/compile_single_owner_mission.py`; atomically persist it outside the
   managed Skill directory.
4. Bootstrap `reddit_single_owner_queue/v1` with
   `scripts/single_owner_queue.py bootstrap`. The initial queue contains one
   generation for every selected active unit in canonical order.
5. Run a neutral, agent-owned `https://example.com/` canary before Reddit work:
   new tab, navigation, then minimal page proof are separate boundaries.
6. Persist canary proof, start the first unit, and create/read back one
   mission-level recurring Heartbeat only when unfinished work remains.

The task may request Luna/High only when the host supports it. A request or
metadata readback does not create a successor, prove liveness, or modify the
mission owner.

## Unit execution

The queue starts one unit at a time. `browsing` can use a bounded two-tab,
public, read-only batch after the canary. All serial boundaries stay serial:

- tab creation/claim, focus, scrolling, input, click, submit, result readback;
- mutation preparation and verification;
- recovery, tab close, finalization, and Chrome release.

Each unit loads only its route-specific references. The five units are policy
boundaries, not five threads. Unit order can be amended only by a hashed
revision; no unit can self-enable another unit's action authority.

## Mission envelope and authority

The compiler accepts only the fixed five unit IDs. Its default authority is:

| Unit | Default | Explicit action authority |
| --- | --- | --- |
| browsing | `READ_ONLY` | `VOTE_AUTHORIZED` |
| comments | `RESEARCH_ONLY` | `COMMENT_AUTHORIZED` |
| posts | `RESEARCH_ONLY` | `POST_AUTHORIZED` |
| follow-up | `RESEARCH_ONLY` | `FOLLOWUP_AUTHORIZED` |
| presence | `RESEARCH_ONLY` | `PRESENCE_AUTHORIZED` |

Any non-default authority requires a direct user authorization receipt in the
compiled input. It is still only a scope gate: current rules, account state,
truthful evidence, anti-spam/pacing constraints, and exact submit state can
block the action. `VOTE_AUTHORIZED` is valid only for `browsing` and requires
`vote_policy=BROWSING_ONLY`.

## Safe unit hot-plug protocol

Never edit a current envelope. Compile revision `n+1` with its exact parent
hash and full desired unit plan, then apply it with `single_owner_queue.py
apply-revision`.

| Change | Safe-boundary behavior |
| --- | --- |
| `ADD` | enqueue one fresh unit generation |
| `PAUSE` | move only a queued/yielded unit to append-only history; preserve its cursor and evidence |
| `REMOVE` | same as pause, but mark it removed for this mission revision; never delete history |
| `RESUME` | enqueue a fresh generation; never rewrite a paused/removed/completed generation |
| authority / vote policy | retain the five-unit plan, record exact `from`/`to` values, and require a new direct receipt before any authority increase |

The queue rejects a revision if a unit is `RUNNING`, a read batch is open, a
browser boundary is in flight, the mission is retired, the parent hash/revision
does not match, or the new authority is malformed. A frozen `action_key` is a
settled uncertainty record: it cannot be retried or erased, but it does not
force unrelated read-only units to stop.

## Recovery and retirement

When a recoverable Chrome/read failure persists beyond one bounded same-wake
pass, `YIELD` the active unit with its cursor, remaining budget, exact frozen
keys, and failure class. The next mission Heartbeat resumes that same unit
before any later queued unit. A human repair condition stops browser work but
does not create a replacement Chrome task.

Only after every unit is terminal, paused, or removed; no batch is open; and
agent-owned tabs are proven released, may the task delete its Heartbeat and
retire its queue. Do not archive the user-visible `Reddit 运营台` merely because
one mission ended; keep it ready for a fresh mission.
