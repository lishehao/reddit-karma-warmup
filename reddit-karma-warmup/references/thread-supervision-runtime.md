# Legacy Multi-lane Compatibility

Load this file only when a user explicitly names
`execution_topology=legacy_multi_lane_compat` for an already-running legacy
mission. It is not a setup, dispatch, or recovery path for a new Reddit
operation.

## Default exclusion

The production default is `single_owner_v1`: one present, unarchived,
user-visible `Reddit 运营台` owns all five units, Chrome, Heartbeat, and durable
state. Do not create, discover, reuse, title-match, message, or supervise
separate `Reddit 评论台`, `Reddit 发帖台`, `Reddit 跟进台`, `Reddit 浏览台`, or
`Reddit 主页台` for a default mission.

## Explicit legacy migration only

Before touching a legacy task, require all of:

1. the user explicitly asks to continue that exact legacy topology;
2. exact `task_id` and `host_id` are known and current product state proves the
   task is present and unarchived;
3. the account/lane identity matches; and
4. no active Chrome mutation or uncertain delivery is being moved.

An archived task is never healthy or reusable. `notLoaded`, an empty/partial
inventory, timeout, or unknown archive state is not a reason to adopt, revive,
or send to the old task. Do not auto-unarchive. A migration that cannot prove
all four conditions stops without creating a replacement lane.

The legacy route may preserve historical checkpoints for audit, but a new
mission must be compiled into the single-owner envelope before it starts
Chrome work. There is no generic callback, no shared task scheduler, no
cross-task tab ownership, and no model-driven replacement in the default
topology.
