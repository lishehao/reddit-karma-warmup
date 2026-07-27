# Research and community index

Use this before a `comments` or `posts` packet, and during bootstrap when a
public community shortlist needs refreshing.

## Three evidence layers

1. **Built-in Web Search:** broad current discovery, vocabulary, independent
   sources, duplicate/FAQ risk, and objections. It is mandatory before drafting.
2. **Optional official API index:** public GET-only community metadata, rules,
   and compact hot pointers. It narrows a shortlist.
3. **Logged-in Chrome:** current visible community context/rules, account,
   target, composer, flair, and mutation result. It is the final live gate.

Never use a lower layer to claim a higher layer passed.

## Web Search SOP

Write a compact `research_brief` with decision question, audience, intended
angle, claims/questions, unknowns, and stop condition. Then create a query plan
with distinct purposes—not wording variants—and synthesize findings before
opening finalists in Chrome.

For a post, use 8–12 questions across: community/current discussion;
premise alternatives; duplicate/FAQ risk; and authoritative sources only when
an external claim is intended. For comments, use 4–6 questions across target
community, recent discussion, alternative/objection, and local language. Run
one exact query for the selected target. Add another objection/source query for
a substantive or factual claim. Record unsupported claims and remove or reframe
them before Chrome.

## Optional API index

`scripts/community_index.py` is a local, read-only helper—not a task, daemon,
or Chrome fallback. It runs only with `REDDIT_AUDIT_API_TOKEN` and
`REDDIT_AUDIT_USER_AGENT`; no credentials means `UNCONFIGURED`, not an error.

```text
python scripts/community_index.py status
python scripts/community_index.py refresh --subreddit r/SideProject --subreddit r/indiehackers
python scripts/community_index.py show --subreddit r/SideProject
```

Refresh at most eight shortlisted communities in one bootstrap/expansion pass.
The script uses official OAuth GET endpoints for public `about`, `about/rules`,
and up to three hot pointers; it keeps only compact fields and respects its
configured 30 QPM ceiling. It does not use browser cookies, account endpoints,
comments, post bodies, submit, vote, join, profile, or any write endpoint.

Do not run API refresh to compensate for a Chrome timeout. Do not enable TikHub
by default. A TikHub result, if later deliberately calibrated, can be discovery
only and cannot overwrite official rules or authorize an action.

## Chrome finalist gate

For each Chrome finalist check the exact rule/context, pinned/megathread route,
recent native examples, account/duplicate history, required form/flair, and
whether the drafted text remains truthful. A material change to community,
premise, duplicate risk, or factual claim requires one focused Web Search delta
before drafting or submitting.
