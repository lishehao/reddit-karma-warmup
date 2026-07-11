# Risk Escalation To Main Console

Load in the `Reddit 主控台` coordinator and every worker. The user makes risk decisions only in the coordinator task. Lane workers never ask the user directly.

## What Returns To Main

Escalate immediately when at least one is true:

- `decision_required`: a genuine soft-risk choice changes whether/how the action should continue
- `lane_blocked`: Chrome remains unavailable after recovery, the worker task/heartbeat cannot continue correctly, or the lane cannot meet its mission for a non-candidate-specific reason
- `account_blocked`: a currently visible logout/wrong account, credential request, captcha, sitewide rate limit, lock/suspension, or explicit account-wide warning prevents the action now
- `execution_integrity_failed`: automation targets the wrong task, fires at a materially wrong time, repeats unexpectedly, runs after the stop time, or published evidence cannot be reconciled safely
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

These remain in the worker report unless bounded recovery fails, they become lane-wide/account-wide, or they require a user decision.

## Non-Blocking Subreddit Retirement Notice

A removal/filter/lock/subreddit ban, invalidating parent deletion, or pending-approval withdrawal retires only that exact subreddit. It is not `RISK_ESCALATION` without separate account-level evidence.

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

1. Stop new actions in the affected scope. Keep unrelated lanes outside this worker's control.
2. Preserve exact evidence: URL/surface, time local+UTC, Reddit/browser message, submit state, automation ID/target when relevant, and actions already completed.
3. Cancel or pause only this worker's next trigger when continuing it could worsen the risk. Do not alter sibling automations.
4. Send one message to the exact `coordinator_thread_id`:

```text
RISK_ESCALATION
mission_id: <id>
lane: <comments|posts|follow-up|browsing>
severity: <decision_required|lane_blocked|account_blocked|execution_integrity_failed|material_reputation_risk>
evidence: <one concise factual paragraph>
likely_cause: <one or two evidence-based possibilities, explicitly marked as possible>
recovery_attempts: <what was retried and the observed result>
affected_scope: <candidate|subreddit|lane|account>
current_state: <paused/stopped; completed actions preserved>
safe_options: <continue unchanged only if defensible | safer adjustment | stop>
user_action_needed: <exact decision or repair>
```

5. End the worker turn in `awaiting_coordinator_decision` only when user action or a genuine choice is required. A visible timed rate limit with a known expiry is automatic recovery: preserve the mission, reuse this lane's timer for the expiry when needed, re-probe, and continue without requesting a decision. Do not ask the user, create a substitute task, or broaden the pause to siblings.

If the worker-to-coordinator message capability is unavailable, keep the affected scope paused and mark `risk_return_unavailable`. Unattended continuation for that lane is not allowed; the coordinator's next bounded pull must surface it.

## Coordinator Protocol

On `RISK_ESCALATION`:

1. Read the worker's latest evidence and classify the affected scope.
2. For an account-wide blocker, send a pause instruction to every mutation lane. For a lane/candidate blocker, leave unrelated lanes running.
3. Deduplicate simultaneous reports about the same root cause into one user decision.
4. Explain the issue in the main task only when a user repair or genuine decision is required:

```text
风险：<发生了什么，以及证据>。
可能原因：<基于错误码和范围探测的一个或两个可能原因，不写成定论>。
影响：<暂停了哪些动作；哪些仍在继续>。
当前处理：<已自动检查/重试了什么；已暂停/撤回/保留的内容和自动化状态>。
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
- Lane-wide issue: pause one worker and ask through the coordinator.
- Account-wide issue: coordinator pauses all mutation lanes and asks through the coordinator.
- Automation-only issue: preserve completed Reddit actions, pause the incorrect continuation, repair through the owning worker, then re-audit binding/time before resuming.

Routine progress remains pull-based. Risk escalation is exceptional and must not become per-item callback noise.
