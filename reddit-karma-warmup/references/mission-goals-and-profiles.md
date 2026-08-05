# Mission goals and profiles

Question 2 supplies one operating direction, from which community-discovery
vectors are derived.
Question 3 supplies the primary business goal and action authority. Supporting
units may run only when the recorded evidence graph arms them; neither answer
alone bypasses a live action gate.

## Startup normalization

After bootstrap, compile a complete direct target assignment when one is
present; otherwise obtain the three-answer artifact defined in
[startup intake](startup-intake.md). Normalize either into the canonical
fields below. Do not ask for an account name or handle: use only the later
same-Chrome live session proof. Question 2 carries one operating direction;
persona, target
people, topic cluster, and optional community seeds are interchangeable ways
to express it. Question 3 carries the user-visible action scope, business
goal, authority, and operating limits. Truthful materials are optional at startup and required only for the
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
action_budget: minimal | standard | active
material_refs: real URLs, artifacts, observations, or []
planning_targets: evidence/output targets plus soft throughput targets, never forced action counts
```

Question 2 or explicit target post URLs determines `community_scope`: named communities are `closed`,
expandable seeds are `seeded_expandable`, and a direction-only answer is
`discover`. Do not request audience, topic, material, or a community list after
Question 2; they are all optional details of the one operating direction and default to
`[]` / `discover` where relevant. It does not determine
`business_goal` or grant a write. If the user only says “low frequency”, map it to
`standard/high/minimal`; “high frequency” maps to `broad/standard/active`.
State that mapping in the envelope. If they say “broad but strict”, preserve
`broad/high/<chosen budget>` instead. Do not change the 15-minute Heartbeat.

## Hard gates versus soft threshold

For posts and other full actions require all hard gates: explicit unit authority;
current live rule and format fit; truthful material or claim; account and
submit-state fit; no duplicate/recent-history conflict; one submission plus
verification. Comments use the lighter target/context/basic-rule/composer path
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
or comment. Active missions use soft defaults of 4 verified comments/hour
(ceiling 5), 1 verified post per two hours, 3 useful follow-ups/hour (ceiling 5),
and 30 qualified reads/hour, with a combined public-action ceiling of 6/hour.
Standard missions use 2 comments/hour, 1 post per two hours, 2 follow-ups/hour,
and a 4/hour public-action ceiling. These are pacing targets, not a reason to
publish filler.
For a launch/distribution goal, an eligible post route outranks
more browsing. If no compliant route or truthful material exists, report the
goal as unmet with `RULE_BLOCKED` or `MATERIAL_REQUIRED`; do not disguise it as
successful exploration or repeat the same sweep. One failed candidate or
community is not mission-wide exhaustion: record `candidate-reject`, refill
from browsing, and keep the KPI honest.
