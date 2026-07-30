"""Focused tests for scripts/install-lib.ps1 (PowerShell port of install-lib.sh)."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALL_LIB_PS1 = ROOT / "scripts" / "install-lib.ps1"


def _find_pwsh() -> str | None:
    return shutil.which("pwsh")


def _run_pwsh(
    script: str,
    *,
    cwd: Path | None = None,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    pwsh = _find_pwsh()
    assert pwsh is not None
    return subprocess.run(
        [pwsh, "-NoProfile", "-Command", script],
        cwd=cwd or ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )


@unittest.skipUnless(_find_pwsh(), "pwsh (PowerShell 7+) is required")
class InstallLibPsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)

    def test_backup_emits_backup_line_and_preserves_content(self) -> None:
        source = self.root / "source.txt"
        source.write_text("original\n", encoding="utf-8")
        backup_dir = self.root / "backups"
        lib = str(INSTALL_LIB_PS1).replace("'", "''")
        src = str(source).replace("'", "''")
        bdir = str(backup_dir).replace("'", "''")
        script = (
            f". '{lib}'; "
            f"if (-not (Install-LibBackupFile -Source '{src}' -BackupDir '{bdir}' "
            f"-Name 'source.txt')) {{ exit 1 }}; "
            f"if (-not $script:InstallBackupPath) {{ exit 2 }}"
        )
        result = _run_pwsh(script)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("BACKUP: ", result.stdout)
        backups = list(backup_dir.glob("source.txt.*.bak"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "original\n")

    def test_parallel_backups_never_overwrite_each_other(self) -> None:
        source = self.root / "source.txt"
        source.write_text("original\n", encoding="utf-8")
        backup_dir = self.root / "parallel-backups"
        lib = str(INSTALL_LIB_PS1).replace("'", "''")
        src = str(source).replace("'", "''")
        bdir = str(backup_dir).replace("'", "''")
        # Slow copy widens the same-second collision window (bash tests fake `cp`).
        script = (
            f". '{lib}'; "
            "function Install-LibInternalCopy { "
            "  param([string]$Source,[string]$Destination,[switch]$Recurse) "
            "  Start-Sleep -Milliseconds 150; "
            "  if ($Recurse) { "
            "    Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force -ErrorAction Stop "
            "  } else { "
            "    Copy-Item -LiteralPath $Source -Destination $Destination -Force -ErrorAction Stop "
            "  } "
            "}; "
            f"if (-not (Install-LibBackupFile -Source '{src}' -BackupDir '{bdir}' "
            f"-Name 'source.txt')) {{ exit 1 }}"
        )

        processes = [
            subprocess.Popen(
                [_find_pwsh(), "-NoProfile", "-Command", script],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            for _ in range(2)
        ]
        results = [process.communicate() + (process.returncode,) for process in processes]

        for stdout, stderr, returncode in results:
            self.assertEqual(returncode, 0, stderr + stdout)
            self.assertIn("BACKUP: ", stdout)
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

        if os.name == "nt":
            deny = subprocess.run(
                [
                    "icacls",
                    str(backup_dir),
                    "/deny",
                    f"{os.environ.get('USERNAME', 'Everyone')}:(OI)(CI)(W,D,DC,WD,AD)",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(deny.returncode, 0, deny.stdout + deny.stderr)
        else:
            backup_dir.chmod(0o555)

        lib = str(INSTALL_LIB_PS1).replace("'", "''")
        src = str(source).replace("'", "''")
        bdir = str(backup_dir).replace("'", "''")
        script = (
            f". '{lib}'; "
            f"if (-not (Install-LibBackupFile -Source '{src}' -BackupDir '{bdir}' "
            f"-Name 'source.txt')) {{ exit 1 }}; exit 0"
        )
        try:
            result = _run_pwsh(script, timeout=5)
        finally:
            if os.name == "nt":
                subprocess.run(
                    ["icacls", str(backup_dir), "/reset", "/T", "/C"],
                    text=True,
                    capture_output=True,
                    check=False,
                )
            else:
                backup_dir.chmod(0o755)

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(
            ("could not reserve backup path" in result.stderr)
            or ("could not create backup directory" in result.stderr),
            result.stderr + result.stdout,
        )
        self.assertEqual(source.read_text(encoding="utf-8"), "original\n")
        # Directory may exist but must not contain published backups/locks.
        self.assertFalse(list(backup_dir.glob("*.bak")))
        self.assertFalse(list(backup_dir.glob("*.lock")))

    def test_failed_backup_copy_never_publishes_partial_bak(self) -> None:
        source = self.root / "source.txt"
        source.write_text("original\n", encoding="utf-8")
        backup_dir = self.root / "failed-backups"
        lib = str(INSTALL_LIB_PS1).replace("'", "''")
        src = str(source).replace("'", "''")
        bdir = str(backup_dir).replace("'", "''")
        script = (
            f". '{lib}'; "
            "function Install-LibInternalCopy { "
            "  param([string]$Source,[string]$Destination,[switch]$Recurse) "
            "  Set-Content -LiteralPath $Destination -Value \"partial`n\"; "
            "  throw 'forced copy failure' "
            "}; "
            f"if (-not (Install-LibBackupFile -Source '{src}' -BackupDir '{bdir}' "
            f"-Name 'source.txt')) {{ exit 1 }}; exit 0"
        )
        result = _run_pwsh(script)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("could not back up existing target", result.stderr)
        self.assertFalse(list(backup_dir.glob("*.bak")))
        self.assertFalse(list(backup_dir.glob("*.lock")))
        self.assertEqual(source.read_text(encoding="utf-8"), "original\n")

    def test_nested_backup_directory_inside_target_is_rejected(self) -> None:
        target = self.root / "target-dir"
        target.mkdir()
        (target / "sentinel.txt").write_text("keep\n", encoding="utf-8")
        nested_backup = target / ".backups"
        lib = str(INSTALL_LIB_PS1).replace("'", "''")
        src = str(target).replace("'", "''")
        bdir = str(nested_backup).replace("'", "''")
        script = (
            f". '{lib}'; "
            f"if (-not (Install-LibBackupFile -Source '{src}' -BackupDir '{bdir}')) {{ exit 1 }}; "
            "exit 0"
        )
        result = _run_pwsh(script)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must not be inside the target being backed up", result.stderr)
        self.assertFalse(nested_backup.exists())
        self.assertEqual((target / "sentinel.txt").read_text(encoding="utf-8"), "keep\n")

    def test_resolve_project_root_skip_and_explicit_path(self) -> None:
        project = self.root / "proj"
        project.mkdir()
        lib = str(INSTALL_LIB_PS1).replace("'", "''")
        proj = str(project).replace("'", "''")

        skip = _run_pwsh(
            f". '{lib}'; "
            "if (-not (Install-LibResolveProjectRoot -Provided '' -SkipFlag 1 -Interactive 0)) "
            "{ exit 1 }; "
            "if ($script:InstallProjectRoot -ne '') { exit 2 }"
        )
        self.assertEqual(skip.returncode, 0, skip.stderr + skip.stdout)
        self.assertIn("SKIP: skipping project-scoped steps (--skip-project)", skip.stdout)

        explicit = _run_pwsh(
            f". '{lib}'; "
            f"if (-not (Install-LibResolveProjectRoot -Provided '{proj}' -SkipFlag 0 "
            f"-Interactive 0)) {{ exit 1 }}; "
            f"if ($script:InstallProjectRoot -ne (Resolve-Path -LiteralPath '{proj}').ProviderPath) "
            "{ exit 2 }; "
            "Write-Output \"PROJECT-ROOT-SET: $($script:InstallProjectRoot)\""
        )
        self.assertEqual(explicit.returncode, 0, explicit.stderr + explicit.stdout)
        self.assertIn("PROJECT-ROOT-SET:", explicit.stdout)

        noninteractive = _run_pwsh(
            f". '{lib}'; "
            "if (-not (Install-LibResolveProjectRoot -Provided '' -SkipFlag 0 -Interactive 0)) "
            "{ exit 1 }; "
            "if ($script:InstallProjectRoot -ne '') { exit 2 }"
        )
        self.assertEqual(
            noninteractive.returncode, 0, noninteractive.stderr + noninteractive.stdout
        )
        self.assertIn("no --project-root", noninteractive.stdout)
        self.assertNotIn("PROJECT-ROOT:", noninteractive.stdout)


if __name__ == "__main__":
    unittest.main()
