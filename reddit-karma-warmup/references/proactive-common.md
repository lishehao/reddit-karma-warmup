# Proactive Common Policy

Load in `Reddit 评论台` and `Reddit 发帖台` before the lane-specific playbook. This file owns account bands, community retirement, and the active destination pool. Numeric defaults come only from `operation-defaults.json`.

## Account Bands

Account age and Karma are observable routing signals, not global Reddit permission or safety guarantees. Use the lowest state supported by visible Karma, age, clean recent history, email/eligibility, current warnings, and exact subreddit gates.

| Tier | Observable state | Comment ceiling | Main-post window |
|-|-|-|-|
| `K0 New` | `<50` combined Karma; use `fresh_bootstrap` when `<48h`, blank, unknown, or visibility is uncertain | up to `10/hour`; `60/day` only by explicit high-volume request | locked at `0` |
| `K1 Growing` | `50-199` combined Karma, `>=7d`, clean recent state | up to `16/hour` after explicit override | after unlock, max `1/24h` |
| `K2 Established` | `>=200` combined Karma, `>=14d`, clean recent state | up to `20/hour` after explicit override | `0-3/day`, still rule-gated |

These account-band ceilings are policy limits stored here, not ordinary operation defaults. The user's latest explicit duration/count/intensity replaces ordinary defaults after one concise caution when materially above the suggested band. It never bypasses the organization denylist, live rules, account repair state, or `main_post_unlock`.

Use `new-account-bootstrap.md` for K0 bootstrap and unlock evidence. Use `risk-escalation.md` for current account-wide CAPTCHA, login, suspension, warning, or `429` handling.

## Community Retirement

A current native mod/Automod removal, new-item moderation lock, confirmed filter/invisibility, subreddit ban, invalidating parent deletion, or explicit community warning retires that exact subreddit for relevant outward actions. Record evidence, notify the user once in the affected lane, and continue elsewhere without confirmation or account-wide slowdown.

Multiple retired communities remain a set of community outcomes. Do not infer an account penalty, cooldown, lower tier, generic rate reduction, or mission stop unless Reddit separately exposes an active account-wide state. Reopen a retired subreddit only after an explicit user decision backed by a clear moderator/rule explanation.

## Active Pool Gate

Apply destination evidence in this order before any subreddit visit:

1. `organization-community-denylist.md`: hard organization-wide veto.
2. `community-action-routing-overrides.md`: exact action-level comment/post/product route.
3. filtered rows from `subreddit-profile-index.csv` and, only when necessary, `loci-subreddit-pool-v1.md`.
4. current live rules, pinned posts, recent surfaces, account eligibility, and submit controls.

A survivor post, missing rule text, traffic score, or historical archive never upgrades permission. `research_only`, downgraded, pending-review, retired, `A0`, and `No-go` rows are closed for comments, posts, votes, Join, Flair, and product mention. Public/pending expansion audits rank future preflight only.

For K0 bootstrap, use only low-friction `B/B+` rows with a clear ordinary participation path and no approval, local/community Karma, mandatory megathread, or rigid format gate. Prefer `New` and `Rising` for comments; use `Hot` and `Top` for language and survivor research.

Rule friction routes candidates:

- low: clear on-topic/civility rules and ordinary participation; use first
- medium: required Flair/title/format with a clear path; use sparingly
- high: approval, local/community Karma, mandatory megathread, narrow promotion windows, or subjective showcase enforcement; skip in default operations
