# Shared Community Audit Pool

Load this reference only during `Reddit 启动台` bootstrap, catalog expansion,
or when interpreting an existing cache row. It governs public API audit data;
it does not govern Chrome browsing or any Reddit mutation.

## Identity And Ownership

`Reddit 社区审计服务` is a local script/service, not a user-visible Codex task,
not a lane, and not an account identity. The released Skill ships the script;
`Reddit 启动台` alone initializes/checks its local cache during install/preflight
before becoming `Reddit 分发台`. No operating lane creates the script, database,
or a second pool.

- The bootstrap alone may run `init`, `status`, or one read-only `refresh`.
- `Reddit 分发台` and every lane only read completed cache snapshots. They never
  call a provider, wait for a refresh lock, or communicate with another lane.
- The service has no Chrome tab, cookies, OAuth account identity for publishing,
  task registry, Heartbeat, or Reddit write endpoint.
- One lock and one `rate_state` row per provider/OAuth client make the pool the
  one local writer. A busy lock returns `REFRESH_IN_PROGRESS`; readers keep
  the last completed snapshot and label its freshness honestly.

The default root is
`${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/community-audit-pool/`. It is
user runtime data outside the managed Skill folder and survives upgrades.

## Allowed Data And Providers

Default provider: `official_reddit` over an explicitly configured OAuth bearer
token and truthful User-Agent. It may use GET-only public endpoints for
community metadata, `about/rules`, sidebar, sticky pointers, and at most the
configured number of hot-item pointers. It never calls submit/comment/vote,
never requests an account-specific endpoint, and never treats API output as a
logged-in account gate.

TikHub is optional enrichment only after a field-level calibration against the
official provider. It may add discovery, structural settings, and small public
trend pointers. It cannot overwrite the official rule snapshot, elevate an
evidence level, authorize a post/comment, or supply an account-specific gate.
Missing TikHub credentials or budget is normal and does not degrade the
official/cache path.

Store only what is required for the reference table. Rule text and public
community metadata are versioned with a hash and expiry. Hot samples retain
only ID, permalink, timestamp, score, and comment count; do not persist post
body, comments, profile history, or a bulk content corpus. Expire stale sample
data according to `operation-defaults.json`.

## Rate And Refresh Contract

The published OAuth baseline is an upper bound, not a target. The configured
operating QPM stays lower; runtime 429/retry instructions and returned rate
signals always win. Do not create multiple clients, IP paths, or pool writers
to multiply capacity. A refresh uses an exclusive local lock and a per-provider
rate counter; if unavailable, it yields without retry loops.

Use:

```text
python scripts/community_audit_pool.py init
python scripts/community_audit_pool.py status
python scripts/community_audit_pool.py refresh --subreddit r/example
python scripts/community_audit_pool.py export --output <reference.csv>
```

`refresh` requires both configured official API credentials and an explicit
subreddit list. It is never a lane fallback for Chrome failure. It does not run
automatically merely because a worker wants a fresher row.

## Evidence Levels And Chrome Boundary

| Evidence | Meaning | Can it publish? |
| --- | --- | --- |
| `catalog_only` | discovery/tag row | no |
| `public_rules` | completed official rule snapshot | no |
| `public_rules_enriched` | official snapshot plus TikHub enrichment | no |
| `live_rules` | current visible Chrome clarification plus current route | no, still account-specific checks remain |
| `action_verified` | live Chrome account, submit controls, placement, and mutation verification | only when every lane gate passes |

Actual content browsing remains Chrome-only. A lane opens visible Reddit pages,
reads the post plus needed context/comments, and records qualified-read evidence
before moving on. API item pointers only tell Chrome where a small number of
public current items may be worth opening. Never use timing randomness, hidden
DOM extraction, cursor simulation, fingerprint changes, or automated infinite
scrolling to imitate a human.

All interactive UI is Chrome-only too: title/body/composer entry, flair or tag
selection, rule acknowledgement, preview, submit, vote, join, and result
verification. The audit service never fills a form or replaces a visible
account/session check.

For an action candidate, Chrome still confirms the current submit UI, required
flair, exact placement/megathread, duplicate and recent-own-post risk,
account/community gates, hidden AutoModerator uncertainty, and the result of
the actual mutation.
