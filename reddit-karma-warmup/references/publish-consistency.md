# Publish Consistency And Double Check

Load before every outward comment, follow-up reply, or main post. This reference owns account-history comparison, community restriction routing, cross-action consistency, and the two required pre-publish checks.

## History Ledger

At session start, inspect the account's visible recent posts/comments and combine them with the current session log. Prefer the latest `20` outward actions or the visible last `7 days`, whichever is practical. Build once, refresh on resume, and append after every verified action.

Record:

```text
time | action_type | subreddit | community_cluster | target_url | angle
char_count | word_count | sentence_form | length_tier | why_this_length
opening_pattern | key_claim_or_identity_signal | permalink
```

Consistency means stable identity and facts, not repetitive wording. Never contradict prior claims about role, experience, location, product usage, or expertise. Do not invent missing facts.

## Eligible Community Order

Use this precedence for every destination: `organization-community-denylist.md` -> exact `community-action-routing-overrides.md` row -> historical `loci-subreddit-pool-v1.md` row -> current live rules/account state. A denylist match is terminal. An action override splits comment, main-post, and product-mention permission; never collapse them into one community tier. A downgraded or `research-only` override is closed for all outward interaction.

The expansion report `community-expansion-pending-review-2026-07-13.md` sits outside that permission chain. It may seed a future candidate name, but it cannot bypass or create an action override. Treat every expansion-only name as `closed_pending_live_review` until the current task independently verifies the full required live surface.

The newer public audit `community-action-expansion-public-audit-2026-07-13.md` also sits outside the permission chain. Public rules can prioritize which destination to preflight first, but no logged-in Chrome verification means no comment, post, vote, Join, or product permission is created.

`posting-account-gates-audit-2026-07-14.csv` is the account-age/Karma/participation-gate index for main-post routing. It is incomplete: use its exact status rather than assuming a blank number means no gate. K0 never publishes. For K1 main posts, `unknown`, `blocked`, and `organization_deny` are closed. `verified_numeric`, `verified_qualitative`, and `no_public_gate_found` only allow same-day live preflight; they never grant publication by themselves.

The archive is intentionally large. Read it progressively:

- known subreddit: use an anchored case-insensitive search for the exact row, such as `rg -ni '^\| r/Unity3D \|' loci-subreddit-pool-v1.md`, then read only that row plus the field header
- pool discovery: search by a narrow combination of tier, community type, pain, rule, or publish-surface terms; inspect only the matching rows and keep a small candidate set
- never read the complete archive into context merely to select one subreddit

Each row's `主要用户`, `痛点/反馈`, `版规/边界`, `可发内容`, `账号适配/备注`, and `近期信号/更新` are the routing evidence. Do not infer publish permission from pain relevance alone.

1. Exclude permanent denylist entries, then apply any exact action override before selecting from `B` or `B+` rows whose `版规/边界`, `可发内容`, and `账号适配/备注` support the intended action.
2. Prefer rows with ordinary native participation, no special build/link requirement, and low current moderation friction.
3. Deprioritize rows requiring special flair/megathread, minimum karma/age, strict on-topic proof, official build links, or narrow self-promo exceptions unless the action exactly fits.
4. Treat `A` as research-first. Use it only when the interaction is plainly natural, non-product, and no lower-restriction alternative serves the same purpose.
5. Exclude `A0` and `No-go` from comments, posts, votes, joins, flair, and warm-up.

The bundled row is historical evidence synced from the Feishu archive. Live Reddit state always tightens permission when stricter. A more permissive survivor or blank rules page does not loosen an override; loosening requires explicit current rule text plus a user-targeted decision.

Classify the candidate before discovery:

| Restriction | Signal | Default action |
|-|-|-|
| `low` | B/B+, ordinary native participation allowed, no special account gate | search first |
| `medium` | specific flair/title/megathread/no-link format but the current action can satisfy it | use only when fit is strong |
| `high` | strict on-topic proof, karma/age gate, narrow self-promo exception, sensitive/competitor context, or manual review uncertainty | avoid when a lower-restriction alternative exists |
| `closed` | A0/No-go, clear prohibition, moderator approval requirement, explicit ban on AI-generated posts/comments for Codex-written text, or a prior Loci removal/ban in this exact subreddit | no outward action |

Do not lower a row's restriction because its topic is attractive. If live rules are stricter than the bundled row, use the stricter live result.

## History Diversity

Before selecting a candidate:

- Prefer a subreddit different from the last `2` proactive outward actions when comparable candidates exist.
- Do not publish more than `2` consecutive comments in the same subreddit.
- Across a rolling `6` proactive actions, prefer at least `3` subreddits and `2` community clusters when the eligible pool supports it.
- Main posts: at most one per subreddit per `24h` by default; avoid the same cluster and angle in consecutive posts.
- Do not reuse the same opening pattern, joke, praise frame, or question template from the recent ledger.

These are diversity preferences, not permission to use a lower-quality or higher-risk community. A strong natural continuation can justify a repeat comment; record why.

## Double-Check A: Before Drafting

Run after opening the candidate and before writing text.

For comments/replies:

