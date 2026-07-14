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

1. Resolve the exact visible Reddit account, its durable `account_direction`, and one or two truthful `mission_identity_focus` pillars; normalize the command through `default-operations-sop.md`; generate a new `mission_id`.
2. Broad `开始/运营` enables comments, posts, and follow-up. Add presence only when the profile baseline is incomplete or explicitly requested. Create browsing only for an explicit pure-browse/vote request. A named lane enables only that lane.
3. For comments/posts, load `community-selection-funnel.md`, assess up to 100 matching reference rows, and produce a lane-specific low-friction shortlist before task delivery. Then use `thread-supervision-runtime.md` to resolve each lane: registered reuse first, bounded one-time legacy adoption only when unregistered, then create/replace only when no exact reusable task exists.
4. Keep the distributor pinned and every execution task unpinned. Canonical titles are stable; exact task IDs and the account-keyed registry determine ownership.
5. Send one complete handoff containing `worker_task_id=<the exact selected destination task ID>`, lane, objective, exclusions, account, tier/substate, `account_direction`, `mission_identity_focus`, `direction_tags`, `direction_source`, `comment_shortlist` or `post_reference_shortlist`, `reference_rows_assessed`, `traffic_probe_queue`, duration/count, intensity, per-run style, language, target pool, stop time, first due=`now`, exact action target/cap/read floor, `incidental_voting=already_read_content_only` for comments/posts/follow-up, required references, and `heartbeat_owner=self`. Every comments handoff also carries `per_item_copy_gate=required`, `cluster_copy_batching=forbidden`, and `routine_comment_word_cap=25`. Every post handoff carries `main_post_unlock`, `post_action_mode`, and exact `posting_gate_audit_rows`; K0 is always `research_preflight_only` with target/cap `0/0`, while K1 requires the unlock proof and is capped at one post per rolling `24h`. Every default question-post handoff carries `post_discussion_gate=required_for_question_posts` and `post_discussion_score_min=80`. A traffic-probe row is not an action target until the worker confirms at least `5,000` weekly visitors and passes the exact rule/account gate.
6. Verify only that the exact selected task accepted the mission message. Do not wait for its Chrome result and do not create a supervisor. A first default dispatch is complete only after comments, posts, and follow-up all accept their messages.
7. Persist the exact lane ID and `reused|adopted|created|replaced` state. Return the accepted titles; if any requested lane is unresolved or uncertain, use the partial-dispatch receipt and name it. Then enter `L4_IDLE`.

The distributor never creates timers for workers. Each worker executes immediately, then creates and owns its self-targeted Heartbeat only for unfinished mission work.

If one lane cannot be resolved or accept delivery, report only that lane as unavailable or uncertain. Dispatch every other requested lane normally. Never merge lanes or execute the missing lane in the distributor.

## Handoff Card

```text
role=WORKER
worker_task_id=<exact selected destination task ID>
lane=<comments|posts|follow-up|browsing|presence>
single_objective=<one lane outcome>
out_of_scope=<all other lane outcomes>
mission_id=<new mission ID>
task_routing=<reused|adopted|created|replaced>
first_due=now
heartbeat_owner=self
launcher_callback=none
sibling_visibility=none
per_item_copy_gate=<required for comments>
cluster_copy_batching=<forbidden for comments>
routine_comment_word_cap=<25 for ordinary proactive comments>
post_discussion_gate=<required for question posts>
post_discussion_score_min=<80>
main_post_unlock=<locked|passed>
post_action_mode=<research_preflight_only|publish>
posting_gate_audit_rows=<exact candidate rows for posts>
mission_identity_focus=<one or two truthful direction pillars>
comment_shortlist_or_post_reference_shortlist=<lane-specific cached >=5K matches>
reference_rows_assessed=<up to 100>
traffic_probe_queue=<fit matches needing live traffic check>
```

## Post-Dispatch Instruction

For the first healthy default dispatch, after all three mission messages are accepted, use:

```text
第一轮已分发：Reddit 评论台、Reddit 发帖台、Reddit 跟进台已收到任务。

后续所有 Reddit 运营任务都可以继续在这个 Reddit 分发台下达；告诉我方向、时长或具体动作即可，我会优先沿用已有执行台。

进行中的评论、发帖或跟进，请直接到对应执行台查看或调整。
```

For later complete dispatches, replace the first line with `本轮已分发：<actual accepted task titles>已收到任务。`. For a partial dispatch, use `本轮部分分发：<accepted task titles>已收到任务；<failed or uncertain lane>未确认投递。`. Keep the final two paragraphs unchanged. Never say `已分发` merely because tasks were resolved or messages were prepared.

The distributor keeps only the account-keyed lane registry and remains pinned/idle after delivery. A worker never sends anything back. The user may continue inside a lane task or issue another command in the distributor; the next command generates new mission IDs but normally reuses the registered lane tasks.
