#!/usr/bin/env python3
"""Validate public packaging metadata for the single-owner release."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    assert version == "2026.07.27.2"
    readme_path = ROOT.parent / "README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.is_file() else ""
    agent = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    if readme_path.is_file():
        assert "Protocol version: `" + version + "`" in readme
        assert "Reddit 运营台" in readme
    assert "five-unit" in agent
    assert "single-owner" in agent
    for path in (
        ROOT / "references" / "single-owner-runtime.md",
        ROOT / "references" / "one-prompt-runtime.md",
        ROOT / "scripts" / "compile_single_owner_mission.py",
        ROOT / "scripts" / "single_owner_queue.py",
    ):
        assert path.is_file(), str(path)
    print(json.dumps({
        "status": "PASS", "version": version, "chrome_calls": 0,
        "root_readme": "PRESENT" if readme_path.is_file() else "OPTIONAL_ABSENT",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
