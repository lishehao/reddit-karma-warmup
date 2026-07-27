# Native Posts Playbook

Load only in the `posts` unit of the single `Reddit 运营台`, after the common current-unit runtime documents
from `SKILL.md`. Load `web-search-preflight.md` before Chrome candidate
discovery. Load `post-coverage-and-kpi.md` when the mission includes a
publication KPI; load `community-selection-funnel.md` only while widening a
candidate search; load `new-account-bootstrap.md` and the exact account-gate
row only for K0/K1; load `outbound-copy-gate.md` and
`publish-consistency.md` only before a draft/submission. Numeric defaults come
only from `operation-defaults.json`. This lane uses
`vote_policy=DISABLED_BY_LANE`: never load `browse-vote-playbook.md` or
inspect/click Upvote or Downvote.

## Post Eligibility

K0 is always `research_preflight_only` with `posts.k0_action_*`. K1 requires `main_post_unlock=passed`, the exact account-gate row, and same-day Chrome preflight; it applies `posts.k1_rolling_24h_cap`. Unknown, blocked, organization-deny, approval-required, or unmet rows are closed.

For one required post without an explicitly closed destination pool, run the
broad-to-deep funnel under `target_pool_policy=preferred_expandable`: assess
the configured reference target, create a post `research_brief` and
`query_plan`, run the built-in Web Search post query pack, and write an
`evidence_synthesis` before Chrome finalist narrowing. Use
`posts.narrowing_timebox_minutes`, then complete the configured number of live deep reads and candidate packets. The Web Search pack must include all three
base query-family minimums; query count alone does not unlock drafting. A
timebox, query count, reference count, candidate packet, or
rejected finalist is not publication completion. Honor
`target_pool_exact_and_closed=true` only when it is explicit user scope.

For every finalist, check current rules/sidebar, pinned moderator posts,
`New`/`Hot`/`Top Month`, submit fields, Flair/title/body mode,
account-age/Karma/history gates, megathread placement, external-link/product/
survey rules, same-subreddit history, and approval signals. If the live check
materially changes the target community, premise, duplicate risk, or factual
claim set, run the configured finalist-delta Web Search query and update
`evidence_synthesis` before drafting. Resolve hard compliance first, including
`posts.rules_eligibility_score_min` on live rules and eligibility; any mandatory
conflict immediately retargets. Only then check the mode's minimum content floor
and use the funnel's six-factor score as a secondary ranking signal.

## Discussion-First Default

Without another user angle, resolve `post_mode=native_discussion` and prefer a truthful beginner-readable community-memory question, observation, workflow friction, or tradeoff. It may sound simple but must not impersonate a novice, invent confusion, claim a personal mistake, or use deliberate factual errors. An ordinary discussion post does not require an artifact, project link, metric, or ownership claim.

Before drafting a question post, sample `posts.discussion_survivor_sample_target`
recent native discussion/question survivors when available and search the exact
topic plus close variants through both the Web Search query pack and live Reddit
surfaces. Retain only the premise and factual claims allowed by the evidence
synthesis's `draft_constraints`; remove or reframe every unsupported claim.
Reject FAQ, pinned, duplicate, one-answer, generic “any tips,” or
cross-subreddit template premises. This is the minimum content floor after
compliance, not a demand for maximal engagement potential.

Score discussion potential:

| Factor | Points |
|-|-:|
| Recognition density | 0-25 |
| Answer plurality | 0-20 |
| Story affordance | 0-20 |
| Low reply cost | 0-15 |
| Current native evidence | 0-10 |
| Novelty vs FAQ/recent posts | 0-10 |

After hard compliance passes, draft at `posts.discussion_score_min`, with recognition, plurality, and live evidence all nonzero. Scores from `posts.discussion_rewrite_score_min` up to that floor rewrite once; lower scores retarget. The score is a minimum anti-spam/fit floor and a secondary ranking signal; it never overrides eligibility or becomes a high-quality-only publishing gate. For `artifact` mode, use comparable current artifact/project survivors instead; never invent a discussion premise to avoid an artifact-evidence gap.

## Draft And Submit

Ordinary native posts are drafted directly from current subreddit context. Do not use GPT Inf or `loci-prepare-reddit-post` unless the user explicitly requests an external rewrite for that exact post.

1. Choose the exact subreddit, audience, premise, required format, and linked
   `research_brief_id` / `evidence_synthesis_id`.
2. Compare recent account posts and local survivors for duplicate community, angle, title, opening, and structure.
3. Draft the shortest title/body that supplies expected context and obeys the
   synthesis's `draft_constraints`; run the post section of
   `outbound-copy-gate.md` and Double-Check B. Any unsupported factual claim
   still present requires `rewrite` or `retarget`, never submission.
4. Persist `mutation_state=prepared` through the durable mission record, reselect the primary agent-owned tab, recheck account/target/live submit state, click Post once, and record verified or uncertain submission before another candidate.
5. If the post is awaiting moderator approval, delete/withdraw it immediately, retire that subreddit, record the result, and retarget without confirmation.

A failed candidate, pending-review cleanup, weak premise, completed timebox, or completed read target does not satisfy a required post action. Continue eligible finalist search while time remains. Maintain the conditional publication KPI and coverage packet evidence from `post-coverage-and-kpi.md`; verified publication normally completes a one-post action target.

## Research Reading Without Voting

The live deep-read target is a hard research objective; the coverage packet target is a second hard research objective. If publication succeeds before the read target, finish the remaining qualified survivor/rule research without another post. If research finishes first, continue toward the conditional publication target; do not silently zero it because coverage has finished.

External research samples are read only for rules, survivor patterns, audience fit, and post design. Vote controls are out of scope even when visible. An explicit vote request belongs only to the `browsing` unit and never changes this unit's authorization.

## Diversity And Report

For multiple posts, vary community cluster and native angle only when candidates pass; diversity never justifies a weak destination. Use the shared three-line receipt with publication/read progress, permalink, exact remainder, next mission wake, and next posts-unit plan. Do not include Upvote/Downvote counters.
