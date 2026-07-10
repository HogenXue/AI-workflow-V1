#!/usr/bin/env python3
"""Validate the structural contract for this Skill package."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import unquote, urlsplit

import yaml


REQUIRED_DIRECTORIES = ("agents", "references", "templates", "examples", "scripts")
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\)")


def load_yaml(path: Path) -> tuple[Any | None, str | None]:
    """Load a YAML document, returning an error string instead of raising."""

    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")), None
    except OSError as error:
        return None, f"unable to read YAML: {error}"
    except yaml.YAMLError as error:
        return None, f"invalid YAML: {error}"


def load_skill_metadata(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    """Read and validate the first YAML frontmatter block in a Skill file."""

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        return None, f"unable to read SKILL.md: {error}"

    if not lines or lines[0].strip() != "---":
        return None, "missing YAML frontmatter"

    try:
        end_index = next(
            index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"
        )
    except StopIteration:
        return None, "missing closing YAML frontmatter delimiter"

    try:
        metadata = yaml.safe_load("\n".join(lines[1:end_index]))
    except yaml.YAMLError as error:
        return None, f"invalid YAML: {error}"

    if not isinstance(metadata, dict):
        return None, "frontmatter must be a mapping"

    for key in ("name", "description"):
        value = metadata.get(key)
        if not isinstance(value, str) or not value.strip():
            return None, f"frontmatter {key} must be a non-empty scalar"

    return metadata, None


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _relative_references(markdown_path: Path) -> list[str]:
    references: list[str] = []
    try:
        contents = markdown_path.read_text(encoding="utf-8")
    except OSError:
        return references

    for match in MARKDOWN_LINK.finditer(contents):
        target = match.group(1) or match.group(2)
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or target.startswith(("#", "/")):
            continue
        if not parts.path:
            continue
        references.append(unquote(parts.path))
    return references


def validate_skill(skill_path: Path) -> list[str]:
    """Return every contract violation found in one Skill directory."""

    skill_path = Path(skill_path)
    errors: list[str] = []

    if not skill_path.is_dir():
        return ["missing skill directory"]

    for directory in REQUIRED_DIRECTORIES:
        if not (skill_path / directory).is_dir():
            errors.append(f"missing required directory: {directory}")

    skill_file = skill_path / "SKILL.md"
    if not skill_file.is_file():
        errors.append("missing required file: SKILL.md")
        metadata = None
    else:
        metadata, metadata_error = load_skill_metadata(skill_file)
        if metadata_error:
            errors.append(metadata_error)

    agent_file = skill_path / "agents" / "openai.yaml"
    if not agent_file.is_file():
        errors.append("missing required file: agents/openai.yaml")
    else:
        agent, agent_error = load_yaml(agent_file)
        if agent_error:
            errors.append(f"invalid agents YAML: {agent_error}")
        elif not isinstance(agent, dict):
            errors.append("agents YAML must be a mapping")

    if metadata is not None and metadata["name"] != skill_path.name:
        errors.append(f"metadata name does not match skill directory: {metadata['name']}")

    root = skill_path.resolve()
    for markdown_path in skill_path.rglob("*.md"):
        for reference in _relative_references(markdown_path):
            resolved = (markdown_path.parent / reference).resolve()
            if not _is_relative_to(resolved, root) or not resolved.exists():
                errors.append(f"broken relative reference: {reference}")

    return errors


def validate_config(path: Path) -> list[str]:
    """Return parse and shape errors for one package configuration document."""

    path = Path(path)
    if not path.is_file():
        return ["missing configuration file"]

    document, error = load_yaml(path)
    if error:
        return ["invalid YAML"] if error.startswith("invalid YAML") else [error]
    if not isinstance(document, dict):
        return ["configuration must be a mapping"]
    return []


def _manifest_skills(root: Path) -> tuple[list[str] | None, list[tuple[Path, str]]]:
    manifest_path = root / "manifest.yaml"
    manifest, error = load_yaml(manifest_path)
    if error:
        return None, [(manifest_path, error)]
    if not isinstance(manifest, dict):
        return None, [(manifest_path, "manifest must be a mapping")]

    skills = manifest.get("skills")
    if not isinstance(skills, list) or not all(isinstance(name, str) and name for name in skills):
        return None, [(manifest_path, "manifest skills must be a list of non-empty strings")]
    return skills, []


def main(argv: Sequence[str] | None = None) -> int:
    """Run validation and print stable, script-friendly diagnostics."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", metavar="NAME", help="validate one Skill only")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="package root (default: the repository containing this script)",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()

    errors: list[tuple[Path, str]] = []
    successful_skills: list[str] = []

    if args.skill:
        skills = [args.skill]
    else:
        skills, manifest_errors = _manifest_skills(root)
        errors.extend(manifest_errors)
        if skills is None:
            skills = []
        for config_path in (
            root / "config" / "defaults.yaml",
            root / "config" / "project-config.schema.yaml",
        ):
            errors.extend((config_path, error) for error in validate_config(config_path))

    for name in skills:
        skill_path = root / "skills" / name
        skill_errors = validate_skill(skill_path)
        if skill_errors:
            errors.extend((skill_path, error) for error in skill_errors)
        else:
            successful_skills.append(name)

    for name in successful_skills:
        print(f"OK: {name}")
    for path, error in errors:
        print(f"ERROR: {path}: {error}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
