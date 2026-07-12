# Reusable Stateless Launcher

Load only in `Reddit 启动台`. The launcher installs/checks readiness once, then may accept repeated direct user dispatch commands. For every command it creates fresh requested lane tasks, delivers the new missions, and returns to idle. It is not a coordinator.

## Single Objective

For the current user command, create one fresh independent lane task for every requested lane and deliver each complete mission successfully.

Out of scope:

- Reddit browsing or mutation
- worker execution acceptance or quality review
- recurring Heartbeat creation or repair
- worker callbacks, status pulls, risk consolidation, or completion aggregation
- reading, steering, or reopening lane tasks after dispatch

## Dispatch

1. Normalize the current direct user request through `default-operations-sop.md` and generate a new run ID.
2. Broad `开始/运营` enables comments, posts, and follow-up. Add presence only when the profile baseline is incomplete or explicitly requested. Create browsing only for an explicit pure-browse/vote request. A named lane enables only that lane.
3. Use `thread-supervision-runtime.md` to create one new persistent task per enabled lane. Do not list/search/read/reuse/unarchive/revive historical tasks.
4. Capture only the exact IDs returned by this run's task-creation calls. Rename each new task to its canonical lane title and keep it unpinned.
5. Send one complete handoff containing lane, objective, exclusions, account, duration/count, intensity, style, language, target pool, stop time, first due=`now`, exact action target/cap/read floor, `incidental_voting=already_read_content_only` for comments/posts/follow-up, required references, and `heartbeat_owner=self`.
6. Verify only that the exact task accepted the mission message. Do not wait for its Chrome result and do not create a supervisor.
7. Return the created titles plus the routing instruction below, using only the tasks created in this dispatch, then enter `L3_IDLE`.

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

## Post-Dispatch Instruction

```text
已启动：<created titles>。

后续请直接到对应任务操作：
- 评论、候选帖子互动：Reddit 评论台
- 主帖、版规和发帖候选：Reddit 发帖台
- Notifications、回复和后续互动：Reddit 跟进台
- 自然浏览/投票：随以上执行台读取内容时完成；纯浏览任务才单独创建 Reddit 浏览台
- 新开一轮或重新分配任务：回到 Reddit 启动台
```

Include only execution routes whose tasks were created in this dispatch. Always retain the natural-browsing explanation and final launcher route. If browsing was explicitly created, replace its line with `纯浏览/投票：Reddit 浏览台`.

The launcher task stays stateless and idle after delivery. A worker never sends anything back. The user may continue that run in its lane task or send another direct command to this launcher; the next command repeats fresh creation with a new run ID and still does not inspect prior tasks.
