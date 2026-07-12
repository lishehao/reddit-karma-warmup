# On-Demand Operations Audit

Load only in the user-facing `Reddit 主控台` task when the user asks whether the other tasks are operating as expected. This is a read-only diagnosis by default, not a fifth execution lane and not continuous supervision.

## Audit Scope

Audit the current active mission by default. Include older rounds only when the user asks for a historical review or when recent history is required to judge cadence, repetition, or length mix.

Collect the smallest evidence set that can prove the result:

1. Coordinator mission contract: enabled lanes, count/intensity/style, start/stop times, expected first action, and expected next slots.
2. Worker registry: one distinct `LIVE_REGISTERED` `worker_thread_id` per enabled lane, correct title/role, latest `1-3` relevant turns, successful current mission delivery, and exact action/no-action evidence. Search/title/readable-summary evidence alone is insufficient.
3. Coordinator-managed automation: automation ID, exact `target_thread_id`, prompt/lane match, repeat-on state, recurrence, stop guard, intended local/UTC next run, and actual wake/run time when exposed.
4. Published evidence: exact text, permalink, author/subreddit, submit time, worker verification, and current visibility state. The coordinator may open only exact permalinks and relevant profile/history surfaces in a dedicated read-only tab; it must not perform exploratory browsing or mutations.
5. Recent action ledger: timestamps, subreddits/clusters, action type, character/word counts, sentence form, length tier, and quality-gate evidence.

Never infer success from a task title, automation name/card, plan, or `已启动` claim alone. Mark unavailable evidence as `无证据`; do not convert it into success or failure.

## Five Audit Dimensions

### 1. Topology And Ownership

Check:

- every enabled lane has its own persistent task ID
- worker role matches `Reddit 评论台`, `Reddit 发帖台`, `Reddit 跟进台`, or `Reddit 浏览台`
- every canonical owner is unarchived and accepted its current mission; archived or summary-only candidates are not live owners
- the coordinator did not execute a lane action
- each continuation targets its owning worker, not the coordinator or another lane
- no combined execution heartbeat absorbed several lanes
- every stale-owner replacement records old/new task IDs, the exact missing-rollout reason, and the new automation binding
- no active automation targets a stale/retired task ID, and only one canonical live owner exists per lane

Any missing worker ID, summary-only owner, orphan automation, duplicate canonical owner, coordinator-executed lane action, or mismatched `target_thread_id` is `不合格` even when an individual Reddit action succeeded. If the host cannot expose automation evidence, mark that cleanup field `无证据`; do not claim the stale owner was fully retired.

### 2. Automation Timing

For each due continuation, compare:

```text
intended_local | intended_utc | persisted_schedule | actual_wake_utc
target_thread_id | recurrence/repeat_on | operation_stop_at
```

Classify timing:

- `准确`: target binding is correct and actual/persisted time is within `5 min` of the intended UTC instant
- `轻微延迟`: correct binding and `>5` to `15 min` late, with no hour-scale offset or missed work
- `不准确`: wrong task, wrong day/hour, local/UTC offset error, repeat is off/`COUNT=1`, recurrence differs from the mission, fired after stop time, or `>15 min` late without a concrete runtime reason
- `无证据`: create succeeded but persisted and actual run time are both unavailable

If the next run has not become due, audit only binding and persisted schedule; do not call it missed. Compare actual wake history after it becomes due.

### 3. Execution And Visibility

Compare requested work with actual verified work:

- comments/posts/replies: exact text plus permalink and visibility evidence
- follow-up: Notifications and recent own Posts/Comments surfaces actually checked; actionable items handled or specifically rejected
- browsing: qualified-read count, concrete observations, vote decisions, accepted one-time click results, and no-votes
- no-action: exact candidates/surfaces and the valid gate that rejected them

A no-action result is valid only when its reason matches the Skill. For example, `K0 has not waited 6h` cannot reject the first daily post; `ERR_BLOCKED_BY_CLIENT` on one route cannot end the whole browsing lane before Chrome recovery and alternate-route attempts.

Refusing, downgrading, or requesting confirmation for a current explicit mission solely because of historical/cleared removals, warnings, rate limits, locks, an old recovery preset, or an older mission field is `不合格`. A currently visible timed limit may delay only until expiry and must retain automatic continuation of the original user command.

