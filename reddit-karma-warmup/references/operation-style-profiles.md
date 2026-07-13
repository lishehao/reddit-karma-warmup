# Operation Style Profiles

Load for `ACCOUNT_BOOTSTRAP` or `MISSION` when target discovery, community selection, browsing preference, or writing posture depends on the requested operation style.

`operation_style` is a per-run focus inside the broader durable `account_direction` defined in `account-direction.md`. It may narrow the current run but must not invent a new identity or push the account outside its truthful interest portfolio.

## Selector

Use one resolved `operation_style`:

| Style | Chinese aliases | Target direction | Content and voice |
|-|-|-|-|
| `mixed` | 混合、混合探索、默认 | Rotate across the four Loci interest clusters below according to live opportunity. | Adapt to each community; concise, specific, praise-first, and not locked to one topic. |
| `builder` | 建设者、产品开发、独立开发 | Indie apps, product/UX, game development, AI tools, creator workflow. | Practical observation, implementation tradeoff, useful question, or concrete feedback. |
| `gaming-3d` | 游戏、3D、玩家创作者 | Games, Unity/Unreal, 3D art, VR/social worlds, UGC and mechanics. | Mechanic-specific, player/creator-aware, lighter and more playful where native. |
| `spatial-place` | 空间、地点、AR、探索 | AR/XR, maps, photography, walking, travel, location-based play and place interaction. | Observational, curious, grounded in visible spatial/place details; avoid location or privacy assumptions. |
| `social-creative` | 社交、轻社交、创意共创 | Lightweight social interaction, friendship/memory, avatars, co-creation, creative communities. | Warm but concise; focus on interaction mechanics and creative participation, not therapy or emotional diagnosis. |
| `custom` | 自定义 | User-supplied topics, communities, interests, exclusions, and voice. | Follow the supplied posture while preserving truthfulness and community fit. |

`mixed` is the default. A user may combine one primary style with a simple voice modifier, for example `游戏/3D，更犀利` or `空间地点，轻松一点`. Store the modifier separately as `voice_modifier`.

## Resolution

1. Parse an explicit style or custom brief from the user's latest command.
2. If none is supplied, reuse the active mission style; otherwise default to `mixed`.
3. User-supplied communities, topics, exclusions, or voice override the profile field they address.
4. Resolve the profile before candidate discovery and pass the resolved style plus modifier to each enabled worker.
5. A later `换成…风格` updates future slots only; it does not rewrite or duplicate already published content.

## Lane Use

- `comments`: prefer candidates where the style can add one native, specific contribution; do not force the topic into an unrelated thread.
- `posts`: choose community, audience, and angle from the style before live preflight; the post must still look native without invented experience.
- `browsing`: bias discovery toward the style while preserving community diversity; style fit may support the declared-interest score but never replaces a qualified read.
- `follow-up`: answer the actual reply or notification first. Use the style only as a light voice/interest prior when it does not distort the conversation.

## Boundaries

- Style is a routing preference, not a persona claim. Never invent employment, founder status, expertise, product use, location, age, metrics, or lived experience.
- Live rules, account eligibility, target context, and quality gates override the style.
- Do not repeat one subreddit, topic cluster, opening, or opinion merely to maintain a style.
- `mixed` means adaptive diversity, not random topic switching inside one comment or post.
