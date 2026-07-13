# Account Direction

Use during initial setup, presence work, and every fresh launcher dispatch. Account direction is a durable, broad, truthful interest portfolio. It is not a fictional persona and not a technique for hiding promotion.

## Account-Keyed Storage

Store one confirmed direction per visible Reddit account at:

```text
${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/account-directions/<normalized-reddit-username>.json
```

This is user-owned state outside the managed Skill folder, so atomic upgrades must preserve it. Normalize only for a safe filename; keep the exact visible username inside the JSON. Store no credentials, cookies, tokens, inferred identity facts, or browser identifiers.

Minimum schema:

```json
{
  "schema_version": 1,
  "reddit_account": "u/name",
  "account_direction": ["..."],
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
- If a valid matching file exists, reuse it without asking again and show one short `账号方向：...` line.
- If the file is missing, malformed, or names a different account, show the broad default and ask once for confirmation before dispatch. Accepted replies are `确认`, a concrete modification, or `确认并开始`.
- `确认` atomically writes the default and then asks what operation to start. `确认并开始` writes the default and immediately dispatches the standard three-hour operation. A concrete modification is normalized, written, and treated as confirmed.
- If the initial setup command already supplies an explicit truthful direction, that explicit direction counts as confirmation: normalize and persist it without asking a redundant question.
- If the user supplies a direction, normalize it to `3-5` truthful adjacent pillars and set `direction_source=user`.
- If the user supplies only one narrow topic, preserve it as the primary pillar and add only clearly adjacent support pillars; briefly show the resolved direction.
- A bare `开始` during first-time setup is not direction confirmation. Ask the one-time direction question. After a matching direction file exists, `开始` uses it immediately without another confirmation.
- If the setup command requests operations but has no explicit direction and no matching direction file, complete preflight, ask the one-time direction question, and dispatch immediately after the answer rather than asking a second operation question.

Use this one-time confirmation:

```text
建议账号方向：移动产品与实用 App UX、3D/AR 与空间交互、游戏/UGC 与虚拟世界、摄影与地点体验、创作工具与轻量共创。

这是长期兴趣范围，不是虚构身份。请回复“确认”，或直接告诉我需要增加/删除的方向；回复“确认并开始”会保存后立即按默认 3 小时运营。
```

Use this concise setup line:

```text
账号方向：<3-5 个兴趣支柱>。本轮重点：<operation_style>。
```

## Lane Application

- Comments: prioritize threads where one direction pillar naturally contributes; never force a pillar into unrelated context.
- Posts: select a community-native question, observation, artifact, or transparent project discussion. Current rules decide whether product affiliation is allowed.
- Follow-up: answer the actual inbound message first; direction only supplies background context.
- Browsing/presence: maintain a coherent mix across pillars over time without treating every pillar as a quota.
