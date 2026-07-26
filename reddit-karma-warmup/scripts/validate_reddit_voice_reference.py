#!/usr/bin/env python3
"""Validate the progressive US-leaning Reddit voice reference."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    voice = (ROOT / "references" / "reddit-us-voice-patterns.md").read_text(encoding="utf-8")
    required = [
        "There is no single American voice",
        "Current nearby replies",
        "Stable Patterns",
        "Common Compression",
        "Context-Only Slang",
        "Assertive Moves",
        "dialect performance",
        "Choose the shortest draft",
        "This table ages",
    ]
    errors = [f"missing:{item}" for item in required if item not in voice]

    links = {
        ROOT / "SKILL.md": "reddit-us-voice-patterns.md",
        ROOT / "references" / "outbound-copy-gate.md": "Load `reddit-us-voice-patterns.md`",
    }
    for path, needle in links.items():
        if needle not in path.read_text(encoding="utf-8"):
            errors.append(f"missing_link:{path.name}:{needle}")

    if errors:
        print("REDDIT_VOICE_REFERENCE=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("REDDIT_VOICE_REFERENCE=PASS")
    print("voice=US_LEANING_NOT_MONOLITHIC")
    print("priority=LOCAL_CURRENT_REPLIES")
    print("shape=ASSERTIVE_CONCISE")
    print("stale_filter=ENABLED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
