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

## Question 2 — account direction

Ask: **账号希望在 Reddit 上成为什么样的人，并围绕哪些话题/社区被看见？**
You may answer through the account persona, people you hope to reach, topic
cluster, or seed communities. They are all evidence for one account direction;
one clear expression is enough.

| Choice | Example direction |
| --- | --- |
| `社交与社区` | a thoughtful, human-scale participant around low-pressure connection, friendship, and community UX |
| `个人创作与独立项目` | a curious builder around solo projects, creative tools, and maker practice |
| `3D/游戏/共创` | a playful systems-and-worlds creator around spatial interaction, games, and co-creation |

This one answer sets the account direction; account persona, target people,
topic cluster, and community seeds are not separate required fields. It grants
no action authority and does not select a business goal. Preserve the user's
exact wording in `direction`, and record a compact `account_direction` plus
`direction_tags` only as normalizations of that same answer. Named communities
are optional *seeds* and therefore default to
`seeded_expandable`; only an explicit request to stay within that exact list
creates `closed`. A direction without named communities is `discover`.
Choosing a preset or supplying any clear account-direction text completes
Question 2: do not ask a second-round question for audience, topic, community
scope, a project link, facts, or lived observations. Default omitted scope to
`discover` when no community seeds were volunteered (otherwise
`seeded_expandable`), and material refs to
`[]`. If posts later lack material, park only `posts` as
`MATERIAL_REQUIRED`; do not ask another startup question or invent facts.

## Question 3 — action scope

Ask: **这轮希望账号做到哪一步？**

| Choice | What the user will see | Business goal | Explicit units | Default profile |
| --- | --- | --- | --- | --- |
| `模拟浏览` | 只读探索社区和内容，不公开互动 | `community_discovery` | `browsing=READ_ONLY` | `standard / high / minimal` |
| `参与讨论` | 在有真实具体贡献时自然评论；不发项目帖 | `conversation_entry` | `browsing=READ_ONLY`, `comments=COMMENT_AUTHORIZED` | `standard / standard / standard` |
| `全面推进` | 在符合版规和真实性前提下，可评论、发真实项目帖、跟进已有互动，并做明确的主页/社区维护 | `project_distribution` | `browsing=READ_ONLY`, `comments=COMMENT_AUTHORIZED`, `posts=POST_AUTHORIZED`, `follow-up=FOLLOWUP_AUTHORIZED`, `presence=PRESENCE_AUTHORIZED` | `broad / standard / active` |

The three profile values are `coverage_budget / action_threshold / action_budget`.
Every outward action remains subject to live rules, truthful evidence, account
and composer state, duplicate checks, and independent verification. The
choice controls action scope, not a frequency, quota, or promise of publication.

Accept `Other` only when the user explicitly names permitted units, one
business goal, and optional `narrow|standard|broad` coverage plus
`high|standard|low` threshold. Record that free-text answer as
`authority_profile` and extract it into the compiler's structured
`custom_authority` object; otherwise the compiler returns
`INVALID_STARTUP_INPUT` rather than inferring a write authorization. Never
infer a write authorization or business goal from Question 2. Preserve the
exact third answer as the authorization receipt. Legacy answer labels remain
accepted by the local compiler only for already-written prompts; do not show
them in a new intake.

## Completion rule

Once all three answers are complete, record them in one local JSON artifact and
run `scripts/compile_startup_intake.py --input <answers.json> --output
<normalized.json>`. Only `STARTUP_ANSWERS_COMPLETE` may proceed; partial input
stays `WAITING_FOR_STARTUP_INPUT`, and explicit cancellation stays
`STARTUP_CANCELLED_BY_USER`. The compiler is local-only and creates no queue,
Heartbeat, Chrome binding, or Reddit action. It normalizes Question 2 into
`direction`, `account_direction`, `direction_tags`, and `community_scope`; the
first two are the exact and compact forms of one answer, not separate inputs. It
normalizes Question 3 into `business_goal`, `coverage_budget`,
`action_threshold`, `action_budget`, selected units, and authority.
`material_refs` are optional at startup and `planning_targets` remain
evidence/output targets, never forced actions. Merge only this completed
normalized artifact with system-provided mission ID, live account, start time,
and source-prompt evidence, then, without another user prompt, complete this
same-task transition:

`runtime fence -> immutable envelope -> neutral canary + same-Chrome account
gate -> Heartbeat create/readback -> INITIAL direct packet -> recorded next-work
continuation`

The `INITIAL` packet is round one of the mission. If it runs `browsing`, it
must perform the mission's real community/candidate work and record its real
evidence; it is not a preview, pre-filter, or separate planning round. If it
produces an authorized, concrete comment/post route, record the queue `handoff`
before closing the packet so the next verified Heartbeat runs the target unit.
Technical gates remain required, but a passing gate must continue directly into
that first packet. No fourth question is required, including for a community
list, project link, material facts, or a candidate preview.
