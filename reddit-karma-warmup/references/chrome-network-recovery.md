# Chrome Loading And Network Recovery

Load this reference only when Chrome control, navigation, or page loading fails. It applies to every lane. The goal is to recover the existing logged-in Chrome session without duplicating an outward action or misclassifying a network fault as Reddit enforcement.

Always follow the installed Chrome control Skill. For extension/native-messaging/discovery failures, load its Chrome/bootstrap troubleshooting documentation before resetting any runtime or claiming Chrome is unavailable.

## Navigation And Tab Ownership

- Use `tab.goto(url)` for a known destination and a DOM-supported link click plus navigation wait for an in-page transition. Page-side evaluation is read-only and is not a navigation fallback.
- `CUA` keypress/type acts on the focused webpage, not reliably on the Chrome omnibox. Never use `Meta+L` address-bar simulation as recovery.
- `openTabs()` returning a Reddit URL/title proves only tab metadata visibility. After claiming the exact recorded lane tab, require one successful DOM, screenshot, or equivalent page-state read before declaring control healthy.
- Each lane keeps one persistent dedicated Reddit primary tab. Persist `own_tab_id` immediately after creation and before the first `goto`; never recover by claiming an arbitrary existing Reddit tab. A nonterminal turn preserves its controllable primary tab as `handoff`; terminal cleanup closes/releases it.
- Give awaited `tab.goto(...)` up to `90 sec`. A timeout or REPL reset makes the navigation acknowledgement uncertain because the page transition may already have completed. Reconnect the same Chrome/profile, reclaim the exact `own_tab_id`, and run a post-timeout page-state check using URL/title plus DOM or screenshot before classifying failure.
- Only when that same-tab check and one bounded same-tab retry still show `about:blank` or an unreadable page may the lane classify a page-control/control-channel failure. Never call `finalize({keep: []})` for this nonterminal condition, never create replacement tabs in a loop, and never claim a user/launcher/sibling tab. Keep the lane mission, Heartbeat, and primary tab as `handoff` for the next wake.

## Evidence First

Immediately stop the current click/type sequence and record:

```text
time_local + UTC
lane + mission_id
URL + tab_id
exact browser/tool error code or visible message
phase = before_input | after_input_before_submit | submit_uncertain | after_submit_before_verify | read_only
last_verified_state
```

Read the exact returned error or visible Chrome error page. A blank page, spinner, missing selector, or timeout is `unknown_loading_failure` until scoped; do not invent a Chrome code.

Derive a `likely_cause` from the exact code plus scope probes. Always present it as a possibility, never a proven root cause:

| Evidence | User-safe likely-cause wording |
|-|-|
| `ERR_NETWORK_CHANGED` | 网络或代理连接可能刚刚发生切换 |
| `ERR_CONNECTION_RESET/CLOSED` | 网络、VPN/代理或安全软件可能中断了连接 |
| `ERR_CONNECTION_TIMED_OUT`, `ERR_TIMED_OUT`, `ERR_EMPTY_RESPONSE` | 当前网络较慢，或目标站点暂时繁忙/无响应 |
| `ERR_NAME_NOT_RESOLVED` | URL 可能有误，或 DNS 暂时无法解析域名 |
| `ERR_INTERNET_DISCONNECTED` | 设备当前可能没有可用网络连接 |
| `ERR_PROXY_CONNECTION_FAILED`, `ERR_TUNNEL_CONNECTION_FAILED` | 代理连接或代理隧道可能不可用 |
| `ERR_CERT_*`, `ERR_SSL_*` | TLS 证书、系统时间或代理 HTTPS 路径可能异常 |
| HTTP `500-599` | Reddit 服务或该路由可能暂时异常 |
| persistent HTTP `403` | 该路由可能被 WAF、权限或登录状态阻止；尚不能判断为账号处罚 |
| `ERR_BLOCKED_BY_CLIENT` | 浏览器扩展、内容过滤或客户端规则可能阻止了该请求 |
| blank/spinner/`Aw, Snap!` | 页面脚本、渲染资源、内存或网络加载可能异常 |

When several causes remain possible, give at most the two strongest based on the probes. Use wording such as `可能原因：...`; do not blame the user's network, proxy, Reddit, or account without evidence.

## Error Classes

