# Startup intake

Ask all three questions at once after bootstrap. Wait for all three answers
before Chrome, research, mission compilation, queue, or Heartbeat work. Do not ask for an account; the later same-Chrome gate is authoritative. This intake
has no fourth question.

Use `request_user_input` once when available, with three choices per question
and no `autoResolutionMs`. Otherwise ask the same questions in one compact text
message. A preset or explicit `Other` value completes its question. Do not turn
`Other` into an open-ended interview.

## Required-answer wait

No response, a partial response, dismissal, or expiry is
`WAITING_FOR_STARTUP_INPUT`. Only an explicit cancellation returns
`STARTUP_CANCELLED_BY_USER`; silence never does, and do **not** submit
`request_user_input` again.

## Text fallback after an unanswered form

Send this normal-text reminder and keep waiting. Mention recognized/missing
answers, but always repeat all three questions:

```text
请先回答以下三个问题（可直接按 `1) … 2) … 3) …` 回复）：
1) 运行多久？可选：2 小时 / 4 小时 / 8 小时。
2) 希望账号在 Reddit 上成为什么样的人、围绕什么方向或社区被看见？可选：社交与社区 / 个人创作与独立项目 / 3D/游戏/共创。
3) 这轮希望账号做到哪一步？可选：模拟浏览 / 参与讨论 / 全面推进。
```

This is the same intake, not a second-round question. Use the compiler's exact
fallback payload rather than improvising field names.

## Question 1 — duration

Ask how long the mission should run.

| Choice | Hours |
| --- | ---: |
| `2 hours` | 2 |
| `4 hours` | 4 |
| `8 hours` | 8 |

Accept an explicit custom duration from more than zero through 168 hours. It
does not change the 15-minute Heartbeat.

## Question 2 — one account direction

Ask: **账号希望在 Reddit 上成为什么样的人，并围绕哪些话题/社区被看见？**

| Choice | Direction |
| --- | --- |
| `社交与社区` | low-pressure connection, friendship, community UX |
| `个人创作与独立项目` | solo projects, creative tools, maker practice |
| `3D/游戏/共创` | spatial interaction, games, co-creation |

Persona, audience, topics, and community seeds are one account direction, not
separate required fields. Preserve the user's wording and normalize it only
into `account_direction` and `direction_tags`. Named communities are optional
seeds (`seeded_expandable`); only an explicit closed list is `closed`; no seeds
means `discover`.

This answer grants no action authority, and do not ask a second-round question for
scope, materials, a project link, facts, or observations. Default
`material_refs=[]`. Missing material does not automatically park posts: use
mission-wide `MATERIAL_REQUIRED` only after a bounded truthful-format audit.

## Question 3 — action scope

Ask: **这轮希望账号做到哪一步？**

| Choice | User-visible scope | Business goal | Units |
| --- | --- | --- | --- |
| `模拟浏览` | read-only discovery | `community_discovery` | browsing |
| `参与讨论` | discovery plus natural comments | `conversation_entry` | browsing, comments |
| `全面推进` | eligible comments, truthful posts, follow-up, concrete presence | `project_distribution` | all five units |

This is action scope, not frequency, quota, or a publication promise. All
outward actions still require live rules, truthful evidence, account/composer
state, duplicate checks, and verification. Accept a custom answer only when it
explicitly names allowed units and one business goal; never infer write
authority from Question 2.

## Completion rule

Write the three answers to one local JSON artifact and run
`scripts/compile_startup_intake.py`. Only `STARTUP_ANSWERS_COMPLETE` proceeds;
invalid or incomplete input keeps waiting.

Merge the normalized artifact with the system mission ID, live account, start
time, and source prompt, then continue without another prompt:

`runtime fence -> immutable envelope -> neutral canary/account gate ->
Heartbeat create/readback -> INITIAL direct packet -> continuation`

The INITIAL direct packet is formal round one, not a preview, pre-filter, or
separate planning round. It must perform real mission work immediately. If it
finds an authorized concrete route, record atomic handoff before closing so the
next verified Heartbeat runs that action unit. Technical gates are required but
not another user-decision stage.
