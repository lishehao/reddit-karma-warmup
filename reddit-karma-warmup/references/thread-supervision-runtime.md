# Reusable Lane Task Routing

Load only in `Reddit 分发台` for a direct user dispatch command. It resolves one exact task per requested account+lane, sends the new mission, persists routing, and returns idle. It is not ongoing supervision.

## Canonical Titles

| Lane | Title |
|-|-|
| comments | `Reddit 评论台` |
| posts | `Reddit 发帖台` |
| follow-up | `Reddit 跟进台` |
| browsing | `Reddit 浏览台` |
| presence | `Reddit 主页台` |

Titles are presentation labels. Exact task IDs plus the visible Reddit account are the routing identity.

## Account-Keyed Registry

Persist one user-owned registry outside the managed Skill tree:

```text
${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/lane-registry/<username>.json
```

Store `registry_version`, exact Reddit username, and per lane: `task_id`, canonical title, `last_mission_id`, `last_delivery_at`, and `last_delivery_state`. Never store credentials, Reddit content, Heartbeat IDs, worker runtime state, or sibling state. Write atomically and never reuse another Reddit account's registry.

## Resolve One Lane

For every requested lane, use this order:

1. **Registered reuse:** read the exact registered task ID once. If it exists, is the same canonical lane, belongs to the current Reddit account, and can accept a message, reuse it. Unarchive that exact registered task when needed, restore its canonical title if it drifted, keep it unpinned, and send the new mission.
2. **One-time legacy adoption:** only when the lane has no registry entry, perform one bounded lookup for the exact canonical title. Inspect at most the three newest candidates. Adopt only the newest task whose lane identity and visible Reddit account both match and whose history does not show a conflicting role. Persist its exact ID. If evidence is ambiguous, adopt none.
3. **Create or replace:** when no exact reusable task exists, create one new persistent task, capture the returned ID, rename it to the canonical title, keep it unpinned, send the mission, and atomically register it. If a registered task is permanently unavailable or rejects delivery after one bounded transient retry, create one replacement and overwrite only that lane's registry entry.

Do not create a duplicate when a healthy registered task accepted delivery. Do not select by title alone. Do not adopt a task from another Reddit account. Do not revive a completed mission or old Heartbeat: task reuse carries only the durable task surface and its lane history; the incoming `mission_id` is new and supersedes prior mission fields.

## Delivery Contract

1. Generate a new `mission_id` for the current user command even when the task is reused.
2. Send the complete mission to the resolved exact task ID with `worker_task_id=<that same exact destination task ID>`, `first_due=now`, `heartbeat_owner=self`, and `launcher_callback=none`.
3. The worker reads its exact current-task ID from host context and accepts the mission only when it equals `worker_task_id`. It then applies its latest-command rule, executes the first slot immediately, and creates/updates only its own explicitly bound and post-read-verified Heartbeat for unfinished work. If its previous mission finished, the retired old Heartbeat stays retired; the new mission creates a new lifecycle.
4. Successful message acceptance is delivery proof. Persist `last_mission_id`, timestamp, and `reused|adopted|created|replaced`.
5. Return the exact title and routing state, then release launcher ownership.

If delivery certainty is unknown, do not send the same mission to a second task because that could duplicate Reddit actions. Report that lane as `delivery_uncertain`; other lanes continue.

## Independence

- No combined worker or invisible subagent as lane owner.
- No launcher Heartbeat and no worker callback.
- No ongoing task reads between direct user commands.
- No sibling discovery from a worker.
- No shared-tab or account collision checks.
- No cross-task pause, timer change, status aggregation, archive, or completion monitoring.

The distributor may read/reuse/adopt/replace tasks only during a direct dispatch command. After successful delivery it returns to pinned idle. Workers never register with, callback, or send completion/risk events to the distributor.
