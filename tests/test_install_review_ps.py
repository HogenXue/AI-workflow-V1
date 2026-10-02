"""Regressions for final-review source safety and Graphify failure recovery."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PWSH = shutil.which("pwsh")


def find_bash():
    if os.name == "nt" and shutil.which("git"):
        candidate = Path(shutil.which("git")).parent.parent / "bin/bash.exe"
        if candidate.is_file():
            return str(candidate)
    return shutil.which("bash")


BASH = find_bash()


def run(argv, env=None):
    result = subprocess.run(argv, capture_output=True, timeout=30, env=env, check=False)
    return subprocess.CompletedProcess(argv, result.returncode,
                                       result.stdout.decode("utf-8", errors="replace"),
                                       result.stderr.decode("utf-8", errors="replace"))


@unittest.skipUnless(PWSH, "PowerShell 7+ required")
class SourceAliasSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / "package"
        scripts = self.package / "scripts"
        scripts.mkdir(parents=True)
        for name in ("install-config.ps1", "install-lib.ps1"):
            shutil.copyfile(ROOT / "scripts" / name, scripts / name)
        self.source = self.package / "config"
        self.source.mkdir()
        self.marker = self.source / "must-preserve.txt"
        self.marker.write_text("original source", encoding="utf-8")

    def create_alias(self, name="alias", *, junction=False, relative=False):
        alias = self.root / name
        if junction:
            result = run([PWSH, "-NoProfile", "-Command",
                          f"New-Item -ItemType Junction -Path '{alias}' -Target '{self.package}' | Out-Null"])
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            try:
                alias.symlink_to("package" if relative else self.package, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"Directory symlink unavailable: {exc}")
        return alias

    def assert_refused(self, target, *, preview=False):
        self.assertTrue(target.resolve().is_relative_to(self.root.resolve()))
        argv = [PWSH, "-NoProfile", "-File", str(self.package / "scripts/install-config.ps1"),
                "--copy", "--replace", "--target", str(target), "--backup-dir", str(self.root / "backups")]
        if preview:
            argv.append("--dry-run")
        result = run(argv)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("overlaps package source", result.stderr)
        self.assertEqual(self.marker.read_text(encoding="utf-8"), "original source")
        self.assertFalse((self.root / "backups").exists())

    def test_parent_symbolic_link_cannot_alias_source_for_replacement(self):
        self.assert_refused(self.create_alias() / "config")

    def test_relative_parent_link_cannot_alias_source(self):
        self.assert_refused(self.create_alias(relative=True) / "config")

    @unittest.skipUnless(os.name == "nt", "Windows junction")
    def test_parent_junction_cannot_alias_source_for_replacement(self):
        self.assert_refused(self.create_alias(junction=True) / "config")

    def test_nonexistent_suffix_under_source_alias_is_refused(self):
        self.assert_refused(self.create_alias() / "config/new/subdir", preview=True)

    def test_unrelated_parent_junction_still_allows_copy(self):
        destination = self.root / "destination"
        destination.mkdir()
        alias = self.root / "destination-alias"
        if os.name == "nt":
            create = run([PWSH, "-NoProfile", "-Command",
                          f"New-Item -ItemType Junction -Path '{alias}' -Target '{destination}' | Out-Null"])
            self.assertEqual(create.returncode, 0, create.stderr)
        else:
            alias.symlink_to(destination, target_is_directory=True)
        result = run([PWSH, "-NoProfile", "-File", str(self.package / "scripts/install-config.ps1"),
                      "--copy", "--target", str(alias / "installed")])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((destination / "installed/must-preserve.txt").read_text(encoding="utf-8"), "original source")
        self.assertEqual(self.marker.read_text(encoding="utf-8"), "original source")

    def test_script_invoked_through_alias_cannot_overwrite_physical_source(self):
        alias = self.create_alias()
        result = run([PWSH, "-NoProfile", "-File", str(alias / "scripts/install-config.ps1"),
                      "--copy", "--replace", "--target", str(self.source), "--backup-dir", str(self.root / "backups")])
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("overlaps package source", result.stderr)
        self.assertEqual(self.marker.read_text(encoding="utf-8"), "original source")
        self.assertFalse((self.root / "backups").exists())

    def test_backup_inside_aliased_target_is_refused_before_mutation(self):
        alias = self.create_alias()
        lib = self.package / "scripts/install-lib.ps1"
        result = run([PWSH, "-NoProfile", "-Command",
                      f". '{lib}'; if (Install-LibBackupFile -Source '{self.source}' "
                      f"-BackupDir '{alias / 'config/backups'}') {{ exit 0 }}; exit 1"])
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.marker.read_text(encoding="utf-8"), "original source")
        self.assertFalse((self.source / "backups").exists())

    def test_link_cycle_is_refused_by_overlap_check(self):
        for name, destination in (("a", "b"), ("b", "a")):
            try:
                (self.root / name).symlink_to(self.root / destination, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"Directory symlink unavailable: {exc}")
        lib = self.package / "scripts/install-lib.ps1"
        result = run([PWSH, "-NoProfile", "-Command",
                      f". '{lib}'; if (Install-LibPathsOverlap -Source '{self.source}' "
                      f"-Target '{self.root / 'a/config'}') {{ exit 0 }}; exit 1"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(os.name == "nt", "Windows device namespace")
    def test_unresolved_device_namespace_is_refused(self):
        lib = self.package / "scripts/install-lib.ps1"
        target = r"\\?\Volume{00000000-0000-0000-0000-000000000000}\config"
        result = run([PWSH, "-NoProfile", "-Command",
                      f". '{lib}'; if (Install-LibPathsOverlap -Source '{self.source}' "
                      f"-Target '{target}') {{ exit 0 }}; exit 1"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class GraphifyRecoveryHarness:
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        self.target = self.home / ".agents/skills/graphify"
        self.env = {**os.environ, "HOME": str(self.home),
                    "PATH": str(bin_dir) + os.pathsep + (str(Path(BASH).parent) + os.pathsep if BASH else "") + os.environ["PATH"]}
        if self.ext == "ps1":
            body = ('@echo off\nmkdir "%HOME%\\.agents\\skills\\graphify" 2>nul\n'
                    'echo partial>"%HOME%\\.agents\\skills\\graphify\\partial.tmp"\n'
                    'if "%GRAPHIFY_TEST_MODE%"=="success" (\n'
                    'echo completed>"%HOME%\\.agents\\skills\\graphify\\SKILL.md"\nexit /b 0\n)\n'
                    'if "%GRAPHIFY_TEST_MODE%"=="fail" exit /b 23\nexit /b 0\n')
            (bin_dir / "graphify.cmd").write_text(body, encoding="utf-8", newline="\r\n")
        else:
            body = ('#!/usr/bin/env bash\nmkdir -p "$HOME/.agents/skills/graphify"\n'
                    'printf partial > "$HOME/.agents/skills/graphify/partial.tmp"\n'
                    'if [[ "$GRAPHIFY_TEST_MODE" == success ]]; then\n'
                    'printf completed > "$HOME/.agents/skills/graphify/SKILL.md"\nexit 0\nfi\n'
                    '[[ "$GRAPHIFY_TEST_MODE" != fail ]] || exit 23\nexit 0\n')
            command = bin_dir / "graphify"
            command.write_text(body, encoding="utf-8", newline="\n")
            command.chmod(0o755)

    def invoke(self, mode, replace=False):
        executable = [PWSH, "-NoProfile", "-File"] if self.ext == "ps1" else [BASH]
        argv = executable + [str(ROOT / "scripts" / ("install-graphify." + self.ext)), "--apply"]
        if replace:
            argv.append("--replace")
        return run(argv, {**self.env, "GRAPHIFY_TEST_MODE": mode})

    def test_fresh_failure_clears_target_and_allows_retry(self):
        for mode in ("fail", "missing"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as alternate:
                self.home = Path(alternate)
                self.env["HOME"] = str(self.home)
                self.target = self.home / ".agents/skills/graphify"
                result = self.invoke(mode)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.target.exists(), result.stdout + result.stderr)
                retry = self.invoke("success")
                self.assertEqual(retry.returncode, 0, retry.stdout + retry.stderr)
                self.assertTrue((self.target / "SKILL.md").is_file())

    def test_replacement_failure_restores_original(self):
        for mode in ("fail", "missing"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as alternate:
                self.home = Path(alternate)
                self.env["HOME"] = str(self.home)
                self.target = self.home / ".agents/skills/graphify"
                self.target.mkdir(parents=True)
                (self.target / "SKILL.md").write_text("original", encoding="utf-8")
                result = self.invoke(mode, replace=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((self.target / "SKILL.md").read_text(encoding="utf-8"), "original")
                self.assertFalse((self.target / "partial.tmp").exists())


@unittest.skipUnless(PWSH and os.name == "nt", "PowerShell Windows CMD fixture")
class GraphifyPsRecoveryTests(GraphifyRecoveryHarness, unittest.TestCase):
    ext = "ps1"


@unittest.skipUnless(BASH, "Bash required")
class GraphifyBashRecoveryTests(GraphifyRecoveryHarness, unittest.TestCase):
    ext = "sh"


if __name__ == "__main__":
    unittest.main()
