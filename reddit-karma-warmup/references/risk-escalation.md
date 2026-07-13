# Lane-Local Risk And Recovery

Load inside every lane task. Risks, repairs, and user communication stay in the affected task. There is no callback or central risk surface.

## Default: Continue Locally

Automatically recover or retarget for:

- Chrome disconnect, stale tab, blank/loading page, selector drift;
- DNS/network/proxy/TLS error, HTTP `5xx`, `ERR_BLOCKED_BY_CLIENT`;
- one rejected candidate, one restrictive subreddit, empty candidate set;
- timed rate limit with a visible expiry;
- pending-review own post cleanup and subreddit retirement;
- missing delayed visibility after immediate submit proof;
- uncertain exact mutation, which is never repeated but does not stop other safe work in this lane;
- this task's stale/malformed timer or one failed wake.

Keep this task's Heartbeat active, withhold only the exact impossible/uncertain action, and retry or retarget on later wakes. Do not ask for permission to continue.

## Direct User Repair In This Task

Ask the user here only when a currently visible state requires their action:

- logged out or account identity cannot be established after bounded recovery;
- password, credential, or manual login is required;
- persistent CAPTCHA/challenge;
- account lock/suspension or required acknowledgement with no automatic path;
- the user required one exact prohibited/unsafe target and no substitute is authorized.

Use:

```text
需要你处理：<one exact repair>。
影响：仅暂停当前 <lane> 中受影响的动作；本任务 Heartbeat 保持运行以便复查。
完成后在本任务回复“继续”。
```

Never send this to `Reddit 分发台` and never inspect sibling state.

## Subreddit Retirement

If an own post is awaiting moderator approval, delete/withdraw it immediately without confirmation. If a post/comment is removed or a live rule prohibits the action, retire that subreddit for this account's relevant lane, record the permalink/reason, and retarget. Inform the user once in this task; do not stop the lane or other tasks.

An explicit permanent subreddit ban is a separate event. Load `permanent-ban-issue-reporting.md`, retire the community immediately, and attempt the deduplicated sanitized GitHub Issue without another confirmation. The report attempt and any retry stay lane-local and never pause other eligible work.

Historical removals, rate limits, warnings, or locks are context only. They do not prove a current blocker.

## Lane Isolation

- One lane's failure never changes another lane's mission, cadence, timer, task, tab, or target pool.
- Similar error codes in several tasks do not authorize cross-task coordination.
- The affected task does not look for or message siblings.
- User stop applies only to the addressed task unless the user independently stops others.
