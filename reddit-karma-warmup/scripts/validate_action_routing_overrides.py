#!/usr/bin/env python3
"""Validate action-specific community routing overrides."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "references" / "community-action-routing-overrides.md"
LIVE_AUDIT = ROOT / "references" / "community-live-audit-30-2026-07-13.md"


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
        "photography", "photographs", "graphic_design", "animation",
        "VideoEditing", "AfterEffects", "Filmmakers", "ArtistLounge",
        "learnart", "photocritique", "ArtCrit", "videography",
        "urbanexploration", "solotravel", "travel", "AndroidApps",
        "droidappshowcase", "ShowMeYourApps", "InternetIsBeautiful",
        "Android", "ios", "OpenSource", "BoardGames", "Anime", "movies",
        "music", "television", "GenZ", "AskGenZ", "musicians",
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
    a0_rows = {"ArtistLounge", "urbanexploration", "GenZ", "AskGenZ"}
    for subreddit in a0_rows:
        pattern = rf"^\| `r/{re.escape(subreddit)}` \| research-only \| closed \| closed \|"
        if not re.search(pattern, body, flags=re.MULTILINE | re.IGNORECASE):
            errors.append(f"a0_not_closed:{subreddit}")
    for needle in (
        "comment, main post, and product mention separately",
        "Only `r/gamedev` and `r/CozyGamers`",
        "never loosen from survivor content alone",
        "do not label the account `new`",
    ):
        if needle not in body:
            errors.append(f"missing_contract:{needle}")

    live_body = LIVE_AUDIT.read_text(encoding="utf-8")
    live_rows = re.findall(r"^\| `r/([^`]+)` \| live_checked(?:_manual|_private)? \|", live_body, flags=re.MULTILINE)
    if len(live_rows) != 30:
        errors.append(f"live_audit_row_count:{len(live_rows)}")
    if len(live_rows) != len(set(name.casefold() for name in live_rows)):
        errors.append("live_audit_duplicate_rows")
    for needle in (
        "B=4, B+=6, A=16, A0=4, No-go=0",
        "A visible submit composer is not posting permission",
        "r/gamedev` and `r/CozyGamers` were not visited",
    ):
        if needle not in live_body:
            errors.append(f"missing_live_audit_contract:{needle}")

    links = [
        (ROOT / "SKILL.md", "community-action-routing-overrides.md"),
        (ROOT / "SKILL.md", "community-live-audit-30-2026-07-13.md"),
        (ROOT / "references" / "proactive-playbook.md", "Gate the requested action independently"),
        (ROOT / "references" / "publish-consistency.md", "never collapse them into one community tier"),
    ]
    for path, needle in links:
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
