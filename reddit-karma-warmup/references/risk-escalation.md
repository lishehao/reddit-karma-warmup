# Recovery And Rare User Escalation

Load in the `Reddit 主控台` coordinator and every worker. The user makes risk decisions only in the coordinator task. Lane workers never ask the user directly.

## Progress-First Contract

Default outcome is `continue`, not `blocked`. Apply this ladder before any user-facing interruption:

1. retry the exact read-only/control step once without replaying a mutation
2. reclaim a clean lane tab or native Reddit route
3. skip/retarget the candidate, subreddit, or action
4. continue other safe work in the same lane
5. keep lane and supervisor Heartbeats active and re-probe on later wakes

An empty candidate set, exhausted per-wake budget, missing selector, missing proof field, delayed visibility, worker transport failure, scheduler repair, timed rate limit, or uncertain exact mutation is a checkpoint with narrowed scope. It is never a mission-wide blocker or permission question.

## What Returns To Main

Use `RISK_ESCALATION` only when the user must perform or decide something that cannot be safely inferred:

- `user_repair_required`: credentials are required; the expected account remains logged out/wrong after recovery; a CAPTCHA/challenge requires manual completion; Reddit explicitly locks/suspends the account or requires user acknowledgement; or the only permitted Chrome control remains unavailable across three consecutive recovery wakes
- `explicit_target_decision`: the user explicitly required one exact target/action, live rules or truthfulness make it impossible, and no authorized substitute preserves the request

Task/worker transport, scheduler binding/time, route/network, candidate, and content-quality failures return to the coordinator as internal recovery evidence, not `RISK_ESCALATION`. The coordinator repairs one bounded step per supervisor wake while every valid Heartbeat and unaffected lane stays active. It may inform the user of degraded progress, but does not ask permission to continue.

Do not escalate ordinary operations noise:

- one low-score/stale/saturated candidate
- one subreddit with unclear rules when another eligible target remains
- no actionable Notification
- no qualified vote after the read budget
- no qualified post/comment candidate in the current slot
- a live rule that rejects one candidate/community when retargeting is possible
- delayed or unavailable `surface_visible`/`survivor_visible` proof after immediate submit proof
- one worker/task transport failure or missing rollout while replacement/retry is pending
- scheduler misbinding, unreadable next-run fields, or a missed wake while coordinator repair is pending
- a recoverable Chrome route error that succeeds after recovery
- a transient DNS/network/proxy/site loading error while its bounded `chrome-network-recovery.md` checkpoint is still pending
- normal count shortfall because too few candidates passed
- any historical or already-cleared removal, warning, rate limit, lock, or login fault
- a `STALE_OWNER_TOMBSTONE` that the coordinator atomically replaces with verified mission delivery and a correctly bound new Heartbeat
- pending-review cleanup, including automatic deletion/withdrawal and retry of an exact cleanup permalink
- a retryable lane-local Chrome/control/network/client-block/route failure while the lane Heartbeat remains active

These remain in the worker report and recurring recovery until they either recover, reach the deadline, or become an allowlisted user-repair state.

Missing-rollout evidence is an orchestration condition, never Reddit account risk. Do not ask the user to approve owner replacement. If one bounded replacement cannot accept the mission or receive continuation, keep the lane `lane_recovering`; the supervisor retries on later wakes while other lanes continue.

`SCHEDULER_CONTINUATION_FAILURE` is orchestration state, never Reddit account risk or a user-confirmation gate. The coordinator preserves completed actions and valid timers, records slot counts, marks the mission `degraded`, and retries repair on later supervisor wakes.

## Non-Blocking Subreddit Retirement Notice

A removal/filter/lock/subreddit ban, invalidating parent deletion, or pending-approval withdrawal retires only that exact subreddit. It is not `RISK_ESCALATION` without separate account-level evidence.

Pending approval is never a user decision. Delete/withdraw the own post immediately, verify once, retire the subreddit, and continue. If cleanup is temporarily unreachable, queue the exact permalink for automatic lane-local retry; do not ask the user or pause any lane.

The worker immediately retargets to another eligible community and sends one informational event to `coordinator_thread_id`:

```text
type = SUBREDDIT_RETIRED
mission_id
lane
subreddit + permalink
observed_state = removed | filtered | locked | subreddit_ban | parent_deleted | pending_withdrawn
evidence = exact visible notice/state; no inferred account penalty
action_taken = retired subreddit; no repost; replacement discovery continuing
process_state = continuing
```