0. For every individual item in a proactive cluster, assign a new `per_comment_gate_id`; do not reuse another item's Check A, context, voice sample, intended length, or final draft.
1. Perform a quick rule glance for this exact action. Re-read the relevant row restriction and either the visible subreddit rule summary or a live rule snapshot captured in this task within the last `60 min`; name the one rule most likely to affect this comment. Entering a new subreddit, a missing/uncertain snapshot, or a changed sidebar requires reopening its current rules once. This is a brief comment check, not the full post preflight.
2. Read the full post/media, intended parent comment, and enough nearby replies to understand the actual point, local energy, and what has already been said. When available, inspect at least `3` nearby/top replies; when the thread is empty, sample recent native comments from the same subreddit.
3. Record one `context_detail` that the reply will react to, one `duplicate_to_avoid`, and `2-4` short local voice patterns or Reddit-native expressions observed on the current surface. Do not copy another user's sentence.
4. Confirm the target is visible, unlocked, current enough, and not sensitive or hostile.
5. Compare subreddit, cluster, angle, intended claim, and the last `10` measured comment/reply lengths with `history_ledger`.
6. Confirm the account can contribute without fake experience, product mention, or unsupported factual claims.

For main posts, also verify live home/about/rules, pinned posts, recent survivor patterns, karma/age, flair/title/megathread, link/self-promo rules, submit controls, same-subreddit history, and moderator-approval state. For a question/discussion angle, require the local `discussion_survivor_sample` and `discussion_potential_score`; never use a fabricated novice identity as the hook.

Decision: `pass_to_draft`, `retarget`, `recover_lane`, or `hard_user_repair`.

## Copy Consistency

Run `outbound-copy-gate.md` after Check A.

- Preserve a coherent voice: curious, practical, concise, praise-first when appropriate.
- Vary form based on context. Do not force every comment into two sentences or every post into the same question template.
- Compare the last `10` measured comment/reply entries. If the last `3` use the same tier or sentence form, reassess the next shape against the target's real information need and nearby style.
- Comments should remain mostly micro/fragment/one-liner; two-beat and compact paragraphs need a concrete reason.
- Variation is a quality check, not a random schedule: do not pad, truncate, or cycle tiers merely to make the ledger look different.
- Main-post length should follow recent native survivor posts and the amount of context the subreddit expects. Do not use one universal post length.
- Topic, facts, and persona stay consistent even when length and phrasing vary.
- Across a session, use Reddit-native shorthand, contractions, fragments, and discourse markers frequently when the sampled local style supports them. Never force slang into every reply or copy a fashionable phrase that changes the intended meaning.

## Double-Check B: Immediately Before Submit

Run after the final draft is entered and before clicking Reply/Post.

1. Confirm the intended Reddit account, target subreddit/URL, and action type.
2. Confirm the target is still visible/unlocked and no currently active warning, removal, captcha, or rate limit appeared.
3. Re-read the final text against the exact parent/post and current subreddit context.
4. Confirm truthfulness, on-topic fit, no prohibited promotion/link, and no contradiction with `history_ledger`; for a comment/reply, verify the final text visibly uses the recorded `context_detail` and does not repeat `duplicate_to_avoid`.
5. Compute the final draft's `char_count`, `word_count`, `sentence_form`, and `length_tier`; confirm its length, opening, rhythm, subreddit, cluster, and angle are not needlessly repeating recent actions.
   For an ordinary proactive cluster item, default to `<=25` English words. A `26-45` word two-beat reply requires the recorded depth exception and no other item in that cluster may consume another such exception; compact paragraphs are invalid for routine proactive clusters.
6. Confirm this exact action was not already submitted; after a Chrome reconnect, inspect profile/thread before any retry.
7. For posts, confirm title, flair, body/link mode, megathread placement, eligibility, and no moderator-approval requirement one final time.

Decision:

- `submit`: every check passes.
- `rewrite`: copy or length/history consistency fails; revise and rerun Check B.
- `retarget`: community, eligibility, history saturation, or live context fails; abandon draft and return to discovery.
- `recover_lane`: timed rate limit or temporary account/control state; preserve the mission, continue permitted work, and re-probe automatically.
- `hard_user_repair`: only a current state from `risk-escalation.md`'s user-repair allowlist. A clear rule prohibition for this target is `retarget`; unsafe/deceptive copy is abandoned or rewritten. Historical/cleared evidence never qualifies.

If removal/filter/lock/pending-approval evidence appears for an own action, apply `SUBREDDIT_RETIRED`, close that exact subreddit, and retarget. For pending approval, immediately delete/withdraw without asking and verify cleanup once; if its route is temporarily blocked, queue the exact permalink for automatic retry while all eligible work continues. Do not classify any of these as an account-wide failure without separate Reddit account-level evidence.

## Log

For every outward action, record:

```text
double_check_a | double_check_b | history_comparison | restriction_level
per_comment_gate_id | cluster_id | item_index | shortening_pass
rule_glance | context_detail | duplicate_to_avoid | local_voice_sample
char_count | word_count | sentence_form | length_tier | why_this_length
subreddit/cluster diversity result | verified permalink
```
