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

    def test_dry_run_does_not_create_target_or_release(self) -> None:
        result = self.run_install("--dry-run")
        config_dest = self.target.parent / "config"

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                f"DRY-RUN: copy config -> {config_dest}",
                *(
                    f"DRY-RUN: copy {name} -> {self.target / name}"
                    for name in (
                        "memory",
                        "gitnexus",
                        "openspec",
                        "release",
                        "karpathy-guidelines-zh",
                    )
                ),
            ],
        )
        self.assertFalse(self.target.exists())
        self.assertFalse(config_dest.exists())
        self.assertFalse((self.target / "release").exists())
        self.assertFalse(self.backup.exists())

    def test_dry_run_reports_conflict_and_replace_advice_without_writes(self) -> None:
        sentinel = self.target / "release" / "sentinel"
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
        self.assertIn("release", output)
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
        self.assertIn(
            f"DRY-RUN: copy config -> {codex_home / 'config'}",
            result.stdout,
        )
        self.assertIn(f"DRY-RUN: copy release -> {codex_home / 'skills' / 'release'}", result.stdout)
        self.assertFalse((codex_home / "skills").exists())
        self.assertFalse((codex_home / "config").exists())

    def test_invalid_arguments_exit_two_without_writes(self) -> None:
        for args in (("--link", "--copy"), ("--target",), ("--unknown",)):
            with self.subTest(args=args):
                result = self.run_install(*args)

                self.assertEqual(result.returncode, 2)
                self.assertIn("usage", f"{result.stdout}\n{result.stderr}".lower())
                self.assertFalse(self.target.exists())
                self.assertFalse(self.backup.exists())

    def test_copy_without_replace_preserves_existing_release(self) -> None:
        sentinel = self.target / "release" / "sentinel"
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
        release = self.target / "release"
        release.mkdir(parents=True)
        (release / "sentinel").write_text("replace", encoding="utf-8")

        result = self.run_install("--copy", "--replace")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.target / "release" / "SKILL.md").is_file())
        backup_sentinels = list(self.backup.glob("*/release/sentinel"))
        self.assertEqual(len(backup_sentinels), 1)
        self.assertEqual(backup_sentinels[0].read_text(encoding="utf-8"), "replace")

    def test_copy_installs_config_and_skills_as_files(self) -> None:
        result = self.run_install("--copy", "--replace")
        config_dest = self.target.parent / "config"

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(config_dest.is_dir())
        self.assertFalse(config_dest.is_symlink())
        self.assertTrue((config_dest / "defaults.yaml").is_file())
        for name in (
            "memory",
            "gitnexus",
            "openspec",
            "release",
            "karpathy-guidelines-zh",
        ):
            with self.subTest(skill=name):
                installed = self.target / name
                self.assertTrue(installed.is_dir())
                self.assertFalse(installed.is_symlink())
                self.assertTrue((installed / "SKILL.md").is_file())

    def test_link_installs_all_manifest_skills(self) -> None:
        result = self.run_install("--link", "--replace")
        config_dest = self.target.parent / "config"

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(config_dest.is_symlink())
        self.assertEqual(config_dest.resolve(), (ROOT / "config").resolve())
        self.assertTrue((config_dest / "defaults.yaml").is_file())
        self.assertIn("INSTALLED: config ->", result.stdout)
        for name in (
            "memory",
            "gitnexus",
            "openspec",
            "release",
            "karpathy-guidelines-zh",
        ):
            with self.subTest(skill=name):
                installed = self.target / name
                self.assertTrue(installed.is_symlink())
                self.assertEqual(installed.resolve(), (ROOT / "skills" / name).resolve())
                self.assertIn(f"INSTALLED: {name}", result.stdout)

    def test_failed_creation_rolls_back_new_links_and_restores_backup(self) -> None:
        release = self.target / "release"
        release.mkdir(parents=True)
        (release / "sentinel").write_text("restore", encoding="utf-8")
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
        self.assertEqual((release / "sentinel").read_text(encoding="utf-8"), "restore")
        self.assertFalse((self.target / "memory").exists())
        self.assertFalse((self.target / "gitnexus").exists())
        self.assertFalse((self.target / "openspec").exists())
        self.assertFalse((self.target.parent / "config").exists())
        self.assertEqual(list(self.backup.glob("*/release")), [])
