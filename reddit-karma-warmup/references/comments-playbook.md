# Proactive Comments Playbook

Load only in `Reddit 评论台`, together with `proactive-common.md`, `default-operations-sop.md`, `publish-consistency.md`, `outbound-copy-gate.md`, and the shared runtime pack. Numeric defaults come only from `operation-defaults.json`. This lane uses `vote_policy=DISABLED_BY_LANE`: never load `browse-vote-playbook.md` or inspect/click Upvote or Downvote.

## Mission And High-Volume Mode

Resolve one exact action target, cap, and qualified-read target from `operation-defaults.json` or the latest user override. A count of `2+` uses clustered windows with at least two verified comments per completed window. A user request for exactly one total comment is the only count-based single-action exception.

Daily `60` mode is not default. Enable it only for an explicit roughly-60/day request or explicit high intensity for at least `6h`. Keep at least six eligible communities and three clusters when available, no more than five proactive comments in one subreddit per `24h`, and no catch-up burst. The target never lowers candidate, copy, rule, or pacing gates.

## Candidate Gate

Score the exact post and intended parent after the required measured read:

| Factor | Points |
|-|-:|
| Exact context relevance | 0-25 |
| New value available | 0-25 |
| Freshness and visibility | 0-20 |
| Community/account fit | 0-15 |
| Rules and truthfulness | 0-15 |

- `Act >=80`; a reply to one exact parent should reach `>=82`.
- `Watch 68-79`: learn and continue.
- `Skip <68`: stale, saturated, generic, unsafe, promotional, or dependent on invented experience.

A qualified read opens the exact content, consumes body/media and enough nearby replies to assess duplication, and passes the measured dwell in `interaction-pacing.md`. Feed impressions and titles do not count.

## Per-Item Execution

For every individual comment, including every item in one cluster:

1. Assign a fresh `per_comment_gate_id` and reopen the exact target.
2. Run the current rule glance and record `context_detail`, `duplicate_to_avoid`, and `local_voice_sample`.
3. Score the candidate and run Double-Check A.
4. Run `outbound-copy-gate.md`; generate internal micro, one-liner, and two-beat alternatives and choose the shortest passing version.
5. Use short native speech and high-frequency locally supported Reddit/internet markers across the session. Normally use one marker, never more than two; no percentage quota, forced slang, or copied phrasing.
6. Enter only the final draft, then use the controlled-input contract in `chrome-atomic-command-runtime.md`: resolve one fresh visible-DOM string node, separate focus and typing, and verify the exact live value through the focused control's open Shadow DOM before Double-Check B. A successful action acknowledgement or light-DOM-only empty result cannot advance to submit. Satisfy the canonical pacing clocks, then use a local wait, one click-only submit cell, and one separate targeted result read. Never combine typing, submit, or verification.
7. Persist the mutation result and measured text/read fields to `lane-state-checkpoint.md` before the next candidate.
8. Keep the resolved `comments.proactive_submit_gap_seconds_*`, then restart this full loop for the next item. Never prewrite a cluster.

Ordinary proactive comments use `comments.routine_word_cap` and remain mostly micro/fragment/one-liner. One two-beat exception within `voice.two_beat_word_range` may appear in a routine cluster only when the exact target earns it. Do not use routine compact paragraphs, polished two-sentence templates, generic praise, post summaries, repeated top comments, or product links outside explicit rule-compliant scope.

## Reading Without Voting

The action target and qualified-read target are separate hard completion conditions. If comments reach target first, continue lane-local qualified reading without publishing beyond the action target. If reading reaches target first, continue candidate discovery toward the remaining comment target. Deadline, explicit stop, or a current concrete blocker may produce a shortfall; candidate scarcity alone produces an interim checkpoint and later retry.

Qualified reading exists only to understand, score, and safely comment on candidates. Vote controls are out of scope even when visible. An explicit vote request belongs to `Reddit 浏览台` and never changes this lane's authorization.

## Report

Use the shared three-line receipt. Report verified comments/target, qualified reads/target, links, exact remainder, next verified wake, and the next lane-local plan. Do not include Upvote/Downvote counters.
