import json
import os
import subprocess
import sys
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
    "setup-matt-pocock-skills",
)


class ComponentInstallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.skills_target = self.root / "skills"
        self.config_target = self.root / "config"
        self.backup = self.root / "backup"

    def run_component(
        self, component: str, *args: str, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(ROOT / "scripts" / "install.sh"), component, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            env=env,
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
        self.assertEqual({path.name for path in self.skills_target.iterdir()}, set(SKILLS))
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

    def test_skill_lock_adoption_detaches_owned_names_and_preserves_other_content(self) -> None:
        lock = self.root / ".skill-lock.json"
        original = {
            "version": 3,
            "skills": {
                "tdd": {"source": "mattpocock/skills", "skillFolderHash": "old"},
                "grill-with-docs": {"source": "mattpocock/skills"},
                "ask-matt": {"source": "mattpocock/skills"},
            },
            "dismissed": {"notice": True},
            "lastSelectedAgents": ["codex"],
        }
        lock.write_text(json.dumps(original), encoding="utf-8")
        result = self.run_component(
            "skills", "--copy", "--replace", "--adopt-skill-lock",
            "--target", str(self.skills_target), "--backup-dir", str(self.backup),
        )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        expected = {**original, "skills": {"ask-matt": original["skills"]["ask-matt"]}}
        self.assertEqual(json.loads(lock.read_text(encoding="utf-8")), expected)
        backups = list(self.backup.glob(".skill-lock.json.*.bak"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(json.loads(backups[0].read_text(encoding="utf-8")), original)
        self.assertEqual(
            (self.skills_target / "tdd" / "SKILL.md").read_bytes(),
            (ROOT / "skills" / "tdd" / "SKILL.md").read_bytes(),
        )

    def test_skill_lock_adoption_preview_is_read_only(self) -> None:
        lock = self.root / ".skill-lock.json"
        original = '{"version":3,"skills":{"tdd":{"source":"upstream"}}}\n'
        lock.write_text(original, encoding="utf-8")
        result = self.run_component(
            "skills", "--dry-run", "--replace", "--adopt-skill-lock",
            "--target", str(self.skills_target), "--backup-dir", str(self.backup),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("tdd", result.stdout)
        self.assertIn(".skill-lock.json", result.stdout)
        self.assertEqual(lock.read_text(encoding="utf-8"), original)
        self.assertFalse(self.skills_target.exists())
        self.assertFalse(self.backup.exists())

    def test_skill_lock_is_preserved_without_explicit_adoption(self) -> None:
        lock = self.root / ".skill-lock.json"
        original = '{"version":3,"skills":{"tdd":{"source":"upstream"}}}\n'
        lock.write_text(original, encoding="utf-8")
        result = self.run_component(
            "skills", "--copy", "--replace", "--target", str(self.skills_target),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(lock.read_text(encoding="utf-8"), original)

    def test_invalid_skill_lock_fails_before_replacing_skills(self) -> None:
        lock = self.root / ".skill-lock.json"
        lock.write_text('{"skills": []}', encoding="utf-8")
        sentinel = self.skills_target / "tdd" / "sentinel"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_text("original", encoding="utf-8")
        result = self.run_component(
            "skills", "--copy", "--replace", "--adopt-skill-lock",
            "--target", str(self.skills_target), "--backup-dir", str(self.backup),
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("skill lock", result.stderr.lower())
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "original")
        self.assertFalse(self.backup.exists())

    def test_skill_lock_fifo_is_rejected_without_blocking(self) -> None:
        lock = self.root / ".skill-lock.json"
        os.mkfifo(lock)
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "lib" / "adopt_skill_lock.py"),
             "--target", str(lock), "--skills", "tdd"],
            cwd=ROOT, text=True, capture_output=True, check=False, timeout=2,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("regular file", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_non_utf8_skill_lock_fails_before_replacing_skills(self) -> None:
        lock = self.root / ".skill-lock.json"
        original = b'\xff{"skills":{"tdd":{}}}'
        lock.write_bytes(original)
        sentinel = self.skills_target / "tdd" / "sentinel"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_text("original", encoding="utf-8")
        result = self.run_component(
            "skills", "--copy", "--replace", "--adopt-skill-lock",
            "--target", str(self.skills_target), "--backup-dir", str(self.backup),
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR: skill lock:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(lock.read_bytes(), original)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "original")
        self.assertFalse(self.backup.exists())

    def test_skill_lock_failure_rolls_back_replaced_skills_and_lock(self) -> None:
        lock = self.root / ".skill-lock.json"
        original = '{"version":3,"skills":{"tdd":{"source":"upstream"}}}\n'
        lock.write_text(original, encoding="utf-8")
        sentinel = self.skills_target / "tdd" / "sentinel"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_text("old tdd", encoding="utf-8")
        fake_bin = self.root / "fake-bin"
        fake_bin.mkdir()
        fake_python = fake_bin / "python3"
        fake_python.write_text(
            '#!/usr/bin/env bash\n'
            'for arg in "$@"; do\n'
            '  if [[ "$arg" == --apply ]]; then\n'
            '    printf "partial write\\n" > "$SKILL_LOCK_PATH"\n'
            '    exit 1\n'
            '  fi\n'
            'done\n'
            'exec "$ACTUAL_PYTHON" "$@"\n',
            encoding="utf-8",
        )
        fake_python.chmod(0o755)
        result = subprocess.run(
            ["bash", str(ROOT / "scripts" / "install.sh"), "skills", "--copy",
             "--replace", "--adopt-skill-lock", "--target", str(self.skills_target),
             "--backup-dir", str(self.backup)],
            cwd=ROOT, text=True, capture_output=True, check=False,
            env={**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}",
                 "ACTUAL_PYTHON": sys.executable, "SKILL_LOCK_PATH": str(lock)},
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rolling back", result.stderr)
        self.assertEqual(lock.read_text(encoding="utf-8"), original)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "old tdd")
        self.assertEqual({path.name for path in self.skills_target.iterdir()}, {"tdd"})
        self.assertEqual(len(list(self.backup.glob(".skill-lock.json.*.bak"))), 1)

    def test_skill_lock_symlink_fails_without_touching_its_target(self) -> None:
        actual = self.root / "external-lock.json"
        original = '{"skills":{"tdd":{"source":"upstream"}}}'
        actual.write_text(original, encoding="utf-8")
        lock = self.root / ".skill-lock.json"
        lock.symlink_to(actual)
        result = self.run_component(
            "skills", "--copy", "--replace", "--adopt-skill-lock",
            "--target", str(self.skills_target),
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink", result.stderr)
        self.assertTrue(lock.is_symlink())
        self.assertEqual(actual.read_text(encoding="utf-8"), original)
        self.assertFalse(self.skills_target.exists())

    def test_skill_lock_adoption_without_matching_entries_keeps_exact_contents(self) -> None:
        lock = self.root / ".skill-lock.json"
        original = '{"version":3,"skills":{"ask-matt":{"source":"upstream"}}}\n'
        lock.write_text(original, encoding="utf-8")
        result = self.run_component(
            "skills", "--copy", "--replace", "--adopt-skill-lock",
            "--target", str(self.skills_target), "--backup-dir", str(self.backup),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(lock.read_text(encoding="utf-8"), original)
        self.assertFalse(self.backup.exists())

    def test_custom_dot_target_adopts_parent_lock(self) -> None:
        target = self.root / "custom" / "skills"
        target.mkdir(parents=True)
        lock = target.parent / ".skill-lock.json"
        lock.write_text('{"skills":{"tdd":{"source":"upstream"}}}', encoding="utf-8")
        for spelling in (str(target / ".") + "/.", "."):
            with self.subTest(target=spelling):
                result = subprocess.run(
                    ["bash", str(ROOT / "scripts" / "install.sh"), "skills", "--dry-run",
                     "--adopt-skill-lock", "--target", spelling],
                    cwd=target, text=True, capture_output=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(str(lock), result.stdout)

    def test_missing_custom_dot_target_previews_parent_lock(self) -> None:
        parent = self.root / "custom-missing"
        parent.mkdir()
        lock = parent / ".skill-lock.json"
        lock.write_text('{"skills":{"tdd":{"source":"upstream"}}}', encoding="utf-8")
        result = self.run_component("skills", "--dry-run", "--adopt-skill-lock",
                                    "--target", str(parent / "skills") + "/.")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(lock), result.stdout)

    def test_custom_symlink_target_adopts_its_caller_adjacent_lock(self) -> None:
        actual_skills = self.root / "actual" / "skills"
        actual_skills.mkdir(parents=True)
        actual_lock = actual_skills.parent / ".skill-lock.json"
        actual_original = '{"skills":{"tdd":{"source":"actual-sentinel"}}}\n'
        actual_lock.write_text(actual_original, encoding="utf-8")
        target = self.root / "custom" / "skills"
        target.parent.mkdir()
        target.symlink_to(actual_skills, target_is_directory=True)
        lock = target.parent / ".skill-lock.json"
        original = '{"version":3,"skills":{"tdd":{"source":"upstream"}}}\n'
        lock.write_text(original, encoding="utf-8")

        result = self.run_component(
            "skills", "--copy", "--replace", "--adopt-skill-lock",
            "--target", str(target), "--backup-dir", str(self.backup),
        )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(actual_lock.read_text(encoding="utf-8"), actual_original)
        self.assertEqual(json.loads(lock.read_text(encoding="utf-8")), {"version": 3, "skills": {}})
        self.assertTrue(target.is_symlink())
        self.assertEqual((target / "tdd" / "SKILL.md").read_bytes(),
                         (ROOT / "skills" / "tdd" / "SKILL.md").read_bytes())
        backups = list(self.backup.glob(".skill-lock.json.*.bak"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), original)

    def test_standard_host_targets_adopt_the_shared_global_skill_lock(self) -> None:
        for index, suffix in enumerate((".agents/skills", ".codex/skills", ".cursor/skills")):
            with self.subTest(target=suffix):
                fixture_home = self.root / f"host-{index}"
                target = fixture_home / suffix
                lock = fixture_home / ".agents" / ".skill-lock.json"
                lock.parent.mkdir(parents=True)
                original = {"version": 3, "skills": {"tdd": {"source": "upstream"},
                            "ask-matt": {"source": "upstream"}}, "dismissed": {"notice": True}}
                lock.write_text(json.dumps(original), encoding="utf-8")
                adjacent = target.parent / ".skill-lock.json"
                if adjacent != lock:
                    adjacent.parent.mkdir(parents=True)
                    adjacent.write_text('{"skills":{"tdd":{"source":"adjacent-sentinel"}}}',
                                        encoding="utf-8")
                    adjacent_before = adjacent.read_bytes()
                result = self.run_component(
                    "skills", "--copy", "--replace", "--adopt-skill-lock", "--target", str(target),
                    env={**os.environ, "HOME": str(fixture_home),
                         "CODEX_HOME": str(fixture_home / ".codex"), "XDG_STATE_HOME": ""},
                )

                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                expected = {**original, "skills": {"ask-matt": original["skills"]["ask-matt"]}}
                self.assertEqual(json.loads(lock.read_text(encoding="utf-8")), expected)
                self.assertEqual(len(list((target.parent / ".ai-workflow-backups").glob(
                    ".skill-lock.json.*.bak"))), 1)
                if adjacent != lock:
                    self.assertEqual(adjacent.read_bytes(), adjacent_before)

    def test_standard_target_skill_lock_adoption_honors_xdg_state_home(self) -> None:
        fixture_home = self.root / "xdg-home"
        target = fixture_home / ".cursor" / "skills"
        lock = self.root / "state" / "skills" / ".skill-lock.json"
        lock.parent.mkdir(parents=True)
        lock.write_text('{"skills":{"tdd":{"source":"upstream"}}}', encoding="utf-8")
        fallback = fixture_home / ".agents" / ".skill-lock.json"
        fallback.parent.mkdir(parents=True)
        fallback.write_text('{"skills":{"tdd":{"source":"fallback-sentinel"}}}',
                            encoding="utf-8")
        fallback_before = fallback.read_bytes()
        result = self.run_component(
            "skills", "--copy", "--replace", "--adopt-skill-lock", "--target", str(target),
            env={**os.environ, "HOME": str(fixture_home),
                 "CODEX_HOME": str(fixture_home / ".codex"),
                 "XDG_STATE_HOME": str(self.root / "state")},
        )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(json.loads(lock.read_text(encoding="utf-8")), {"skills": {}})
        self.assertEqual(fallback.read_bytes(), fallback_before)

    def test_standard_cursor_skill_lock_preview_uses_global_lock_without_writes(self) -> None:
        fixture_home = self.root / "preview-home"
        target = fixture_home / ".cursor" / "skills"
        lock = fixture_home / ".agents" / ".skill-lock.json"
        lock.parent.mkdir(parents=True)
        original = '{"skills":{"tdd":{"source":"upstream"}}}\n'
        lock.write_text(original, encoding="utf-8")
        result = self.run_component(
            "skills", "--dry-run", "--adopt-skill-lock", "--target", str(target),
            env={**os.environ, "HOME": str(fixture_home),
                 "CODEX_HOME": str(fixture_home / ".codex"), "XDG_STATE_HOME": ""},
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(lock), result.stdout)
        self.assertEqual(lock.read_text(encoding="utf-8"), original)
        self.assertFalse(target.parent.exists())

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

    def test_graphify_component_installs_global_agents_skill(self) -> None:
        home = self.root / "home"
        fake_bin = self.root / "fake-bin"
        fake_bin.mkdir()
        args_file = self.root / "graphify-args.txt"
        fake_graphify = fake_bin / "graphify"
        fake_graphify.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "printf '%s\\n' \"$*\" > \"$GRAPHIFY_ARGS_FILE\"\n"
            "[[ \"$1\" == install && \"$2\" == --platform && \"$3\" == agents ]]\n"
            "mkdir -p \"$HOME/.agents/skills/graphify\"\n"
            "printf '%s\\n' '---' 'name: graphify' '---' > \"$HOME/.agents/skills/graphify/SKILL.md\"\n",
            encoding="utf-8",
        )
        fake_graphify.chmod(0o755)

        dry_run = subprocess.run(
            ["bash", str(ROOT / "scripts" / "install.sh"), "graphify", "--dry-run"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home), "PATH": f"{fake_bin}:{os.environ['PATH']}"},
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
        self.assertIn("DRY-RUN: Graphify global Skill", dry_run.stdout)
        self.assertFalse(home.exists())

        apply = subprocess.run(
            ["bash", str(ROOT / "scripts" / "install.sh"), "graphify", "--apply"],
            cwd=ROOT,
            env={
                **os.environ,
                "HOME": str(home),
                "PATH": f"{fake_bin}:{os.environ['PATH']}",
                "GRAPHIFY_ARGS_FILE": str(args_file),
            },
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(apply.returncode, 0, apply.stderr + apply.stdout)
        self.assertEqual(args_file.read_text(encoding="utf-8"), "install --platform agents\n")
        self.assertTrue((home / ".agents" / "skills" / "graphify" / "SKILL.md").is_file())
        self.assertIn('run_component graphify "${graphify_args[@]}"', (ROOT / "scripts" / "install.sh").read_text(encoding="utf-8"))

    def test_graphify_component_requires_replace_and_backs_up_existing_skill(self) -> None:
        home = self.root / "home"
        target = home / ".agents" / "skills" / "graphify"
        sentinel = target / "sentinel"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_text("keep\n", encoding="utf-8")
        fake_bin = self.root / "fake-bin"
        fake_bin.mkdir()
        fake_graphify = fake_bin / "graphify"
        fake_graphify.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "mkdir -p \"$HOME/.agents/skills/graphify\"\n"
            "printf '%s\\n' '---' 'name: graphify' '---' > \"$HOME/.agents/skills/graphify/SKILL.md\"\n",
            encoding="utf-8",
        )
        fake_graphify.chmod(0o755)
        env = {**os.environ, "HOME": str(home), "PATH": f"{fake_bin}:{os.environ['PATH']}"}

        conflict = subprocess.run(
            ["bash", str(ROOT / "scripts" / "install.sh"), "graphify", "--apply"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(conflict.returncode, 0)
        self.assertIn("CONFLICT", conflict.stderr)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")

        backup_dir = self.root / "backup"
        replace = subprocess.run(
            [
                "bash",
                str(ROOT / "scripts" / "install.sh"),
                "graphify",
                "--apply",
                "--replace",
                "--backup-dir",
                str(backup_dir),
            ],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(replace.returncode, 0, replace.stderr + replace.stdout)
        backups = list(backup_dir.glob("graphify.*.bak/sentinel"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "keep\n")
        self.assertTrue((target / "SKILL.md").is_file())

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
