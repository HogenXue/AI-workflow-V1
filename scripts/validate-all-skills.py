#!/usr/bin/env python3
"""Validate the structural contract for this Skill package."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    yaml = None


PYAML_INSTALL_MESSAGE = (
    "PyYAML is required to validate this package. "
    "Install development dependencies with: python3 -m pip install -r requirements-dev.txt"
)


REQUIRED_DIRECTORIES = ("agents", "references", "templates", "examples", "scripts")
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\)")


def load_yaml(path: Path) -> tuple[Any | None, str | None]:
    """Load a YAML document, returning an error string instead of raising."""

    if yaml is None:
        return None, PYAML_INSTALL_MESSAGE

    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")), None
    except OSError as error:
        return None, f"unable to read YAML: {error}"
    except yaml.YAMLError as error:
        return None, f"invalid YAML: {error}"


def load_skill_metadata(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    """Read and validate the first YAML frontmatter block in a Skill file."""

    if yaml is None:
        return None, PYAML_INSTALL_MESSAGE

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


def _directory_has_file(path: Path) -> bool:
    return any(
        candidate.is_file()
        and candidate.stat().st_size > 0
        and not any(part.startswith(".") for part in candidate.relative_to(path).parts)
        for candidate in path.rglob("*")
    )


def _validate_agent_metadata(agent: Any, skill_name: str) -> list[str]:
    """Return contract errors for one Skill's Codex agent metadata."""

    if not isinstance(agent, dict):
        return ["agents YAML must be a mapping"]

    interface = agent.get("interface")
    if not isinstance(interface, dict):
        return ["agent interface must be a mapping"]

    errors: list[str] = []
    for key in ("display_name", "short_description", "default_prompt"):
        value = interface.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"agent interface {key} must be a non-empty string")

    short_description = interface.get("short_description")
    if (
        isinstance(short_description, str)
        and short_description.strip()
        and not 25 <= len(short_description) <= 64
    ):
        errors.append("agent short_description must contain 25 to 64 characters")

    default_prompt = interface.get("default_prompt")
    if (
        isinstance(default_prompt, str)
        and default_prompt.strip()
        and not re.search(rf"\${re.escape(skill_name)}(?![\w-])", default_prompt)
    ):
        errors.append(f"agent default_prompt must reference ${skill_name}")

    return errors


