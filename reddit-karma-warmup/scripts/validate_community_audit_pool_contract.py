#!/usr/bin/env python3
"""Validate the shared public-rule audit-pool contract without network access."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "references"
SCRIPT = ROOT / "scripts" / "community_audit_pool.py"


def require(path: Path, terms: list[str], errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if not text:
        errors.append(f"missing:{path.name}")
        return
    for term in terms:
        if term not in text:
            errors.append(f"missing:{path.name}:{term}")


def run(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return json.loads(result.stdout)


def main() -> int:
    errors: list[str] = []
    require(
        ROOT / "SKILL.md",
        [
            "Reddit 社区审计服务",
            "Only `Reddit 启动台`",
            "GET-only",
            "Chrome live gates",
        ],
        errors,
    )
    require(
        REFERENCES / "community-audit-pool.md",
        [
            "local script/service, not a user-visible Codex task",
            "Reddit 启动台",
            "one local writer",
            "TikHub is optional enrichment only",
            "Actual content browsing remains Chrome-only",
            "Never use timing randomness",
        ],
        errors,
    )
    require(
        REFERENCES / "runtime-and-setup.md",
        ["community_audit_pool.py init", "tasks only read the latest completed snapshot"],
        errors,
    )
    require(
        REFERENCES / "community-selection-funnel.md",
        ["never call a provider from", "API cache replaces repeated public-rule scraping"],
        errors,
    )
    require(
        REFERENCES / "interaction-pacing.md",
        ["Purposeful Visible Chrome Reading", "Never add random delay", "API as a per-item browsing surface"],
        errors,
    )
    defaults = json.loads((REFERENCES / "operation-defaults.json").read_text(encoding="utf-8"))
    pool = defaults.get("community_audit_pool", {})
    expected = {
        "owner": "REDDIT_LAUNCHER_ONLY",
        "provider_default": "official_reddit",
        "provider_write_policy": "GET_ONLY_NO_REDDIT_MUTATION",
        "lanes_may_refresh": False,
        "content_browsing_surface": "CHROME_ONLY",
        "official_oauth_documented_qpm_baseline": 100,
        "operating_qpm": 60,
        "unauthenticated_api_policy": "DISABLED",
        "one_local_writer": True,
    }
    for key, value in expected.items():
        if pool.get(key) != value:
            errors.append(f"defaults:{key}")
    if pool.get("small_hot_pointer_limit_per_community", 99) > 3:
        errors.append("defaults:hot_pointer_limit")

    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "pool"
        initialized = run("--root", str(root), "init")
        current = run("--root", str(root), "status")
        exported = run("--root", str(root), "export", "--output", str(root / "reference.csv"))
        if initialized.get("status") != "INITIALIZED":
            errors.append("script:init")
        if current.get("snapshot_count") != 0:
            errors.append("script:initial_status")
        if exported.get("rows") != 0 or not (root / "reference.csv").is_file():
            errors.append("script:export")

    source = SCRIPT.read_text(encoding="utf-8") if SCRIPT.exists() else ""
    for term in (
        "method=\"GET\"",
        "REFRESH_IN_PROGRESS",
        "RATE_PAUSED_UNTIL",
        "MISSING_OFFICIAL_API_CREDENTIALS",
        "compact_hot_pointers",
        "hot pointer limit must be 1..3",
    ):
        if term not in source:
            errors.append(f"script_term:{term}")
    forbidden = ("/api/submit", "/api/comment", "/api/vote", "method=\"POST\"")
    for term in forbidden:
        if term in source:
            errors.append(f"forbidden_api_mutation:{term}")

    if errors:
        print("COMMUNITY_AUDIT_POOL_CONTRACT=FAIL")
        print("\n".join(f"- {item}" for item in errors))
        return 1
    print("COMMUNITY_AUDIT_POOL_CONTRACT=PASS")
    print("owner=REDDIT_LAUNCHER_ONLY")
    print("provider=OFFICIAL_REDDIT_GET_ONLY")
    print("content_browsing=CHROME_ONLY")
    print("tikhub=OPTIONAL_ENRICHMENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
