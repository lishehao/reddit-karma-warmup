# Account Direction

Use during initial setup, presence work, and every distributor dispatch. Account direction is a durable, broad, truthful interest portfolio. It is not a fictional persona and not a technique for hiding promotion.

## Account-Keyed Storage

Store one confirmed direction per visible Reddit account at:

```text
${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/account-directions/<normalized-reddit-username>.json
```

This is user-owned state outside the managed Skill folder, so atomic upgrades must preserve it. Normalize only for a safe filename; keep the exact visible username inside the JSON. Store no credentials, cookies, tokens, inferred identity facts, or browser identifiers.

Minimum schema:

```json
{
  "schema_version": 2,
  "reddit_account": "u/name",
  "account_direction": ["..."],
  "direction_tags": ["..."],
  "direction_source": "default_loci_broad",
  "confirmed_at": "ISO-8601 with timezone"
}
```

## Default Loci Direction

When the user provides no direction, resolve:

```text
account_direction:
  - mobile products and practical app UX
  - 3D, AR/XR, and spatial interaction
  - games, UGC, virtual worlds, and creator mechanics
  - photography, place discovery, walking, and real-world experiences
  - creative tools, visual making, and lightweight co-creation
direction_source=default_loci_broad
```

This breadth supports several adjacent communities without turning the account into a random general-interest profile.

## Constraints

1. Use `3-5` adjacent pillars. One pillar is usually too narrow; more than five unrelated pillars becomes incoherent.
2. Every pillar must be a truthful interest the account can sustain through ordinary reading, comments, questions, and occasional native posts.
3. Keep identity facts separate from interests. Never invent age, location, job, founder status, expertise, ownership, product use, metrics, or lived experience.
4. A per-run `operation_style` selects one or two pillars; it does not rewrite the durable account direction.
5. Product-related participation must comply with live self-promotion rules and disclose affiliation when material. Do not disguise Loci promotion as an independent recommendation, fake discovery, fake customer story, or unrelated user testimony.
6. Do not manufacture unrelated filler or enforce a mechanical product/non-product ratio to make promotion less visible. Genuine participation and community fit are the standard.
7. Community diversity comes from adjacent pillars, not from repeatedly switching identity, voice, or biography.

## Setup Resolution

- After Chrome confirms the exact visible Reddit account, read only that account's direction file. Never reuse another account's file.
- If a valid matching file exists, reuse it silently as the durable fallback. The first successful Bootstrap still asks once for this run's direction and duration; it does not print a separate account-direction status line.
- If the file is missing, malformed, or names a different account, prepare the broad default silently. The combined direction-and-duration answer confirms and persists the normalized direction.
- If the initial setup command already supplies an explicit truthful direction and duration, normalize/persist it and dispatch immediately without a redundant question.
- If the user supplies a direction, normalize it to `3-5` truthful adjacent pillars and set `direction_source=user`.
- Map the confirmed pillars to canonical `direction_tags` from `subreddit-catalog-taxonomy.md`. Persist those tags with the direction so later launcher runs do not have to reinterpret the same wording.
- If the user supplies only one narrow topic, preserve it as the primary pillar and add only clearly adjacent support pillars; briefly show the resolved direction.
- Only after a healthy Bootstrap has emitted its direction-and-duration prompt, `继续`, `开始`, `默认`, or `没想法` accepts the matching saved direction or broad default and starts `3h`. A repair-state `继续` never reaches direction resolution or dispatch.
- A direction-only answer defaults to `3h`; a duration-only answer uses the matching saved direction or broad default. Dispatch immediately after this one answer rather than asking a second confirmation or operation question.

After direction confirmation, select one or two truthful pillars as `mission_identity_focus` and load `community-selection-funnel.md`. For each enabled proactive lane, run lane-specific retrieval. This is local catalog retrieval, not Reddit browsing:

```text
scripts/query_subreddit_profile_index.py --direction <resolved pillars + mission focus> --lane comments --reference-sweep-limit 100 --limit 20 --include-traffic-probes
scripts/query_subreddit_profile_index.py --direction <resolved pillars + mission focus> --lane posts --reference-sweep-limit 100 --limit 20 --include-traffic-probes
```

Use `research_matches` only to summarize account-direction coverage. Keep only the relevant `comment_shortlist` or `post_reference_shortlist` plus `traffic_probe_queue` for worker dispatch:

- `operating_shortlist`: cached traffic is at least `5,000` weekly visitors; exact action rules still require live preflight.
- `traffic_probe_queue`: tag-fit candidate with missing/stale traffic; a worker must confirm current weekly visitors before it can act.
- `comment_shortlist`: comment-route candidates ordered by direction fit and stored rule friendliness; the comment worker still scores the exact live post.
- `post_reference_shortlist`: post-route candidates ordered by direction fit and stored rule friendliness; the post worker still performs deep live rules/account preflight.
- `research_matches`: traffic-qualified catalog matches that remain `research_only`; they may shape the displayed interest cluster or future audit queue, but never enter a worker handoff or action target.
- a cached row below `5,000` never enters either list.

If the index or query script is unavailable, do not block setup. Preserve the confirmed direction, report `社区索引暂不可用`, and let each worker use the existing exact rule references without an indexed shortlist.

Use the Bootstrap Success Prompt from `runtime-and-setup.md`; do not emit another direction confirmation block from this reference. Its direction explanation is intentionally user-facing while the durable `3-5` pillar normalization remains internal.

Legacy clients may still send `确认` or `确认并开始`; accept them as default direction plus `3h`, but never advertise those commands in the successful Bootstrap output.

For non-Bootstrap diagnostics only, the internal resolved state may be summarized as:

```text
账号方向：<3-5 个兴趣支柱>。本轮重点：<operation_style>。
```

## Lane Application

- Comments: begin with the supplied low-friction `comment_shortlist`, then prioritize threads where one direction pillar naturally contributes; never force a pillar into unrelated context.
- Posts: begin with `post_reference_shortlist`, run the broad-to-deep destination funnel, then select a community-native question, observation, artifact, or transparent project discussion. Current rules decide whether product affiliation is allowed.
- Follow-up: answer the actual inbound message first; direction only supplies background context.
- Browsing/presence: maintain a coherent mix across pillars over time without treating every pillar as a quota.
