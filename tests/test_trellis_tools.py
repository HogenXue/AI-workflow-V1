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

    def test_apply_backs_up_agents_and_enables_hooks_in_config(self) -> None:
        self.codex_home.mkdir()
        target_agents = self.codex_home / "AGENTS.md"
        target_agents.write_text("existing global instructions\n", encoding="utf-8")
        config = self.codex_home / "config.toml"
        config.write_text(
            '[mcp_servers.example]\napi_key = "sentinel-secret"\n',
            encoding="utf-8",
        )

        result = self.run_install("--apply")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("INSTALLED:", result.stdout)
        self.assertIn("UPDATED: config.toml", result.stdout)
        self.assertIn("AI 工作原则（Trellis 兼容全局模板）", target_agents.read_text(encoding="utf-8"))
        self.assertEqual(
            config.read_text(encoding="utf-8"),
            '[mcp_servers.example]\napi_key = "sentinel-secret"\n\n'
            "[features]\n"
            "hooks = true   # Codex 0.129+。旧版用 `codex_hooks = true`。\n",
        )
        backups = list(self.backup_dir.glob("*/AGENTS.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "existing global instructions\n")
        config_backups = list(self.backup_dir.glob("*/config.toml"))
        self.assertEqual(len(config_backups), 1)
        self.assertEqual(
            config_backups[0].read_text(encoding="utf-8"),
            '[mcp_servers.example]\napi_key = "sentinel-secret"\n',
        )

    def test_apply_enables_hooks_in_existing_features_section(self) -> None:
        self.codex_home.mkdir()
        config = self.codex_home / "config.toml"
        config.write_text(
            "[features]\n"
            "experimental = true\n"
            "hooks = false\n"
            "\n"
            "[mcp_servers.example]\n"
            'api_key = "sentinel-secret"\n',
            encoding="utf-8",
        )

        result = self.run_install("--apply")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("UPDATED: config.toml", result.stdout)
        self.assertEqual(
            config.read_text(encoding="utf-8"),
            "[features]\n"
            "experimental = true\n"
            "hooks = true   # Codex 0.129+。旧版用 `codex_hooks = true`。\n"
            "\n"
            "[mcp_servers.example]\n"
            'api_key = "sentinel-secret"\n',
        )

    def test_apply_rejects_non_regular_config_without_changing_agents(self) -> None:
        self.codex_home.mkdir()
        target_agents = self.codex_home / "AGENTS.md"
        target_agents.write_text("existing instructions\n", encoding="utf-8")
        config_directory = self.codex_home / "config.toml"
        config_directory.mkdir()

        result = self.run_install("--apply")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a regular file", result.stderr)
        self.assertEqual(target_agents.read_text(encoding="utf-8"), "existing instructions\n")
        self.assertFalse(list(config_directory.iterdir()))
        self.assertFalse(self.backup_dir.exists())

    def test_apply_rejects_symlinked_config_without_changing_agents(self) -> None:
        self.codex_home.mkdir()
        target_agents = self.codex_home / "AGENTS.md"
        target_agents.write_text("existing instructions\n", encoding="utf-8")
        linked_config = Path(self.temp_dir.name) / "linked-config.toml"
        linked_config.write_text("sentinel = true\n", encoding="utf-8")
        (self.codex_home / "config.toml").symlink_to(linked_config)

        result = self.run_install("--apply")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a regular file", result.stderr)
        self.assertEqual(target_agents.read_text(encoding="utf-8"), "existing instructions\n")
        self.assertEqual(linked_config.read_text(encoding="utf-8"), "sentinel = true\n")

    def test_apply_restores_agents_when_config_update_fails(self) -> None:
        self.codex_home.mkdir()
        target_agents = self.codex_home / "AGENTS.md"
        target_agents.write_text("existing instructions\n", encoding="utf-8")
        config = self.codex_home / "config.toml"
        config.write_text("sentinel = true\n", encoding="utf-8")
        self.codex_home.chmod(0o555)
        try:
            result = self.run_install("--apply")
        finally:
            self.codex_home.chmod(0o755)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("could not create a temporary config file", result.stderr)
        self.assertEqual(target_agents.read_text(encoding="utf-8"), "existing instructions\n")
        self.assertEqual(config.read_text(encoding="utf-8"), "sentinel = true\n")

    def test_apply_removes_new_agents_when_config_backup_fails(self) -> None:
        self.codex_home.mkdir()
        config = self.codex_home / "config.toml"
        config.write_text("sentinel = true\n", encoding="utf-8")
        invalid_backup_dir = Path(self.temp_dir.name) / "backup-file"
        invalid_backup_dir.write_text("not a directory\n", encoding="utf-8")

        result = subprocess.run(
            [
                "bash",
                str(ROOT / "trellis" / "install.sh"),
                "--apply",
                "--codex-home",
                str(self.codex_home),
                "--backup-dir",
                str(invalid_backup_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("could not create backup directory", result.stderr)
        self.assertFalse((self.codex_home / "AGENTS.md").exists())
        self.assertEqual(config.read_text(encoding="utf-8"), "sentinel = true\n")

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
        backups = list((agents_home / ".trellis-template-backups").glob("*/AGENTS.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "existing instructions\n")

    def test_unified_agents_component_enables_hooks(self) -> None:
        self.codex_home.mkdir()
        target_agents = self.codex_home / "AGENTS.md"
        target_agents.write_text("existing instructions\n", encoding="utf-8")
        config = self.codex_home / "config.toml"
        config.write_text("sentinel = true\n", encoding="utf-8")

        result = subprocess.run(
            [
                "bash",
                str(ROOT / "scripts" / "install.sh"),
                "agents",
                "--apply",
                "--agents-home",
                str(self.codex_home),
                "--backup-dir",
                str(self.backup_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("AI 工作原则（Trellis 兼容全局模板）", target_agents.read_text(encoding="utf-8"))
        self.assertEqual(
            config.read_text(encoding="utf-8"),
            "sentinel = true\n\n"
            "[features]\n"
            "hooks = true   # Codex 0.129+。旧版用 `codex_hooks = true`。\n",
        )
        self.assertEqual(len(list(self.backup_dir.glob("*/AGENTS.md"))), 1)


class TrellisConfigCheckTests(unittest.TestCase):
    def test_check_lists_only_mcp_names(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            codex_home = Path(temporary_directory) / "codex-home"
            codex_home.mkdir()
            (codex_home / "config.toml").write_text(
                '[mcp_servers.example]\napi_key = "sentinel-secret"\n',
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
        self.assertNotIn("sentinel-secret", result.stdout)
