#!/usr/bin/env python3
"""Validate action-specific community routing overrides."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "references" / "community-action-routing-overrides.md"


def main() -> int:
    body = REFERENCE.read_text(encoding="utf-8")
    rows = re.findall(r"^\| `r/([^`]+)` \|", body, flags=re.MULTILINE)
    required_rows = {
        "apps", "betatesters", "StartupSoloFounder", "gamedesign",
        "AppIdeas", "SideProject", "roastmystartup", "WebXR", "Unity3D",
        "IndieDev", "FlutterDev", "reactjs", "nextjs", "iOSProgramming",
        "webdev", "web_design", "playtesters", "Notion", "ObsidianMD",
        "Entrepreneur", "iosapps", "CollegeRant", "SaaS", "startups",
        "GradSchool", "worldbuilding", "vibecoding",
    }
    errors = []
    missing = sorted(required_rows - set(rows), key=str.casefold)
    if missing:
        errors.append("missing_rows:" + ",".join(missing))
    if len(rows) != len(set(name.casefold() for name in rows)):
        errors.append("duplicate_rows")
    downgraded = {
        "apps", "betatesters", "StartupSoloFounder", "gamedesign",
        "LEGOfortnite", "gmod", "StableDiffusion", "collegeadvice",
    }
    for subreddit in downgraded:
        pattern = rf"^\| `r/{re.escape(subreddit)}` \| research-only \| closed \| closed \|"
        if not re.search(pattern, body, flags=re.MULTILINE | re.IGNORECASE):
            errors.append(f"downgrade_not_closed:{subreddit}")
    for needle in (
        "comment, main post, and product mention separately",
        "Only `r/gamedev` and `r/CozyGamers`",
        "never loosen from survivor content alone",
        "do not label the account `new`",
    ):
        if needle not in body:
            errors.append(f"missing_contract:{needle}")

    links = {
        ROOT / "SKILL.md": "community-action-routing-overrides.md",
        ROOT / "references" / "proactive-playbook.md": "Gate the requested action independently",
        ROOT / "references" / "publish-consistency.md": "never collapse them into one community tier",
    }
    for path, needle in links.items():
        if needle not in path.read_text(encoding="utf-8"):
            errors.append(f"missing_link:{path.name}:{needle}")

    if errors:
        print("ACTION_ROUTING_OVERRIDES=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("ACTION_ROUTING_OVERRIDES=PASS")
    print(f"override_rows={len(rows)}")
    print("routing=COMMENT_POST_PRODUCT_SPLIT")
    print("organization_permanent_deny=r/gamedev,r/CozyGamers")
    print("downgraded=RESEARCH_ONLY_NO_OUTWARD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
