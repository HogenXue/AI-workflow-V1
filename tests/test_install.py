import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "memory",
    "gitnexus",
    "openspec",
    "release",
    "karpathy-guidelines-zh",
)


class ComponentInstallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.skills_target = self.root / "skills"
        self.config_target = self.root / "config"
        self.backup = self.root / "backup"

    def run_component(self, component: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(ROOT / "scripts" / "install.sh"), component, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_skills_dry_run_does_not_create_skills_or_config(self) -> None:
        result = self.run_component("skills", "--dry-run", "--target", str(self.skills_target))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"DRY-RUN: copy memory -> {self.skills_target / 'memory'}", result.stdout)
        self.assertFalse(self.skills_target.exists())
        self.assertFalse(self.config_target.exists())

    def test_skills_copy_installs_only_manifest_skills(self) -> None:
        result = self.run_component(
            "skills",
            "--copy",
            "--replace",
            "--target",
            str(self.skills_target),
            "--backup-dir",
            str(self.backup),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        for name in SKILLS:
            with self.subTest(skill=name):
                self.assertTrue((self.skills_target / name / "SKILL.md").is_file())
        self.assertFalse(self.config_target.exists())

    def test_skills_conflict_requires_replace_and_preserves_existing_file(self) -> None:
        sentinel = self.skills_target / "release" / "sentinel"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_text("keep", encoding="utf-8")

        result = self.run_component("skills", "--copy", "--target", str(self.skills_target))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CONFLICT", result.stderr)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_config_is_explicit_and_can_be_copied_separately(self) -> None:
        dry_run = self.run_component("config", "--dry-run", "--target", str(self.config_target))

        self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
        self.assertIn(f"DRY-RUN: copy config -> {self.config_target}", dry_run.stdout)
        self.assertFalse(self.config_target.exists())

        apply = self.run_component(
            "config",
            "--copy",
            "--replace",
            "--target",
            str(self.config_target),
            "--backup-dir",
            str(self.backup),
        )

        self.assertEqual(apply.returncode, 0, apply.stderr)
        self.assertTrue((self.config_target / "defaults.yaml").is_file())
        self.assertFalse(self.skills_target.exists())

    def test_config_replace_backs_up_existing_configuration(self) -> None:
        self.config_target.mkdir(parents=True)
        sentinel = self.config_target / "sentinel"
        sentinel.write_text("replace", encoding="utf-8")

        result = self.run_component(
            "config",
            "--copy",
            "--replace",
            "--target",
            str(self.config_target),
            "--backup-dir",
            str(self.backup),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        backups = list(self.backup.glob("*/config/sentinel"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "replace")

    def test_unknown_component_is_usage_error_without_writes(self) -> None:
        result = self.run_component("unknown", "--dry-run")

        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown installer component", result.stderr)
        self.assertFalse(self.skills_target.exists())
        self.assertFalse(self.config_target.exists())

    def test_default_skills_target_uses_codex_home(self) -> None:
        codex_home = self.root / "codex-home"
        result = subprocess.run(
            ["bash", str(ROOT / "scripts" / "install.sh"), "skills"],
            cwd=ROOT,
            env={**os.environ, "CODEX_HOME": str(codex_home)},
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"DRY-RUN: copy release -> {codex_home / 'skills' / 'release'}", result.stdout)
        self.assertFalse(codex_home.exists())
