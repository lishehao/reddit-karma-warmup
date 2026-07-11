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

## Error Classes

| Class | Typical evidence | Initial interpretation | Required behavior |
|-|-|-|-|
| `control_channel` | explicit browser disconnected/extension/native messaging error | Chrome control binding failed, not a Reddit/network verdict | Reconnect Chrome control; preserve the existing Chrome profile. |
| `stale_tab` | tab missing/closed/not in session, while browser binding remains connected | Only this tab binding is stale | Discard only the tab binding and open/reclaim a fresh lane tab from the existing Chrome binding. Do not reconnect the whole browser. |
| `dns_or_offline` | `ERR_NAME_NOT_RESOLVED`, `ERR_INTERNET_DISCONNECTED` | bad hostname, DNS, or device/network outage | Validate the URL, then run the scope probes below. |
| `transient_network` | `ERR_NETWORK_CHANGED`, `ERR_CONNECTION_TIMED_OUT`, `ERR_TIMED_OUT`, `ERR_CONNECTION_RESET`, `ERR_CONNECTION_CLOSED`, `ERR_EMPTY_RESPONSE` | unstable network, VPN/proxy transition, busy/down site, or middlebox | Bounded retry and scope probes; do not infer account enforcement. |
| `proxy_or_tls` | `ERR_PROXY_CONNECTION_FAILED`, `ERR_TUNNEL_CONNECTION_FAILED`, `ERR_CERT_*`, `ERR_SSL_*` | proxy/VPN/TLS path problem | Never bypass a certificate warning or change proxy/VPN settings. Probe scope, then escalate if persistent. |
| `site_or_http` | HTTP `500-599`, persistent `403`, `ERR_CONNECTION_REFUSED` | site/server/WAF/route issue; `403` is not automatically an account ban | Probe Reddit home and another route. Retry only when mutation state is safe. |
| `rate_or_account` | HTTP `429`, Reddit rate-limit/captcha/challenge/login/lock/warning UI | possible platform/account enforcement | Stop mutations immediately and return evidence through `risk-escalation.md`; do not use network retries to bypass it. |
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
2. If still failing and no hard-stop/account signal exists, update this lane's same logical Heartbeat timer for a recovery checkpoint `5-10 min` later. End the turn with the normal three-line report; `下轮计划` names the exact probe and withheld mutation.
3. `attempt 2` at the Heartbeat wake: rerun the scope probes once. If healthy, reconfirm account/context and resume from the last safe state. If still unhealthy, return `lane_blocked` or `account_blocked` to `Reddit 主控台` with the exact code, scope results, and mutation state.

Never create a second recovery automation. Reuse the lane's existing `operation_timer_id`. Never compress missed work after recovery.

## Mutation Integrity

- `before_input`: safe to reopen and redraft after recovery.
- `after_input_before_submit`: assume unsent; re-read context before using preserved/retyped copy.
- `submit_uncertain` or `after_submit_before_verify`: inspect the target thread, profile history, or Notifications first. If the exact action exists, record it; if state remains uncertain, stop that action and escalate. Never submit a second time.
- `read_only`: retry through the bounded state machine without changing account state.

## Recovery Result

Record internally:

```text
error_class + exact_code
scope = control | tab | all_network | proxy_tls | reddit_domain | reddit_route | account
attempts
mutation_state
recovery_action
account_reconfirmed
result = recovered | skipped_route | heartbeat_recheck | escalated
```

A recovered transient error stays local. A persistent lane/account blocker returns to `Reddit 主控台`. Ordinary Heartbeat output still uses only:

```text
本轮完成：<recovery/action result>
下一轮心跳：<exact local time/timezone and UTC, or none>
下轮计划：<exact recovery probe or resumed lane target>
```

## Primary References

- Google Chrome Help, common error messages: https://support.google.com/chrome/answer/95669
- Google Chrome Help, connection and loading recovery: https://support.google.com/chrome/answer/6098869
