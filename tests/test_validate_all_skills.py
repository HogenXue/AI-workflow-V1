import contextlib
import io
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_validator(path: Path):
    spec = importlib.util.spec_from_file_location("validator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_complete_skill(root: Path, name: str) -> Path:
    skill = root / name
    for directory in ("agents", "references", "templates", "examples", "scripts"):
        (skill / directory).mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: test skill\n---\n[ref](references/guide.md)\n",
        encoding="utf-8",
    )
    (skill / "agents" / "openai.yaml").write_text(
        "interface:\n"
        "  display_name: \"Test\"\n"
        "  short_description: \"Test skill\"\n"
        f"  default_prompt: \"Use ${name} for this test.\"\n",
        encoding="utf-8",
    )
    (skill / "references" / "guide.md").write_text("guide\n", encoding="utf-8")
    (skill / "templates" / "report.md").write_text("# Report\n", encoding="utf-8")
    (skill / "examples" / "example.md").write_text("# Example\n", encoding="utf-8")
    (skill / "scripts" / "check.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    return skill


class ValidateAllSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.validator = load_validator(ROOT / "scripts" / "validate-all-skills.py")

    def test_complete_skill_has_no_errors(self) -> None:
        skill = create_complete_skill(self.root, "review")

        self.assertEqual(self.validator.validate_skill(skill), [])

    def test_missing_examples_directory_is_reported(self) -> None:
        skill = create_complete_skill(self.root, "review")
        (skill / "examples" / "example.md").unlink()
        (skill / "examples").rmdir()

        errors = self.validator.validate_skill(skill)

        self.assertIn("missing required directory: examples", errors)

    def test_invalid_frontmatter_yaml_is_reported(self) -> None:
        skill = create_complete_skill(self.root, "review")
        (skill / "SKILL.md").write_text(
            "---\nname: review: broken\ndescription: test skill\n---\n",
            encoding="utf-8",
        )

        _, error_text = self.validator.load_skill_metadata(skill / "SKILL.md")

        self.assertIn("invalid YAML", error_text)

    def test_broken_relative_link_is_reported(self) -> None:
        skill = create_complete_skill(self.root, "review")
        (skill / "SKILL.md").write_text(
            "---\nname: review\ndescription: review code\n---\n"
            "[missing](references/nope.md)\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_skill(skill)

        self.assertIn("broken relative reference: references/nope.md", errors)

    def test_invalid_configuration_yaml_is_reported(self) -> None:
        config = self.root / "defaults.yaml"
        config.write_text("language: zh-CN: broken\n", encoding="utf-8")

        errors = self.validator.validate_config(config)

        self.assertIn("invalid YAML", errors)

    def test_configuration_unknown_key_is_reported_against_schema(self) -> None:
        config = self.root / "hogen-codex.yaml"
        schema = self.root / "project-config.schema.yaml"
        config.write_text("tools:\n  unexpected: true\n", encoding="utf-8")
        schema.write_text(
            "type: mapping\nallowed_keys:\n  tools:\n    type: mapping\n    allowed_keys: {}\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_config(config, schema)

        self.assertIn("unknown configuration key: tools.unexpected", errors)

    def test_configuration_type_mismatch_is_reported_against_schema(self) -> None:
        config = self.root / "hogen-codex.yaml"
        schema = self.root / "project-config.schema.yaml"
        config.write_text('change_policy:\n  minimal_change: "yes"\n', encoding="utf-8")
        schema.write_text(
            "type: mapping\nallowed_keys:\n  change_policy:\n    type: mapping\n    allowed_keys:\n      minimal_change:\n        type: boolean\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_config(config, schema)

        self.assertIn(
            "configuration change_policy.minimal_change must be a boolean", errors
        )

    def test_empty_required_resource_directory_is_reported(self) -> None:
        skill = create_complete_skill(self.root, "review")
        (skill / "templates" / "report.md").unlink()

        errors = self.validator.validate_skill(skill)

        self.assertIn("required directory is empty: templates", errors)

    def test_example_todo_placeholder_is_reported(self) -> None:
        skill = create_complete_skill(self.root, "review")
        (skill / "examples" / "example.md").write_text("# TODO: fill this in\n", encoding="utf-8")

        errors = self.validator.validate_skill(skill)

        self.assertIn("placeholder in example: examples/example.md", errors)

    def test_agent_default_prompt_must_reference_its_skill(self) -> None:
        skill = create_complete_skill(self.root, "review")
        (skill / "agents" / "openai.yaml").write_text(
            "interface:\n"
            "  display_name: \"Test\"\n"
            "  short_description: \"Test skill\"\n"
            "  default_prompt: \"Use $debugging for this test.\"\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_skill(skill)

        self.assertIn("agent default_prompt must reference $review", errors)

    def test_agent_default_prompt_requires_an_exact_skill_reference(self) -> None:
        skill = create_complete_skill(self.root, "review")
        (skill / "agents" / "openai.yaml").write_text(
            "interface:\n"
            "  display_name: \"Test\"\n"
            "  short_description: \"Test skill\"\n"
            "  default_prompt: \"Use $reviewing for this test.\"\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_skill(skill)

        self.assertIn("agent default_prompt must reference $review", errors)

    def test_agent_interface_requires_nonempty_metadata_fields(self) -> None:
        skill = create_complete_skill(self.root, "review")
        (skill / "agents" / "openai.yaml").write_text(
            "interface:\n  display_name: \"\"\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_skill(skill)

        self.assertIn("agent interface display_name must be a non-empty string", errors)
        self.assertIn("agent interface short_description must be a non-empty string", errors)
        self.assertIn("agent interface default_prompt must be a non-empty string", errors)

    def test_agent_interface_metadata_must_use_quoted_scalars(self) -> None:
        skill = create_complete_skill(self.root, "review")
        (skill / "agents" / "openai.yaml").write_text(
            "interface:\n"
            "  display_name: Test\n"
            "  short_description: \"Test skill\"\n"
            "  default_prompt: \"Use $review for this test.\"\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_skill(skill)

        self.assertIn(
            "agent interface display_name must use a double-quoted scalar", errors
        )

    def test_main_validates_project_override_against_schema(self) -> None:
        (self.root / "manifest.yaml").write_text("skills: []\n", encoding="utf-8")
        config_dir = self.root / "config"
        config_dir.mkdir()
        (config_dir / "defaults.yaml").write_text("language: zh-CN\n", encoding="utf-8")
        (config_dir / "project-config.schema.yaml").write_text(
            "type: mapping\nallowed_keys:\n  language:\n    type: string\n",
            encoding="utf-8",
        )
        (self.root / "hogen-codex.yaml").write_text("unknown: true\n", encoding="utf-8")
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            status = self.validator.main(["--root", str(self.root)])

        self.assertEqual(status, 1)
        self.assertIn("hogen-codex.yaml: unknown configuration key: unknown", output.getvalue())

    def test_external_project_root_merges_nested_override_with_package_defaults(self) -> None:
        package_root = self.root / "package"
        project_root = self.root / "project"
        package_root.mkdir()
        project_root.mkdir()
        (package_root / "manifest.yaml").write_text("skills: []\n", encoding="utf-8")
        config_dir = package_root / "config"
        config_dir.mkdir()
        (config_dir / "defaults.yaml").write_text(
            "change_policy:\n"
            "  minimal_change: true\n"
            "  preserve_dirty_worktree: true\n"
            "tools:\n"
            "  missing_tool_policy: report-and-degrade\n",
            encoding="utf-8",
        )
        (config_dir / "project-config.schema.yaml").write_text(
            "type: mapping\n"
            "allowed_keys:\n"
            "  change_policy:\n"
            "    type: mapping\n"
            "    allowed_keys:\n"
            "      minimal_change:\n"
            "        type: boolean\n"
            "      preserve_dirty_worktree:\n"
            "        type: boolean\n"
            "  tools:\n"
            "    type: mapping\n"
            "    allowed_keys:\n"
            "      missing_tool_policy:\n"
            "        type: string\n",
            encoding="utf-8",
        )
        (project_root / "hogen-codex.yaml").write_text(
            "change_policy:\n  minimal_change: false\n",
            encoding="utf-8",
        )

        config, errors = self.validator.load_effective_config(package_root, project_root)

        self.assertEqual(errors, [])
        self.assertEqual(
            config,
            {
                "change_policy": {
                    "minimal_change": False,
                    "preserve_dirty_worktree": True,
                },
                "tools": {"missing_tool_policy": "report-and-degrade"},
            },
        )
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate-all-skills.py"),
                "--root",
                str(package_root),
                "--project-root",
                str(project_root),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_external_project_root_reports_unknown_nested_override_key(self) -> None:
        package_root = self.root / "package"
        project_root = self.root / "project"
        package_root.mkdir()
        project_root.mkdir()
        (package_root / "manifest.yaml").write_text("skills: []\n", encoding="utf-8")
        config_dir = package_root / "config"
        config_dir.mkdir()
        (config_dir / "defaults.yaml").write_text("tools: {}\n", encoding="utf-8")
        (config_dir / "project-config.schema.yaml").write_text(
            "type: mapping\n"
            "allowed_keys:\n"
            "  tools:\n"
            "    type: mapping\n"
            "    allowed_keys:\n"
            "      missing_tool_policy:\n"
            "        type: string\n",
            encoding="utf-8",
        )
        override = project_root / "hogen-codex.yaml"
        override.write_text("tools:\n  unexpected: true\n", encoding="utf-8")
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            status = self.validator.main(
                [
                    "--root",
                    str(package_root),
                    "--project-root",
                    str(project_root),
                ]
            )

        self.assertEqual(status, 1)
        self.assertIn(
            f"{override}: unknown configuration key: tools.unexpected",
            output.getvalue(),
        )

    def test_missing_pyyaml_has_actionable_message(self) -> None:
        result = subprocess.run(
            [sys.executable, "-S", str(ROOT / "scripts" / "validate-all-skills.py")],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("PyYAML is required", result.stderr)
        self.assertIn("pip install -r requirements-dev.txt", result.stderr)


class ManifestTests(unittest.TestCase):
    def test_manifest_lists_standard_skill_names(self) -> None:
        metadata = yaml.safe_load((ROOT / "manifest.yaml").read_text(encoding="utf-8"))

        self.assertEqual(
            metadata["skills"],
            [
                "memory",
                "gitnexus",
                "openspec",
                "review",
                "debugging",
                "release",
                "karpathy-guidelines-zh",
            ],
        )


class BundledSkillContractTests(unittest.TestCase):
    EXPECTED_METADATA = {
        "memory": {
            "name": "memory",
            "description": (
                "Retrieve and record durable project context, decisions, learned "
                "constraints, and completed outcomes. Use for prior-work questions, "
                "architecture decisions, handoffs, and preserving important conclusions."
            ),
        },
        "gitnexus": {
            "name": "gitnexus",
            "description": (
                "Analyze code relationships, change impact, worktrees, commit scope, "
                "and release branches. Use before changing symbols, reviewing blast "
                "radius, working with Git worktrees, or validating affected flows before a commit."
            ),
        },
        "openspec": {
            "name": "openspec",
            "description": (
                "Create and maintain requirements, technical designs, RFCs, API "
                "contracts, database contracts, and implementation tasks for medium or "
                "large changes. Use before architecture-heavy, cross-module, data-model, "
                "or interface changes."
            ),
        },
        "review": {
            "name": "review",
            "description": (
                "Review code changes for correctness, security, compatibility, "
                "maintainability, performance, and regression risk. Use for pull-request "
                "review, pre-merge review, release review, or a focused review of changed files."
            ),
        },
        "debugging": {
            "name": "debugging",
            "description": (
                "Investigate bugs, crashes, test failures, and unexpected behavior through "
                "reproduction, evidence collection, root-cause isolation, minimal repair, and "
                "verification. Use whenever diagnosing or fixing a defect."
            ),
        },
        "release": {
            "name": "release",
            "description": (
                "Plan, verify, execute, and report releases with versioning, change notes, "
                "rollback readiness, and post-release checks. Use for release preparation, "
                "deployment, rollout, rollback, or release-status verification."
            ),
        },
        "karpathy-guidelines-zh": {
            "name": "karpathy-guidelines-zh",
            "description": (
                "Apply Karpathy-inspired 12-rule behavior contract for coding, review, refactor, "
                "and multi-step agent work. Use to reduce silent assumptions, over-engineering, "
                "unrelated edits, weak tests, context drift, and hidden failures."
            ),
        },
    }

    def test_standard_skill_package_contracts(self) -> None:
        for name, expected_metadata in self.EXPECTED_METADATA.items():
            with self.subTest(skill=name):
                skill = ROOT / "skills" / name
                for directory in ("agents", "references", "templates", "examples", "scripts"):
                    self.assertTrue((skill / directory).is_dir(), f"missing {name}/{directory}")
                self.assertTrue((skill / "scripts" / "validate.sh").is_file())
                self.assertEqual(
                    yaml.safe_load((skill / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[1]),
                    expected_metadata,
                )
                agent = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
                self.assertIn(f"${name}", agent["interface"]["default_prompt"])

    def test_openspec_and_review_workflows_cover_configuration_and_fallbacks(self) -> None:
        expected_phrases = {
            "openspec": (
                "config/defaults.yaml",
                "hogen-codex.yaml",
                "OpenSpec 不可用时",
            ),
            "review": (
                "config/defaults.yaml",
                "hogen-codex.yaml",
                "审查工具不可用时",
            ),
        }

        for name, phrases in expected_phrases.items():
            with self.subTest(skill=name):
                content = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                for phrase in phrases:
                    self.assertIn(phrase, content)

    def test_debugging_and_release_workflows_cover_configuration_and_fallbacks(self) -> None:
        expected_phrases = {
            "debugging": (
                "config/defaults.yaml",
                "hogen-codex.yaml",
                "调试工具不可用时",
            ),
            "release": (
                "config/defaults.yaml",
                "hogen-codex.yaml",
                "发布工具不可用时",
            ),
        }

        for name, phrases in expected_phrases.items():
            with self.subTest(skill=name):
                content = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                for phrase in phrases:
                    self.assertIn(phrase, content)

    def test_debugging_and_release_templates_use_fixed_evidence_gates(self) -> None:
        expected_headings = {
            "debugging": (
                "templates/debug-report.md",
                ("Reproduction", "Observed evidence", "Root cause", "Minimal fix", "Verification", "Unverified"),
            ),
            "release": (
                "templates/release-checklist.md",
                (
                    "Scope",
                    "Pre-release checks",
                    "Rollback",
                    "Execution record",
                    "Post-release checks",
                    "Outstanding risks",
                ),
            ),
        }

        for name, (template_path, headings) in expected_headings.items():
            with self.subTest(skill=name):
                content = (ROOT / "skills" / name / template_path).read_text(encoding="utf-8")
                for heading in headings:
                    self.assertIn(f"## {heading}", content)
