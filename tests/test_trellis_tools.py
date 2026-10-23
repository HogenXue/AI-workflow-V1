import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TrellisInstallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.codex_home = Path(self.temp_dir.name) / "codex-home"
        self.backup_dir = Path(self.temp_dir.name) / "backups"

    def run_install(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "bash",
                str(ROOT / "trellis" / "install.sh"),
                *args,
                "--codex-home",
                str(self.codex_home),
                "--backup-dir",
                str(self.backup_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_dry_run_does_not_write(self) -> None:
        result = self.run_install("--dry-run")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DRY-RUN: would copy", result.stdout)
        self.assertFalse((self.codex_home / "AGENTS.md").exists())
        self.assertFalse((self.codex_home / "config.toml").exists())
        self.assertFalse(self.backup_dir.exists())

    def test_apply_backs_up_agents_and_preserves_native_config(self) -> None:
        self.codex_home.mkdir()
        target = self.codex_home / "AGENTS.md"
        target.write_text("existing instructions\n")
        config = self.codex_home / "config.toml"
        original = '[mcp_servers.example]\napi_key = "sentinel-secret"\n'
        config.write_text(original)
        result = self.run_install("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(target.read_bytes(), (ROOT / "agents/AGENTS.global.md").read_bytes())
        self.assertEqual(config.read_text(), original)
        backups = list(self.backup_dir.glob("AGENTS.md.*.bak"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "existing instructions\n")
        self.assertFalse(list(self.backup_dir.glob("config.toml.*.bak")))

    def test_apply_preserves_explicit_disabled_hooks(self) -> None:
        self.codex_home.mkdir()
        config = self.codex_home / "config.toml"
        original = '[features]\nhooks = false\nexperimental = true\n[mcp_servers.example]\napi_key = "sentinel-secret"\n'
        config.write_text(original)
        result = self.run_install("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(config.read_text(), original)
        self.assertIn("preserved", result.stdout)

    def test_agents_install_does_not_touch_non_regular_config(self) -> None:
        self.codex_home.mkdir()
        config = self.codex_home / "config.toml"
        config.mkdir()
        sentinel = config / "keep.txt"
        sentinel.write_text("unrelated")
        result = self.run_install("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(sentinel.read_text(), "unrelated")
        self.assertEqual((self.codex_home / "AGENTS.md").read_bytes(), (ROOT / "agents/AGENTS.global.md").read_bytes())

    def test_agents_install_preserves_symlinked_config(self) -> None:
        self.codex_home.mkdir()
        linked = Path(self.temp_dir.name) / "linked.toml"
        linked.write_text("sentinel = true\n")
        config = self.codex_home / "config.toml"
        config.symlink_to(linked)
        result = self.run_install("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(config.is_symlink())
        self.assertEqual(linked.read_text(), "sentinel = true\n")

    def test_apply_restores_agents_when_copy_fails(self) -> None:
        self.codex_home.mkdir()
        target = self.codex_home / "AGENTS.md"
        target.write_text("existing instructions\n")
        target.chmod(0o444)
        try:
            result = self.run_install("--apply")
        finally:
            target.chmod(0o644)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_text(), "existing instructions\n")
        self.assertEqual(len(list(self.backup_dir.glob("AGENTS.md.*.bak"))), 1)

    def test_apply_leaves_existing_guide_when_backup_fails(self) -> None:
        self.codex_home.mkdir()
        target = self.codex_home / "AGENTS.md"
        target.write_text("original guide\n")
        self.backup_dir.write_text("not a directory\n")
        result = self.run_install("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_text(), "original guide\n")
        self.assertFalse((self.codex_home / "config.toml").exists())

    def test_agents_home_installs_and_backs_up_agents_file(self) -> None:
        agents_home = Path(self.temp_dir.name) / "other-ai"
        agents_home.mkdir()
        target_agents = agents_home / "AGENTS.md"
        target_agents.write_text("existing instructions\n", encoding="utf-8")

        result = subprocess.run(
            [
                "bash",
                str(ROOT / "trellis" / "install.sh"),
                "--apply",
                "--agents-home",
                str(agents_home),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("AI 工作原则（Trellis 兼容全局模板）", target_agents.read_text(encoding="utf-8"))
        backups = list(
            (agents_home / ".ai-workflow-backups").glob("AGENTS.md.*.bak")
        )
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "existing instructions\n")

    def test_unified_agents_component_preserves_config(self) -> None:
        self.codex_home.mkdir()
        config = self.codex_home / "config.toml"
        config.write_text("sentinel = true\n")
        result = subprocess.run(["bash", str(ROOT / "scripts/install.sh"), "agents", "--apply", "--agents-home", str(self.codex_home)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(config.read_text(), "sentinel = true\n")
        self.assertEqual((self.codex_home / "AGENTS.md").read_bytes(), (ROOT / "agents/AGENTS.global.md").read_bytes())

    def test_repeated_apply_keeps_unique_timestamped_backups(self) -> None:
        self.codex_home.mkdir()
        target_agents = self.codex_home / "AGENTS.md"
        target_agents.write_text("first version\n", encoding="utf-8")

        first = self.run_install("--apply")
        self.assertEqual(first.returncode, 0, first.stderr)

        target_agents.write_text("second version\n", encoding="utf-8")
        second = self.run_install("--apply")
        self.assertEqual(second.returncode, 0, second.stderr)

        backups = list(self.backup_dir.glob("AGENTS.md.*.bak"))
        self.assertEqual(len(backups), 2)
        self.assertEqual(
            {path.read_text(encoding="utf-8") for path in backups},
            {"first version\n", "second version\n"},
        )


class TrellisConfigCheckTests(unittest.TestCase):
    def test_check_lists_only_mcp_names(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            codex_home = Path(temporary_directory) / "codex-home"
            codex_home.mkdir()
            (codex_home / "config.toml").write_text(
                '[mcp_servers.example]\napi_key = "sentinel-secret"\n'
                '[mcp_servers.example.env]\nTOKEN = "nested-secret"\n',
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "bash",
                    str(ROOT / "trellis" / "config-check.sh"),
                    "--codex-home",
                    str(codex_home),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MCP servers: example", result.stdout)
        self.assertNotIn("example.env", result.stdout)
        self.assertNotIn("sentinel-secret", result.stdout)
        self.assertNotIn("nested-secret", result.stdout)
