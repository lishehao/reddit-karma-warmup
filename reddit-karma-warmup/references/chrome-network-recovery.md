# Chrome Loading And Network Recovery

Load this reference only when Chrome control, navigation, or page loading fails. It applies to every lane. The goal is to recover the existing logged-in Chrome session without duplicating an outward action or misclassifying a network fault as Reddit enforcement.

Always follow the installed Chrome control Skill. For extension/native-messaging/discovery failures, load its Chrome/bootstrap troubleshooting documentation before resetting any runtime or claiming Chrome is unavailable.

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
| `rate_or_account` | current HTTP `429`, Reddit rate-limit/captcha/challenge/login/lock/warning UI | possible platform/account enforcement | Pause impossible mutations. For a displayed timed limit, preserve the mission and re-probe automatically at expiry; escalate only a state that needs user repair. Do not use network retries to bypass it. |
| `client_block` | `ERR_BLOCKED_BY_CLIENT` | route blocked by client/extension/filter; not proof of Reddit restriction | Reconnect only if control also dropped; otherwise use a clean lane tab and native Reddit entry route. Skip one persistently blocked deep route. |
| `form_replay` | `ERR_CACHE_MISS`, resubmit warning, submit result unknown | replay could duplicate an action | Never reload/resubmit blindly. Inspect target thread/profile/history first. |
| `page_runtime` | `Aw, Snap!`, blank/white page, endless loading, script/selector failure without network code | renderer, memory, page script, stale DOM, or unknown loading fault | One reload, then one fresh lane tab; scope before classifying. |

Chrome documents common loading codes and exposes the installed browser's full list at `chrome://network-errors/`. Treat the code as evidence about the failing layer, not as proof of root cause.

## Scope Probes

Use Chrome Browser only. Never switch to Computer Use, another browser, Web Search, or a logged-out session as a recovery substitute.

1. Validate the exact URL/hostname.
2. If the browser binding is connected, wait `5-15 sec` and retry the current read-only navigation once. Do not repeat a mutation.
3. In a fresh lane-owned tab, open the relevant Reddit native home surface (`reddit.com`, subreddit home, Notifications, or profile history).
4. If Reddit still fails, open one neutral public page such as `https://example.com/` in that same Chrome session.
5. Classify the scope:
   - neutral page and Reddit both fail: device/network/proxy/Chrome path
   - neutral page works, Reddit home fails: Reddit/site/domain path
   - Reddit home works, deep target fails: route/candidate path
   - browser calls fail before any page response: control-channel path
6. After recovery, reconfirm the expected Reddit account and target URL before any mutation.

Do not inspect cookies/local storage, clear browsing data, disable extensions, restart Chrome, change DNS/VPN/proxy, or bypass TLS warnings automatically. Those actions can destroy login state or alter the user's machine and require user involvement when genuinely needed.

## Bounded Recovery State Machine

`attempt 0` is the original failure.

1. `attempt 1`: preserve mutation state, apply the class-specific immediate recovery, then probe current domain plus scope.
2. If still failing and no hard-stop/account signal exists, keep this lane's recurring Heartbeat active and request a recovery checkpoint `5-10 min` later. End the turn with the normal three-line report; `下轮计划` names the exact probe and withheld mutation. Do not pause or edit sibling lanes.
3. `attempt 2` at the Heartbeat wake: rerun the scope probes once. If healthy, reconfirm account/context and resume from the last safe state. If still unhealthy but the class remains technical/retryable, record `lane_recovering`, choose another native route/safe candidate when possible, and re-probe on a later varied wake until recovery or mission deadline. Return `lane_blocked` only when a concrete external user repair is required; return `account_blocked` only for explicit current Reddit account-level UI.

Do not ask the user before or between retryable technical attempts. A known timed rate limit does not require approval. The worker never creates a recovery automation; it returns the proposed recovery time and relies on the existing coordinator-managed recurring Heartbeat. Never compress missed work after recovery. A pending-review cleanup remains queued and automatically retried; it never becomes a user decision.

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
result = recovered | skipped_route | heartbeat_recheck | lane_recovering | escalated
```

A recovered transient error stays local and the worker continues. Its next normal three-line report briefly names the exact code, likely cause, and successful automatic recovery in `本轮完成`; do not create a separate alert. A persistent retryable lane fault stays `lane_recovering` with its Heartbeat active and does not return a user decision. Only an external-repair requirement or explicit account-level blocker returns to `Reddit 主控台`. Ordinary Heartbeat output still uses only:

```text
本轮完成：<exact code；可能原因；已自动重试/恢复结果；action result>
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
