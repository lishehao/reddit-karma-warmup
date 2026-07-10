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

For the proactive comment lane, write this first-action marker as soon as the first permalink exists, then continue toward the `10`-comment first-hour target. The coordinator's delayed visibility check runs in parallel; do not pause the worker merely because that check is pending. A concrete failed visibility/account result stops further comments.

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

Profile edits, joins, flair, notification sweeps, and verified no-action results have no public visibility gate. Validate only their own final UI state and heartbeat handoff.

## Acceptance And Recovery

A lane with a first outward action reaches `first_round_ok` only after `submit_verified`, `surface_visible`, and `survivor_visible`, plus verified worker heartbeat handoff when continuation is required.

Non-publishing lanes use action-specific acceptance instead of permalink checks:

- `内容浏览`: `8-12` qualified reads are logged and the vote gate was applied; `0` votes is valid. If a vote was cast, a refresh confirms the selected arrow remains active.
- `主页维护`: the due profile/join work is verified, or the lane records a concrete valid no-action result.
- `消息跟进`: Notifications and recent own activity were swept, with any reply processed through the normal outward checks.

These lanes still require a verified next heartbeat when continuation is due.

On `visibility_failed`:

1. Read the exact Reddit, Automod, or moderator state; do not guess.
2. Do not repost the same content immediately.
3. Send the evidence to the owning worker for one focused diagnosis or safer retarget.
4. Keep startup acceptance open for at most two recoverable retries; then record `startup_blocked` with the exact reason.

Early acceptance does not end coordinator observation. Keep the temporary read-only heartbeat through `startup_watch_deadline`, run the final first-hour sweep, then delete it and enter `IDLE`. Do not use Goal Mode or active polling between checks. Later worker rounds do not receive coordinator visibility supervision unless the user explicitly requests another audit.
