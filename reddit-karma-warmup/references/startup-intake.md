# Startup intake

## Direct target shortcut

If the user supplies 1–32 Reddit post URLs (`target_posts`), explicit `requested_work_types`/actions, and a duration, use `direct_target_mode=true` and compile it without the four-question form. Example:

```text
持续 2 小时；只浏览、评论并跟进下面几个帖子：<URL 1> <URL 2>。
```

The compiler returns `DIRECT_TARGET_ASSIGNMENT_COMPLETE`, scopes work to those posts, and the same task immediately runs `INITIAL`. The account is read silently by Chrome. If URLs, actions, or duration are missing, send one direct-text reminder and do not create a mission or second form.

Ask all four questions at once after bootstrap. Wait for all four answers before Chrome, research, mission compilation, queue, or Heartbeat work. Do not ask for an account name or handle; the same-Chrome gate reads it silently. Frequency controls workload, not the Heartbeat interval.

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
answers, but always repeat all four questions:

```text
请先回答以下四个问题（可直接按 `1) … 2) … 3) … 4) …` 回复）：
1) 运行多久？可选：2 小时 / 4 小时 / 8 小时。
2) 这轮想围绕什么方向或哪些社区运营？可选：社交与社区 / 个人创作与独立项目 / 3D/游戏/共创。
3) 这轮希望做到哪一步？可选：模拟浏览 / 参与讨论 / 全面推进。
4) 互动节奏希望怎样？可选：低 / 标准 / 高。
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

## Question 2 — operating direction

Ask: **这轮想围绕什么方向或哪些社区运营？**

| Choice | Direction |
| --- | --- |
| `社交与社区` | low-pressure connection, friendship, community UX |
| `个人创作与独立项目` | solo projects, creative tools, maker practice |
| `3D/游戏/共创` | spatial interaction, games, co-creation |

账号风格、目标受众、话题和社区种子都属于这一项，不需要拆开追问。保留用户原话，内部写入 `account_direction`/`direction_tags`；这不是账号姓名确认。命名社区是可选种子（`seeded_expandable`）；明确封闭列表才是 `closed`，没有种子则为 `discover`。

This answer grants no action authority, and do not ask a second-round question for
scope, materials, a project link, facts, or observations. Default
`material_refs=[]`. Missing material does not automatically park posts: use
mission-wide `MATERIAL_REQUIRED` only after a bounded truthful-format audit.

## Question 3 — action scope

Ask: **这轮希望做到哪一步？**

| Choice | User-visible scope | Business goal | Units |
| --- | --- | --- | --- |
| `模拟浏览` | read-only discovery | `community_discovery` | browsing |
| `参与讨论` | discovery plus natural comments | `conversation_entry` | browsing, comments |
| `全面推进` | eligible comments, truthful posts, follow-up, concrete presence | `project_distribution` | all five units |

This is action scope, not frequency, quota, or a publication promise. All
outward actions still require the action-type gate: comments use current context,
a basic rule, composer, and verification; posts use the fuller rules, truth,
format, duplicate, and session checks. Accept a custom answer only when it
explicitly names allowed units and one business goal; never infer write
authority from Question 2.

## Question 4 — interaction rhythm

Ask: **互动节奏希望怎样？**

| Choice | Typical pace |
| --- | --- |
| `低` | 约 12 个有效阅读/小时；评论 1/小时；跟进 1/小时；主帖最多 1 个/4 小时；公开动作上限 2/小时。 |
| `标准` | 约 20 个有效阅读/小时；评论 2/小时；跟进 2/小时；主帖最多 1 个/2 小时；公开动作上限 4/小时。 |
| `高` | 约 30 个有效阅读/小时；评论 5/小时；跟进 3/小时；主帖最多 1 个/2 小时；公开动作上限 6/小时。 |

These are pacing targets and ceilings, not a promise to publish filler. The
chosen rhythm is independent of action scope: `模拟浏览` can read more without
writing, while `全面推进` can use all authorized units at the same pace. Hourly
counters reset at each UTC hour bucket; they are not lifetime mission quotas.
The 15-minute Heartbeat remains unchanged.

## Completion rule

Write the four answers or direct assignment to one local JSON artifact and run
`scripts/compile_startup_intake.py`. Only `STARTUP_ANSWERS_COMPLETE` or
`DIRECT_TARGET_ASSIGNMENT_COMPLETE` proceeds;
invalid or incomplete input keeps waiting.

Merge the normalized artifact with the system mission ID, the silently derived
live session identity, start time, and source prompt, then continue without
another prompt:

`current-task scope -> immutable envelope -> one same-Chrome session gate ->
INITIAL direct packet -> optional Heartbeat continuation`

The INITIAL direct packet is formal round one, not a preview, pre-filter, or
separate planning round. It must perform real mission work immediately. If it
finds an authorized concrete route, record atomic handoff before closing so the
next task wake can run that action unit. Technical gates are required but not
another user-decision stage; missing scheduler telemetry does not block the
current packet.
