# Proactive Comments Playbook

Load only in the `comments` unit of the single `Reddit 运营台`. Follow the progressive load map in `SKILL.md`:
load common runtime documents for the current unit, then load this playbook.
Load `web-search-preflight.md` before Chrome candidate discovery. Load
`outbound-copy-gate.md`, `reddit-us-voice-patterns.md`, and
`publish-consistency.md` only after one exact comment candidate has passed
context/rule checks. Numeric defaults come only from `operation-defaults.json`.
This lane uses `vote_policy=DISABLED_BY_LANE`: never load
`browse-vote-playbook.md` or inspect/click Upvote or Downvote.

## Mission And High-Volume Mode

Resolve one exact action target, cap, and qualified-read target from `operation-defaults.json` or the latest user override. A count of `2+` uses clustered windows with at least two verified comments per completed window. A user request for exactly one total comment is the only count-based single-action exception.

Daily `60` mode is not default. Enable it only for an explicit roughly-60/day request or explicit high intensity for at least `6h`. Keep at least six eligible communities and three clusters when available, no more than five proactive comments in one subreddit per `24h`, and no catch-up burst. The target never lowers candidate, copy, rule, or pacing gates.

## Candidate Gate

Before opening candidate threads in Chrome, run the comment-window built-in Web
Search pipeline: `research_brief`, labelled `query_plan`, all configured window
families, and `evidence_synthesis`. It must state useful current signals,
objections/duplicate risks, discarded angles, and draft constraints. Before
every individual comment, run its separate exact query, record the returned
`web_search_item_id`, and update the item-level synthesis; a cluster never
shares one item-level query or synthesis. A substantive recommendation,
technical/product interpretation, or external/current factual angle also needs
the configured objection/duplicate-risk query before draft. Search is the fast
discovery layer, not proof that Reddit still permits the action. A no-result
query is valid discovery evidence for a thread-native response, but Chrome must
then establish the live context, rules, and composer state.

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

1. Assign a fresh `per_comment_gate_id`, preserve its `research_brief_id` and
   `query_plan_id`, run the required exact Web Search query, update the
   `evidence_synthesis_id`, and reopen the exact target. For a substantive
   angle, also record the required objection/duplicate-risk query.
2. Run the current rule glance and record `context_detail`, `duplicate_to_avoid`,
   `local_voice_sample`, `web_search_item_id`, `evidence_synthesis_id`, any
   `unsupported_or_forbidden_claims` removed or reframed, and the current
   `draft_constraints`.
3. Score the candidate and run Double-Check A.
4. Run `outbound-copy-gate.md`; generate internal micro, one-liner, and two-beat alternatives and choose the shortest passing version.
5. Use short native speech and high-frequency locally supported Reddit/internet markers across the session. Normally use one marker, never more than two; no percentage quota, forced slang, or copied phrasing.
6. Enter only the final draft, then use the controlled-input contract in `chrome-atomic-command-runtime.md`: resolve one fresh visible-DOM string node, separate focus and typing, and verify the exact live value through the focused control's open Shadow DOM before Double-Check B. A successful action acknowledgement or light-DOM-only empty result cannot advance to submit. Satisfy the canonical pacing clocks, then use a local wait, one click-only submit cell, and one separate targeted result read. Never combine typing, submit, or verification.
7. Persist the mutation result and measured text/read fields to the durable mission record before the next candidate.
8. Keep the resolved `comments.proactive_submit_gap_seconds_*`, then restart this full loop for the next item. Never prewrite a cluster.

Ordinary proactive comments use `comments.routine_word_cap` and remain mostly micro/fragment/one-liner. One two-beat exception within `voice.two_beat_word_range` may appear in a routine cluster only when the exact target earns it. Do not use routine compact paragraphs, polished two-sentence templates, generic praise, post summaries, repeated top comments, or product links outside explicit rule-compliant scope.

## Reading Without Voting

The action target and qualified-read target are separate hard completion conditions. If comments reach target first, continue unit-local qualified reading without publishing beyond the action target. If reading reaches target first, continue candidate discovery toward the remaining comment target. Deadline, explicit stop, or a current concrete blocker may produce a shortfall; candidate scarcity alone produces an interim checkpoint and later retry.

Qualified reading exists only to understand, score, and safely comment on candidates. Vote controls are out of scope even when visible. An explicit vote request belongs only to the `browsing` unit and never changes this unit's authorization.

## Report

Use the shared three-line receipt. Report verified comments/target, qualified reads/target, links, exact remainder, the next mission-level wake, and the next unit-local plan. Do not include Upvote/Downvote counters.
