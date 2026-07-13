# Subreddit Catalog And Tag Taxonomy

Use this reference when resolving an account direction, expanding the community catalog, or querying `subreddit-profile-index.csv`. The catalog is a discovery index, not posting permission.

## Two-Layer Model

1. `subreddit-profile-index.csv`: lightweight discovery metadata for hundreds of communities. It owns tags, traffic snapshots, broad fit, and evidence status.
2. `subreddit-catalog-expansion-2026-07-14.csv` plus `reddit-community-search-snapshot-2026-07-14.json`: curated traffic-qualified discovery rows and the read-only Reddit search snapshot that produced them. These rows are `research_only` by default.
3. `loci-subreddit-pool-v1.md` plus `community-action-routing-overrides.md`: detailed pain/rules evidence and action routing. Current live Reddit rules and account state remain final.

Never promote a catalog-only row directly into comment or post scoring. A match only identifies which exact rule rows and live pages to inspect next.

## Catalog Fields

| Field | Meaning |
|-|-|
| `subreddit` | Canonical `r/name` key. |
| `tier` | Existing B/B+/A/A0/No-go research tier when known. |
| `community_type` | Human-readable source category. |
| `topic_tags` | Product, gaming, social, place, creative, AI, developer, entertainment, and related subject tags. |
| `audience_tags` | Builders, students, gamers, creators, travelers, photographers, friends/couples, and similar audience tags. |
| `need_tags` | Repeated needs such as feedback, discovery, lightweight social contact, co-creation, identity, place memory, onboarding, distribution, and technical help. |
| `format_tags` | Native surfaces such as comment, question, text, image, video, critique, showcase, or megathread. |
| `risk_tags` | Promotion, survey, AI, privacy, minors, approval, megathread, or account-gate signals. These are retrieval warnings, not complete rules. |
| `comment_route` / `post_route` / `product_route` | Cached action-level direction. Exact overrides and live rules still win. |
| `launcher_state` | `candidate`, `research_only`, or `closed`. Only `candidate` may enter launcher shortlisting. |
| `weekly_visitors` | Reddit's visible weekly visitor metric when captured. |
| `weekly_contributions` | Reddit's visible weekly post/comment contribution metric when captured. |
| `traffic_checked_at` | Timestamp for the activity snapshot. |
| `traffic_state` | `pass`, `below_floor`, `unknown`, or `stale`. |
| `evidence_level` | `catalog_only`, `traffic_verified`, `historical_pool`, `public_rules`, `live_rules`, `action_verified`, `retired`, or `deny`. |

## Traffic Gate

The default discovery floor is `5,000` weekly visitors. Reddit defines weekly visitors as users visiting in the past seven days based on a rolling 28-day average; bots and anonymous native-app browsing are excluded. Weekly contributions count non-removed posts and comments in the past seven days.

- `weekly_visitors >= 5000` and snapshot age `<=30d`: traffic `pass`.
- `weekly_visitors < 5000`: exclude from the packaged operating catalog. Do not spend rule-audit time on it unless the user explicitly targets it.
- missing or older than `30d`: `unknown` or `stale`; it may enter a bounded traffic-probe queue but not the final operating shortlist.
- Weekly contributions are a secondary quality signal. Prefer `>=100`; lower values may still support research but should not outrank an equally relevant active community.

Official metric reference: https://support.reddithelp.com/hc/en-us/articles/41043361207316-Understanding-weekly-visitors-and-contributions-on-Reddit

## Tag Families

Keep tags canonical and reusable. Do not create a new synonym when one of these fits.

- Topics: `product_app`, `startup_builder`, `developer`, `mobile`, `ios`, `android`, `web`, `ai`, `3d`, `ar_xr`, `gaming`, `virtual_world`, `ugc`, `social_relationship`, `youth_campus`, `place`, `travel_outdoor`, `creative`, `visual_art`, `photography_video`, `productivity_learning`, `entertainment_media`.
- Audiences: `indie_builder`, `developer`, `early_tester`, `student`, `young_adult`, `mobile_user`, `web_user`, `gamer`, `world_builder`, `spatial_user`, `creator`, `artist_designer`, `photographer_video_creator`, `traveler_outdoor`, `place_explorer`, `social_participant`, `friends_couples`, `media_fan`, `ai_user`.
- Needs: `feedback_testing`, `onboarding_ux`, `technical_help`, `discovery`, `lightweight_social`, `co_creation`, `identity_avatar`, `place_memory`, `creator_distribution`, `privacy_safety`, `learning_productivity`, `entertainment_discussion`.
- Risks: `promotion_restricted`, `survey_restricted`, `ai_restricted`, `privacy_sensitive`, `minors_sensitive`, `approval_gate`, `megathread_gate`, `account_gate`, `topic_purity`, `competitor_context`.

## Launcher Retrieval

After the visible account's direction is confirmed:

1. Map its `3-5` pillars to canonical tags.
2. Query `subreddit-profile-index.csv` with `scripts/query_subreddit_profile_index.py`.
3. Exclude `closed`, `research_only`, permanent denylist, retired destinations, and cached traffic below `5,000`.
4. Return at most `12` candidates: up to `6` direct matches, `3` adjacent matches, and `3` bounded exploration matches. Unknown/stale traffic rows are labeled `traffic_probe`, never final recommendations.
5. Put the shortlist and probe queue into worker handoffs. Each worker still checks the exact action override and current live rules before drafting or acting.

Do not show hundreds of rows to the user. The setup response should summarize the resolved pillars and a short candidate cluster only.

## Expansion Standard

Target catalog size is an outcome, not a quota. Expand in batches across product/mobile, gaming/worlds, youth/campus, social/relationships, creative/visual, place/travel/outdoor, entertainment/media, productivity/learning, AI/companions, and developer/tooling.

Every admitted row needs:

- canonical subreddit name and accessible public community page;
- current weekly visitors at or above `5,000`;
- at least one topic, audience, and need tag;
- traffic timestamp and evidence source;
- evidence level and broad launcher state;
- duplicate, redirect, private, quarantined, and organization-deny checks.

Catalog-only expansion does not require a full rule audit. Run detailed public/live rule audits only for high-fit rows selected repeatedly by account-direction queries. This keeps a `400-500` discovery catalog maintainable without pretending all rows are publication-ready.

The 2026-07-14 batch adds broad youth/social, gaming, film/TV, anime, music, photography, art/design, travel/place, productivity, AI-companion, mobile-app, and spatial/3D coverage. Keyword false positives, communities below `5,000` weekly visitors, and obviously inactive or irrelevant matches were excluded before merge. Passing this batch means only that traffic and broad relevance were observed; it does not mean the community permits comments, posts, product mention, or coordinated account activity.
