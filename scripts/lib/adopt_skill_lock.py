#!/usr/bin/env python3
"""Detach package-owned Skill names from an adjacent third-party update lock."""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import tempfile
from pathlib import Path


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
    data = json.loads(target.read_text(encoding="utf-8"))
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
            os.fchmod(stream.fileno(), stat.S_IMODE(target_stat.st_mode))
            json.dump(data, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return detached


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--skills", nargs="+", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
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
