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

## Post Modes

Resolve `post_mode` before drafting:

| Mode | Default use | Candidate gate | Additional truth requirement |
|-|-|-|-|
| `native_discussion` | Ordinary community question, observation, workflow friction, or tradeoff | `posts.native_discussion_candidate_score_min` | A real, community-native premise; no personal claim unless known true. No project link, metric, or artifact is required. |
| `artifact` | Research, build, launch, benchmark, project, or evidence-led post | `posts.artifact_post_candidate_score_min` | The claimed artifact, ownership, facts, and any metrics must be directly verifiable before drafting. |

Use `native_discussion` by default. Do not make an ordinary question inherit an artifact-link requirement. Do not relabel a promotion, launch, survey, recruiting post, or weak personal anecdote as discussion to bypass artifact evidence.

## Coverage Packet

Target `posts.candidate_packet_target` candidate packets before declaring a nonterminal no-post state. A packet is not a draft and need not pass; it records:

```text
subreddit + post_mode + truthful premise
live rules/account/submit result + exact score
recent survivor/topic evidence + duplicate check
accept/reject decision + exact reason
```

For `native_discussion`, sample `posts.discussion_survivor_sample_target` recent local discussion survivors across the candidates and use the mode's discussion-potential gate. For `artifact`, sample the comparable current artifact/project format; do not apply a fake discussion-score requirement.

Candidate packets make the system accountable for breadth and publishing readiness. They do not lower any hard rule or turn rejected communities into publishable destinations.

## Selection Loop

1. Use cached catalog breadth for the resolved reference sweep; do not rapidly open every community in Chrome.
2. Deep-preflight the ranked range from `community_selection.post_live_preflight_community_range` and inspect recent native content in each viable finalist.
3. Build candidate packets, retarget immediately after a concrete rejection, and keep the exact reasons.
4. Publish once only when one packet passes its mode gate, live rules/eligibility, submit state, history/duplicate checks, and Double-Check B.
5. After verified publication, finish any remaining hard reading objective without another post.

Never use the coverage KPI to imply that Reddit accepted a post. Only a verified permalink completes the publication KPI.
