# Measured Interaction Pacing

Load in every Chrome-backed Reddit execution task before reading candidates, clicking controls, voting, or publishing text. This file owns short in-turn timing; `scheduler-and-heartbeats.md` owns waits longer than five minutes.

## Hard Clocks

| Clock | Hard minimum | Normal range |
|-|-:|-:|
| distinct candidate post/comment remains open after readable content appears | `30 sec` | `30-75 sec`; longer material may use `60-180 sec` |
| post/parent readable to comment or reply submission | `45 sec` | `45-120 sec` |
| draft entered to final comment/reply/Post click | `5 sec` | `5-12 sec` |
| separate non-atomic UI clicks | `1 sec` | `1-4 sec` |
| verified proactive comment to next comment submission | `3 min` | `3-5 min` |
| verified follow-up reply to next reply submission | `1 min` | `1-3 min` |

These are measured wall-clock floors, not estimates. The user may request a slower cadence. A faster user request does not remove the `30 sec` candidate dwell, `45 sec` readable-to-comment floor, `5 sec` pre-submit review, or one-click mutation rules.

## Candidate Dwell

1. Set `content_readable_at` only after the actual body/media and enough parent/thread context are visible and readable. Navigation, loading, blank-page, reconnect, and tool latency before that point do not count.
2. Read the content and current context, then keep that exact candidate open until at least `30 sec` has elapsed. Choose a longer dwell from content length and complexity; do not use the same exact duration mechanically.
3. Before the dwell floor passes, do not move to another candidate, cast a vote, begin a publish mutation, or count a qualified read. Scrolling and additional context reading on the same item are allowed.
4. If useful reading and analysis already consumed the floor, do not add another full wait. Record actual elapsed time and continue.

For comments and replies, `comment_readable_to_submit_seconds` must also be at least `45`. The 30-second candidate dwell is contained inside that clock; it is not added twice.

## Short Timer Implementation

- Capture real timestamps before and after each floor. Store `content_readable_at`, `candidate_leave_or_act_at`, `candidate_dwell_seconds`, and, for text, `draft_entered_at`, `submit_at`, and `pre_submit_pause_seconds`.
- For a remaining wait of at most five minutes, prefer a local terminal sleep such as `sleep <remaining_seconds>` while preserving the dedicated Reddit tab. A tool-supported wait is acceptable only when it yields real wall-clock time.
- Do not use a page-side JavaScript timer, busy loop, repeated screenshot, reload, or fake timestamp as a wait.
- Use the lane's recurring Heartbeat for waits longer than five minutes. Never create a Heartbeat for a 30-second read dwell or a 5-12 second submit pause.

## Click And Submit Sequence

1. Inspect the visible control and account/target state.
2. Keep `1-4 sec` between separate non-atomic UI clicks; never double-click, click-loop, or use repeated clicks as verification.
3. For text, enter the final passing draft, run Double-Check B, then keep the draft visible for `5-12 sec` before the one final submit click. Require the total readable-to-submit clock to be at least `45 sec`.
4. For votes, the candidate dwell must pass before the one-click vote gate. After an accepted click, do not spend another delay reconfirming selected styling.
5. After a verified proactive comment, use `3-5 min` before another comment submission. Follow-up replies use `1-3 min`. Discovery may continue during the gap, but every newly opened candidate still owns its separate 30-second dwell.

## Evidence And Failure

A qualified-read or publish ledger entry includes the measured clocks. If the tab changes, reloads, disconnects, or becomes unreadable before the floor passes, discard that dwell and restart `content_readable_at` after the exact content is readable again. Never report a timing floor as passed from planned duration alone.
