# Chrome Atomic Command Runtime

Load in every Chrome-backed Reddit execution task before the first page command. This reference owns browser command granularity and outer timeout budgets; `chrome-network-recovery.md` owns failures after these rules are applied.

## Canonical Budget

Read `operation-defaults.json.chrome_command_runtime`. Every `node_repl` cell that crosses the Chrome browser boundary must set the tool's outer `timeout_ms` to `outer_timeout_ms`. A locator action may additionally set its supported inner `timeoutMs` to `locator_action_timeout_ms`.

The ordinary `node_repl` default of `30000 ms` is not a valid Chrome operation budget on a machine where the browser client itself has a roughly 30-second control or telemetry delay. A browser command that returns successfully after the configured `slow_success_threshold_ms` is slow success, not a timeout, disconnect, page failure, or account risk.

## One Boundary Command Per Cell

Use at most `browser_boundary_commands_per_cell` awaited browser-boundary command in one `node_repl` cell. Local string parsing, hashing, scoring, and use of a previously stored snapshot may share a cell because they do not cross the browser boundary.

Browser-boundary commands include navigation, DOM/screenshot/evaluate reads, locator reads, clicks, fills, typing, keypresses, scrolling, tab claiming, and finalization. In particular, never bundle:

- `goto + DOM read`;
- `snapshot + locator count + action`;
- `click + type + DOM read`;
- `fill/type + submit-state read`;
- fixed wait + mutation click;
- mutation click + result verification.

Cheap `url()` or `title()` metadata may be read only when needed, but never use their speed to justify bundling a slow page command or mutation in the same cell.

## Stable Sequences

### Navigation

1. Run only `tab.goto(exact_url)` with the configured outer timeout.
2. In a new cell, read only the cheapest state needed: URL/title or one snapshot.
3. Reuse that snapshot until the UI changes or it proves stale.

### Read And Interact

1. Take one snapshot or targeted read in its own cell.
2. Prefer `dom_cua.get_visible_dom()` for an interactable control. Resolve one exact node locally and preserve `node_id` as a string; DOM CUA rejects numeric node IDs before the page call.
   For Reddit search, identify the unique visible native `textarea` by semantic identity (`name=q` inside the Reddit search host), not by one exact placeholder. `Find anything`, `Search in r/<subreddit>`, localized copy, and later placeholder changes are equivalent search-control variants; record the observed placeholder as evidence but never use a placeholder mismatch alone to reject an otherwise unique control.
3. If a Playwright locator is used, prove uniqueness in one separate `count()` cell.
4. Run the click/fill/type as the sole browser-boundary command in its cell. A focus-dependent DOM CUA control uses separate `click({node_id: string})` and `type(...)` cells.
5. Collect a separate targeted observation only when the next decision requires it.

If a locator action fails at its internal selector/CDP deadline while `get_visible_dom()` or a bounded page projection succeeds, classify `locator_backend_deadline`. Do not reconnect Chrome, reload, or retry that locator. Resolve one fresh DOM CUA node for that control and continue once. Never loop over locators or repeatedly reacquire Chrome after a slow-but-successful command.

### Controlled Text Inputs

Treat text entry and text-state proof as separate browser commands. A successful `fill()`, `type()`, or `keypress()` acknowledgement proves only that Chrome accepted the command; it does not prove the final text. Before any outward submit, perform one bounded page projection that reads the live property of the focused control. Starting at `document.activeElement`, follow each open `shadowRoot.activeElement`; recursively inspect open shadow roots when Reddit wraps the native input in a custom element. For value-bearing controls compare the exact `value`; for `contenteditable` compare the exact live text property. Return only the control identity and value needed for proof, never the page body.

An interaction can change a control's tag, accessible name, placeholder, visible label, or surrounding DOM. Never reuse a locator or DOM node across that state change. Fresh visible DOM may expose a shadow-native `textarea` while page-level DOM exposes only its custom-element host. This is expected. Use shadow-aware live-property proof; if the exact draft is not provable, keep the mutation `prepared` and do not submit.

Do not hard-code Reddit placeholder copy as control identity. When visible DOM exposes more than one `textarea name=q`, use a bounded shadow-aware projection to associate each native textarea with its nearest Reddit search host and current scope, then require exactly one visible, enabled candidate. If uniqueness is still not provable, stop that interaction without typing; this is `control_ambiguous`, not a Chrome disconnect or page-control failure.

For a non-empty controlled input that must be replaced or cleared:

1. Take fresh visible DOM, resolve one exact control node, and preserve its `node_id` as a string.
2. Click that node in its own cell when focus is not already proven.
3. On macOS run only `dom_cua.keypress({keys:["Meta","A"]})`; elsewhere use `Control`; in the next cell run only Backspace.
4. Run one separate shadow-aware live-property projection and require the exact intended draft or empty string. A fresh visible DOM exact-text check is a fallback proof only when it exposes the complete value.
5. If the value is not the intended exact draft or empty string, do not submit. Rebuild once and use the platform fallback only when the first shortcut itself is unsupported; never loop on an acknowledged but ineffective action.

Do not use `fill("")` as the sole proof that a Reddit controlled input cleared. Do not use a light-DOM-only selector against a Reddit custom element as proof that its shadow input is empty. If an action returns success but shadow-aware readback disagrees, trust the readback, keep the mutation in `prepared`, and repair or abandon the draft before any submit click.

### Outward Mutation

1. Persist `mutation_state=prepared`, exact target, and text hash.
2. Run any remaining `pre_submit_pause_seconds` with terminal `sleep` as a separate local wait. Do not call `playwright.waitForTimeout` in the submit cell.
3. Reuse fresh control evidence only if the UI has not changed; otherwise take one separate fresh visible-DOM transaction.
4. Run exactly one final click as the only browser-boundary command in a cell whose outer timeout is `outer_timeout_ms`.
5. If the click returns success, record the immediate accepted state available from that call and perform at most one separate targeted readback when needed.
6. If the outer call has no acknowledgement after the full configured timeout, set `submission_uncertain`, quarantine the exact action, and never replay it.

For a focus-dependent editor, prefer fresh DOM CUA on this runtime. Put the focus click and type action in two separate cells, each with the full outer timeout, then run shadow-aware readback in a third cell. Never combine them with a DOM read or submit.

## Ambient Network Delay

The bundled Chrome client may emit `Statsig` or `ab.chatgpt.com` timeout logs when its optional ambient telemetry cannot use the machine's proxy path. If the requested Chrome command still returns successfully, classify `ambient_network_degraded` and continue in atomic mode. These logs do not prove Reddit failure, Chrome disconnection, rate limit, account enforcement, or failed mutation.

`BROWSER_USE_DISABLE_AMBIENT_NETWORK=1` under `[mcp_servers.node_repl.env]` is an optional latency optimization, not a Skill dependency. It requires a fresh Node REPL/Codex process to take effect. Never stop a healthy mission merely because this flag is absent; the atomic timeout contract must remain sufficient.

Classify `page_control_partial` only when one atomic command receives no acknowledgement after the full outer timeout or the control transport explicitly fails. An internal locator deadline with healthy visible DOM/page projection is `locator_backend_deadline`, not page-control failure. A successful 20-60 second command is evidence that page control remains usable.
