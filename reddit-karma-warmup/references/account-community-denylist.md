# Account Community Denylist

Load before opening or selecting any subreddit for any Reddit lane. This is an account-level destination fence, not a historical risk score.

| Subreddit | State | Reason | Allowed action |
|-|-|-|-|
| `r/gamedev` | permanent deny | confirmed community ban and prior spam removals for the managed account; the community also applies strict game-development value and anti-showcase/self-promotion rules | none |
| `r/CozyGamers` | permanent deny | user-directed permanent exclusion; current community participation is tightly channeled, including weekly self-promotion placement and developer post-frequency limits | none |

For a permanent-deny entry:

- do not open, browse, search within, read, vote, join, flair, comment, post, test access, or revalidate through Chrome
- exclude it before candidate scoring and before any bundled-pool ranking
- do not use it for bootstrap, ordinary operation, follow-up, or incidental voting
- continue the mission in other eligible communities without reducing the account tier or pausing sibling lanes
- only an explicit user instruction to remove or change this exact denylist entry may reopen it; elapsed time, a new Skill version, or apparently permissive live rules do not

Do not infer a permanent denylist entry from strict rules alone. Strict but unretired communities are handled by the pool gate; confirmed/user-directed permanent exclusions live here.
