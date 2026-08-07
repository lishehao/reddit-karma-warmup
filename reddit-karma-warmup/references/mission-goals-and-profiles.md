# Mission goals and profiles

Question 2 supplies one operating direction, from which community-discovery
vectors are derived.
Question 3 supplies the primary business goal and action authority. Question 4
supplies the workload rhythm. Supporting
units may run only when the recorded evidence graph arms them; neither answer
alone bypasses a live action gate.

## Startup normalization

After bootstrap, compile a complete direct target assignment when one is
present; otherwise obtain the four-answer artifact defined in
[startup intake](startup-intake.md). Normalize either into the canonical
fields below. Do not ask for an account name or handle: use only the later
same-Chrome live session proof. Question 2 carries one operating direction;
persona, target
people, topic cluster, and optional community seeds are interchangeable ways
to express it. Question 3 carries the user-visible action scope, business
goal, and authority. Question 4 carries the workload rhythm independently.
Truthful materials are optional at startup and required only for the
specific action that needs them.

| Goal | Derived from Question 3 | Primary result |
| --- | --- | --- |
| `community_discovery` | `模拟浏览` | current community-route and candidate packs |
| `conversation_entry` | `参与讨论` | context-fit discussion opportunities |
| `project_distribution` | `全面推进` | eligible native publication only when a route and material pass |
| `relationship_maintenance` | explicit `Other` / follow-up only | useful reply/monitoring result |
| `profile_readiness` | explicit `Other` / presence only | verified presence result |

## User prompt compilation

Accept natural language, then record these canonical fields:

```text
business_goal: one table value
direction: exact one Question 2 operating-direction answer
account_direction: internal compatibility field; compact normalization of that
same direction, not an account name or another answer
direction_tags: derived community-discovery vectors
community_scope: closed | seeded_expandable | discover
coverage_budget: narrow | standard | broad
action_threshold: high | standard | low
frequency: low | standard | high
action_budget: minimal | standard | active
material_refs: real URLs, artifacts, observations, or []
planning_targets: evidence/output targets plus soft throughput targets, never forced action counts
```

Question 2 or explicit target post URLs determines `community_scope`: named communities are `closed`,
expandable seeds are `seeded_expandable`, and a direction-only answer is
`discover`. Do not request audience, topic, material, or a community list after
Question 2; they are all optional details of the one operating direction and default to
`[]` / `discover` where relevant. It does not determine
`business_goal` or grant a write. Question 4 maps `低 / 标准 / 高` to the
independent workload profiles below; it never changes the 15-minute Heartbeat.
Direct target assignments default to `标准` unless they explicitly include a
rhythm.

For `discover` and `seeded_expandable`, use community-diverse coverage by
default: each coverage block should sample five distinct communities, with a
minimum of four when a route fails. Spread public actions across four or five
distinct communities before repeating one. This is a routing target, not a
filler quota: live rules, truthful contribution, and fit still decide whether
anything is published. `closed` direct-target assignments stay closed.

## Hard gates versus soft threshold

For posts and other full actions require all hard gates: explicit unit authority;
current live rule and format fit; truthful material or claim; account and
submit-state fit; no duplicate/recent-history conflict; one submission plus
verification. For posts, the live Flair control is part of the format gate:
select the most specific truthful Flair when required, and stop if no truthful
option exists. Comments use the lighter target/context/basic-rule/composer path
with same-target duplicate protection.

Apply `action_threshold` only after those gates pass:

- `high`: require strong direct relevance and a specific truthful contribution.
- `standard`: require clear relevance and contextual fit.
- `low`: require adequate relevance and non-duplicative truthful value.

“Low” never allows irrelevant, fabricated, promotional, duplicate, or
rule-breaking content.

## KPI semantics

Use three reporting layers:

1. **Coverage:** community routes and qualified reads.
2. **Opportunity:** dated candidate packs and `ACTION_ELIGIBLE` routes.
3. **Output:** verified public actions.

Planning targets describe desired evidence and output, but never force a post
or comment. The three rhythm profiles are:

| Rhythm | Reads/hour | Comments/hour | Follow-ups/hour | Posts | Public actions/hour |
| --- | ---: | ---: | ---: | --- | ---: |
| `低` | 12 | 1 (ceiling 2) | 1 (ceiling 2) | at most 1/4h | 2 |
| `标准` | 20 | 2 (ceiling 3) | 2 (ceiling 3) | at most 1/2h | 4 |
| `高` | 30 | 5 (ceiling 6) | 3 (ceiling 5) | at most 1/2h | 6 |

The action scope still decides which units are authorized. For example,
`模拟浏览 + 高` means more reading, not comments or posts; `全面推进 + 高`
enables all five units at the high profile. Hourly counters reset by UTC hour
bucket, so a completed hour does not permanently consume the mission's future
capacity. These are pacing targets, not a reason to publish filler.
For a launch/distribution goal, an eligible post route outranks
more browsing. If no compliant route or truthful material exists, report the
goal as unmet with `RULE_BLOCKED` or `MATERIAL_REQUIRED`; do not disguise it as
successful exploration or repeat the same sweep. One failed candidate or
community is not mission-wide exhaustion: record `candidate-reject`, refill
from browsing, and keep the KPI honest.
