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

## Question 2 — goal, topic, and scope

Ask: **What is the goal, topic, and scope? Include target audience, discovery
or named communities, and any truthful material; write `none` for no material.**

| Choice | Default business goal | Default scope |
| --- | --- | --- |
| `community discovery` | `community_discovery` | `discover` |
| `discussion or feedback` | `conversation_entry` | `seeded_expandable` |
| `project operation` | `project_distribution` | `discover` |

The same answer must carry the actual topic and audience. A named community
list changes scope to `closed`; a starting list that may expand changes it to
`seeded_expandable`. If the user explicitly asks only for a verified own
permalink or a concrete profile change, normalize to `relationship_maintenance`
or `profile_readiness` instead. If a `project operation` answer includes no
truthful publishable material, posts later become `MATERIAL_REQUIRED`; do not
ask another question and do not invent facts.

## Question 3 — authority and operating profile

Ask: **What may the task do, and how selective should it be?**

| Choice | Explicit units | Default profile |
| --- | --- | --- |
| `research first` | `browsing=READ_ONLY` | `standard / high / minimal` |
| `discussion first` | `browsing=READ_ONLY`, `comments=COMMENT_AUTHORIZED` | `standard / standard / standard` |
| `project operation` | `browsing=READ_ONLY`, `comments=COMMENT_AUTHORIZED`, `posts=POST_AUTHORIZED`, `follow-up=FOLLOWUP_AUTHORIZED`, `presence=PRESENCE_AUTHORIZED` | `broad / standard / active` |

The three profile values are `coverage_budget / action_threshold / action_budget`.
Every outward action remains subject to live rules, truthful evidence, account
and composer state, duplicate checks, and independent verification. The
profile is not a quota.

Accept `Other` only when the user explicitly names permitted units and optional
`narrow|standard|broad` coverage plus `high|standard|low` threshold. Never
infer a write authorization from Question 2. Preserve the exact third answer
as the authorization receipt.

## Completion rule

Once all three answers are complete, normalize them into the existing canonical
mission fields: `business_goal`, `community_scope`, `coverage_budget`,
`action_threshold`, `action_budget`, `material_refs`, `planning_targets`,
selected units, and authority. Then perform the same-Chrome live account gate,
compile the immutable envelope, and begin the single-owner mission. No fourth
question is required.
