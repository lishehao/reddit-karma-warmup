# Research and community index

Use this before a `comments` or `posts` packet, and during bootstrap when a
public community shortlist needs refreshing.

## Three evidence layers

1. **Built-in Web Search:** broad current discovery, vocabulary, independent
   sources, duplicate/FAQ risk, and objections. It is mandatory for posts;
   comments use it only when a factual, technical, or unfamiliar claim needs it.
2. **Optional official API index:** public GET-only community metadata, rules,
   and compact hot pointers. It narrows a shortlist.
3. **Logged-in Chrome:** current visible community context/rules, session
   identity,
   target, composer, flair, and mutation result. It is the final live gate.

Never use a lower layer to claim a higher layer passed.

Global exclusion: `r/saas` is never an allowed research or action target. Do not
open it in Chrome or query it through the optional API index; remove it from
candidate packs and reject direct assignments to it.

## Web Search SOP

Posts require a compact `research_brief` and distinct-purpose query plan before
opening finalists in Chrome. A short comment normally needs no brief or search;
read the target and nearby context directly, and add one focused query only if
the comment would introduce a factual, technical, or unfamiliar claim.

For a post, normally use 4–8 questions across community/current discussion,
duplicate risk, and any claim that needs support. For comments, use 0–1 query,
only when it adds information. Stop when the decision is clear. Record
unsupported claims and remove or reframe them before Chrome.

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

For a post finalist check the exact rule/context, pinned/megathread route,
recent native examples, account/duplicate history, required form/flair, and
truthfulness. For a comment, check only the target context, a basic current
rule or fresh cache, and the same-target duplicate risk. A material factual
claim still gets one focused Web Search delta before submitting.
