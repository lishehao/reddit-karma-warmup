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
    "Never create a bootstrap probe Heartbeat",
    "emit only the Bootstrap Success Prompt",
    "do not expose version, validator count, NOOP/install state",
], errors)

require(ROOT / "references" / "runtime-and-setup.md", [
    "Do not create, update, or delete a bootstrap test Heartbeat",
    "BOOTSTRAP_SUCCESS_OUTPUT_EXACT=true",
    "你希望这个 Reddit 账号往什么方向运营，先运营多久？",
    "方向：指账号接下来主要参与的主题范围",
    "时长：指本轮自动运营持续多久",
    "电脑需要保持开机且不要休眠",
    "Chrome 保持登录",
    "网络尽量稳定",
    "Direction-only answers use `3h`",
    "Never ask a second confirmation or a second operation question",
], errors)

require(ROOT / "references" / "account-direction.md", [
    "first successful Bootstrap still asks once for this run's direction and duration",
    "direction-only answer defaults to `3h`",
    "Legacy clients may still send `确认` or `确认并开始`",
], errors)

if README.exists():
    require(README, [
        "只返回 README 规定的“运营方向 + 运营时长”提问",
        "Bootstrap 不创建测试 Heartbeat",
        "首次 Bootstrap 成功时只返回",
        "关机、休眠、关闭 Chrome 或断网会影响后续轮次",
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
}, ensure_ascii=False, sort_keys=True))
