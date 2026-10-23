"""Merge package-owned hook handlers while preserving host and user customizations."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import sys
import tempfile

CODEX_MARKER = "Trellis/Codex session context"
LEGACY_CODEX_SH_SHA256 = "00314a3a1871ac29ef9fad7c6472574ffa27bf592ec6f5d5497655e5b08a249f"


def checked_path(path: Path, directory: bool = False) -> None:
    if path.is_symlink() or (path.exists() and (not path.is_dir() if directory else not path.is_file())):
        raise ValueError(f"refusing non-regular {'directory' if directory else 'file'}: {path}")


def read_config(target: Path) -> dict:
    checked_path(target)
    data = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
    if not isinstance(data, dict) or ("hooks" in data and not isinstance(data["hooks"], dict)):
        raise ValueError("hooks.json must be an object with an optional hooks object")
    data.setdefault("hooks", {})
    return data


def merge_codex(data: dict, template: dict, scripts: Path) -> dict:
    groups = data["hooks"].get("SessionStart", [])
    if not isinstance(groups, list):
        raise ValueError("SessionStart hooks must be a list")
    kept = []
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
            raise ValueError("SessionStart groups must contain a hooks list")
        handlers = group["hooks"]
        foreign = [h for h in handlers if not (isinstance(h, dict) and h.get("statusMessage") == CODEX_MARKER)]
        if len(foreign) == len(handlers):
            kept.append(group)
        elif foreign:
            kept.append({**group, "hooks": foreign})
    managed = copy.deepcopy(template["hooks"]["SessionStart"])
    script = scripts / "session-start.sh"
    managed[0]["hooks"][0]["command"] = f"bash {shlex.quote(str(script))}"
    managed[0]["hooks"][0]["commandWindows"] = f'python "{script.with_suffix(".py").as_posix()}"'
    data["hooks"]["SessionStart"] = kept + managed
    return data


def merge_cursor(data: dict, template: dict) -> dict:
    # Only exact package command paths are identities; basename matching could
    # remove a user's unrelated script. Keep all other metadata and event arrays.
    for event, managed in template["hooks"].items():
        existing = data["hooks"].get(event, [])
        if not isinstance(existing, list) or any(not isinstance(h, dict) for h in existing):
            raise ValueError(f"{event} hooks must be a list of objects")
        # A handler with a package command but different matching/options may
        # be user-customized. Keep it intact instead of widening its scope.
        commands = {h["command"] for h in managed}
        for handler in existing:
            if handler.get("command") in commands and handler not in managed:
                raise ValueError(f"customized {event} handler uses a package script; review it before updating")
        data["hooks"][event] = [h for h in existing if h not in managed] + copy.deepcopy(managed)
    data.setdefault("version", template.get("version", 1))
    return data


def install(host: str, templates: Path, target: Path, dry_run: bool) -> None:
    hook_dir = target.parent / "hooks"
    scripts = hook_dir
    checked_path(hook_dir, directory=True)
    data = read_config(target)
    template = json.loads((templates / "hooks.json").read_text(encoding="utf-8"))
    sources = sorted(p for p in (templates / "hooks").iterdir() if p.is_file())
    ownership_file = hook_dir / ".ai-workflow-managed.json"
    checked_path(ownership_file)
    ownership = {}
    if ownership_file.exists():
        previous = json.loads(ownership_file.read_text(encoding="utf-8"))
        if not isinstance(previous, dict) or previous.get("host") != host or previous.get("version") != 1 or not isinstance(previous.get("files"), dict):
            raise ValueError(f"unrecognized hook ownership record preserved: {ownership_file}")
        ownership = previous["files"]
    for source in sources:
        destination = scripts / source.name
        checked_path(destination)
        if destination.exists():
            known = {hashlib.sha256(source.read_bytes()).hexdigest()}
            recorded = ownership.get(source.name)
            if isinstance(recorded, str):
                known.add(recorded)
            if host == "codex" and source.name == "session-start.sh":
                known.add(LEGACY_CODEX_SH_SHA256)
            if hashlib.sha256(destination.read_bytes()).hexdigest() not in known:
                raise ValueError(f"unrecognized or customized hook script preserved: {destination}")
    data = merge_codex(data, template, scripts) if host == "codex" else merge_cursor(data, template)
    if dry_run:
        print(f"DRY-RUN: would merge {host} package hooks into {target}; preserve foreign handlers and scripts")
        return
    scripts.mkdir(parents=True, exist_ok=True)
    for source in sources:
        shutil.copy2(source, scripts / source.name)
    # Remember the exact bytes we own, so later package upgrades can replace
    # older package assets while refusing a user's intervening edits.
    write_json_atomic(ownership_file, {"version": 1, "host": host, "files": {
        source.name: hashlib.sha256(source.read_bytes()).hexdigest() for source in sources
    }})
    # Publish config only after every referenced package script is present.
    write_json_atomic(target, data)
    print(f"INSTALLED: {target}")
    print(f"INSTALLED: {scripts}")
    if host == "codex":
        print("NOTE: review new or changed hook definitions in Codex /hooks; installation does not grant native hook trust.")


def write_json_atomic(target: Path, data: dict) -> None:
    fd, temporary = tempfile.mkstemp(prefix=".hooks.", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
        if target.exists():
            shutil.copymode(target, temporary)
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=("codex", "cursor"), required=True)
    parser.add_argument("--templates", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        install(args.host, args.templates, args.target, args.dry_run)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"CONFLICT: could not merge {args.host} hooks: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
