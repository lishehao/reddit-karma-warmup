# Reusable Lane Task Routing

Load only in `Reddit 分发台` for a direct user dispatch command. It resolves one exact task per requested account+lane, sends the new mission, persists routing, and returns idle. It is not ongoing supervision.

## Generic Supervisor Alignment

This scoped contract is aligned with `thread-supervisor` revision `2026.07.14.5`:

- choose the task operation before the topology;
- identify a task by exact `task_id` plus `host_id` when the host exposes one;
- use persistent user-visible tasks, not subagents, for Reddit lanes the user asked to operate independently;
- treat titles, directories, previews, and search results as labels/discovery evidence only;
- preserve the exact returned identifier type and never treat a queued `clientThreadId` as a ready `threadId`;
- for a newly created Reddit task, select the first host-supported model pair from `operation-defaults.json`: `gpt-5.6-terra/high`, then `gpt-5.6-luna/high`, then `gpt-5.5/high`, then `gpt-5.4/high`; an explicit user override wins;
- treat create/send/read requests as intent, not success proof; use returned identity and supported readback/acceptance evidence.

The external `thread-supervisor` Skill is optional. Its absence does not block Reddit because this file contains the required scoped contract. Its generic coordinator/callback protocol must not override Reddit's independent no-callback lane topology.

## Canonical Titles

| Lane | Title |
|-|-|
| comments | `Reddit 评论台` |
| posts | `Reddit 发帖台` |
| follow-up | `Reddit 跟进台` |
| browsing | `Reddit 浏览台` |
| presence | `Reddit 主页台` |

Titles are presentation labels. Exact task IDs, `host_id` when applicable, plus the visible Reddit account are the routing identity.

## Account-Keyed Registry

Persist one user-owned registry outside the managed Skill tree:

```text
${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/lane-registry/<username>.json
```

Store `registry_version`, exact Reddit username, and per lane: `task_id`, optional `host_id`, `identifier_state=ready`, canonical title, `last_mission_id`, `last_delivery_at`, and `last_delivery_state`. Never store credentials, Reddit content, Heartbeat IDs, worker runtime state, or sibling state. Write atomically and never reuse another Reddit account's registry.

## Resolve One Lane

For every requested lane, use this order:

1. **Registered reuse:** read the exact registered task ID once, passing its `host_id` to host-aware tools. If it exists, is the same canonical lane, belongs to the current Reddit account, and can accept a message, reuse it. Unarchive that exact registered task when needed, restore its canonical title if it drifted, keep it unpinned, and send the new mission.
2. **One-time legacy adoption:** only when the lane has no registry entry, perform one bounded lookup for the exact canonical title. Inspect at most the three newest candidates. Adopt only one uniquely supported task whose lane identity and visible Reddit account both match and whose history does not show a conflicting role. Persist its exact ID and returned `host_id`. If zero or multiple candidates remain plausible, adopt none; never choose by recency alone.
3. **Create or replace:** when no exact reusable task exists, create one new persistent projectless task for this general Chrome operation. The user's current dispatch command is the authorization for this persistent task. Use the first host-supported pair in the canonical model fallback chain; if model availability cannot be queried, attempt the chain in order and treat an unsupported-model response as a creation retry, not an operation blocker. Put the lane identity, Reddit account, and same-turn assignment expectation in the initial prompt, capture the returned identifier, rename the ready task to the canonical title, keep it unpinned, send the complete mission immediately, and atomically register it only after acceptance. If the tool returns a ready `threadId`, use it. If it returns only a queued `clientThreadId`, do not register, rename, message, or claim the lane ready until product state exposes the real task ID. If a registered task is permanently unavailable or rejects delivery after one bounded transient retry, create one replacement and overwrite only that lane's registry entry. Never recreate a healthy reusable task merely to change its model; record its actual runtime and continue.

Do not create a duplicate when a healthy registered task accepted delivery. A readable task or successful rename is not delivery proof. Do not select by title alone, choose by recency alone, or adopt a task from another Reddit account. Do not revive a completed mission or old Heartbeat: task reuse carries only the durable task surface and its lane history; the incoming `mission_id` is new and supersedes prior mission fields.

## Delivery Contract

1. Generate a new `mission_id` for the current user command even when the task is reused.
2. Send the complete mission to the resolved exact ready task ID, passing `host_id` when supported, with `worker_task_id=<that same exact destination task ID>`, `first_due=now`, `heartbeat_owner=self`, and `launcher_callback=none`.
3. The worker reads its exact current-task ID from host context and accepts the mission only when it equals `worker_task_id`. It then applies its latest-command rule, executes the first slot immediately, and creates/updates only its own explicitly bound and post-read-verified Heartbeat for unfinished work. If its previous mission finished, the retired old Heartbeat stays retired; the new mission creates a new lifecycle.
4. Successful message acceptance by the exact selected task is delivery proof. A create response, readable summary, rename, or pin alone is not. Persist `last_mission_id`, timestamp, exact `task_id`, optional `host_id`, and `reused|adopted|created|replaced` only for accepted lanes.
5. Call a requested first dispatch complete only when comments, posts, and follow-up each accepted their exact mission. If any lane is unavailable or `delivery_uncertain`, call it a partial dispatch, name that lane, and never claim that all first-round missions were sent.
6. Return the exact accepted titles and any failed lane, then release launcher ownership.

If delivery certainty is unknown, do not send the same mission to a second task because that could duplicate Reddit actions. Report that lane as `delivery_uncertain`; other lanes continue.

## Independence

- No combined worker or invisible subagent as lane owner.
- No launcher Heartbeat and no worker callback.
- No ongoing task reads between direct user commands.
- No sibling discovery from a worker.
- No shared-tab or account collision checks.
- No cross-task pause, timer change, status aggregation, archive, or completion monitoring.

The distributor may read/reuse/adopt/replace tasks only during a direct dispatch command. After successful delivery it returns to pinned idle. Workers never register with, callback, or send completion/risk events to the distributor.
