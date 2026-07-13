#!/usr/bin/env python3
"""Validate the per-comment rule, context, voice, and brevity gate."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    required = {
        ROOT / "references" / "publish-consistency.md": [
            "quick rule glance",
            "context_detail",
            "duplicate_to_avoid",
            "local_voice_sample",
            "at least `3` nearby/top replies",
        ],
        ROOT / "references" / "outbound-copy-gate.md": [
            "Reddit-native voice",
            "micro/fragment",
            "three internal alternatives",
            "native compression, not cosplay",
        ],
        ROOT / "references" / "proactive-playbook.md": [
            "Missing rule/context/voice evidence is `Watch`",
            "micro/one-liner/two-beat alternatives",
            "Choose the shortest passing alternative",
        ],
    }
    errors = []
    for path, needles in required.items():
        body = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in body:
                errors.append(f"missing:{path.name}:{needle}")

    if errors:
        print("COMMENT_REVIEW_CONTRACT=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("COMMENT_REVIEW_CONTRACT=PASS")
    print("rule_check=QUICK_CURRENT")
    print("context=POST_PARENT_NEARBY_REPLIES")
    print("voice=LOCAL_REDDIT_NATIVE")
    print("drafts=MICRO_ONE_LINER_TWO_BEAT")
    print("selection=SHORTEST_PASSING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
