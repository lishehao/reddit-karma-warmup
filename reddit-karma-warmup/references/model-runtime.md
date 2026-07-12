# Model Runtime

Use one default model/effort pair for both coordination and lane execution:

```text
launcher model: gpt-5.6-luna
launcher thinking effort: high (High)
worker model: gpt-5.6-luna
worker thinking effort: high (High)
```

Use Luna/high for the launcher and every lane worker. Role separation comes from persistent task ownership and lane prompts, not from different model families. Do not present a model menu during normal operation.

The Skill cannot change the model of an already-running task. If a launcher or worker already exists on another model, do not recreate or interrupt it only to switch; record the actual model and continue setup or the current user-requested operation.

Before dispatch, verify Luna/high against the host's actual model surface. If Luna/high is unavailable, use Luna at the nearest supported effort, then the strongest practical model/effort pair exposed by the host. Apply the same fallback policy to launcher and workers. Model fallback never blocks Reddit work.

Do not use `ultra` by default. The Skill already owns lane fan-out and assigns an independent Chrome tab context to each worker, so automatic task delegation would duplicate orchestration.

The user's explicit model/effort request still overrides these defaults when the requested pair is available.

Keep launcher/worker model runtime internal. Mention it only when an unavailable model or effort materially changes execution quality or blocks the current task.
