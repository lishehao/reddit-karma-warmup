# Startup intake

After bootstrap passes, ask all three questions at once. Wait for all three
answers before opening Chrome or compiling a mission. Do not ask for an account: the later same-Chrome live gate is the only account source of truth.
Do not ask a fourth question merely to collect a missing project artifact,
community rule, or candidate; record the resulting blocked unit honestly.

Use the presets when the task UI supports three choices per question. `Other`
is for an explicit custom value, not a reason to start an unbounded interview.
Keep the user's one-line additions as the authorization and source-prompt
evidence.

When `request_user_input` is available, submit exactly these three questions in
one request and wait for the user's answers. Omit `autoResolutionMs`: automatic
resolution is only for nonblocking prompts and is forbidden for this intake.
Otherwise present the same three headings in one compact message and wait.
Never split them into sequential questions or use an automatic timeout to infer
an answer. This flow asks no fourth question.

## Required-answer wait

Treat no response, a partial response, a dismissed form, or a platform-side
question expiry as `WAITING_FOR_STARTUP_INPUT`. Do not infer missing values,
compile an envelope, create a queue/Heartbeat, open Chrome, or begin research.
Resume only when all three answers are explicit. An explicit user cancellation
ends intake as `STARTUP_CANCELLED_BY_USER`; silence never does.

## Question 1 — duration

Ask: **How long should this mission run?**

| Choice | Normalized duration |
| --- | --- |
| `2 hours` | `2` |
| `4 hours` | `4` |
| `8 hours` | `8` |

Accept `Other` only as an explicit duration from more than zero through 168
hours. The duration never changes the 15-minute Heartbeat interval.

## Question 2 — account direction and community discovery

Ask: **账号想往什么方向找社区，并塑造成怎样的 IP？请写主方向、目标受众和
希望呈现的账号感；已有社区可一并写，没有则按方向探索。**

| Choice | Community-discovery vector | Account/IP intent |
| --- | --- | --- |
| `社交与社区` | low-pressure connection, friendship, community UX, city/campus/offline social life | a thoughtful, human-scale community participant |
| `个人创作与独立项目` | solo building, side projects, creative tools, maker practice | a curious builder who shares useful work and process |
| `3D/游戏/共创` | spatial interaction, games, UGC, virtual worlds, co-creation | a playful systems-and-worlds creator |

This answer selects a community-discovery direction and account/IP
positioning; it grants no action authority and does not select a business
goal. Preserve the user's exact direction in `direction`, and record a
compact `account_direction` plus `direction_tags` when useful. A named
community list is `closed`; a starting list that may expand is
`seeded_expandable`; a direction without named communities is `discover`.
Choosing a preset or supplying custom direction/IP text completes Question 2:
do not ask a second-round question for community scope, a project link, facts,
or lived observations. Default omitted scope to `discover` and omitted
material refs to `[]`. If posts later lack material, park only `posts` as
`MATERIAL_REQUIRED`; do not ask another startup question or invent facts.

## Question 3 — authority and operating profile

Ask: **What may the task do, and how selective should it be?**

| Choice | Business goal | Explicit units | Default profile |
| --- | --- | --- |
| `research first` | `community_discovery` | `browsing=READ_ONLY` | `standard / high / minimal` |
| `discussion first` | `conversation_entry` | `browsing=READ_ONLY`, `comments=COMMENT_AUTHORIZED` | `standard / standard / standard` |
| `project operation` | `project_distribution` | `browsing=READ_ONLY`, `comments=COMMENT_AUTHORIZED`, `posts=POST_AUTHORIZED`, `follow-up=FOLLOWUP_AUTHORIZED`, `presence=PRESENCE_AUTHORIZED` | `broad / standard / active` |

The three profile values are `coverage_budget / action_threshold / action_budget`.
Every outward action remains subject to live rules, truthful evidence, account
and composer state, duplicate checks, and independent verification. The
profile is not a quota.

Accept `Other` only when the user explicitly names permitted units, one
business goal, and optional `narrow|standard|broad` coverage plus
`high|standard|low` threshold. Never infer a write authorization or business
goal from Question 2. Preserve the exact third answer as the authorization
receipt.

## Completion rule

Once all three answers are complete, normalize Question 2 into `direction`,
`account_direction`, `direction_tags`, and `community_scope`; normalize
Question 3 into `business_goal`, `coverage_budget`, `action_threshold`,
`action_budget`, selected units, and authority. `material_refs` are optional
at startup and `planning_targets` remain evidence/output targets, never forced
actions. Then, without another user prompt, complete this same-task transition:

`runtime fence -> immutable envelope -> neutral canary + same-Chrome account
gate -> Heartbeat create/readback -> INITIAL formal packet`

The `INITIAL` packet is round one of the mission. If it runs `browsing`, it
must perform the mission's real community/candidate work and record its real
evidence; it is not a preview, pre-filter, or separate planning round. Technical
gates remain required, but a passing gate must continue directly into that first
packet. No fourth question is required.
