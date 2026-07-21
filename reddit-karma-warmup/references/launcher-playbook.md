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

1. Load `operation-defaults.json`, `lane-action-ownership.md`, and `model-runtime.md`. Resolve the exact visible Reddit account, its durable `account_direction`, and one or two truthful `mission_identity_focus` pillars; normalize the command through `default-operations-sop.md`; generate a new `mission_id`.
2. Broad `开始/运营` enables comments, posts, and follow-up. Add presence only when the profile baseline is incomplete or explicitly requested. Create browsing only for an explicit pure-browse/vote request. A named lane enables only that lane.
3. For comments/posts, load `community-selection-funnel.md`, assess the selected lane's configured reference sweep, and produce a lane-specific low-friction shortlist before task delivery. Then use `thread-supervision-runtime.md` to resolve each lane by exact ready task ID plus `host_id` when available: registered reuse first, bounded one-time legacy adoption only when unregistered, then create/replace only when no exact reusable task exists. A queued `clientThreadId` is not a ready lane.
4. Keep the distributor pinned and every execution task unpinned. Canonical titles are stable; exact task IDs and the account-keyed registry determine ownership.
5. Order enabled mutation-capable lanes as `comments -> follow-up -> posts -> browsing -> presence`, assign phase indexes `0..n-1`, and send one complete handoff containing `worker_task_id=<the exact selected destination task ID>`, lane, objective, exclusions, account, tier/substate, `account_direction`, `direction_source`, `mission_identity_focus`, `direction_tags`, lane shortlist, duration/count, intensity, style, language, target pool, stop time, first due=`now`, phase fields, exact `action_target`, `action_cap`, hard `qualified_read_target`, `qualified_read_remaining`, lane-owned `vote_policy`, selected/actual model fields, required references, `checkpoint_path`, `checkpoint_schema_version=1`, `heartbeat_owner=self`, `dedicated_reddit_tab=required`, and `tab_persistence=handoff_until_mission_terminal`. Comments/posts/follow-up/presence always receive `vote_policy=DISABLED_BY_LANE`, `vote_cap=0`, zero current Upvote/Downvote counters, no vote target/remainder, and `browse_vote_playbook=NOT_LOADED`. Only browsing receives `vote_policy=BROWSING_ONLY`, `vote_target_mode=opportunity|hard`, optional explicit `vote_target`, hard `vote_cap`, and separate Upvote/Downvote counters. Every comments handoff also carries `per_item_copy_gate=required`, `cluster_copy_batching=forbidden`, and the resolved routine word cap. Every post handoff carries `main_post_unlock`, `post_action_mode`, exact `posting_gate_audit_rows`, and resolved K0/K1 limits. Every default question-post handoff carries the resolved discussion score gate. A traffic-probe row is not an action target until the worker confirms the catalog's minimum traffic requirement and passes the exact rule/account gate.
6. Verify only that the exact selected ready task accepted the mission message. A create response, readable summary, rename, or pin is not acceptance. Do not wait for its Chrome result and do not create a supervisor. A first default dispatch is complete only after comments, posts, and follow-up all accept their messages.
7. Persist the exact lane ID and `reused|adopted|created|replaced` state. Return the accepted titles; if any requested lane is unresolved or uncertain, use the partial-dispatch receipt and name it. Then enter `L4_IDLE`.

The distributor never creates timers for workers. Every worker starts reading and preparing immediately; phase `0` may mutate immediately, while later phases wait only for their assigned first-write boundary. Each worker then creates and owns its self-targeted Heartbeat only for unfinished mission work.

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
mutation_phase_index=<0..n-1>
initial_mutation_not_before=<resolved scheduler phase step * phase index>
phase_jitter_minutes=<resolved scheduler range>
missed_phase_policy=next_own_window
heartbeat_owner=self
dedicated_reddit_tab=required
tab_persistence=handoff_until_mission_terminal
checkpoint_path=<canonical account/lane/task checkpoint path>
checkpoint_schema_version=1
launcher_callback=none
sibling_visibility=none
per_item_copy_gate=<required for comments>
cluster_copy_batching=<forbidden for comments>
routine_comment_word_cap=<resolved comments.routine_word_cap>
interaction_pacing=measured_human_scale
candidate_dwell_min_seconds=<resolved interaction_pacing field>
comment_readable_to_submit_min_seconds=<resolved interaction_pacing field>
pre_submit_pause_seconds=<resolved interaction_pacing range>
inter_click_pause_seconds=<resolved interaction_pacing range>
post_discussion_gate=<required for question posts>
post_discussion_score_min=<resolved posts.discussion_score_min>
main_post_unlock=<locked|passed>
post_action_mode=<research_preflight_only|publish>
posting_gate_audit_rows=<exact candidate rows for posts>
mission_identity_focus=<one or two truthful direction pillars>
direction_source=<saved|default_loci_broad|explicit_user>
direction_tags=<normalized tags>
comment_shortlist_or_post_reference_shortlist=<lane-specific cached >=5K matches>
reference_rows_assessed=<resolved lane reference target>
traffic_probe_queue=<fit matches needing live traffic check>
qualified_read_target=<canonical hard target or explicit override>
qualified_read_remaining=<same initial value>
vote_policy=<DISABLED_BY_LANE except BROWSING_ONLY for browsing>
vote_cap=<0 for non-browsing; resolved cap for browsing>
browse_vote_playbook=<NOT_LOADED except LOADED for browsing>
vote_target_mode=<browsing only: opportunity by default; hard only when explicit>
vote_target=<browsing only: absent by default; explicit count only>
upvote_target=<browsing only: optional explicit directional target>
downvote_target=<browsing only: optional explicit directional target>
selected_model=<first supported fallback pair>
actual_model=<host-reported pair when exposed>
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
