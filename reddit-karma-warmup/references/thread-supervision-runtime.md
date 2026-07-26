# Reusable Lane Task Routing

Load only in `Reddit 分发台` for a direct user dispatch command. It resolves one exact task per requested account+lane, sends the new mission, persists routing, and returns idle. It is not ongoing supervision.

## Generic Supervisor Alignment

This scoped contract adopts the current semantic task-health contract from
`thread-supervisor`; it intentionally does not pin a revision because Reddit is
published independently:

- choose the task operation before the topology;
- identify a task by exact `task_id` plus `host_id` when the host exposes one;
- use persistent user-visible tasks, not subagents, for Reddit lanes the user asked to operate independently;
- treat titles, directories, previews, and search results as labels/discovery evidence only;
- preserve the exact returned identifier type and never treat a queued `clientThreadId` as a ready `threadId`;
- omit model and reasoning overrides unless the current user command explicitly
  supplies them; an explicit preferred-model request may use the
  user-authorized fallback chain in `operation-defaults.json`, but model choice
  never proves liveness, delivery, archive state, or replacement eligibility;
- treat create/send/read requests as intent, not success proof; use returned identity and supported readback/acceptance evidence.
- treat a task as reusable only with current exact-ID, present/unarchived,
  account/lane-matched proof; an archived task is never healthy or reusable.

The external `thread-supervisor` Skill is optional. Its absence does not block
Reddit because this file contains the required scoped contract. Its generic
coordinator/callback protocol must not override Reddit's independent
no-callback lane topology; Reddit has no shared version lock with the TikTok
bundle.

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

Store `registry_version`, exact Reddit username, and per lane: `task_id`, optional `host_id`, `identifier_state=ready`, canonical title, `last_known_archive_state=unarchived`, `last_mission_id`, `last_delivery_at`, and `last_delivery_state`. `last_known_archive_state` is cached routing evidence only: re-read current product state on every direct dispatch. Never store credentials, Reddit content, Heartbeat IDs, worker runtime state, or sibling state. Write atomically and never reuse another Reddit account's registry.

Current presence proof must come from a host-exposed archive-state readback or
the product's current unarchived task inventory for the exact task ID and
`host_id`. `read_thread` history alone is observation, not liveness.

Treat these states differently:

- `ARCHIVED_EXACT`, `MISSING_EXACT`, or a permanent exact-task delivery
  rejection: replacement is eligible; never auto-unarchive the old task.
- `LIVENESS_UNVERIFIED` (`notLoaded`, empty/partial inventory, host/tool timeout,
  or unknown archive result): the task is not reusable. For this direct new
  mission, create one fresh same-lane replacement immediately; do not message,
  unarchive, or otherwise operate the old task. Persist the old ID as
  `UNAVAILABLE_SUPERSEDED_PENDING_ACCEPTANCE`, then overwrite the registry only
  after the replacement has `DELIVERY_ACCEPTED`.
- a host that never exposes archive state or a usable current inventory:
  apply the same fresh-replacement policy once per lane+mission. The missing
  capability is not proof that the old task is absent and never authorizes
  archive mutation.

A registry written before `last_known_archive_state` existed remains readable,
but its task still needs the same current proof.

## Resolve One Lane

For every requested lane, use this order:

1. **Registered reuse:** resolve the exact registered task ID once, passing its
   `host_id` to host-aware tools, and separately obtain current
   presence/archive proof. Reuse it only when current product state proves it
   is present and unarchived, it is the same canonical lane, it belongs to the
   current Reddit account, and the exact send yields a `DELIVERY_ACCEPTED`
   host receipt. A readable archived task, exact archived ID, matching title,
   accessible history, prior idleness, or a requested model is not liveness.
   Never auto-unarchive it. Restore the canonical title only for a currently
   unarchived reusable task, keep it unpinned, and apply a model override only
   when the current user command explicitly authorizes one.
2. **Unavailable routing:** if the exact registered task is `notLoaded`, absent
   from an incomplete/empty inventory, produces a transient tool failure, or
   has unknown archive state, do not message, adopt, or revive that old task.
   Create one fresh same-lane replacement for this mission. Use a deterministic
   `replacement_key=<account>/<lane>/<mission_id>` and record it before create;
   a second create is forbidden for the same key. If create returns only a
   queued ID, or handoff delivery is uncertain, return
   `replacement_creation_uncertain`/`delivery_uncertain` and do not create
   again. `DELIVERY_UNCERTAIN` for an otherwise healthy selected task follows
   the same no-second-send rule.
3. **One-time legacy adoption:** only when the lane has no registry entry and a
   current reliable unarchived inventory is available, perform one bounded
   lookup among current present/unarchived tasks for the exact canonical title.
   Inspect at most the three newest candidates that are eligible under this
   unarchived-only rule. Archived search/history entries are ineligible. Adopt
   only one uniquely supported task whose lane identity and visible Reddit
   account both match and whose history does not show a conflicting role.
   Persist its exact ID and returned `host_id` only after `DELIVERY_ACCEPTED`.
   If zero or multiple candidates remain plausible, adopt none; never choose by
   recency alone.
