# Outbound Copy Gate

This reference was split out of SKILL.md to keep the entrypoint small. Load it only when the SKILL.md routing table says it is needed.

## Outbound Copy Gate

Run this gate before every outward text action: proactive comments, follow-up replies, main posts, and mod/Automod acknowledgements. The goal is to avoid fixed-length, generic, or AI-shaped replies.

Before drafting, decide and record:

- `length_tier`: micro / fragment / one-liner / two-beat / compact paragraph / long only-if-needed
- `why_this_length`: why this target deserves that length, based on thread energy and local style
- `tone`: praise-first, useful nit, crisp question, clarification, playful aside, or direct answer
- `interesting_hook`: the specific detail, contrast, question, or observation that makes the text worth posting
- `local_style_basis`: nearby comment/post style sampled from the target surface
- `avoid_pattern`: what common/generic reply shape to avoid, especially default two-sentence replies
- `length_mix_state`: the last `10` outward comment/reply measurements from `history_ledger`, including `char_count`, `word_count`, `sentence_form`, and `length_tier`
- `comment_fun_score`: for comments/replies only, whether the text is actually worth saying instead of just safe
- `rule_glance`: the one current community rule most relevant to this exact comment/reply
- `context_detail`: one concrete post/media/parent detail the final text will touch
- `duplicate_to_avoid`: the already-dominant answer, joke, or praise frame not to repeat
- `local_voice_sample`: `2-4` short syntax/slang patterns observed in nearby current replies; patterns are evidence, not text to copy
- `native_marker_plan`: the one locally supported compression marker planned for this draft, or `plain_local_voice` with a concrete reason the nearby thread does not support slang
- `native_marker_used`: the exact contraction, fragment, abbreviation, subreddit term, or casual marker present in the final text; `none` requires the recorded `plain_local_voice` reason

Measurement rules:

- `char_count`: count the trimmed final Unicode text, including internal spaces and punctuation. This is the primary cross-language measure.
- `word_count`: count whitespace-delimited tokens. Treat it as secondary for Japanese or other scripts where whitespace is not a reliable word boundary.
- `sentence_form`: `fragment`, `one_sentence`, `two_sentence`, or `paragraph`.
- Measure the exact final text after publishing; do not estimate from the draft.

Length ladder:

| Tier | Typical size | Use when |
|-|-|-|
| `micro` | 1-6 words | simple reaction is enough and nearby replies are short |
| `fragment` | 5-15 words | one sharp observation or praise detail lands better than a full sentence |
| `one-liner` | 8-25 words | most ordinary comments; one idea only |
| `two-beat` | 20-45 words | useful when adding a small contrast, caveat, or question |
| `compact paragraph` | 45-90 words | only for concrete advice, detailed feedback, or nuanced follow-up |
| `long only-if-needed` | 90+ words | rare; only when the target explicitly asks for detailed feedback |

## Comment Copy Gate

Use this stricter gate for proactive comments and follow-up replies. Comments should bias short. A longer comment must earn its length with a concrete insight, useful detail, or direct requested feedback.

Hard default length bias for ordinary comment sessions:

- `80-90%` should be `micro`, `fragment`, or `one-liner`.
- `8-17%` can be `two-beat`.
- `2-5%` can be `compact paragraph`.
- `long only-if-needed` should be exceptional, normally `<1%`.

This is a batch-level hard bias, not a mechanical rotation. If the rolling last `10` comments contain fewer than `8` short-tier comments, the next passing candidate defaults to `micro`, `fragment`, or `one-liner` unless the target explicitly needs depth. Do not lengthen a comment to improve variety.

Before publishing a comment/reply, score `comment_fun_score`:

| Factor | Points | Good signal |
|-|-:|-|
| Specific visible detail | 0-25 | reacts to a concrete thing in the post/comment, not a generic vibe |
| Small insight or useful distinction | 0-25 | adds one crisp idea, contrast, question, or nit |
| Reddit-native local voice | 0-25 | matches nearby length, slang density, contractions, fragments, and energy without imitation |
| Brevity/compression | 0-15 | says only what it needs; no setup sentence if unnecessary |
| Rhythm variation | 0-10 | differs from the last few comments in length/opening/syntax |

Decision:

- `Act`: `>=76`, no blocker, the draft is no longer than needed, and the native-marker gate below passes.
- `Rewrite shorter`: `65-75`, or any draft that defaults to two polished sentences.
- `Skip`: `<65`, generic, summary-like, too long, or only safe praise.

Short-first rewrite rules:

- If the draft is two sentences, test whether it can become one sentence or one fragment. Prefer the shorter version if the meaning survives.
- If a full sentence sounds too polished, use a fragment when local style supports it.
- If the comment only praises, name the exact detail being praised or skip it.
- If the comment adds advice, keep one advice point only.
- If the comment asks a question, ask one question only.
- Compact paragraphs require `comment_fun_score >=85` and an explicit reason: OP asked for feedback, technical advice is useful, or the parent comment needs nuance.
- Long comments require explicit user request, OP request, or a high-value feedback context; otherwise cut to compact paragraph or shorter.

