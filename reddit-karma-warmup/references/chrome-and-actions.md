# Chrome and actions

Use the same logged-in Chrome and one primary Reddit tab for actual Reddit
consumption and every interactive action. For session-bound work, first claim a
visible user tab from `browser.user.openTabs()`; a temporary `tabs.new()` tab is
recovery-only and is never proof of the logged-in Reddit session. Read the installed
`$chrome:control-chrome` protocol before first browser work.

## Health and routing

Track independently: browser control, tab metadata, content channel, route, and
session identity. A successful tab list/claim/title does not prove page readability.
When `goto`, DOM, screenshot, or evaluate times out while metadata remains
healthy, record `CHROME_CONTENT_CHANNEL_TIMEOUT`; do not report disconnect,
missing tab, or account enforcement.
This is not a Reddit rule result. If such a timeout prevents reading rules,
composer state, duplicates, or session proof, the affected unit must use
`LIVE_GATE_UNVERIFIED`/`YIELDED`, not `RULE_BLOCKED`.
An explicit target signal such as “This is an archived post. You won't be able
to vote or comment.” is a target-level `TARGET_ARCHIVED`/`TARGET_LOCKED` result,
not `LIVE_GATE_UNVERIFIED`, `RULE_BLOCKED`, or `ACCOUNT_BANNED`. Discard that
target and continue the search; it never implies that the account is banned.
The next task wake resumes that same unit with `RECOVERY_FIRST`; it must not
use `WATCH`, `SKIP`, `DEFER`, or fast NOOP merely because the previous tab was
blank.

Start on Old Reddit for ordinary listings, text, rules, and text forms. Make at
most one equivalent current-Reddit fallback when the required capability is
absent. Preserve the same canonical target and logged-in session. Never clear cookies,
switch browser/profile, change proxy/TLS, or turn an API result into a browser
recovery path.

## Silent session identity gate

The user never supplies or confirms an account name/handle. At startup, read
the visible logged-in session once and store its
internal proof in the mission envelope. Normal Heartbeat receipts do not echo
the handle. Recheck silently only after a tab rebind, login change, recovery,
stale checkpoint, or immediately before a mutation. If the session is unknown
or changed, pause the affected unit and report the mismatch; do not guess or
ask the user to repeat the account.

## Bounded startup and recovery

Run one short recovery path before the first Reddit session gate and again only
for a due `RECOVERY_FIRST` unit. It is a bounded retry, not a chain of probes:

1. Establish or reuse the existing Chrome binding and read tab metadata. Only
   an explicit browser-disconnected error permits one reconnect; a blank page,
   navigation timeout, or DOM timeout is a content-channel failure.
2. Claim or reuse the current task's visible user Reddit tab and perform navigation/read as
   separate calls. After a navigation timeout, read URL/title once before
   deciding whether the page actually loaded.
3. If metadata works but content does not, record
   `CHROME_CONTENT_CHANNEL_TIMEOUT`; retry in one fresh owned tab when the
   packet has budget. On a later wake, always make one fresh-tab content probe
   before yielding again. A URL-only check or `finalize` is not a content
   recovery.
4. If the current Reddit page is readable, continue immediately. Do not open
   neutral canary tabs, scan other tasks, or wait for a scheduler receipt.
5. Keep the same logged-in Chrome/profile. Never clear cookies, switch browser,
   change proxy/TLS, or turn an API result into a browser recovery path.

The classification deliberately does not guess whether the root cause is the
network, extension transport, or renderer. It distinguishes a content timeout
from a true browser disconnect without adding a startup blocker. A current live
rule/composer/session gate is still required immediately before a public
action; comments use the lightweight target/context/basic-rule version.

## Atomic boundary rules

- Create/claim a tab, navigate, read DOM/screenshot, fill, click, submit, and
  verify in separate calls. Set `timeout_ms=120000` (or the configured
  `chrome.minimum_outer_timeout_ms`) on the actual browser call; writing the
  value only into a ledger is invalid. Never inherit a 30-second Node/REPL or
  ambient browser default. If a tool returns `Script running` or a pending
  cell, await that result instead of reissuing the same browser action. A
  background telemetry timeout is not a browser failure unless the browser
  call or its readback also fails.
- One browser-client operation means one call boundary. Never combine
  `tabs.new()` with `goto`, `goto` with DOM/screenshot, or session naming with
  navigation. The normal call plan is `claim/new -> metadata -> navigate ->
  metadata -> read_projection`; the sole permitted metadata pair is URL plus
  title in one metadata step.
- Record every browser call in the packet's `browser-steps.jsonl` as exactly
  one `claim`, `metadata`, `navigate`, `read_projection`, `fill`, `click`,
  `submit`, `refresh`, `verify`, or `finalize` step. `metadata` may read URL and title
  together, but it must never include navigation or DOM work. Every record
  must include the actual `outer_timeout_ms`; a value below the configured
  minimum is invalid. Before a public
  action or packet finish, run `scripts/validate_browser_step_ledger.py` on
  that file; mixed `url/title/goto` calls are invalid. Every new `navigate`
  record includes `outcome=PASS|TIMEOUT|ERROR|UNKNOWN`; a `TIMEOUT` must be
  followed by an immediate metadata record with
  `post_timeout_readback=true` before another navigation or fresh-tab claim.
- After a navigation timeout, first read back URL/title/page state because the
  page may have loaded. Do not use `Promise.race` as faux cancellation.
  If readback is still `about:blank` or the content channel remains
  unavailable, use the next distinct ladder step in a fresh owned tab if the
  packet has budget; otherwise yield and let the next task wake run one fresh-tab
  recovery probe. Immediate same-boundary retry is forbidden, but a later
  read-only recovery is required. Do not turn the next wake into a no-Chrome
  `SKIP` solely because navigation failed.
- Build locators from a fresh snapshot. Act only on one visible, interactive,
  unique control. Refresh the snapshot after every state change.
- React fields may ignore `fill("")`; clear with Select All then Backspace and
  read back value/disabled state. Prefer visible controls over hidden inputs.
- Browse sequentially through real visible pages and bounded scroll/click
  transitions. Do not randomize timing, fake input, scrape hidden DOM, or run
  infinite scrolling.

## Action gate

Before a public action persist `action_key`, target, text/direction, and
expected session proof. For comments recheck target/context, basic rule,
composer, and submit availability; posts also recheck title/body, the live
Flair option/selection, and duplicate/recent history. If Flair is required,
select the most specific truthful option and record its visible label or ID;
if no truthful option exists, treat that route as `RULE_BLOCKED`. Submit once.
Verify with a separate targeted read. If
the click/send may have occurred but proof is missing, record
`MUTATION_UNKNOWN`, freeze the exact key, and never retry it on another surface
or tab. If the browser submit call completed but the page remains
`submitting...` or shows no new text after a bounded status read, do not click
again: record `POST_SUBMIT_FEEDBACK_PENDING`, perform at most one read-only
`refresh` on the exact target URL in the same logged-in Chrome session, then take
a fresh targeted read. A visible own author/text/permalink verifies the original
action; continued absence or ambiguity remains `MUTATION_UNKNOWN`/
`SUBMISSION_UNCERTAIN` and the key stays frozen. If the submit call itself timed
out or errored, the same refresh is optional observation only and never permits a
resubmit.

Release agent-owned research tabs before turn end. Keep a tab only when a
mission must continue from it; never retain or manipulate an unrelated user tab.
