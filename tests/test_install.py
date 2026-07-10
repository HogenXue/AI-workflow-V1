import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def snapshot_tree(root: Path) -> tuple[tuple[str, bytes | None], ...]:
    if not root.exists():
        return ()
    return tuple(
        (path.relative_to(root).as_posix(), None if path.is_dir() else path.read_bytes())
        for path in sorted(root.rglob("*"))
    )


class InstallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        root = Path(self.temp_dir.name)
        self.target = root / "target"
        self.backup = root / "backup"

    def run_install(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "bash",
                str(ROOT / "scripts" / "install.sh"),
                *args,
                "--target",
                str(self.target),
                "--backup-dir",
                str(self.backup),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_dry_run_does_not_create_target_or_review(self) -> None:
        result = self.run_install("--dry-run")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                f"DRY-RUN: link {name} -> {self.target / name}"
                for name in ("memory", "gitnexus", "openspec", "review", "debugging", "release")
            ],
        )
        self.assertFalse(self.target.exists())
        self.assertFalse((self.target / "review").exists())
        self.assertFalse(self.backup.exists())

    def test_dry_run_reports_conflict_and_replace_advice_without_writes(self) -> None:
        sentinel = self.target / "review" / "sentinel"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_text("keep", encoding="utf-8")
        self.backup.mkdir()
        (self.backup / "existing-backup").write_text("preserve", encoding="utf-8")
        target_before = snapshot_tree(self.target)
        backup_before = snapshot_tree(self.backup)

        result = self.run_install("--dry-run")

        self.assertEqual(result.returncode, 0, result.stderr)
        output = f"{result.stdout}\n{result.stderr}".lower()
        self.assertIn("conflict", output)
        self.assertIn("review", output)
        self.assertIn("--replace", output)
        self.assertEqual(snapshot_tree(self.target), target_before)
        self.assertEqual(snapshot_tree(self.backup), backup_before)

    def test_default_dry_run_uses_codex_home_skills_directory(self) -> None:
        codex_home = Path(self.temp_dir.name) / "codex-home"
        result = subprocess.run(
            ["bash", str(ROOT / "scripts" / "install.sh")],
            cwd=ROOT,
            env={**os.environ, "CODEX_HOME": str(codex_home)},
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"DRY-RUN: link review -> {codex_home / 'skills' / 'review'}", result.stdout)
        self.assertFalse((codex_home / "skills").exists())

    def test_invalid_arguments_exit_two_without_writes(self) -> None:
        for args in (("--link", "--copy"), ("--target",), ("--unknown",)):
            with self.subTest(args=args):
                result = self.run_install(*args)

                self.assertEqual(result.returncode, 2)
                self.assertIn("usage", f"{result.stdout}\n{result.stderr}".lower())
                self.assertFalse(self.target.exists())
                self.assertFalse(self.backup.exists())

    def test_copy_without_replace_preserves_existing_review(self) -> None:
        sentinel = self.target / "review" / "sentinel"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_text("keep", encoding="utf-8")
        before = snapshot_tree(self.target)

        result = self.run_install("--copy")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("conflict", f"{result.stdout}\n{result.stderr}".lower())
        self.assertTrue(sentinel.exists())
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
        self.assertEqual(snapshot_tree(self.target), before)

    def test_copy_replace_installs_skill_and_creates_backup(self) -> None:
        review = self.target / "review"
        review.mkdir(parents=True)
        (review / "sentinel").write_text("replace", encoding="utf-8")

        result = self.run_install("--copy", "--replace")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.target / "review" / "SKILL.md").is_file())
        backup_sentinels = list(self.backup.glob("*/review/sentinel"))
        self.assertEqual(len(backup_sentinels), 1)
        self.assertEqual(backup_sentinels[0].read_text(encoding="utf-8"), "replace")

    def test_link_installs_all_manifest_skills(self) -> None:
        result = self.run_install("--link", "--replace")

        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ("memory", "gitnexus", "openspec", "review", "debugging", "release"):
            with self.subTest(skill=name):
                installed = self.target / name
                self.assertTrue(installed.is_symlink())
                self.assertEqual(installed.resolve(), (ROOT / "skills" / name).resolve())
                self.assertIn(f"INSTALLED: {name}", result.stdout)

    def test_failed_creation_rolls_back_new_links_and_restores_backup(self) -> None:
        review = self.target / "review"
        review.mkdir(parents=True)
        (review / "sentinel").write_text("restore", encoding="utf-8")
        fake_bin = Path(self.temp_dir.name) / "bin"
        fake_bin.mkdir()
        failing_link = fake_bin / "ln"
        failing_link.write_text(
            "#!/bin/sh\n"
            "if [ \"$3\" = \"$FAIL_DESTINATION\" ]; then\n"
            "  exit 1\n"
            "fi\n"
            "exec /bin/ln \"$@\"\n",
            encoding="utf-8",
        )
        failing_link.chmod(0o755)

        result = subprocess.run(
            [
                "bash",
                str(ROOT / "scripts" / "install.sh"),
                "--link",
                "--replace",
                "--target",
                str(self.target),
                "--backup-dir",
                str(self.backup),
            ],
            cwd=ROOT,
            env={
                **os.environ,
                "PATH": f"{fake_bin}{os.pathsep}{os.environ['PATH']}",
                "FAIL_DESTINATION": str(self.target / "openspec"),
            },
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rolling back", result.stderr.lower())
        self.assertEqual((review / "sentinel").read_text(encoding="utf-8"), "restore")
        self.assertFalse((self.target / "memory").exists())
        self.assertFalse((self.target / "gitnexus").exists())
        self.assertFalse((self.target / "openspec").exists())
        self.assertEqual(list(self.backup.glob("*/review")), [])
