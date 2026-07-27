# Mission goals and profiles

Question 2 supplies account direction and community-discovery vectors.
Question 3 supplies the primary business goal and action authority. Supporting
units may run only when the recorded evidence graph arms them; neither answer
alone bypasses a live action gate.

## Three-question startup normalization

After bootstrap, obtain the three-answer artifact defined in
[startup intake](startup-intake.md), then normalize it into the canonical
fields below. Do not ask for an account: use only the later same-Chrome live
account proof. Question 2 carries account direction/IP, audience, and optional
community seeds. Question 3 carries business goal, authority, and operating
limits. Truthful materials are optional at startup and required only for the
specific action that needs them.

| Goal | Derived from Question 3 | Primary result |
| --- | --- | --- |
| `community_discovery` | `research first` | current community-route and candidate packs |
| `conversation_entry` | `discussion first` | context-fit discussion opportunities |
| `project_distribution` | `project operation` | eligible native publication only when a route and material pass |
| `relationship_maintenance` | explicit `Other` / follow-up only | useful reply/monitoring result |
| `profile_readiness` | explicit `Other` / presence only | verified presence result |

## User prompt compilation

Accept natural language, then record these canonical fields:

```text
business_goal: one table value
direction: exact Question 2 answer
account_direction: compact account/IP positioning
direction_tags: one or more community-discovery vectors
community_scope: closed | seeded_expandable | discover
coverage_budget: narrow | standard | broad
action_threshold: high | standard | low
action_budget: minimal | standard | active
material_refs: real URLs, artifacts, observations, or []
planning_targets: evidence/output targets, never forced action counts
```

Question 2 determines `community_scope`: named communities are `closed`,
expandable seeds are `seeded_expandable`, and a direction-only answer is
`discover`. It does not determine `business_goal` or grant a write. If the
user only says “low frequency”, map it to
`standard/high/minimal`; “high frequency” maps to `broad/standard/active`.
State that mapping in the envelope. If they say “broad but strict”, preserve
`broad/high/<chosen budget>` instead. Do not change the 15-minute Heartbeat.

## Hard gates versus soft threshold

Always require all hard gates: explicit unit authority; current live rule and
format fit; truthful material or claim; account and submit-state fit; no
duplicate/recent-history conflict; one submission plus verification.

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
or comment. For a launch/distribution goal, an eligible post route outranks
more browsing. If no compliant route or truthful material exists, report the
goal as unmet with `RULE_BLOCKED` or `MATERIAL_REQUIRED`; do not disguise it as
successful exploration or repeat the same sweep.
