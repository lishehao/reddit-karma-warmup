# Model Runtime

The default single-owner operating profile prefers `gpt-5.6-luna / high`.
This is a **request preference**, not proof that the host switched the current
task. The configured fallback chain is `gpt-5.6-luna / high`,
`gpt-5.6-terra / high`, `gpt-5.5 / high`, then `gpt-5.4 / high`.

## Record, do not guess

When the host exposes model selection or runtime metadata, record all three:

```text
requested_model / requested_reasoning_effort
actual_model / actual_reasoning_effort when exposed
evidence_state = ACTUAL_CONFIRMED | REQUESTED_NOT_RUNTIME_PROOF | INHERITED
```

If the host cannot switch or cannot expose the actual pair, keep the same
`Reddit 运营台`; do not create a successor, a parallel task, or a duplicate
mission. Model metadata is never Chrome, archive, account, delivery, or action
success evidence.

The configured fallback chain is only a host request policy. It may be used
when the host explicitly supports a preferred-model request; the queue and
mission envelope remain unchanged across any supported fallback. Do not use a
model switch as Chrome recovery or as a reason to replay a mutation.
