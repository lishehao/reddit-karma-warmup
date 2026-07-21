#!/usr/bin/env python3
"""Validate the minimal successful Bootstrap output and probe-free preflight."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"


def require(path: Path, needles: list[str], errors: list[str]) -> None:
    body = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{path.name}:{needle}")


errors: list[str] = []

require(ROOT / "SKILL.md", [
    "Never create a probe Heartbeat",
    "emit only the Bootstrap Success Prompt",
    "load `references/runtime-and-setup.md`, `references/reddit-surface-routing.md`, `references/chrome-atomic-command-runtime.md`",
], errors)

require(ROOT / "references" / "runtime-and-setup.md", [
    "Do not create, update, or delete a bootstrap test Heartbeat",
    "DOM snapshot, screenshot, or a bounded read-only",
    "chrome_content_channel_timeout",
    "one lightweight metadata transaction under `metadata_timeout_ms`",
    "Claim only a",
    "provably unowned Reddit tab",
    "user, launcher, or sibling-lane tab as fallback",
    "at most one neutral",
    "do not recommend reinstalling or re-enabling the extension",
    "BOOTSTRAP_SUCCESS_OUTPUT_EXACT=true",
    "你希望这个 Reddit 账号往什么方向运营，先运营多久？",
    "方向：指账号接下来主要参与的主题范围",
    "时长：指本轮自动运营持续多久",
    "电脑需要保持开机且不要休眠",
    "Chrome 保持登录",
    "网络尽量稳定",
    "Direction-only answers use `3h`",
    "bootstrap_state=BOOTSTRAP_REPAIR_REQUIRED",
    "bootstrap_state=BOOTSTRAP_AWAITING_OPERATION",
    "`继续`, `开始`, `默认`, or `没想法`",
    "immediately dispatches the first comments + posts + follow-up missions",
    "later bare `继续` in pinned idle must not duplicate the previous mission",
    "Never ask a second confirmation or a second operation question",
], errors)

require(ROOT / "references" / "account-direction.md", [
    "first successful Bootstrap still asks once for this run's direction and duration",
    "direction-only answer defaults to `3h`",
    "Only after a healthy Bootstrap",
    "A repair-state `继续` never reaches direction resolution or dispatch",
    "Legacy clients may still send `确认` or `确认并开始`",
], errors)

if README.exists():
    require(README, [
        "只返回 README 规定的“运营方向 + 运营时长”提问",
        "Bootstrap 不创建测试 Heartbeat",
        "账号预检还需要一个最便宜的页面状态证明",
        "chrome_content_channel_timeout",
        "绝不拿无关用户、启动台或 sibling lane 标签改道",
        "未被其他启动台或执行台的 checkpoint 记录为占用",
        "CHROME_CONTENT_CHANNEL_TIMEOUT",
        "元数据已成功时不建议重装或重新启用扩展",
        "首次 Bootstrap 成功时只返回",
        "关机、休眠、关闭 Chrome 或断网会影响后续轮次",
        "健康 Bootstrap 提问后，用户回复“继续”",
        "只有三条精确任务消息都被对应执行台接受后",
        "只有真实失败时才返回一个最小修复动作",
    ], errors)

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "success_output": "DIRECTION_AND_DURATION_PROMPT_ONLY",
    "technical_success_details": "INTERNAL_ONLY",
    "bootstrap_probe_heartbeat": "FORBIDDEN",
    "missing_direction": "USE_SAVED_OR_DEFAULT",
    "missing_duration": "DEFAULT_3H",
    "uptime_explanation": "REQUIRED",
    "failure_output": "ONE_CONCRETE_REPAIR",
    "healthy_continue": "DISPATCH_DEFAULT_3H_THREE_LANES_NOW",
    "repair_continue": "RECHECK_ONLY",
}, ensure_ascii=False, sort_keys=True))
