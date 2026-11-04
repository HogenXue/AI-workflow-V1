#!/usr/bin/env python3
"""Resolve and update explicit third-party Skill ownership without changing payloads."""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import tempfile
from pathlib import Path


def resolve_skill_lock_path(target: Path, logical_cwd: Path | None = None) -> Path:
    """Keep caller-visible ownership while rejecting unverified cwd hints."""
    home = Path(os.environ.get("HOME") or Path.home())
    codex = Path(os.environ.get("CODEX_HOME") or home / ".codex")
    standard = [home / ".agents/skills", codex / "skills", home / ".cursor/skills"]
    physical_cwd = Path.cwd()
    hint = logical_cwd or (Path(os.environ["PWD"]) if os.environ.get("PWD") else None)
    try:
        verified = hint is not None and hint.is_absolute() and hint.samefile(physical_cwd)
    except OSError:
        verified = False
    if logical_cwd is not None and not verified:
        raise ValueError("logical cwd does not identify the current directory")
    cwd = hint if verified else physical_cwd
    if not verified:
        # Preserve configured standard spellings across system aliases such as
        # macOS /var -> /private/var when no verified caller spelling exists.
        for anchor in [home, home / ".agents", codex, home / ".cursor", *standard]:
            try:
                if anchor.samefile(physical_cwd):
                    cwd = anchor
                    break
            except OSError:
                pass
    expanded = target.expanduser()
    logical = Path(os.path.normpath(str(expanded if expanded.is_absolute() else cwd / expanded)))
    if os.path.normcase(str(logical)) in {os.path.normcase(os.path.abspath(p)) for p in standard}:
        state = os.environ.get("XDG_STATE_HOME")
        return Path(state) / "skills/.skill-lock.json" if state else home / ".agents/.skill-lock.json"
    return logical.parent / ".skill-lock.json"


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate lock key: {key}")
        result[key] = value
    return result


def adopt_skill_lock(target: Path, names: list[str], apply: bool) -> list[str]:
    """Preview or atomically detach exact names, preserving all other lock data."""
    try:
        target_stat = target.lstat()
    except FileNotFoundError:
        return []
    if stat.S_ISLNK(target_stat.st_mode):
        raise ValueError("skill lock must be a regular file, not a symlink")
    if not stat.S_ISREG(target_stat.st_mode):
        raise ValueError("skill lock must be a regular file")
    data = json.loads(target.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)
    if not isinstance(data, dict) or not isinstance(data.get("skills"), dict):
        raise ValueError("skill lock must contain a skills mapping")
    detached = [name for name in names if name in data["skills"]]
    if not apply or not detached:
        return detached

    for name in detached:
        del data["skills"][name]
    descriptor, temporary_name = tempfile.mkstemp(prefix=".skill-lock-", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            os.chmod(temporary, stat.S_IMODE(target_stat.st_mode))
            json.dump(data, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return detached


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--resolve-for", type=Path)
    parser.add_argument("--cwd", type=Path)
    parser.add_argument("--skills", nargs="+")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.resolve_for is not None:
        if args.target is not None or args.skills or args.apply:
            parser.error("--resolve-for cannot be combined with lock updates")
        try:
            print(resolve_skill_lock_path(args.resolve_for, args.cwd))
        except (OSError, ValueError) as error:
            print(f"ERROR: skill lock: {error}", file=sys.stderr)
            return 1
        return 0
    if args.cwd is not None or args.target is None or not args.skills:
        parser.error("lock updates require --target and --skills")
    try:
        detached = adopt_skill_lock(args.target, args.skills, args.apply)
    except (OSError, ValueError) as error:
        print(f"ERROR: skill lock: {error}", file=sys.stderr)
        return 1
    for name in detached:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
