# Independent Task Allocation

Load only in `Reddit 启动台` while allocating the first requested lanes. This is task creation/reuse, not ongoing supervision.

## Canonical Tasks

| Lane | Title |
|-|-|
| comments | `Reddit 评论台` |
| posts | `Reddit 发帖台` |
| follow-up | `Reddit 跟进台` |
| browsing | `Reddit 浏览台` |
| presence | `Reddit 主页台` |

Each lane has exactly one active task for the dispatched mission. Titles are discovery hints; exact task IDs prove ownership.

## Resolve Or Create

1. Search for an unarchived task with the canonical lane title.
2. Reuse it only when its exact ID is readable and the current mission delivery succeeds.
3. Archived tasks are retired. Missing-rollout evidence is a stale tombstone. Transient host/tool failure preserves the candidate for one bounded retry.
4. If no live owner exists, create one persistent user-visible task, capture its exact ID, rename it immediately, and keep it unpinned.
5. Send the actual mission, not a probe. If delivery fails deterministically, create at most one replacement for that lane.
6. Record successful delivery, return the task title to the user, and release launcher ownership.

The launcher never creates timers for workers and never reads them again after dispatch. Workers never register with, callback, or send completion/risk events to the launcher.

## Independence

- No combined worker.
- No invisible subagent as lane owner.
- No launcher registry after delivery.
- No sibling task discovery from a worker.
- No shared-tab or account collision checks.
- No cross-task pause, amendment, timer change, archive, or status inspection.

Task title or pin control failure does not block delivery. A worker can correct its own title later.