| Class | Typical evidence | Initial interpretation | Required behavior |
|-|-|-|-|
| `control_channel` | explicit browser disconnected/extension/native messaging error | Chrome control binding failed, not a Reddit/network verdict | Reconnect Chrome control; preserve the existing Chrome profile. |
| `stale_tab` | tab missing/closed/not in session, while browser binding remains connected | Only this tab binding is stale | Discard only the tab binding and open/reclaim a fresh lane tab from the existing Chrome binding. Do not reconnect the whole browser. |
| `dns_or_offline` | `ERR_NAME_NOT_RESOLVED`, `ERR_INTERNET_DISCONNECTED` | bad hostname, DNS, or device/network outage | Validate the URL, then run the scope probes below. |
| `transient_network` | `ERR_NETWORK_CHANGED`, `ERR_CONNECTION_TIMED_OUT`, `ERR_TIMED_OUT`, `ERR_CONNECTION_RESET`, `ERR_CONNECTION_CLOSED`, `ERR_EMPTY_RESPONSE` | unstable network, VPN/proxy transition, busy/down site, or middlebox | Bounded retry and scope probes; do not infer account enforcement. |
| `proxy_or_tls` | `ERR_PROXY_CONNECTION_FAILED`, `ERR_TUNNEL_CONNECTION_FAILED`, `ERR_CERT_*`, `ERR_SSL_*` | proxy/VPN/TLS path problem | Never bypass a certificate warning or change proxy/VPN settings. Probe scope, then escalate if persistent. |
| `site_or_http` | HTTP `500-599`, persistent `403`, `ERR_CONNECTION_REFUSED` | site/server/WAF/route issue; `403` is not automatically an account ban | Probe Reddit home and another route. Retry only when mutation state is safe. |
| `rate_or_account` | current HTTP `429`, Reddit `Too Many Requests`, or rate-limit/captcha/challenge/login/lock/warning UI | possible platform/account enforcement | An explicit `429` enters `429_ROUND_PAUSE` below. Other displayed timed limits preserve the mission and re-probe automatically at expiry; escalate only a state that needs user repair. Do not use network retries to bypass either state. |
| `client_block` | `ERR_BLOCKED_BY_CLIENT` | route blocked by client/extension/filter; not proof of Reddit restriction | Reconnect only if control also dropped; otherwise use a clean lane tab and native Reddit entry route. Skip one persistently blocked deep route. |
| `form_replay` | `ERR_CACHE_MISS`, resubmit warning, submit result unknown | replay could duplicate an action | Never reload/resubmit blindly. Inspect target thread/profile/history first. |
| `page_runtime` | `Aw, Snap!`, blank/white page, endless loading, script/selector failure without network code | renderer, memory, page script, stale DOM, or unknown loading fault | One reload, then one fresh lane tab; scope before classifying. |

Chrome documents common loading codes and exposes the installed browser's full list at `chrome://network-errors/`. Treat the code as evidence about the failing layer, not as proof of root cause.

## Scope Probes

Use Chrome Browser only. Never switch to Computer Use, another browser, Web Search, or a logged-out session as a recovery substitute.

1. Validate the exact URL/hostname.
2. If awaited navigation times out, first reconnect the same Chrome/profile, reclaim the exact recorded `own_tab_id`, and inspect actual post-timeout page state. If URL moved and DOM/screenshot is readable, continue as recovered without another navigation.
3. If the same tab remains blank or unreadable, wait `5-15 sec` and retry the current read-only navigation once in that tab. Do not repeat a mutation and do not create a second primary tab.
4. In the lane's dedicated primary tab, open the relevant Reddit native home surface (`reddit.com`, subreddit home, Notifications, or profile history). Only if the recorded tab is absent from the current tab inventory is its binding stale and replaceable once.
5. If Reddit still fails, open one neutral public page such as `https://example.com/` in that same Chrome session.
6. Classify the scope:
   - neutral page and Reddit both fail: device/network/proxy/Chrome path
   - neutral page works, Reddit home fails: Reddit/site/domain path
   - Reddit home works, deep target fails: route/candidate path
   - browser calls fail before any page response, or a new tab stays `about:blank` for both Reddit and the neutral page: page-control/control-channel path
7. After recovery, reconfirm the expected Reddit account and target URL before any mutation.

Do not inspect cookies/local storage, clear browsing data, disable extensions, restart Chrome, change DNS/VPN/proxy, or bypass TLS warnings automatically. Those actions can destroy login state or alter the user's machine and require user involvement when genuinely needed.

## Bounded Recovery State Machine

### Explicit 429 Round Pause

When the current Chrome surface or response explicitly shows HTTP `429`, `Too Many Requests`, or an equivalent server rate-limit response:

