# Purposeful Visible Chrome Reading

Load only when a current lane is about to begin a measured candidate dwell or
an outward mutation. Do not preload it during setup, registry resolution, or a
pure checkpoint repair. Numeric clocks come only from `operation-defaults.json`;
this file explains short in-turn timing, while `scheduler-and-heartbeats.md`
owns waits longer than the configured local-sleep maximum.

## Hard Clocks

| Clock | Canonical field |
|-|-|
| distinct candidate remains open after readable content appears | `interaction_pacing.candidate_dwell_*` |
| parent readable to comment or reply submission | `interaction_pacing.comment_readable_to_submit_*` |
| draft entered to final submit click | `interaction_pacing.pre_submit_pause_seconds` |
| separate non-atomic UI clicks | `interaction_pacing.inter_click_pause_seconds` |
| verified proactive comment to next comment submission | `comments.proactive_submit_gap_seconds_*` |
| verified follow-up reply to next reply submission | `followup.reply_submit_gap_seconds_*` |

These are measured comprehension/evidence floors, not a recipe for pretending
to be human. The user may request a slower cadence. A faster user request does
not remove any configured floor or the one-click mutation rules. Never add random delay, cursor jitter, hidden-DOM scrolling, fingerprint changes, or other stealth behavior.

## Candidate Dwell

1. Set `content_readable_at` only after the actual body/media and enough parent/thread context are visible and readable. Navigation, loading, blank-page, reconnect, and tool latency before that point do not count.
2. Read the content and current visible context through the normal Chrome page path. Let real content length, premise, comments, and needed context determine whether the configured floor is naturally exceeded; do not select variable delays to imitate a person.
3. Before the dwell floor passes, do not move to another candidate, cast a vote, begin a publish mutation, or count a qualified read. Scrolling and additional context reading on the same item are allowed.
4. If useful reading and analysis already consumed the floor, do not add another full wait. Record actual elapsed time and continue.

## Browser/API Boundary

All account browsing is visible Chrome browsing: open a normal subreddit/post
surface, read the post and enough visible context/comments for the decision, and
move to the next item only after the qualified-read evidence exists. Do not use
the audit API as a per-item browsing surface, bulk-read post bodies, automate
infinite scrolling, or substitute API item lists for a lane's visible content
reading. The shared audit pool may provide a small list of public hot-item IDs
or permalinks; Chrome still opens and evaluates every such item.

For comments and replies, `comment_readable_to_submit_seconds` must also meet its configured minimum. Candidate dwell is contained inside that clock; it is not added twice.

## Short Timer Implementation

- Capture real timestamps before and after each floor. Store `content_readable_at`, `candidate_leave_or_act_at`, `candidate_dwell_seconds`, and, for text, `draft_entered_at`, `submit_at`, and `pre_submit_pause_seconds`.
- For a remaining wait at or below `local_sleep_max_seconds`, use a local terminal sleep such as `sleep <remaining_seconds>` while preserving the dedicated Reddit tab. Never bundle that wait with click, fill, type, vote, or submit; the same ban applies to browser-side waits.
- Do not use a page-side JavaScript timer, busy loop, repeated screenshot, reload, or fake timestamp as a wait.
- Use the lane's recurring Heartbeat for waits longer than `local_sleep_max_seconds`. Never create a Heartbeat for an in-item read or submit-pause floor.

## Click And Submit Sequence

1. Inspect the visible control and account/target state in one atomic browser read; reuse that evidence until the UI changes.
2. Keep the configured inter-click pause between separate non-atomic UI clicks; never double-click, click-loop, or use repeated clicks as verification. Every click, fill/type, and result observation is a separate `node_repl` cell under `chrome-atomic-command-runtime.md`.
3. For text, enter the final passing draft as one browser command, run Double-Check B from stored evidence or a separate read, then keep the draft visible for the configured pre-submit pause using terminal `sleep`. The one final submit click is the sole browser-boundary command in its cell. Require the configured readable-to-submit floor.
4. Only `Reddit 浏览台` applies vote pacing: candidate dwell must pass before the one-click vote gate. After an accepted click, do not spend another delay reconfirming selected styling. Every other lane ignores vote controls entirely.
5. After a verified proactive comment or follow-up reply, use the matching configured submit gap. Discovery may continue during the gap, but every newly opened candidate still owns its separate dwell.

## Evidence And Failure

A qualified-read or publish ledger entry includes the measured clocks. If the tab changes, reloads, disconnects, or becomes unreadable before the floor passes, discard that dwell and restart `content_readable_at` after the exact content is readable again. Never report a timing floor as passed from planned duration alone.
