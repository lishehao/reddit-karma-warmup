# Risk Escalation To Main Console

Load in the `Reddit 主控台` coordinator and every worker. The user makes risk decisions only in the coordinator task. Lane workers never ask the user directly.

## What Returns To Main

Escalate immediately when at least one is true:

- `decision_required`: a genuine soft-risk choice changes whether/how the action should continue
- `lane_blocked`: Chrome remains unavailable after recovery, the worker task/heartbeat cannot continue correctly, or the lane cannot meet its mission for a non-candidate-specific reason
- `account_blocked`: logout/wrong account, credential request, captcha, rate limit, lock/suspension, account-wide warning, or repeated cross-community removal state
- `execution_integrity_failed`: automation targets the wrong task, fires at a materially wrong time, repeats unexpectedly, runs after the stop time, or published evidence cannot be reconciled safely
- `material_reputation_risk`: an intended action appears technically possible but has clear moderation, deception, identity, or brand risk requiring a user choice

Do not escalate ordinary operations noise:

- one low-score/stale/saturated candidate
- one subreddit with unclear rules when another eligible target remains
- no actionable Notification
- no qualified vote after the read budget
- a recoverable Chrome route error that succeeds after recovery
- normal count shortfall because too few candidates passed

These remain in the worker report unless they become lane-wide or require a user decision.

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
affected_scope: <candidate|subreddit|lane|account>
current_state: <paused/stopped; completed actions preserved>
safe_options: <continue unchanged only if defensible | safer adjustment | stop>
user_action_needed: <exact decision or repair>
```

5. End the worker turn in `awaiting_coordinator_decision`. Do not ask the user, continue automatically, create a substitute task, or broaden the pause to siblings.

If the worker-to-coordinator message capability is unavailable, keep the affected scope paused and mark `risk_return_unavailable`. Unattended continuation for that lane is not allowed; the coordinator's next bounded pull must surface it.

## Coordinator Protocol

On `RISK_ESCALATION`:

1. Read the worker's latest evidence and classify the affected scope.
2. For an account-wide blocker, send a pause instruction to every mutation lane. For a lane/candidate blocker, leave unrelated lanes running.
3. Deduplicate simultaneous reports about the same root cause into one user decision.
4. Explain the issue in the main task only:

```text
风险：<发生了什么，以及证据>。
影响：<暂停了哪些动作；哪些仍在继续>。
当前处理：<已暂停/撤回/保留的内容和自动化状态>。
建议：<最稳妥的下一步；必要时给一个可继续的替代方案>。
请确认：继续原方案 / 按建议调整 / 停止该范围。
```

5. Do not tell the user to open or reply in a worker task.
6. Do not resume a hard-stop condition merely because the user says `继续`; first verify the required external repair, such as restored login or cleared captcha/rate-limit state.
7. Route the resolved decision back to the owner. The owner re-probes its lane, acts only within the approved scope, and returns new proof.

## Scope Rules

- Candidate-specific issue: skip/retarget automatically; no escalation unless the user explicitly required that exact target.
- Subreddit-specific removal/rule issue: pause that subreddit; escalate only when it changes the requested mission or signals repeated risk.
- Lane-wide issue: pause one worker and ask through the coordinator.
- Account-wide issue: coordinator pauses all mutation lanes and asks through the coordinator.
- Automation-only issue: preserve completed Reddit actions, pause the incorrect continuation, repair through the owning worker, then re-audit binding/time before resuming.

Routine progress remains pull-based. Risk escalation is exceptional and must not become per-item callback noise.
