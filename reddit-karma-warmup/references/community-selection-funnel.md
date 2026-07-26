# Community Selection Funnel

Use in `Reddit 分发台` for lane-specific reference routing, in `Reddit 评论台` for its initial community order, and in `Reddit 发帖台` for broad-to-deep post destination selection. For posts, load `post-coverage-and-kpi.md` as the KPI and pool-policy authority. This funnel ranks candidates; live rules and the organization denylist still control the exact action.

## Truthful Account Focus

Start from the confirmed `account_direction` and select one or two truthful pillars as `mission_identity_focus`. This is the current public-interest background of the account, not a fictional persona, biography, or hidden promotion device. Do not invent age, job, founder status, expertise, location, product use, or lived experience.

## Stage A: Distributor Reference Sweep

For every comment or post mission, resolve the reference sweep from `community_selection.comment_reference_sweep_limit` or `posts.<intensity>.reference_sweep_target` before worker dispatch. When Python is available, use:

```text
scripts/query_subreddit_profile_index.py
  --direction <confirmed pillars + mission focus>
  --lane <comments|posts>
  --reference-sweep-limit <resolved reference sweep>
  --limit <resolved lane shortlist limit>
  --include-traffic-probes
```

Without Python, perform the equivalent CSV/reference filter. Apply this order:

1. Remove `organization-community-denylist.md` matches, retired communities, `A0`, `No-go`, `research_only`, and any lane route marked `closed` or `research-only`.
2. Match `mission_identity_focus` against topic, audience, need, and format tags.
3. Prefer cached traffic at or above `community_selection.traffic_floor_weekly_visitors`; unknown/stale traffic remains a probe, never an action destination.
4. Apply exact `community-action-routing-overrides.md` rows before historical pool evidence.
5. Rank lower rule friction first: ordinary participation paths outrank approval, megathread, account/local-Karma, tight-format, topic-purity, and promotion gates.
6. For K0/K1 post missions, join the exact subreddit row from `posting-account-gates-audit-2026-07-14.csv`. With Python, call `scripts/query_posting_account_gate.py --subreddit <name>`; otherwise perform an exact case-insensitive CSV lookup. Exclude `unknown`, `blocked`, and `organization_deny`; attach the remaining gate fields to the post shortlist. This audit filter does not replace the action-route or live-rule gates. K0 remains research-only even when a row is complete.

Score the reference row out of `100`:

| Factor | Points | Meaning |
|-|-:|-|
| Account and mission-focus fit | 0-25 | The community matches the account's truthful interest background and this mission. |
| Lane action route | 0-25 | The exact comment/post route is open enough to justify live preflight. |
| Stored rule friendliness | 0-20 | Ordinary participation path with few special gates. |
| Traffic and current activity | 0-15 | Cached weekly visitors/contributions show enough opportunity. |
| Native content-shape fit | 0-15 | The intended question, discussion, critique, or artifact matches stored formats. |

Reference evidence never publishes by itself. Output:

- `catalog_rows_scanned`: all indexed rows considered by the local filter;
- `reference_rows_assessed`: up to the resolved direction/lane reference sweep retained for ranking;
- `mission_identity_focus`;
- `comment_shortlist`: up to `community_selection.shortlist_limit` eligible communities ordered by fit and rule friendliness; use fewer when fewer pass traffic/action gates;
- `post_reference_shortlist`: up to `community_selection.post_shortlist_limit` eligible communities ordered by fit and rule friendliness; use fewer when fewer pass traffic/action gates;
- each row's route, traffic, friction band/reasons, matched tags, and next live gate;
- `traffic_probe_queue`, kept outside action targets until traffic passes.

The distributor places the relevant shortlist in the lane mission. It does not open Reddit pages, mutate Reddit, or monitor worker results.

## Stage B: Comment Lane Use

The comment worker starts from `comment_shortlist`, favoring low-friction `B/B+` destinations aligned with `mission_identity_focus`. It still scores the exact live post and parent comment; a friendly subreddit row never makes a weak post commentable.

If the supplied shortlist produces too few passing live candidates, widen through other eligible reference rows in score order. Do not drift into unrelated communities merely to fill volume. Before each comment, retain the quick current-rule glance, full-context read, local-voice sample, and comment score gate from `comments-playbook.md`.

## Stage C: Post Lane Deep Search

When the post mission requires one verified main post, resolve `post_selection_timebox` from `posts.narrowing_timebox_minutes`, `reference_rows_assessed_target` from `posts.<intensity>.reference_sweep_target`, `live_deep_preflight_target` from `community_selection.post_live_preflight_community_range`, and `candidate_packet_target` from `posts.candidate_packet_target`. The timebox is for initial selection work, not permission to stop without posting while authorized time and viable candidates remain.

