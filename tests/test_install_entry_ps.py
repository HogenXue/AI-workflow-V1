"""Minimal entry tests for scripts/install.ps1 and install.cmd."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _find_pwsh() -> str | None:
    return shutil.which("pwsh")


@unittest.skipUnless(_find_pwsh(), "pwsh (PowerShell 7+) is required")
class InstallEntryPsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.skills_target = self.root / "skills"

    def run_install_ps(self, *args: str, stdin=subprocess.DEVNULL) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [_find_pwsh(), "-NoProfile", "-File", str(ROOT / "scripts" / "install.ps1"), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            stdin=stdin,
        )

    def test_no_args_non_tty_exits_2(self) -> None:
        result = self.run_install_ps()
        self.assertEqual(result.returncode, 2)
        combined = (result.stderr + result.stdout).lower()
        self.assertIn("interactive", combined)
        self.assertIn("usage", combined)

    def test_help_exits_0(self) -> None:
        result = self.run_install_ps("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stderr)

    def test_unknown_component_exits_2(self) -> None:
        result = self.run_install_ps("unknown")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown installer component", result.stderr)
        self.assertFalse(self.skills_target.exists())

    def test_skills_dry_run_via_dispatch(self) -> None:
        result = self.run_install_ps(
            "skills",
            "--dry-run",
            "--target",
            str(self.skills_target),
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn(f"DRY-RUN: copy memory -> {self.skills_target / 'memory'}", result.stdout)
        self.assertFalse(self.skills_target.exists())

    @unittest.skipUnless(os.name == "nt", "install.cmd is Windows-only")
    def test_install_cmd_skills_dry_run(self) -> None:
        result = subprocess.run(
            [
                "cmd",
                "/c",
                str(ROOT / "scripts" / "install.cmd"),
                "skills",
                "--dry-run",
                "--target",
                str(self.skills_target),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("DRY-RUN: copy memory", result.stdout)
        self.assertFalse(self.skills_target.exists())