For every removal/filter/lock/subreddit ban/pending withdrawal, verify that the exact subreddit entered the retired set, `SUBREDDIT_RETIRED` informed the coordinator once, and the worker continued in another eligible community. An account-tier downgrade, generic slowdown, or process-wide pause from removal evidence alone is `不合格` unless Reddit separately displayed an account-level warning/rate-limit/captcha/lock/suspension/login problem.

Use visibility labels from `startup-health-check.md`. If the coordinator cannot independently open the permalink, report worker proof separately from current independent visibility.

### 4. Cadence And Coverage

Compare actual timestamps with the mission plan and lane limits:

- first micro-slot occurred in the user-command turn, not only at the next heartbeat
- verified comment submissions retained their required local pause and were not caught up in a burst
- post spacing, same-subreddit `24h` history, and second-same-day `6h` gate were applied correctly
- follow-up and browsing intervals remained within the selected range unless live state justified a change
- subreddit, topic cluster, and action distribution did not become needlessly repetitive
- missed slots were replanned from actual time rather than compressed

Classify `节奏正常`, `偏慢/偏快但可解释`, or `节奏不合格`, and name the timestamps that support the decision.

### 5. Content Length And Quality

Read the exact recent outward texts, not only worker summaries. For comments/replies, inspect up to the latest `10`; for posts, inspect all posts in the current mission.

Length review:

- verify measured character/word counts and sentence forms when available
- check that comments bias toward micro/fragment/one-liner without mechanically rotating tiers
- flag repeated two-sentence shapes, repeated openings, uniform length, unnecessary paragraphs, or length unsupported by nearby native style
- distinguish purposeful repetition from accidental templating

Score each sampled text only from visible evidence:

| Factor | Points |
|-|-:|
| Exact target/context specificity | 0-25 |
| Useful insight, distinction, question, or precise praise | 0-25 |
| Native subreddit/thread style fit | 0-20 |
| Appropriate compression and length choice | 0-15 |
| Truthfulness plus diversity versus recent history | 0-15 |

- `>=80`: `合格`
- `65-79`: `需改进`
- `<65`: `不合格`

Do not reward slang, fragments, or brevity by themselves. Generic praise, unsupported experience, repetitive syntax, weak context fit, or polished filler lowers the score.

## Lane And Overall Verdict

Give every relevant lane one verdict:

- `合格`: requested execution and required automation/evidence all pass
- `部分合格`: action/no-action judgment is sound, but one non-core proof or timing item is missing/late
- `不合格`: wrong ownership, wrong schedule, invalid skip reason, missed required recovery, unverified publishing, or poor/repetitive content
- `无证据`: the host cannot read enough worker/automation/action evidence

Overall accuracy is not an average that hides a broken lane. Report both:

```text
动作判断准确度 = sound action/no-action decisions / relevant lanes
端到端合格度 = lanes passing ownership + execution + evidence + required handoff / relevant lanes
```

## Audit Report

Use concise Chinese:

```text
总体：动作判断准确度 <N/M>；端到端合格度 <N/M>。
评论：<执行｜自动化｜节奏｜长度/质量｜结论>。
发帖：<执行｜自动化｜节奏｜长度/质量｜结论>。
跟进：<执行｜自动化｜节奏｜质量｜结论>。
浏览：<执行｜自动化｜节奏｜投票证据｜结论>。
主要问题：<按影响排序的 1-3 项>。
下一步：<只写可执行修复或待现场补证>。
```

Keep task IDs, raw scheduler fields, and internal scores hidden unless they explain a failure or the user asks for technical detail.

## Repair Boundary

An audit request is read-only. If the user also asks to fix problems:

1. Send the correction to the owning worker task.
2. The worker repairs only its lane action and returns new proof; scheduler repair belongs to the coordinator.
3. Re-audit the repaired evidence once.
4. The coordinator never substitutes for the worker or creates a combined execution trigger.

The coordinator deactivates a misbound/repeat-off/one-shot lane Heartbeat and creates one corrected recurring replacement explicitly targeting the worker.

For a stale task owner, the coordinator follows the atomic transaction in `thread-supervision-runtime.md`: remove old-ID automation bindings, keep the tombstone archived, create at most one replacement, deliver the current mission, verify the exact new ID, and bind only the new recurring Heartbeat. Do not ask a lane worker to repair its own missing rollout.
