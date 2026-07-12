# One-Time Launcher Playbook

Load only in `Reddit 启动台`. The launcher installs, checks readiness, allocates requested lane tasks once, and then becomes idle. It is not a coordinator.

## Single Objective

Create one fresh independent lane task for every requested lane and deliver each complete mission successfully.

Out of scope:

- Reddit browsing or mutation
- worker execution acceptance or quality review
- recurring Heartbeat creation or repair
- worker callbacks, status pulls, risk consolidation, or completion aggregation
- reading, steering, or reopening lane tasks after dispatch

## Dispatch

1. Normalize the first request through `default-operations-sop.md`.
2. Broad `开始/运营` enables comments, posts, follow-up, and browsing. Add presence only when the profile baseline is incomplete or explicitly requested. A named lane enables only that lane.
3. Use `thread-supervision-runtime.md` to create one new persistent task per enabled lane. Do not list/search/read/reuse/unarchive/revive historical tasks.
4. Capture only the exact IDs returned by this run's task-creation calls. Rename each new task to its canonical lane title and keep it unpinned.
5. Send one complete handoff containing lane, objective, exclusions, account, duration/count, intensity, style, language, target pool, stop time, first due=`now`, required references, and `heartbeat_owner=self`.
6. Verify only that the exact task accepted the mission message. Do not wait for its Chrome result and do not create a supervisor.
7. Return a compact mapping of lane titles, then enter `L3_IDLE`.

The launcher never creates timers for workers. Each worker creates and owns its self-targeted Heartbeat after executing its immediate first slot.

If one fresh lane task cannot be created or accept delivery, report only that lane as unavailable. Dispatch every other requested lane normally. Do not fall back to an old task, merge lanes, or execute the missing lane in the launcher.

## Handoff Card

```text
role=WORKER
lane=<comments|posts|follow-up|browsing|presence>
single_objective=<one lane outcome>
out_of_scope=<all other lane outcomes>
first_due=now
heartbeat_owner=self
launcher_callback=none
sibling_visibility=none
```

The launcher task stays idle after delivery. Future user instructions belong in the relevant lane task.
