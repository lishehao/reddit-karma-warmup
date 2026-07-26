# Post Coverage And Conditional KPI

Load in `Reddit 分发台` when creating a posts mission and in `Reddit 发帖台` before selecting a destination. `operation-defaults.json` owns every numeric value here.

## One Publication Target, Not A Forced Publication

The normal posts mission has `publication_target=1`, `publication_cap=1`, and `publication_kpi=CONDITIONAL_ONE_VERIFIED_POST`. This is a conditional KPI: publish one verified native post when an exact candidate clears every hard gate. It never authorizes fabricated experience, invented project facts, rule evasion, duplicate posting, or a weak post merely to turn the counter green.

Measure two independent outcomes:

1. **Coverage KPI:** complete the resolved reference sweep, live deep reads, survivor/topic reads, and candidate packets.
2. **Publication KPI:** `0/1` until one post is verified. Do not silently change it to `0/0` because early candidates fail.

If time remains after coverage and no post is eligible, persist `publication_status=blocked_after_coverage`, preserve `action_remaining=1`, include exact rejection reasons, and continue the next eligible search/recheck on the lane's own Heartbeat. At deadline or explicit stop, report the conditional publication KPI honestly as `0/1`, never as completed.

## Pool Policy

Default `target_pool_policy=preferred_expandable`. Treat any supplied communities as preferred seeds, not a closed ceiling. Work through the ranked, action-eligible catalog rows until the configured coverage KPI is met or a verified post publishes.

Use `target_pool_exact_and_closed=true` only when the user explicitly names a closed pool. Honor it literally; do not expand. If that pool is exhausted, record `closed_pool_exhausted` with the exact failed routes and keep the publication KPI at `0/1`. A task author, cached shortlist, or old lane checkpoint must never make a pool closed by implication.

Expansion is not a permission shortcut. Every new community still passes denylist -> action override -> filtered catalog/audit -> same-day live rules/account/submit checks. `research_only`, closed, unknown K1 gate, and live-rule failures remain ineligible.

## Compliance First, Quality Second

Evaluate every candidate in this fixed order:

1. **Hard compliance:** denylist and action route, same-day live rules, account and submission eligibility, flair/title/body/megathread placement, self-promotion/link limits, approval state, and same-subreddit duplicate/recent-post checks. A mandatory conflict or a live rule/account failure is an immediate `retarget`; do not draft, score for hype, or try to compensate with better copy.
2. **Minimum content floor:** the premise is truthful, directly on topic, native to the allowed format, non-spam, and not a FAQ or recent duplicate. This protects the community but is not a demand for a highly optimized viral angle.
3. **Secondary ranking:** only among candidates that passed 1 and 2, use audience fit, timeliness, survivor fit, originality, and discussion potential to choose the least-friction suitable destination. A higher ranking score never rescues a compliance failure, and a compliant candidate that meets the content floor is not rejected merely for missing an arbitrary high aggregate score.

Live rules are time-sensitive, so a historical route or a strong local content pattern never substitutes for the first step.

## Post Modes

Resolve `post_mode` before drafting:

| Mode | Default use | Candidate gate | Additional truth requirement |
|-|-|-|-|
| `native_discussion` | Ordinary community question, observation, workflow friction, or tradeoff | hard compliance pass + `posts.native_discussion_content_score_floor` | A real, community-native premise; no personal claim unless known true. No project link, metric, or artifact is required. |
| `artifact` | Research, build, launch, benchmark, project, or evidence-led post | hard compliance pass + `posts.artifact_content_score_floor` | The claimed artifact, ownership, facts, and any metrics must be directly verifiable before drafting. |

Use `native_discussion` by default. Do not make an ordinary question inherit an artifact-link requirement. Do not relabel a promotion, launch, survey, recruiting post, or weak personal anecdote as discussion to bypass artifact evidence.

## Coverage Packet

Target `posts.candidate_packet_target` candidate packets before declaring a nonterminal no-post state. A packet is not a draft and need not pass; it records the two gates before any ranking:

```text
subreddit + post_mode + truthful premise
hard_compliance=pass|fail + exact live rule/account/submit/duplicate evidence
content_floor=pass|fail + exact reason
secondary_rank_score only after both gates pass
accept/reject decision + exact reason
```

For `native_discussion`, sample `posts.discussion_survivor_sample_target` recent local discussion survivors across the candidates and use the mode's lower content floor. For `artifact`, sample the comparable current artifact/project format; direct proof is a truth requirement, not a popularity score.

Candidate packets make the system accountable for breadth and publishing readiness. They do not lower any hard rule or turn rejected communities into publishable destinations.

## Selection Loop

1. Use cached catalog breadth for the resolved reference sweep; do not rapidly open every community in Chrome.
2. Deep-preflight the ranked range from `community_selection.post_live_preflight_community_range` and inspect recent native content in each viable finalist.
3. Build candidate packets, retarget immediately after a concrete rejection, and keep the exact reasons.
4. Publish once when one packet first passes hard compliance, its mode's minimum content floor, and Double-Check B. Use secondary ranking only to choose among multiple passing packets.
5. After verified publication, finish any remaining hard reading objective without another post.

Never use the coverage KPI to imply that Reddit accepted a post. Only a verified permalink completes the publication KPI.
