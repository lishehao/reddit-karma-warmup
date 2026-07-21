#!/usr/bin/env python3
"""Validate the machine-defined plus/minus five-minute wake tolerance."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"
defaults = json.loads((ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8"))
tolerance = defaults["scheduler"].get("heartbeat_trigger_tolerance_seconds")
errors: list[str] = []

if tolerance != 300:
    errors.append(f"tolerance:{tolerance}")

scheduler = (ROOT / "references" / "scheduler-and-heartbeats.md").read_text(encoding="utf-8")
required = (
    "trigger_delta_seconds = actual_wake_utc - intended_due_utc",
    "abs(trigger_delta_seconds) <= tolerance_seconds",
    "trigger_status=ON_TIME_TOLERANCE",
    "Do not notify, reschedule, downgrade, repair",
    "trigger_status=EARLY_OUTSIDE_TOLERANCE",
    "trigger_status=LATE_OUTSIDE_TOLERANCE",
    "Never create a catch-up burst",
    "mission deadline follows terminal cleanup",
)
for needle in required:
    if needle not in scheduler:
        errors.append(f"scheduler_missing:{needle}")

if README.exists() and "`±5 分钟` 内一律视为正常并直接继续" not in README.read_text(encoding="utf-8"):
    errors.append("readme_tolerance")


def resolve(delta_seconds: int) -> str:
    if abs(delta_seconds) <= tolerance:
        return "ON_TIME_TOLERANCE_CONTINUE"
    if delta_seconds < -tolerance:
        return "EARLY_OUTSIDE_TOLERANCE_NOT_DUE"
    return "LATE_OUTSIDE_TOLERANCE_CONTINUE_NO_CATCHUP"


scenarios = {
    "early_301s": resolve(-301),
    "early_300s": resolve(-300),
    "on_time": resolve(0),
    "late_300s": resolve(300),
    "late_301s": resolve(301),
}
expected = {
    "early_301s": "EARLY_OUTSIDE_TOLERANCE_NOT_DUE",
    "early_300s": "ON_TIME_TOLERANCE_CONTINUE",
    "on_time": "ON_TIME_TOLERANCE_CONTINUE",
    "late_300s": "ON_TIME_TOLERANCE_CONTINUE",
    "late_301s": "LATE_OUTSIDE_TOLERANCE_CONTINUE_NO_CATCHUP",
}
if scenarios != expected:
    errors.append(f"scenarios:{scenarios}")

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "tolerance_seconds": tolerance,
    "window": "INCLUSIVE_PLUS_MINUS_5_MINUTES",
    "scenarios": scenarios,
}, ensure_ascii=False, sort_keys=True))
