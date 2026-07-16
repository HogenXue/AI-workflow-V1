import os
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
        self.assertIn(
            f"DRY-RUN: copy grill-with-docs -> {self.skills_target / 'grill-with-docs'}",
            result.stdout,
        )
        self.assertIn(f"DRY-RUN: copy tdd -> {self.skills_target / 'tdd'}", result.stdout)
        self.assertNotIn("DRY-RUN: copy review", result.stdout)
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

        replace = self.run_component(
            "skills",
            "--copy",
            "--replace",
            "--target",
            str(self.skills_target),
            "--backup-dir",
            str(self.backup),
        )
        self.assertEqual(replace.returncode, 0, replace.stderr)
        backups = list(self.backup.glob("release.*.bak/sentinel"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "keep")

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
        self.assertTrue((self.config_target / "effective_config.py").is_file())
        self.assertTrue((self.config_target / "workflow_check.py").is_file())
        self.assertTrue((self.config_target / "consumers.yaml").is_file())
        self.assertFalse((self.config_target / "__pycache__").exists())
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
        backups = list(self.backup.glob("config.*.bak/sentinel"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "replace")

    def test_config_rejects_backup_directory_inside_target(self) -> None:
        self.config_target.mkdir(parents=True)
        sentinel = self.config_target / "sentinel"
        sentinel.write_text("keep\n", encoding="utf-8")
        nested_backup = self.config_target / ".backups"

        result = self.run_component(
            "config",
            "--copy",
            "--replace",
            "--target",
            str(self.config_target),
            "--backup-dir",
            str(nested_backup),
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")
        self.assertFalse(nested_backup.exists())

    def test_config_trailing_slash_uses_parent_backup_root(self) -> None:
        self.config_target.mkdir(parents=True)
        sentinel = self.config_target / "sentinel"
        sentinel.write_text("old config\n", encoding="utf-8")

        result = self.run_component(
            "config",
            "--copy",
            "--replace",
            "--target",
            f"{self.config_target}/",
        )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        backups = list(
            (self.root / ".ai-workflow-backups").glob("config.*.bak/sentinel")
        )
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "old config\n")

    def test_unknown_component_is_usage_error_without_writes(self) -> None:
        result = self.run_component("unknown", "--dry-run")

        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown installer component", result.stderr)
        self.assertFalse(self.skills_target.exists())
        self.assertFalse(self.config_target.exists())

    def test_config_rejects_source_directory_as_target(self) -> None:
        result = self.run_component(
            "config",
            "--dry-run",
            "--target",
            str(ROOT / "config"),
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("overlaps package source", result.stderr)

    def test_config_rejects_nonexistent_target_inside_source(self) -> None:
        target = ROOT / "config" / ".test-install-target-does-not-exist"
        self.assertFalse(target.exists())

        result = self.run_component("config", "--dry-run", "--target", str(target))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("overlaps package source", result.stderr)

    def test_skills_rejects_source_directory_as_target(self) -> None:
        result = self.run_component(
            "skills",
            "--dry-run",
            "--target",
            str(ROOT / "skills"),
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("overlaps package source", result.stderr)

    def test_skills_rejects_nonexistent_target_inside_source(self) -> None:
        target = ROOT / "skills" / ".test-install-target-does-not-exist"
        self.assertFalse(target.exists())

        result = self.run_component("skills", "--dry-run", "--target", str(target))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("overlaps package source", result.stderr)

    def test_parallel_backups_never_overwrite_each_other(self) -> None:
        source = self.root / "source.txt"
        source.write_text("original\n", encoding="utf-8")
        fake_bin = self.root / "fake-bin"
        fake_bin.mkdir()
        slow_cp = fake_bin / "cp"
        slow_cp.write_text(
            "#!/usr/bin/env bash\nsleep 0.1\nexec /bin/cp \"$@\"\n",
            encoding="utf-8",
        )
        slow_cp.chmod(0o755)
        backup_dir = self.root / "parallel-backups"
        command = (
            'source "$1"; '
            'install_lib_backup_file "$2" "$3" "source.txt"'
        )
        env = {**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}"}

        processes = [
            subprocess.Popen(
                [
                    "bash",
                    "-c",
                    command,
                    "backup-test",
                    str(ROOT / "scripts" / "install-lib.sh"),
                    str(source),
                    str(backup_dir),
                ],
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            for _ in range(2)
        ]
        results = [process.communicate() + (process.returncode,) for process in processes]

        for stdout, stderr, returncode in results:
            self.assertEqual(returncode, 0, stderr + stdout)
        backups = list(backup_dir.glob("source.txt.*.bak"))
        self.assertEqual(len(backups), 2)
        self.assertFalse(list(backup_dir.glob("*.lock")))
        self.assertEqual(
            {path.read_text(encoding="utf-8") for path in backups},
            {"original\n"},
        )

    def test_unwritable_backup_directory_fails_without_hanging(self) -> None:
        source = self.root / "source.txt"
        source.write_text("original\n", encoding="utf-8")
        backup_dir = self.root / "unwritable-backups"
        backup_dir.mkdir()
        backup_dir.chmod(0o555)
        command = (
            'source "$1"; '
            'install_lib_backup_file "$2" "$3" "source.txt"'
        )
        try:
            result = subprocess.run(
                [
                    "bash",
                    "-c",
                    command,
                    "backup-test",
                    str(ROOT / "scripts" / "install-lib.sh"),
                    str(source),
                    str(backup_dir),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=2,
            )
        finally:
            backup_dir.chmod(0o755)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("could not reserve backup path", result.stderr)
        self.assertEqual(source.read_text(encoding="utf-8"), "original\n")
        self.assertFalse(list(backup_dir.iterdir()))

    def test_failed_backup_copy_never_publishes_partial_bak(self) -> None:
        source = self.root / "source.txt"
        source.write_text("original\n", encoding="utf-8")
        fake_bin = self.root / "failing-bin"
        fake_bin.mkdir()
        failing_cp = fake_bin / "cp"
        failing_cp.write_text(
            "#!/usr/bin/env bash\ndest=\"${!#}\"\nprintf 'partial\\n' > \"$dest\"\nexit 1\n",
            encoding="utf-8",
        )
        failing_cp.chmod(0o755)
        backup_dir = self.root / "failed-backups"
        command = (
            'source "$1"; '
            'install_lib_backup_file "$2" "$3" "source.txt"'
        )

        result = subprocess.run(
            [
                "bash",
                "-c",
                command,
                "backup-test",
                str(ROOT / "scripts" / "install-lib.sh"),
                str(source),
                str(backup_dir),
            ],
            cwd=ROOT,
            env={**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}"},
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(list(backup_dir.glob("*.bak")))
        self.assertFalse(list(backup_dir.glob("*.lock")))
        self.assertEqual(source.read_text(encoding="utf-8"), "original\n")

    def test_default_skills_target_uses_agents_home(self) -> None:
        home = self.root / "home"
        result = subprocess.run(
            ["bash", str(ROOT / "scripts" / "install.sh"), "skills"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home)},
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            f"DRY-RUN: copy release -> {home / '.agents' / 'skills' / 'release'}",
            result.stdout,
        )
        self.assertFalse(home.exists())

    def test_agents_target_warns_about_duplicate_codex_skill_names(self) -> None:
        home = self.root / "home"
        codex_home = home / ".codex"
        duplicate = codex_home / "skills" / "memory"
        duplicate.mkdir(parents=True)

        result = subprocess.run(
            ["bash", str(ROOT / "scripts" / "install.sh"), "skills", "--dry-run"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home), "CODEX_HOME": str(codex_home)},
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("duplicate Skill names", result.stderr)
        self.assertIn(str(codex_home / "skills"), result.stderr)
        self.assertIn("memory", result.stderr)

    def test_other_root_pruning_is_explicit_and_backed_up(self) -> None:
        home = self.root / "home"
        codex_home = home / ".codex"
        duplicate = codex_home / "skills" / "memory" / "sentinel"
        duplicate.parent.mkdir(parents=True)
        duplicate.write_text("duplicate", encoding="utf-8")
        target = home / ".agents" / "skills"

        preview = subprocess.run(
            [
                "bash",
                str(ROOT / "scripts" / "install.sh"),
                "skills",
                "--dry-run",
                "--prune-other-root",
                "--target",
                str(target),
                "--backup-dir",
                str(self.backup),
            ],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home), "CODEX_HOME": str(codex_home)},
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertIn("would back up and remove other-root Skill", preview.stdout)
        self.assertEqual(duplicate.read_text(encoding="utf-8"), "duplicate")

        apply = subprocess.run(
            [
                "bash",
                str(ROOT / "scripts" / "install.sh"),
                "skills",
                "--copy",
                "--prune-other-root",
                "--target",
                str(target),
                "--backup-dir",
                str(self.backup),
            ],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home), "CODEX_HOME": str(codex_home)},
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(apply.returncode, 0, apply.stderr)
        self.assertFalse(duplicate.exists())
        backups = list(self.backup.glob("memory.*.bak/sentinel"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "duplicate")
        self.assertTrue((target / "memory" / "SKILL.md").is_file())

    def test_default_config_target_uses_agents_config(self) -> None:
        home = self.root / "home"
        result = subprocess.run(
            ["bash", str(ROOT / "scripts" / "install.sh"), "config"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home)},
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"DRY-RUN: copy config -> {home / '.agents' / 'config'}", result.stdout)
        self.assertFalse(home.exists())

    def test_default_component_backups_share_agents_root(self) -> None:
        home = self.root / "home"
        skills_target = home / ".agents" / "skills"
        release_sentinel = skills_target / "release" / "sentinel"
        release_sentinel.parent.mkdir(parents=True)
        release_sentinel.write_text("old release\n", encoding="utf-8")

        skills = subprocess.run(
            ["bash", str(ROOT / "scripts" / "install.sh"), "skills", "--copy", "--replace"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home)},
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(skills.returncode, 0, skills.stderr)

        config_target = home / ".agents" / "config"
        config_target.mkdir()
        config_sentinel = config_target / "sentinel"
        config_sentinel.write_text("old config\n", encoding="utf-8")
        config = subprocess.run(
            ["bash", str(ROOT / "scripts" / "install.sh"), "config", "--copy", "--replace"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home)},
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(config.returncode, 0, config.stderr)

        backup_root = home / ".agents" / ".ai-workflow-backups"
        self.assertEqual(
            len(list(backup_root.glob("release.*.bak/sentinel"))),
            1,
        )
        self.assertEqual(
            len(list(backup_root.glob("config.*.bak/sentinel"))),
            1,
        )

    def test_legacy_workflow_skills_pruning_is_explicit_and_backed_up(self) -> None:
        sentinels = {}
        for name in ("openspec", "review", "grill-me"):
            sentinel = self.skills_target / name / "sentinel"
            sentinel.parent.mkdir(parents=True)
            sentinel.write_text("legacy", encoding="utf-8")
            sentinels[name] = sentinel

        preview = self.run_component(
            "skills",
            "--dry-run",
            "--prune-legacy",
            "--target",
            str(self.skills_target),
            "--backup-dir",
            str(self.backup),
        )

        self.assertEqual(preview.returncode, 0, preview.stderr)
        for name, sentinel in sentinels.items():
            self.assertIn(f"would back up and remove legacy Skill: {name}", preview.stdout)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "legacy")

        apply = self.run_component(
            "skills",
            "--copy",
            "--replace",
            "--prune-legacy",
            "--target",
            str(self.skills_target),
            "--backup-dir",
            str(self.backup),
        )

        self.assertEqual(apply.returncode, 0, apply.stderr)
        for name in sentinels:
            self.assertFalse((self.skills_target / name).exists())
            backups = list(self.backup.glob(f"{name}.*.bak/sentinel"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "legacy")

    def test_prune_legacy_dry_run_succeeds_when_no_legacy_skills_exist(self) -> None:
        result = self.run_component(
            "skills",
            "--dry-run",
            "--prune-legacy",
            "--target",
            str(self.skills_target),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("would back up and remove legacy Skill", result.stdout)