4. **Create or replace:** create one new persistent projectless task when there
   is no registry entry after reliable legacy-adoption resolution, or replace
   after `ARCHIVED_EXACT`, `MISSING_EXACT`, `PERMANENT_DELIVERY_REJECTION`, or
   the unavailable-routing state above. Leave every prior task untouched. Put
   the lane identity, Reddit account, and
   same-turn assignment expectation in the initial prompt, capture the returned
   identifier, rename the ready task to the canonical title, keep it unpinned,
   send the complete mission immediately, and atomically register it only after
   `DELIVERY_ACCEPTED`. If the tool returns a ready `threadId`, use it. If it
   returns only a queued `clientThreadId`, do not register, rename, message, or
   claim the lane ready until product state exposes the real task ID. Omit model
   fields unless the current user command explicitly requests them. Never
   recreate a healthy reusable lane because model readback is missing or an
   override is unverified. Record requested pair, actual pair when exposed, and
   evidence state separately only for an explicit model request.

Do not create a duplicate when a healthy present/unarchived registered task has
`DELIVERY_ACCEPTED`, or when this mission already holds the lane's
`replacement_key`. A readable task, successful rename, accessible archived
history, or model metadata is neither archive-state nor delivery proof. Do not
search archives, select by title alone, choose by recency alone, or adopt a task
from another Reddit account. Do not revive a completed mission or old
Heartbeat: task reuse carries only the durable unarchived task surface and its
lane history; the incoming `mission_id` is new and supersedes prior mission
fields.

## Mistaken Unarchive Recovery

If ordinary dispatch mistakenly unarchived an old registered task, do not promote that mistake into health or reuse evidence:

1. Stop and release any mission mistakenly delivered to the old task without replaying uncertain Reddit actions.
2. Create a fresh replacement and require `DELIVERY_ACCEPTED`.
3. Update the lane registry only after the replacement has `DELIVERY_ACCEPTED`.
4. Rearchive the old exact task only after its mission, Heartbeat, and Chrome ownership are proven released.

The generic restore exception remains separate: restore an archived task only when the user explicitly asks to resume that exact task. A broad Reddit dispatch, account direction, or request to reuse healthy lanes is never such authorization.

## Delivery Contract

1. Generate a new `mission_id` for the current user command even when the task is reused.
2. Send the complete mission to the resolved exact ready task ID, passing
   `host_id` when supported, with `worker_task_id=<that same exact destination
   task ID>`, `first_due=now`, `heartbeat_owner=self`, and
   `launcher_callback=none`. Omit model fields unless the current user command
   explicitly supplies a model request. On an explicit request, record the
   request, actual pair when exposed, and evidence state.
3. The worker reads its exact current-task ID from host context and applies the
   mission only when it equals `worker_task_id`. It then applies its latest-
   command rule, executes the first slot immediately, and creates/updates only
   its own explicitly bound and post-read-verified Heartbeat for unfinished
   work. If its previous mission finished, the retired old Heartbeat stays
   retired; the new mission creates a new lifecycle.
4. `DELIVERY_ACCEPTED` is the Reddit domain gate: a successful exact host send
   receipt addressed to the ready task ID. It proves dispatch delivery, not the
   worker's later Reddit execution. A create response, readable summary, rename,
   pin, or uncertain tool timeout is not `DELIVERY_ACCEPTED`. Persist
   `last_mission_id`, timestamp, exact `task_id`, optional `host_id`, and
   `reused|adopted|created|replaced` only after this receipt.
5. Call a requested first dispatch complete only when comments, posts, and
   follow-up each have `DELIVERY_ACCEPTED`. If any lane has
   `replacement_creation_uncertain` or `delivery_uncertain`, call it a partial dispatch,
   name that lane, and never claim that all first-round missions were sent.
6. Return the exact accepted titles and any failed lane, then release launcher ownership.

If delivery certainty is unknown, do not send the same mission to a second task
because that could duplicate Reddit actions. Report that lane as
`delivery_uncertain`; other lanes continue.

## Independence

- No combined worker or invisible subagent as lane owner.
- No launcher Heartbeat and no worker callback.
- No ongoing task reads between direct user commands.
- No sibling discovery from a worker.
- No sibling page/content inspection or account-state coordination. A lane may
  inspect only local `chrome_tab_lease/v1`/`chrome_control_slot/v1` metadata to
  avoid shared-tab or concurrent-control collisions; it must never use that
  metadata to claim, read, or wait on a sibling tab.
- No cross-task pause, timer change, status aggregation, archive, or completion monitoring.

The distributor may read/reuse/adopt/replace tasks only during a direct dispatch command. After successful delivery it returns to pinned idle. Workers never register with, callback, or send completion/risk events to the distributor.
