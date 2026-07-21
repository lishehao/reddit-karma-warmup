# Chrome Recovery Edge Cases

Load this matrix only after `chrome-network-recovery.md` classifies a failure. It extends that state machine; it does not replace the installed Chrome control Skill or authorize another browser.

## Binding And Runtime

| Edge case | Evidence boundary | Required response |
|-|-|-|
| Chrome tool is temporarily unavailable | tool is absent or returns an explicit extension/native-messaging/control error | Record `control_channel`; retry discovery within the wake budget, then continue through the lane Heartbeat. Do not switch to Computer Use, Browser, Playwright, or Web Search. |
| Browser binding is explicitly disconnected | exact disconnected/extension communication result | Reconnect the same Chrome/profile, enumerate tabs, then reclaim the recorded lane tab. Reconfirm the Reddit account before mutation. |
| `openTabs()` returns an empty list | no explicit disconnected result | Treat as unknown inventory, not proof that Chrome is disconnected. Retry inventory once; do not invalidate the browser binding. |
| Recorded lane tab was manually closed | browser binding healthy and exact `own_tab_id` absent after bounded inventory retry | Mark only `stale_tab`; create one replacement lane tab from the same binding and persist the new ID. |
| Chrome restarted and tab IDs changed | explicit reconnect succeeds but recorded tab is absent | Treat as one stale-tab replacement after reconnect. Never search for a visually similar user tab. |
| Lane tab was navigated elsewhere | exact tab exists but URL no longer matches the mission | If no mutation is uncertain, navigate that same lane tab back through a native URL. If a mutation is uncertain, inspect history/target first and quarantine the action. |
| DOM handle or selector became stale | tab URL is correct and page readable, but prior node/action handle fails | Re-read the current DOM and re-resolve the control once. Do not reload the page or consume a network retry. |
| Action changes accessible name or control identity | the action returned success; old locator fails; fresh evidence shows the same control under changed text/name/state | Record `locator_identity_changed`, resolve fresh control evidence once, and read the live property through the current focused/shadow control. Do not classify page-control failure. |
| Locator action hits an internal selector/CDP deadline but visible DOM and bounded page projection work | locator alone fails around its backend deadline; tab claim, `get_visible_dom()`, or page projection still acknowledges | Record `locator_backend_deadline`; do not retry the locator, reload, reconnect, or change models. Resolve a fresh DOM CUA string node for that control and continue once. |
| Browser call times out before a page response | no exact page code and call acknowledgement unknown | Record `unknown_loading_failure`; inspect actual tab state before issuing another navigation. |
| Atomic command returns after 20-60 seconds | full configured outer timeout was available and the requested command returned success | Record `slow_success` and continue. Do not reconnect, reload, replace the tab, or classify page/account failure. |
| `Statsig` or `ab.chatgpt.com` timeout appears but the Chrome command succeeds | optional browser-client ambient telemetry failed while the requested page command returned | Record `ambient_network_degraded`; ignore it for Reddit/account/rate-limit decisions. Continue with one blocking page/action command per cell; the bounded pure-metadata exception remains available. |
| Tab inventory works but exact-tab metadata times out | inventory or `tabs.new()` succeeds, while exact-object claim or URL/title returns no acknowledgement | Classify `page_control_partial`, not disconnected/network/account failure. Preserve the browser binding and exact recorded tab ID; after one bounded reconciliation attempt, make no more identical metadata calls in this wake and continue on the verified Heartbeat. A navigation timeout alone never enters this class. |
| Metadata is healthy but content surfaces time out | `openTabs()`/exact-object `claimTab()` and URL/title work, while DOM, screenshot, evaluate, or read-only projection times out after the full outer budget | Classify `chrome_content_channel_timeout`, not Chrome disconnected, target tab missing, Reddit login failure, or account risk. When no draft/mutation/uncertain submit exists, use at most one disposable neutral HTTPS content probe; then end content reads for the wake and preserve both bindings. Do not recommend extension reinstall/enable from this evidence. |
| Launcher cannot create/group a new tab | `tabs.new()` returns a window/grouping limitation before navigation | Prefer only an already-open Reddit tab from the current `openTabs()` result whose exact ID is not recorded as owned by another launcher or execution lane. If no provably unowned Reddit tab exists, ask the user to open Reddit; never navigate, close, inspect, or repurpose an unrelated user/launcher/sibling tab as fallback. This is not a Chrome disconnect. |
| Execution lane cannot create/group its primary tab | the lane's first `tabs.new()` returns a window/grouping limitation and no lane-owned `own_tab_id` exists | Record `tab_creation_unavailable`, preserve mission/checkpoint, and retry only within the configured tab/recovery budget through the lane's own Heartbeat. Never claim an unrelated user, launcher, or sibling tab. If the condition becomes an eligible persistent control repair, ask for one user action; do not fabricate tab ownership. |
| Pure metadata needs one compact transaction | only `openTabs`, exact-object `claimTab`, `url`, and `title` are needed | Bundle no more than `metadata_commands_per_cell` under `metadata_timeout_ms`. DOM, screenshot, evaluate, navigation, CUA, mutation, or finalization cancels this exception and must run alone with the applicable page/action budget. |
| Nonterminal tab handoff/finalize acknowledgement is unknown | finalization call timed out or returned no proof | Keep the recorded `own_tab_id` and mark disposition uncertain. On the next wake, enumerate and reclaim that exact ID before considering replacement; never create a second primary tab merely because handoff proof is missing. |

