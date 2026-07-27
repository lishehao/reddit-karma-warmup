# Legacy Multi-lane Heartbeats

This file applies only to an explicitly requested `legacy_multi_lane_compat`
migration. A new `single_owner_v1` mission has exactly one recurring,
mission-level Heartbeat owned by the single `Reddit 运营台`.

Do not create per-unit timers. A heartbeat deviation within the configured
five-minute tolerance is ordinary; continue the same queue without repair.

