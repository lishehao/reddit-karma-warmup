# Model Runtime

Use one ordered model/effort fallback chain for both distribution and lane execution. The canonical chain is stored in `operation-defaults.json`:

```text
1. gpt-5.6-luna / high
2. gpt-5.6-terra / high
3. gpt-5.5 / high
4. gpt-5.4 / high
```

Use the first pair exposed by the destination host. Apply the same chain to the distributor and every newly created lane worker. Role separation comes from persistent task ownership and lane prompts, not from different model families. Do not present a model menu during normal operation.

The bootstrap prompt explicitly authorizes requesting `gpt-5.6-luna/high` for the distributor and all lane tasks. A model request is intent, not proof. Record one of these evidence states whenever the host exposes task model control:

- `LUNA_CONFIRMED`: actual task runtime metadata reports `gpt-5.6-luna/high`;
- `LUNA_REQUESTED_UNVERIFIED`: create/send accepted the override but actual runtime metadata is unavailable;
- `LUNA_UNAVAILABLE_FALLBACK`: the host explicitly rejected Luna and the next supported pair was used;
- `SELF_MODEL_UNVERIFIED`: the current launcher's actual pair cannot be read;
- `SELF_SUCCESSOR_CREATED_CONFIRMED`: one Luna/high successor accepted the exact distributor handoff and its runtime was confirmed.

Never report `LUNA_CONFIRMED` from a requested field, accepted message, title, or model preference alone.

## New And Existing Tasks

Before creating a distributor successor or lane task, inspect the host's actual model surface when available. Request Luna/high first; otherwise request Terra/high, then 5.5/high, then 5.4/high. If none is exposed, inherit the current/default model and use High or the nearest supported effort. Model fallback never blocks Reddit work.

When dispatching a new mission to an existing present, unarchived, healthy lane task, request `gpt-5.6-luna/high` on that exact send/continuation call when the host schema supports per-turn model overrides. Read actual runtime metadata afterward when exposed. If readback is absent or does not change, preserve the exact task, record `LUNA_REQUESTED_UNVERIFIED` or the actual pair, and continue the authorized mission. Do not recreate a healthy lane merely because a per-turn override is unverified.

## Current Launcher Self-Transition

The Skill cannot mutate the model of the turn that is already executing. The current `Reddit 启动台` must therefore follow this ordered gate after read-only preflight and before becoming the persistent distributor:

1. Read the current task's actual model/effort when the host exposes it.
2. If it is already Luna/high, keep the same task and record `LUNA_CONFIRMED`.
3. If the host exposes a verifiable current-task/next-turn model update, request Luna/high once and require actual runtime readback before calling it confirmed.
4. If the current task is explicitly confirmed non-Luna, no verifiable in-place update exists, and the bootstrap prompt or latest user instruction explicitly authorizes Luna migration, create exactly one projectless Luna/high successor. Send only the distributor identity, bootstrap/preflight result, exact account direction state, and pending user command. Require exact successor acceptance, actual ready task ID, canonical rename/pin, and model readback when available. Only then release and archive the old temporary launcher. Never transfer an in-flight Reddit mutation or Heartbeat.
5. If the current model is unknown, do not create a speculative duplicate. Keep the same task, record `SELF_MODEL_UNVERIFIED`, and continue with Luna/high requests for every created or continued lane task.

At most one successor attempt is allowed per bootstrap. A queued `clientThreadId`, create response, readable history, title, or pin is not a ready successor. If the successor is unsupported, uncertain, or rejects the handoff, keep the current launcher and use the normal fallback chain; do not archive it.

Model choice is not a Chrome-recovery mechanism. A selector backend deadline, transport error, stale tab, or unsupported browser API must follow the Chrome runtime contract on every model. Switching Luna/Terra never repairs browser transport or page content channels.

Do not use `ultra` by default. The Skill already owns lane fan-out and assigns an independent Chrome tab context to each worker, so automatic task delegation would duplicate orchestration.

The user's latest explicit model/effort request overrides the chain when that pair is available. Record requested pair, actual pair, and evidence state separately in mission state.

Keep launcher/worker model runtime internal. Mention it only when an unavailable model or effort materially changes execution quality or blocks the current task.
