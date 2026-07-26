# Built-in Web Search Preflight

Load before any Chrome candidate discovery in `Reddit 评论台` or `Reddit 发帖台`.
Use the host's built-in Web Search, not a Chrome search page, for broad current
discovery. It is intentionally query-rich because parallel Web Search is much
faster than opening many candidate pages in Chrome. Its output narrows the
Chrome work; it never proves live Reddit permission, account eligibility,
composer state, or mutation success.

## Shared ledger

Write one compact `web_search_preflight` record before Chrome narrowing:

```text
web_search_item_id | lane | purpose | query | result_url | source_kind | source_date?
candidate_or_claim_use | queried_at | disposition
```

`purpose` is one of `discovery`, `recent_discussion`, `premise_variant`,
`duplicate_risk`, or `fact_support`. Every query must have a stated use; do not
inflate count with wording duplicates. Batch independent queries in one tool
call when supported. A no-result query is valid evidence of discovery effort,
not an action blocker by itself.

## Comment lane: broad window, exact item

For every comment window, run `web_search.comments.cluster_discovery_query_min`
to `cluster_discovery_query_cap` distinct queries (default 4–10). Cover at
least: the exact community/topic, current related discussions, a competing
answer/objection, and a recent phrasing or event signal. Use results to choose
threads worth opening, not to draft from snippets.

Before **every individual comment**, run at least
`per_comment_exact_query_min` (default 1) additional query scoped to that
subreddit, thread topic, and intended angle. Record its `web_search_item_id` in
the per-item gate. Then open the exact Reddit target in Chrome and read the
post, relevant parent, nearby replies, current rules, and live composer.

If the comment makes a time-sensitive external factual claim, collect at least
`time_sensitive_claim_source_min` (default 2) authoritative sources through
Web Search. If that support is absent, remove the claim or reframe it as a
question; never turn a search snippet into an asserted fact.

## Post lane: large directed query pack

Before Chrome deep-preflight, run the post pack with at least
`web_search.posts.query_pack_min` queries (default 12), target 18, cap 30.
Use the first three query families, plus the fourth whenever the post makes an
external factual claim:

1. community/topic and recent discussion;
2. the premise plus close variants;
3. FAQ, duplicate, and saturation risk;
4. external factual or primary-source support when the post makes such claims.

When the fourth family does not apply, record `no_external_fact_claim` rather
than inventing an unnecessary source or query.

Spread the pack across plausible eligible communities and angles. Examples may
use `site:reddit.com/r/<subreddit>`, current topic terms, dates/recency, and
contrasting wording, but must not treat indexed results as current rule or
submission evidence. Preserve the source date when exposed and prioritize
primary/official sources for technical, policy, product, research, or news
claims.

After the pack, use Chrome only on the narrowed finalists. Recheck live Reddit
rules, pins, current feeds, duplicates, account gates, flair/submit controls,
and the final exact target. A web result can prioritize a finalist; it cannot
open a closed route or bypass a Reddit gate.

## Boundaries

- Web Search is mandatory for comment/post research, not for vote, presence,
  browsing-only, or Chrome-recovery lanes.
- It must happen before drafting, and a time-sensitive fact check must happen
  before the final submit check.
- Do not use Web Search as a workaround for a broken Chrome control path.
- Do not search for private data, credentials, or ways to evade Reddit limits.
- Do not pad a query pack after the evidence is already decisive; expand only
  for a distinct community, premise, contradiction, or factual uncertainty.
