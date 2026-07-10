# Model Runtime

Use separate defaults for coordination and lane execution:

```text
coordinator model: gpt-5.6-sol
coordinator thinking effort: xhigh (Extra High)
worker model: gpt-5.6-luna
worker thinking effort: xhigh (Extra High)
```

Use Sol/xhigh only for startup decomposition, worker dispatch, bounded observation, heartbeat handoff, and later user-requested cross-thread reconciliation. Use Luna/xhigh for every lane worker. Do not present a model menu during normal operation.

The Skill cannot change the model of an already-running coordinator task. Start a new coordinator with `gpt-5.6-sol/xhigh` when the host exposes that pair. If the coordinator already exists on another model, do not recreate or interrupt it only to switch; record the actual model and continue startup acceptance or the current user-requested coordination.

Before dispatch, verify each requested pair against the host's actual model surface. If Sol/xhigh is unavailable, use the strongest coordinator model actually exposed with `xhigh`; if xhigh is unavailable, use the highest supported effort. If Luna/xhigh is unavailable for workers, use Luna at the highest supported effort, then inherit the strongest practical worker fallback. Model fallback never blocks Reddit work.

Do not use `ultra` by default. The Skill already owns lane fan-out and assigns an independent Chrome tab context to each worker, so automatic task delegation would duplicate orchestration.

The user's explicit model/effort request still overrides these defaults when the requested pair is available.

Keep coordinator/worker model runtime in internal state. Mention it in the user-facing `风险` field only when an unavailable model or effort changes execution quality or blocks a lane.
