# Chrome and actions

Use the same logged-in Chrome and one primary agent-owned Reddit tab for actual
Reddit consumption and every interactive action. Read the installed
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
2. Claim or reuse the current task's Reddit tab and perform navigation/read as
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
from a true browser disconnect without adding a startup blocker. A current
live rule/composer/session gate is still required immediately before a public
action.

## Atomic boundary rules

- Create/claim a tab, navigate, read DOM/screenshot, fill, click, submit, and
  verify in separate calls. Allow a configurable outer budget (normally up to
  120 seconds) only when the current wrapper supports an explicit per-call
  timeout; otherwise record the actual wrapper timeout and never pretend a
  shorter ambient timeout proves failure.
- One browser-client operation means one call boundary. Never combine
  `tabs.new()` with `goto`, or `goto` with DOM/screenshot. The sole permitted
  metadata pair is URL plus title in one metadata step.
- Record every browser call in the packet's `browser-steps.jsonl` as exactly
  one `claim`, `metadata`, `navigate`, `read_projection`, `fill`, `click`,
  `submit`, `verify`, or `finalize` step. `metadata` may read URL and title
  together, but it must never include navigation or DOM work. Before a public
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
expected session proof. Recheck the fresh visible session/composer/control,
title/body/flair,
live rule context, and submit availability. Submit once. Verify with a separate
targeted read. If the click/send may have occurred but proof is missing, record
`MUTATION_UNKNOWN`, freeze the exact key, and never retry it on another surface
or tab.

Release agent-owned research tabs before turn end. Keep a tab only when a
mission must continue from it; never retain or manipulate an unrelated user tab.
