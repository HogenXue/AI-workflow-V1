"""Focused smoke tests for PowerShell host-merge installers."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX_MERGE_PS1 = ROOT / "scripts" / "install-codex-merge.ps1"
CURSOR_MERGE_PS1 = ROOT / "scripts" / "install-cursor-merge.ps1"


def _find_pwsh() -> str | None:
    return shutil.which("pwsh")


def _can_create_symlink() -> bool:
    """Return True when this process can create a file symlink (Windows needs privilege)."""
    probe_root = Path(tempfile.mkdtemp(prefix="aiw-symlink-probe-"))
    try:
        link = probe_root / "link"
        target = probe_root / "missing-target"
        try:
            link.symlink_to(target)
        except OSError:
            return False
        return link.is_symlink()
    finally:
        shutil.rmtree(probe_root, ignore_errors=True)


def _run_ps(
    script: Path,
    *args: str,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    pwsh = _find_pwsh()
    assert pwsh is not None
    return subprocess.run(
        [pwsh, "-NoProfile", "-File", str(script), *args],
        cwd=str(cwd or ROOT),
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def _forwards_interactive_to_merge_host_mcp(script: Path) -> bool:
    """True when the PS merge script mirrors bash: TTY + --interactive → merge_host_mcp.py."""
    text = script.read_text(encoding="utf-8")
    needle = (
        "if (($interactive -eq 1) -and (Test-InstallLibStdinTty)) {\n"
        "    $mcpArgs += '--interactive'\n"
        "}"
    )
    return needle in text


class InstallMergePsInteractiveWiringTests(unittest.TestCase):
    def test_merge_scripts_forward_interactive_to_merge_host_mcp(self) -> None:
        # Why: per-server URL prompts live in merge_host_mcp.py; without this
        # hand-off, Windows TTY installs silently skip keep/replace prompts.
        # Source assertion (no pwsh required) guards the bash/PS drift contract.
        self.assertTrue(
            _forwards_interactive_to_merge_host_mcp(CODEX_MERGE_PS1),
            "install-codex-merge.ps1 must pass --interactive to merge_host_mcp.py on TTY",
        )
        self.assertTrue(
            _forwards_interactive_to_merge_host_mcp(CURSOR_MERGE_PS1),
            "install-cursor-merge.ps1 must pass --interactive to merge_host_mcp.py on TTY",
        )


@unittest.skipUnless(_find_pwsh(), "pwsh (PowerShell 7+) is required")
class InstallMergePsSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.project = self.root / "project"
        self.project.mkdir()
        (self.project / "AGENTS.md").write_text("project-owned\n", encoding="utf-8")

    def env(self) -> dict[str, str]:
        return {
            **os.environ,
            "HOME": str(self.home),
            "CODEX_HOME": str(self.home / ".codex"),
        }

    def test_codex_merge_skip_project_dry_run(self) -> None:
        codex_home = self.home / ".codex"
        codex_home.mkdir(parents=True)
        (codex_home / "config.toml").write_text("[features]\nmemories = true\n", encoding="utf-8")

        result = _run_ps(
            CODEX_MERGE_PS1,
            "--dry-run",
            "--mcp-overwrite",
            "--skip-project",
            "--codex-home",
            str(codex_home),
            "--backup-dir",
            str(self.root / "backup"),
            env=self.env(),
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("DRY-RUN", result.stdout)
        self.assertIn("ignoring --skip-project", result.stdout)
        self.assertFalse((codex_home / "hooks.json").exists())
        self.assertEqual(
            (codex_home / "config.toml").read_text(encoding="utf-8"),
            "[features]\nmemories = true\n",
        )

    def test_codex_merge_apply_user_hooks_ignores_project_root(self) -> None:
        codex_home = self.home / ".codex"
        codex_home.mkdir(parents=True)
        (codex_home / "config.toml").write_text("[features]\nmemories = true\n", encoding="utf-8")

        result = _run_ps(
            CODEX_MERGE_PS1,
            "--mcp-overwrite",
            "--mem0-url",
            "https://example.test/mem0",
            "--project-root",
            str(self.project),
            "--codex-home",
            str(codex_home),
            "--backup-dir",
            str(self.root / "backup"),
            env=self.env(),
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("ignoring --project-root", result.stdout)
        self.assertTrue((codex_home / "hooks.json").is_file())
        self.assertTrue((codex_home / "hooks" / "session-start.sh").is_file())
        self.assertFalse((self.project / ".codex").exists())
        self.assertEqual((self.project / "AGENTS.md").read_text(encoding="utf-8"), "project-owned\n")
        text = (codex_home / "config.toml").read_text(encoding="utf-8")
        self.assertIn("[mcp_servers.recallium]", text)
        self.assertIn("[mcp_servers.mem0]", text)

    def test_cursor_merge_skip_project_leaves_project_untouched(self) -> None:
        mcp_file = self.home / ".cursor" / "mcp.json"
        mcp_file.parent.mkdir(parents=True)
        mcp_file.write_text('{"mcpServers":{}}\n', encoding="utf-8")

        result = _run_ps(
            CURSOR_MERGE_PS1,
            "--mcp-overwrite",
            "--mem0-url",
            "https://example.test/mem0",
            "--mcp-file",
            str(mcp_file),
            "--skip-project",
            "--backup-dir",
            str(self.root / "backup"),
            env=self.env(),
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("SKIP: skipping project-scoped steps (--skip-project)", result.stdout)
        self.assertFalse((self.project / ".cursor").exists())
        data = json.loads(mcp_file.read_text(encoding="utf-8"))
        self.assertIn("gitnexus", data["mcpServers"])
        self.assertIn("mem0", data["mcpServers"])

    def test_cursor_merge_project_root_generates_rules_leaves_agents_md(self) -> None:
        mcp_file = self.home / ".cursor" / "mcp.json"
        mcp_file.parent.mkdir(parents=True)
        mcp_file.write_text('{"mcpServers":{}}\n', encoding="utf-8")

        result = _run_ps(
            CURSOR_MERGE_PS1,
            "--mcp-keep",
            "--mem0-url",
            "https://example.test/mem0",
            "--mcp-file",
            str(mcp_file),
            "--project-root",
            str(self.project),
            "--backup-dir",
            str(self.root / "backup"),
            env=self.env(),
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        rules = self.project / ".cursor" / "rules" / "ai-workflow-global.mdc"
        self.assertTrue(rules.is_file())
        rules_text = rules.read_text(encoding="utf-8")
        agents_body = (ROOT / "AGENTS.global.md").read_text(encoding="utf-8")
        self.assertTrue(rules_text.startswith("---\n"))
        self.assertIn("alwaysApply: true", rules_text)
        _, _, body = rules_text.split("---", 2)
        self.assertEqual(body.lstrip("\n").rstrip("\n"), agents_body.rstrip("\n"))
        self.assertTrue((self.project / ".cursor" / "hooks.json").is_file())
        self.assertEqual((self.project / "AGENTS.md").read_text(encoding="utf-8"), "project-owned\n")
        self.assertFalse((self.home / ".codex").exists())

    def test_cursor_merge_rejects_packaged_mcp_fragment(self) -> None:
        fragment = ROOT / "trellis" / "cursor" / "mcp" / "servers.json"
        before = fragment.read_text(encoding="utf-8")

        result = _run_ps(
            CURSOR_MERGE_PS1,
            "--dry-run",
            "--mcp-file",
            str(fragment),
            "--skip-project",
            env=self.env(),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("package MCP fragment", result.stderr)
        self.assertEqual(fragment.read_text(encoding="utf-8"), before)

    def test_codex_merge_conflict_restores_mcp(self) -> None:
        codex_home = self.home / ".codex"
        codex_home.mkdir(parents=True)
        config = codex_home / "config.toml"
        original = '[mcp_servers.other]\ncommand = "keep"\n'
        config.write_text(original, encoding="utf-8")
        (codex_home / "hooks.json").write_text("existing\n", encoding="utf-8")

        result = _run_ps(
            CODEX_MERGE_PS1,
            "--mcp-overwrite",
            "--codex-home",
            str(codex_home),
            "--backup-dir",
            str(self.root / "backup"),
            env=self.env(),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CONFLICT", result.stderr)
        self.assertEqual(config.read_text(encoding="utf-8"), original)
        self.assertEqual((codex_home / "hooks.json").read_text(encoding="utf-8"), "existing\n")

    def test_codex_merge_rejects_remote_http_before_mutating_target(self) -> None:
        codex_home = self.home / ".codex"
        codex_home.mkdir(parents=True)
        config = codex_home / "config.toml"
        original = "[features]\nmemories = true\n"
        config.write_text(original, encoding="utf-8")

        result = _run_ps(
            CODEX_MERGE_PS1,
            "--mcp-overwrite",
            "--mem0-url",
            "http://memory.example.test/mcp",
            "--skip-project",
            "--codex-home",
            str(codex_home),
            "--backup-dir",
            str(self.root / "backup"),
            env=self.env(),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("insecure remote HTTP", result.stderr)
        self.assertEqual(config.read_text(encoding="utf-8"), original)

    def test_cursor_merge_rejects_remote_http_before_mutating_target(self) -> None:
        mcp_file = self.home / ".cursor" / "mcp.json"
        mcp_file.parent.mkdir(parents=True)
        original = '{"mcpServers":{"existing":{"command":"keep"}}}\n'
        mcp_file.write_text(original, encoding="utf-8")

        result = _run_ps(
            CURSOR_MERGE_PS1,
            "--mcp-overwrite",
            "--mem0-url",
            "http://memory.example.test/mcp",
            "--mcp-file",
            str(mcp_file),
            "--skip-project",
            "--backup-dir",
            str(self.root / "backup"),
            env=self.env(),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("insecure remote HTTP", result.stderr)
        self.assertEqual(mcp_file.read_text(encoding="utf-8"), original)

    @unittest.skipUnless(
        _can_create_symlink(),
        "dangling-symlink backup requires SeCreateSymbolicLinkPrivilege / Developer Mode",
    )
    def test_codex_merge_backs_up_dangling_config_symlink(self) -> None:
        codex_home = self.home / ".codex"
        codex_home.mkdir(parents=True)
        config = codex_home / "config.toml"
        missing_target = self.root / "missing-config.toml"
        config.symlink_to(missing_target)
        backup_dir = self.root / "backup"

        result = _run_ps(
            CODEX_MERGE_PS1,
            "--mcp-overwrite",
            "--skip-project",
            "--codex-home",
            str(codex_home),
            "--backup-dir",
            str(backup_dir),
            env=self.env(),
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue(config.is_file())
        self.assertFalse(config.is_symlink())
        backups = list(backup_dir.glob("config.toml.*.bak"))
        self.assertEqual(len(backups), 1)
        self.assertTrue(backups[0].is_symlink())
        self.assertEqual(os.readlink(backups[0]), str(missing_target))

    @unittest.skipUnless(
        _can_create_symlink(),
        "dangling-symlink backup requires SeCreateSymbolicLinkPrivilege / Developer Mode",
    )
    def test_cursor_merge_backs_up_dangling_mcp_symlink(self) -> None:
        cursor_home = self.home / ".cursor"
        cursor_home.mkdir(parents=True)
        mcp_file = cursor_home / "mcp.json"
        missing_target = self.root / "missing-mcp.json"
        mcp_file.symlink_to(missing_target)
        backup_dir = self.root / "backup"

        result = _run_ps(
            CURSOR_MERGE_PS1,
            "--mcp-overwrite",
            "--mcp-file",
            str(mcp_file),
            "--skip-project",
            "--backup-dir",
            str(backup_dir),
            env=self.env(),
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue(mcp_file.is_file())
        self.assertFalse(mcp_file.is_symlink())
        backups = list(backup_dir.glob("mcp.json.*.bak"))
        self.assertEqual(len(backups), 1)
        self.assertTrue(backups[0].is_symlink())
        self.assertEqual(os.readlink(backups[0]), str(missing_target))


if __name__ == "__main__":
    unittest.main()
