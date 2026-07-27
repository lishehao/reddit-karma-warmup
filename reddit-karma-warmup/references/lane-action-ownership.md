# Five-unit Action Ownership

Load in the single `Reddit 运营台` before accepting a mission or revision. The
table defines unit authority; it does not create five separate tasks.

| Unit | May read | Default / explicit mutation | Never does |
| --- | --- | --- | --- |
| `browsing` | authorized listings, posts, media, comment context, rules | `READ_ONLY`; only `VOTE_AUTHORIZED` may vote | text publishing, replies, profile/community changes |
| `comments` | candidates, parent comments, nearby replies, rules | `RESEARCH_ONLY`; `COMMENT_AUTHORIZED` may publish a proactive comment | Upvote/Downvote inspection, posts, inbound replies, presence work |
| `posts` | listings, rules, submit requirements, survivor posts | `RESEARCH_ONLY`; `POST_AUTHORIZED` may publish one compliant native post | Upvote/Downvote inspection, comments, inbound replies, presence work |
| `follow-up` | known own chains, supplied permalinks, inbound surfaces | `RESEARCH_ONLY`; `FOLLOWUP_AUTHORIZED` may reply | Upvote/Downvote inspection, proactive discovery, main posts, presence work |
| `presence` | profile/community presence surfaces | `RESEARCH_ONLY`; `PRESENCE_AUTHORIZED` may make truthful profile/community changes | Upvote/Downvote inspection, text publishing, replies |

Every non-browsing unit resolves:

```text
vote_policy=DISABLED_BY_LANE
vote_cap=0
upvote_count=0
downvote_count=0
vote_target=<absent>
browse_vote_playbook=NOT_LOADED
```

Only a browsing unit with both `VOTE_AUTHORIZED` and
`vote_policy=BROWSING_ONLY` may load or inspect vote controls. A comment, post,
follow-up, or presence unit must ignore votes even if the controls are visible.

An action authority is only an envelope scope. Each outward action still needs
its unit playbook, built-in Web Search when applicable, current live rules,
account/submit gates, a deterministic action key, and exact result verification.
