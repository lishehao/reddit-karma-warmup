#!/usr/bin/env python3
"""Build a lightweight tagged subreddit index from the bundled evidence tables."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "references" / "loci-subreddit-pool-v1.md"
OVERRIDES = ROOT / "references" / "community-action-routing-overrides.md"
DENYLIST = ROOT / "references" / "organization-community-denylist.md"
PUBLIC_AUDIT = ROOT / "references" / "community-action-expansion-public-audit-2026-07-13.md"
TRAFFIC_SNAPSHOT = ROOT / "references" / "reddit-community-search-snapshot-2026-07-14.json"
CATALOG_EXPANSION = ROOT / "references" / "subreddit-catalog-expansion-2026-07-14.csv"
OUTPUT = ROOT / "references" / "subreddit-profile-index.csv"

TAG_RULES = {
    "topic_tags": {
        "product_app": ["app", "应用", "testflight", "mobile product"],
        "startup_builder": ["startup", "builder", "founder", "indie", "side project", "saas"],
        "developer": ["developer", "开发", "coding", "programming", "swift", "react", "nextjs", "flutter", "unity", "unreal"],
        "mobile": ["mobile", "ios", "android", "iphone", "apple vision"],
        "ios": ["ios", "swift", "testflight", "iphone", "visionos"],
        "android": ["android", "google play"],
        "web": ["web", "react", "nextjs", "webxr", "website"],
        "ai": [" ai ", "ai/", "chatgpt", "llm", "stable diffusion", "kindroid", "character ai", "generative"],
        "3d": ["3d", "blender", "modeling", "threejs", "unity", "unreal"],
        "ar_xr": ["augmented", " ar ", "ar/", " vr ", "vr/", "xr", "webxr", "quest", "vision pro", "visionos", "空间交互"],
        "gaming": ["game", "游戏", "minecraft", "roblox", "rec room", "vrchat", "palia", "sims"],
        "virtual_world": ["virtual world", "虚拟世界", "worldbuilding", "avatar", "ugc world", "home decor", "sandbox"],
        "ugc": ["ugc", "creator mechanics", "world builder", "创作者", "共创"],
        "social_relationship": ["社交", "social", "friend", "朋友", "couple", "relationship", "discord", "loneliness", "陪伴"],
        "youth_campus": ["college", "student", "校园", "大学", "genz", "teen", "school", "年轻人"],
        "place": ["地点", "place", "location", "map", "geocach", "wayfarer", "randonaut", "postcard"],
        "travel_outdoor": ["travel", "旅行", "outdoor", "hiking", "camping", "walking", "urban exploration", "geocach"],
        "creative": ["creative", "创作", "creator", "design", "art", "blender", "worldbuilding"],
        "visual_art": ["art", "design", "graphic", "illustration", "3dmodel", "blender"],
        "photography_video": ["photo", "摄影", "video", "videography", "camera", "image"],
        "productivity_learning": ["study", "learning", "productivity", "notion", "obsidian", "education"],
        "entertainment_media": ["movie", "music", "television", "concert", "popheads", "entertainment"],
    },
    "audience_tags": {
        "indie_builder": ["builder", "founder", "indie", "startup", "side project"],
        "developer": ["developer", "开发者", "coding", "programming", "engineer"],
        "early_tester": ["tester", "beta", "alpha", "testflight", "playtest"],
        "student": ["student", "college", "学生", "校园", "大学"],
        "young_adult": ["young adult", "genz", "teen", "年轻人"],
        "mobile_user": ["android user", "ios user", "mobile app user", "iphone user"],
        "web_user": ["website user", "web user", "internet user"],
        "gamer": ["player", "玩家", "game", "gaming"],
        "world_builder": ["world builder", "worldbuilding", "ugc", "virtual world", "sandbox"],
        "spatial_user": ["ar user", "vr user", "quest user", "vision pro", "spatial"],
        "creator": ["creator", "创作者", "creative", "content creation"],
        "artist_designer": ["artist", "designer", "art", "design", "illustrator"],
        "photographer_video_creator": ["photographer", "photography", "videography", "camera", "video creator"],
        "traveler_outdoor": ["traveler", "travel", "hiking", "camping", "walking", "outdoor"],
        "place_explorer": ["place", "location", "geocach", "letterbox", "randonaut", "whereisthis"],
        "social_participant": ["conversation", "social", "friendship", "introvert", "social skills", "penpal"],
        "friends_couples": ["friend", "朋友", "couple", "relationship", "伴侣"],
        "media_fan": ["movie fan", "music fan", "television viewer", "anime fan", "观众", "听众"],
        "ai_user": ["ai user", "chatgpt", "llm", "ai companion", "generative"],
    },
    "need_tags": {
        "feedback_testing": ["feedback", "test", "beta", "critique", "roast", "反馈"],
        "onboarding_ux": ["onboarding", "ux", "ui", "新手引导", "体验"],
        "technical_help": ["technical", "开发", "bug", "help", "support", "架构"],
        "discovery": ["discover", "discovery", "发现", "recommend", "推荐"],
        "lightweight_social": ["轻社交", "small everyday", "check-in", "想到", "轻互动", "friend"],
        "co_creation": ["co-creation", "co creation", "共创", "共同", "collab"],
        "identity_avatar": ["avatar", "character", "identity", "persona", "形象", "人格"],
        "place_memory": ["place memory", "地点记忆", "postcard", "location history", "地点"],
        "creator_distribution": ["distribution", "传播", "showcase", "self-promo", "作品分享", "creator"],
        "privacy_safety": ["privacy", "安全", "隐私", "personal information", "location exposure"],
        "learning_productivity": ["study", "learning", "productivity", "学习", "效率"],
        "entertainment_discussion": ["movie", "music", "television", "concert", "娱乐", "剧情"],
    },
    "format_tags": {
        "comment": ["comment", "评论", "自然互动"],
        "question": ["question", "问题帖", "求助", "help request"],
        "text": ["text", "正文", "经验帖"],
        "image": ["image", "图片", "照片", "screenshot"],
        "video": ["video", "视频", "demo"],
        "critique": ["critique", "roast", "反馈"],
        "showcase": ["showcase", "作品", "demo"],
        "megathread": ["megathread", "weekly thread", "周帖"],
    },
    "risk_tags": {
        "promotion_restricted": ["self-promo", "self promotion", "自推", "广告", "promotion", "no promotions"],
        "survey_restricted": ["survey", "问卷", "market research"],
        "ai_restricted": ["no ai", "禁ai", "ai slop", "ai bots", "ai-generated"],
        "privacy_sensitive": ["privacy", "隐私", "personal information", "个人信息", "location exposure"],
        "minors_sensitive": ["minor", "未成年人", "儿童", "youth"],
        "approval_gate": ["mod approval", "moderator approval", "批准", "approval"],
        "megathread_gate": ["megathread", "weekly thread", "周帖", "指定线程"],
        "account_gate": ["local karma", "community karma", "账号需", "account age", "karma>"],
        "topic_purity": ["must be", "仅限", "必须与", "only"],
        "competitor_context": ["竞品", "official", "平台语境", "必须.*相关"],
    },
}

EXACT_TAG_OVERRIDES = {
    "r/aftereffects": {"topic_tags": ["creative", "photography_video"], "audience_tags": ["creator"], "need_tags": ["technical_help"]},
    "r/android": {"audience_tags": ["mobile_user"], "need_tags": ["technical_help"]},
    "r/androidapps": {"audience_tags": ["mobile_user"]},
    "r/ai_agents": {"need_tags": ["technical_help", "discovery"]},
    "r/animalcrossing": {"need_tags": ["co_creation", "lightweight_social"]},
    "r/apps": {"audience_tags": ["mobile_user", "web_user"]},
    "r/appideas": {"need_tags": ["discovery", "feedback_testing"]},
    "r/anime": {"topic_tags": ["entertainment_media"], "audience_tags": ["media_fan", "young_adult"], "need_tags": ["entertainment_discussion", "identity_avatar"]},
    "r/applevisionpro": {"audience_tags": ["spatial_user"]},
    "r/artcrit": {"topic_tags": ["creative", "visual_art"], "audience_tags": ["artist_designer"], "need_tags": ["feedback_testing"]},
    "r/artistlounge": {"topic_tags": ["creative", "visual_art"], "audience_tags": ["artist_designer"], "need_tags": ["feedback_testing"]},
    "r/askgenz": {"topic_tags": ["social_relationship", "youth_campus"], "audience_tags": ["young_adult"], "need_tags": ["lightweight_social"]},
    "r/boardgames": {"need_tags": ["co_creation", "lightweight_social"]},
    "r/bereal_app": {"need_tags": ["identity_avatar", "lightweight_social"]},
    "r/buddycrossing": {"topic_tags": ["gaming", "social_relationship"], "audience_tags": ["gamer", "social_participant"], "need_tags": ["lightweight_social"]},
    "r/casualconversation": {"audience_tags": ["social_participant"], "need_tags": ["lightweight_social"]},
    "r/chatgpt": {"need_tags": ["discovery", "technical_help"]},
    "r/chatgptcoding": {"need_tags": ["technical_help"]},
    "r/claudeai": {"need_tags": ["technical_help"]},
    "r/college": {"need_tags": ["learning_productivity", "lightweight_social"]},
    "r/collegerant": {"need_tags": ["learning_productivity"]},
    "r/collegeadvice": {"need_tags": ["learning_productivity"]},
    "r/constructedadventures": {"audience_tags": ["place_explorer", "world_builder"]},
    "r/entrepreneur": {"topic_tags": ["startup_builder"], "audience_tags": ["indie_builder"], "need_tags": ["discovery", "feedback_testing"]},
    "r/filmmakers": {"topic_tags": ["creative", "entertainment_media", "photography_video"], "audience_tags": ["creator", "photographer_video_creator"], "need_tags": ["technical_help"]},
    "r/friendship": {"need_tags": ["lightweight_social"]},
    "r/friendshipadvice": {"need_tags": ["lightweight_social"]},
    "r/habbo": {"audience_tags": ["gamer", "world_builder"], "need_tags": ["identity_avatar", "lightweight_social"]},
    "r/gamedesign": {"audience_tags": ["developer", "gamer", "world_builder"], "need_tags": ["co_creation", "technical_help"]},
    "r/gamerpals": {"audience_tags": ["gamer", "social_participant"], "need_tags": ["lightweight_social"]},
    "r/gmod": {"audience_tags": ["gamer", "world_builder"], "need_tags": ["co_creation", "technical_help"]},
    "r/godot": {"audience_tags": ["developer", "gamer"]},
    "r/genz": {"need_tags": ["lightweight_social"]},
    "r/internetisbeautiful": {"topic_tags": ["product_app", "web"], "audience_tags": ["web_user"], "need_tags": ["discovery"]},
    "r/internetfriends": {"need_tags": ["lightweight_social"]},
    "r/indieappcircle": {"audience_tags": ["developer", "indie_builder"]},
    "r/introvert": {"audience_tags": ["social_participant"], "need_tags": ["lightweight_social"]},
    "r/ios": {"audience_tags": ["mobile_user"]},
    "r/iosprogramming": {"need_tags": ["technical_help"]},
    "r/jurassicworldalive": {"audience_tags": ["gamer", "place_explorer"], "need_tags": ["discovery", "place_memory"]},
    "r/kindroidai": {"need_tags": ["identity_avatar", "lightweight_social"]},
    "r/ldr": {"topic_tags": ["social_relationship"], "audience_tags": ["friends_couples"], "need_tags": ["lightweight_social", "place_memory"]},
    "r/letterboxing": {"topic_tags": ["place", "travel_outdoor"], "audience_tags": ["place_explorer", "traveler_outdoor"], "need_tags": ["discovery", "place_memory"]},
    "r/learnart": {"topic_tags": ["creative", "visual_art"], "audience_tags": ["artist_designer"], "need_tags": ["feedback_testing", "learning_productivity"]},
    "r/legofortnite": {"audience_tags": ["gamer", "world_builder"]},
    "r/lightbulb": {"topic_tags": ["product_app", "startup_builder"], "audience_tags": ["indie_builder"], "need_tags": ["discovery", "feedback_testing"]},
    "r/localllama": {"need_tags": ["technical_help"]},
    "r/longdistance": {"audience_tags": ["friends_couples"], "need_tags": ["lightweight_social", "place_memory"]},
    "r/makenewfriendshere": {"need_tags": ["lightweight_social"]},
    "r/movies": {"topic_tags": ["entertainment_media"], "audience_tags": ["media_fan"], "need_tags": ["entertainment_discussion"]},
    "r/music": {"audience_tags": ["media_fan"], "need_tags": ["entertainment_discussion"]},
    "r/musicians": {"audience_tags": ["creator", "media_fan"], "need_tags": ["co_creation"]},
    "r/munzee": {"topic_tags": ["gaming", "place"], "need_tags": ["discovery", "place_memory"]},
    "r/notion": {"audience_tags": ["web_user"]},
    "r/obsidianmd": {"audience_tags": ["web_user"], "need_tags": ["learning_productivity"]},
    "r/ornarpg": {"topic_tags": ["gaming", "place"], "need_tags": ["discovery"]},
    "r/photocritique": {"audience_tags": ["photographer_video_creator"], "need_tags": ["feedback_testing"]},
    "r/photographs": {"need_tags": ["creator_distribution", "discovery"]},
    "r/photography": {"need_tags": ["discovery", "feedback_testing"]},
    "r/penpals": {"audience_tags": ["social_participant"], "need_tags": ["lightweight_social"]},
    "r/ps4dreams": {"need_tags": ["co_creation", "creator_distribution"]},
    "r/randonauts": {"audience_tags": ["place_explorer"]},
    "r/roommates": {"need_tags": ["lightweight_social"]},
    "r/recroom": {"need_tags": ["co_creation", "identity_avatar", "lightweight_social"]},
    "r/replika": {"need_tags": ["identity_avatar", "lightweight_social"]},
    "r/roastmystartup": {"need_tags": ["feedback_testing"]},
    "r/runner5": {"topic_tags": ["gaming", "place", "travel_outdoor"], "audience_tags": ["gamer", "traveler_outdoor"]},
    "r/saas": {"need_tags": ["discovery", "feedback_testing"]},
    "r/secondlife": {"audience_tags": ["gamer", "world_builder"]},
    "r/socialanxiety": {"audience_tags": ["social_participant"], "need_tags": ["lightweight_social"]},
    "r/socialskills": {"audience_tags": ["social_participant"]},
    "r/showmeyourapps": {"audience_tags": ["indie_builder", "mobile_user"]},
    "r/somebodymakethis": {"topic_tags": ["product_app", "startup_builder"], "audience_tags": ["indie_builder"], "need_tags": ["discovery", "feedback_testing"]},
    "r/solotravel": {"need_tags": ["discovery"]},
    "r/stablediffusion": {"need_tags": ["co_creation", "technical_help"]},
    "r/startups": {"need_tags": ["discovery", "feedback_testing"]},
    "r/terraria": {"topic_tags": ["gaming", "virtual_world"], "need_tags": ["co_creation"]},
    "r/television": {"audience_tags": ["media_fan"]},
    "r/travel": {"need_tags": ["discovery"]},
    "r/unrealengine": {"need_tags": ["co_creation", "technical_help"]},
    "r/urbanexploration": {"topic_tags": ["place", "travel_outdoor"], "audience_tags": ["place_explorer", "traveler_outdoor"], "need_tags": ["discovery", "privacy_safety"]},
    "r/videoediting": {"topic_tags": ["creative", "photography_video"], "audience_tags": ["creator", "photographer_video_creator"], "need_tags": ["feedback_testing", "technical_help"]},
    "r/walking": {"need_tags": ["discovery", "place_memory"]},
    "r/walkscape": {"audience_tags": ["gamer", "traveler_outdoor"], "need_tags": ["discovery", "place_memory"]},
    "r/webxr": {"need_tags": ["technical_help"]},
    "r/wemetonline": {"need_tags": ["lightweight_social", "place_memory"]},
    "r/whereisthis": {"audience_tags": ["place_explorer"]},
    "r/widgetable": {"need_tags": ["identity_avatar", "lightweight_social"]},
    "r/zepetosuggestions": {"topic_tags": ["gaming", "social_relationship", "virtual_world"], "audience_tags": ["gamer", "world_builder"]},
}

EXACT_TAG_REMOVALS = {
    "r/indiehackers": {"topic_tags": ["gaming"]},
    "r/iosappsmarketing": {"topic_tags": ["gaming"]},
}


def split_md_row(line: str) -> list[str]:
    raw = line.strip().strip("|")
    return [part.replace("\\|", "|").strip() for part in re.split(r"(?<!\\)\|", raw)]


def table_rows(path: Path, first_header: str) -> list[list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(first_header))
    rows: list[list[str]] = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        rows.append(split_md_row(line))
    return rows


def matched_tags(text: str, rules: dict[str, list[str]]) -> list[str]:
    lowered = f" {text.lower()} "
    found = []
    for tag, patterns in rules.items():
        if any(pattern_matches(lowered, pattern) for pattern in patterns):
            found.append(tag)
    return sorted(found)


def pattern_matches(text: str, pattern: str) -> bool:
    if ".*" in pattern:
        return bool(re.search(pattern, text))
    cleaned = pattern.strip().lower()
    if not cleaned:
        return False
    if any(ord(char) > 127 for char in cleaned) or "/" in cleaned:
        return cleaned in text
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(cleaned)}(?![a-z0-9])", text))


def parse_number(raw: str) -> int:
    cleaned = raw.replace(",", "")
    suffix = cleaned[-1:].lower()
    numeric = cleaned[:-1] if suffix in {"k", "m"} else cleaned
    value = float(numeric)
    if suffix == "k":
        value *= 1_000
    elif suffix == "m":
        value *= 1_000_000
    return int(value)


def traffic_from_text(text: str) -> tuple[str, str, str]:
    visitor_match = re.search(r"([0-9][0-9.,]*\s*[kKmM]?)\s+weekly visitors", text, re.I)
    contribution_match = re.search(r"([0-9][0-9.,]*\s*[kKmM]?)\s+weekly contributions", text, re.I)
    visitors = parse_number(visitor_match.group(1).replace(" ", "")) if visitor_match else None
    contributions = parse_number(contribution_match.group(1).replace(" ", "")) if contribution_match else None
    state = "unknown" if visitors is None else ("pass" if visitors >= 5_000 else "below_floor")
    return str(visitors or ""), str(contributions or ""), state


def load_traffic_snapshot() -> dict[str, tuple[str, str, str, str]]:
    rows = json.loads(TRAFFIC_SNAPSHOT.read_text(encoding="utf-8"))
    result = {}
    for row in rows:
        visitors = parse_number(row["weekly_visitors"])
        contributions = parse_number(row["weekly_contributions"])
        state = "pass" if visitors >= 5_000 else "below_floor"
        result[row["subreddit"].lower()] = (
            str(visitors),
            str(contributions),
            "2026-07-14",
            state,
        )
    return result


def merge_traffic(
    key: str,
    visitors: str,
    contributions: str,
    checked_at: str,
    traffic_state: str,
    snapshot: dict[str, tuple[str, str, str, str]],
) -> tuple[str, str, str, str]:
    return snapshot.get(key, (visitors, contributions, checked_at, traffic_state))


def load_overrides() -> dict[str, tuple[str, str, str]]:
    result = {}
    for row in table_rows(OVERRIDES, "| Subreddit | Ordinary comment"):
        if len(row) < 4:
            continue
        key = row[0].strip("`").lower()
        result[key] = tuple(cell.strip("`").lower() for cell in row[1:4])
    return result


def load_denylist() -> set[str]:
    result = set()
    for row in table_rows(DENYLIST, "| Subreddit | State"):
        if row:
            result.add(row[0].strip("`").lower())
    return result


def default_routes(tier: str) -> tuple[str, str, str]:
    if tier == "B":
        return "default", "conditional", "closed"
    if tier == "B+":
        return "default", "conditional", "closed"
    return "research-only", "closed", "closed"


def normalize_route(raw: str) -> str:
    lowered = raw.strip("` ").lower()
    for state in ("research-only", "conditional", "default", "closed"):
        if lowered.startswith(state):
            return state
    return "closed"


def launcher_state(key: str, tier: str, routes: tuple[str, str, str], denylist: set[str]) -> str:
    if key in denylist or tier in {"A0", "No-go"}:
        return "closed"
    comment, post, _ = routes
    if comment in {"default", "conditional"} or post in {"default", "conditional"}:
        return "candidate"
    return "research_only"


def evidence_level(text: str, key: str, denylist: set[str]) -> str:
    if key in denylist:
        return "deny"
    if "Chrome Batch" in text or "2026-07-11 Chrome" in text or "Chrome 核验" in text:
        return "live_rules"
    return "historical_pool"


def merge_exact_tags(key: str, field: str, generated: list[str]) -> list[str]:
    additions = EXACT_TAG_OVERRIDES.get(key, {}).get(field, [])
    removals = EXACT_TAG_REMOVALS.get(key, {}).get(field, [])
    return sorted((set(generated) | set(additions)) - set(removals))


def main() -> int:
    overrides = load_overrides()
    denylist = load_denylist()
    traffic_snapshot = load_traffic_snapshot()
    output_rows = []
    seen = set()
    for row in table_rows(POOL, "| Subreddit | 层级"):
        if len(row) != 10:
            raise ValueError(f"unexpected pool row width {len(row)}: {row[:2]}")
        subreddit, tier, community_type = row[:3]
        key = subreddit.lower()
        seen.add(key)
        text = " ".join(row)
        # Hot/New snapshots are volatile examples, not durable community identity.
        semantic_text = " ".join([row[0], row[2], row[3], row[4]])
        routes = overrides.get(key, default_routes(tier))
        visitors, contributions, traffic_state = traffic_from_text(text)
        checked_at = "2026-07-13" if visitors else ""
        visitors, contributions, checked_at, traffic_state = merge_traffic(
            key, visitors, contributions, checked_at, traffic_state, traffic_snapshot
        )
        output_rows.append(
            {
                "subreddit": subreddit,
                "tier": tier,
                "community_type": community_type,
                "topic_tags": ";".join(merge_exact_tags(key, "topic_tags", matched_tags(semantic_text, TAG_RULES["topic_tags"]))),
                "audience_tags": ";".join(merge_exact_tags(key, "audience_tags", matched_tags(semantic_text, TAG_RULES["audience_tags"]))),
                "need_tags": ";".join(merge_exact_tags(key, "need_tags", matched_tags(semantic_text, TAG_RULES["need_tags"]))),
                "format_tags": ";".join(matched_tags(text, TAG_RULES["format_tags"])),
                "risk_tags": ";".join(matched_tags(text, TAG_RULES["risk_tags"])),
                "comment_route": routes[0],
                "post_route": routes[1],
                "product_route": routes[2],
                "launcher_state": launcher_state(key, tier, routes, denylist),
                "weekly_visitors": visitors,
                "weekly_contributions": contributions,
                "traffic_checked_at": checked_at,
                "traffic_state": traffic_state,
                "evidence_level": evidence_level(text, key, denylist),
                "source": "loci-subreddit-pool-v1.md",
            }
        )

    for row in table_rows(PUBLIC_AUDIT, "| subreddit | 方向/用户"):
        if len(row) != 8:
            raise ValueError(f"unexpected public-audit row width {len(row)}: {row[:2]}")
        subreddit = row[0].strip("`")
        key = subreddit.lower()
        if key in seen:
            continue
        seen.add(key)
        community_type = row[1]
        semantic_text = " ".join([row[0], row[1], row[5]])
        full_text = " ".join(row)
        public_routes = tuple(normalize_route(value) for value in row[2:5])
        routes = overrides.get(key, public_routes)
        evidence = "public_rules" if "public-rule-confirmed" in row[7] else "catalog_only"
        visitors, contributions, checked_at, traffic_state = merge_traffic(
            key, "", "", "", "unknown", traffic_snapshot
        )
        output_rows.append(
            {
                "subreddit": subreddit,
                "tier": "catalog",
                "community_type": community_type,
                "topic_tags": ";".join(merge_exact_tags(key, "topic_tags", matched_tags(semantic_text, TAG_RULES["topic_tags"]))),
                "audience_tags": ";".join(merge_exact_tags(key, "audience_tags", matched_tags(semantic_text, TAG_RULES["audience_tags"]))),
                "need_tags": ";".join(merge_exact_tags(key, "need_tags", matched_tags(semantic_text, TAG_RULES["need_tags"]))),
                "format_tags": ";".join(matched_tags(full_text, TAG_RULES["format_tags"])),
                "risk_tags": ";".join(matched_tags(full_text, TAG_RULES["risk_tags"])),
                "comment_route": routes[0],
                "post_route": routes[1],
                "product_route": routes[2],
                "launcher_state": launcher_state(key, "catalog", routes, denylist),
                "weekly_visitors": visitors,
                "weekly_contributions": contributions,
                "traffic_checked_at": checked_at,
                "traffic_state": traffic_state,
                "evidence_level": evidence,
                "source": "community-action-expansion-public-audit-2026-07-13.md",
            }
        )

    with CATALOG_EXPANSION.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            subreddit = row["subreddit"]
            key = subreddit.lower()
            if key in seen:
                continue
            seen.add(key)
            output_rows.append(
                {
                    "subreddit": subreddit,
                    "tier": "catalog",
                    "community_type": row["community_type"],
                    "topic_tags": row["topic_tags"],
                    "audience_tags": row["audience_tags"],
                    "need_tags": row["need_tags"],
                    "format_tags": row["format_tags"],
                    "risk_tags": row["risk_tags"],
                    "comment_route": row["comment_route"],
                    "post_route": row["post_route"],
                    "product_route": row["product_route"],
                    "launcher_state": row["launcher_state"],
                    "weekly_visitors": row["weekly_visitors"],
                    "weekly_contributions": row["weekly_contributions"],
                    "traffic_checked_at": row["traffic_checked_at"],
                    "traffic_state": row["traffic_state"],
                    "evidence_level": row["evidence_level"],
                    "source": "subreddit-catalog-expansion-2026-07-14.csv",
                }
            )

    fieldnames = list(output_rows[0])
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(output_rows, key=lambda item: item["subreddit"].lower()))
    print(f"SUBREDDIT_PROFILE_INDEX=BUILT rows={len(output_rows)} output={OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
