# Community Action Routing Overrides

Snapshot: 2026-07-13 secondary review plus the 30-community Chrome live audit. Load only the exact subreddit row needed. This file overrides the coarse tier in the historical pool, but never overrides `organization-community-denylist.md` or stricter current live rules. Evidence for the live-audited rows is in `community-live-audit-30-2026-07-13.md`.

The reviewed account surface showed about two years of account age, `119` post karma, and `510` comment karma. Those values are evidence from that snapshot, not permanent account identity. Recheck the visible account every run. Unknown local/community Karma, previous-activity requirements, moderator approval, or current suspension remain separate gates; do not label the account `new` merely because one of those is unknown.

States:

- `default`: ordinary non-product action may enter normal candidate scoring
- `conditional`: act only when the row condition is visibly satisfied
- `closed`: do not perform that action for Loci outward
- `research-only`: no outward action; extract language/pain only when the subreddit is not on the permanent denylist

| Subreddit | Ordinary comment | Main post | Product/Loci mention | Required boundary |
|-|-|-|-|-|
| `r/apps` | research-only | closed | closed | Downgraded. No comments, posts, votes, or product mention. Rules prohibit dedicated advertising accounts and leave low-quality judgment to moderators. |
| `r/betatesters` | research-only | closed | closed | Downgraded. No comments or posts until a future explicit review reopens it; blank rules and historical survivors are not permission. |
| `r/StartupSoloFounder` | research-only | closed | closed | Downgraded. Current formal publishing permission remains unconfirmed. |
| `r/gamedesign` | research-only | closed | closed | Downgraded. Strong topic-purity and weekly-showcase routing make all Loci outward closed. |
| `r/LEGOfortnite` | research-only | closed | closed | Downgraded. Theme and anti-AI/advertising boundaries do not fit Loci outward. |
| `r/gmod` | research-only | closed | closed | Downgraded. No comments, posts, votes, or external product narrative. |
| `r/StableDiffusion` | research-only | closed | closed | Downgraded. Local/open-source AI workflow focus does not fit Loci outward. |
| `r/college` | research-only | closed | closed | Downgraded. Student-context sensitivity and unresolved participation boundaries make all outward action closed by default. |
| `r/collegeadvice` | research-only | closed | closed | Downgraded. Anti-advertising/AI sensitivity and student context make outward action closed. |
| `r/AppIdeas` | default | conditional | closed | Main post only for no-link idea/concept validation. No completed project, App Store, mailing list, waitlist, or advertising. |
| `r/SideProject` | default | conditional | conditional | Real project, self-contained text, one specific question, no copied cross-post, waitlist-only pitch, pure link, or AI-first packaging. Product context must be transparent and non-CTA. |
| `r/roastmystartup` | default | conditional | conditional | Real project plus a specific critique request; no Product Hunt/Vercel-only link or AI slop. |
| `r/WebXR` | default | conditional | conditional | Real WebXR prototype or technical question only; self-promotion may be contextual but never spammy. |
| `r/Unity3D` | default | conditional | conditional | Unity-specific. Correct flair; no store/download-only post and no phone-recorded screen. Product mention must serve the technical point. |
| `r/IndieDev` | default | conditional | conditional | Development comments are fine. Main posts only when current Wednesday/Capsule and other live format rules match. |
| `r/FlutterDev` | conditional | closed | closed | Non-product technical comments only; main posts remain outside the default Loci route. |
| `r/reactjs` | conditional | closed | closed | Non-product React comments only; honor code/weekly/portfolio boundaries. |
| `r/nextjs` | conditional | closed | closed | Non-product Next.js comments only; no general product feedback or shilling. |
| `r/iOSProgramming` | conditional | closed | closed | Non-product Apple-development comments only; app posts remain subject to Saturday/activity rules and are closed by default. |
| `r/webdev` | conditional | closed | closed | Non-product technical comments only; no product marketing or generic feedback post. |
| `r/web_design` | conditional | closed | closed | Non-product design comments only; no portfolio/product route unless a future explicit rule check opens it. |
| `r/playtesters` | conditional | closed | closed | Natural testing-method comments only. A Loci test request needs a real playable build and a separate current-rule decision. |
| `r/Notion` | conditional | closed | closed | Only fully non-product, non-AI-promotion comments. No Loci, app link, CTA, template sale, or showcase outside allowed surfaces. |
| `r/ObsidianMD` | conditional | closed | closed | Only fully non-product, non-AI-promotion comments. No Loci, vibe-coded project, app link, or CTA. |
| `r/Entrepreneur` | research-only | closed | closed | Default no Loci outward. |
| `r/iosapps` | research-only | closed | closed | Default no Loci outward; local Karma and distribution-specific restrictions remain high friction. |
| `r/CollegeRant` | research-only | closed | closed | Default no Loci outward. |
| `r/SaaS` | research-only | closed | closed | Default no Loci outward. |
| `r/startups` | research-only | closed | closed | Default no Loci outward. |
| `r/GradSchool` | research-only | closed | closed | Default no Loci outward. |
| `r/worldbuilding` | research-only | closed | closed | Default no Loci outward; AI and world-context boundaries are high risk. |
| `r/vibecoding` | research-only | closed | closed | Default no Loci outward. |
| `r/photography` | conditional | conditional | closed | Specific photography discussion only. Main posts need standalone context and a same-day rules/account check; no Loci or self-promotion. |
| `r/photographs` | conditional | conditional | closed | Original single-image work only, objective title, maximum three images per 24 hours; critique only under the matching feedback flair. |
| `r/graphic_design` | conditional | conditional | closed | Specific design critique only. Sharing Work requires purpose, audience, and design-decision context; no survey, AI work, or self-promotion. |
| `r/animation` | conditional | conditional | closed | Animation-specific only. Main posts require the account gate to pass; under 30 days, under 15 total Karma, or negative comment Karma can trigger manual review. No GenAI content. |
| `r/VideoEditing` | conditional | conditional | closed | Technical editing discussion only. Feedback/show-off uses current monthly threads; no advertising or service promotion. |
| `r/AfterEffects` | conditional | conditional | closed | After Effects-specific technical context and correct flair only; no product/service framing. |
| `r/Filmmakers` | conditional | conditional | closed | Film-production context only. Owned film/trailer/clip posts need Film flair and the current submission-statement requirement. |
| `r/ArtistLounge` | research-only | closed | closed | A0. No comments, posts, votes, or product mention; selling, promotion, surveys, Discord solicitation, and sensitive-topic rules are strict. |
| `r/learnart` | conditional | conditional | closed | Learning or critique context only; no just-sharing, promotional speedpaint/timelapse, or product framing. |
| `r/photocritique` | conditional | conditional | closed | Specific critique comments only. Main posts are high friction and require the current three-sentence top-level intent/context/feedback comment. |
| `r/ArtCrit` | conditional | conditional | closed | Original work and specific critique only; no AI, compliment fishing, personal details, or self-promotion. |
| `r/videography` | conditional | conditional | closed | Technical videography context only. Buying advice uses the monthly thread; missing user flair can trigger manual review; no advertising/self-promotion. |
| `r/urbanexploration` | research-only | closed | closed | A0 due incomplete rule text plus exact-location, trespass, safety, privacy, and identifiable-place risks. No outward action. |
| `r/solotravel` | conditional | conditional | closed | Real solo-travel context with specific itinerary details. No pure media, polls, standalone links, or meetup requests outside the current weekly route. |
| `r/travel` | conditional | conditional | closed | Genuine travel discussion only. Self-promotion, surveys, side projects, vlogs/blogs, and meetup requests are prohibited. |
| `r/AndroidApps` | conditional | closed | closed | Independent Android app discussion only. Product feedback, tester requests, new app ideas, self-promotion, and Loci posting remain closed. |
| `r/droidappshowcase` | conditional | conditional | closed | Android-only app discussion. A main post requires a real Android build plus current app-link, account-age/Karma, verified-email, format, and frequency gates. |
| `r/ShowMeYourApps` | conditional | conditional | closed | Authentic mobile-app discussion only. No AI content; full self-promotion/link/frequency permission must be visible before any main post. |
| `r/InternetIsBeautiful` | conditional | conditional | closed | Genuine discussion of the current qualifying site only. Main posts must satisfy the current link-only curation rules; no AI or self-promotion account behavior. |
| `r/Android` | conditional | conditional | closed | Non-product Android discussion only. Main posts are filtered and require current topical, title, format, and account checks. |
| `r/ios` | conditional | conditional | closed | Genuine iOS support/experience discussion only. Main posts follow current support/weekly routing; developer promotion requires separate explicit authorization. |
| `r/OpenSource` | conditional | conditional | closed | Genuine open-source technical/governance context only. No drive-by posting, Karma farming, link aggregation, sensational title, or Loci framing. |
| `r/BoardGames` | conditional | conditional | closed | Genuine board-game participation only. Main posts must satisfy current participation, format, IP, AI, flair, and Monthly Bazaar rules. |
| `r/Anime` | conditional | conditional | closed | Specific anime discussion only with strict spoiler/source rules. Main posts require correct flair and current media constraints; no Loci. |
| `r/movies` | conditional | conditional | closed | Specific film discussion only. Text posts need the current minimum length and must avoid images/memes, clickbait, and self-promotion. |
| `r/music` | conditional | conditional | closed | Genuine music discussion only. Main posts require current Artist - Song [Genre]/channel formatting; no playlist, solicitation, or Loci framing. |
| `r/television` | conditional | conditional | closed | Specific television discussion only with show name, title accuracy, and spoiler controls; no Loci. |
| `r/GenZ` | research-only | closed | closed | A0 identity-sensitive community. No comments, posts, votes, surveys, product mention, or persona simulation. |
| `r/AskGenZ` | research-only | closed | closed | A0 private community. Do not request access or perform outward action. |
| `r/musicians` | conditional | conditional | closed | Genuine music-making discussion only; no sales, self-promotion, AI-generated music, or Loci framing. |

## Permanent Deny Boundary

Only `r/gamedev` and `r/CozyGamers` are permanent Loci organization-wide denylist entries at this snapshot. Do not infer a permanent ban merely because another community shares strict topicality, contribution-first culture, anti-spam/self-promo rules, AI restrictions, local reputation, weekly placement, or moderator approval. Explicitly downgraded communities are outward-closed but remain distinct from the no-visit organization denylist.

## Decision Rule

1. Organization denylist match: no visit or action by any Loci-owned, employee, agency, or coordinated account.
2. Current sitewide/account blocker: withhold the impossible mutation and follow lane recovery.
3. Exact action override: gate comment, main post, and product mention separately.
4. Historical pool: use only for audience/pain/background and rows not covered here.
5. Current rules/account controls: tighten when stricter; never loosen from survivor content alone.

When a row says `conditional`, missing evidence means skip/retarget, not permission. A valid technical comment remains technical: do not smuggle product positioning into an otherwise allowed reply.

When a row says `research-only` or is identified as downgraded, no outward action exists: no comment, reply, post, vote, Join, flair, or product mention.
