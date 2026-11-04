"""Exercise the expanded AIHero package through real component entrypoints."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NEW_SKILLS = (
    "grill-with-docs", "to-spec", "to-tickets", "implement", "code-review", "wayfinder",
    "grilling", "domain-modeling", "research", "prototype", "handoff",
)
CURRENT_SKILLS = ("memory", "gitnexus", "grill-me", "tdd", "diagnosing-bugs", "codebase-design", "resolving-merge-conflicts", "retro", "setup-matt-pocock-skills")
RESTORED = ("grill-with-docs", "grilling", "domain-modeling")


class AiheroInstallContract:
    shell: str

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="aihero install ")
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
        (sentinel.parent / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Existing installed Skill fixture.\n---\nOld body.\n", encoding="utf-8"
        )
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

    def install_crlf(self, *args: str, fail_catalog: bool = False) -> subprocess.CompletedProcess[str]:
        """Run real helpers with Windows-style stdout, including on Unix CI."""
        shim = self.root / "crlf_stdout.py"
        shim.write_text(
            "import os, subprocess, sys\n"
            "if os.environ.get('AI_WORKFLOW_FAIL_CATALOG') == '1' and '--field' in sys.argv:\n"
            "    print('fixture catalog failure', file=sys.stderr)\n"
            "    sys.exit(23)\n"
            "result = subprocess.run([sys.executable, *sys.argv[1:]], stdout=subprocess.PIPE)\n"
            "sys.stdout.buffer.write(result.stdout.replace(b'\\r\\n', b'\\n').replace(b'\\n', b'\\r\\n'))\n"
            "sys.exit(result.returncode)\n",
            encoding="utf-8",
        )
        command = [
            shutil.which("bash"), "-c",
            'python3() { "$AI_WORKFLOW_REAL_PYTHON" "$AI_WORKFLOW_CRLF_SHIM" "$@"; }; '
            'export -f python3; exec bash "$@"',
            "crlf-fixture", str(ROOT / "scripts/install.sh"), "skills", *args,
            "--target", str(self.target), "--backup-dir", str(self.backup),
        ]
        return subprocess.run(
            command, cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
            env={**os.environ, "PYTHONUTF8": "1",
                 "AI_WORKFLOW_REAL_PYTHON": Path(sys.executable).as_posix(),
                 "AI_WORKFLOW_CRLF_SHIM": shim.as_posix(),
                 "AI_WORKFLOW_FAIL_CATALOG": "1" if fail_catalog else "0"},
        )

    def test_crlf_catalog_supports_default_mode_preview_and_copy(self) -> None:
        preview = self.install_crlf("--dry-run")
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        self.assertIn("DRY-RUN: copy memory ->", preview.stdout)
        self.assertFalse(self.target.exists())
        result = self.install_crlf("--copy")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual({p.name for p in self.target.iterdir()}, set(CURRENT_SKILLS + NEW_SKILLS))

    def test_crlf_lock_path_adoption_preserves_unrelated_entries(self) -> None:
        lock = self.root / ".skill-lock.json"
        original = {"version": 3, "skills": {"memory": {"source": "upstream"},
                                            "personal": {"source": "keep"}}}
        lock.write_text(json.dumps(original), encoding="utf-8")
        result = self.install_crlf("--copy", "--adopt-skill-lock")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(lock.read_text()),
                         {"version": 3, "skills": {"personal": {"source": "keep"}}})
        backups = list(self.backup.glob(".skill-lock.json.*.bak"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(json.loads(backups[0].read_text()), original)

    def test_crlf_catalog_failure_preserves_status_and_stderr_without_writes(self) -> None:
        result = self.install_crlf("--copy", fail_catalog=True)
        self.assertEqual(result.returncode, 23, result.stdout + result.stderr)
        self.assertIn("fixture catalog failure", result.stderr)
        self.assertFalse(self.target.exists())
        self.assertFalse(self.backup.exists())


@unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7+ is required")
class AiheroInstallPsTests(AiheroInstallContract, unittest.TestCase):
    shell = "pwsh"


if __name__ == "__main__":
    unittest.main()
