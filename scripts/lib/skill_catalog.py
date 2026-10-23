#!/usr/bin/env python3
"""Strict package catalog and read-only, host-aware Skill discovery checks."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None

NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKIP = {".git", "__pycache__", "node_modules"}


def read_yaml(text: str):
    if yaml is None:
        raise ValueError("PyYAML is required; install the package requirements first")
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise ValueError(f"invalid YAML: {error}") from error


def metadata(path: Path) -> dict:
    text = path.read_text(encoding="utf-8-sig")
    match = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|$)", text, re.S)
    if not match:
        raise ValueError(f"missing Skill frontmatter: {path}")
    data = read_yaml(match.group(1))
    if not isinstance(data, dict) or not isinstance(data.get("name"), str):
        raise ValueError(f"missing Skill name: {path}")
    return data


def load_catalog(root: Path, *, check_sources: bool = True) -> dict:
    data = read_yaml((root / "manifest.yaml").read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("manifest must be a mapping")
    names = data.get("skills")
    if not isinstance(names, list) or not names:
        raise ValueError("manifest skills must be a non-empty list")
    if any(not isinstance(n, str) or len(n) > 64 or not NAME.fullmatch(n) for n in names):
        raise ValueError("manifest contains an invalid Skill name (use lowercase letters, digits and hyphens)")
    if len(set(names)) != len(names):
        raise ValueError("manifest contains duplicate Skill names")
    mode = data.get("default_install_mode", "copy")
    if mode not in ("copy", "link"):
        raise ValueError("default_install_mode must be copy or link")
    if check_sources:
        source_root = (root / "skills").resolve()
        for name in names:
            source = root / "skills" / name
            if source.resolve().parent != source_root:
                raise ValueError(f"Skill source escapes package root: {name}")
            info = metadata(source / "SKILL.md")
            if info["name"] != name:
                raise ValueError(f"Skill identity differs from manifest directory: {name} -> {info['name']}")
            if not isinstance(info.get("description"), str) or not info["description"].strip():
                raise ValueError(f"missing Skill description: {name}")
            if info.get("disable-model-invocation") is True:
                ui = source / "agents/openai.yaml"
                ui_data = read_yaml(ui.read_text()) if ui.is_file() else {}
                policy = ui_data.get("policy", {}) if isinstance(ui_data, dict) else {}
                if not isinstance(policy, dict) or policy.get("allow_implicit_invocation") is not False:
                    raise ValueError(f"explicit-only Skill lacks Codex invocation policy: {name}")
    return {"skills": names, "default_install_mode": mode}


def fingerprint(path: Path) -> str:
    """Compare actual payloads across host copies, without following nested links."""
    digest = hashlib.sha256()
    root = path.resolve()
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP)
        for name in sorted([*dirs, *files]):
            p = Path(current) / name
            if name == ".DS_Store" or p.suffix in (".pyc", ".pyo"):
                continue
            relative = p.relative_to(root).as_posix().encode()
            if p.is_symlink():
                value = b"link:" + os.readlink(p).encode()
            elif p.is_file():
                value = b"file:" + p.read_bytes()
            else:
                value = b"dir"
            digest.update(len(relative).to_bytes(8, "big") + relative)
            digest.update(hashlib.sha256(value).digest())
    return digest.hexdigest()


def discover(root: Path) -> tuple[list[dict], list[str]]:
    entries, errors = [], []

    def visit(path: Path, ancestors: frozenset[Path]):
        real = path.resolve()
        if real in ancestors or not path.is_dir():
            return
        try:
            if (path / "SKILL.md").is_file():
                info = metadata(path / "SKILL.md")
                entries.append({"name": info["name"], "path": str(path), "root": str(root),
                                "realpath": str(real), "fingerprint": fingerprint(path)})
        except (OSError, ValueError) as error:
            errors.append(str(error))
        # A malformed wrapper Skill must not hide valid nested aliases or
        # historical copies from the same discovery root.
        try:
            for child in sorted(path.iterdir()):
                if child.name not in SKIP and child.is_dir():
                    visit(child, ancestors | {real})
        except (OSError, ValueError) as error:
            errors.append(str(error))

    visit(root, frozenset())
    return entries, errors


def preflight(root: Path, target: Path, other: Path | None, allow_prune: bool) -> list[str]:
    names = set(load_catalog(root)["skills"])
    conflicts = []

    def verify_slot(candidate: Path, name: str, action: str) -> None:
        if not candidate.exists() and not candidate.is_symlink():
            return
        try:
            info = metadata(candidate / "SKILL.md")
            if not isinstance(info.get("description"), str) or not info["description"].strip():
                raise ValueError("missing Skill description")
        except (OSError, ValueError) as error:
            raise ValueError(f"refusing to {action} {candidate}: cannot verify declared Skill identity: {error}") from error
        if info["name"] != name:
            raise ValueError(f"refusing to {action} {candidate}: declares independent identity {info['name']!r}, expected {name!r}")

    # Every canonical slot that can be replaced must have a verified identity.
    # Directory names and incomplete legacy remnants do not prove ownership.
    for name in sorted(names):
        verify_slot(target / name, name, "replace")
    if allow_prune and other is not None:
        for name in sorted(names):
            verify_slot(other / name, name, "prune")
    for location in [target, *([other] if other else [])]:
        entries, _ = discover(location)
        for entry in entries:
            name = entry["name"]
            if name not in names:
                continue
            path = Path(entry["path"])
            if location == target and path == target / name:
                continue
            if location == other and allow_prune and path == other / name:
                continue
            conflicts.append(f"{name}: {path}")
    return conflicts


def host_roots(home: Path, host: str) -> list[Path]:
    # Overrides are honored only for the real home. --home fixtures are isolated.
    real_home = home.resolve() == Path.home().resolve()
    codex = Path(os.environ.get("CODEX_HOME", str(home / ".codex"))) if real_home else home / ".codex"
    minimax = Path(os.environ.get("MINIMAX_DATA_DIR") or os.environ.get("MAVIS_DATA_DIR") or home / ".minimax") if real_home else home / ".minimax"
    buddy = Path(os.environ.get("CODEBUDDY_CONFIG_DIR") or home / ".codebuddy") if real_home else home / ".codebuddy"
    roots = {"codex": [home / ".agents/skills", codex / "skills"],
             "cursor": [home / ".agents/skills", home / ".cursor/skills", home / ".claude/skills", codex / "skills"],
             "claude": [home / ".claude/skills"],
             "minimax": [minimax / "skills", home / ".claude/skills", codex / "skills", home / ".agents/skills"],
             "workbuddy": [buddy / "skills"]}
    return list(dict.fromkeys(roots[host]))


def audit(root: Path, home: Path, hosts: list[str]) -> dict:
    names = set(load_catalog(root)["skills"])
    result = {"conflicts": [], "equivalent_copies": [], "drift": [], "metadata_errors": [], "hosts": {}}
    cache = {}
    expected = {name: fingerprint(root / "skills" / name) for name in names}
    for host in hosts:
        entries = []
        for path in host_roots(home, host):
            if str(path) not in cache:
                cache[str(path)] = discover(path)
            found, errors = cache[str(path)]
            entries.extend(e for e in found if e["name"] in names)
            result["metadata_errors"].extend({"host": host, "error": error} for error in errors)
        groups = defaultdict(list)
        for entry in entries:
            groups[entry["name"]].append(entry)
            if entry["fingerprint"] != expected[entry["name"]]:
                result["drift"].append({"host": host, "name": entry["name"], "path": entry["path"]})
        for name, group in groups.items():
            if len(group) > 1:
                key = "conflicts" if host == "codex" or len({e["fingerprint"] for e in group}) > 1 or len({e["root"] for e in group}) < len(group) else "equivalent_copies"
                result[key].append({"host": host, "name": name, "paths": [e["path"] for e in group]})
        result["hosts"][host] = {"roots": [str(p) for p in host_roots(home, host)], "managed_identities": sorted(groups), "missing": sorted(names - set(groups))}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("catalog", "preflight", "audit"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--field", choices=("names", "mode", "json"), default="names")
    parser.add_argument("--target", type=Path)
    parser.add_argument("--other-root", type=Path)
    parser.add_argument("--allow-other-root-prune", action="store_true")
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--host", choices=("all", "codex", "cursor", "claude", "minimax", "workbuddy"), action="append")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-current", action="store_true", help="also fail when installed managed payloads differ from this package")
    parser.add_argument("--require-complete", action="store_true", help="also fail if the selected host cannot discover every packaged Skill")
    args = parser.parse_args()
    try:
        if args.command == "catalog":
            data = load_catalog(args.root)
            print(json.dumps(data) if args.field == "json" else data["default_install_mode"] if args.field == "mode" else "\n".join(data["skills"]))
        elif args.command == "preflight":
            if args.target is None:
                parser.error("preflight requires --target")
            conflicts = preflight(args.root, args.target, args.other_root, args.allow_other_root_prune)
            if conflicts:
                print("CONFLICT: managed Skill identities also exist at:\n  " + "\n  ".join(conflicts) + "\nBack up and resolve these exact aliases before installation; no files were changed.", file=sys.stderr)
                return 2
        else:
            hosts = list(dict.fromkeys(args.host)) if args.host and "all" not in args.host else ["codex", "cursor", "claude", "minimax", "workbuddy"]
            result = audit(args.root, args.home, hosts)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                for host, info in result["hosts"].items():
                    count = sum(c["host"] == host for c in result["conflicts"])
                    drift = sum(c["host"] == host for c in result["drift"])
                    print(f"AUDIT: {host}: {len(info['managed_identities'])} managed identities, {count} conflicts, {drift} payload differences")
                for conflict in result["conflicts"]:
                    print(f"CONFLICT: {conflict['host']} {conflict['name']}: " + ", ".join(conflict["paths"]), file=sys.stderr)
                for error in result["metadata_errors"]:
                    print(f"WARNING: {error['host']}: {error['error']}", file=sys.stderr)
            return int(bool(result["conflicts"] or (args.require_current and result["drift"]) or (args.require_complete and any(h["missing"] for h in result["hosts"].values()))))
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
