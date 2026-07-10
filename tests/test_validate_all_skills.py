import importlib.util
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
    (skill / "agents" / "openai.yaml").write_text("display_name: Test\n", encoding="utf-8")
    (skill / "references" / "guide.md").write_text("guide\n", encoding="utf-8")
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


class ManifestTests(unittest.TestCase):
    def test_manifest_lists_exactly_six_standard_skill_names(self) -> None:
        metadata = yaml.safe_load((ROOT / "manifest.yaml").read_text(encoding="utf-8"))

        self.assertEqual(
            metadata["skills"],
            ["memory", "gitnexus", "openspec", "review", "debugging", "release"],
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
