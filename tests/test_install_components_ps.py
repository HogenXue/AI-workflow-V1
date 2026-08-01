"""Focused smoke tests for PowerShell component installers (skills/config)."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "memory",
    "gitnexus",
    "release",
    "karpathy-guidelines-zh",
    "grill-with-docs",
    "tdd",
    "diagnosing-bugs",
    "codebase-design",
    "resolving-merge-conflicts",
)


def _find_pwsh() -> str | None:
    return shutil.which("pwsh")


@unittest.skipUnless(_find_pwsh(), "pwsh (PowerShell 7+) is required")
class InstallComponentsPsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.skills_target = self.root / "skills"
        self.config_target = self.root / "config"
        self.backup = self.root / "backup"

    def run_ps(self, script: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [_find_pwsh(), "-NoProfile", "-File", str(ROOT / "scripts" / script), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_skills_dry_run_does_not_write(self) -> None:
        result = self.run_ps(
            "install-skills.ps1",
            "--dry-run",
            "--target",
            str(self.skills_target),
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn(f"DRY-RUN: copy memory -> {self.skills_target / 'memory'}", result.stdout)
        self.assertIn(f"DRY-RUN: copy tdd -> {self.skills_target / 'tdd'}", result.stdout)
        self.assertFalse(self.skills_target.exists())

    def test_skills_copy_and_conflict(self) -> None:
        install = self.run_ps(
            "install-skills.ps1",
            "--copy",
            "--target",
            str(self.skills_target),
            "--backup-dir",
            str(self.backup),
        )
        self.assertEqual(install.returncode, 0, install.stderr + install.stdout)
        for name in SKILLS:
            with self.subTest(skill=name):
                self.assertTrue((self.skills_target / name / "SKILL.md").is_file())

        sentinel = self.skills_target / "release" / "sentinel"
        sentinel.write_text("keep", encoding="utf-8")
        conflict = self.run_ps(
            "install-skills.ps1",
            "--copy",
            "--target",
            str(self.skills_target),
        )
        self.assertNotEqual(conflict.returncode, 0)
        self.assertIn("CONFLICT", conflict.stderr)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_config_copy_and_overlap_reject(self) -> None:
        dry = self.run_ps(
            "install-config.ps1",
            "--dry-run",
            "--target",
            str(self.config_target),
        )
        self.assertEqual(dry.returncode, 0, dry.stderr + dry.stdout)
        self.assertIn(f"DRY-RUN: copy config -> {self.config_target}", dry.stdout)
        self.assertFalse(self.config_target.exists())

        copy = self.run_ps(
            "install-config.ps1",
            "--copy",
            "--target",
            str(self.config_target),
            "--backup-dir",
            str(self.backup),
        )
        self.assertEqual(copy.returncode, 0, copy.stderr + copy.stdout)
        self.assertTrue((self.config_target / "defaults.yaml").is_file())

        overlap = self.run_ps(
            "install-config.ps1",
            "--copy",
            "--target",
            str(ROOT / "config"),
        )
        self.assertNotEqual(overlap.returncode, 0)
        self.assertIn("overlaps package source", overlap.stderr)

    def test_default_skills_target_uses_home_agents(self) -> None:
        home = self.root / "home"
        home.mkdir()
        result = subprocess.run(
            [
                _find_pwsh(),
                "-NoProfile",
                "-File",
                str(ROOT / "scripts" / "install-skills.ps1"),
                "--dry-run",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            env={**os.environ, "HOME": str(home)},
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        expected = home / ".agents" / "skills" / "release"
        self.assertIn(f"DRY-RUN: copy release -> {expected}", result.stdout)