The coordinator informs the user once without asking for confirmation and without pausing any worker. Use the normal three-line format: put the retirement and continuing state in `本轮完成`, retain the verified next Heartbeat, and name the replacement-community work in `下轮计划`.

## Worker Protocol

When the rare user escalation is required:

1. Stop only the currently impossible exact action. Keep the lane Heartbeat active for recovery, continue other safe work in this lane, and keep unrelated lanes outside this worker's control.
2. Preserve exact evidence: URL/surface, time local+UTC, Reddit/browser message, submit state, automation ID/target when relevant, and actions already completed.
3. Report retry state and the next planned re-probe. The recurring Heartbeat stays active unless the user stopped the scope, the deadline arrived, the lane became terminal, or the coordinator verified a corrected replacement. Do not inspect or alter sibling automations.
4. Send one message to the exact `coordinator_thread_id`:

```text
RISK_ESCALATION
mission_id: <id>
lane: <comments|posts|follow-up|browsing|presence>
severity: <user_repair_required|explicit_target_decision>
evidence: <one concise factual paragraph>
likely_cause: <one or two evidence-based possibilities, explicitly marked as possible>
recovery_attempts: <what was retried and the observed result>
affected_scope: <candidate|subreddit|lane|account>
current_state: <exact_action_withheld | lane_recovering | terminal; completed actions preserved>
safe_options: <exact user repair | authorized substitute | stop exact scope>
user_action_needed: <exact decision or repair>
```

5. End the worker turn in `awaiting_coordinator_decision` only for the allowlist above. A visible timed rate limit is automatic recovery: preserve the mission, continue permitted work, and resume on/after expiry without requesting a decision. Do not broaden the held scope to siblings.

If the worker-to-coordinator message capability is unavailable, withhold only the exact action requiring a decision and mark `risk_return_unavailable`. Keep its recurring Heartbeat active; the coordinator's next supervisor pull must surface it before that exact action resumes. Unrelated work remains active.

## Coordinator Protocol

On a valid `RISK_ESCALATION`:

1. Read the worker's latest evidence and classify the affected scope.
2. Hold only the mutations the current user-repair state makes impossible. Leave read-only work, unrelated actions, every Heartbeat, and every unaffected lane running. Identical technical error codes across lanes do not prove an account-wide blocker.
3. Deduplicate simultaneous reports about the same root cause into one user repair request.
4. Explain the issue in the main task only when a user repair or genuine decision is required:

```text
风险：<发生了什么，以及证据>。
可能原因：<基于错误码和范围探测的一个或两个可能原因，不写成定论>。
影响：<暂停了哪些动作；哪些仍在继续>。
当前处理：<已自动检查/重试了什么；已暂缓/撤回/保留的 exact action；Heartbeat 保持 active>。
建议：<最稳妥的下一步；必要时给一个可继续的替代方案>。
请确认：继续原方案 / 按建议调整 / 停止该范围。
```

5. Do not tell the user to open or reply in a worker task.
6. Verify that the current user-repair state cleared. Do not use a historical event as proof that it remains active.
7. Route the repair/decision back to the owner. The owner re-probes its lane and resumes the user's latest command without adding a recovery tier or asking for another confirmation.

The latest explicit user command controls authorized operations after a current blocker clears. Recommendations may be reported once but never replace the requested duration, intensity, count, or lane unless the user accepts the change.

## Scope Rules

- Candidate-specific issue: skip/retarget automatically; no escalation unless the user explicitly required that exact target.
- Subreddit-specific removal/rule/ban issue: retire that subreddit, send `SUBREDDIT_RETIRED`, and continue elsewhere. Multiple retired communities are still non-blocking. Escalate for a decision only when that exact subreddit was explicitly required and no substitute is acceptable, or Reddit separately shows account-wide evidence.
- Retryable lane-wide technical issue: keep that worker's Heartbeat active, mark `lane_recovering`, automatically retry, and do not ask the user; siblings continue.
- Lane issue requiring a concrete external repair: surface only that repair after the allowlisted persistence threshold; Heartbeats and siblings continue.
- Account-wide issue: only explicit current Reddit account-level UI may hold the mutations it prevents; never infer it from shared Chrome/network/client-block errors.
- Automation-only issue: preserve completed Reddit actions and every valid continuation. The coordinator repairs in place or verifies a corrected replacement before retiring the old timer, then re-audits binding/time. Never create a no-Heartbeat gap or alter sibling timers.

Routine progress remains pull-based. Risk escalation is exceptional and must not become per-item callback noise.
