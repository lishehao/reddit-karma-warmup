# Risk Escalation To Main Console

Load in the `Reddit 主控台` coordinator and every worker. The user makes risk decisions only in the coordinator task. Lane workers never ask the user directly.

## What Returns To Main

Escalate immediately when at least one is true:

- `decision_required`: a genuine soft-risk choice changes whether/how the action should continue
- `lane_blocked`: a concrete external repair is required after automatic recovery, or the worker task/Heartbeat cannot technically continue; ordinary retryable route/network/client-block failures are `lane_recovering`, not escalation
- `account_blocked`: a currently visible logout/wrong account, credential request, captcha, sitewide rate limit, lock/suspension, or explicit account-wide warning prevents the action now
- `execution_integrity_failed`: automation targets the wrong task, fires at a materially wrong time, has recurrence inconsistent with the mission, runs after the stop time, or published evidence cannot be reconciled safely
- `scheduler_continuation_failed`: a promised multi-slot mission has no valid recurring Heartbeat, a timer is `COUNT=1`/repeat-off/misbound, or no worker wake/slot proof appears after one bounded coordinator repair
- `material_reputation_risk`: an intended action appears technically possible but has clear moderation, deception, identity, or brand risk requiring a user choice

Do not escalate ordinary operations noise:

- one low-score/stale/saturated candidate
- one subreddit with unclear rules when another eligible target remains
- no actionable Notification
- no qualified vote after the read budget
- a recoverable Chrome route error that succeeds after recovery
- a transient DNS/network/proxy/site loading error while its bounded `chrome-network-recovery.md` checkpoint is still pending
- normal count shortfall because too few candidates passed
- any historical or already-cleared removal, warning, rate limit, lock, or login fault
- a `STALE_OWNER_TOMBSTONE` that the coordinator atomically replaces with verified mission delivery and a correctly bound new Heartbeat
- pending-review cleanup, including automatic deletion/withdrawal and retry of an exact cleanup permalink
- a retryable lane-local Chrome/control/network/client-block/route failure while the lane Heartbeat remains active

These remain in the worker report unless bounded recovery fails, they become lane-wide/account-wide, or they require a user decision.

Missing-rollout evidence is an orchestration condition, never Reddit account risk. Do not ask the user to approve a successful owner replacement. If one bounded replacement cannot accept the mission or receive a valid continuation, classify `execution_integrity_failed`, pause only that lane, and return the exact old/new task evidence to `Reddit 主控台`.

`SCHEDULER_CONTINUATION_FAILURE` is orchestration state, never Reddit account risk. The coordinator preserves completed actions, reports exact planned/started/completed/blocked/missed counts, and marks the mission `degraded` or `partial_completed`; it does not change account tier or subreddit eligibility.

## Non-Blocking Subreddit Retirement Notice

A removal/filter/lock/subreddit ban, invalidating parent deletion, or pending-approval withdrawal retires only that exact subreddit. It is not `RISK_ESCALATION` without separate account-level evidence.

Pending approval is never `decision_required`. Delete/withdraw the own post immediately, verify once, retire the subreddit, and continue. If cleanup is temporarily unreachable, queue the exact permalink for automatic lane-local retry; do not ask the user or pause any lane.

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

When escalation is required:

1. Stop only the currently impossible exact action. Keep the lane Heartbeat active for recovery, continue other safe work in this lane, and keep unrelated lanes outside this worker's control.
2. Preserve exact evidence: URL/surface, time local+UTC, Reddit/browser message, submit state, automation ID/target when relevant, and actions already completed.
3. Report retry state and the next planned re-probe. The recurring Heartbeat stays active unless the user stopped the scope, the deadline arrived, the lane became terminal, or the coordinator verified a corrected replacement. Do not inspect or alter sibling automations.
4. Send one message to the exact `coordinator_thread_id`:

```text
RISK_ESCALATION
mission_id: <id>
lane: <comments|posts|follow-up|browsing|presence>
severity: <decision_required|lane_blocked|account_blocked|execution_integrity_failed|scheduler_continuation_failed|material_reputation_risk>
evidence: <one concise factual paragraph>
likely_cause: <one or two evidence-based possibilities, explicitly marked as possible>
recovery_attempts: <what was retried and the observed result>
affected_scope: <candidate|subreddit|lane|account>
current_state: <exact_action_withheld | lane_recovering | terminal; completed actions preserved>
safe_options: <continue unchanged only if defensible | safer adjustment | stop>
user_action_needed: <exact decision or repair>
```

5. End the worker turn in `awaiting_coordinator_decision` only when user action or a genuine choice is required. A visible timed rate limit with a known expiry is automatic recovery: preserve the mission, return the expiry to the coordinator scheduler, and continue on a later recurring wake without requesting a decision. Do not ask the user, create a substitute task, or broaden the pause to siblings.

If the worker-to-coordinator message capability is unavailable, withhold only the exact action requiring a decision and mark `risk_return_unavailable`. Keep its recurring Heartbeat active; the coordinator's next supervisor pull must surface it before that exact action resumes. Unrelated work remains active.

## Coordinator Protocol

On `RISK_ESCALATION`:

1. Read the worker's latest evidence and classify the affected scope.
2. For explicit current Reddit account-wide UI, pause only the mutations that UI makes impossible. For a lane/candidate/route blocker, leave every unrelated lane and Heartbeat running. Identical technical error codes across lanes do not prove an account-wide blocker.
3. Deduplicate simultaneous reports about the same root cause into one user decision.
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
6. Verify that the current blocking state cleared. Do not use a historical event as proof that it remains active.
7. Route the repair/decision back to the owner. The owner re-probes its lane and resumes the user's latest command without adding a recovery tier or asking for another confirmation.

The latest explicit user command controls authorized operations after a current blocker clears. Recommendations may be reported once but never replace the requested duration, intensity, count, or lane unless the user accepts the change.

## Scope Rules

- Candidate-specific issue: skip/retarget automatically; no escalation unless the user explicitly required that exact target.
- Subreddit-specific removal/rule/ban issue: retire that subreddit, send `SUBREDDIT_RETIRED`, and continue elsewhere. Multiple retired communities are still non-blocking. Escalate for a decision only when that exact subreddit was explicitly required and no substitute is acceptable, or Reddit separately shows account-wide evidence.
- Retryable lane-wide technical issue: keep that worker's Heartbeat active, mark `lane_recovering`, automatically retry, and do not ask the user; siblings continue.
- Lane issue requiring a concrete external repair: surface only that repair through the coordinator; siblings continue.
- Account-wide issue: only explicit current Reddit account-level UI may pause the mutations it prevents; never infer it from shared Chrome/network/client-block errors.
- Automation-only issue: preserve completed Reddit actions and every valid continuation. The coordinator repairs in place or verifies a corrected replacement before retiring the old timer, then re-audits binding/time. Never create a no-Heartbeat gap or alter sibling timers.

Routine progress remains pull-based. Risk escalation is exceptional and must not become per-item callback noise.
