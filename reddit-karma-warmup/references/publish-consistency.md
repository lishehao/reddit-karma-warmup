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

Use `loci-subreddit-pool-v1.md` as the default routing source when the user gives no exclusive pool.

1. Start with `B` or `B+` rows whose `版规/边界`, `可发内容`, and `账号适配/备注` support the intended action.
2. Prefer rows with ordinary native participation, no special build/link requirement, and low current moderation friction.
3. Deprioritize rows requiring special flair/megathread, minimum karma/age, strict on-topic proof, official build links, or narrow self-promo exceptions unless the action exactly fits.
4. Treat `A` as research-first. Use it only when the interaction is plainly natural, non-product, and no lower-restriction alternative serves the same purpose.
5. Exclude `A0` and `No-go` from comments, posts, votes, joins, flair, and warm-up.

The bundled row is historical evidence. Live Reddit state wins when it conflicts with the reference.

Classify the candidate before discovery:

| Restriction | Signal | Default action |
|-|-|-|
| `low` | B/B+, ordinary native participation allowed, no special account gate | search first |
| `medium` | specific flair/title/megathread/no-link format but the current action can satisfy it | use only when fit is strong |
| `high` | strict on-topic proof, karma/age gate, narrow self-promo exception, sensitive/competitor context, high removal history, or manual review uncertainty | avoid when a lower-restriction alternative exists |
| `closed` | A0/No-go, clear prohibition, moderator approval requirement, or explicit ban on AI-generated posts/comments for Codex-written text | no outward action |

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

1. Confirm pool layer and row restrictions permit interaction.
2. Read the post, intended parent comment, and enough nearby replies to avoid duplication.
3. Confirm the target is visible, unlocked, current enough, and not sensitive or hostile.
4. Compare subreddit, cluster, angle, intended claim, and the last `10` measured comment/reply lengths with `history_ledger`.
5. Confirm the account can contribute without fake experience, product mention, or unsupported factual claims.

For main posts, also verify live home/about/rules, pinned posts, recent survivor patterns, karma/age, flair/title/megathread, link/self-promo rules, submit controls, same-subreddit history, and moderator-approval state.

Decision: `pass_to_draft`, `retarget`, or `hard_stop`.

## Copy Consistency

Run `outbound-copy-gate.md` after Check A.

- Preserve a coherent voice: curious, practical, concise, praise-first when appropriate.
- Vary form based on context. Do not force every comment into two sentences or every post into the same question template.
- Compare the last `10` measured comment/reply entries. If the last `3` use the same tier or sentence form, reassess the next shape against the target's real information need and nearby style.
- Comments should remain mostly micro/fragment/one-liner; two-beat and compact paragraphs need a concrete reason.
- Variation is a quality check, not a random schedule: do not pad, truncate, or cycle tiers merely to make the ledger look different.
- Main-post length should follow recent native survivor posts and the amount of context the subreddit expects. Do not use one universal post length.
- Topic, facts, and persona stay consistent even when length and phrasing vary.

## Double-Check B: Immediately Before Submit

Run after the final draft is entered and before clicking Reply/Post.

1. Confirm the intended Reddit account, target subreddit/URL, and action type.
2. Confirm the target is still visible/unlocked and no warning, removal, captcha, or rate limit appeared.
3. Re-read the final text against the exact parent/post and current subreddit context.
4. Confirm truthfulness, on-topic fit, no prohibited promotion/link, and no contradiction with `history_ledger`.
5. Compute the final draft's `char_count`, `word_count`, `sentence_form`, and `length_tier`; confirm its length, opening, rhythm, subreddit, cluster, and angle are not needlessly repeating recent actions.
6. Confirm this exact action was not already submitted; after a Chrome reconnect, inspect profile/thread before any retry.
7. For posts, confirm title, flair, body/link mode, megathread placement, eligibility, and no moderator-approval requirement one final time.

Decision:

- `submit`: every check passes.
- `rewrite`: copy or length/history consistency fails; revise and rerun Check B.
- `retarget`: community, eligibility, history saturation, or live context fails; abandon draft and return to discovery.
- `hard_stop`: account/browser/platform warning or clear rule prohibition.

## Log

For every outward action, record:

```text
double_check_a | double_check_b | history_comparison | restriction_level
char_count | word_count | sentence_form | length_tier | why_this_length
subreddit/cluster diversity result | verified permalink
```
