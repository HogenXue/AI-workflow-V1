#!/usr/bin/env python3
"""Validate and emit the effective AI-workflow configuration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

try:
    import yaml
except ImportError:
    yaml = None


PYAML_INSTALL_MESSAGE = (
    "PyYAML is required to load AI-workflow configuration. "
    "Install development dependencies with: python3 -m pip install -r requirements-dev.txt"
)


def load_yaml(path: Path) -> tuple[Any | None, str | None]:
    """Load a YAML document, returning an error string instead of raising."""

    if yaml is None:
        return None, PYAML_INSTALL_MESSAGE
    try:
        return yaml.safe_load(Path(path).read_text(encoding="utf-8")), None
    except OSError as error:
        return None, f"unable to read YAML: {error}"
    except yaml.YAMLError as error:
        return None, f"invalid YAML: {error}"


def validate_schema(schema: Any, location: str = "configuration schema") -> list[str]:
    """Return structural errors for the supported declarative schema subset."""

    if not isinstance(schema, dict):
        return [f"{location} must be a mapping"]
    schema_type = schema.get("type")
    if schema_type not in {"mapping", "string", "boolean"}:
        return [f"{location} has unsupported type: {schema_type!r}"]
    if schema_type != "mapping":
        return []

    allowed_keys = schema.get("allowed_keys")
    if not isinstance(allowed_keys, dict):
        return [f"{location} mapping must define allowed_keys"]
    errors: list[str] = []
    for key, nested_schema in allowed_keys.items():
        if not isinstance(key, str) or not key:
            errors.append(f"{location} allowed_keys must use non-empty string keys")
            continue
        errors.extend(validate_schema(nested_schema, f"{location}.{key}"))
    return errors


def validate_config_value(value: Any, schema: dict[str, Any], location: str) -> list[str]:
    """Validate one configuration value against the supported schema subset."""

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
            errors.extend(validate_config_value(nested_value, nested_schema, nested_location))
        return errors
    if schema_type == "string" and not isinstance(value, str):
        return [f"configuration {location} must be a string"]
    if schema_type == "boolean" and not isinstance(value, bool):
        return [f"configuration {location} must be a boolean"]
    return []


def validate_config(path: Path, schema_path: Path | None = None) -> list[str]:
    """Return parse, schema and unknown-key errors for a configuration file."""

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
    schema_errors = validate_schema(schema)
    if schema_errors:
        return schema_errors
    return validate_config_value(document, schema, "")


def merge_config(defaults: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge a project override into package defaults."""

    merged = defaults.copy()
    for key, override_value in override.items():
        default_value = merged.get(key)
        if isinstance(default_value, dict) and isinstance(override_value, dict):
            merged[key] = merge_config(default_value, override_value)
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

    merged = merge_config(defaults, override)
    schema, schema_error = load_yaml(schema_path)
    if schema_error:
        return None, [(schema_path, f"invalid configuration schema: {schema_error}")]
    schema_errors = validate_schema(schema)
    if schema_errors:
        return None, [(schema_path, error) for error in schema_errors]
    merge_errors = validate_config_value(merged, schema, "")
    if merge_errors:
        return None, [(override_path, error) for error in merge_errors]
    return merged, []


def _schema_leaf_keys(schema: dict[str, Any], prefix: str = "") -> set[str]:
    if schema.get("type") != "mapping":
        return {prefix}
    leaves: set[str] = set()
    for key, nested in schema.get("allowed_keys", {}).items():
        path = f"{prefix}.{key}" if prefix else key
        leaves.update(_schema_leaf_keys(nested, path))
    return leaves


def validate_consumers(package_root: Path) -> list[str]:
    """Require one named runtime or policy consumer for every public config leaf."""

    config_dir = Path(package_root) / "config"
    schema, schema_error = load_yaml(config_dir / "project-config.schema.yaml")
    if schema_error:
        return [f"invalid configuration schema: {schema_error}"]
    schema_errors = validate_schema(schema)
    if schema_errors:
        return schema_errors

    registry, registry_error = load_yaml(config_dir / "consumers.yaml")
    if registry_error:
        return [f"invalid configuration consumer registry: {registry_error}"]
    consumers = registry.get("consumers") if isinstance(registry, dict) else None
    if not isinstance(consumers, dict):
        return ["configuration consumer registry must define a consumers mapping"]

    leaf_keys = _schema_leaf_keys(schema)
    errors: list[str] = []
    for key in sorted(leaf_keys - set(consumers)):
        errors.append(f"missing configuration consumer: {key}")
    for key in sorted(set(consumers) - leaf_keys):
        errors.append(f"unknown configuration consumer key: {key}")
    for key in sorted(leaf_keys & set(consumers)):
        names = consumers[key]
        if not isinstance(names, list) or not names or not all(
            isinstance(name, str) and name.strip() for name in names
        ):
            errors.append(f"configuration consumer list must be non-empty: {key}")
    return errors


def get_config_value(config: dict[str, Any], dotted_key: str) -> Any:
    """Resolve a dotted configuration key or raise KeyError."""

    value: Any = config
    for part in dotted_key.split("."):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(dotted_key)
        value = value[part]
    return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_package_root = Path(__file__).resolve().parents[1]
    parser.add_argument("--package-root", type=Path, default=default_package_root)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--get", metavar="DOTTED_KEY")
    parser.add_argument("--validate-consumers", action="store_true")
    args = parser.parse_args(argv)

    if yaml is None:
        print(f"ERROR: {PYAML_INSTALL_MESSAGE}", file=sys.stderr)
        return 2

    package_root = args.package_root.resolve()
    project_root = args.project_root.resolve()
    config, errors = load_effective_config(package_root, project_root)
    if args.validate_consumers:
        errors.extend(
            (package_root / "config" / "consumers.yaml", error)
            for error in validate_consumers(package_root)
        )
    if errors:
        for path, error in errors:
            print(f"ERROR: {path}: {error}", file=sys.stderr)
        return 1
    if args.validate_consumers:
        return 0
    assert config is not None

    if args.get:
        try:
            value = get_config_value(config, args.get)
        except KeyError:
            print(f"ERROR: unknown configuration key: {args.get}", file=sys.stderr)
            return 1
        print(json.dumps(value, ensure_ascii=False, sort_keys=True))
        return 0
    print(json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
