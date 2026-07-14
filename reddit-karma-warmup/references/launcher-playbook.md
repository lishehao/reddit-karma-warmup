# Reusable Lane Distributor

Load in the pinned `Reddit 分发台` after temporary `Reddit 启动台` setup passes preflight. For every direct command it routes each requested lane to the healthy registered task for the visible Reddit account, creates only missing/unusable replacements, delivers the new missions, and returns to pinned idle. It is not a coordinator.

## Single Objective

For the current user command, resolve one exact independent task per requested lane and deliver each complete mission successfully.

Out of scope:

- Reddit browsing or mutation
- worker execution acceptance or quality review
- recurring Heartbeat creation or repair
- worker callbacks, status pulls, risk consolidation, or completion aggregation
- reading or steering lane tasks between user dispatch commands

## Dispatch

1. Resolve the exact visible Reddit account, its durable `account_direction`, and cached catalog retrieval through `account-direction.md`; normalize the command through `default-operations-sop.md`; generate a new `mission_id`.
2. Broad `开始/运营` enables comments, posts, and follow-up. Add presence only when the profile baseline is incomplete or explicitly requested. Create browsing only for an explicit pure-browse/vote request. A named lane enables only that lane.
3. Use `thread-supervision-runtime.md` to resolve each lane: registered reuse first, bounded one-time legacy adoption only when unregistered, then create/replace only when no exact reusable task exists.
4. Keep the distributor pinned and every execution task unpinned. Canonical titles are stable; exact task IDs and the account-keyed registry determine ownership.
5. Send one complete handoff containing lane, objective, exclusions, account, `account_direction`, `direction_tags`, `direction_source`, `subreddit_shortlist`, `traffic_probe_queue`, duration/count, intensity, per-run style, language, target pool, stop time, first due=`now`, exact action target/cap/read floor, `incidental_voting=already_read_content_only` for comments/posts/follow-up, required references, and `heartbeat_owner=self`. A traffic-probe row is not an action target until the worker confirms at least `5,000` weekly visitors and passes the exact rule/account gate.
6. Verify only that the exact selected task accepted the mission message. Do not wait for its Chrome result and do not create a supervisor.
7. Persist the exact lane ID and `reused|adopted|created|replaced` state, return the routed titles, then enter `L4_IDLE`.

The distributor never creates timers for workers. Each worker executes immediately, then creates and owns its self-targeted Heartbeat only for unfinished mission work.

If one lane cannot be resolved or accept delivery, report only that lane as unavailable or uncertain. Dispatch every other requested lane normally. Never merge lanes or execute the missing lane in the distributor.

## Handoff Card

```text
role=WORKER
lane=<comments|posts|follow-up|browsing|presence>
single_objective=<one lane outcome>
out_of_scope=<all other lane outcomes>
mission_id=<new mission ID>
task_routing=<reused|adopted|created|replaced>
first_due=now
heartbeat_owner=self
launcher_callback=none
sibling_visibility=none
subreddit_shortlist=<cached >=5K matches>
traffic_probe_queue=<fit matches needing live traffic check>
```

## Post-Dispatch Instruction

```text
已分发：<title + 沿用/收编/新建/替换>。

后续请直接到对应任务操作：
- 评论、候选帖子互动：Reddit 评论台
- 主帖、版规和发帖候选：Reddit 发帖台
- Notifications、回复和后续互动：Reddit 跟进台
- 自然浏览/投票：随以上执行台读取内容时完成；纯浏览任务才单独使用 Reddit 浏览台
- 新一轮或重新分配任务：回到 Reddit 分发台；默认继续沿用以上执行台
```

Include only routes selected in this dispatch. Always retain the natural-browsing explanation and final distributor route. If browsing was explicitly selected, use `纯浏览/投票：Reddit 浏览台`.

The distributor keeps only the account-keyed lane registry and remains pinned/idle after delivery. A worker never sends anything back. The user may continue inside a lane task or issue another command in the distributor; the next command generates new mission IDs but normally reuses the registered lane tasks.
