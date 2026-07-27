# Legacy Lane Checkpoint Compatibility

This reference applies **only** to the explicit migration mode
`execution_topology=legacy_multi_lane_compat`. It is not part of the production
`single_owner_v1` route and must not be loaded by a normal Reddit mission.

For the production default, use one durable record owned by `Reddit 运营台`:

```text
${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/single-owner/queues/
```

Its schema is `reddit_single_owner_queue/v1`, managed only through
`scripts/single_owner_queue.py`. That record keeps the five-unit plan,
append-only revision history, active/yielded unit, read batch, browser boundary,
frozen action keys, and Chrome-release proof together. Do not recreate
per-lane checkpoints, per-lane tabs, or per-lane Heartbeats in the production
topology.

Historical `lane-state/` and `lane-history/` files may be retained as evidence
from earlier multi-lane missions. They are read-only legacy artifacts: never
use them to infer a current owner, authorization, tab, timer, or action budget.
