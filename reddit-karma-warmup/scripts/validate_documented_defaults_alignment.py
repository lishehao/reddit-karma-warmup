#!/usr/bin/env python3
"""Validate that human-facing numeric summaries match canonical defaults."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"
defaults = json.loads((ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8"))
if not README.exists():
    print(json.dumps({
        "status": "PASS",
        "authority": "operation-defaults.json",
        "readme": "NOT_PRESENT_INSTALLED_LAYOUT",
    }, ensure_ascii=False, sort_keys=True))
    raise SystemExit(0)

body = README.read_text(encoding="utf-8")
errors: list[str] = []


def require(fragment: str, label: str) -> None:
    if fragment not in body:
        errors.append(f"readme_mismatch:{label}:{fragment}")


duration = defaults["default_duration_hours"]
phase = defaults["scheduler"]["first_mutation_phase_step_minutes"]
jitter = defaults["scheduler"]["phase_jitter_minutes"]
pacing = defaults["interaction_pacing"]
comments = defaults["comments"]
votes = defaults["votes"]
posts = defaults["posts"]
selection = defaults["community_selection"]
voice = defaults["voice"]
chain = defaults["model_runtime"]["fallback_chain"]

require(f"默认 `{duration} 小时`", "duration")
require(f"`0/{phase}/{phase * 2}/{phase * 3}...` 分钟", "phase")
require(f"`{jitter[0]}-{jitter[1]}` 分钟浮动", "phase_jitter")
require(f"至少停留 `{pacing['candidate_dwell_min_seconds']}` 秒", "candidate_dwell")
require(f"至少 `{pacing['comment_readable_to_submit_min_seconds']}` 秒", "readable_to_submit")
require(f"`{pacing['pre_submit_pause_seconds'][0]}-{pacing['pre_submit_pause_seconds'][1]}` 秒", "pre_submit")
require(f"`{pacing['inter_click_pause_seconds'][0]}-{pacing['inter_click_pause_seconds'][1]}` 秒", "inter_click")
require(
    f"`{comments['proactive_submit_gap_seconds_min'] // 60}-{comments['proactive_submit_gap_seconds_max'] // 60}` 分钟间隔",
    "proactive_submit_gap",
)
require(
    f"`{votes['caps_by_intensity']['low']}/{votes['caps_by_intensity']['standard']}/{votes['caps_by_intensity']['high']}`",
    "vote_caps",
)
require(f"至少 {posts['main_post_unlock_min_combined_karma']} combined Karma", "post_unlock_karma")
require(f"账号满 {posts['main_post_unlock_min_account_age_days']} 天", "post_unlock_age")
require(
    f"至少 {posts['main_post_unlock_min_visible_comments']} 条可见评论分布在 {posts['main_post_unlock_min_eligible_communities']} 个合格社区",
    "post_unlock_history",
)
require(f"最多每 24 小时 {posts['k1_rolling_24h_cap']} 篇", "k1_cap")
require(f"评估最多 {selection['comment_reference_sweep_limit']} 个匹配社区", "reference_sweep")
require(f"各收到最多 {selection['shortlist_limit']} 个", "shortlist")
require(
    f"排名前 {selection['post_live_preflight_community_range'][0]}–{selection['post_live_preflight_community_range'][1]} 个社区",
    "post_live_preflight",
)
require(f"至少抽样 {posts['discussion_survivor_sample_target']} 条", "discussion_samples")
require(f"discussion_potential_score >={posts['discussion_score_min']}", "discussion_score")
require(f"不超过 {comments['routine_word_cap']} 个英文词", "routine_word_cap")
require(
    f"放宽到 {voice['two_beat_word_range'][0]}–{voice['two_beat_word_range'][1]} 词",
    "two_beat_word_range",
)
require(
    "、".join(f"`{row['model']}/{row['reasoning_effort']}`" for row in chain),
    "model_chain",
)

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "authority": "operation-defaults.json",
    "readme": "ALIGNED",
}, ensure_ascii=False, sort_keys=True))
