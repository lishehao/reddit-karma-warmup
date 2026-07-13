# Permanent Subreddit Ban Issue Reporting

Load only when current Reddit UI or Modmail explicitly states that the visible account is permanently banned from a named subreddit.

## Trigger Gate

Trigger only with all three:

1. exact subreddit is visible;
2. source is Reddit UI or Modmail visible in the authorized session;
3. wording explicitly means permanent community ban, such as `permanently banned from participating in r/...`.

Do not trigger for a removed post/comment, awaiting approval, temporary ban, sitewide temporary suspension, warning, rate limit, shadowban suspicion, strict rules, inaccessible page, or historical inference.

## Immediate Action

- Stop all actions in that subreddit for this lane and retarget elsewhere.
- Do not revisit the subreddit to collect more evidence.
- Preserve only the minimum event fields: normalized subreddit, observed local time and timezone, source type, action lane, Skill version, and a short paraphrase of the visible evidence.
- Do not ask the user for confirmation and do not pause the lane.

## Issue Destination And Dedupe

Repository: `lishehao/reddit-karma-warmup`

Marker: `PERMANENT_SUBREDDIT_BAN:<lowercase_subreddit_without_r_prefix>`

Before creating an Issue, search open and closed Issues for the exact marker. If one exists, record its URL and do not create or comment on a duplicate unless the user explicitly requests an update.

Create when no marker exists:

```text
Title: Permanent subreddit ban detected: r/<name>

Body:
<!-- PERMANENT_SUBREDDIT_BAN:<lowercase_name> -->

## Event
- Subreddit: r/<name>
- Observed at: <local ISO time with UTC offset>
- Source: <Reddit UI | Modmail>
- Lane: <comments | posts | follow-up | browsing | presence>
- Skill version: <version>
- Evidence: <short sanitized paraphrase; no username or moderator identity>

## Requested repository action
- Review for addition to the organization community denylist.
- Keep all Loci-associated accounts out of this community unless the repository owner explicitly reverses it.
```

## Authenticated Creation Route

Use one already-available authenticated GitHub surface in this order:

1. connected GitHub app/tool with Issue creation;
2. authenticated GitHub CLI/API;
3. the user's logged-in Chrome GitHub session in a separate task-owned tab.

This event-specific authorization permits creating this one sanitized Issue without a second confirmation. It does not grant broader repository write access.

GitHub authentication is not a setup dependency. Never request or expose a token, password, Cookie, or credential. Never place Reddit username, account URL, email, IP, device data, moderator identity, private Modmail link, or screenshot containing private data in a public Issue.

## Failure And Retry

If no authenticated GitHub route is available or creation fails:

- record `ban_issue_status=pending_retry`, the marker, sanitized body, exact failure class, and no secret;
- continue the Reddit lane in other eligible communities;
- retry once on the next normal Heartbeat, checking dedupe again first;
- keep later failures as a concise lane-local risk; never disable the lane Heartbeat or other Reddit work.

After successful creation, record `ban_issue_status=created`, Issue URL, marker, and `subreddit_retired=true`. Do not repeatedly reopen or verify the Issue.
