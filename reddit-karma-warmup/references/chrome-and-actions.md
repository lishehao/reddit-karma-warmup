# Chrome and actions

Use the same logged-in Chrome and one primary agent-owned Reddit tab for actual
Reddit consumption and every interactive action. Read the installed
`$chrome:control-chrome` protocol before first browser work.

## Health and routing

Track independently: browser control, tab metadata, content channel, route, and
account. A successful tab list/claim/title does not prove page readability.
When `goto`, DOM, screenshot, or evaluate times out while metadata remains
healthy, record `CHROME_CONTENT_CHANNEL_TIMEOUT`; do not report disconnect,
missing tab, or account enforcement.
This is not a Reddit rule result. If such a timeout prevents reading rules,
composer state, duplicates, or account proof, the affected unit must use
`LIVE_GATE_UNVERIFIED`/`YIELDED`, not `RULE_BLOCKED`.

Start on Old Reddit for ordinary listings, text, rules, and text forms. Make at
most one equivalent current-Reddit fallback when the required capability is
absent. Preserve the same canonical target and account. Never clear cookies,
switch browser/profile, change proxy/TLS, or turn an API result into a browser
recovery path.

## Atomic boundary rules

- Create/claim a tab, navigate, read DOM/screenshot, fill, click, submit, and
  verify in separate calls. Allow a configurable outer budget (normally up to
  120 seconds) for a slow environment.
- Record every browser call in the packet's `browser-steps.jsonl` as exactly
  one `claim`, `metadata`, `navigate`, `read_projection`, `fill`, `click`,
  `submit`, `verify`, or `finalize` step. `metadata` may read URL and title
  together, but it must never include navigation or DOM work. Before a public
  action or packet finish, run `scripts/validate_browser_step_ledger.py` on
  that file; mixed `url/title/goto` calls are invalid.
- After a navigation timeout, first read back URL/title/page state because the
  page may have loaded. Do not use `Promise.race` as faux cancellation.
  If readback is still `about:blank` or the content channel remains
  unavailable, yield the packet and let the next verified Heartbeat run one
  bounded recovery probe. Do not turn the next wake into a no-Chrome `SKIP`
  solely because this navigation failed.
- Build locators from a fresh snapshot. Act only on one visible, interactive,
  unique control. Refresh the snapshot after every state change.
- React fields may ignore `fill("")`; clear with Select All then Backspace and
  read back value/disabled state. Prefer visible controls over hidden inputs.
- Browse sequentially through real visible pages and bounded scroll/click
  transitions. Do not randomize timing, fake input, scrape hidden DOM, or run
  infinite scrolling.

## Action gate

Before a public action persist `action_key`, target, text/direction, and
expected account. Recheck fresh visible composer/control, title/body/flair,
live rule context, and submit availability. Submit once. Verify with a separate
targeted read. If the click/send may have occurred but proof is missing, record
`MUTATION_UNKNOWN`, freeze the exact key, and never retry it on another surface
or tab.

Release agent-owned research tabs before turn end. Keep a tab only when a
mission must continue from it; never retain or manipulate an unrelated user tab.
