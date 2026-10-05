"""Exercise the expanded AIHero package through real component entrypoints."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NEW_SKILLS = (
    "grill-with-docs", "to-spec", "to-tickets", "implement", "code-review", "wayfinder",
    "grilling", "domain-modeling", "research", "prototype", "handoff",
)
CURRENT_SKILLS = ("memory", "gitnexus", "grill-me", "tdd", "diagnosing-bugs", "codebase-design", "resolving-merge-conflicts")
RESTORED = ("grill-with-docs", "grilling", "domain-modeling")


class AiheroInstallContract:
    shell: str

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / "skills"
        self.backup = self.root / "backups"

    def install(self, *args: str) -> subprocess.CompletedProcess[str]:
        if self.shell == "pwsh":
            command = [shutil.which("pwsh"), "-NoProfile", "-File", str(ROOT / "scripts/install.ps1"), "skills"]
        else:
            command = [shutil.which("bash"), str(ROOT / "scripts/install.sh"), "skills"]
        return subprocess.run(
            [*command, *args, "--target", str(self.target), "--backup-dir", str(self.backup)],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
            env={**os.environ, "PYTHONUTF8": "1"},
        )

    def seed_old(self, name: str) -> Path:
        sentinel = self.target / name / "sentinel.txt"
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        sentinel.write_text(f"user copy of {name}", encoding="utf-8")
        return sentinel

    def test_fresh_install_copies_all_skills_metadata_and_licenses(self) -> None:
        result = self.install("--copy")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual({p.name for p in self.target.iterdir()}, set(CURRENT_SKILLS + NEW_SKILLS))
        for name in NEW_SKILLS:
            with self.subTest(skill=name):
                for relative in ("SKILL.md", "agents/openai.yaml", "LICENSE"):
                    self.assertEqual((self.target / name / relative).read_bytes(), (ROOT / "skills" / name / relative).read_bytes())
        self.assertFalse(self.backup.exists())

    def test_preview_preserves_old_restored_skills_and_does_not_prune_them(self) -> None:
        originals = {name: self.seed_old(name) for name in RESTORED}
        result = self.install("--dry-run", "--prune-legacy")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name, path in originals.items():
            self.assertEqual(path.read_text(encoding="utf-8"), f"user copy of {name}")
            self.assertNotIn(f"remove legacy Skill: {name}", result.stdout)
        self.assertFalse(self.backup.exists())
        self.assertFalse((self.target / "implement").exists())

    def test_upgrade_replaces_restored_skills_with_backups_and_prunes_only_legacy(self) -> None:
        for name in (*RESTORED, "review"):
            self.seed_old(name)
        result = self.install("--copy", "--replace", "--prune-legacy")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in RESTORED:
            with self.subTest(skill=name):
                self.assertTrue((self.target / name / "SKILL.md").is_file())
                self.assertFalse((self.target / name / "sentinel.txt").exists())
                saved = list(self.backup.glob(f"{name}.*.bak/sentinel.txt"))
                self.assertEqual(len(saved), 1)
                self.assertEqual(saved[0].read_text(encoding="utf-8"), f"user copy of {name}")
                self.assertNotIn(f"PRUNED: legacy Skill {name}", result.stdout)
        self.assertFalse((self.target / "review").exists())
        self.assertIn("PRUNED: legacy Skill review", result.stdout)
        self.assertEqual(len(list(self.backup.glob("review.*.bak/sentinel.txt"))), 1)


@unittest.skipUnless(shutil.which("bash"), "Bash is required")
class AiheroInstallBashTests(AiheroInstallContract, unittest.TestCase):
    shell = "bash"


@unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7+ is required")
class AiheroInstallPsTests(AiheroInstallContract, unittest.TestCase):
    shell = "pwsh"


if __name__ == "__main__":
    unittest.main()