## Navigation And Rendering

| Edge case | Evidence boundary | Required response |
|-|-|-|
| `goto` times out and completion is unknown | navigation was the sole blocking command with the full outer budget, and the recorded tab URL/title may have changed | Record `navigation_result_unknown`, keep the same browser and tab bindings, then run a metadata-only reconciliation followed by one separate cheapest content read. A readable landed page is recovered success. Metadata failure routes to `page_control_partial`; healthy metadata plus content-read timeout routes to `chrome_content_channel_timeout`. Never classify the navigation timeout itself as `page_control_partial`, and never repeat the same `goto` merely to obtain acknowledgement. |
| Blank page, spinner, script error, or `Aw, Snap!` | no exact network code | Wait within `chrome_recovery.short_wait_seconds`, read again, then perform at most one safe same-tab reload/native navigation. Replace the tab only when its binding is actually stale or unusable. |
| Selected Reddit surface loops or fails while the equivalent capability may exist on the other surface | home/metadata is readable, exact route is unreadable, redirecting, or missing the required visible control | Apply `reddit-surface-routing.md` once for the same `canonical_target_key`: Old to current Reddit, or current Reddit to Old only when the required capability exists there. Preserve dwell, dedupe, mutation key, and recovery budget. Never bounce hosts or switch surfaces after an uncertain mutation. Retarget if the bounded equivalent route also fails. |
| HTTP `404` or `410` | exact target is deleted/unavailable | Retire that candidate and continue discovery. Do not retry the same target. |
| Private, restricted, quarantined, NSFW, archived, or locked surface | explicit page state | Apply live rules and mission scope. Skip/retarget unless the exact read/action is allowed and accessible; never treat it as a global Chrome fault. |
| Consent, login, or interstitial page | visible current UI | Resolve only a harmless native consent/interstitial when unambiguous. Password, login, CAPTCHA, account acknowledgement, or identity uncertainty is `user_repair`; keep the Heartbeat for read-only recheck. |

## Network And Site

| Edge case | Evidence boundary | Required response |
|-|-|-|
| DNS/offline/network changed/reset/timeout | exact Chrome code | Run one Reddit-home and at most one neutral-page scope probe; use bounded backoff across wakes. Do not infer account enforcement. |
| Proxy, tunnel, TLS, certificate, captive portal, or wrong system clock | exact code or visible Chrome warning | Never bypass TLS or change proxy/DNS/VPN. A neutral probe may identify wider scope; request one concrete user repair only after bounded persistence or an explicit portal/time warning. |
| HTTP `500-599` | exact response | Treat as transient site/route failure; retry within budget, then use Heartbeat backoff. |
| Persistent HTTP `403` | exact response on target, possibly home | Probe Reddit home and expected account. Route-level `403` retires/defers the route; login/WAF/account UI determines whether user repair is needed. |
| HTTP `429` or `Too Many Requests` | exact response or visible Reddit message | Enter `429_ROUND_PAUSE`; no same-wake probe, reload, navigation, or mutation. Respect `Retry-After` and preserve the mission/Heartbeat. |
| `ERR_BLOCKED_BY_CLIENT` | exact code | Try one clean native Reddit entry route in the lane tab. Do not disable extensions automatically. Persistently blocked deep routes are skipped; the mission continues elsewhere. |
| Neutral probe also fails | Reddit and neutral page both unreadable | Classify broad network/proxy/Chrome scope. Enter cross-wake backoff without opening more diagnostic tabs. |
| Neutral probe works but Reddit home fails | exact neutral proof plus failed Reddit home | Classify Reddit domain/site scope. Preserve login state and retry later; do not reset Chrome data. |

## Mutation And Verification

