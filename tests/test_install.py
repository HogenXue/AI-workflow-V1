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
        self.assertFalse(self.target.exists())
        self.assertFalse((self.target / "review").exists())
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
