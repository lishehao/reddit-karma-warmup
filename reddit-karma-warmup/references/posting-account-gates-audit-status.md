# Posting Account Gates Audit Status

Use this summary when answering coverage questions. Query the companion CSV by exact subreddit for any main-post decision.

When Python is available, use `scripts/query_posting_account_gate.py --summary` or `--subreddit <name>`. Without Python, search the CSV by exact subreddit name.

## Snapshot

- checked at: `2026-07-14 19:20 Asia/Shanghai`
- catalog rows: `254`
- ordinary communities: `252`
- completed ordinary gate reviews: `22/252` (`8.73%`)
- `verified_numeric`: `5`
- `verified_qualitative`: `10`
- `no_public_gate_found`: `7`
- `unknown`: `229`
- `blocked`: `1`
- `organization_deny`: `2`

The audit is not complete. The CSV is authoritative for row-level status.

## Interpretation

- `verified_numeric`: at least one public numeric account gate was confirmed. Meet every recorded number and every nonnumeric condition, then repeat the same-day live preflight.
- `verified_qualitative`: a participation, approval, placement, history, or content gate was confirmed without a complete numeric threshold. This is not unrestricted access.
- `no_public_gate_found`: checked public surfaces exposed no account number. Hidden AutoModerator or submit-time gates may still exist.
- `unknown`: current evidence is incomplete. It is closed for K0 main posts.
- `blocked`: the current participation surface said the account could not participate. It is closed.
- `organization_deny`: never visit or act unless the user explicitly removes the deny entry.

## Confirmed Numeric Examples

| Subreddit | Public gate captured | Important limitation |
|-|-|-|
| `r/AdultGamers` | account `>=30d`, `>=20` karma | route is closed; 20 karma type is not specified |
| `r/Android` | account `>=90d` | developer posting history is also required; route remains conditional |
| `r/animation` | `<30d` plus `<15` total karma triggers manual review | joint review trigger, not two independent sufficient thresholds |
| `r/Anime` | `>=10` comment karma from `r/anime` | community-specific participation gate |
| `r/droidappshowcase` | account `>=1d`, `>=2` combined karma, verified email | Android-only plus format/frequency rules |

No completed row currently exposes a standalone post-karma minimum or a generic community-karma minimum. Blank fields mean not publicly confirmed, not zero.

## K0/K1 Routing Rule

For a K0/K1 main-post shortlist:

1. require at least K1 plus `main_post_unlock=passed` (`>=50` combined Karma, `>=7d` account age, and the required visible participation/health evidence);
2. look up the exact CSV row;
3. exclude `unknown`, `blocked`, and `organization_deny`;
4. satisfy every captured numeric and qualitative gate;
5. rerun same-day Chrome rules, pinned, feeds, submit, and account-control checks;
6. publish at most once per rolling `24h` while K1; K0 never publishes.

A completed row ranks a destination for live preflight. It never grants publication by itself.
