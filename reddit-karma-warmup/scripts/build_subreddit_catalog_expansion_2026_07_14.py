#!/usr/bin/env python3
"""Build the curated 2026-07-14 discovery catalog from the packaged search snapshot."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "references" / "reddit-community-search-snapshot-2026-07-14.json"
OUTPUT = ROOT / "references" / "subreddit-catalog-expansion-2026-07-14.csv"


CATEGORIES = {
    "gaming_general": {
        "community_type": "泛游戏讨论与选择",
        "audience_summary": "活跃玩家、游戏购买者与求推荐用户",
        "pain_summary": "想找到值得玩的游戏、判断玩法是否有趣，并交换真实体验",
        "topic_tags": "gaming;entertainment_media",
        "audience_tags": "gamer;young_adult",
        "need_tags": "discovery;entertainment_discussion",
        "format_tags": "comment;question;text",
        "risk_tags": "promotion_restricted;topic_purity",
    },
    "gaming_social": {
        "community_type": "社交游戏、共玩与世界玩法",
        "audience_summary": "重视共玩、社区玩法、虚拟空间或游戏创作的玩家",
        "pain_summary": "想找到能与他人一起参与、持续发现或共同创造的玩法",
        "topic_tags": "gaming;social_relationship;virtual_world",
        "audience_tags": "gamer;social_participant;world_builder",
        "need_tags": "co_creation;discovery;lightweight_social",
        "format_tags": "comment;question;text;showcase",
        "risk_tags": "promotion_restricted;topic_purity;competitor_context",
    },
    "film_tv": {
        "community_type": "电影与电视泛娱乐讨论",
        "audience_summary": "电影、电视和流行文化爱好者",
        "pain_summary": "想快速获得推荐、解释作品体验，并围绕共同兴趣交流",
        "topic_tags": "entertainment_media",
        "audience_tags": "media_fan;young_adult",
        "need_tags": "discovery;entertainment_discussion",
        "format_tags": "comment;question;text",
        "risk_tags": "promotion_restricted;topic_purity",
    },
    "anime": {
        "community_type": "动漫兴趣与推荐讨论",
        "audience_summary": "动漫受众、年轻兴趣社群与角色文化爱好者",
        "pain_summary": "想获得作品推荐、讨论角色与身份投射，并找到同好",
        "topic_tags": "entertainment_media;social_relationship",
        "audience_tags": "media_fan;young_adult",
        "need_tags": "discovery;entertainment_discussion;identity_avatar",
        "format_tags": "comment;question;text",
        "risk_tags": "promotion_restricted;topic_purity;minors_sensitive",
    },
    "music": {
        "community_type": "音乐兴趣、创作与传播",
        "audience_summary": "音乐听众、年轻乐迷、音乐创作者与推广者",
        "pain_summary": "想发现音乐、讨论审美、展示作品并获得传播反馈",
        "topic_tags": "creative;entertainment_media",
        "audience_tags": "creator;media_fan;young_adult",
        "need_tags": "creator_distribution;discovery;entertainment_discussion",
        "format_tags": "comment;question;text;showcase",
        "risk_tags": "promotion_restricted;topic_purity",
    },
    "photo": {
        "community_type": "摄影作品、技巧与审美反馈",
        "audience_summary": "摄影爱好者、视觉创作者与城市记录者",
        "pain_summary": "想提升作品、获得具体反馈，并发现值得记录的视觉与地点",
        "topic_tags": "creative;photography_video;place",
        "audience_tags": "photographer_video_creator;place_explorer",
        "need_tags": "creator_distribution;discovery;feedback_testing;place_memory",
        "format_tags": "comment;critique;image;question",
        "risk_tags": "promotion_restricted;privacy_sensitive;topic_purity",
    },
    "art_design": {
        "community_type": "艺术、设计与创作反馈",
        "audience_summary": "艺术家、设计师、创作者与学习者",
        "pain_summary": "想展示作品、得到具体建议，并改善视觉表达或创作流程",
        "topic_tags": "creative;visual_art",
        "audience_tags": "artist_designer;creator",
        "need_tags": "creator_distribution;feedback_testing;learning_productivity",
        "format_tags": "comment;critique;image;question;showcase",
        "risk_tags": "promotion_restricted;topic_purity",
    },
    "place_travel": {
        "community_type": "旅行、户外、城市与地点发现",
        "audience_summary": "旅行者、步行者、户外参与者与城市探索者",
        "pain_summary": "想发现真实地点、规划体验、记录见闻并交流安全边界",
        "topic_tags": "place;travel_outdoor",
        "audience_tags": "place_explorer;traveler_outdoor",
        "need_tags": "discovery;place_memory;privacy_safety",
        "format_tags": "comment;image;question;text",
        "risk_tags": "privacy_sensitive;promotion_restricted;topic_purity",
    },
    "productivity": {
        "community_type": "效率、习惯与工具讨论",
        "audience_summary": "学生、年轻职场用户与效率工具使用者",
        "pain_summary": "想减少拖延、形成持续习惯，并找到低负担的工具或方法",
        "topic_tags": "product_app;productivity_learning",
        "audience_tags": "student;young_adult",
        "need_tags": "discovery;learning_productivity;onboarding_ux",
        "format_tags": "comment;question;text",
        "risk_tags": "promotion_restricted;topic_purity",
    },
    "social_youth": {
        "community_type": "年轻人、朋友与轻社交讨论",
        "audience_summary": "年轻人、内向用户、寻找朋友或关系建议的用户",
        "pain_summary": "想低压力地认识人、维持关系、表达情绪并获得同伴回应",
        "topic_tags": "social_relationship;youth_campus",
        "audience_tags": "social_participant;young_adult",
        "need_tags": "lightweight_social;privacy_safety",
        "format_tags": "comment;question;text",
        "risk_tags": "minors_sensitive;privacy_sensitive;promotion_restricted",
    },
    "ai_companion": {
        "community_type": "AI 陪伴、人格与关系讨论",
        "audience_summary": "AI companion 用户、数字人格爱好者与关系型 AI 使用者",
        "pain_summary": "想获得持续陪伴、人格一致性与安全的情感表达空间",
        "topic_tags": "ai;social_relationship;virtual_world",
        "audience_tags": "ai_user;social_participant",
        "need_tags": "identity_avatar;lightweight_social;privacy_safety",
        "format_tags": "comment;question;text",
        "risk_tags": "competitor_context;privacy_sensitive;promotion_restricted",
    },
    "app_product": {
        "community_type": "移动应用、产品与开发讨论",
        "audience_summary": "移动应用用户、独立开发者、产品设计者与早期体验者",
        "pain_summary": "想发现可用产品、解决开发和体验问题，并获得具体产品反馈",
        "topic_tags": "mobile;product_app;startup_builder",
        "audience_tags": "early_tester;indie_builder;mobile_user",
        "need_tags": "discovery;feedback_testing;onboarding_ux;technical_help",
        "format_tags": "comment;question;text",
        "risk_tags": "account_gate;promotion_restricted;topic_purity",
    },
    "spatial_3d": {
        "community_type": "3D、VR 与空间计算生态",
        "audience_summary": "3D 创作者、VR 玩家和空间计算用户",
        "pain_summary": "想理解空间体验、改善创作流程，并发现更自然的沉浸式交互",
        "topic_tags": "3d;ar_xr;creative;virtual_world",
        "audience_tags": "creator;gamer;spatial_user",
        "need_tags": "co_creation;discovery;technical_help",
        "format_tags": "comment;question;showcase;video",
        "risk_tags": "competitor_context;promotion_restricted;topic_purity",
    },
}


SELECTIONS = {
    "gaming_general": [
        "r/gaming", "r/Games", "r/ShouldIbuythisgame", "r/gamingsuggestions",
        "r/gamesuggestions", "r/AskGames", "r/GirlGamers", "r/AdultGamers",
    ],
    "gaming_social": [
        "r/CitiesSkylines", "r/soloboardgaming", "r/GamesOnReddit", "r/WebGames",
        "r/localmultiplayergames", "r/BoardgameDesign",
    ],
    "film_tv": [
        "r/FIlm", "r/MovieSuggestions", "r/Cinema", "r/MoviesAndTVTalk",
        "r/moviequestions", "r/films",
    ],
    "anime": [
        "r/animequestions", "r/Animesuggest", "r/AnimeReccomendations",
        "r/AnimeDiscussion", "r/AnimeAlley",
    ],
    "music": [
        "r/LetsTalkMusic", "r/WeAreTheMusicMakers", "r/musicmarketing",
        "r/musicteenager", "r/MusicPromotion",
    ],
    "photo": [
        "r/itookapicture", "r/AskPhotography", "r/streetphotography",
        "r/AmateurPhotography", "r/filmphotography", "r/PhotographyAdvice",
        "r/FineArtPhoto",
    ],
    "art_design": [
        "r/Art", "r/crafts", "r/Design", "r/DigitalArt", "r/UXDesign",
        "r/BeginnerArtists", "r/DigitalPainting", "r/webdesign",
        "r/instructionaldesign", "r/DesignJobs",
    ],
    "place_travel": [
        "r/UrbanHell", "r/TravelHacks", "r/roadtrip", "r/backpacking",
        "r/CampingandHiking", "r/WildernessBackpacking", "r/Urbanism",
        "r/traveladvice", "r/Outdoors", "r/Urbex", "r/CityPorn", "r/walkingpics",
    ],
    "productivity": [
        "r/productivity", "r/getdisciplined", "r/Productivitycafe",
        "r/ProductivityApps", "r/ProductivityHQ",
    ],
    "social_youth": [
        "r/IntrovertsChat", "r/DatingApps", "r/GenZHumor", "r/MakeRedditFriends",
        "r/Students", "r/IntrovertsSafeDating", "r/FRIEND",
    ],
    "ai_companion": ["r/MyBoyfriendIsAI", "r/AIRelationships", "r/aipartners"],
    "app_product": ["r/socialmedia", "r/IPhoneApps", "r/AppDevelopers"],
    "spatial_3d": ["r/blender", "r/oculus", "r/VRGaming"],
}


def parse_metric(raw: str) -> int:
    value = raw.strip()
    suffix = value[-1:].upper()
    numeric = value[:-1] if suffix in {"K", "M"} else value
    result = float(numeric)
    if suffix == "K":
        result *= 1_000
    elif suffix == "M":
        result *= 1_000_000
    return int(result)


def main() -> int:
    snapshot_rows = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    snapshot = {row["subreddit"].lower(): row for row in snapshot_rows}
    output_rows = []
    seen = set()
    for category_name, subreddits in SELECTIONS.items():
        category = CATEGORIES[category_name]
        for subreddit in subreddits:
            key = subreddit.lower()
            if key in seen:
                raise ValueError(f"duplicate selection: {subreddit}")
            if key not in snapshot:
                raise ValueError(f"selection missing from snapshot: {subreddit}")
            seen.add(key)
            evidence = snapshot[key]
            visitors = parse_metric(evidence["weekly_visitors"])
            contributions = parse_metric(evidence["weekly_contributions"])
            if visitors < 5_000:
                raise ValueError(f"selection below traffic floor: {subreddit} {visitors}")
            output_rows.append(
                {
                    "subreddit": evidence["subreddit"],
                    **category,
                    "comment_route": "research-only",
                    "post_route": "closed",
                    "product_route": "closed",
                    "launcher_state": "research_only",
                    "weekly_visitors": visitors,
                    "weekly_contributions": contributions,
                    "traffic_checked_at": "2026-07-14",
                    "traffic_state": "pass",
                    "evidence_level": "traffic_verified",
                    "source_query": ";".join(evidence.get("queries") or [evidence.get("query", "")]),
                    "description": evidence.get("description", ""),
                }
            )

    fieldnames = list(output_rows[0])
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(output_rows, key=lambda row: row["subreddit"].lower()))
    print(f"SUBREDDIT_CATALOG_EXPANSION=BUILT rows={len(output_rows)} output={OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