def _validate_quoted_agent_interface(path: Path) -> list[str]:
    """Ensure user-facing agent interface strings retain the package's quoted style."""

    if yaml is None:
        return [PYAML_INSTALL_MESSAGE]
    try:
        document = yaml.compose(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        return [f"unable to inspect agent interface quoting: {error}"]

    if document is None or getattr(document, "id", None) != "mapping":
        return []
    interface_node = None
    for key_node, value_node in document.value:
        if getattr(key_node, "value", None) == "interface":
            interface_node = value_node
            break
    if interface_node is None or getattr(interface_node, "id", None) != "mapping":
        return []

    values = {
        getattr(key_node, "value", None): value_node
        for key_node, value_node in interface_node.value
    }
    errors: list[str] = []
    for key in ("display_name", "short_description", "default_prompt"):
        value_node = values.get(key)
        if value_node is not None and getattr(value_node, "style", None) != '"':
            errors.append(f"agent interface {key} must use a double-quoted scalar")
    return errors


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
        directory_path = skill_path / directory
        if not directory_path.is_dir():
            errors.append(f"missing required directory: {directory}")
        elif directory in {"templates", "examples", "scripts"} and not _directory_has_file(directory_path):
            errors.append(f"required directory is empty: {directory}")

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
        else:
            errors.extend(_validate_agent_metadata(agent, skill_path.name))
            errors.extend(_validate_quoted_agent_interface(agent_file))

    if metadata is not None and metadata["name"] != skill_path.name:
        errors.append(f"metadata name does not match skill directory: {metadata['name']}")

    root = skill_path.resolve()
    for markdown_path in skill_path.rglob("*.md"):
        for reference in _relative_references(markdown_path):
            resolved = (markdown_path.parent / reference).resolve()
            if not _is_relative_to(resolved, root) or not resolved.exists():
                errors.append(f"broken relative reference: {reference}")

    examples_path = skill_path / "examples"
    if examples_path.is_dir():
        for example_path in examples_path.rglob("*.md"):
            try:
                contents = example_path.read_text(encoding="utf-8")
            except OSError as error:
                errors.append(f"unable to read example: {example_path.relative_to(skill_path)}: {error}")
                continue
            if re.search(r"\b(?:TODO|TBD)\b", contents, flags=re.IGNORECASE):
                errors.append(f"placeholder in example: {example_path.relative_to(skill_path)}")

    return errors


def _validate_schema(schema: Any, location: str = "configuration schema") -> list[str]:
    """Return contract errors for the small declarative configuration schema."""

    if not isinstance(schema, dict):
        return [f"{location} must be a mapping"]

    schema_type = schema.get("type")
    if schema_type not in {"mapping", "string", "boolean"}:
        return [f"{location} has unsupported type: {schema_type!r}"]

    if schema_type == "mapping":
        allowed_keys = schema.get("allowed_keys")
        if not isinstance(allowed_keys, dict):
            return [f"{location} mapping must define allowed_keys"]
        errors: list[str] = []
        for key, nested_schema in allowed_keys.items():
            if not isinstance(key, str) or not key:
                errors.append(f"{location} allowed_keys must use non-empty string keys")
                continue
            errors.extend(_validate_schema(nested_schema, f"{location}.{key}"))
        return errors

    return []


def _validate_config_value(value: Any, schema: dict[str, Any], location: str) -> list[str]:
    schema_type = schema["type"]
    if schema_type == "mapping":
        if not isinstance(value, dict):
            return [f"configuration {location} must be a mapping"]
        errors: list[str] = []
        allowed_keys = schema["allowed_keys"]
        for key, nested_value in value.items():
            nested_location = f"{location}.{key}" if location else str(key)
            nested_schema = allowed_keys.get(key)
            if nested_schema is None:
                errors.append(f"unknown configuration key: {nested_location}")
                continue
            errors.extend(_validate_config_value(nested_value, nested_schema, nested_location))
        return errors

    if schema_type == "string" and not isinstance(value, str):
        return [f"configuration {location} must be a string"]
    if schema_type == "boolean" and not isinstance(value, bool):
        return [f"configuration {location} must be a boolean"]
    return []


def validate_config(path: Path, schema_path: Path | None = None) -> list[str]:
    """Return parse, schema, and unknown-key errors for one configuration file."""

    path = Path(path)
    if not path.is_file():
        return ["missing configuration file"]

    document, error = load_yaml(path)
    if error:
        return ["invalid YAML"] if error.startswith("invalid YAML") else [error]
    if not isinstance(document, dict):
        return ["configuration must be a mapping"]
    if schema_path is None:
        return []

    schema, schema_error = load_yaml(Path(schema_path))
    if schema_error:
        return [f"invalid configuration schema: {schema_error}"]
    schema_errors = _validate_schema(schema)
    if schema_errors:
        return schema_errors
    return _validate_config_value(document, schema, "")


def _merge_config(defaults: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge a project override into package defaults."""

    merged = defaults.copy()
    for key, override_value in override.items():
        default_value = merged.get(key)
        if isinstance(default_value, dict) and isinstance(override_value, dict):
            merged[key] = _merge_config(default_value, override_value)
        else:
            merged[key] = override_value
    return merged


def load_effective_config(
    package_root: Path, project_root: Path
) -> tuple[dict[str, Any] | None, list[tuple[Path, str]]]:
    """Validate and merge package defaults with an optional project override."""

    package_root = Path(package_root)
    project_root = Path(project_root)
    defaults_path = package_root / "config" / "defaults.yaml"
    schema_path = package_root / "config" / "project-config.schema.yaml"
    errors = [(defaults_path, error) for error in validate_config(defaults_path, schema_path)]
    if errors:
        return None, errors

    defaults, defaults_error = load_yaml(defaults_path)
    if defaults_error or not isinstance(defaults, dict):
        return None, [(defaults_path, defaults_error or "configuration must be a mapping")]

    override_path = project_root / "hogen-codex.yaml"
    if not override_path.exists():
        return defaults, []

    errors = [(override_path, error) for error in validate_config(override_path, schema_path)]
    if errors:
        return None, errors

    override, override_error = load_yaml(override_path)
    if override_error or not isinstance(override, dict):
        return None, [(override_path, override_error or "configuration must be a mapping")]

    merged = _merge_config(defaults, override)
    schema, schema_error = load_yaml(schema_path)
    if schema_error:
        return None, [(schema_path, f"invalid configuration schema: {schema_error}")]
    schema_errors = _validate_schema(schema)
    if schema_errors:
        return None, [(schema_path, error) for error in schema_errors]
    merge_errors = _validate_config_value(merged, schema, "")
    if merge_errors:
        return None, [(override_path, error) for error in merge_errors]
    return merged, []


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
    parser.add_argument(
        "--project-root",
        type=Path,
        help="project root containing an optional hogen-codex.yaml (default: package root)",
    )
    args = parser.parse_args(argv)
    if yaml is None:
        print(f"ERROR: {PYAML_INSTALL_MESSAGE}", file=sys.stderr)
        return 2
    root = args.root.resolve()
    project_root = args.project_root.resolve() if args.project_root else root

    errors: list[tuple[Path, str]] = []
    successful_skills: list[str] = []

    if args.skill:
        skills = [args.skill]
    else:
        skills, manifest_errors = _manifest_skills(root)
        errors.extend(manifest_errors)
        if skills is None:
            skills = []
        _, config_errors = load_effective_config(root, project_root)
        errors.extend(config_errors)

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