| Edge case | Evidence boundary | Required response |
|-|-|-|
| Failure before input | no draft entered | Safe to reopen/rebuild after context and account are re-read. |
| Failure after input but before submit | draft present, no submit attempt | Treat as unsent; re-read the target before preserving or retyping copy. |
| Fill/type/keypress acknowledges but controlled-input readback differs | focused-control shadow-aware live value does not equal the intended draft or empty value | Trust the readback, keep mutation `prepared`, and do not submit. Use the bounded platform select-all plus Backspace sequence or abandon the draft. |
| Light DOM shows no value for a Reddit custom input | visible DOM or `document.activeElement` identifies a custom host while its open shadow textarea owns the text | Recursively read open shadow roots and the active chain. Do not treat a light-DOM `[]` or empty host value as proof that the draft is empty. |
| Click/send call times out or response is lost | the click was the only browser-boundary command in its cell, received the full outer timeout, and submit acknowledgement is still unknown | Set `submission_uncertain`, quarantine exact target+text hash, and inspect target/profile/Notifications once. Never click/send the same mutation again automatically. |
| Comment/post/reply exists but permalink verification route fails | immediate native submit proof exists | Count only the immediate accepted UI proof already recorded; delayed visibility is follow-up evidence, not permission to resubmit. |
| Vote click returns an accepted UI transition | selected-state transition observed once | Count once and move on. Do not toggle or repeatedly reopen to reconfirm. |
| Vote click acknowledgement is unknown | click may have happened but no accepted transition proof | Mark exact vote uncertain and do not click that direction again. Continue other safe reads/actions after account and page health recover. |
| `ERR_CACHE_MISS` or form-resubmit warning | browser asks to replay entered data | Never reload/resubmit. Inspect target history once and quarantine if unresolved. |

## Scheduler, State, And User Activity

| Edge case | Evidence boundary | Required response |
|-|-|-|
| Heartbeat wakes while Chrome/network is still down | same fingerprint persists | Increment the failure-wake counter once, perform the wake's bounded read-only probe, choose the next configured backoff, and keep the same Heartbeat. |
| Three or more identical failed wakes | same fingerprint and scope | Enter `quiet_recovery`: one read-only probe per due wake, suppress duplicate user notices, and keep retrying until deadline/stop/terminal proof. Control-channel failure may request one user repair; ordinary route/network failure does not. |
| Several scheduled rounds were missed | actual time is later than planned | Recompute from current remainders and remaining authorization. Never catch up with a burst or claim missed reads/actions. |
| Local timezone, UTC offset, sleep/wake, or system clock changed | current local+UTC differs from checkpoint intent | Recalculate and read back the Heartbeat time before further work. Do not infer lateness only from displayed wall time. |
| Mission deadline passes during outage | current time is at/after `operation_stop_at` | Perform terminal checkpoint/Heartbeat cleanup; do not run a final recovery mutation or catch-up action. |
| Proposed recovery or `Retry-After` falls after the mission deadline | calculated recovery time is later than `operation_stop_at` | Clamp the next wake to `operation_stop_at`; that wake performs cleanup only and does not probe or mutate Reddit. |
| Checkpoint is missing/malformed | file unavailable or schema fields invalid | Reconstruct read-only from exact task, timer, tab inventory, and lane history. No mutation until identity and submission certainty are restored. |
| Checkpoint write fails | atomic persistence not proven | Withhold new mutation, keep the last durable remainders, retry persistence within budget, and use Heartbeat recovery. |
| Existing self-owned Heartbeat update/readback fails | previous recurring timer ownership is already verified | Preserve the previous timer and desired due time in the checkpoint; do not create a duplicate. Reconcile and repair on its next wake, or request user repair only if no verified future wake remains. |
| First Heartbeat creation or target binding cannot be verified | no prior verified recurring timer exists | Retry the create/readback transaction once. If self-targeting still cannot be proven, record `scheduler_repair_required` and tell the user autonomous continuation is unavailable; never claim the mission will continue automatically. |
| Heartbeat target is hidden/mismatched/duplicated | automation readback evidence | Follow the self-binding transaction. Repair only this task's recorded timer; never inspect or alter another task's timer. |
| User switches Reddit accounts in the shared Chrome profile | visible account differs from checkpoint account | Set `account_recheck_required`; do not write under the new identity. Continue read-only recovery and request user repair unless a new explicit mission revision authorizes that account. |
| User uses Chrome concurrently or changes focus | no explicit modification to the lane tab | Ignore focus. Address the lane tab by exact ID and never claim/navigate/close arbitrary user tabs. |

## Cross-Wake Invariants

- Mission-level recovery persists until verified mission completion, explicit user stop, `operation_stop_at`, or a hard user-repair state that cannot be automatically observed past the deadline.
- Same-wake retries are bounded by `operation-defaults.json`; a new Heartbeat wake is not permission to replay an uncertain mutation.
- Use `error_fingerprint = error_class|exact_code|failure_scope|hostname`. Keep the backoff index when only the deep URL changes inside the same failed scope.
- Reset backoff only after the configured number of healthy readable proofs and expected-account confirmation. Reddit home plus the exact target may provide the two proofs in one wake.
- A recovered technical failure resumes from persisted remainders without catch-up. A terminal deadline retires the Heartbeat even if the targets remain incomplete.
- A technical retry promise is valid only while a verified self-targeted Heartbeat has a future wake. Checkpoint persistence alone is not an automation guarantee.
