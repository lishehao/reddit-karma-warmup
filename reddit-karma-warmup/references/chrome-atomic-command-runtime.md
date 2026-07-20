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

### Read And Locator

1. Take one snapshot or targeted read in its own cell.
2. Build a locator from that evidence locally.
3. If uniqueness is not already guaranteed, run only `count()` in a new cell.
4. Run the click/fill/type as the sole browser-boundary command in its cell.
5. Collect a separate targeted observation only when the next decision requires it.

Prefer one targeted locator/evaluate check over repeated full `domSnapshot()` calls. Never loop over locators or repeatedly reacquire Chrome after a slow-but-successful command.

### Outward Mutation

1. Persist `mutation_state=prepared`, exact target, and text hash.
2. Run any remaining `pre_submit_pause_seconds` with terminal `sleep` as a separate local wait. Do not call `playwright.waitForTimeout` in the submit cell.
3. Reuse fresh locator evidence or take one separate snapshot/count transaction.
4. Run exactly one final click as the only browser-boundary command in a cell whose outer timeout is `outer_timeout_ms`.
5. If the click returns success, record the immediate accepted state available from that call and perform at most one separate targeted readback when needed.
6. If the outer call has no acknowledgement after the full configured timeout, set `submission_uncertain`, quarantine the exact action, and never replay it.

For a focus-dependent editor, use one `fill()` when supported. If DOM CUA genuinely requires focus then typing, put the focus click and the type action in two separate cells, each with the full outer timeout. Never combine them with a DOM read.

## Ambient Network Delay

The bundled Chrome client may emit `Statsig` or `ab.chatgpt.com` timeout logs when its optional ambient telemetry cannot use the machine's proxy path. If the requested Chrome command still returns successfully, classify `ambient_network_degraded` and continue in atomic mode. These logs do not prove Reddit failure, Chrome disconnection, rate limit, account enforcement, or failed mutation.

`BROWSER_USE_DISABLE_AMBIENT_NETWORK=1` under `[mcp_servers.node_repl.env]` is an optional latency optimization, not a Skill dependency. It requires a fresh Node REPL/Codex process to take effect. Never stop a healthy mission merely because this flag is absent; the atomic timeout contract must remain sufficient.

Classify `page_control_partial` only when one atomic command receives no acknowledgement after the full outer timeout or the control transport explicitly fails. A successful 20-60 second command is evidence that page control remains usable.
