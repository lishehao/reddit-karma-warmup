# Native Posts Playbook

Load only in `Reddit 发帖台`, together with `proactive-common.md`, `community-selection-funnel.md`, `new-account-bootstrap.md`, `posting-account-gates-audit-2026-07-14.csv`, `publish-consistency.md`, `outbound-copy-gate.md`, and the shared runtime pack. Numeric defaults come only from `operation-defaults.json`. This lane uses `vote_policy=DISABLED_BY_LANE`: never load `browse-vote-playbook.md` or inspect/click Upvote or Downvote.

## Post Eligibility

K0 is always `research_preflight_only` with `posts.k0_action_*`. K1 requires `main_post_unlock=passed`, the exact account-gate row, and same-day Chrome preflight; it applies `posts.k1_rolling_24h_cap`. Unknown, blocked, organization-deny, approval-required, or unmet rows are closed.

For one required post without an exact destination, run the broad-to-deep funnel: assess the configured reference target, use `posts.narrowing_timebox_minutes`, then complete the configured number of live deep reads. A timebox, reference count, or rejected finalist is not mission completion.

For every finalist, check current rules/sidebar, pinned moderator posts, `New`/`Hot`/`Top Month`, submit fields, Flair/title/body mode, account-age/Karma/history gates, megathread placement, external-link/product/survey rules, same-subreddit history, and approval signals. Use the funnel's six-factor score; require `posts.post_candidate_score_min`, including `posts.rules_eligibility_score_min` on live rules and eligibility.

## Discussion-First Default

Without another user angle, prefer a truthful beginner-readable community-memory question about a common mistake, misleading assumption, setup tradeoff, or delayed consequence. It may sound simple but must not impersonate a novice, invent confusion, claim a personal mistake, or use deliberate factual errors.

Before drafting a question post, sample `posts.discussion_survivor_sample_target` recent native discussion/question survivors when available and search the exact topic plus close variants. Reject FAQ, pinned, duplicate, one-answer, generic “any tips,” or cross-subreddit template premises.

Score discussion potential:

| Factor | Points |
|-|-:|
| Recognition density | 0-25 |
| Answer plurality | 0-20 |
| Story affordance | 0-20 |
| Low reply cost | 0-15 |
| Current native evidence | 0-10 |
| Novelty vs FAQ/recent posts | 0-10 |

Draft only at `posts.discussion_score_min`, with recognition, plurality, and live evidence all nonzero. Scores from `posts.discussion_rewrite_score_min` up to that gate rewrite once; lower scores retarget. The score predicts discussion potential and never overrides eligibility.

## Draft And Submit

Ordinary native posts are drafted directly from current subreddit context. Do not use GPT Inf or `loci-prepare-reddit-post` unless the user explicitly requests an external rewrite for that exact post.

1. Choose the exact subreddit, audience, premise, and required format.
2. Compare recent account posts and local survivors for duplicate community, angle, title, opening, and structure.
3. Draft the shortest title/body that supplies expected context; run the post section of `outbound-copy-gate.md` and Double-Check B.
4. Persist `mutation_state=prepared` through `lane-state-checkpoint.md`, reselect the dedicated tab, recheck account/target/live submit state, click Post once, and record verified or uncertain submission before another candidate.
5. If the post is awaiting moderator approval, delete/withdraw it immediately, retire that subreddit, record the result, and retarget without confirmation.

A failed candidate, pending-review cleanup, weak premise, completed timebox, or completed read target does not satisfy a required post action. Continue eligible finalist search while time remains. Verified publication normally completes a one-post action target.

## Research Reading Without Voting

The configured live deep-read target is a hard research objective. If publication succeeds before the read target, finish the remaining qualified survivor/rule research without another post. If research finishes first, continue toward the post target.

External research samples are read only for rules, survivor patterns, audience fit, and post design. Vote controls are out of scope even when visible. An explicit vote request belongs to `Reddit 浏览台` and never changes this lane's authorization.

## Diversity And Report

For multiple posts, vary community cluster and native angle only when candidates pass; diversity never justifies a weak destination. Use the shared three-line receipt with publication/read progress, permalink, exact remainder, next verified wake, and next post-lane plan. Do not include Upvote/Downvote counters.