Default to `target_pool_policy=preferred_expandable`: an initial shortlist is a starting order, not a closed list. Expand through the next action-eligible reference rows after a concrete rejection. Only a user-provided `target_pool_exact_and_closed=true` stops expansion; record that exhaustion as a blocker instead of converting the publication target to zero.

Do not turn the reference sweep into rapid live navigation. Use
cached/reference breadth, then the built-in Web Search post research pipeline
for current external and Reddit-indexed discovery, then use Chrome for depth:

1. Take the highest-ranked range from `community_selection.post_initial_candidate_range`. For K0/K1, first remove every candidate without a completed account-gate audit row.
2. Create the post `research_brief` and `query_plan`, then complete
   `web_search.posts.query_pack_min` or more purpose-labelled Web Search
   queries before narrowing. Meet the configured minimum for every base query
   family; use external-fact queries only when the proposed post actually makes
   an external factual claim. Batch independent queries when the tool supports
   it. Record query, result URL, source date when visible,
   `research_question_id`, and exact candidate/claim use; then write
   `evidence_synthesis` before selecting Chrome finalists. It must preserve
   claim support, contradictions/open uncertainty, FAQ/duplicate risk,
   discarded angles, and draft constraints.
3. Deep-preflight the configured `community_selection.post_live_preflight_community_range` with current subreddit home/About/rules, pinned mod posts, `New`, `Hot`, `Top Month`, submit fields, account/Karma/flair requirements, posting placement, and recent same-angle repetition. A `no_public_gate_found` audit row still needs this same-day check because hidden AutoModerator gates remain possible.
4. Search the exact proposed topic and close variants in each finalist on live Reddit; Web Search results do not replace this current duplicate check.
5. Build a candidate packet for every serious finalist. Attach the
   `research_brief_id`, `query_plan_id`, `evidence_synthesis_id`,
   supported-claim allowlist, unsupported claims removed/reframed, and Chrome
   live-gate targets. If the live check materially
   changes the finalist, premise, or factual claim, run the configured targeted
   finalist delta query and update the synthesis before drafting. First resolve
   hard compliance, then the minimum content floor; draft only after both pass.
   Do not let a high aggregate ranking score rescue a rules failure.
6. If a candidate fails, immediately retarget to the next ranked candidate. Continue until one post is verified, the user stops, the operation deadline arrives, or a current concrete post-lane blocker survives recovery.

### Compliance Gate Before Ranking

Before computing a ranking score, require every one of these facts to be positively evidenced: action route is open; current subreddit rules permit the exact content and format; account-age/Karma/history and current submit controls pass; required flair/title/body/megathread placement is known and satisfiable; no approval, self-promotion, external-link, or duplicate/recent-own-post conflict remains. A failure is `retarget`, not a lower score.

Then require the content floor: truthful premise, exact topical fit, native format, no spam, and no FAQ/recent duplicate. A compliant but generic, fabricated, or duplicate premise is rewritten or retargeted; it is not published just because it is technically allowed.

### Secondary Ranking Among Passing Candidates

Rank only live-compliant, content-floor-passing finalists out of `100`:

| Factor | Points | Meaning |
|-|-:|-|
| Live rules and account eligibility | 0-25 | Current rules, Karma/age, flair, format, and placement clearly pass. |
| Audience and pain/interest fit | 0-20 | Members plausibly care about this exact topic. |
| Current demand and timing | 0-15 | Recent posts/comments show active interest without saturation. |
| Native format and survivor fit | 0-15 | The post shape matches current community norms without copying. |
| Originality and account coherence | 0-15 | Distinct from account/team history and consistent with the truthful identity focus. |
| Rule friendliness and moderation friction | 0-10 | Low special-placement, approval, or subjective promotion risk. |

Both modes require at least `posts.rules_eligibility_score_min` on live rules and eligibility, no mandatory conflict, and their mode's content floor. No 100-point aggregate candidate score is a publication gate. Prefer the highest-ranked candidate only after the hard compliance and content-floor checks have passed. If two candidates are within `community_selection.near_tie_score_margin`, prefer the lower-friction route and stronger account coherence.

## Completion Evidence

For a one-post mission, selection is progress and the verified post is completion. Track:

```text
reference_rows_assessed
live_communities_preflighted
finalist_scores
candidate_packets + rejection_reasons
target_pool_policy + closed_pool_exhausted
selected_subreddit + selected_angle
verified_post_permalink
remaining_post_target
```

Do not report the mission complete because a configured timebox, reference sweep, or live-preflight range was exhausted. Those are search-depth signals. Completion remains the verified action target or a real terminal condition.