1. Record the exact code/message, URL, local/UTC time, lane, mission ID, remaining target, and any exposed `Retry-After` or expiry.
2. End the current wake immediately. Perform no more Reddit navigation, reload, comment, reply, post, vote, Join, profile edit, or submit attempt in this round.
3. Preserve the mission, remaining target, draft state, and the lane's existing Heartbeat. Never delete, deactivate, or mark the mission complete.
4. Set `next_due` to the later of this lane's next normal round and any explicit `Retry-After`/displayed expiry. If no normal next round exists, use `30m` as the one-round fallback.
5. On that wake, probe one read-only Reddit surface once. If healthy, reconfirm account/context and resume normally without catch-up. If `429` remains, repeat one round pause.

`429_ROUND_PAUSE` is lane-local because tasks do not share runtime state. Another lane pauses only if it independently receives the same explicit response. Do not create cross-task locks, callbacks, or pause messages.

`attempt 0` is the original failure.

1. `attempt 1`: preserve mutation state, apply the class-specific immediate recovery, then probe current domain plus scope. Explicit `429` bypasses this same-wake retry and uses `429_ROUND_PAUSE`.
2. If still failing and no user-repair state exists, keep this lane's recurring Heartbeat active and request a recovery checkpoint `5-10 min` later. End the turn with the normal three-line report; `下轮计划` names the exact probe and withheld mutation. Do not pause or edit sibling lanes.
3. `attempt 2` at the Heartbeat wake: rerun the scope probes once. If healthy, reconfirm account/context and resume from the last safe state. If still technical/retryable, record `lane_recovering`, choose another native route/safe candidate when possible, and re-probe on later wakes until recovery or mission deadline. Chrome-control failure becomes user-repair eligible only after three consecutive recovery wakes; ordinary network/route/client-block failure never does by itself.

Do not ask the user before or between retryable technical attempts. A known timed rate limit does not require approval. The worker relies on its own recurring Heartbeat for later recovery and may update that timer when the recovery time changes. For explicit `429`, do not retry, probe, or continue Reddit work again in the same wake. Never compress missed work after recovery. A pending-review cleanup remains queued and automatically retried; it never becomes a user decision.

Never delete, deactivate, or pause this lane's Heartbeat because a Chrome, network, page, route, client-block, or recovery attempt failed. Multiple unsuccessful recovery wakes remain `lane_recovering` and continue on the existing timer until the deadline, explicit user stop, terminal proof, or verified timer replacement. An explicit account blocker may withhold the mutations it prevents, but this task's Heartbeat stays active for timed re-probe unless the user stops the operation. `submit_uncertain` withholds only that exact mutation; it does not stop other safe work in this task.

## Mutation Integrity

- `before_input`: safe to reopen and redraft after recovery.
- `after_input_before_submit`: assume unsent; re-read context before using preserved/retyped copy.
- `submit_uncertain` or `after_submit_before_verify`: inspect the target thread, profile history, or Notifications first. If the exact action exists, record it; if state remains uncertain, stop that action and escalate. Never submit a second time.
- `read_only`: retry through the bounded state machine without changing account state.

## Recovery Result

Record internally:

```text
error_class + exact_code
likely_cause + cause_confidence = low | medium | high
scope = control | tab | all_network | proxy_tls | reddit_domain | reddit_route | account
attempts
mutation_state
recovery_action
account_reconfirmed
result = recovered | skipped_route | heartbeat_recheck | round_paused_429 | lane_recovering | escalated
```

A recovered transient error stays local and the worker continues. Its next normal three-line report briefly names the exact code, likely cause, and successful automatic recovery in `本轮完成`; do not create a separate alert. Explicit `429` reports `round_paused_429`, the verified next-round time, and no same-wake retry. A persistent retryable lane fault stays `lane_recovering` with its Heartbeat active and does not request a user decision. Only an allowlisted hard user-repair state is shown directly to the user in this task. Ordinary Heartbeat output still uses only:

```text
本轮完成：<exact code；可能原因；已自动重试/恢复结果，或 429 已暂停本轮；action result>
下一轮心跳：<exact local time/timezone and UTC, or none>
下轮计划：<exact recovery probe or resumed lane target>
```

Example while recovery is pending:

```text
本轮完成：页面加载失败（ERR_NETWORK_CHANGED）；可能原因是网络或代理刚刚切换；已自动重试 1 次，未重复提交。
下一轮心跳：2026-07-12 01:18:00 Asia/Shanghai（2026-07-11 17:18:00 UTC）
下轮计划：复查 Reddit 首页与中性页面；恢复后确认账号并继续当前评论候选。
```

## Primary References

- Google Chrome Help, common error messages: https://support.google.com/chrome/answer/95669
- Google Chrome Help, connection and loading recovery: https://support.google.com/chrome/answer/6098869
