import importlib.util
import tempfile
import unittest
from pathlib import Path


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
