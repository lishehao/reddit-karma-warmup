#!/usr/bin/env python3
"""Decide and, when requested, atomically apply a fetched Reddit Skill.

It compares the complete Skill tree (not a per-file hash ledger).  The staged
tree must already have passed the Skill validator before ``--apply`` is used.
"""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time


VERSION_RE = re.compile(r"^(\d{4})\.(\d{2})\.(\d{2})\.(\d+)$")
IGNORED_PARTS = {"__pycache__"}


def version(value):
    if not isinstance(value, str):
        raise ValueError("invalid version")
    match = VERSION_RE.fullmatch(value)
    if match is None:
        raise ValueError("invalid version")
    return tuple(int(item) for item in match.groups())


def read_manifest(root):
    path = Path(root) / "manifest.json"
    if not path.is_file():
        raise ValueError("manifest.json missing")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("invalid manifest.json") from exc
    if not isinstance(value, dict) or value.get("name") != "reddit-karma-warmup":
        raise ValueError("invalid Skill manifest")
    return value


def tree(root):
    root = Path(root)
    if not root.is_dir():
        raise ValueError("Skill directory missing")
    result = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in IGNORED_PARTS for part in relative.parts):
            continue
        if path.is_dir():
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError("invalid non-regular Skill entry: " + str(relative))
        result[str(relative)] = path.read_bytes()
    return result


def decision_for(staged, installed):
    staged_manifest = read_manifest(staged)
    staged_version = version(staged_manifest["version"])
    if not Path(installed).is_dir():
        return staged_manifest, None, "HOT_REPLACE_INITIAL", "managed local Skill is missing", tree(staged), {}
    installed_manifest = read_manifest(installed)
    installed_version = version(installed_manifest["version"])
    if staged_manifest.get("schema_version") != installed_manifest.get("schema_version"):
        return staged_manifest, installed_manifest, "DEFER_INCOMPATIBLE", "manifest schema differs", {}, {}
    staged_tree = tree(staged)
    installed_tree = tree(installed)
    changed = sorted(
        name for name in set(staged_tree) | set(installed_tree)
        if staged_tree.get(name) != installed_tree.get(name)
    )
    if staged_version < installed_version:
        decision = "REMOTE_OLDER_IGNORED"
        reason = "downgrade is not implicit"
    elif not changed:
        decision = "NOOP_ALREADY_SYNCED"
        reason = "remote and local trees are identical"
    elif staged_version == installed_version:
        decision = "HOT_REPLACE_SAME_VERSION_DRIFT"
        reason = "remote tree differs despite equal manifest version"
    else:
        decision = "HOT_REPLACE"
        reason = "remote compatible tree is newer"
    return staged_manifest, installed_manifest, decision, reason, staged_tree, installed_tree


def atomic_replace(staged, installed, backup=None):
    staged = Path(staged)
    installed = Path(installed)
    parent = installed.parent
    parent.mkdir(parents=True, exist_ok=True)
    temp_path = Path(tempfile.mkdtemp(prefix=f".{installed.name}.sync-", dir=parent))
    backup_path = None
    moved_old = False
    try:
        payload = temp_path / installed.name
        shutil.copytree(staged, payload, symlinks=False)
        if installed.exists():
            backup_path = Path(backup) if backup else parent / f"{installed.name}.backup-{int(time.time())}"
            if backup_path.exists():
                raise ValueError(f"backup path already exists: {backup_path}")
            os.replace(installed, backup_path)
            moved_old = True
        else:
            backup_path = None
        os.replace(payload, installed)
        return backup_path
    except Exception:
        if moved_old and backup_path and backup_path.exists() and not installed.exists():
            os.replace(backup_path, installed)
        raise
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", required=True, type=Path)
    parser.add_argument("--installed", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--backup", type=Path)
    args = parser.parse_args()
    try:
        staged_manifest, installed_manifest, decision, reason, staged_tree, installed_tree = decision_for(
            args.staged, args.installed
        )
        changed_file_count = len(set(staged_tree) | set(installed_tree)) if decision == "DEFER_INCOMPATIBLE" else len([
            name for name in set(staged_tree) | set(installed_tree)
            if staged_tree.get(name) != installed_tree.get(name)
        ])
        backup_path = None
        if args.apply and decision in {"HOT_REPLACE_INITIAL", "HOT_REPLACE", "HOT_REPLACE_SAME_VERSION_DRIFT"}:
            backup_path = atomic_replace(args.staged, args.installed, args.backup)
            installed_after = tree(args.installed)
            if installed_after != staged_tree:
                raise ValueError("installed readback differs from staged Skill after replace")
            installed_tree = installed_after
            installed_manifest = read_manifest(args.installed)
            decision = "APPLIED_" + decision
        output = {
            "status": "PASS",
            "decision": decision,
            "reason": reason,
            "remote_version": staged_manifest.get("version"),
            "installed_version": installed_manifest.get("version") if installed_manifest else None,
            "tree_equal": staged_tree == installed_tree,
            "changed_file_count": changed_file_count,
        }
        if backup_path is not None:
            output["backup_path"] = str(backup_path)
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
