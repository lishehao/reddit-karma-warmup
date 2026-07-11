# Startup Health Check

Load only for first-round acceptance of a newly dispatched batch. It verifies that the first outward action was actually published, remained visible after initial moderation, and handed off to a valid worker heartbeat. The coordinator uses a dedicated read-only Reddit acceptance tab or Tab Group; it never touches worker tabs.

## Visibility Levels

Use precise labels:

- `submit_verified`: the worker submitted, received an exact permalink, reloaded it, and still sees the expected author/content with no pending, removed, deleted, filtered, spam, or warning state
- `surface_visible`: the coordinator independently opens the permalink in its own logged-in Chrome tab and also finds the item on a second Reddit surface
- `survivor_visible`: the same item remains visible in the delayed coordinator sweep `15-30 min` later
- `public_visible`: a separate signed-out/Guest Chrome context can open the item; use only when that context already exists or Chrome can create it without logging out the operating account
- `visibility_failed`: the item is missing, removed, pending approval, author-only, or inconsistent across required surfaces

Do not call same-account visibility `public_visible`. If no independent signed-out Chrome context exists, report `survivor_visible` and state internally that anonymous public visibility was not tested. Do not log out the operating Reddit account to manufacture this check.

## Required Evidence

The worker records after its first outward action:

- exact permalink
- expected author and subreddit/parent thread
- local submit time and timezone
- immediate reload result and any Reddit/Automod message

For the proactive comment lane, write this first-action marker as soon as the first permalink exists, then continue within the selected first-hour intensity envelope. The coordinator's delayed visibility check runs in parallel; do not pause the worker merely because that check is pending. A concrete failed visibility/account result stops further comments.

The coordinator then uses its own read-only acceptance tab:

1. Open the exact permalink and hard reload once.
2. Confirm author, content identity, timestamp, and absence of removed/pending/error UI.
3. Confirm a second Reddit surface:
   - main post: subreddit `/new` plus the author's Posts view
   - comment/reply: parent thread comment chain plus the author's Comments view
4. Record `surface_visible` or `visibility_failed`.
5. Schedule or update one temporary coordinator heartbeat for `15-30 min` after the latest first outward action.
6. Reopen the same permalink and second surface. Record `survivor_visible` only if both still pass.
7. If a separate signed-out/Guest Chrome context is already available, optionally open the permalink there and record `public_visible`; otherwise do not claim anonymous visibility.

Bootstrap profile edits/joins, notification sweeps, browsing, and verified no-action results have no public visibility gate. Validate only their own final UI state and heartbeat handoff.

## Acceptance And Recovery

A lane with a first outward action reaches `first_round_ok` only after its persistent worker exists, `submit_verified`, `surface_visible`, and `survivor_visible`, plus a successfully created lane-owned heartbeat handoff when continuation is required. A combined coordinator continuation cannot satisfy this check. Exact persisted timing should be verified when exposed; `created_unreadable` is acceptable until the heartbeat's first real wakeup proves or disproves timing.

Non-publishing lanes use action-specific acceptance instead of permalink checks:

- `自然浏览`: the configured qualified-read budget is logged and each vote gate was applied. Standard expects `20-30` reads and targets `2` combined votes. A shortfall is valid only with exhausted budget or a concrete blocker; every cast vote is refreshed once to confirm the selected arrow remains active.
- `消息跟进`: Notifications and recent own activity were swept, with any reply processed through the normal outward checks.

These lanes still require a successfully created next heartbeat when continuation is due. Hidden persisted timing is recorded as `created_unreadable` and does not pause the lane.

On `visibility_failed`:

1. Read the exact Reddit, Automod, or moderator state; do not guess.
2. Do not repost the same content immediately.
3. Send the evidence to the owning worker for one focused diagnosis or safer retarget.
4. Keep startup acceptance open for at most two recoverable retries; then record `startup_blocked` with the exact reason.

Early acceptance does not end coordinator observation. Keep the temporary read-only heartbeat through `startup_watch_deadline`, run the final first-hour sweep, then delete it and enter `IDLE`. Do not use Goal Mode or active polling between checks. Later worker rounds do not receive coordinator visibility supervision unless the user explicitly requests another audit.
