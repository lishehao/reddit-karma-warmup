# Single-owner Risk Escalation

Load this only after the active unit encounters a concrete issue. Keep all
state in the one mission record; do not create, message, or inspect another
Reddit task.

## Classify and contain

| Evidence | Required result |
| --- | --- |
| candidate/rule/content mismatch | mark the candidate ineligible and continue the active unit |
| stale tab | discard only the tab binding; retain the Chrome binding and mission |
| content/route/network failure | run the bounded classifier in `chrome-network-recovery.md`; otherwise `YIELD` the active unit |
| explicit HTTP 429 | stop all Reddit work for this wake; preserve the queue and resume the active unit on the mission Heartbeat |
| uncertain submit/click | persist `MUTATION_UNKNOWN`, freeze the exact action key forever, and never retry it |
| login challenge, CAPTCHA, suspension, password/OTP requirement | stop affected browser work and ask the user for one precise repair |

A yielded unit is not a new round. It retains its cursor, budget, and frozen
keys, and resumes before later units. The user may safely pause or remove it at
a safe boundary; do not reset its evidence or use another unit to probe an
uncertain action.

## User repair message

```text
需要你处理：<one exact repair>。
影响：仅暂停当前 <unit>；任务队列与 Heartbeat 保留。
完成后在同一 Reddit 运营台回复“继续”。
```

Historical warnings, past removals, and an absent UI banner are not current
account-risk proof.

