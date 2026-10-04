"""Minimal entry tests for scripts/install.ps1 and install.cmd."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class InstallEntryPsSourceContractTests(unittest.TestCase):
    def test_install_ps1_mentions_claude_multi_select_without_pwsh(self) -> None:
        # Why: bash/PS drift rule — Claude menu and dispatch must exist even when
        # this machine cannot execute pwsh smoke tests.
        text = (ROOT / "scripts" / "install.ps1").read_text(encoding="utf-8")
        self.assertIn("'claude-merge' = 'install-claude-merge.ps1'", text)
        self.assertIn("Install-ProfileClaude", text)
        self.assertIn("Parse-AgentSelection", text)
        self.assertIn("Select agents (e.g. 1, 1 3, 1,2,3)", text)
        self.assertIn("-DocumentName 'CLAUDE.md'", text)
        self.assertIn("'--document-name', $DocumentName", text)
        self.assertIn("--no-hooks-feature", text)
        # Why: bash wizard leaves mem0 to merge_host_mcp interactive prompts;
        # a PS-only pre-merge URL question would violate dual-impl drift rule.
        self.assertNotIn("Provide mem0 MCP URL now?", text)
        self.assertNotIn("3) Codex + Cursor", text)

    def test_claude_merge_ps1_exists_with_backup_root_contract(self) -> None:
        text = (ROOT / "scripts" / "install-claude-merge.ps1").read_text(encoding="utf-8")
        self.assertIn("--host', 'claude'", text.replace('"', "'"))
        self.assertIn(".claude/.ai-workflow-backups", text)
        self.assertIn("SKIP: Claude merge has no project-scoped steps", text)

    def test_new_host_ports_dispatch_and_propagate_component_exit(self) -> None:
        text = (ROOT / "scripts/install.ps1").read_text()
        for host, label, document in (
            ("minimax", "MiniMax Code", "AGENTS.md"),
            ("workbuddy", "WorkBuddy", "CODEBUDDY.md"),
        ):
            with self.subTest(host=host):
                self.assertIn(f"'{host}-merge' = 'install-{host}-merge.ps1'", text)
                self.assertIn(f"-HostLabel '{label}'", text)
                self.assertIn(f"-DocumentName '{document}'", text)
                wrapper = (ROOT / "scripts" / f"install-{host}-merge.ps1").read_text()
                self.assertIn(f'install-json-mcp.ps1" {host} @args', wrapper)
                self.assertIn('exit $LASTEXITCODE', wrapper)


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

    def test_component_usage_error_exits_2(self) -> None:
        result = self.run_install_ps("skills", "--unknown")
        self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
        self.assertIn("unrecognized option", result.stderr)
        self.assertFalse(self.skills_target.exists())

    def test_agents_dry_run_uses_agents_template_directory(self) -> None:
        result = self.run_install_ps("agents", "--dry-run", "--agents-home", str(self.root / "codex"))
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn(str(ROOT / "agents" / "AGENTS.global.md"), result.stdout)
        self.assertFalse((self.root / "codex").exists())

    def test_dependency_preview_via_dispatch(self) -> None:
        result = self.run_install_ps("deps", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("DEPENDENCIES:", result.stdout)

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

    def test_claude_merge_dispatched_and_menu_mentions_claude(self) -> None:
        # Why: PS entry must advertise claude-merge and multi-select Claude menu
        # so Windows peers cannot drift from bash installer contracts.
        text = (ROOT / "scripts" / "install.ps1").read_text(encoding="utf-8")
        self.assertIn("claude-merge", text)
        self.assertIn("Install-ProfileClaude", text)
        self.assertIn("Parse-AgentSelection", text)
        self.assertIn("Select agents (e.g. 1, 1 3, 1,2,3)", text)

        result = self.run_install_ps("claude-merge", "--help")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        combined = result.stderr + result.stdout
        self.assertIn("install-claude-merge.ps1", combined)
        self.assertIn("user-level MCP only", combined)

    @unittest.skipUnless(os.name == "nt", "install.cmd is Windows-only")
    def test_install_cmd_propagates_component_error(self) -> None:
        result = subprocess.run(
            ["cmd", "/c", str(ROOT / "scripts" / "install.cmd"), "skills", "--unknown"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
        self.assertIn("unrecognized option", result.stderr)

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
