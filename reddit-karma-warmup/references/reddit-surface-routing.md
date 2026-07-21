# Reddit Surface Routing

This is the single authority for choosing among Old Reddit and current Reddit
web surfaces. Load it in launcher preflight and every execution lane. The goal
is stable, auditable work on the same logged-in Chrome profile, not forcing an
account-wide preference or treating one host as permanently superior.

## Routing Principle

Use `old_first_modern_fallback` for ordinary text-community work:

- Prefer `https://old.reddit.com/` for subreddit listings (`new`, `hot`, and
  `top`), post text, comment trees and context, visible sidebar/rules/wiki,
  simple text comments/replies, simple link/text submit, and profile
  post/comment history.
- Use current Reddit (`https://www.reddit.com/`, or another current native
  Reddit route already exposed by the live UI) when the required capability is
  absent or materially broken on Old Reddit: gallery/video/media rendering,
  Chat, account settings, modern moderation surfaces, complex Flair/media
  fields, new post types, or a composer that Old Reddit cannot complete.
- Treat `sh.reddit.com` only as an observed current native Reddit route, never
  as a guaranteed alias or universal fallback.
- Never rewrite every Reddit URL blindly, change the account preference, clear
  cookies, switch browsers/profiles, or use a logged-out surface as recovery.

Old Reddit is the starting surface, not an availability assumption. If its
equivalent route is blocked, missing, redirecting, or unreadable, try one
semantically equivalent current Reddit route. A current Reddit route may fall
back once to Old Reddit when the required capability exists there. After the
bounded alternate fails, classify the route and retarget or enter the existing
Chrome recovery state; do not bounce between hosts.

## Capability Matrix

| Intent | Preferred surface | Bounded fallback |
|-|-|-|
| Listing scan, post text, comment context, profile history | `old_reddit` | equivalent current Reddit route |
| Rules/sidebar/wiki when Old exposes them | `old_reddit` | current About/Rules/wiki route |
| Simple comment or reply | `old_reddit` | current visible composer |
| Simple text/link submit | `old_reddit` | current composer when required fields are unavailable |
| Gallery, video, rich media, Chat, settings, complex Flair/media/new post type | `modern_reddit` | Old only when it can satisfy the exact capability |
| Notifications/inbox | use the first native route that is readable and complete for the required sweep | one semantically equivalent native route |

Do not confuse visual simplicity with permission. Community rules, account
gates, action authority, and current warning state remain unchanged across
surfaces.

## Canonical Target Identity

Hosts are views, not different candidates. Derive one `canonical_target_key`
from the stable Reddit identity available in the permalink/fullname:

- post: `t3_<post_id>` or `/comments/<post_id>/...`
- comment/reply: `t1_<comment_id>` or the permalink comment ID
- subreddit/listing: normalized subreddit plus listing/sort
- notification/profile item: its stable permalink/fullname when available

Normalize `old.reddit.com`, `www.reddit.com`, and an observed current native
Reddit host to that same key. A surface switch never creates a new qualified
read, candidate, comment opportunity, vote opportunity, or post target. Preserve
the original dwell/read measurements and count the canonical target at most
once.

## Surface Switch Transaction

1. Record `surface_requested`, `surface_used`, `surface_reason`,
   `canonical_target_key`, and current mutation phase.
2. Confirm there is no `submission_uncertain` or mutation whose click/send may
   already have been issued.
3. Navigate the same lane-owned primary tab to one semantically equivalent
   native route. Use a new auxiliary tab only when the role playbook genuinely
   requires simultaneous read-only context; close it in the same turn.
4. Obtain a fresh page-state proof and verify the same canonical target,
   expected account, and required visible capability.
5. Record `fallback_from`, `fallback_reason`, and `route_result` as
   `readable`, `capability_missing`, `route_failed`, or `recovery_required`.

One semantic target gets at most one cross-surface fallback per wake. A changed
host does not reset the same-URL retry budget, recovery fingerprint, pacing
clock, history deduplication, or action cap.

## Mutation Invariants

Before every vote, comment, reply, or post, persist:

```text
surface_used
canonical_target_key
mutation_key
mutation_phase
submission_state
```

- `mutation_key` is independent of host. The same target/action/text or vote
  direction has one key on every surface.
- If click/send may have happened and acknowledgement is unknown, record the
  existing uncertain state, quarantine the exact mutation key, and never switch
  surfaces to retry or manufacture verification.
- An already selected vote on either surface is `existing_vote`; never toggle
  it or click again on the other surface.
- A posted comment/reply/post discovered on either surface satisfies the same
  mutation key once. Do not submit or count it again.
- A surface-specific hidden/ambiguous control is a reason to skip or perform the
  one safe pre-mutation fallback, not permission to use a broad selector or
  hidden DOM.

## Required Evidence

Each routed candidate or action records at minimum:

```text
surface_requested
surface_used
surface_reason
canonical_target_key
fallback_from
fallback_reason
route_result
```

Keep absent fallback fields null. Report surface failures as route evidence,
not account enforcement, unless the live page independently shows an account
warning, login mismatch, CAPTCHA, lock, or rate limit.
