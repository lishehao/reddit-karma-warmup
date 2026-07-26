# Model Runtime

The default is **inheritance**, not automatic migration: omit `model` and
`reasoning_effort` on task creation and continuation unless the current user
explicitly supplies a model request. Do not silently upgrade a task or copy a
previous task's execution profile. Role separation comes from exact task
ownership and lane prompts, not model-family differences.

The optional fallback chain in `operation-defaults.json` is available only when
the user explicitly asks for a preferred model **and** permits fallback:

```text
1. gpt-5.6-luna / high
2. gpt-5.6-terra / high
3. gpt-5.5 / high
4. gpt-5.4 / high
```

## Explicit Request Forms

- **Absent:** send no model override; record `MODEL_INHERITED`. Host/default
  runtime is valid and needs no model readback.
- **Exact pair:** request only the user-specified pair. If unavailable, record
  `MODEL_REQUEST_UNAVAILABLE`; do not silently substitute a different model.
- **Preferred pair with fallback:** use the user-authorized chain, record the
  requested pair and the actual pair when exposed, and use
  `MODEL_FALLBACK_CONFIRMED` only after runtime readback.

For an explicit request, `MODEL_REQUESTED_UNVERIFIED` means the host accepted
the request but did not expose actual runtime metadata. It is never confirmation.
No model request, accepted send, title, pin, or model readback is task-liveness,
archive, delivery, or replacement evidence.

## New And Existing Tasks

For a new task, pass a model pair only under an explicit request form. For an
existing present/unarchived lane, apply a per-turn override only when the same
current user command explicitly authorizes it and the host supports it. A
missing/unchanged readback preserves the exact lane; it never causes recreation.

The current `Reddit 启动台` normally becomes the distributor in place. Create a
successor for a model reason only when the user explicitly requests a model
migration, the host cannot update the current task in place, and the ordinary
exact-ID handoff gate succeeds. Unknown model metadata always keeps the current
task. Never transfer an in-flight Reddit mutation or Heartbeat to a successor.

Model choice is not a Chrome-recovery mechanism. A selector deadline,
transport error, stale tab, or page-content timeout follows the Chrome runtime
contract on every model. Do not use `ultra` by default.

Keep model metadata internal unless an explicit request is unavailable or
materially changes the current task.
