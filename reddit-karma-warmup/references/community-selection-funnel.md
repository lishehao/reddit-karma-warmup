# Community Selection Funnel

Use in `Reddit 分发台` for lane-specific reference routing, in `Reddit 评论台` for its initial community order, and in `Reddit 发帖台` for broad-to-deep post destination selection. This funnel ranks candidates; live rules and the organization denylist still control the exact action.

## Truthful Account Focus

Start from the confirmed `account_direction` and select one or two truthful pillars as `mission_identity_focus`. This is the current public-interest background of the account, not a fictional persona, biography, or hidden promotion device. Do not invent age, job, founder status, expertise, location, product use, or lived experience.

## Stage A: Distributor Reference Sweep

For every comment or post mission, evaluate up to `100` matching rows from `subreddit-profile-index.csv` before worker dispatch. When Python is available, use:

```text
scripts/query_subreddit_profile_index.py
  --direction <confirmed pillars + mission focus>
  --lane <comments|posts>
  --reference-sweep-limit 100
  --limit 20
  --include-traffic-probes
```

Without Python, perform the equivalent CSV/reference filter. Apply this order:

1. Remove `organization-community-denylist.md` matches, retired communities, `A0`, `No-go`, `research_only`, and any lane route marked `closed` or `research-only`.
2. Match `mission_identity_focus` against topic, audience, need, and format tags.
3. Prefer cached `>=5,000` weekly visitors; unknown/stale traffic remains a probe, never an action destination.
4. Apply exact `community-action-routing-overrides.md` rows before historical pool evidence.
5. Rank lower rule friction first: ordinary participation paths outrank approval, megathread, account/local-Karma, tight-format, topic-purity, and promotion gates.
6. For K0 post missions, join the exact subreddit row from `posting-account-gates-audit-2026-07-14.csv`. With Python, call `scripts/query_posting_account_gate.py --subreddit <name>`; otherwise perform an exact case-insensitive CSV lookup. Exclude `unknown`, `blocked`, and `organization_deny`; attach the remaining gate fields to the post shortlist. This audit filter is K0-specific and does not replace the action-route or live-rule gates.

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
- `reference_rows_assessed`: up to `100` direction/lane matches retained for ranking;
- `mission_identity_focus`;
- `comment_shortlist`: up to `20` eligible communities ordered by fit and rule friendliness; use fewer when fewer pass traffic/action gates;
- `post_reference_shortlist`: up to `20` eligible communities ordered by fit and rule friendliness; use fewer when fewer pass traffic/action gates;
- each row's route, traffic, friction band/reasons, matched tags, and next live gate;
- `traffic_probe_queue`, kept outside action targets until traffic passes.

The distributor places the relevant shortlist in the lane mission. It does not open Reddit pages, mutate Reddit, or monitor worker results.

## Stage B: Comment Lane Use

The comment worker starts from `comment_shortlist`, favoring low-friction `B/B+` destinations aligned with `mission_identity_focus`. It still scores the exact live post and parent comment; a friendly subreddit row never makes a weak post commentable.

If the supplied shortlist produces too few passing live candidates, widen through other eligible reference rows in score order. Do not drift into unrelated communities merely to fill volume. Before each comment, retain the quick current-rule glance, full-context read, local-voice sample, and comment score gate from `proactive-playbook.md`.

## Stage C: Post Lane Deep Search

When the post mission requires one verified main post, set `post_selection_timebox=20-30m`, `reference_rows_assessed_target=up_to_100`, and `live_deep_preflight_target=8-15`. The timebox is for initial selection work, not permission to stop without posting while authorized time and viable candidates remain.

Do not try to open 100 live subreddit pages in 30 minutes. Use the reference sweep for breadth, then use Chrome for depth:

1. Take the highest-ranked `12-20` post reference candidates. For K0, first remove every candidate without a completed account-gate audit row.
2. Deep-preflight the best `8-15` with current subreddit home/About/rules, pinned mod posts, `New`, `Hot`, `Top Month`, submit fields, account/Karma/flair requirements, posting placement, and recent same-angle repetition. A `no_public_gate_found` audit row still needs this same-day check because hidden AutoModerator gates remain possible.
3. Search the exact proposed topic and close variants in each finalist.
4. Draft only after one subreddit + audience + angle passes the live post gate.
5. If a candidate fails, immediately retarget to the next ranked candidate. Continue until one post is verified, the user stops, the operation deadline arrives, or a current concrete post-lane blocker survives recovery.

Rank each live finalist out of `100`:

| Factor | Points | Meaning |
|-|-:|-|
| Live rules and account eligibility | 0-25 | Current rules, Karma/age, flair, format, and placement clearly pass. |
| Audience and pain/interest fit | 0-20 | Members plausibly care about this exact topic. |
| Current demand and timing | 0-15 | Recent posts/comments show active interest without saturation. |
| Native format and survivor fit | 0-15 | The post shape matches current community norms without copying. |
| Originality and account coherence | 0-15 | Distinct from account/team history and consistent with the truthful identity focus. |
| Rule friendliness and moderation friction | 0-10 | Low special-placement, approval, or subjective promotion risk. |

`pass` requires `>=82`, at least `20/25` on live rules and eligibility, and no mandatory conflict. Prefer the highest passing candidate, not the first merely acceptable community. If two candidates are within `3` points, prefer the lower-friction route and stronger account coherence.

## Completion Evidence

For a one-post mission, selection is progress and the verified post is completion. Track:

```text
reference_rows_assessed
live_communities_preflighted
finalist_scores
selected_subreddit + selected_angle
verified_post_permalink
remaining_post_target
```

Do not report the mission complete because 20-30 minutes elapsed, 100 rows were screened, or 15 live communities were checked. Those are search-depth signals. Completion remains the verified action target or a real terminal condition.
