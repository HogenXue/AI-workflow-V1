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

    def test_apply_backs_up_agents_and_preserves_config(self) -> None:
        self.codex_home.mkdir()
        target_agents = self.codex_home / "AGENTS.md"
        target_agents.write_text("existing global instructions\n", encoding="utf-8")
        config = self.codex_home / "config.toml"
        config_bytes = b'[mcp_servers.example]\napi_key = "sentinel-secret"\n'
        config.write_bytes(config_bytes)

        result = self.run_install("--apply")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("INSTALLED:", result.stdout)
        self.assertIn("UNCHANGED: config.toml", result.stdout)
        self.assertIn("Trellis 兼容全局模板", target_agents.read_text(encoding="utf-8"))
        self.assertEqual(config.read_bytes(), config_bytes)
        backups = list(self.backup_dir.glob("*/AGENTS.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "existing global instructions\n")

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
        self.assertIn("Trellis 兼容全局模板", target_agents.read_text(encoding="utf-8"))
        backups = list((agents_home / ".trellis-template-backups").glob("*/AGENTS.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "existing instructions\n")

    def test_unified_agents_component_has_the_same_safe_behavior(self) -> None:
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
        self.assertIn("Trellis 兼容全局模板", target_agents.read_text(encoding="utf-8"))
        self.assertEqual(config.read_text(encoding="utf-8"), "sentinel = true\n")
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
