# Fresh-Only Task Allocation

Load only in `Reddit 分发台` for each direct user dispatch command. This is repeatable one-way fresh task creation, not discovery, reuse, or ongoing supervision.

## Canonical Titles

| Lane | Title |
|-|-|
| comments | `Reddit 评论台` |
| posts | `Reddit 发帖台` |
| follow-up | `Reddit 跟进台` |
| browsing | `Reddit 浏览台` |
| presence | `Reddit 主页台` |

Titles are presentation labels only. Duplicate historical titles are expected and never used for ownership selection.

## Fresh Creation Contract

For every new launcher command/run:

1. Resolve enabled lanes without listing old tasks.
2. Call task creation exactly once for each enabled lane.
3. Capture the new task ID returned by that exact creation call and bind it to a new `run_id` plus lane.
4. Rename only that newly created task to the canonical lane title and keep it unpinned.
5. Send the actual current mission to that new ID. Successful delivery is the only handoff proof.
6. Record only this run's new IDs for the dispatch receipt, then release launcher ownership and enter idle.

The launcher must not call task list/search/read to find historical workers. It must not reuse, unarchive, revive, replace, inspect, rename, archive, or send a mission to an old task, regardless of title, status, age, readability, or whether an old run is still active.

If fresh task creation fails, return `fresh_task_creation_failed` for that lane. Do not retry by selecting an old task. One bounded retry of the create operation itself is allowed only for a transient task-tool failure when it cannot have created a task; if creation certainty is unknown, report it and do not create a possible duplicate.

## Independence

- No combined worker.
- No invisible subagent as lane owner.
- No launcher registry after delivery.
- No historical task discovery or fallback.
- No sibling task discovery from a worker.
- No shared-tab or account collision checks.
- No cross-task pause, amendment, timer change, archive, or status inspection.

The launcher never creates timers for workers and never reads the new workers again after delivery. Workers never register with, callback, or send completion/risk events to the launcher.

After delivery the same launcher may accept another user command and repeat this section with a new run ID. It carries no worker state across commands.
