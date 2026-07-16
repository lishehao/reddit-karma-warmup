# Model Runtime

Use one ordered model/effort fallback chain for both distribution and lane execution. The canonical chain is stored in `operation-defaults.json`:

```text
1. gpt-5.6-luna / high
2. gpt-5.5 / high
3. gpt-5.4 / high
```

Use the first pair exposed by the destination host. Apply the same chain to the distributor and every newly created lane worker. Role separation comes from persistent task ownership and lane prompts, not from different model families. Do not present a model menu during normal operation.

The Skill cannot change the model of an already-running task. If a launcher or worker already exists on another model, do not recreate or interrupt it only to switch; record the actual model and continue setup or the current user-requested operation.

Before task creation, inspect the host's actual model surface. Request Luna/high when supported; otherwise request 5.5/high, then 5.4/high. If none is exposed, inherit the current/default model and use High or the nearest supported effort. Model fallback never blocks Reddit work.

Do not use `ultra` by default. The Skill already owns lane fan-out and assigns an independent Chrome tab context to each worker, so automatic task delegation would duplicate orchestration.

The user's latest explicit model/effort request overrides the chain when that pair is available. Record the actual selected pair in mission state; do not recreate a healthy existing task merely to change models.

Keep launcher/worker model runtime internal. Mention it only when an unavailable model or effort materially changes execution quality or blocks the current task.
