# Built-in Web Search Preflight

Load before any Chrome candidate discovery in `Reddit 评论台` or `Reddit 发帖台`.
Use the host's built-in Web Search, not a Chrome search page, for broad current
discovery. It is intentionally query-rich because parallel Web Search is much
faster than opening many candidate pages in Chrome. Its output narrows Chrome
work; it never proves live Reddit permission, account eligibility, composer
state, or mutation success.

## Mandatory Pipeline

The only research sequence is:

```text
research_brief -> query_plan -> purpose-labelled Web Search -> evidence_synthesis -> Chrome live gate
```

Web Search must produce a compact research artifact, not just a query count:

1. `research_brief`: state the decision question, target surface/audience,
   candidate angle, intended claims/questions, unknowns, research questions,
   likely publish risk, and stop condition. Keep it within the configured
   compact-bullet ceiling.
2. `query_plan`: map every query to one distinct `research_question_id`, family,
   and candidate/claim use. Wording variants of the same question do not count.
3. `evidence_synthesis`: connect results to a retain/retarget/abandon decision;
   list usable findings, counter-evidence, FAQ/saturation risk, unsupported
   claims to remove or reframe, draft constraints, and exact Chrome live gates.
4. `Chrome live gate`: open Reddit only after the synthesis says what must be
   verified live. Chrome remains the authority for rules, logged-in eligibility,
   target context, composer state, and mutation result.

If a brief, plan, or evidence synthesis is absent or only summarizes snippets,
block drafting and continue research. Query count alone never satisfies
preflight. Do not draft from snippets.

## Compact Records

Before querying, write one `research_brief` using every configured required
field. Then write one `query_plan` using every configured required field. The
shared `web_search_preflight` ledger is:

```text
web_search_item_id | research_brief_id | query_plan_id | lane | query_family
research_question_id | purpose | query | result_url | source_kind | source_date?
candidate_or_claim_use | queried_at | disposition
```

After the planned pack, write an `evidence_synthesis` with every configured
field:

```text
research_brief_id | evidence_synthesis_id | linked_web_search_item_ids
usable_findings | counter_evidence_or_objections | saturation_or_duplicate_risk
unsupported_or_forbidden_claims | candidate_decision | draft_constraints
chrome_live_gate_targets
```

`purpose` is one of `discovery`, `recent_discussion`, `premise_variant`,
`duplicate_risk`, or `fact_support`. Batch independent queries in one tool call
when supported. A no-result query is valid discovery evidence, not a permission
or action blocker by itself. Do not inflate a pack with wording duplicates.

## Comment Lane: Window Then Item

For every comment window, complete the brief, plan, and the configured
`cluster_discovery_query_min..cluster_discovery_query_cap` distinct queries.
Cover all configured window families:

1. `community_topic` — the exact community/topic;
2. `recent_discussion` — current related discussion or event context;
3. `contradiction_or_objection` — a competing answer, limitation, or reason not
   to make the intended point;
4. `language_or_event_signal` — current phrasing, terminology, or event signal.

Write the window synthesis before selecting threads worth opening. Use results
to choose candidates and set draft constraints, never to write from snippets.

Before **every individual comment**, run the configured
`per_comment_exact_query_min` query scoped to that subreddit, thread topic, and
intended angle. Record its `web_search_item_id` and update the item-level
`evidence_synthesis_id`. If the intended comment is substantive — a
recommendation, technical/product interpretation, external fact, or
current-event assertion — also run the configured
`substantive_item_objection_query_min` distinct objection or duplicate-risk
query. A simple context reaction need not manufacture a second query.

If a comment makes a time-sensitive external factual claim, collect the
configured `time_sensitive_claim_source_min` authoritative sources. Without
that support, remove the claim or reframe it as a question. Then open the exact
Reddit target in Chrome and read the post, relevant parent, nearby replies,
current rules, and live composer.

## Post Lane: Directed Pack And Finalist Delta

Before Chrome deep-preflight, complete the post brief, query plan, and the
configured `query_pack_min..query_pack_cap` pack. The three base families each
meet the configured minimum; an external-fact family is added only when the
post makes an external factual claim:

1. `community_topic_and_recent_discussion` — community vocabulary and current
   discussion;
2. `premise_and_close_variants` — the intended premise, alternatives, and
   audience framing;
3. `duplicate_and_faq_risk` — existing answers, repeated premises, and
   saturation;
4. `external_fact_or_primary_source_when_claimed` — primary/official support
   for a factual claim, with the configured minimum when used.

When family four does not apply, record `no_external_fact_claim`; do not invent
a fact to consume the quota. Spread the pack across plausible eligible
communities and angles. Preserve source date when exposed, and prioritize
primary/official sources for technical, policy, product, research, or news
claims.

Write the post evidence synthesis before Chrome narrowing; this is the
`synthesis_required_before_chrome_finalists` gate. Chrome then checks live rules,
pins, feeds, duplicates, account gates, flair/submit controls, and the final
target. If that live check materially changes the community, premise, or an
outward claim, run at least `finalist_delta_query_min` targeted delta query,
update the synthesis, and only then draft. This is one evidence update, not a
way to keep reopening rejected routes.

## Boundaries

- Web Search is mandatory for comment/post research, not for vote, presence,
  browsing-only, or Chrome-recovery lanes.
- It happens before drafting; factual support and any finalist delta happen
  before the final submit check.
- Do not use Web Search as a workaround for a broken Chrome control path, or as
  a route around current Reddit rules, logged-in gates, or composer state.
- Do not search for private data, credentials, or ways to evade Reddit limits.
- Expand only for a distinct community, premise, contradiction, factual
  uncertainty, or material live-finalist change; never pad a query pack.