### Reddit-native voice

Use current nearby replies as the primary language source. Across a session, comments should often contain natural Reddit/internet speech, but each individual reply uses only what fits its meaning and subreddit.

Load `reddit-us-voice-patterns.md` after sampling nearby replies. Use it as a fallback pattern table and stale-phrase filter, never as a phrase quota. The current thread and subreddit vocabulary always win.

- contractions and compression: `it's`, `that's`, `I'd`, `doesn't`, `can't`, dropped subjects, sentence fragments
- stance markers: `tbh`, `ngl`, `imo/imho`, `fwiw`, `idk`, `honestly`, `fair`, `yeah`, `nah`
- conversational texture: `kinda`, `pretty`, `lowkey`, `legit`, `wild`, `solid`, `yep`, `lol/lmao` when the thread actually carries that energy
- Reddit references: `OP`, `+1`, `this`, `same`, `username checks out` only when literally relevant
- subreddit-native vocabulary observed in the current thread takes priority over this generic list

Density guidance:

- `micro/fragment`: usually `0-1` marker
- `one-liner`: usually `1-2` markers or one fragment/contraction pattern
- `two-beat`: usually `1-3` markers across the whole reply
- paragraphs: use slang more sparsely so the advice remains readable

Native-marker gate:

- For ordinary non-sensitive sessions, target `60-75%` of published comments with at least one locally supported native marker: a contraction, fragment, abbreviation, subreddit term, compressed connective, or casual stance marker.
- Every `one-liner` or `two-beat` draft must test at least one marker from `local_voice_sample`. Use it only if the meaning stays natural.
- A final draft passes with no marker only when nearby replies are predominantly formal/technical, the topic is sensitive, or the marker would distort the author's voice. Record that reason as `plain_local_voice`.
- Do not satisfy this gate with a random `lol`, `tbh`, or abbreviation. The marker must match the exact thread energy and meaning.

Do not stack abbreviations, force `lol/lmao`, imitate AAVE, invent typos, or use stale canned Reddit lines such as `take my upvote`, `this is the way`, or `sir, this is a Wendy's` unless the current thread itself makes the phrase specifically relevant. The target is native compression, not cosplay.

Rules:

- Read the last `10` measured comment/reply entries before choosing a tier. If the last `3` share the same tier or the rolling set is dominated by one sentence form, explicitly reassess whether the next target naturally supports another shape.
- Do not rotate or randomize tiers mechanically. Change length only when the target's information need and nearby style support it; never add filler or cut a useful point merely to alter the count.
- Keep facts and persona coherent with history while varying length, opening, subreddit, and syntax.
- Do not default to two sentences. Two-beat replies must earn their length.
- If the only draft is generic praise, filler, a summary of the post, or a safe-sounding two-sentence template, skip or rewrite.
- If you cannot state the `interesting_hook` in one line before posting, do not post yet.
- If `rule_glance`, `context_detail`, `duplicate_to_avoid`, `local_voice_sample`, or `native_marker_plan` is missing, do not draft or enter text yet.
- Before entering the draft, produce three internal alternatives: `micro`, `one-liner`, and `two-beat`. Score them for specificity, fun, local voice, and compression; enter only the shortest option that preserves the useful point.
- Prefer shorter than the model's first instinct unless the thread asks for depth.
- For long or medium replies, add natural compression and internet phrasing where appropriate; avoid polished essay cadence.
- After verification, append the measured counts, form, `native_marker_used`, and any `plain_local_voice` reason to `history_ledger` before discovering the next candidate.

## Main Post Copy Shape

- Sample recent surviving native posts in the target subreddit before choosing length and structure.
- Use the shortest body that supplies the context the community expects; do not force comment-length brevity onto a post.
- Compare recent account posts for title pattern, opening, angle, paragraph shape, and length. Avoid repeating all of them together.
- Preserve factual/persona consistency even when the post format changes.
- Run final title/body/flair checks through Double-Check B in `publish-consistency.md`.

Before submission, score the final title/body package separately from the candidate/community score:

| Factor | Points | Simple question |
|-|-:|-|
| Clear hook | 0-25 | Is the reason to read obvious without clickbait? |
| Native subreddit fit | 0-25 | Does it sound and look like a useful native post here? |
| Specific value | 0-20 | Does it provide or ask one concrete thing? |
| Compression | 0-15 | Is it no longer than the community and idea require? |
| Distinct/account-consistent shape | 0-15 | Is it non-duplicative while remaining truthful? |

Publish only at `post_copy_score >=80` with all live eligibility checks still passing. `70-79` rewrites once; `<70` retargets or skips. A copy score never overrides the mandatory post gate.
